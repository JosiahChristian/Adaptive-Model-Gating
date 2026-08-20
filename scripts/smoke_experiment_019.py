#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_019 import run_experiment_019_strategy
from run_experiment_019 import STRATEGIES,calibrations

def main():
 vals=calibrations()
 cells=[('healthy',0.0),('drift_ab_fault',0.5),('drift_ab_gain050',0.5),('drift_ab_gain0375',0.5),('drift_ab_gain025',0.5),('drift_ab_gain0125',0.5),('drift_all_aux_fault',0.5)]
 for f,m in cells:
  for st in STRATEGIES:
   rows=run_experiment_019_strategy(19000,f,m,st,*vals)
   if len(rows)!=900:raise RuntimeError(f'{f} {m} {st}: expected 900 rows, got {len(rows)}')
 print('Experiment 019 smoke passed')
if __name__=='__main__':main()
