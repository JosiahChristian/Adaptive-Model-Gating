#!/usr/bin/env python3
import math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_046 import CELLS,STRATEGIES,WITHIN_SPLIT_E_STRATEGY,E_THRESHOLD,BASELINE_SLICES,SIGMA_PROBE,bet_factor,generate_experiment_046_stream,infer_within_split_eprocess,run_experiment_046_strategy,split_indices
from run_experiment_021 import calibrations

def main():
 if E_THRESHOLD!=100.0 or SIGMA_PROBE!=0.05:raise AssertionError((E_THRESHOLD,SIGMA_PROBE))
 expected=[list(range(181,185)),list(range(185,189)),list(range(189,193)),list(range(193,197)),list(range(197,201))]
 if [list(BASELINE_SLICES[r]) for r in range(1,6)]!=expected:raise AssertionError(BASELINE_SLICES)
 for r in range(1,6):
  target,(bd,bc)=split_indices(r)
  if set(bd)&set(bc) or len(bd)!=2 or len(bc)!=2:raise AssertionError((r,bd,bc))
  for td,tc in target.values():
   if set(td)&set(tc) or len(td)!=2 or len(tc)!=3:raise AssertionError((r,td,tc))
 for x in (-1.0,-0.1,0.0,0.1,1.0):
  m=bet_factor(x)
  if not math.isfinite(m) or m<0 or m>2:raise AssertionError((x,m))
 vals=calibrations();seed=46999
 for idx in (0,4,8,12,15):
  c=CELLS[idx];s=generate_experiment_046_stream(seed,c);groups,accepted,abstain,stop,path,mats,scores=infer_within_split_eprocess(s)
  if len(scores)!=3 or len(path)!=5 or stop!=5:raise AssertionError((c['label'],len(path),stop))
  cand=path[0]['candidate']
  if any(p['candidate']!=cand for p in path):raise AssertionError((c['label'],'candidate reselection'))
  prev=1.0
  for p in path:
   f1,f2=p['factors'];calc=prev*f1*f2
   if abs(calc-p['e_value'])>1e-12:raise AssertionError((c['label'],calc,p['e_value']))
   prev=p['e_value']
  if accepted != int(path[-1]['e_value']>=E_THRESHOLD) or abstain!=1-accepted:raise AssertionError((c['label'],accepted,abstain,path[-1]['e_value']))
 c=CELLS[0]
 for st in STRATEGIES:
  rows=run_experiment_046_strategy(seed,c,st,vals)
  if not rows or len(rows)!=900:raise AssertionError((st,len(rows)))
  if st==WITHIN_SPLIT_E_STRATEGY:
   r0=rows[0]
   if int(float(r0.get('within_discovery_acceptance',1) or 0))!=0 or int(float(r0.get('within_candidate_reselected',1) or 0))!=0:raise AssertionError('split integrity')
 print('Experiment 046 smoke OK')
if __name__=='__main__':main()
