#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from run_experiment_017 import STRATEGIES,calibrations,summary
from experiment_017_dispatch import run_experiment_017_strategy

def main():
 vals=calibrations();seed=3199
 for family,magnitude in [('drift_ab_fault',.5),('drift_ab_gain0375',.5),('drift_ab_gain0125',.5),('drift_all_aux_fault',.5)]:
  for st in STRATEGIES:
   rows=run_experiment_017_strategy(seed,family,magnitude,st,*vals)
   if len(rows)!=900:raise AssertionError((family,st,len(rows)))
   s=summary(rows,family,magnitude)
   if s['strategy']!=st:raise AssertionError((family,st,s['strategy']))
 print('Experiment 017 all-strategy smoke passed')
if __name__=='__main__':main()
