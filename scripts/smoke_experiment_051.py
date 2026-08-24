#!/usr/bin/env python3
import math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_046 import E_THRESHOLD,split_indices
from experiment_047 import AMP_DENOM,BLOCK_PRECISION,discovery_profile
from experiment_051 import CELLS,STRATEGIES,SIGNED_RANK_STRATEGY,CONTRAST_COUNT,W_CUTOFF,P167_NUMERATOR,P167_DENOMINATOR,P167,P166,ACCEPT_E,generate_experiment_051_stream,infer_20contrast_exact_signed_rank,run_experiment_051_strategy,signed_rank_statistic
from run_experiment_021 import calibrations


def main():
 if E_THRESHOLD!=100.0:raise AssertionError(E_THRESHOLD)
 if BLOCK_PRECISION!=((4.0/3.0,-2.0/3.0),(-2.0/3.0,4.0/3.0)):raise AssertionError(BLOCK_PRECISION)
 expected=math.sqrt(sum(a*a for a in (0.025,0.050,0.100,0.200,0.200)))
 if abs(AMP_DENOM-expected)>1e-15:raise AssertionError((AMP_DENOM,expected))
 if CONTRAST_COUNT!=20 or W_CUTOFF!=167:raise AssertionError((CONTRAST_COUNT,W_CUTOFF))
 if P167_NUMERATOR!=10084 or P167_DENOMINATOR!=1048576:raise AssertionError((P167_NUMERATOR,P167_DENOMINATOR))
 if abs(P167-0.009616851806640625)>1e-18 or abs(P166-0.0107421875)>1e-18:raise AssertionError((P167,P166))
 if not (P167<=.01<P166) or not (ACCEPT_E>=100):raise AssertionError((P167,P166,ACCEPT_E))
 # Exact subset-sum boundary sanity checks.
 if signed_rank_statistic(tuple(range(1,21)))[0]!=210:raise AssertionError('all-positive W+')
 vals=tuple((-1.0 if i<10 else 1.0)*(i+1) for i in range(20))
 w,r=signed_rank_statistic(vals)
 if sorted(r)!=list(range(1,21)) or not (0<=w<=210):raise AssertionError((w,r))
 for rnum in range(1,6):
  target,(bd,bc)=split_indices(rnum)
  if set(bd)&set(bc) or len(bd)!=2 or len(bc)!=2:raise AssertionError((rnum,bd,bc))
  for td,tc in target.values():
   if set(td)&set(tc) or len(td)!=2 or len(tc)!=3:raise AssertionError((rnum,td,tc))
 vals_cal=calibrations();seed=51000
 for idx in (0,4,8,12,15):
  c=CELLS[idx];stream=generate_experiment_051_stream(seed,c)
  groups,accepted,abstain,stop,path,mats,y,scores=infer_20contrast_exact_signed_rank(stream);y2,s2,cand2=discovery_profile(mats)
  if tuple(y)!=tuple(y2) or scores!=s2 or path[0]['candidate']!=cand2:raise AssertionError('profile mismatch')
  if len(path)!=5 or stop!=5 or any(p['candidate']!=cand2 for p in path):raise AssertionError('candidate/latency')
  flat=[]
  for p in path:
   if len(p['pairwise_responses'])!=4:raise AssertionError('four contrasts per round')
   flat.extend(p['pairwise_responses'])
  if len(flat)!=20:raise AssertionError(len(flat))
  wplus,ranks=signed_rank_statistic(flat);final=ACCEPT_E if wplus>=W_CUTOFF else 0.0
  if path[-1]['wplus']!=wplus or tuple(path[-1]['ranks'])!=tuple(ranks):raise AssertionError('rank mismatch')
  if abs(path[-1]['e_value']-final)>1e-12:raise AssertionError((wplus,path[-1]['e_value'],final))
  if accepted!=int(final>=E_THRESHOLD) or abstain!=1-accepted:raise AssertionError((accepted,abstain,final))
 c=CELLS[0]
 for st in STRATEGIES:
  rows=run_experiment_051_strategy(seed,c,st,vals_cal)
  if not rows or len(rows)!=900:raise AssertionError((st,len(rows)))
  if st==SIGNED_RANK_STRATEGY:
   r0=rows[0]
   if int(float(r0.get('rank51_discovery_acceptance',1) or 0))!=0 or int(float(r0.get('rank51_candidate_reselected',1) or 0))!=0:raise AssertionError('split integrity')
   if int(float(r0.get('rank51_contrast_count',0) or 0))!=20 or int(float(r0.get('rank51_w_cutoff',0) or 0))!=167:raise AssertionError('frozen exact rule')
   if int(float(r0.get('rank51_uses_experiment050_replicate',1) or 0))!=0:raise AssertionError('resource accounting')
 print('Experiment 051 smoke OK')
if __name__=='__main__':main()
