#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from adaptive_model_gating import N_STEPS,INITIAL_FIT_END
from experiment_025 import run_experiment_025_strategy
from run_experiment_026 import CELLS,STRATEGIES,calibrations,wilson_upper,wilson_two_sided
PICKS=('healthy_0.00','g0.500_n1.00_0.50','g0.500_n1.50_0.50','g0.425_n1.50_0.50','g0.350_n2.00_0.50')
def main():
 if len(CELLS)!=10 or len(STRATEGIES)!=5:raise AssertionError((len(CELLS),len(STRATEGIES)))
 if not (0 < wilson_upper(0,1000) < .01):raise AssertionError(wilson_upper(0,1000))
 lo,hi=wilson_two_sided(500,1000)
 if not (lo<.5<hi):raise AssertionError((lo,hi))
 vals=calibrations();by={c['label']:c for c in CELLS};seed=26999
 for label in PICKS:
  c=by[label]
  for st in STRATEGIES:
   rows=run_experiment_025_strategy(seed,c,st,vals)
   if len(rows)!=(N_STEPS-INITIAL_FIT_END):raise AssertionError((label,st,len(rows)))
 print('Experiment 026 smoke passed for all frozen comparators and Wilson reporting.')
if __name__=='__main__':main()
