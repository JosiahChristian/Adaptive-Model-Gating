#!/usr/bin/env python3
import math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from adaptive_model_gating import INITIAL_FIT_END,N_STEPS
from experiment_035 import CELLS,NOISE_FAMILIES,STRATEGIES,generate_experiment_035_stream,run_experiment_035_strategy,evaluate_experiment_035_posterior
from run_experiment_035 import calibration_values

def main():
 vals=calibration_values();seed=34999
 for nf in NOISE_FAMILIES:
  c=next(x for x in CELLS if x['noise_family']==nf and x['gain']==.50 and x['noise_scale']==1.0);s=generate_experiment_035_stream(seed,c)
  assert s['probe_noise_family']==nf and s['probe_noise_scale']==1.0
  for x in 'abc':
   assert len(s[f'probe_obs_{x}'])==N_STEPS+1
   assert all(math.isfinite(float(v)) for v in s[f'probe_obs_{x}'][1:])
  p=evaluate_experiment_035_posterior(seed,c);assert len(p)==5
  for r in p:
   ps=[r['P_'+h] for h in ('H_ab','H_ac','H_bc','H_null')];assert all(math.isfinite(v) and 0<=v<=1 for v in ps);assert abs(sum(ps)-1)<1e-9
  for st in STRATEGIES:
   rows=run_experiment_035_strategy(seed,c,st,vals);assert len(rows)==N_STEPS-INITIAL_FIT_END
 print('Experiment 035 smoke passed')
if __name__=='__main__':main()
