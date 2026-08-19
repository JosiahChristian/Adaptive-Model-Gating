#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_014 import run_experiment_014_strategy
from run_experiment_014 import STRATEGIES,calibrations,summary

def main():
 vals=calibrations();seed=1603
 for st in STRATEGIES:
  rows=run_experiment_014_strategy(seed,'healthy',0.0,st,*vals)
  if len(rows)!=900:raise ValueError(f'{st}: expected 900 rows')
  for key in ('latent_input_sq_error','corr_ab','corr_ac','corr_bc','inferred_group_a','inferred_group_b','inferred_group_c','inferred_partition_correct','raw_mismatch_votes','inferred_group_mismatch_votes'):
   if key not in rows[0]:raise KeyError(f'{st}: missing {key}')
  s=summary(rows,'healthy',0.0)
  if s['seed']!=seed or s['strategy']!=st:raise ValueError(f'{st}: summary mismatch')
 # Exercise the branch where oracle and learned group semantics may differ, without using an evaluation seed.
 for st in ('naive_three_anchor_quorum','oracle_provenance_quorum','learned_provenance_quorum'):
  rows=run_experiment_014_strategy(1604,'drift_bc_misleading_signature',.5,st,*vals);summary(rows,'drift_bc_misleading_signature',.5)
 print('Experiment 014 execution smoke passed')
if __name__=='__main__':main()
