#!/usr/bin/env python3
import math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_046 import E_THRESHOLD,split_indices
from experiment_047 import AMP_DENOM,BLOCK_PRECISION,discovery_profile
from experiment_048 import CELLS,STRATEGIES,SIGN_E_STRATEGY,EXACT_ALL_POSITIVE_TAIL,EXACT_GE9_TAIL,sign_factor,generate_experiment_048_stream,infer_exact_sign_eprocess,run_experiment_048_strategy
from run_experiment_021 import calibrations

def main():
 if E_THRESHOLD!=100.0:raise AssertionError(E_THRESHOLD)
 if BLOCK_PRECISION!=((4.0/3.0,-2.0/3.0),(-2.0/3.0,4.0/3.0)):raise AssertionError(BLOCK_PRECISION)
 expected=math.sqrt(sum(a*a for a in (0.025,0.050,0.100,0.200,0.200)))
 if abs(AMP_DENOM-expected)>1e-15:raise AssertionError((AMP_DENOM,expected))
 if EXACT_ALL_POSITIVE_TAIL!=1/1024 or EXACT_GE9_TAIL!=11/1024 or not (EXACT_ALL_POSITIVE_TAIL<.01<EXACT_GE9_TAIL):raise AssertionError((EXACT_ALL_POSITIVE_TAIL,EXACT_GE9_TAIL))
 if [sign_factor(x) for x in (1.0,-1.0,0.0)]!=[2.0,0.0,1.0]:raise AssertionError('sign factors')
 for r in range(1,6):
  target,(bd,bc)=split_indices(r)
  if set(bd)&set(bc) or len(bd)!=2 or len(bc)!=2:raise AssertionError((r,bd,bc))
  for td,tc in target.values():
   if set(td)&set(tc) or len(td)!=2 or len(tc)!=3:raise AssertionError((r,td,tc))
 vals=calibrations();seed=48999
 for idx in (0,4,8,12,15):
  c=CELLS[idx];s=generate_experiment_048_stream(seed,c);groups,accepted,abstain,stop,path,mats,y,scores=infer_exact_sign_eprocess(s);y2,s2,cand2=discovery_profile(mats)
  if tuple(y)!=tuple(y2) or scores!=s2 or path[0]['candidate']!=cand2:raise AssertionError('profile mismatch')
  if len(path)!=5 or stop!=5:raise AssertionError((len(path),stop))
  cand=path[0]['candidate'];prev=1.0;positive=0
  if any(p['candidate']!=cand for p in path):raise AssertionError('candidate reselection')
  for p in path:
   f1,f2=p['factors'];x1,x2=p['responses'];positive+=int(x1>0)+int(x2>0)
   if f1!=sign_factor(x1) or f2!=sign_factor(x2):raise AssertionError('factor mismatch')
   prev*=f1*f2
   if prev!=p['e_value']:raise AssertionError((prev,p['e_value']))
  if positive==10 and prev!=1024.0:raise AssertionError((positive,prev))
  if positive<10 and prev!=0.0:raise AssertionError((positive,prev))
  if accepted!=int(prev>=E_THRESHOLD) or abstain!=1-accepted:raise AssertionError((accepted,abstain,prev))
 c=CELLS[0]
 for st in STRATEGIES:
  rows=run_experiment_048_strategy(seed,c,st,vals)
  if not rows or len(rows)!=900:raise AssertionError((st,len(rows)))
  if st==SIGN_E_STRATEGY:
   r0=rows[0]
   if int(float(r0.get('sign48_discovery_acceptance',1) or 0))!=0 or int(float(r0.get('sign48_candidate_reselected',1) or 0))!=0:raise AssertionError('split integrity')
 print('Experiment 048 smoke OK')
if __name__=='__main__':main()
