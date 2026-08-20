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
from experiment_018 import calibrate_round5_thresholds,run_experiment_018_strategy

STRATEGIES=['frozen','continuous','threshold','persistence','health_persistence','triad_persistence','independent_persistence','naive_three_anchor_quorum','oracle_provenance_quorum','max_probe_provenance_quorum','sequential_provenance_quorum','cumulative_provenance_quorum','selective_cumulative_provenance_quorum','replicated_selective_cumulative_provenance_quorum']
CELLS=[('healthy',0.0)]+[(f,m) for f in ('drift','common_mode','primary_fault','drift_ab_fault','drift_ab_gain050','drift_ab_gain0375','drift_ab_gain025','drift_ab_gain0125','drift_all_aux_fault') for m in (.25,.5,1.0)]
SEEDS=list(range(18000,18200));AUDIT=set(range(18000,18005));RESULTS=ROOT/'results'/'experiment_018'

def write_csv(p,rows):
 p.parent.mkdir(parents=True,exist_ok=True);fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with p.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def summary(rows,f,m):
 p=[r for r in rows if 401<=r['t']<=600];a=[r for r in rows if r['t']>=401];p20=[r for r in rows if 401<=r['t']<=420];r0=rows[0];target=BASELINE_A+m if f.startswith('drift') else BASELINE_A
 return {'seed':r0['seed'],'family':f,'magnitude':m,'strategy':r0['strategy'],'operational_loss_401_600':sum(r['sq_error'] for r in p),'latent_input_loss_401_600':sum(r['latent_input_sq_error'] for r in p),'adapt_401_420':int(any(r['adapt'] for r in p20)),'adapt_count_401_1200':sum(r['adapt'] for r in a),'probe_gain':r0.get('probe_gain',0),'probe_stop_round':r0.get('probe_stop_round',0),'probe_energy':r0.get('probe_energy',0),'provenance_accepted':r0.get('provenance_accepted',0),'provenance_abstain':r0.get('provenance_abstain',0),'accepted_partition_correct':r0.get('accepted_partition_correct',''),'candidate_partition_correct':r0.get('candidate_partition_correct',r0.get('inferred_partition_correct','')),'inferred_partition_correct':r0.get('inferred_partition_correct',''),'round5_executed':r0.get('round5_executed',0),'round5_rescued_acceptance':r0.get('round5_rescued_acceptance',0),'round5_rescued_correct':r0.get('round5_rescued_correct',''),'final_slope':rows[-1]['slope_after'],'target_slope':target,'final_slope_error_abs':abs(rows[-1]['slope_after']-target)}

def ci(v):return list(paired_bootstrap_ci(v,seed=18018,reps=10000))
def mean_for(c,st,k):
 q=[float(r[k]) for r in c if r['strategy']==st];return sum(q)/len(q)
def paired(c,a,b,k):
 by={(int(float(r['seed'])),r['strategy']):r for r in c};return [float(by[(s,a)][k])-float(by[(s,b)][k]) for s in SEEDS]
def rates(c,st):
 q=[r for r in c if r['strategy']==st];acc=[r for r in q if float(r['provenance_accepted'])==1];wrong=sum(1 for r in acc if float(r['accepted_partition_correct'])!=1)
 return {'deployment_coverage':len(acc)/200,'abstention_rate':1-len(acc)/200,'accepted_partition_precision':(sum(float(r['accepted_partition_correct']) for r in acc)/len(acc) if acc else None),'wrong_acceptance_rate':wrong/200}

def report_from(summaries,*vals):
 tau,k,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5=vals;cells=[];rep='replicated_selective_cumulative_provenance_quorum';sel='selective_cumulative_provenance_quorum';tri='triad_persistence';naive='naive_three_anchor_quorum'
 for f,m in CELLS:
  c=[r for r in summaries if r['family']==f and float(r['magnitude'])==m];rr=rates(c,rep);sr=rates(c,sel)
  r={'family':f,'magnitude':m,'replicated_rates':rr,'original_selective_rates':sr,'mean_probe_energy':{st:mean_for(c,st,'probe_energy') for st in STRATEGIES},'adapt_401_420_rate':{st:mean_for(c,st,'adapt_401_420') for st in STRATEGIES},'mean_operational_loss_401_600':{st:mean_for(c,st,'operational_loss_401_600') for st in STRATEGIES},'mean_final_slope_error_abs':{st:mean_for(c,st,'final_slope_error_abs') for st in STRATEGIES}}
  rq=[x for x in c if x['strategy']==rep];resc=[x for x in rq if float(x['round5_rescued_acceptance'])==1];r['round5_execution_rate']=sum(float(x['round5_executed']) for x in rq)/200;r['round5_rescue_rate']=len(resc)/200;r['rescue_fraction_among_round4_abstainers']=(len(resc)/(200*(1-sr['deployment_coverage'])) if sr['deployment_coverage']<1 else None);r['rescued_decision_precision']=(sum(float(x['round5_rescued_correct']) for x in resc)/len(resc) if resc else None)
  if f=='drift_ab_fault':
   d=paired(c,rep,naive,'operational_loss_401_600');r['C1']={'mean_replicated_minus_naive':sum(d)/200,'ci':ci(d),'adapt_gap_vs_triad':r['adapt_401_420_rate'][rep]-r['adapt_401_420_rate'][tri]}
  if f=='drift_ab_gain050':
   d=paired(c,rep,sel,'operational_loss_401_600');r['C2']={'round4_coverage':sr['deployment_coverage'],'final_coverage':rr['deployment_coverage'],'absolute_coverage_gain':rr['deployment_coverage']-sr['deployment_coverage'],'mean_replicated_minus_original':sum(d)/200,'ci':ci(d),'original_loss_mean':r['mean_operational_loss_401_600'][sel],'adapt_gap_vs_triad':r['adapt_401_420_rate'][rep]-r['adapt_401_420_rate'][tri]};r['C3']={'rescue_fraction_among_round4_abstainers':r['rescue_fraction_among_round4_abstainers'],'rescued_decision_precision':r['rescued_decision_precision'],'wrong_acceptance_increase':rr['wrong_acceptance_rate']-sr['wrong_acceptance_rate']};r['C6']={'replicated_energy':r['mean_probe_energy'][rep],'original_energy':r['mean_probe_energy'][sel],'round5_execution_rate':r['round5_execution_rate'],'energy_difference':r['mean_probe_energy'][rep]-r['mean_probe_energy'][sel]}
  if f in ('drift_ab_gain0375','drift_ab_gain025'):
   dt=paired(c,rep,tri,'operational_loss_401_600');do=paired(c,rep,sel,'operational_loss_401_600');r['C4']={'mean_replicated_minus_triad':sum(dt)/200,'ci_vs_triad':ci(dt),'mean_replicated_minus_original':sum(do)/200,'ci_vs_original':ci(do),'adapt_gap_vs_triad':r['adapt_401_420_rate'][rep]-r['adapt_401_420_rate'][tri],'coverage_gain':rr['deployment_coverage']-sr['deployment_coverage']}
  if f=='drift_ab_gain0125':
   dt=paired(c,rep,tri,'operational_loss_401_600');r['C5']={'mean_replicated_minus_triad':sum(dt)/200,'ci':ci(dt)}
  if f=='drift':
   by={(int(float(x['seed'])),x['strategy']):x for x in c};v=[]
   for s in SEEDS:
    Lr=float(by[(s,rep)]['operational_loss_401_600']);Lt=float(by[(s,tri)]['operational_loss_401_600']);v.append((Lr-Lt)/max(abs(Lt),1e-12))
   r['C7']={'mean_relative_excess':sum(v)/200,'ci':ci(v),'adapt_gap_vs_triad':r['adapt_401_420_rate'][rep]-r['adapt_401_420_rate'][tri]}
  if f=='common_mode':
   d=paired(c,rep,tri,'final_slope_error_abs');r['C8']={'mean_slope_error_difference':sum(d)/200,'ci':ci(d)}
  if f=='primary_fault':
   d=paired(c,rep,tri,'final_slope_error_abs');r['C9']={'mean_slope_error_difference':sum(d)/200,'ci':ci(d)}
  if f=='drift_all_aux_fault':
   d=paired(c,rep,tri,'operational_loss_401_600');r['C10']={'mean_replicated_minus_triad':sum(d)/200,'ci':ci(d)}
  cells.append(r)
 return {'tau':tau,'kappa':k,'kappa3':k3,'lambda_anchor_a':la,'lambda_anchor_b':lb,'lambda_anchor_c':lc,'lambda_anchor_ab':lab,'lambda_anchor_ac':lac,'lambda_anchor_bc':lbc,'lambda_probe_rounds':list(lambdas),'mu_cumulative_rounds':list(mu),'nu_cumulative_rounds':list(nu),'mu_5':mu5,'nu_5':nu5,'inherited_probe_calibration_seeds':[1800,1999],'inherited_cumulative_calibration_seeds':[2000,2999],'round5_calibration_seeds':[3000,3999],'evaluation_seeds':[18000,18199],'bootstrap_seed':18018,'n_seeds_per_cell':200,'strategies':STRATEGIES,'cells':cells,'audit_seeds':sorted(AUDIT)}

def calibrations():
 tau=calibrate_tau();k=calibrate_kappa();k3=calibrate_kappa3();la=calibrate_lambda_anchor();lb,lab=calibrate_dual_anchor_thresholds();lc,lac,lbc=calibrate_anchor_c_thresholds();lambdas=calibrate_lambda_probe_rounds();mu,nu=calibrate_cumulative_thresholds();mu5,nu5=calibrate_round5_thresholds();return tau,k,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5

def main():
 vals=calibrations();summaries=[];audit=[]
 for f,m in CELLS:
  for seed in SEEDS:
   for st in STRATEGIES:
    rows=run_experiment_018_strategy(seed,f,m,st,*vals);summaries.append(summary(rows,f,m))
    if seed in AUDIT:audit.extend(dict(r,family=f,magnitude=m) for r in rows)
 write_csv(RESULTS/'seed_summary.csv',summaries);write_csv(RESULTS/'audit_trace_seeds_18000_18004.csv',audit);rep=report_from(summaries,*vals);RESULTS.mkdir(parents=True,exist_ok=True);(RESULTS/'report.json').write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps(rep,indent=2))
if __name__=='__main__':main()
