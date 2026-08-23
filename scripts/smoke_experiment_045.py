#!/usr/bin/env python3
import math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_045 import CELLS,STRATEGIES,SYMMETRY_E_STRATEGY,E_THRESHOLD,BASELINE_SLICES,SIGMA_PROBE,bet_factor,generate_experiment_045_stream,infer_symmetry_eprocess,run_experiment_045_strategy
from run_experiment_021 import calibrations

def main():
 if E_THRESHOLD!=100.0 or SIGMA_PROBE!=0.05:raise AssertionError((E_THRESHOLD,SIGMA_PROBE))
 if [list(BASELINE_SLICES[r]) for r in range(1,6)]!=[list(range(181,185)),list(range(185,189)),list(range(189,193)),list(range(193,197)),list(range(197,201))]:raise AssertionError(BASELINE_SLICES)
 for x in (-1.0,-0.1,0.0,0.1,1.0):
  m=bet_factor(x)
  if not math.isfinite(m) or m<0 or m>2:raise AssertionError((x,m))
 vals=calibrations();seed=45999
 for idx in (0,4,8,12,15):
  c=CELLS[idx];s=generate_experiment_045_stream(seed,c);groups,accepted,abstain,stop,path,mats,scores=infer_symmetry_eprocess(s)
  if len(scores)!=3 or path[0]['stage']!=1 or path[0]['crossing']!=0:raise AssertionError((c['label'],scores,path[0]))
  cand=path[0]['candidate']
  if any(p['candidate']!=cand for p in path):raise AssertionError((c['label'],'candidate reselection'))
  prev=1.0
  for p in path[1:]:
   f1,f2=p['factors'];calc=prev*f1*f2
   if abs(calc-p['e_value'])>1e-12:raise AssertionError((c['label'],calc,p['e_value']))
   if p['stage']<stop and p['e_value']>=E_THRESHOLD:raise AssertionError((c['label'],'early unrecorded crossing'))
   prev=p['e_value']
  if accepted and (stop<2 or path[-1]['e_value']<E_THRESHOLD):raise AssertionError((c['label'],stop,path[-1]['e_value']))
  if abstain and any(p['e_value']>=E_THRESHOLD for p in path):raise AssertionError((c['label'],'abstain after crossing'))
 # Exercise all dispatch paths on one representative cell.
 c=CELLS[0]
 for st in STRATEGIES:
  rows=run_experiment_045_strategy(seed,c,st,vals)
  if not rows or len(rows)!=900:raise AssertionError((st,len(rows)))
  if st==SYMMETRY_E_STRATEGY:
   r0=rows[0]
   if int(float(r0.get('symmetry_discovery_acceptance',1) or 0))!=0 or int(float(r0.get('symmetry_candidate_reselected',1) or 0))!=0:raise AssertionError('split integrity')
 print('Experiment 045 smoke OK')
if __name__=='__main__':main()
