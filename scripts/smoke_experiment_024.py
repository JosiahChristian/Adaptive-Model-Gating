#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from adaptive_model_gating import N_STEPS,INITIAL_FIT_END
from experiment_024 import MARGIN_STRATEGY,run_experiment_024_strategy,Z_MARGIN
from run_experiment_024 import CELLS,STRATEGIES,calibrations
PICKS=('healthy_0.00','g0.500_n1.00_0.50','g0.500_n1.50_0.50','g0.500_n2.00_0.50','g0.425_n1.50_0.50','g0.350_n2.00_0.50')
def main():
 if len(CELLS)!=46:raise AssertionError(len(CELLS))
 if Z_MARGIN<=0:raise AssertionError(Z_MARGIN)
 by={c['label']:c for c in CELLS};vals=calibrations();seed=24999
 for label in PICKS:
  c=by[label]
  for st in STRATEGIES:
   rows=run_experiment_024_strategy(seed,c,st,vals)
   if len(rows)!=(N_STEPS-INITIAL_FIT_END):raise AssertionError((label,st,len(rows)))
   if st==MARGIN_STRATEGY and any(r.get('experiment024_cell')!=label for r in rows):raise AssertionError((label,st,'annotation'))
 print('Experiment 024 smoke passed.')
if __name__=='__main__':main()
