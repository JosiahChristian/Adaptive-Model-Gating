#!/usr/bin/env python3
import math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_027 import inject_symmetric_round5
from experiment_029 import ACCEPT_THRESHOLD,infer_posterior_risk
from experiment_043 import CELLS,STRATEGIES,CONFIRMATIONS_REQUIRED,generate_experiment_043_stream,infer_replicated_gaussian,run_experiment_043_strategy,evaluate_gaussian_posterior
from run_experiment_021 import calibrations

def main():
 if CONFIRMATIONS_REQUIRED!=2 or ACCEPT_THRESHOLD!=.99:raise AssertionError((CONFIRMATIONS_REQUIRED,ACCEPT_THRESHOLD))
 vals=calibrations();seed=43999
 for idx in (0,1,4,8,12,15):
  c=CELLS[idx];s=inject_symmetric_round5(generate_experiment_043_stream(seed,c));_,_,_,_,rp=infer_replicated_gaussian(s);_,_,_,_,gp=infer_posterior_risk(s)
  for a,b in zip(rp,gp):
   if a['candidate']!=b['candidate'] or abs(a['candidate_posterior']-b['candidate_posterior'])>1e-12:raise AssertionError((c['label'],a,b))
   for h in a['posterior']:
    if abs(a['posterior'][h]-b['posterior'][h])>1e-12:raise AssertionError((c['label'],h,a['posterior'][h],b['posterior'][h]))
  pr=evaluate_gaussian_posterior(seed,c)
  if len(pr)!=5:raise AssertionError((c['label'],len(pr)))
  for row in pr:
   ps=[row[k] for k in ('P_H_ab','P_H_ac','P_H_bc','P_H_null')]
   if abs(sum(ps)-1)>1e-10 or any((not math.isfinite(x) or x<0 or x>1) for x in ps):raise AssertionError(row)
  for st in STRATEGIES:
   rows=run_experiment_043_strategy(seed,c,st,vals)
   if not rows or len(rows)!=900:raise AssertionError((c['label'],st,len(rows)))
   if st==STRATEGIES[0]:
    r0=rows[0];accepted=int(float(r0.get('provenance_accepted',0) or 0));stop=int(float(r0.get('probe_stop_round',0) or 0))
    if accepted:
     if stop<2 or int(float(r0.get('replication_confirmations_required',0) or 0))!=2 or int(float(r0.get('replication_confirmed',0) or 0))!=1:raise AssertionError((c['label'],stop,r0.get('replication_confirmed')))
     if r0.get('replication_previous_candidate')!=r0.get('replication_accept_candidate') or float(r0.get('replication_previous_posterior',0))<.99 or float(r0.get('replication_accept_posterior',0))<.99:raise AssertionError((c['label'],'confirmation integrity'))
 print('Experiment 043 smoke OK')
if __name__=='__main__':main()
