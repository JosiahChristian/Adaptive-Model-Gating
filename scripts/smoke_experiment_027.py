#!/usr/bin/env python3
import math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_027 import BETA_SCALE,HYPOTHESES,evaluate_posterior_path
from run_experiment_027 import CELLS
PICKS=('healthy','g0.500_n1.50','g0.350_n2.00','drift_all_aux_fault_0.50')
def main():
 if len(CELLS)!=15 or BETA_SCALE!=.20:raise AssertionError((len(CELLS),BETA_SCALE))
 by={c['label']:c for c in CELLS};seed=28999
 for label in PICKS:
  rows=evaluate_posterior_path(seed,by[label])
  if len(rows)!=5 or {int(r['stage']) for r in rows}!={1,2,3,4,5}:raise AssertionError((label,len(rows)))
  for r in rows:
   ps=[float(r['P_'+h]) for h in HYPOTHESES]
   if any((not math.isfinite(p) or p<0 or p>1) for p in ps):raise AssertionError((label,r['stage'],ps))
   if abs(sum(ps)-1)>1e-10:raise AssertionError((label,r['stage'],sum(ps)))
   if not (float(r['sigma_hat'])>0 and float(r['sigma_c'])>0):raise AssertionError((label,r['stage'],'sigma'))
 print('Experiment 027 smoke passed: four representative cells, five stages, proper posteriors.')
if __name__=='__main__':main()
