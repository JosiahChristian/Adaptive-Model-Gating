#!/usr/bin/env python3
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from adaptive_model_gating import BASELINE_A,EVENT_T,calibrate_tau,paired_bootstrap_ci
from experiment_008 import calibrate_kappa
from experiment_010 import calibrate_kappa3
from experiment_011 import calibrate_lambda_anchor
from experiment_012 import calibrate_dual_anchor_thresholds,run_experiment_012_strategy
STRATEGIES=['frozen','continuous','threshold','persistence','health_persistence','triad_persistence','independent_persistence','dual_independent_arbitration']
CELLS=[('healthy',0.0)]+[(f,m) for f in ('drift','common_mode','primary_fault','drift_anchor_a_fault','drift_anchor_b_fault','drift_dual_anchor_fault') for m in (.25,.5,1.0)]
SEEDS=list(range(12000,12200));AUDIT=set(range(12000,12005));RESULTS=ROOT/'results'/'experiment_012'
def write_csv(p,rows):
 p.parent.mkdir(parents=True,exist_ok=True);fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with p.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def summary(rows,f,m):
 p200=[r for r in rows if 401<=r['t']<=600];pall=[r for r in rows if r['t']>=401];p20=[r for r in rows if 401<=r['t']<=420];ats=[r['t'] for r in pall if r['adapt']];target=BASELINE_A+m if f in ('drift','drift_anchor_a_fault','drift_anchor_b_fault','drift_dual_anchor_fault') else BASELINE_A
 return {'seed':rows[0]['seed'],'family':f,'magnitude':m,'strategy':rows[0]['strategy'],'operational_loss_401_600':sum(r['sq_error'] for r in p200),'latent_input_loss_401_600':sum(r['latent_input_sq_error'] for r in p200),'adapt_401_420':int(any(r['adapt'] for r in p20)),'adapt_count_401_1200':sum(r['adapt'] for r in pall),'anchor_mismatch_fraction':sum(r['anchor_mismatch'] for r in pall)/len(pall),'anchor_b_mismatch_fraction':sum(r['anchor_b_mismatch'] for r in pall)/len(pall),'anchor_ab_disagreement_fraction':sum(r['anchor_ab_disagreement'] for r in pall)/len(pall),'common_mode_suspect_fraction':sum(r['common_mode_suspect'] for r in pall)/len(pall),'independent_veto_count':sum(r.get('independent_veto',0) for r in pall),'final_slope':rows[-1]['slope_after'],'target_slope':target,'final_slope_error_abs':abs(rows[-1]['slope_after']-target)}
def means(rows,k):return {s:sum(r[k] for r in rows if r['strategy']==s)/len(SEEDS) for s in STRATEGIES}
def ci(v):return list(paired_bootstrap_ci(v,seed=12012,reps=10000))
def report_from(summaries,tau,k,k3,la,lb,lab):
 reports=[]
 for f,m in CELLS:
  c=[r for r in summaries if r['family']==f and float(r['magnitude'])==m];p={s:{st:next(r for r in c if int(r['seed'])==s and r['strategy']==st) for st in STRATEGIES} for s in SEEDS}
  rep={'family':f,'magnitude':m,'mean_operational_loss_401_600':means(c,'operational_loss_401_600'),'mean_final_slope_error_abs':means(c,'final_slope_error_abs'),'adapt_401_420_rate':means(c,'adapt_401_420'),'mean_anchor_a_mismatch_fraction':means(c,'anchor_mismatch_fraction'),'mean_anchor_b_mismatch_fraction':means(c,'anchor_b_mismatch_fraction'),'mean_anchor_ab_disagreement_fraction':means(c,'anchor_ab_disagreement_fraction'),'mean_common_mode_suspect_fraction':means(c,'common_mode_suspect_fraction'),'mean_independent_veto_count':means(c,'independent_veto_count')}
  if f=='common_mode':
   d=[p[s]['dual_independent_arbitration']['final_slope_error_abs']-p[s]['triad_persistence']['final_slope_error_abs'] for s in SEEDS];rep['C1_dual_minus_triad_final_slope_error_mean']=sum(d)/200;rep['C1_bootstrap_95_ci']=ci(d)
  if f=='drift_anchor_a_fault':
   d=[p[s]['dual_independent_arbitration']['operational_loss_401_600']-p[s]['independent_persistence']['operational_loss_401_600'] for s in SEEDS];rep['C2_dual_minus_independent_early_loss_mean']=sum(d)/200;rep['C2_bootstrap_95_ci']=ci(d);rep['C2_adapt_rate_gap_vs_triad']=rep['adapt_401_420_rate']['dual_independent_arbitration']-rep['adapt_401_420_rate']['triad_persistence']
  if f=='drift_anchor_b_fault':
   d=[p[s]['dual_independent_arbitration']['operational_loss_401_600']-p[s]['triad_persistence']['operational_loss_401_600'] for s in SEEDS];rep['anchor_b_dual_minus_triad_early_loss_mean']=sum(d)/200;rep['anchor_b_bootstrap_95_ci']=ci(d)
  if f=='drift':
   rr=[(p[s]['dual_independent_arbitration']['operational_loss_401_600']-p[s]['triad_persistence']['operational_loss_401_600'])/max(abs(p[s]['triad_persistence']['operational_loss_401_600']),1e-12) for s in SEEDS];rep['C3_mean_R']=sum(rr)/200;rep['C3_bootstrap_95_ci']=ci(rr);rep['C3_upper_lt_0_10']=rep['C3_bootstrap_95_ci'][1]<.10
  if f=='primary_fault':
   d=[p[s]['dual_independent_arbitration']['final_slope_error_abs']-p[s]['triad_persistence']['final_slope_error_abs'] for s in SEEDS];rep['C4_dual_minus_triad_final_slope_error_mean']=sum(d)/200;rep['C4_bootstrap_95_ci']=ci(d)
  if f=='drift_dual_anchor_fault':
   d=[p[s]['dual_independent_arbitration']['operational_loss_401_600']-p[s]['triad_persistence']['operational_loss_401_600'] for s in SEEDS];rep['C5_dual_minus_triad_early_loss_mean']=sum(d)/200;rep['C5_bootstrap_95_ci']=ci(d);rep['C5_adapt_rate_gap']=rep['adapt_401_420_rate']['dual_independent_arbitration']-rep['adapt_401_420_rate']['triad_persistence']
  reports.append(rep)
 return {'tau':tau,'kappa':k,'kappa3':k3,'lambda_anchor_a':la,'lambda_anchor_b':lb,'lambda_anchor_ab':lab,'anchor_a_calibration_seeds':[600,799],'dual_calibration_seeds':[800,999],'evaluation_seeds':[12000,12199],'bootstrap_seed':12012,'n_seeds_per_cell':200,'strategies':STRATEGIES,'cells':reports,'audit_seeds':sorted(AUDIT)}
def main():
 tau=calibrate_tau();k=calibrate_kappa();k3=calibrate_kappa3();la=calibrate_lambda_anchor();lb,lab=calibrate_dual_anchor_thresholds();summaries=[];audit=[]
 for f,m in CELLS:
  for seed in SEEDS:
   for st in STRATEGIES:
    rows=run_experiment_012_strategy(seed,f,m,st,tau,k,k3,la,lb,lab);summaries.append(summary(rows,f,m))
    if seed in AUDIT:audit.extend(dict(r,family=f,magnitude=m) for r in rows)
 write_csv(RESULTS/'seed_summary.csv',summaries);write_csv(RESULTS/'audit_trace_seeds_12000_12004.csv',audit);rep=report_from(summaries,tau,k,k3,la,lb,lab);RESULTS.mkdir(parents=True,exist_ok=True);(RESULTS/'report.json').write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps(rep,indent=2))
if __name__=='__main__':main()
