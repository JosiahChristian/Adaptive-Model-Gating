#!/usr/bin/env python3
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from adaptive_model_gating import BASELINE_A,calibrate_tau,paired_bootstrap_ci
from experiment_008 import calibrate_kappa
from experiment_010 import calibrate_kappa3
from experiment_011 import calibrate_lambda_anchor
from experiment_012 import calibrate_dual_anchor_thresholds
from experiment_013 import calibrate_anchor_c_thresholds,run_experiment_013_strategy
STRATEGIES=['frozen','continuous','threshold','persistence','health_persistence','triad_persistence','independent_persistence','naive_three_anchor_quorum','provenance_aware_quorum']
CELLS=[('healthy',0.0)]+[(f,m) for f in ('drift','common_mode','primary_fault','drift_g1_common_fault','drift_g2_fault','drift_misdeclared_g1_fault','drift_all_aux_fault') for m in (.25,.5,1.0)]
SEEDS=list(range(13000,13200));AUDIT=set(range(13000,13005));RESULTS=ROOT/'results'/'experiment_013'
def write_csv(p,rows):
 p.parent.mkdir(parents=True,exist_ok=True);fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with p.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def summary(rows,f,m):
 p=[r for r in rows if 401<=r['t']<=600];allr=[r for r in rows if r['t']>=401];p20=[r for r in rows if 401<=r['t']<=420];target=BASELINE_A+m if f.startswith('drift') else BASELINE_A
 avg=lambda k:sum(r.get(k,0) for r in allr)/len(allr)
 return {'seed':rows[0]['seed'],'family':f,'magnitude':m,'strategy':rows[0]['strategy'],'operational_loss_401_600':sum(r['sq_error'] for r in p),'latent_input_loss_401_600':sum(r['latent_input_sq_error'] for r in p),'adapt_401_420':int(any(r['adapt'] for r in p20)),'adapt_count_401_1200':sum(r['adapt'] for r in allr),'anchor_a_mismatch_fraction':avg('anchor_mismatch'),'anchor_b_mismatch_fraction':avg('anchor_b_mismatch'),'anchor_c_mismatch_fraction':avg('anchor_c_mismatch'),'anchor_ab_disagreement_fraction':avg('anchor_ab_disagreement'),'anchor_ac_disagreement_fraction':avg('anchor_ac_disagreement'),'anchor_bc_disagreement_fraction':avg('anchor_bc_disagreement'),'raw_mismatch_votes_mean':avg('raw_mismatch_votes'),'provenance_mismatch_votes_mean':avg('provenance_mismatch_votes'),'common_mode_suspect_fraction':avg('common_mode_suspect'),'independent_veto_count':sum(r.get('independent_veto',0) for r in allr),'final_slope':rows[-1]['slope_after'],'target_slope':target,'final_slope_error_abs':abs(rows[-1]['slope_after']-target)}
def means(rows,k):return {s:sum(r[k] for r in rows if r['strategy']==s)/len(SEEDS) for s in STRATEGIES}
def ci(v):return list(paired_bootstrap_ci(v,seed=13013,reps=10000))
def report_from(summaries,tau,k,k3,la,lb,lab,lc,lac,lbc):
 reports=[]
 for f,m in CELLS:
  c=[r for r in summaries if r['family']==f and float(r['magnitude'])==m];p={s:{st:next(r for r in c if int(r['seed'])==s and r['strategy']==st) for st in STRATEGIES} for s in SEEDS};rep={'family':f,'magnitude':m,'mean_operational_loss_401_600':means(c,'operational_loss_401_600'),'mean_final_slope_error_abs':means(c,'final_slope_error_abs'),'adapt_401_420_rate':means(c,'adapt_401_420'),'mean_independent_veto_count':means(c,'independent_veto_count')}
  if f=='common_mode':d=[p[s]['provenance_aware_quorum']['final_slope_error_abs']-p[s]['triad_persistence']['final_slope_error_abs'] for s in SEEDS];rep.update(C1_mean=sum(d)/200,C1_bootstrap_95_ci=ci(d))
  if f=='drift_g1_common_fault':d=[p[s]['provenance_aware_quorum']['operational_loss_401_600']-p[s]['naive_three_anchor_quorum']['operational_loss_401_600'] for s in SEEDS];rep.update(C2_mean=sum(d)/200,C2_bootstrap_95_ci=ci(d),C2_adapt_gap_vs_triad=rep['adapt_401_420_rate']['provenance_aware_quorum']-rep['adapt_401_420_rate']['triad_persistence'])
  if f in ('drift_g2_fault','drift'):
   rr=[(p[s]['provenance_aware_quorum']['operational_loss_401_600']-p[s]['triad_persistence']['operational_loss_401_600'])/max(abs(p[s]['triad_persistence']['operational_loss_401_600']),1e-12) for s in SEEDS];key='C3' if f=='drift_g2_fault' else 'C4';rep[key+'_mean_R']=sum(rr)/200;rep[key+'_bootstrap_95_ci']=ci(rr);rep[key+'_adapt_gap_vs_triad']=rep['adapt_401_420_rate']['provenance_aware_quorum']-rep['adapt_401_420_rate']['triad_persistence']
  if f=='primary_fault':d=[p[s]['provenance_aware_quorum']['final_slope_error_abs']-p[s]['triad_persistence']['final_slope_error_abs'] for s in SEEDS];rep.update(C5_mean=sum(d)/200,C5_bootstrap_95_ci=ci(d))
  if f in ('drift_misdeclared_g1_fault','drift_all_aux_fault'):
   d=[p[s]['provenance_aware_quorum']['operational_loss_401_600']-p[s]['triad_persistence']['operational_loss_401_600'] for s in SEEDS];key='C6' if f=='drift_misdeclared_g1_fault' else 'C7';rep[key+'_mean']=sum(d)/200;rep[key+'_bootstrap_95_ci']=ci(d);rep[key+'_adapt_gap_vs_triad']=rep['adapt_401_420_rate']['provenance_aware_quorum']-rep['adapt_401_420_rate']['triad_persistence']
  reports.append(rep)
 return {'tau':tau,'kappa':k,'kappa3':k3,'lambda_anchor_a':la,'lambda_anchor_b':lb,'lambda_anchor_ab':lab,'lambda_anchor_c':lc,'lambda_anchor_ac':lac,'lambda_anchor_bc':lbc,'anchor_c_calibration_seeds':[1000,1199],'evaluation_seeds':[13000,13199],'bootstrap_seed':13013,'n_seeds_per_cell':200,'strategies':STRATEGIES,'cells':reports,'audit_seeds':sorted(AUDIT)}
def main():
 tau=calibrate_tau();k=calibrate_kappa();k3=calibrate_kappa3();la=calibrate_lambda_anchor();lb,lab=calibrate_dual_anchor_thresholds();lc,lac,lbc=calibrate_anchor_c_thresholds();summaries=[];audit=[]
 for f,m in CELLS:
  for seed in SEEDS:
   for st in STRATEGIES:
    rows=run_experiment_013_strategy(seed,f,m,st,tau,k,k3,la,lb,lc,lab,lac,lbc);summaries.append(summary(rows,f,m))
    if seed in AUDIT:audit.extend(dict(r,family=f,magnitude=m) for r in rows)
 write_csv(RESULTS/'seed_summary.csv',summaries);write_csv(RESULTS/'audit_trace_seeds_13000_13004.csv',audit);rep=report_from(summaries,tau,k,k3,la,lb,lab,lc,lac,lbc);RESULTS.mkdir(parents=True,exist_ok=True);(RESULTS/'report.json').write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps(rep,indent=2))
if __name__=='__main__':main()
