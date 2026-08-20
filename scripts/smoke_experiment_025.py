#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from adaptive_model_gating import N_STEPS,INITIAL_FIT_END
from experiment_025 import CONDITIONAL_CONFIRMATION_STRATEGY,NOISE_TRIGGER,inject_round6,round6_candidate_score,run_experiment_025_strategy
from experiment_024 import MARGIN_STRATEGY
from experiment_023 import NOISE_AWARE_STRATEGY
from experiment_021 import QUALIFICATION_AWARE_STRATEGY
from experiment_022 import TRIAD,generate_stress_stream
from run_experiment_025 import CELLS,STRATEGIES,calibrations

PICKS=('healthy_0.00','g0.500_n1.00_0.50','g0.500_n1.50_0.50','g0.500_n2.00_0.50','g0.425_n1.50_0.50','g0.350_n2.00_0.50')
def main():
 if len(CELLS)!=46 or len(STRATEGIES)!=5:raise AssertionError((len(CELLS),len(STRATEGIES)))
 vals=calibrations();by={c['label']:c for c in CELLS};seed=25999
 saw_low=False;saw_high=False
 for label in PICKS:
  c=by[label]
  for st in STRATEGIES:
   rows=run_experiment_025_strategy(seed,c,st,vals)
   if len(rows)!=(N_STEPS-INITIAL_FIT_END):raise AssertionError((label,st,len(rows)))
   if st==CONDITIONAL_CONFIRMATION_STRATEGY:
    if any(r.get('experiment025_cell')!=label for r in rows):raise AssertionError((label,'annotation'))
    f=float(rows[0].get('diagnostic_noise_factor',1.0))
    saw_low |= f<=NOISE_TRIGGER;saw_high |= f>NOISE_TRIGGER
 if not saw_low or not saw_high:raise AssertionError(('dispatcher coverage',saw_low,saw_high))
 # Mechanical round-6 injection sanity, independent of any acceptance outcome.
 s=generate_stress_stream(seed,by['g0.500_n2.00_0.50']);s6=inject_round6(s,('a','b'))
 if all(s6['probe_obs_a'][t]==s['probe_obs_a'][t] for t in range(276,286)):raise AssertionError('round6 injection missing')
 print('Experiment 025 smoke passed for both dispatch branches, all five comparators, and round-6 injection.')
if __name__=='__main__':main()
