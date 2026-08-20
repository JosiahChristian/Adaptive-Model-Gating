#!/usr/bin/env python3
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from adaptive_model_gating import BASELINE_A,paired_bootstrap_ci
from run_experiment_019 import STRATEGIES as S19,calibrations as calibrations019
from experiment_020 import EARLY_STRATEGY,calibrate_early_thresholds,run_experiment_020_strategy
STRATEGIES=S19+[EARLY_STRATEGY]
CELLS=[('healthy',0.0)]+[(f,m) for f in ('drift','common_mode','primary_fault','drift_ab_fault','drift_ab_gain050','drift_ab_gain0375','drift_ab_gain025','drift_ab_gain0125','drift_all_aux_fault') for m in (.25,.5,1.0)]
SEEDS=list(range(20000,20200));AUDIT=set(range(20000,20005));RESULTS=ROOT/'results'/'experiment_020'
def write_csv(p,rows):
 p.parent.mkdir(parents=True,exist_ok=True);fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with p.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def summary(rows,f,m):
 p=[r for r in rows if 401<=r['t']<=600];p20=[r for r in rows if 401<=r['t']<=420];r0=rows[0];target=BASELINE_A+m if f.startswith('drift') else BASELINE_A
 return {'seed':r0['seed'],'family':f,'magnitude':m,'strategy':r0['strategy'],'operational_loss_401_600':sum(r['sq_error'] for r in p),'adapt_401_420':int(any(r['adapt'] for r in p20)),'probe_energy':r0.get('probe_energy',0),'provenance_accepted':r0.get('provenance_accepted',0),'provenance_abstain':r0.get('provenance_abstain',0),'accepted_partition_correct':r0.get('accepted_partition_correct',''),'early_targeted_round4_executed':r0.get('early_targeted_round4_executed',0),'early_selected_edge':r0.get('early_selected_edge',''),'early_selector_correct':r0.get('early_selector_correct',''),'missing_third_block_executed':r0.get('missing_third_block_executed',0),'fallback_completion':r0.get('fallback_completion',0),'targeted_round5_executed':r0.get('targeted_round5_executed',0),'final_slope_error_abs':abs(rows[-1]['slope_after']-target)}
def ci(v):return list(paired_bootstrap_ci(v,seed=20020,reps=10000))
def mean_for(c,st,k):
 q=[float(r[k]) for r in c if r['strategy']==st];return sum(q)/len(q)
def paired(c,a,b,k):
 by={(int(float(r['seed'])),r['strategy']):r for r in c};return [float(by[(s,a)][k])-float(by[(s,b)][k]) for s in SEEDS]
def rates(c,st):
 q=[r for r in c if r['strategy']==st];acc=[r for r in q if float(r['provenance_accepted'])==1];wrong=sum(1 for r in acc if float(r['accepted_partition_correct'])!=1)
 return {'coverage':len(acc)/200,'abstention':1-len(acc)/200,'precision':sum(float(r['accepted_partition_correct']) for r in acc)/len(acc) if acc else None,'wrong_acceptance':wrong/200}
def report_from(summaries,*vals):
 *v19,mu4e,nu4e=vals;early=EARLY_STRATEGY;tar='targeted_replicated_selective_cumulative_provenance_quorum';tri='triad_persistence';cells=[]
 for f,m in CELLS:
  c=[r for r in summaries if r['family']==f and float(r['magnitude'])==m];er=rates(c,early);tr=rates(c,tar)
  r={'family':f,'magnitude':m,'early_rates':er,'experiment019_rates':tr,'mean_probe_energy':{st:mean_for(c,st,'probe_energy') for st in (early,tar,tri)},'adapt_401_420_rate':{st:mean_for(c,st,'adapt_401_420') for st in (early,tar,tri)},'mean_operational_loss_401_600':{st:mean_for(c,st,'operational_loss_401_600') for st in (early,tar,tri)},'mean_final_slope_error_abs':{st:mean_for(c,st,'final_slope_error_abs') for st in (early,tar,tri)}}
  eq=[x for x in c if x['strategy']==early];entered=[x for x in eq if float(x['early_targeted_round4_executed'])==1];fallback=[x for x in eq if float(x['fallback_completion'])==1]
  r['early_execution_rate']=len(entered)/200;r['fallback_completion_rate']=len(fallback)/200;r['selector_correct_among_entered']=(sum(float(x['early_selector_correct']) for x in entered)/len(entered) if entered else None)
  if f.startswith('drift_ab_') or f=='drift_ab_fault':
   d=paired(c,early,tar,'operational_loss_401_600');r['vs_experiment019']={'coverage_gap':er['coverage']-tr['coverage'],'loss_mean':sum(d)/200,'loss_ci':ci(d),'energy_gap':r['mean_probe_energy'][early]-r['mean_probe_energy'][tar],'adapt_gap':r['adapt_401_420_rate'][early]-r['adapt_401_420_rate'][tar]}
  if f in ('drift_ab_gain0375','drift_ab_gain025','drift_ab_gain0125'):
   d=paired(c,early,tri,'operational_loss_401_600');r['attenuation_vs_triad']={'loss_mean':sum(d)/200,'loss_ci':ci(d),'adapt_gap':r['adapt_401_420_rate'][early]-r['adapt_401_420_rate'][tri]}
  if f=='drift':
   by={(int(float(x['seed'])),x['strategy']):x for x in c};vv=[]
   for s in SEEDS:
    a=float(by[(s,early)]['operational_loss_401_600']);b=float(by[(s,tar)]['operational_loss_401_600']);vv.append((a-b)/max(abs(b),1e-12))
   r['drift_regression']={'relative_excess_mean':sum(vv)/200,'ci':ci(vv),'adapt_gap':r['adapt_401_420_rate'][early]-r['adapt_401_420_rate'][tar]}
  if f in ('common_mode','primary_fault'):
   d=paired(c,early,tar,'final_slope_error_abs');r['fault_regression']={'slope_error_diff_mean':sum(d)/200,'ci':ci(d)}
  cells.append(r)
 return {'mu_4_early':mu4e,'nu_4_early':nu4e,'early_calibration_seeds':[5000,5999],'evaluation_seeds':[20000,20199],'bootstrap_seed':20020,'n_seeds_per_cell':200,'strategies':STRATEGIES,'cells':cells,'audit_seeds':sorted(AUDIT)}
def calibrations():
 v=calibrations019();mu,nu=v[10],v[11];mu4e,nu4e=calibrate_early_thresholds(mu,nu);return (*v,mu4e,nu4e)
