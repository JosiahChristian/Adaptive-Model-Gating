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
from experiment_015 import calibrate_lambda_probe,run_experiment_015_strategy
STRATEGIES=['frozen','continuous','threshold','persistence','health_persistence','triad_persistence','independent_persistence','naive_three_anchor_quorum','oracle_provenance_quorum','interventional_provenance_quorum']
CELLS=[('healthy',0.0)]+[(f,m) for f in ('drift','common_mode','primary_fault','drift_ab_fault','drift_ab_weak_probe','drift_ab_cross_coupled_probe','drift_all_aux_fault') for m in (.25,.5,1.0)]
SEEDS=list(range(15000,15200));AUDIT=set(range(15000,15005));RESULTS=ROOT/'results'/'experiment_015'
def write_csv(p,rows):
 p.parent.mkdir(parents=True,exist_ok=True);fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with p.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def summary(rows,f,m):
 p=[r for r in rows if 401<=r['t']<=600];a=[r for r in rows if r['t']>=401];p20=[r for r in rows if 401<=r['t']<=420];r0=rows[0];target=BASELINE_A+m if f.startswith('drift') else BASELINE_A;avg=lambda k:sum(float(r.get(k,0)) for r in a)/len(a)
 out={'seed':r0['seed'],'family':f,'magnitude':m,'strategy':r0['strategy'],'operational_loss_401_600':sum(r['sq_error'] for r in p),'latent_input_loss_401_600':sum(r['latent_input_sq_error'] for r in p),'adapt_401_420':int(any(r['adapt'] for r in p20)),'adapt_count_401_1200':sum(r['adapt'] for r in a),'common_mode_suspect_fraction':avg('common_mode_suspect'),'independent_veto_count':sum(r.get('independent_veto',0) for r in a),'inferred_group_a':r0['inferred_group_a'],'inferred_group_b':r0['inferred_group_b'],'inferred_group_c':r0['inferred_group_c'],'inferred_partition_correct':r0['inferred_partition_correct'],'probe_amplitude':r0['probe_amplitude'],'probe_cross_coupled':r0['probe_cross_coupled'],'mean_raw_mismatch_votes':avg('raw_mismatch_votes'),'mean_provenance_mismatch_votes':avg('provenance_mismatch_votes'),'final_slope':rows[-1]['slope_after'],'target_slope':target,'final_slope_error_abs':abs(rows[-1]['slope_after']-target)}
 for i in 'abc':
  for j in 'abc':out[f'probe_R_{i}{j}']=r0[f'probe_R_{i}{j}']
 return out
def means(c,k):return {s:sum(float(r[k]) for r in c if r['strategy']==s)/len(SEEDS) for s in STRATEGIES}
def ci(v):return list(paired_bootstrap_ci(v,seed=15015,reps=10000))
def report_from(summaries,tau,k,k3,la,lb,lab,lc,lac,lbc,lp):
 reps=[]
 for f,m in CELLS:
  c=[r for r in summaries if r['family']==f and float(r['magnitude'])==m];p={s:{st:next(r for r in c if int(float(r['seed']))==s and r['strategy']==st) for st in STRATEGIES} for s in SEEDS};rep={'family':f,'magnitude':m,'mean_operational_loss_401_600':means(c,'operational_loss_401_600'),'mean_final_slope_error_abs':means(c,'final_slope_error_abs'),'adapt_401_420_rate':means(c,'adapt_401_420'),'mean_veto_count':means(c,'independent_veto_count'),'mean_partition_correct':means(c,'inferred_partition_correct')}
  if f=='drift_ab_fault':
   d=[p[s]['interventional_provenance_quorum']['operational_loss_401_600']-p[s]['naive_three_anchor_quorum']['operational_loss_401_600'] for s in SEEDS];o=[p[s]['interventional_provenance_quorum']['operational_loss_401_600']-p[s]['oracle_provenance_quorum']['operational_loss_401_600'] for s in SEEDS];rep['C1_mean']=sum(d)/200;rep['C1_bootstrap_95_ci']=ci(d);rep['C1_adapt_gap_vs_triad']=rep['adapt_401_420_rate']['interventional_provenance_quorum']-rep['adapt_401_420_rate']['triad_persistence'];rep['C1_partition_correct_rate']=rep['mean_partition_correct']['interventional_provenance_quorum'];rep['C2_mean']=sum(o)/200;rep['C2_bootstrap_95_ci']=ci(o);rep['C2_oracle_loss_mean']=rep['mean_operational_loss_401_600']['oracle_provenance_quorum']
  if f=='common_mode':
   d=[p[s]['interventional_provenance_quorum']['final_slope_error_abs']-p[s]['triad_persistence']['final_slope_error_abs'] for s in SEEDS];rep['C3_mean']=sum(d)/200;rep['C3_bootstrap_95_ci']=ci(d)
  if f=='drift':
   rr=[(p[s]['interventional_provenance_quorum']['operational_loss_401_600']-p[s]['triad_persistence']['operational_loss_401_600'])/max(abs(p[s]['triad_persistence']['operational_loss_401_600']),1e-12) for s in SEEDS];rep['C4_mean_R']=sum(rr)/200;rep['C4_bootstrap_95_ci']=ci(rr);rep['C4_adapt_gap_vs_triad']=rep['adapt_401_420_rate']['interventional_provenance_quorum']-rep['adapt_401_420_rate']['triad_persistence']
  if f=='primary_fault':
   d=[p[s]['interventional_provenance_quorum']['final_slope_error_abs']-p[s]['triad_persistence']['final_slope_error_abs'] for s in SEEDS];rep['C5_mean']=sum(d)/200;rep['C5_bootstrap_95_ci']=ci(d)
  if f in ('drift_ab_weak_probe','drift_ab_cross_coupled_probe'):
   d1=[p[s]['interventional_provenance_quorum']['operational_loss_401_600']-p[s]['naive_three_anchor_quorum']['operational_loss_401_600'] for s in SEEDS];d2=[p[s]['interventional_provenance_quorum']['operational_loss_401_600']-p[s]['oracle_provenance_quorum']['operational_loss_401_600'] for s in SEEDS];key='C6' if f=='drift_ab_weak_probe' else 'C7';rep[key+'_interventional_minus_naive_mean']=sum(d1)/200;rep[key+'_interventional_minus_naive_ci']=ci(d1);rep[key+'_interventional_minus_oracle_mean']=sum(d2)/200;rep[key+'_interventional_minus_oracle_ci']=ci(d2);rep[key+'_partition_correct_rate']=rep['mean_partition_correct']['interventional_provenance_quorum'];rep[key+'_adapt_gap_vs_triad']=rep['adapt_401_420_rate']['interventional_provenance_quorum']-rep['adapt_401_420_rate']['triad_persistence']
  if f=='drift_all_aux_fault':
   d=[p[s]['interventional_provenance_quorum']['operational_loss_401_600']-p[s]['triad_persistence']['operational_loss_401_600'] for s in SEEDS];rep['C8_mean']=sum(d)/200;rep['C8_bootstrap_95_ci']=ci(d);rep['C8_adapt_gap_vs_triad']=rep['adapt_401_420_rate']['interventional_provenance_quorum']-rep['adapt_401_420_rate']['triad_persistence']
  reps.append(rep)
 return {'tau':tau,'kappa':k,'kappa3':k3,'lambda_anchor_a':la,'lambda_anchor_b':lb,'lambda_anchor_ab':lab,'lambda_anchor_c':lc,'lambda_anchor_ac':lac,'lambda_anchor_bc':lbc,'lambda_probe':lp,'probe_calibration_seeds':[1600,1799],'evaluation_seeds':[15000,15199],'bootstrap_seed':15015,'delta_probe':0.20,'sigma_probe':0.05,'gamma_probe':0.80,'n_seeds_per_cell':200,'strategies':STRATEGIES,'cells':reps,'audit_seeds':sorted(AUDIT)}
def calibrations():
 tau=calibrate_tau();k=calibrate_kappa();k3=calibrate_kappa3();la=calibrate_lambda_anchor();lb,lab=calibrate_dual_anchor_thresholds();lc,lac,lbc=calibrate_anchor_c_thresholds();lp=calibrate_lambda_probe();return tau,k,k3,la,lb,lab,lc,lac,lbc,lp
def main():
 vals=calibrations();summaries=[];audit=[]
 for f,m in CELLS:
  for seed in SEEDS:
   for st in STRATEGIES:
    rows=run_experiment_015_strategy(seed,f,m,st,*vals);summaries.append(summary(rows,f,m))
    if seed in AUDIT:audit.extend(dict(r,family=f,magnitude=m) for r in rows)
 write_csv(RESULTS/'seed_summary.csv',summaries);write_csv(RESULTS/'audit_trace_seeds_15000_15004.csv',audit);rep=report_from(summaries,*vals);RESULTS.mkdir(parents=True,exist_ok=True);(RESULTS/'report.json').write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps(rep,indent=2))
if __name__=='__main__':main()
