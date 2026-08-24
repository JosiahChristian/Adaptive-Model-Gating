#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
import experiment_051 as exp51
from experiment_046 import E_THRESHOLD
from run_experiment_052 import SEEDS,AUDIT,OPERATIVE_SPEC_ISSUE,CELLS,STRATEGIES,SIGNED_RANK_STRATEGY,calibration_values,run_experiment_052_strategy,configure

def main():
 configure()
 if list(SEEDS)[:1]!=[52000] or list(SEEDS)[-1:]!=[52999] or AUDIT!=set(range(52000,52005)):raise AssertionError('seed freeze')
 if OPERATIVE_SPEC_ISSUE!=162 or exp51.OPERATIVE_SPEC_ISSUE!=162:raise AssertionError('spec issue')
 if E_THRESHOLD!=100.0 or exp51.W_CUTOFF!=167 or exp51.CONTRAST_COUNT!=20:raise AssertionError('frozen rule')
 if exp51.P167_NUMERATOR!=10084 or exp51.P167_DENOMINATOR!=1048576 or not (exp51.P167<=.01<exp51.P166):raise AssertionError('exact tails')
 vals=calibration_values();c=CELLS[0]
 for st in STRATEGIES:
  rows=run_experiment_052_strategy(52000,c,st,vals)
  if not rows or len(rows)!=900:raise AssertionError((st,len(rows)))
  if st==SIGNED_RANK_STRATEGY:
   r0=rows[0]
   if int(float(r0.get('rank51_spec_issue',0)))!=162:raise AssertionError('prospective spec provenance')
   if int(float(r0.get('rank51_w_cutoff',0)))!=167 or int(float(r0.get('rank51_contrast_count',0)))!=20:raise AssertionError('confirmation freeze')
   if int(float(r0.get('rank51_uses_experiment050_replicate',1)))!=0:raise AssertionError('resource freeze')
 print('Experiment 052 smoke OK')
if __name__=='__main__':main()
