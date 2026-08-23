#!/usr/bin/env python3
import math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_028 import VECTOR,TOPOLOGY_DIRECTIONS
from experiment_046 import E_THRESHOLD,SIGMA_PROBE,split_indices,bet_factor
from experiment_047 import CELLS,STRATEGIES,COV_MATCHED_E_STRATEGY,AMP_DENOM,BLOCK_PRECISION,discovery_profile,generate_experiment_047_stream,infer_cov_matched_eprocess,run_experiment_047_strategy
from run_experiment_021 import calibrations

def main():
 if E_THRESHOLD!=100.0 or SIGMA_PROBE!=0.05:raise AssertionError((E_THRESHOLD,SIGMA_PROBE))
 if BLOCK_PRECISION!=((4.0/3.0,-2.0/3.0),(-2.0/3.0,4.0/3.0)):raise AssertionError(BLOCK_PRECISION)
 expected=math.sqrt(sum(a*a for a in (0.025,0.050,0.100,0.200,0.200)))
 if abs(AMP_DENOM-expected)>1e-15:raise AssertionError((AMP_DENOM,expected))
 for r in range(1,6):
  target,(bd,bc)=split_indices(r)
  if set(bd)&set(bc) or len(bd)!=2 or len(bc)!=2:raise AssertionError((r,bd,bc))
  for td,tc in target.values():
   if set(td)&set(tc) or len(td)!=2 or len(tc)!=3:raise AssertionError((r,td,tc))
 vals=calibrations();seed=47999
 for idx in (0,4,8,12,15):
  c=CELLS[idx];s=generate_experiment_047_stream(seed,c);groups,accepted,abstain,stop,path,mats,y,scores=infer_cov_matched_eprocess(s)
  y2,s2,cand2=discovery_profile(mats)
  if tuple(y)!=tuple(y2) or scores!=s2 or path[0]['candidate']!=cand2:raise AssertionError('profile mismatch')
  if len(y)!=len(VECTOR) or len(scores)!=3 or set(scores)!=set(TOPOLOGY_DIRECTIONS):raise AssertionError((len(y),scores))
  if any((not math.isfinite(v) or v<0) for v in scores.values()):raise AssertionError(scores)
  if len(path)!=5 or stop!=5:raise AssertionError((len(path),stop))
  cand=path[0]['candidate']
  if any(p['candidate']!=cand for p in path):raise AssertionError('candidate reselection')
  prev=1.0
  for p in path:
   f1,f2=p['factors']
   if abs(f1-bet_factor(p['responses'][0]))>1e-12 or abs(f2-bet_factor(p['responses'][1]))>1e-12:raise AssertionError('factor mismatch')
   calc=prev*f1*f2
   if abs(calc-p['e_value'])>1e-12:raise AssertionError((calc,p['e_value']))
   prev=p['e_value']
  if accepted!=int(path[-1]['e_value']>=E_THRESHOLD) or abstain!=1-accepted:raise AssertionError((accepted,abstain,path[-1]['e_value']))
 c=CELLS[0]
 for st in STRATEGIES:
  rows=run_experiment_047_strategy(seed,c,st,vals)
  if not rows or len(rows)!=900:raise AssertionError((st,len(rows)))
  if st==COV_MATCHED_E_STRATEGY:
   r0=rows[0]
   if int(float(r0.get('cov47_discovery_acceptance',1) or 0))!=0 or int(float(r0.get('cov47_candidate_reselected',1) or 0))!=0:raise AssertionError('split integrity')
 print('Experiment 047 smoke OK')
if __name__=='__main__':main()
