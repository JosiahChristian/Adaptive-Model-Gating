#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from adaptive_model_gating import N_STEPS,INITIAL_FIT_END
from experiment_022 import CELLS,STRATEGIES,generate_stress_stream,run_experiment_022_strategy
from run_experiment_021 import calibrations

PICKS=('healthy_0.00','gain_0.425_0.50','noise_1.50_0.50','timing_m20_0.50','asym_1.00_1.50_0.50','mixed_drift_common_0.50')
EXPECTED_ROWS=N_STEPS-INITIAL_FIT_END

def main():
 if len(CELLS)!=76:raise AssertionError(len(CELLS))
 by={c['label']:c for c in CELLS};vals=calibrations();seed=22999
 for label in PICKS:
  c=by[label];s=generate_stress_stream(seed,c)
  if len(s['y'])!=N_STEPS+1 or len(s['probe_obs_a'])!=N_STEPS+1:raise AssertionError(f'bad stream length {label}')
  if c.get('gain') is not None and abs(float(s['probe_gain'])-float(c['gain']))>1e-12:raise AssertionError(f'gain mismatch {label}')
  for st in STRATEGIES:
   rows=run_experiment_022_strategy(seed,c,st,vals)
   if len(rows)!=EXPECTED_ROWS:raise AssertionError(f'row count {label} {st}: {len(rows)}')
   if any(r.get('experiment022_cell')!=label for r in rows):raise AssertionError(f'cell annotation {label} {st}')
 print('Experiment 022 smoke passed for all six stress classes and four frozen comparators.')
if __name__=='__main__':main()
