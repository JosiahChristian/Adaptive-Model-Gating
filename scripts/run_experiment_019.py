#!/usr/bin/env python3
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from adaptive_model_gating import BASELINE_A,calibrate_tau,paired_bootstrap_ci
from experiment_008 import calibrate_kappa
from experiment_010 import calibrate_kappa3
from experiment_011 import calibrate_lambda_anchor
from experiment_012 import calibrate_dual_anchor_thresholds
from experiment_013 import calibrate_anchor_c_thresholds
from experiment_016 import calibrate_lambda_probe_rounds
from experiment_017 import calibrate_cumulative_thresholds
from experiment_018 import calibrate_round5_thresholds
from experiment_019 import calibrate_targeted_thresholds,run_experiment_019_strategy

STRATEGIES=['frozen','continuous','threshold','persistence','health_persistence','triad_persistence','independent_persistence','naive_three_anchor_quorum','oracle_provenance_quorum','max_probe_provenance_quorum','sequential_provenance_quorum','cumulative_provenance_quorum','selective_cumulative_provenance_quorum','replicated_selective_cumulative_provenance_quorum','targeted_replicated_selective_cumulative_provenance_quorum']
CELLS=[('healthy',0.0)]+[(f,m) for f in ('drift','common_mode','primary_fault','drift_ab_fault','drift_ab_gain050','drift_ab_gain0375','drift_ab_gain025','drift_ab_gain0125','drift_all_aux_fault') for m in (.25,.5,1.0)]
SEEDS=list(range(19000,19200));AUDIT=set(range(19000,19005));RESULTS=ROOT/'results'/'experiment_019'

def write_csv(p,rows):
 p.parent.mkdir(parents=True,exist_ok=True);fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with p.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def summary(rows,f,m):
 p=[r for r in rows if 401<=r['t']<=600];p20=[r for r in rows if 401<=r['t']<=420];r0=rows[0];target=BASELINE_A+m if f.startswith('drift') else BASELINE_A
 return {'seed':r0['seed'],'family':f,'magnitude':m,'strategy':r0['strategy'],'operational_loss_401_600':sum(r['sq_error'] for r in p),'adapt_401_420':int(any(r['adapt'] for r in p20)),'probe_energy':r0.get('probe_energy',0),'provenance_accepted':r0.get('provenance_accepted',0),'provenance_abstain':r0.get('provenance_abstain',0),'accepted_partition_correct':r0.get('accepted_partition_correct',''),'targeted_round5_executed':r0.get('targeted_round5_executed',0),'targeted_selected_edge':r0.get('targeted_selected_edge',''),'targeted_selector_correct':r0.get('targeted_selector_correct',''),'final_slope_error_abs':abs(rows[-1]['slope_after']-target)}

def ci(v):return list(paired_bootstrap_ci(v,seed=19019,reps=10000))
def mean_for(c,st,k):
 q=[float(r[k]) for r in c if r['strategy']==st];return sum(q)/len(q)
def paired(c,a,b,k):
 by={(int(float(r['seed'])),r['strategy']):r for r in c};return [float(by[(s,a)][k])-float(by[(s,b)][k]) for s in SEEDS]
def rates(c,st):
 q=[r for r in c if r['strategy']==st];acc=[r for r in q if float(r['provenance_accepted'])==1];wrong=sum(1 for r in acc if float(r['accepted_partition_correct'])!=1)
 return {'coverage':len(acc)/200,'abstention':1-len(acc)/200,'precision':sum(float(r['accepted_partition_correct']) for r in acc)/len(acc) if acc else None,'wrong_acceptance':wrong/200}

def report_from(summaries,*vals):
 tau,k,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5,mu5t,nu5t=vals;cells=[];tar='targeted_replicated_selective_cumulative_provenance_quorum';full='replicated_selective_cumulative_provenance_quorum';tri='triad_persistence'
 for f,m in CELLS:
  c=[r for r in summaries if r['family']==f and float(r['magnitude'])==m];tr=rates(c,tar);fr=rates(c,full);r={'family':f,'magnitude':m,'targeted_rates':tr,'full_rates':fr,'mean_probe_energy':{st:mean_for(c,st,'probe_energy') for st in STRATEGIES},'adapt_401_420_rate':{st:mean_for(c,st,'adapt_401_420') for st in STRATEGIES},'mean_operational_loss_401_600':{st:mean_for(c,st,'operational_loss_401_600') for st in STRATEGIES},'mean_final_slope_error_abs':{st:mean_for(c,st,'final_slope_error_abs') for st in STRATEGIES}}
  tq=[x for x in c if x['strategy']==tar];entered=[x for x in tq if float(x['targeted_round5_executed'])==1];r['targeted_round5_execution_rate']=len(entered)/200;r['selector_correct_among_entered']=(sum(float(x['targeted_selector_correct']) for x in entered)/len(entered) if entered else None)
  if f=='drift_ab_gain050':
   d=paired(c,tar,full,'operational_loss_401_600');r['C1']={'coverage_gap_vs_full':tr['coverage']-fr['coverage'],'targeted_minus_full_loss_mean':sum(d)/200,'ci':ci(d),'energy_difference':r['mean_probe_energy'][tar]-r['mean_probe_energy'][full],'adapt_gap_vs_triad':r['adapt_401_420_rate'][tar]-r['adapt_401_420_rate'][tri]};r['C3']={'selector_correct_among_entered':r['selector_correct_among_entered']}
  if f=='drift_ab_fault':r['C2']={'adapt_gap_vs_triad':r['adapt_401_420_rate'][tar]-r['adapt_401_420_rate'][tri]}
  if f in ('drift_ab_gain0375','drift_ab_gain025','drift_ab_gain0125'):
   d=paired(c,tar,tri,'operational_loss_401_600');r['C4']={'targeted_minus_triad_mean':sum(d)/200,'ci':ci(d),'adapt_gap_vs_triad':r['adapt_401_420_rate'][tar]-r['adapt_401_420_rate'][tri]}
  if f=='drift':
   by={(int(float(x['seed'])),x['strategy']):x for x in c};v=[]
   for s in SEEDS:
    a=float(by[(s,tar)]['operational_loss_401_600']);b=float(by[(s,tri)]['operational_loss_401_600']);v.append((a-b)/max(abs(b),1e-12))
   r['C5']={'relative_excess_mean':sum(v)/200,'ci':ci(v),'adapt_gap_vs_triad':r['adapt_401_420_rate'][tar]-r['adapt_401_420_rate'][tri]}
  if f in ('common_mode','primary_fault'):
   d=paired(c,tar,full,'final_slope_error_abs');r['C6']={'targeted_minus_full_slope_error_mean':sum(d)/200,'ci':ci(d)}
  if f=='drift_all_aux_fault':
   d=paired(c,tar,tri,'operational_loss_401_600');r['C7']={'targeted_minus_triad_mean':sum(d)/200,'ci':ci(d)}
  cells.append(r)
 return {'tau':tau,'kappa':k,'kappa3':k3,'lambda_anchor_a':la,'lambda_anchor_b':lb,'lambda_anchor_c':lc,'lambda_anchor_ab':lab,'lambda_anchor_ac':lac,'lambda_anchor_bc':lbc,'lambda_probe_rounds':list(lambdas),'mu_cumulative_rounds':list(mu),'nu_cumulative_rounds':list(nu),'mu_5':mu5,'nu_5':nu5,'mu_5_targeted':mu5t,'nu_5_targeted':nu5t,'targeted_calibration_seeds':[4000,4999],'evaluation_seeds':[19000,19199],'bootstrap_seed':19019,'n_seeds_per_cell':200,'strategies':STRATEGIES,'cells':cells,'audit_seeds':sorted(AUDIT)}

def calibrations():
 tau=calibrate_tau();k=calibrate_kappa();k3=calibrate_kappa3();la=calibrate_lambda_anchor();lb,lab=calibrate_dual_anchor_thresholds();lc,lac,lbc=calibrate_anchor_c_thresholds();lambdas=calibrate_lambda_probe_rounds();mu,nu=calibrate_cumulative_thresholds();mu5,nu5=calibrate_round5_thresholds();mu5t,nu5t=calibrate_targeted_thresholds(mu,nu);return tau,k,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5,mu5t,nu5t

def main():
 vals=calibrations();summaries=[];audit=[]
 for f,m in CELLS:
  for seed in SEEDS:
   for st in STRATEGIES:
    rows=run_experiment_019_strategy(seed,f,m,st,*vals);summaries.append(summary(rows,f,m))
    if seed in AUDIT:audit.extend(dict(r,family=f,magnitude=m) for r in rows)
 write_csv(RESULTS/'seed_summary.csv',summaries);write_csv(RESULTS/'audit_trace_seeds_19000_19004.csv',audit);rep=report_from(summaries,*vals);RESULTS.mkdir(parents=True,exist_ok=True);(RESULTS/'report.json').write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps(rep,indent=2))
if __name__=='__main__':main()
