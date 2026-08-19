#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_016 import run_experiment_016_strategy
from run_experiment_016 import STRATEGIES,calibrations,summary

def main():
 vals=calibrations();tau,k,k3,la,lb,lc,lab,lac,lbc,thresholds=vals
 assert len(thresholds)==4 and all(x>0 for x in thresholds)
 for seed,f,m in ((2100,'drift_ab_fault',0.5),(2101,'drift_ab_gain050',0.5)):
  for st in STRATEGIES:
   rows=run_experiment_016_strategy(seed,f,m,st,*vals)
   assert len(rows)==900
   s=summary(rows,f,m)
   for key in ('operational_loss_401_600','latent_input_loss_401_600','probe_energy','probe_stop_round','inferred_partition_correct','final_slope_error_abs'):
    assert key in s
   r=rows[-1]
   assert r['lambda_probe_1']==thresholds[0] and r['lambda_probe_4']==thresholds[3]
   assert 'latent_input_sq_error' in r and 'x_true' in r and 'x_primary' in r
   if st=='max_probe_provenance_quorum':
    assert abs(s['probe_energy']-15*0.2**2)<1e-12 and int(s['probe_stop_round'])==4
   elif st=='sequential_provenance_quorum':
    assert s['probe_energy']>0 and 1<=int(s['probe_stop_round'])<=4
   else:
    assert s['probe_energy']==0
 print('Experiment 016 pre-shard smoke passed for all strategies.')
if __name__=='__main__':main()
