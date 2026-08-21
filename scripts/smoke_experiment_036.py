#!/usr/bin/env python3
import math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_029 import ACCEPT_THRESHOLD,WRONG_COST,FALLBACK_COST,TRIAD
from experiment_032 import COMPOSED_STRATEGY
from experiment_036 import CELLS,ROBUST_STRATEGY,STRATEGIES,NU,BETA_STEP,BETA_MAX,generate_experiment_036_stream,evaluate_robust_posterior,run_experiment_036_strategy
from run_experiment_021 import calibrations

def main():
 assert len(CELLS)==16 and STRATEGIES==(ROBUST_STRATEGY,COMPOSED_STRATEGY,TRIAD)
 assert NU==3.0 and BETA_STEP==0.01 and BETA_MAX==1.20 and ACCEPT_THRESHOLD==0.99 and WRONG_COST==100.0 and FALLBACK_COST==1.0
 labels={c['label'] for c in CELLS};assert len(labels)==16
 seed=35999
 for nf in ('gaussian','laplace','student_t3','contaminated_gaussian'):
  c=next(x for x in CELLS if x['noise_family']==nf and x['gain']==.50 and x['noise_scale']==1.5)
  s=generate_experiment_036_stream(seed,c);assert s['probe_noise_family']==nf and abs(float(s['probe_noise_scale'])-1.5)<1e-12
  pr=evaluate_robust_posterior(seed,c);assert len(pr)==5
  for r in pr:
   ps=[r['P_'+h] for h in ('H_ab','H_ac','H_bc','H_null')];assert all(math.isfinite(p) and 0<=p<=1 for p in ps);assert abs(sum(ps)-1)<1e-9
 vals=calibrations()
 for label in ('gaussian_g0.500_n1.00','student_t3_g0.425_n1.50'):
  c=next(x for x in CELLS if x['label']==label)
  for st in STRATEGIES:
   rows=run_experiment_036_strategy(seed,c,st,vals);assert len(rows)==900;assert all('adapt' in r and 'sq_error' in r for r in rows)
 print('Experiment 036 smoke validation passed')
if __name__=='__main__':main()
