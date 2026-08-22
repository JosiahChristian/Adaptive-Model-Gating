#!/usr/bin/env python3
import math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_029 import ACCEPT_THRESHOLD
from experiment_037 import CELLS,STRATEGIES,MODEL_PRIOR,posterior_model_averaged,run_experiment_037_strategy,evaluate_model_averaged_posterior
from experiment_028 import covariance_terms
from run_experiment_021 import calibrations

def main():
 assert MODEL_PRIOR=={'gaussian':0.5,'student_t3':0.5};assert ACCEPT_THRESHOLD==0.99
 var,cov=covariance_terms(.05,3);p,m=posterior_model_averaged((.1,0,.1,0,0,0),var,cov);assert abs(sum(p.values())-1)<1e-10 and abs(sum(m.values())-1)<1e-10
 vals=calibrations();seed=38999
 for nf in ('gaussian','laplace','student_t3','contaminated_gaussian'):
  c=next(x for x in CELLS if x['noise_family']==nf and x['gain']==.50 and x['noise_scale']==1.0)
  pr=evaluate_model_averaged_posterior(seed,c);assert len(pr)==5
  for r in pr:
   ps=[r['P_'+h] for h in ('H_ab','H_ac','H_bc','H_null')];assert all(math.isfinite(x) and 0<=x<=1 for x in ps) and abs(sum(ps)-1)<1e-9
  for st in STRATEGIES:
   rows=run_experiment_037_strategy(seed,c,st,vals);assert rows and len(rows)==900
 print('Experiment 037 smoke PASS')
if __name__=='__main__':main()
