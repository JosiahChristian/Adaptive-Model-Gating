#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from adaptive_model_gating import N_STEPS,INITIAL_FIT_END
from experiment_029 import POSTERIOR_RISK_STRATEGY,TRIAD,ACCEPT_THRESHOLD,run_experiment_029_strategy
from run_experiment_030 import CELLS,calibrations
PICKS=('healthy','common_mode_0.50','g0.500_n1.00','g0.500_n1.50')
def main():
 if len(CELLS)!=7:raise AssertionError(len(CELLS))
 if abs(ACCEPT_THRESHOLD-.99)>1e-12:raise AssertionError(ACCEPT_THRESHOLD)
 vals=calibrations();by={c['label']:c for c in CELLS};seed=31999
 for label in PICKS:
  for st in (POSTERIOR_RISK_STRATEGY,TRIAD):
   rows=run_experiment_029_strategy(seed,by[label],st,vals)
   if len(rows)!=(N_STEPS-INITIAL_FIT_END):raise AssertionError((label,st,len(rows)))
   if st==POSTERIOR_RISK_STRATEGY and any(r.get('posterior_risk_accept_threshold')!=.99 for r in rows):raise AssertionError((label,'threshold'))
 print('Experiment 030 smoke passed for frozen policies and representative contexts.')
if __name__=='__main__':main()
