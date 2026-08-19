from __future__ import annotations
from random import Random
from statistics import mean, median
from math import sqrt
from adaptive_model_gating import BASELINE_A,EVENT_T,INITIAL_FIT_END,N_STEPS,PERSISTENCE_COUNT,ROLLING_WINDOW,empirical_quantile,initial_model,refit,run_strategy_on_stream
from experiment_008 import run_health_persistence_on_stream
from experiment_010 import SIGMA_REF,classify_triad,rolling_pairwise_health,run_triad_persistence_on_stream
from experiment_011 import BETA_ANCHOR,SIGMA_ANCHOR,run_independent_persistence_on_stream
from experiment_013 import health

RHO_SIG=.35
DEPENDENCE_CALIBRATION_SEEDS=range(1400,1600)
FAMILIES={'healthy','drift','common_mode','primary_fault','drift_ab_fault','drift_ab_absent_signature','drift_bc_misleading_signature','drift_all_aux_fault'}

def generate_experiment_014_stream(seed,family,magnitude,rho_override=None):
 if family not in FAMILIES: raise ValueError(family)
 if magnitude<0: raise ValueError('magnitude must be nonnegative')
 rho=(0.0 if family=='drift_ab_absent_signature' else RHO_SIG) if rho_override is None else float(rho_override);rng=Random(seed)
 keys=('x_true','x_primary','x_r1','x_r2','z','z_b','z_c','y','a','physical_epsilon','r1_unit_noise','r2_unit_noise','anchor_unit_noise','anchor_b_unit_noise','anchor_c_unit_noise','dependence_unit_noise','common_unit_noise','primary_unit_noise','ab_fault_unit_noise','bc_fault_unit_noise','true_sigma_x','ref_fault_unit_noise','primary_fault_sigma','ref1_fault_sigma','common_sigma')
 rnd=('physical_epsilon','r1_unit_noise','r2_unit_noise','anchor_unit_noise','anchor_b_unit_noise','anchor_c_unit_noise','dependence_unit_noise','common_unit_noise','primary_unit_noise','ab_fault_unit_noise','bc_fault_unit_noise')
 s={k:[0.0]*(N_STEPS+1) for k in keys};s['a']=[BASELINE_A]*(N_STEPS+1)
 for t in range(1,N_STEPS+1):
  s['x_true'][t]=.8*s['x_true'][t-1]+rng.gauss(0,.5)
  for k in rnd:s[k][t]=rng.gauss(0,.5) if k=='physical_epsilon' else rng.gauss(0,1)
  xt=s['x_true'][t];s['x_primary'][t]=xt;s['x_r1'][t]=xt+SIGMA_REF*s['r1_unit_noise'][t];s['x_r2'][t]=xt+SIGMA_REF*s['r2_unit_noise'][t];q=rho*s['dependence_unit_noise'][t]
  s['z'][t]=BETA_ANCHOR*xt+SIGMA_ANCHOR*(s['anchor_unit_noise'][t]+q);s['z_b'][t]=BETA_ANCHOR*xt+SIGMA_ANCHOR*(s['anchor_b_unit_noise'][t]+q);s['z_c'][t]=BETA_ANCHOR*xt+SIGMA_ANCHOR*s['anchor_c_unit_noise'][t]
  if t>=EVENT_T:
   if family=='drift':s['a'][t]=BASELINE_A+magnitude
   elif family=='common_mode':
    q2=magnitude*s['common_unit_noise'][t];s['x_primary'][t]+=q2;s['x_r1'][t]+=q2;s['x_r2'][t]+=q2;s['true_sigma_x'][t]=magnitude;s['common_sigma'][t]=magnitude
   elif family=='primary_fault':s['x_primary'][t]+=magnitude*s['primary_unit_noise'][t];s['true_sigma_x'][t]=magnitude;s['primary_fault_sigma'][t]=magnitude
   elif family in ('drift_ab_fault','drift_ab_absent_signature'):
    s['a'][t]=BASELINE_A+magnitude;q2=BETA_ANCHOR*magnitude*s['ab_fault_unit_noise'][t];s['z'][t]+=q2;s['z_b'][t]+=q2
   elif family=='drift_bc_misleading_signature':
    s['a'][t]=BASELINE_A+magnitude;q2=BETA_ANCHOR*magnitude*s['bc_fault_unit_noise'][t];s['z_b'][t]+=q2;s['z_c'][t]+=q2
   elif family=='drift_all_aux_fault':
    s['a'][t]=BASELINE_A+magnitude;q2=BETA_ANCHOR*magnitude*s['ab_fault_unit_noise'][t];s['z'][t]+=q2;s['z_b'][t]+=q2;s['z_c'][t]+=q2
  s['y'][t]=s['a'][t]*xt+s['physical_epsilon'][t]
 s['x_ref']=s['x_r1'];s['reference_unit_noise']=s['r1_unit_noise'];s['rho_sig']=rho;return s

def _pearson(x,y):
 xb,yb=mean(x),mean(y);dx=[v-xb for v in x];dy=[v-yb for v in y];d=sqrt(sum(v*v for v in dx)*sum(v*v for v in dy));return 0.0 if d==0 else sum(a*b for a,b in zip(dx,dy))/d

def preevent_correlations(s):
 a=[];b=[];c=[]
 for t in range(101,301):
  xm=median((s['x_primary'][t],s['x_r1'][t],s['x_r2'][t]));a.append(s['z'][t]/BETA_ANCHOR-xm);b.append(s['z_b'][t]/BETA_ANCHOR-xm);c.append(s['z_c'][t]/BETA_ANCHOR-xm)
 return _pearson(a,b),_pearson(a,c),_pearson(b,c)

def calibrate_lambda_dep():
 v=[]
 for seed in DEPENDENCE_CALIBRATION_SEEDS:v.extend(abs(x) for x in preevent_correlations(generate_experiment_014_stream(seed,'healthy',0.0,rho_override=0.0)))
 return empirical_quantile(v,.99)

def infer_groups(s,lam):
 corr=preevent_correlations(s);nodes=('a','b','c');adj={n:set() for n in nodes}
 for (u,v),r in zip((('a','b'),('a','c'),('b','c')),corr):
  if abs(r)>lam:adj[u].add(v);adj[v].add(u)
 g={};i=0
 for n in nodes:
  if n in g:continue
  i+=1;stack=[n]
  while stack:
   u=stack.pop()
   if u in g:continue
   g[u]=f'G{i}';stack.extend(adj[u]-g.keys())
 return g,corr

def oracle_groups(family):
 if family=='drift_bc_misleading_signature':return {'a':'G1','b':'G2','c':'G2'}
 if family=='drift_all_aux_fault':return {'a':'G1','b':'G1','c':'G1'}
 return {'a':'G1','b':'G1','c':'G2'}

def partition_matches(a,b):
 n=('a','b','c');return int(all((a[x]==a[y])==(b[x]==b[y]) for i,x in enumerate(n) for y in n[i+1:]))

def _annotate(rows,s,k3,la,lb,lc,lab,lac,lbc,ld,inferred,corr,family,gate=None):
 gate=gate or inferred;h=health(s);ph=rolling_pairwise_health(s);correct=partition_matches(inferred,oracle_groups(family))
 for r in rows:
  t=r['t'];m={x:int(h[x][t] is not None and h[x][t]>z) for x,z in [('a',la),('b',lb),('c',lc)]};d={x:int(h[x][t] is not None and h[x][t]>z) for x,z in [('ab',lab),('ac',lac),('bc',lbc)]};consistent=int(all(ph[k][t] is not None and ph[k][t]<=k3 for k in ph))
  rawcross=int((m['a'] and m['b'] and not d['ab'])or(m['a'] and m['c'] and not d['ac'])or(m['b'] and m['c'] and not d['bc']));gcross=int((gate['a']!=gate['b'] and m['a'] and m['b'] and not d['ab'])or(gate['a']!=gate['c'] and m['a'] and m['c'] and not d['ac'])or(gate['b']!=gate['c'] and m['b'] and m['c'] and not d['bc']))
  ia={inferred[x] for x in 'abc' if m[x]};ga={gate[x] for x in 'abc' if m[x]}
  r.update({'z_c':s['z_c'][t],'anchor_mismatch':m['a'],'anchor_b_mismatch':m['b'],'anchor_c_mismatch':m['c'],'anchor_ab_disagreement':d['ab'],'anchor_ac_disagreement':d['ac'],'anchor_bc_disagreement':d['bc'],'raw_mismatch_votes':sum(m.values()),'inferred_group_mismatch_votes':len(ia),'gate_group_mismatch_votes':len(ga),'triad_consistent':consistent,'raw_cross_consistent':rawcross,'group_cross_consistent':gcross,'corr_ab':corr[0],'corr_ac':corr[1],'corr_bc':corr[2],'lambda_dep':ld,'inferred_group_a':inferred['a'],'inferred_group_b':inferred['b'],'inferred_group_c':inferred['c'],'gate_group_a':gate['a'],'gate_group_b':gate['b'],'gate_group_c':gate['c'],'inferred_partition_correct':correct})
  for key in ('x_true','x_primary','x_r1','x_r2','z','z_b','physical_epsilon','r1_unit_noise','r2_unit_noise','anchor_unit_noise','anchor_b_unit_noise','anchor_c_unit_noise','dependence_unit_noise','common_unit_noise','primary_unit_noise','ab_fault_unit_noise','bc_fault_unit_noise'):r.setdefault(key,s[key][t])
  lh=r['slope_before']*s['x_true'][t]+r['intercept_before'];r.setdefault('latent_input_sq_error',(s['y'][t]-lh)**2);r.setdefault('common_mode_suspect',0);r.setdefault('independent_veto',0)
 return rows

def _quorum(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,ld,s,family,mode):
 inferred,corr=infer_groups(s,ld);gate=oracle_groups(family) if mode=='oracle' else inferred;xp,ys=s['x_primary'],s['y'];model=initial_model(xp,ys);sq=[];streak=0;rows=[]
 base=_annotate(run_strategy_on_stream(seed,label,'frozen',tau,xp,ys,s['a']),s,k3,la,lb,lc,lab,lac,lbc,ld,inferred,corr,family,gate);diag={r['t']:r for r in base};ph=rolling_pairwise_health(s)
 for t in range(INITIAL_FIT_END+1,N_STEPS+1):
  sb,ib=model.slope,model.intercept;yh=model.predict(xp[t]);e=ys[t]-yh;se=e*e;sq.append(se);rm=mean(sq[-ROLLING_WINDOW:]) if len(sq)>=ROLLING_WINDOW else None;z=diag[t];pbad,_,_,_=classify_triad(ph['h_p_r1'][t],ph['h_p_r2'][t],ph['h_r1_r2'][t],k3);sus=int(z['triad_consistent'] and z['group_cross_consistent'] and z['gate_group_mismatch_votes']>=2)
  if rm is not None:streak=streak+1 if rm>tau else 0
  ready=streak>=PERSISTENCE_COUNT;veto=int(ready and(pbad or sus));adapt=int(ready and not veto)
  if ready:streak=0
  if adapt:model=refit(xp,ys,t)
  row=dict(z);row.update({'strategy':'oracle_provenance_quorum' if mode=='oracle' else 'learned_provenance_quorum','y_hat':yh,'error':e,'sq_error':se,'rolling_mse':rm,'adapt':adapt,'slope_before':sb,'intercept_before':ib,'slope_after':model.slope,'intercept_after':model.intercept,'common_mode_suspect':sus,'independent_veto':veto,'latent_input_sq_error':(ys[t]-(sb*s['x_true'][t]+ib))**2});rows.append(row)
 return rows

def _naive(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,ld,s,family):
 inferred,corr=infer_groups(s,ld);xp,ys=s['x_primary'],s['y'];model=initial_model(xp,ys);sq=[];streak=0;rows=[];base=_annotate(run_strategy_on_stream(seed,label,'frozen',tau,xp,ys,s['a']),s,k3,la,lb,lc,lab,lac,lbc,ld,inferred,corr,family,inferred);diag={r['t']:r for r in base};ph=rolling_pairwise_health(s)
 for t in range(INITIAL_FIT_END+1,N_STEPS+1):
  sb,ib=model.slope,model.intercept;yh=model.predict(xp[t]);e=ys[t]-yh;se=e*e;sq.append(se);rm=mean(sq[-ROLLING_WINDOW:]) if len(sq)>=ROLLING_WINDOW else None;z=diag[t];pbad,_,_,_=classify_triad(ph['h_p_r1'][t],ph['h_p_r2'][t],ph['h_r1_r2'][t],k3);sus=int(z['triad_consistent'] and z['raw_cross_consistent'] and z['raw_mismatch_votes']>=2)
  if rm is not None:streak=streak+1 if rm>tau else 0
  ready=streak>=PERSISTENCE_COUNT;veto=int(ready and(pbad or sus));adapt=int(ready and not veto)
  if ready:streak=0
  if adapt:model=refit(xp,ys,t)
  row=dict(z);row.update({'strategy':'naive_three_anchor_quorum','y_hat':yh,'error':e,'sq_error':se,'rolling_mse':rm,'adapt':adapt,'slope_before':sb,'intercept_before':ib,'slope_after':model.slope,'intercept_after':model.intercept,'common_mode_suspect':sus,'independent_veto':veto,'latent_input_sq_error':(ys[t]-(sb*s['x_true'][t]+ib))**2});rows.append(row)
 return rows

def run_experiment_014_strategy(seed,family,magnitude,strategy,tau,kappa,k3,la,lb,lc,lab,lac,lbc,ld):
 allowed={'frozen','continuous','threshold','persistence','health_persistence','triad_persistence','independent_persistence','naive_three_anchor_quorum','oracle_provenance_quorum','learned_provenance_quorum'}
 if strategy not in allowed:raise ValueError(strategy)
 s=generate_experiment_014_stream(seed,family,magnitude);label=f'experiment014_{family}_{magnitude:.2f}';inferred,corr=infer_groups(s,ld)
 if strategy=='learned_provenance_quorum':return _quorum(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,ld,s,family,'learned')
 if strategy=='oracle_provenance_quorum':return _quorum(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,ld,s,family,'oracle')
 if strategy=='naive_three_anchor_quorum':return _naive(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,ld,s,family)
 if strategy=='independent_persistence':rows=run_independent_persistence_on_stream(seed,label,tau,k3,la,s)
 elif strategy=='triad_persistence':rows=run_triad_persistence_on_stream(seed,label,tau,k3,s)
 elif strategy=='health_persistence':rows=run_health_persistence_on_stream(seed,label,tau,kappa,s)
 else:rows=run_strategy_on_stream(seed,label,strategy,tau,s['x_primary'],s['y'],s['a'])
 return _annotate(rows,s,k3,la,lb,lc,lab,lac,lbc,ld,inferred,corr,family,inferred)
