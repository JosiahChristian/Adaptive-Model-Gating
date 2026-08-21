#!/usr/bin/env python3
import math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_027 import HYPOTHESES
from experiment_028 import covariance_terms,evaluate_both_paths,posterior_from_directed
from run_experiment_028 import CELLS,MODELS

PICKS=('healthy','g0.500_n1.00','g0.500_n1.50','g0.350_n2.00','drift_all_aux_fault_0.50')
def main():
 if len(CELLS)!=15 or len(MODELS)!=2:raise AssertionError((len(CELLS),len(MODELS)))
 # Pure algebra checks, independent of evaluation outcomes.
 for stage in range(1,6):
  v,c=covariance_terms(.05,stage)
  if not (v>c>=0):raise AssertionError((stage,v,c))
  p,_,_=posterior_from_directed((0,0,0,0,0,0),v,c)
  if abs(sum(p.values())-1)>1e-10 or any((not math.isfinite(x) or x<0) for x in p.values()):raise AssertionError((stage,p))
 by={c['label']:c for c in CELLS};seed=29999
 for label in PICKS:
  rows=evaluate_both_paths(seed,by[label])
  if len(rows)!=10:raise AssertionError((label,len(rows)))
  if {r['model'] for r in rows}!=set(MODELS):raise AssertionError((label,'models'))
  for r in rows:
   ps=[float(r['P_'+h]) for h in HYPOTHESES]
   if abs(sum(ps)-1)>1e-10:raise AssertionError((label,r['model'],r['stage'],sum(ps)))
 print('Experiment 028 smoke passed: covariance algebra, both frozen models, five stages, and boundary cells.')
if __name__=='__main__':main()
