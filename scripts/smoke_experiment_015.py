#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_015 import run_experiment_015_strategy
from run_experiment_015 import STRATEGIES,summary,calibrations

def main():
 vals=calibrations()
 for family,magnitude,seed in [('healthy',0.0,1808),('drift_ab_fault',0.5,1809),('drift_ab_cross_coupled_probe',0.5,1810)]:
  for st in STRATEGIES:
   rows=run_experiment_015_strategy(seed,family,magnitude,st,*vals)
   if len(rows)!=900:raise ValueError(f'{family} {st}: {len(rows)} rows')
   s=summary(rows,family,magnitude)
   required=('operational_loss_401_600','latent_input_loss_401_600','final_slope_error_abs','inferred_partition_correct','probe_R_ab','probe_R_ba')
   missing=[k for k in required if k not in s]
   if missing:raise ValueError(f'{family} {st}: missing {missing}')
 print('Experiment 015 smoke passed for all strategies through real summary path.')
if __name__=='__main__':main()
