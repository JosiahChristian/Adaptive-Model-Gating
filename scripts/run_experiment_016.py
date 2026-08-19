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
from experiment_016 import calibrate_lambda_probe_rounds,run_experiment_016_strategy

STRATEGIES=['frozen','continuous','threshold','persistence','health_persistence','triad_persistence','independent_persistence','naive_three_anchor_quorum','oracle_provenance_quorum','max_probe_provenance_quorum','sequential_provenance_quorum']
CELLS=[('healthy',0.0)]+[(f,m) for f in ('drift','common_mode','primary_fault','drift_ab_fault','drift_ab_gain050','drift_ab_gain025','drift_all_aux_fault') for m in (.25,.5,1.0)]
SEEDS=list(range(16000,16200));AUDIT=set(range(16000,16005));RESULTS=ROOT/'results'/'experiment_016'

def write_csv(p,rows):
 p.parent.mkdir(parents=True,exist_ok=True);fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with p.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def summary(rows,f,m):
 p=[r for r in rows if 401<=r['t']<=600];a=[r for r in rows if r['t']>=401];p20=[r for r in rows if 401<=r['t']<=420];r0=rows[0];target=BASELINE_A+m if f.startswith('drift') else BASELINE_A;avg=lambda k:sum(float(r.get(k,0) or 0) for r in a)/len(a)
 return {'seed':r0['seed'],'family':f,'magnitude':m,'strategy':r0['strategy'],'operational_loss_401_600':sum(r['sq_error'] for r in p),'latent_input_loss_401_600':sum(r['latent_input_sq_error'] for r in p),'adapt_401_420':int(any(r['adapt'] for r in p20)),'adapt_count_401_1200':sum(r['adapt'] for r in a),'common_mode_suspect_fraction':avg('common_mode_suspect'),'independent_veto_count':sum(r.get('independent_veto',0) for r in a),'inferred_group_a':r0['inferred_group_a'],'inferred_group_b':r0['inferred_group_b'],'inferred_group_c':r0['inferred_group_c'],'inferred_partition_correct':r0['inferred_partition_correct'],'probe_gain':r0['probe_gain'],'probe_stop_round':r0['probe_stop_round'],'probe_decisive':r0['probe_decisive'],'probe_max_amplitude':r0['probe_max_amplitude'],'probe_block_count':r0['probe_block_count'],'probe_energy':r0['probe_energy'],'mean_raw_mismatch_votes':avg('raw_mismatch_votes'),'mean_provenance_mismatch_votes':avg('provenance_mismatch_votes'),'final_slope':rows[-1]['slope_after'],'target_slope':target,'final_slope_error_abs':abs(rows[-1]['slope_after']-target)}

def means(c,k):return {s:sum(float(r[k]) for r in c if r['strategy']==s)/len(SEEDS) for s in STRATEGIES}
def ci(v):return list(paired_bootstrap_ci(v,seed=16016,reps=10000))

def report_from(summaries,tau,k,k3,la,lb,lc,lab,lac,lbc,thresholds):
 reps=[]
 for f,m in CELLS:
  c=[r for r in summaries if r['family']==f and float(r['magnitude'])==m];p={seed:{st:next(r for r in c if int(float(r['seed']))==seed and r['strategy']==st) for st in STRATEGIES} for seed in SEEDS}
  rep={'family':f,'magnitude':m,'mean_operational_loss_401_600':means(c,'operational_loss_401_600'),'mean_final_slope_error_abs':means(c,'final_slope_error_abs'),'adapt_401_420_rate':means(c,'adapt_401_420'),'mean_veto_count':means(c,'independent_veto_count'),'mean_partition_correct':means(c,'inferred_partition_correct'),'mean_probe_energy':means(c,'probe_energy'),'mean_probe_stop_round':means(c,'probe_stop_round'),'mean_probe_max_amplitude':means(c,'probe_max_amplitude')}
  if f=='drift_ab_fault':
   d=[p[s]['sequential_provenance_quorum']['operational_loss_401_600']-p[s]['naive_three_anchor_quorum']['operational_loss_401_600'] for s in SEEDS];do=[p[s]['sequential_provenance_quorum']['operational_loss_401_600']-p[s]['oracle_provenance_quorum']['operational_loss_401_600'] for s in SEEDS];de=[p[s]['sequential_provenance_quorum']['probe_energy']-p[s]['max_probe_provenance_quorum']['probe_energy'] for s in SEEDS]
   rep.update(C1_mean=sum(d)/200,C1_bootstrap_95_ci=ci(d),C1_adapt_gap_vs_triad=rep['adapt_401_420_rate']['sequential_provenance_quorum']-rep['adapt_401_420_rate']['triad_persistence'],C1_partition_correct_rate=rep['mean_partition_correct']['sequential_provenance_quorum'],C2_seq_minus_oracle_mean=sum(do)/200,C2_seq_minus_oracle_ci=ci(do),C2_oracle_loss_mean=rep['mean_operational_loss_401_600']['oracle_provenance_quorum'],C2_seq_minus_max_energy_mean=sum(de)/200,C2_seq_energy_mean=rep['mean_probe_energy']['sequential_provenance_quorum'],C2_max_energy_mean=rep['mean_probe_energy']['max_probe_provenance_quorum'])
  if f=='drift_ab_gain050':
   d=[p[s]['sequential_provenance_quorum']['operational_loss_401_600']-p[s]['max_probe_provenance_quorum']['operational_loss_401_600'] for s in SEEDS];rep.update(C3_mean=sum(d)/200,C3_bootstrap_95_ci=ci(d),C3_max_loss_mean=rep['mean_operational_loss_401_600']['max_probe_provenance_quorum'],C3_partition_correct_rate=rep['mean_partition_correct']['sequential_provenance_quorum'],C3_adapt_gap_vs_triad=rep['adapt_401_420_rate']['sequential_provenance_quorum']-rep['adapt_401_420_rate']['triad_persistence'],C3_seq_energy_mean=rep['mean_probe_energy']['sequential_provenance_quorum'])
  if f=='drift_ab_gain025':
   dm=[p[s]['sequential_provenance_quorum']['operational_loss_401_600']-p[s]['max_probe_provenance_quorum']['operational_loss_401_600'] for s in SEEDS];do=[p[s]['sequential_provenance_quorum']['operational_loss_401_600']-p[s]['oracle_provenance_quorum']['operational_loss_401_600'] for s in SEEDS];rep.update(C4_seq_minus_max_mean=sum(dm)/200,C4_seq_minus_max_ci=ci(dm),C4_seq_minus_oracle_mean=sum(do)/200,C4_seq_minus_oracle_ci=ci(do),C4_partition_correct_rate=rep['mean_partition_correct']['sequential_provenance_quorum'],C4_adapt_gap_vs_triad=rep['adapt_401_420_rate']['sequential_provenance_quorum']-rep['adapt_401_420_rate']['triad_persistence'],C4_seq_energy_mean=rep['mean_probe_energy']['sequential_provenance_quorum'])
  if f=='drift':
   rr=[(p[s]['sequential_provenance_quorum']['operational_loss_401_600']-p[s]['triad_persistence']['operational_loss_401_600'])/max(abs(p[s]['triad_persistence']['operational_loss_401_600']),1e-12) for s in SEEDS];rep.update(C5_mean_R=sum(rr)/200,C5_bootstrap_95_ci=ci(rr),C5_adapt_gap_vs_triad=rep['adapt_401_420_rate']['sequential_provenance_quorum']-rep['adapt_401_420_rate']['triad_persistence'])
  if f=='common_mode':
   d=[p[s]['sequential_provenance_quorum']['final_slope_error_abs']-p[s]['triad_persistence']['final_slope_error_abs'] for s in SEEDS];rep.update(C6_mean=sum(d)/200,C6_bootstrap_95_ci=ci(d))
  if f=='primary_fault':
   d=[p[s]['sequential_provenance_quorum']['final_slope_error_abs']-p[s]['triad_persistence']['final_slope_error_abs'] for s in SEEDS];rep.update(C7_mean=sum(d)/200,C7_bootstrap_95_ci=ci(d))
  if f=='drift_all_aux_fault':
   d=[p[s]['sequential_provenance_quorum']['operational_loss_401_600']-p[s]['triad_persistence']['operational_loss_401_600'] for s in SEEDS];rep.update(C8_mean=sum(d)/200,C8_bootstrap_95_ci=ci(d),C8_adapt_gap_vs_triad=rep['adapt_401_420_rate']['sequential_provenance_quorum']-rep['adapt_401_420_rate']['triad_persistence'],C8_seq_energy_mean=rep['mean_probe_energy']['sequential_provenance_quorum'])
  reps.append(rep)
 return {'tau':tau,'kappa':k,'kappa3':k3,'lambda_anchor_a':la,'lambda_anchor_b':lb,'lambda_anchor_c':lc,'lambda_anchor_ab':lab,'lambda_anchor_ac':lac,'lambda_anchor_bc':lbc,'lambda_probe_rounds':list(thresholds),'probe_calibration_seeds':[1800,1999],'evaluation_seeds':[16000,16199],'bootstrap_seed':16016,'probe_amplitudes':[.025,.05,.1,.2],'sigma_probe':.05,'n_seeds_per_cell':200,'strategies':STRATEGIES,'cells':reps,'audit_seeds':sorted(AUDIT)}

def calibrations():
 tau=calibrate_tau();k=calibrate_kappa();k3=calibrate_kappa3();la=calibrate_lambda_anchor();lb,lab=calibrate_dual_anchor_thresholds();lc,lac,lbc=calibrate_anchor_c_thresholds();thresholds=calibrate_lambda_probe_rounds();return tau,k,k3,la,lb,lc,lab,lac,lbc,thresholds

def main():
 vals=calibrations();summaries=[];audit=[]
 for f,m in CELLS:
  for seed in SEEDS:
   for st in STRATEGIES:
    rows=run_experiment_016_strategy(seed,f,m,st,*vals);summaries.append(summary(rows,f,m))
    if seed in AUDIT:audit.extend(dict(r,family=f,magnitude=m) for r in rows)
 write_csv(RESULTS/'seed_summary.csv',summaries);write_csv(RESULTS/'audit_trace_seeds_16000_16004.csv',audit);rep=report_from(summaries,*vals);RESULTS.mkdir(parents=True,exist_ok=True);(RESULTS/'report.json').write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps(rep,indent=2))
if __name__=='__main__':main()
