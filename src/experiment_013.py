from __future__ import annotations
from random import Random
from statistics import mean, median
from adaptive_model_gating import BASELINE_A,EVENT_T,INITIAL_FIT_END,N_STEPS,PERSISTENCE_COUNT,ROLLING_WINDOW,empirical_quantile,initial_model,refit,run_strategy_on_stream
from experiment_008 import run_health_persistence_on_stream
from experiment_010 import SIGMA_REF,classify_triad,rolling_pairwise_health,run_triad_persistence_on_stream
from experiment_011 import BETA_ANCHOR,SIGMA_ANCHOR,run_independent_persistence_on_stream
from experiment_012 import calibrate_dual_anchor_thresholds
CALIBRATION_SEEDS=range(1000,1200)
FAMILIES={'healthy','drift','common_mode','primary_fault','drift_g1_common_fault','drift_g2_fault','drift_misdeclared_g1_fault','drift_all_aux_fault'}

def generate_experiment_013_stream(seed,family,magnitude):
 if family not in FAMILIES: raise ValueError(family)
 rng=Random(seed)
 keys=('x_true','x_primary','x_r1','x_r2','z','z_b','z_c','y','a','physical_epsilon','r1_unit_noise','r2_unit_noise','anchor_unit_noise','anchor_b_unit_noise','anchor_c_unit_noise','common_unit_noise','primary_unit_noise','g1_fault_unit_noise','g2_fault_unit_noise','true_sigma_x','ref_fault_unit_noise','primary_fault_sigma','ref1_fault_sigma','common_sigma')
 random_keys=('physical_epsilon','r1_unit_noise','r2_unit_noise','anchor_unit_noise','anchor_b_unit_noise','anchor_c_unit_noise','common_unit_noise','primary_unit_noise','g1_fault_unit_noise','g2_fault_unit_noise')
 s={k:[0.0]*(N_STEPS+1) for k in keys};s['a']=[BASELINE_A]*(N_STEPS+1)
 for t in range(1,N_STEPS+1):
  s['x_true'][t]=.8*s['x_true'][t-1]+rng.gauss(0,.5)
  for k in random_keys: s[k][t]=rng.gauss(0,.5) if k=='physical_epsilon' else rng.gauss(0,1)
  xt=s['x_true'][t];s['x_primary'][t]=xt;s['x_r1'][t]=xt+SIGMA_REF*s['r1_unit_noise'][t];s['x_r2'][t]=xt+SIGMA_REF*s['r2_unit_noise'][t]
  s['z'][t]=BETA_ANCHOR*xt+SIGMA_ANCHOR*s['anchor_unit_noise'][t];s['z_b'][t]=BETA_ANCHOR*xt+SIGMA_ANCHOR*s['anchor_b_unit_noise'][t];s['z_c'][t]=BETA_ANCHOR*xt+SIGMA_ANCHOR*s['anchor_c_unit_noise'][t]
  if t>=EVENT_T:
   if family=='drift': s['a'][t]=BASELINE_A+magnitude
   elif family=='common_mode':
    q=magnitude*s['common_unit_noise'][t];s['x_primary'][t]+=q;s['x_r1'][t]+=q;s['x_r2'][t]+=q;s['true_sigma_x'][t]=magnitude;s['common_sigma'][t]=magnitude
   elif family=='primary_fault':
    s['x_primary'][t]+=magnitude*s['primary_unit_noise'][t];s['true_sigma_x'][t]=magnitude;s['primary_fault_sigma'][t]=magnitude
   elif family in ('drift_g1_common_fault','drift_g2_fault','drift_misdeclared_g1_fault','drift_all_aux_fault'):
    s['a'][t]=BASELINE_A+magnitude
    if family in ('drift_g1_common_fault','drift_misdeclared_g1_fault','drift_all_aux_fault'):
     q=BETA_ANCHOR*magnitude*s['g1_fault_unit_noise'][t];s['z'][t]+=q;s['z_b'][t]+=q
    if family=='drift_g2_fault': s['z_c'][t]+=BETA_ANCHOR*magnitude*s['g2_fault_unit_noise'][t]
    elif family=='drift_all_aux_fault': s['z_c'][t]+=BETA_ANCHOR*magnitude*s['g1_fault_unit_noise'][t]
  s['y'][t]=s['a'][t]*xt+s['physical_epsilon'][t]
 s['x_ref']=s['x_r1'];s['reference_unit_noise']=s['r1_unit_noise'];return s

def health(stream):
 vals={k:[] for k in ('a','b','c','ab','ac','bc')};out={k:[None]*(N_STEPS+1) for k in vals}
 for t in range(1,N_STEPS+1):
  xm=median((stream['x_primary'][t],stream['x_r1'][t],stream['x_r2'][t]));a=stream['z'][t]/BETA_ANCHOR;b=stream['z_b'][t]/BETA_ANCHOR;c=stream['z_c'][t]/BETA_ANCHOR
  now={'a':(xm-a)**2,'b':(xm-b)**2,'c':(xm-c)**2,'ab':(a-b)**2,'ac':(a-c)**2,'bc':(b-c)**2}
  for k,v in now.items():
   vals[k].append(v)
   if len(vals[k])>=ROLLING_WINDOW: out[k][t]=mean(vals[k][-ROLLING_WINDOW:])
 return out

def calibrate_anchor_c_thresholds():
 vc=[];vac=[];vbc=[]
 for seed in CALIBRATION_SEEDS:
  h=health(generate_experiment_013_stream(seed,'healthy',0.0))
  for t in range(101,301):
   vc.append(h['c'][t]);vac.append(h['ac'][t]);vbc.append(h['bc'][t])
 return empirical_quantile(vc,.99),empirical_quantile(vac,.99),empirical_quantile(vbc,.99)

def _annotate(rows,stream,k3,la,lb,lc,lab,lac,lbc,family):
 h=health(stream);ph=rolling_pairwise_health(stream);groups={'a':'G1','b':'G2' if family=='drift_misdeclared_g1_fault' else 'G1','c':'G2'}
 for r in rows:
  t=r['t'];m={x:int(h[x][t] is not None and h[x][t]>l) for x,l in [('a',la),('b',lb),('c',lc)]};dis={x:int(h[x][t] is not None and h[x][t]>l) for x,l in [('ab',lab),('ac',lac),('bc',lbc)]};consistent=int(all(ph[k][t] is not None and ph[k][t]<=k3 for k in ph));active={groups[x] for x in 'abc' if m[x]};cross_ok=int((m['a'] and m['c'] and not dis['ac']) or (m['b'] and m['c'] and not dis['bc']) or (groups['a']!=groups['b'] and m['a'] and m['b'] and not dis['ab']))
  r.update({'z_c':stream['z_c'][t],'anchor_mismatch':m['a'],'anchor_b_mismatch':m['b'],'anchor_c_mismatch':m['c'],'anchor_ab_disagreement':dis['ab'],'anchor_ac_disagreement':dis['ac'],'anchor_bc_disagreement':dis['bc'],'raw_mismatch_votes':sum(m.values()),'provenance_mismatch_votes':len(active),'declared_group_a':groups['a'],'declared_group_b':groups['b'],'declared_group_c':groups['c'],'triad_consistent':consistent,'provenance_cross_consistent':cross_ok})
  r.setdefault('independent_veto',0)
 return rows

def run_quorum(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,stream,family,provenance):
 xp,ys=stream['x_primary'],stream['y'];model=initial_model(xp,ys);sq=[];streak=0;rows=[]
 base=_annotate(run_strategy_on_stream(seed,label,'frozen',tau,xp,ys,stream['a']),stream,k3,la,lb,lc,lab,lac,lbc,family);diag={r['t']:r for r in base};ph=rolling_pairwise_health(stream)
 for t in range(INITIAL_FIT_END+1,N_STEPS+1):
  sb,ib=model.slope,model.intercept;yh=model.predict(xp[t]);err=ys[t]-yh;se=err*err;sq.append(se);rmse=mean(sq[-ROLLING_WINDOW:]) if len(sq)>=ROLLING_WINDOW else None;d=diag[t];pbad,_,_,_=classify_triad(ph['h_p_r1'][t],ph['h_p_r2'][t],ph['h_r1_r2'][t],k3)
  suspect=int(d['triad_consistent'] and d['provenance_cross_consistent'] and ((d['provenance_mismatch_votes']>=2) if provenance else (d['raw_mismatch_votes']>=2)));streak=(streak+1 if rmse is not None and rmse>tau else 0);ready=streak>=PERSISTENCE_COUNT;veto=int(ready and (pbad or suspect));adapt=int(ready and not veto)
  if ready: streak=0
  if adapt:model=refit(xp,ys,t)
  row=dict(d);row.update({'strategy':'provenance_aware_quorum' if provenance else 'naive_three_anchor_quorum','y_hat':yh,'error':err,'sq_error':se,'rolling_mse':rmse,'adapt':adapt,'slope_before':sb,'intercept_before':ib,'slope_after':model.slope,'intercept_after':model.intercept,'common_mode_suspect':suspect,'independent_veto':veto,'latent_input_sq_error':(ys[t]-(sb*stream['x_true'][t]+ib))**2});rows.append(row)
 return rows

def run_experiment_013_strategy(seed,family,magnitude,strategy,tau,kappa,k3,la,lb,lc,lab,lac,lbc):
 stream=generate_experiment_013_stream(seed,family,magnitude);label=f'experiment013_{family}_{magnitude:.2f}'
 if strategy in ('naive_three_anchor_quorum','provenance_aware_quorum'): return run_quorum(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,stream,family,strategy=='provenance_aware_quorum')
 if strategy=='independent_persistence': rows=run_independent_persistence_on_stream(seed,label,tau,k3,la,stream)
 elif strategy=='triad_persistence': rows=run_triad_persistence_on_stream(seed,label,tau,k3,stream)
 elif strategy=='health_persistence': rows=run_health_persistence_on_stream(seed,label,tau,kappa,stream)
 else: rows=run_strategy_on_stream(seed,label,strategy,tau,stream['x_primary'],stream['y'],stream['a'])
 return _annotate(rows,stream,k3,la,lb,lc,lab,lac,lbc,family)
