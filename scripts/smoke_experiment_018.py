#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_018 import run_experiment_018_strategy
from run_experiment_018 import STRATEGIES,calibrations,summary

def main():
 vals=calibrations();seed=4004;f='drift_ab_gain050';m=0.5
 for st in STRATEGIES:
  rows=run_experiment_018_strategy(seed,f,m,st,*vals)
  if len(rows)!=900:raise RuntimeError((st,len(rows)))
  s=summary(rows,f,m)
  for k in ('operational_loss_401_600','latent_input_loss_401_600','final_slope_error_abs','probe_energy'):
   if k not in s:raise RuntimeError((st,k))
 print('Experiment 018 all-strategy smoke passed')
if __name__=='__main__':main()
