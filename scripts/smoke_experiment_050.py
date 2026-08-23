#!/usr/bin/env python3
import math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_046 import E_THRESHOLD,split_indices
from experiment_047 import AMP_DENOM,BLOCK_PRECISION,discovery_profile
from experiment_050 import CELLS,STRATEGIES,REPLICATED_SIGN_STRATEGY,REPLICATE_SEED_OFFSET,SIGN_COUNT,POSITIVE_CUTOFF,P28_NUMERATOR,P28_DENOMINATOR,P28,P27,ACCEPT_E,PRIMARY_PROBE_ENERGY,TOTAL_PROBE_ENERGY,generate_experiment_050_streams,infer_40sign_replicated_exact_binomial,run_experiment_050_strategy
from run_experiment_021 import calibrations

def main():
 if E_THRESHOLD!=100.0:raise AssertionError(E_THRESHOLD)
 if BLOCK_PRECISION!=((4.0/3.0,-2.0/3.0),(-2.0/3.0,4.0/3.0)):raise AssertionError(BLOCK_PRECISION)
 expected=math.sqrt(sum(a*a for a in (0.025,0.050,0.100,0.200,0.200)))
 if abs(AMP_DENOM-expected)>1e-15:raise AssertionError((AMP_DENOM,expected))
 if REPLICATE_SEED_OFFSET!=5000000 or SIGN_COUNT!=40 or POSITIVE_CUTOFF!=28:raise AssertionError((REPLICATE_SEED_OFFSET,SIGN_COUNT,POSITIVE_CUTOFF))
 if P28_NUMERATOR!=9119901052 or P28_DENOMINATOR!=1099511627776 or abs(P28-0.008294501687487355)>1e-18:raise AssertionError((P28_NUMERATOR,P28_DENOMINATOR,P28))
 if not (P28<=.01<P27) or not (ACCEPT_E>=100):raise AssertionError((P28,P27,ACCEPT_E))
 if abs(TOTAL_PROBE_ENERGY-2.0*PRIMARY_PROBE_ENERGY)>1e-15:raise AssertionError((PRIMARY_PROBE_ENERGY,TOTAL_PROBE_ENERGY))
 for r in range(1,6):
  target,(bd,bc)=split_indices(r)
  if set(bd)&set(bc) or len(bd)!=2 or len(bc)!=2:raise AssertionError((r,bd,bc))
  for td,tc in target.values():
   if set(td)&set(tc) or len(td)!=2 or len(tc)!=3:raise AssertionError((r,td,tc))
 vals=calibrations();seed=50000
 for idx in (0,4,8,12,15):
  c=CELLS[idx];primary,replicate=generate_experiment_050_streams(seed,c)
  if primary is replicate:raise AssertionError('replicate alias')
  groups,accepted,abstain,stop,path,mats,y,scores=infer_40sign_replicated_exact_binomial(primary,replicate);y2,s2,cand2=discovery_profile(mats)
  if tuple(y)!=tuple(y2) or scores!=s2 or path[0]['candidate']!=cand2:raise AssertionError('profile mismatch')
  if len(path)!=5 or stop!=5 or any(p['candidate']!=cand2 for p in path):raise AssertionError('candidate/latency')
  flat=[]
  for p in path:
   if len(p['primary_pairwise_responses'])!=4 or len(p['replicate_pairwise_responses'])!=4:raise AssertionError('eight signs per round')
   flat.extend(p['primary_pairwise_responses']);flat.extend(p['replicate_pairwise_responses'])
  if len(flat)!=40:raise AssertionError(len(flat))
  positive=sum(int(x>0) for x in flat);final=ACCEPT_E if positive>=28 else 0.0
  if abs(path[-1]['e_value']-final)>1e-12:raise AssertionError((positive,path[-1]['e_value'],final))
  if accepted!=int(final>=E_THRESHOLD) or abstain!=1-accepted:raise AssertionError((accepted,abstain,final))
 c=CELLS[0]
 for st in STRATEGIES:
  rows=run_experiment_050_strategy(seed,c,st,vals)
  if not rows or len(rows)!=900:raise AssertionError((st,len(rows)))
  if st==REPLICATED_SIGN_STRATEGY:
   r0=rows[0]
   if int(float(r0.get('sign50_discovery_acceptance',1) or 0))!=0 or int(float(r0.get('sign50_candidate_reselected',1) or 0))!=0:raise AssertionError('split integrity')
   if int(float(r0.get('sign50_sign_count',0) or 0))!=40 or int(float(r0.get('sign50_positive_cutoff',0) or 0))!=28:raise AssertionError('frozen exact rule')
   if int(float(r0.get('sign50_replicate_seed',0) or 0))!=seed+REPLICATE_SEED_OFFSET:raise AssertionError('replicate seed')
   if int(float(r0.get('sign50_equal_budget_comparison',1) or 0))!=0:raise AssertionError('resource accounting')
 print('Experiment 050 smoke OK')
if __name__=='__main__':main()
