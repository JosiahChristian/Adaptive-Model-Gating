from __future__ import annotations
from contextlib import contextmanager
from copy import deepcopy
import importlib
from experiment_010 import run_triad_persistence_on_stream
from experiment_016 import groups_from_edges
from experiment_018 import ALL_AMPLITUDES
from experiment_028 import VECTOR
from experiment_029 import TRIAD
from experiment_032 import _run_composed_gate
from experiment_046 import E_THRESHOLD,EDGES,split_indices,response_matrices
from experiment_047 import CELLS,COV_MATCHED_E_STRATEGY,STRATEGIES as EXP047_STRATEGIES,AMP_DENOM,BLOCK_PRECISION,HYP_EDGE,discovery_profile,generate_experiment_047_stream,run_experiment_047_strategy

OPERATIVE_SPEC_ISSUE=130
SIGN_E_STRATEGY='covariance_matched_discovery_exact_sign_eprocess_context_composed_risk_gate'
STRATEGIES=(SIGN_E_STRATEGY,)+EXP047_STRATEGIES
EXACT_ALL_POSITIVE_TAIL=1.0/1024.0
EXACT_GE9_TAIL=11.0/1024.0

def sign_factor(x):
 x=float(x)
 if x>0.0:return 2.0
 if x<0.0:return 0.0
 return 1.0

def generate_experiment_048_stream(seed,c):return generate_experiment_047_stream(seed,c)

def infer_exact_sign_eprocess(stream):
 mats={r:response_matrices(stream,r) for r in range(1,6)};y,scores,candidate=discovery_profile(mats);edge=HYP_EDGE[candidate]
 E=1.0;path=[]
 for r in range(1,6):
  C=mats[r][1];x1=C[edge];x2=C[(edge[1],edge[0])];f1=sign_factor(x1);f2=sign_factor(x2);E*=f1*f2
  path.append({'stage':r,'candidate':candidate,'e_value':E,'factors':(f1,f2),'responses':(x1,x2),'positive_sign_count':sum(int(float(z)>0.0) for p in path for z in p['responses'])+int(float(x1)>0.0)+int(float(x2)>0.0)})
 accepted=int(E>=E_THRESHOLD)
 return (groups_from_edges([edge]) if accepted else None),accepted,1-accepted,5,path,mats,y,scores

def _annotation(stream,accepted,abstain,path,mats,y,scores):
 cand=path[0]['candidate'];final=path[-1]['e_value']
 out={'probe_gain':stream['probe_gain'],'probe_stop_round':5 if accepted else 0,'probe_energy':sum(15.0*(float(a)**2) for a in ALL_AMPLITUDES),'probe_block_count':15,'probe_max_amplitude':float(max(ALL_AMPLITUDES)),
      'provenance_accepted':accepted,'provenance_abstain':abstain,'posterior_deploy_hypothesis':cand if accepted else '','posterior_at_deployment':'','posterior_implied_error_risk':'','posterior_expected_wrong_action_loss':'',
      'sign48_candidate':cand,'sign48_e_threshold':E_THRESHOLD,'sign48_e_final':final,'sign48_discovery_acceptance':0,'sign48_candidate_reselected':0,'sign48_spec_issue':OPERATIVE_SPEC_ISSUE,
      'sign48_rule':'Experiment-047 covariance-matched discovery; ten held-out exact sign factors 2/0 (tie 1); terminal E>=100','sign48_amp_denom':AMP_DENOM,
      'sign48_exact_10of10_tail':EXACT_ALL_POSITIVE_TAIL,'sign48_exact_ge9_tail':EXACT_GE9_TAIL,'sign48_positive_sign_count':path[-1]['positive_sign_count']}
 for pair,val in zip(VECTOR,y):out['sign48_Y_'+''.join(pair)]=val
 for h,v in scores.items():out['sign48_Q_'+h]=v
 for r in range(1,6):
  target,(bd,bc)=split_indices(r);out[f'sign48_baseline_discovery_r{r}']=','.join(map(str,bd));out[f'sign48_baseline_confirmation_r{r}']=','.join(map(str,bc))
  for tgt,(td,tc) in target.items():out[f'sign48_target_discovery_r{r}_{tgt}']=','.join(map(str,td));out[f'sign48_target_confirmation_r{r}_{tgt}']=','.join(map(str,tc))
  D,C=mats[r]
  for i,j in EDGES:
   out[f'sign48_Ddisc_r{r}_{i}{j}']=D[(i,j)];out[f'sign48_Ddisc_r{r}_{j}{i}']=D[(j,i)];out[f'sign48_Dconf_r{r}_{i}{j}']=C[(i,j)];out[f'sign48_Dconf_r{r}_{j}{i}']=C[(j,i)]
  row=path[r-1];out[f'sign48_e_r{r}']=row['e_value'];out[f'sign48_factor_r{r}_forward']=row['factors'][0];out[f'sign48_factor_r{r}_reverse']=row['factors'][1];out[f'sign48_response_r{r}_forward']=row['responses'][0];out[f'sign48_response_r{r}_reverse']=row['responses'][1]
 return out

@contextmanager
def bind_experiment_048_stream(stream):
 targets=(('experiment_022','generate_stress_stream'),('experiment_029','generate_stress_stream'),('experiment_032','generate_stress_stream'))
 old=[]
 def fixed(*args,**kwargs):return deepcopy(stream)
 try:
  for mn,n in targets:
   m=importlib.import_module(mn);old.append((m,n,getattr(m,n)));setattr(m,n,fixed)
  yield
 finally:
  for m,n,v in reversed(old):setattr(m,n,v)

def run_experiment_048_strategy(seed,c,strategy,vals):
 if strategy not in STRATEGIES:raise ValueError(strategy)
 if strategy!=SIGN_E_STRATEGY:return run_experiment_047_strategy(seed,c,strategy,vals)
 stream=generate_experiment_048_stream(seed,c);groups,accepted,abstain,stop,path,mats,y,scores=infer_exact_sign_eprocess(stream);ann=_annotation(stream,accepted,abstain,path,mats,y,scores);tau,kappa,k3,la,lb,lc,lab,lac,lbc,*_=vals
 if abstain:
  rows=run_triad_persistence_on_stream(seed,f'experiment048_{c["label"]}',tau,k3,stream)
  for r in rows:r['strategy']=SIGN_E_STRATEGY;r.update(ann)
 else:
  rows=_run_composed_gate(seed,f'experiment048_{c["label"]}',tau,k3,la,lb,lc,lab,lac,lbc,stream,ann,groups)
  for r in rows:r['strategy']=SIGN_E_STRATEGY
 for r in rows:
  r['experiment048_cell']=c['label'];r['experiment048_noise_family']=c['noise_family'];r['experiment048_no_tuning']=1
 return rows
