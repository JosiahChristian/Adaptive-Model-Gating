#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from adaptive_model_gating import N_STEPS,INITIAL_FIT_END
from experiment_023 import NOISE_AWARE_STRATEGY,diagnostic_noise_factor,scale_thresholds,run_experiment_023_strategy
from experiment_022 import generate_stress_stream
from run_experiment_023 import CELLS,STRATEGIES,calibrations

def main():
 if len(CELLS)!=46:raise AssertionError(len(CELLS))
 by={c['label']:c for c in CELLS};vals=calibrations();seed=23999
 picks=('g0.500_n1.00_0.50','g0.500_n1.50_0.50','g0.500_n2.00_0.50','g0.425_n1.50_0.50','g0.350_n2.00_0.50','healthy_0.00')
 for label in picks:
  c=by[label];s=generate_stress_stream(seed,c);factor,sd=diagnostic_noise_factor(s)
  if factor<1 or sd<=0:raise AssertionError(f'bad factor {label}: {factor} {sd}')
  sv=scale_thresholds(vals,factor)
  if any(sv[i]<vals[i] for i in (12,13,14,15,16,17)):raise AssertionError(f'threshold deflation {label}')
  for st in STRATEGIES:
   rows=run_experiment_023_strategy(seed,c,st,vals)
   if len(rows)!=N_STEPS-INITIAL_FIT_END:raise AssertionError(f'row count {label} {st}: {len(rows)}')
   if st==NOISE_AWARE_STRATEGY and any(float(r['diagnostic_noise_factor'])!=factor for r in rows):raise AssertionError(f'factor annotation {label}')
 print('Experiment 023 smoke passed: estimator, scaling, shared streams, six representative cells, five strategies.')
if __name__=='__main__':main()
