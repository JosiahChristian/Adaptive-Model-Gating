#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_021 import QUALIFICATION_AWARE_STRATEGY,run_experiment_021_strategy
from run_experiment_021 import calibrations

def main():
 vals=calibrations();seen_pre=False;seen_dispatch=False
 cases=[('drift_ab_fault',0.5),('drift_ab_gain050',0.5),('drift_ab_gain0125',0.5),('healthy',0.0)]
 for seed in range(21980,22000):
  for f,m in cases:
   rows=run_experiment_021_strategy(seed,f,m,QUALIFICATION_AWARE_STRATEGY,*vals)
   if len(rows)!=900:raise RuntimeError(f'{seed} {f}: expected 900 rows, got {len(rows)}')
   r0=rows[0];pre=int(r0['inherited_prequalified']);entry=int(r0['experiment020_dispatch_entry'])
   if pre and entry:raise RuntimeError('prequalified seed entered Experiment 020')
   if (not pre) and (not entry):raise RuntimeError('unresolved seed did not enter Experiment 020')
   seen_pre|=bool(pre);seen_dispatch|=bool(entry)
  if seen_pre and seen_dispatch:break
 if not seen_pre:raise RuntimeError('smoke did not exercise inherited prequalification branch')
 if not seen_dispatch:raise RuntimeError('smoke did not exercise Experiment 020 dispatch branch')
 print('Experiment 021 dispatcher smoke passed')
if __name__=='__main__':main()
