from __future__ import annotations
from contextlib import contextmanager
from copy import deepcopy
import importlib
from experiment_010 import run_triad_persistence_on_stream
from experiment_016 import groups_from_edges
from experiment_018 import ALL_AMPLITUDES
from experiment_028 import VECTOR
from experiment_046 import E_THRESHOLD,split_indices,response_matrices
from experiment_047 import AMP_DENOM,HYP_EDGE,discovery_profile
from experiment_048 import CELLS,SIGN_E_STRATEGY,STRATEGIES as EXP048_STRATEGIES,generate_experiment_048_stream,run_experiment_048_strategy
from experiment_032 import _run_composed_gate

OPERATIVE_SPEC_ISSUE=136
PAIR_SIGN_STRATEGY='covariance_matched_discovery_20sign_exact_binomial_context_composed_risk_gate'
STRATEGIES=(PAIR_SIGN_STRATEGY,)+EXP048_STRATEGIES
SIGN_COUNT=20
POSITIVE_CUTOFF=16
P16_NUMERATOR=6196
P16_DENOMINATOR=1048576
P16=P16_NUMERATOR/P16_DENOMINATOR
ACCEPT_E=1.0/P16


def generate_experiment_049_stream(seed,c):return generate_experiment_048_stream(seed,c)

def _pairwise_confirmation(stream,r,edge):
 target,(bd,bc)=split_indices(r)
 if len(bc)!=2:raise AssertionError((r,bc))
 out=[]
 for obs,tgt in (edge,(edge[1],edge[0])):
  tc=target[tgt][1]
  if len(tc)!=3:raise AssertionError((r,tgt,tc))
  vals=[]
  for k in range(2):
   vals.append(float(stream[f'probe_obs_{obs}'][tc[k]])-float(stream[f'probe_obs_{obs}'][bc[k]]))
  out.append(tuple(vals))
 return tuple(out)

def infer_20sign_exact_binomial(stream):
 mats={r:response_matrices(stream,r) for r in range(1,6)};y,scores,candidate=discovery_profile(mats);edge=HYP_EDGE[candidate]
 path=[];positive=0;zero=0
 for r in range(1,6):
  pairs=_pairwise_confirmation(stream,r,edge);flat=tuple(x for pair in pairs for x in pair)
  positive+=sum(int(x>0.0) for x in flat);zero+=sum(int(x==0.0) for x in flat)
  terminal=int(r==5);E=(ACCEPT_E if terminal and positive>=POSITIVE_CUTOFF else 0.0)
  path.append({'stage':r,'candidate':candidate,'e_value':E,'pairwise_responses':flat,'positive_sign_count':positive,'zero_sign_count':zero})
 final=path[-1]['e_value'];accepted=int(final>=E_THRESHOLD)
 return (groups_from_edges([edge]) if accepted else None),accepted,1-accepted,5,path,mats,y,scores

def _annotation(stream,accepted,abstain,path,mats,y,scores):
 cand=path[0]['candidate'];final=path[-1]['e_value']
 out={'probe_gain':stream['probe_gain'],'probe_stop_round':5 if accepted else 0,'probe_energy':sum(15.0*(float(a)**2) for a in ALL_AMPLITUDES),'probe_block_count':15,'probe_max_amplitude':float(max(ALL_AMPLITUDES)),
      'provenance_accepted':accepted,'provenance_abstain':abstain,'posterior_deploy_hypothesis':cand if accepted else '','posterior_at_deployment':'','posterior_implied_error_risk':'','posterior_expected_wrong_action_loss':'',
      'sign49_candidate':cand,'sign49_e_threshold':E_THRESHOLD,'sign49_e_final':final,'sign49_discovery_acceptance':0,'sign49_candidate_reselected':0,'sign49_spec_issue':OPERATIVE_SPEC_ISSUE,
      'sign49_rule':'Experiment-047 covariance-matched discovery; 20 disjoint held-out pairwise signs; exact Bin(20,0.5) S>=16 terminal e-variable','sign49_amp_denom':AMP_DENOM,
      'sign49_sign_count':SIGN_COUNT,'sign49_positive_cutoff':POSITIVE_CUTOFF,'sign49_p16_numerator':P16_NUMERATOR,'sign49_p16_denominator':P16_DENOMINATOR,'sign49_p16':P16,'sign49_accept_e':ACCEPT_E,
      'sign49_positive_sign_count':path[-1]['positive_sign_count'],'sign49_zero_sign_count':path[-1]['zero_sign_count']}
 for pair,val in zip(VECTOR,y):out['sign49_Y_'+''.join(pair)]=val
 for h,v in scores.items():out['sign49_Q_'+h]=v
 for r in range(1,6):
  target,(bd,bc)=split_indices(r);out[f'sign49_baseline_discovery_r{r}']=','.join(map(str,bd));out[f'sign49_baseline_confirmation_r{r}']=','.join(map(str,bc))
  for tgt,(td,tc) in target.items():
   out[f'sign49_target_discovery_r{r}_{tgt}']=','.join(map(str,td));out[f'sign49_target_confirmation_r{r}_{tgt}']=','.join(map(str,tc));out[f'sign49_target_unused_r{r}_{tgt}']=str(tc[2])
  D,_=mats[r]
  for i,j in (('a','b'),('a','c'),('b','c')):
   out[f'sign49_Ddisc_r{r}_{i}{j}']=D[(i,j)];out[f'sign49_Ddisc_r{r}_{j}{i}']=D[(j,i)]
  row=path[r-1];out[f'sign49_e_r{r}']=row['e_value'];out[f'sign49_positive_count_r{r}']=row['positive_sign_count'];out[f'sign49_zero_count_r{r}']=row['zero_sign_count']
  for k,x in enumerate(row['pairwise_responses'],1):out[f'sign49_pair_response_r{r}_{k}']=x
 return out

@contextmanager
def bind_experiment_049_stream(stream):
 targets=(('experiment_022','generate_stress_stream'),('experiment_029','generate_stress_stream'),('experiment_032','generate_stress_stream'))
 old=[]
 def fixed(*args,**kwargs):return deepcopy(stream)
 try:
  for mn,n in targets:
   m=importlib.import_module(mn);old.append((m,n,getattr(m,n)));setattr(m,n,fixed)
  yield
 finally:
  for m,n,v in reversed(old):setattr(m,n,v)

def run_experiment_049_strategy(seed,c,strategy,vals):
 if strategy not in STRATEGIES:raise ValueError(strategy)
 if strategy!=PAIR_SIGN_STRATEGY:return run_experiment_048_strategy(seed,c,strategy,vals)
 stream=generate_experiment_049_stream(seed,c);groups,accepted,abstain,stop,path,mats,y,scores=infer_20sign_exact_binomial(stream);ann=_annotation(stream,accepted,abstain,path,mats,y,scores);tau,kappa,k3,la,lb,lc,lab,lac,lbc,*_=vals
 if abstain:
  rows=run_triad_persistence_on_stream(seed,f'experiment049_{c["label"]}',tau,k3,stream)
  for r in rows:r['strategy']=PAIR_SIGN_STRATEGY;r.update(ann)
 else:
  rows=_run_composed_gate(seed,f'experiment049_{c["label"]}',tau,k3,la,lb,lc,lab,lac,lbc,stream,ann,groups)
  for r in rows:r['strategy']=PAIR_SIGN_STRATEGY
 for r in rows:
  r['experiment049_cell']=c['label'];r['experiment049_noise_family']=c['noise_family'];r['experiment049_no_tuning']=1
 return rows
