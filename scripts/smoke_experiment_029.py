#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from adaptive_model_gating import N_STEPS,INITIAL_FIT_END
from experiment_029 import POSTERIOR_RISK_STRATEGY,ACCEPT_THRESHOLD,WRONG_COST,FALLBACK_COST,run_experiment_029_strategy
from run_experiment_029 import CELLS,STRATEGIES,calibrations
PICKS=('healthy','g0.500_n1.00','g0.500_n1.50','g0.425_n1.50','g0.350_n2.00','drift_all_aux_fault_0.50')
def main():
 if len(CELLS)!=15 or len(STRATEGIES)!=3:raise AssertionError((len(CELLS),len(STRATEGIES)))
 if abs(ACCEPT_THRESHOLD-.99)>1e-12 or WRONG_COST!=100.0 or FALLBACK_COST!=1.0:raise AssertionError((ACCEPT_THRESHOLD,WRONG_COST,FALLBACK_COST))
 vals=calibrations();by={c['label']:c for c in CELLS};seed=30999
 for label in PICKS:
  c=by[label]
  for st in STRATEGIES:
   rows=run_experiment_029_strategy(seed,c,st,vals)
   if len(rows)!=(N_STEPS-INITIAL_FIT_END):raise AssertionError((label,st,len(rows)))
   if st==POSTERIOR_RISK_STRATEGY:
    r=rows[0];accepted=int(r.get('provenance_accepted',0));stop=int(r.get('probe_stop_round',0) or 0);ps=[float(r.get(f'posterior_r{i}_candidate_p',0)) for i in range(1,6)];quals=[i+1 for i,p in enumerate(ps) if p>=ACCEPT_THRESHOLD];expected=quals[0] if quals else 0
    if accepted and stop!=expected:raise AssertionError((label,'earliest',stop,expected))
    if not accepted and expected!=0:raise AssertionError((label,'missed qualifying stage',expected))
 print('Experiment 029 smoke passed: frozen loss threshold, representative execution, and earliest-stage decision integrity.')
if __name__=='__main__':main()
