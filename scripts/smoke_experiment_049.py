#!/usr/bin/env python3
import math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_046 import E_THRESHOLD,split_indices
from experiment_047 import AMP_DENOM,BLOCK_PRECISION,discovery_profile
from experiment_049 import CELLS,STRATEGIES,PAIR_SIGN_STRATEGY,SIGN_COUNT,POSITIVE_CUTOFF,P16_NUMERATOR,P16_DENOMINATOR,P16,ACCEPT_E,generate_experiment_049_stream,infer_20sign_exact_binomial,run_experiment_049_strategy
from run_experiment_021 import calibrations

def main():
 if E_THRESHOLD!=100.0:raise AssertionError(E_THRESHOLD)
 if BLOCK_PRECISION!=((4.0/3.0,-2.0/3.0),(-2.0/3.0,4.0/3.0)):raise AssertionError(BLOCK_PRECISION)
 expected=math.sqrt(sum(a*a for a in (0.025,0.050,0.100,0.200,0.200)))
 if abs(AMP_DENOM-expected)>1e-15:raise AssertionError((AMP_DENOM,expected))
 if SIGN_COUNT!=20 or POSITIVE_CUTOFF!=16:raise AssertionError((SIGN_COUNT,POSITIVE_CUTOFF))
 if P16_NUMERATOR!=6196 or P16_DENOMINATOR!=1048576 or abs(P16-0.005908966064453125)>1e-18:raise AssertionError((P16_NUMERATOR,P16_DENOMINATOR,P16))
 if not (P16<=.01) or not (ACCEPT_E>=100):raise AssertionError((P16,ACCEPT_E))
 p15=sum(math.comb(20,j) for j in range(15,21))/(2**20)
 if not p15>.01:raise AssertionError(p15)
 for r in range(1,6):
  target,(bd,bc)=split_indices(r)
  if set(bd)&set(bc) or len(bd)!=2 or len(bc)!=2:raise AssertionError((r,bd,bc))
  for td,tc in target.values():
   if set(td)&set(tc) or len(td)!=2 or len(tc)!=3:raise AssertionError((r,td,tc))
 vals=calibrations();seed=49999
 for idx in (0,4,8,12,15):
  c=CELLS[idx];s=generate_experiment_049_stream(seed,c);groups,accepted,abstain,stop,path,mats,y,scores=infer_20sign_exact_binomial(s);y2,s2,cand2=discovery_profile(mats)
  if tuple(y)!=tuple(y2) or scores!=s2 or path[0]['candidate']!=cand2:raise AssertionError('profile mismatch')
  if len(path)!=5 or stop!=5 or any(p['candidate']!=cand2 for p in path):raise AssertionError('candidate/latency')
  flat=[]
  for p in path:
   if len(p['pairwise_responses'])!=4:raise AssertionError('four signs per round')
   flat.extend(p['pairwise_responses'])
  if len(flat)!=20:raise AssertionError(len(flat))
  positive=sum(int(x>0) for x in flat)
  final=ACCEPT_E if positive>=16 else 0.0
  if abs(path[-1]['e_value']-final)>1e-12:raise AssertionError((positive,path[-1]['e_value'],final))
  if accepted!=int(final>=E_THRESHOLD) or abstain!=1-accepted:raise AssertionError((accepted,abstain,final))
 c=CELLS[0]
 for st in STRATEGIES:
  rows=run_experiment_049_strategy(seed,c,st,vals)
  if not rows or len(rows)!=900:raise AssertionError((st,len(rows)))
  if st==PAIR_SIGN_STRATEGY:
   r0=rows[0]
   if int(float(r0.get('sign49_discovery_acceptance',1) or 0))!=0 or int(float(r0.get('sign49_candidate_reselected',1) or 0))!=0:raise AssertionError('split integrity')
   if int(float(r0.get('sign49_sign_count',0) or 0))!=20 or int(float(r0.get('sign49_positive_cutoff',0) or 0))!=16:raise AssertionError('frozen exact rule')
 print('Experiment 049 smoke OK')
if __name__=='__main__':main()
