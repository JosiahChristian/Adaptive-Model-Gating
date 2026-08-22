#!/usr/bin/env python3
import math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_042 import CELLS,STRATEGIES,CLEAN_WEIGHT,GROSS_WEIGHT,VARIANCE_RATIO,MIXTURE_VARIANCE,CLEAN_SCALE,GROSS_SCALE,_log_scaled_gaussian_block,posterior_local_gaussian_gross,run_experiment_042_strategy,evaluate_local_gaussian_gross_posterior
from experiment_028 import covariance_terms
from run_experiment_021 import calibrations

def main():
 if CLEAN_WEIGHT!=.95 or GROSS_WEIGHT!=.05 or VARIANCE_RATIO!=25.0 or abs(MIXTURE_VARIANCE-2.2)>1e-12:raise AssertionError((CLEAN_WEIGHT,GROSS_WEIGHT,VARIANCE_RATIO,MIXTURE_VARIANCE))
 if abs(CLEAN_WEIGHT*CLEAN_SCALE+GROSS_WEIGHT*GROSS_SCALE-1.0)>1e-12:raise AssertionError((CLEAN_SCALE,GROSS_SCALE))
 var,cov=covariance_terms(.05,1);det=var*var-cov*cov
 expected=-math.log(2.0*math.pi)-0.5*math.log(det)-math.log(CLEAN_SCALE)
 got=_log_scaled_gaussian_block(0.0,det,CLEAN_SCALE)
 if abs(got-expected)>1e-12:raise AssertionError((got,expected))
 p=posterior_local_gaussian_gross((0,0,0,0,0,0),var,cov)
 if abs(sum(p.values())-1)>1e-10 or any((not math.isfinite(x) or x<0 or x>1) for x in p.values()):raise AssertionError(p)
 vals=calibrations();seed=42999
 for idx in (0,1,4,8,12,15):
  c=CELLS[idx];pr=evaluate_local_gaussian_gross_posterior(seed,c)
  if len(pr)!=5:raise AssertionError((c['label'],len(pr)))
  for st in STRATEGIES:
   rows=run_experiment_042_strategy(seed,c,st,vals)
   if not rows or len(rows)!=900:raise AssertionError((c['label'],st,len(rows)))
 print('Experiment 042 smoke OK')
if __name__=='__main__':main()
# Trigger prospective Experiment 042 preflight after workflow installation.
