#!/usr/bin/env python3
import math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_041 import CELLS,STRATEGIES,GAUSSIAN_WEIGHT,CAUCHY_WEIGHT,CAUCHY_DF,_log_cauchy_block,posterior_local_cauchy,run_experiment_041_strategy,evaluate_local_cauchy_posterior
from experiment_028 import covariance_terms
from run_experiment_021 import calibrations

def main():
 if GAUSSIAN_WEIGHT!=.95 or CAUCHY_WEIGHT!=.05 or CAUCHY_DF!=1.0:raise AssertionError((GAUSSIAN_WEIGHT,CAUCHY_WEIGHT,CAUCHY_DF))
 var,cov=covariance_terms(.05,1);det=var*var-cov*cov
 expected=-math.log(2.0*math.pi)-0.5*math.log(det)
 if abs(_log_cauchy_block(0.0,det)-expected)>1e-12:raise AssertionError((_log_cauchy_block(0.0,det),expected))
 p=posterior_local_cauchy((0,0,0,0,0,0),var,cov)
 if abs(sum(p.values())-1)>1e-10 or any((not math.isfinite(x) or x<0 or x>1) for x in p.values()):raise AssertionError(p)
 vals=calibrations();seed=42999
 for idx in (0,1,4,8,12,15):
  c=CELLS[idx];pr=evaluate_local_cauchy_posterior(seed,c)
  if len(pr)!=5:raise AssertionError((c['label'],len(pr)))
  for st in STRATEGIES:
   rows=run_experiment_041_strategy(seed,c,st,vals)
   if not rows or len(rows)!=900:raise AssertionError((c['label'],st,len(rows)))
 print('Experiment 041 smoke OK')
if __name__=='__main__':main()
