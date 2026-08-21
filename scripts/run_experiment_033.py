#!/usr/bin/env python3
import math,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from adaptive_model_gating import paired_bootstrap_ci
from experiment_029 import POSTERIOR_RISK_STRATEGY,TRIAD,ACCEPT_THRESHOLD,WRONG_COST,FALLBACK_COST
from experiment_032 import COMPOSED_STRATEGY
from experiment_033 import STRATEGIES
from run_experiment_021 import calibrations
from run_experiment_032 import summary,write_csv

SEEDS=range(33000,33500);AUDIT=set(range(33000,33005));BOOTSTRAP_SEED=33033;Z=1.6448536269514722

def cell(label,kind,family,magnitude,**kw):return {'label':label,'kind':kind,'family':family,'magnitude':float(magnitude),**kw}
def cells():
 out=[]
 for g in (.475,.45,.40,.375):
  for n in (1.10,1.40):out.append(cell(f'gn_g{g:.3f}_n{n:.2f}','gain_noise','drift_ab_fault',.50,gain=g,noise_scale=n))
 for g,n in ((.45,1.75),(.40,1.75),(.35,1.25),(.30,1.25)):out.append(cell(f'gn_g{g:.3f}_n{n:.2f}','gain_noise','drift_ab_fault',.50,gain=g,noise_scale=n))
 for off in (-35,35,75):
  tag=f'm{abs(off)}' if off<0 else f'p{off}'
  for n in (1.0,1.5):out.append(cell(f'tn_{tag}_n{n:.2f}','timing_noise','drift_ab_fault',.50,timing_offset=off,noise_scale=n,gain=.50))
 for sa,sb in ((.75,1.25),(.50,1.00),(1.00,1.75)):
  for n in (1.0,1.5):out.append(cell(f'an_{sa:.2f}_{sb:.2f}_n{n:.2f}','asym_noise','drift_ab_fault',.50,scale_a=sa,scale_b=sb,noise_scale=n,gain=.50))
 for cm in (.25,.50,.75):out.append(cell(f'mixed_cm{cm:.2f}_n1.25','mixed_noise','drift',.50,common_magnitude=cm,noise_scale=1.25,gain=1.0))
 for m in (.15,.75,1.25):out.append(cell(f'common_mode_{m:.2f}','common_mode','common_mode',m))
 if len(out)!=30:raise AssertionError(len(out))
 return tuple(out)
CELLS=cells()

def wilson_upper(k,n):
 p=k/n;den=1+Z*Z/n;center=(p+Z*Z/(2*n))/den;rad=Z*math.sqrt(p*(1-p)/n+Z*Z/(4*n*n))/den;return min(1.,center+rad)
def rates(q):
 acc=[x for x in q if int(float(x['coverage']))];wrong=sum(int(float(x['wrong_accept'])) for x in q);correct=sum(int(float(x['correct'])) for x in acc)
 return {'coverage':len(acc)/len(q),'accepted_n':len(acc),'wrong_n':wrong,'wrong_acceptance':wrong/len(q),'wrong_wilson_upper_95':wilson_upper(wrong,len(q)),'precision':correct/len(acc) if acc else None}
def avg(q,k):return sum(float(x[k]) for x in q)/len(q)
def paired(by,a,b,k):return [float(by[(s,a)][k])-float(by[(s,b)][k]) for s in SEEDS]
def ci(v):return list(paired_bootstrap_ci(v,seed=BOOTSTRAP_SEED,reps=10000))

def report_from(rows,vals):
 H={f'H{i}':True for i in range(1,12)};out={}
 for c in CELLS:
  cr=[r for r in rows if r['label']==c['label']];by={(int(r['seed']),r['strategy']):r for r in cr};qs={st:[by[(s,st)] for s in SEEDS] for st in STRATEGIES};rr={st:rates(qs[st]) for st in STRATEGIES}
  for s in SEEDS:
   a,b=by[(s,COMPOSED_STRATEGY)],by[(s,POSTERIOR_RISK_STRATEGY)]
   if any(a[k]!=b[k] for k in ('coverage','abstain','stop_round','deploy_hypothesis')) or abs(float(a['posterior_at_deployment'])-float(b['posterior_at_deployment']))>1e-12 or abs(float(a['probe_energy'])-float(b['probe_energy']))>1e-12:H['H1']=False
  if rr[COMPOSED_STRATEGY]['wrong_wilson_upper_95']>.01:H['H2']=False
  if c['kind']=='gain_noise' and c['gain'] in (.475,.45) and c['noise_scale'] in (1.10,1.40) and (rr[COMPOSED_STRATEGY]['coverage']<.90 or (rr[COMPOSED_STRATEGY]['precision'] or 0)<.99):H['H3']=False
  if c['kind']=='timing_noise':
   if c['noise_scale']==1.0 and (rr[COMPOSED_STRATEGY]['coverage']<.90 or (rr[COMPOSED_STRATEGY]['precision'] or 0)<.99):H['H4']=False
   if c['noise_scale']==1.5 and c['timing_offset'] in (-35,35) and (rr[COMPOSED_STRATEGY]['coverage']<.80 or (rr[COMPOSED_STRATEGY]['precision'] or 0)<.99):H['H4']=False
  if c['kind']=='asym_noise':
   floor=.85 if c['noise_scale']==1.0 else .75
   if rr[COMPOSED_STRATEGY]['coverage']<floor or (rr[COMPOSED_STRATEGY]['precision'] or 0)<.99:H['H5']=False
  d32t=paired(by,COMPOSED_STRATEGY,TRIAD,'operational_loss_401_600');d29t=paired(by,POSTERIOR_RISK_STRATEGY,TRIAD,'operational_loss_401_600');d3229=paired(by,COMPOSED_STRATEGY,POSTERIOR_RISK_STRATEGY,'operational_loss_401_600')
  excess32=sum(d32t)/len(SEEDS);excess29=sum(d29t)/len(SEEDS);reduction=((excess29-excess32)/excess29 if excess29>0 else None)
  losses={st:avg(qs[st],'operational_loss_401_600') for st in STRATEGIES}
  if c['kind']=='common_mode':
   limit={.15:.25,.75:2.0,1.25:50.0}[c['magnitude']]
   if excess32>limit or (excess29>0 and (reduction is None or reduction<.80)):H['H6']=False
  if c['kind'] in ('gain_noise','timing_noise','asym_noise') and losses[COMPOSED_STRATEGY]>losses[POSTERIOR_RISK_STRATEGY]+.05:H['H7']=False
  if c['kind']=='mixed_noise':
   if losses[COMPOSED_STRATEGY]>losses[TRIAD]+10.0:H['H8']=False
   if losses[POSTERIOR_RISK_STRATEGY]<=losses[TRIAD] and losses[COMPOSED_STRATEGY]>losses[POSTERIOR_RISK_STRATEGY]+.05:H['H8']=False
  if sum(int(float(x['causal_violation_count'])) for x in qs[COMPOSED_STRATEGY]) or sum(int(float(x['triad_veto_adapt_violations'])) for x in qs[COMPOSED_STRATEGY]):H['H9']=False
  fallback=0
  for s in SEEDS:
   a,t=by[(s,COMPOSED_STRATEGY)],by[(s,TRIAD)]
   if int(float(a['abstain'])) and (a['adapt_signature']!=t['adapt_signature'] or abs(float(a['operational_loss_401_600'])-float(t['operational_loss_401_600']))>1e-12):fallback+=1
  if fallback:H['H10']=False
  out[c['label']]={'cell':c,'rates':rr,'mean_operational_loss_401_600':losses,'mean_probe_energy':{st:avg(qs[st],'probe_energy') for st in STRATEGIES},
    'mean_final_slope_error_abs':{st:avg(qs[st],'final_slope_error_abs') for st in STRATEGIES},'mean_context_vote_fraction_401_420':avg(qs[COMPOSED_STRATEGY],'context_vote_fraction_401_420'),
    'mean_context_removed_count':avg(qs[COMPOSED_STRATEGY],'context_removed_count'),'mean_changed_adapt_count_vs_029':avg(qs[COMPOSED_STRATEGY],'changed_adapt_count_vs_029'),
    'paired_loss_vs_triad_mean':excess32,'paired_loss_vs_triad_ci':ci(d32t),'paired_loss_vs_029_mean':sum(d3229)/len(SEEDS),'paired_loss_vs_029_ci':ci(d3229),
    'experiment029_excess_vs_triad_mean':excess29,'fraction_excess_reduction_vs_029':reduction,'fallback_exact_mismatches':fallback}
  if c['kind']=='gain_noise' and (c['gain']<.45 or c['noise_scale']>1.40):out[c['label']]['boundary_characterization']=True
  if c['kind']=='timing_noise' and c['timing_offset']==75 and c['noise_scale']==1.5:out[c['label']]['boundary_characterization']=True
 tau,kappa,k3,la,lb,lc,lab,lac,lbc=vals[:9]
 H['H11']=ACCEPT_THRESHOLD==.99 and WRONG_COST==100.0 and FALLBACK_COST==1.0
 return {'evaluation_seeds':[33000,33499],'n_seeds_per_cell':500,'cell_count':30,'strategies':STRATEGIES,'audit_seeds':sorted(AUDIT),'bootstrap_seed':BOOTSTRAP_SEED,'bootstrap_resamples':10000,'hypotheses':H,
  'accept_threshold':ACCEPT_THRESHOLD,'wrong_action_cost':WRONG_COST,'fallback_cost':FALLBACK_COST,'context_vote_formula':'triad_consistent * 1[m_a+m_b+m_c>=2] * 1[d_ab+d_ac+d_bc==0] at current t only',
  'inherited_context_thresholds':{'tau':tau,'kappa':kappa,'k3':k3,'la':la,'lb':lb,'lc':lc,'lab':lab,'lac':lac,'lbc':lbc},'no_recalibration':True,
  'experiment032_controller_frozen':True,'code_commit':os.environ.get('GITHUB_SHA','unknown'),'cells':out}

def calibration_values():return calibrations()
