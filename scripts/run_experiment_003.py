#!/usr/bin/env python3
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from adaptive_model_gating import calibrate_tau,run_gradual_drift_strategy,paired_bootstrap_ci,EVENT_T
RESULTS=ROOT/'results'/'experiment_003'; STRATEGIES=['frozen','continuous','threshold','persistence']; MAG=[.25,.5,1.0]; RAMPS=[20,50,100,200]; SEEDS=list(range(3000,3200)); AUDIT=set(range(3000,3005))
def write(path,rows):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
def main():
 tau=calibrate_tau(); summaries=[]; audit=[]
 for m in MAG:
  for ramp in RAMPS:
   for seed in SEEDS:
    for s in STRATEGIES:
     rows=run_gradual_drift_strategy(seed,m,ramp,s,tau); horizon=[r for r in rows if 401<=r['t']<=800]; during=[r for r in rows if 401<=r['t']<=400+ramp]; after=[r for r in rows if r['t']>=401]; ads=[r['t'] for r in after if r['adapt']]
     summaries.append({'seed':seed,'delta_a':m,'ramp_duration':ramp,'strategy':s,'loss_401_800':sum(r['sq_error'] for r in horizon),'adapt_during_ramp':int(any(r['adapt'] for r in during)),'first_adaptation':ads[0] if ads else '','adaptation_delay':ads[0]-EVENT_T if ads else '','adapt_count_401_800':sum(r['adapt'] for r in horizon),'adapt_count_401_1200':sum(r['adapt'] for r in after)})
     if seed in AUDIT:
      for r in rows: audit.append(dict(r,delta_a=m,ramp_duration=ramp))
 write(RESULTS/'seed_summary.csv',summaries); write(RESULTS/'audit_trace_seeds_3000_3004.csv',audit)
 cells=[]
 for m in MAG:
  for ramp in RAMPS:
   c=[r for r in summaries if r['delta_a']==m and r['ramp_duration']==ramp]; means={s:sum(r['loss_401_800'] for r in c if r['strategy']==s)/200 for s in STRATEGIES}; rates={s:sum(r['adapt_during_ramp'] for r in c if r['strategy']==s)/200 for s in STRATEGIES}; diffs=[]
   for seed in SEEDS:
    g=next(r for r in c if r['seed']==seed and r['strategy']=='persistence'); b=next(r for r in c if r['seed']==seed and r['strategy']=='threshold'); diffs.append(g['loss_401_800']-b['loss_401_800'])
   cells.append({'delta_a':m,'ramp_duration':ramp,'mean_loss':means,'adapt_during_ramp_rate':rates,'persistence_minus_threshold_loss_mean_difference':sum(diffs)/200,'bootstrap_95_ci':list(paired_bootstrap_ci(diffs,seed=2026081803+int(m*100)+ramp))})
 report={'tau':tau,'evaluation_seeds':[3000,3199],'n_seeds_per_cell':200,'cells':cells,'audit_seeds':sorted(AUDIT)}; RESULTS.mkdir(parents=True,exist_ok=True); (RESULTS/'report.json').write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps(report,indent=2))
if __name__=='__main__': main()
