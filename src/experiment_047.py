from __future__ import annotations
from contextlib import contextmanager
from copy import deepcopy
from math import sqrt
import importlib
from experiment_010 import run_triad_persistence_on_stream
from experiment_016 import SIGMA_PROBE,groups_from_edges
from experiment_018 import ALL_AMPLITUDES
from experiment_028 import VECTOR,TOPOLOGY_DIRECTIONS
from experiment_029 import TRIAD
from experiment_032 import COMPOSED_STRATEGY,_run_composed_gate,run_experiment_032_strategy
from experiment_036 import ROBUST_STRATEGY,generate_experiment_036_stream,run_experiment_036_strategy
from experiment_037 import MODEL_AVERAGED_STRATEGY,run_experiment_037_strategy
from experiment_039 import RADIAL_HUBER_STRATEGY,run_experiment_039_strategy
from experiment_042 import LOCAL_GAUSSIAN_GROSS_STRATEGY,run_experiment_042_strategy
from experiment_044 import DIRECTIONAL_GAUSSIAN_STRATEGY,run_experiment_044_strategy
from experiment_045 import SYMMETRY_E_STRATEGY,run_experiment_045_strategy
from experiment_046 import WITHIN_SPLIT_E_STRATEGY,E_THRESHOLD,BASELINE_SLICES,EDGES,HYP,CELLS,split_indices,response_matrices,bet_factor,run_experiment_046_strategy

OPERATIVE_SPEC_ISSUE=125
COV_MATCHED_E_STRATEGY='covariance_matched_discovery_symmetry_eprocess_context_composed_risk_gate'
STRATEGIES=(COV_MATCHED_E_STRATEGY,WITHIN_SPLIT_E_STRATEGY,SYMMETRY_E_STRATEGY,COMPOSED_STRATEGY,DIRECTIONAL_GAUSSIAN_STRATEGY,ROBUST_STRATEGY,MODEL_AVERAGED_STRATEGY,RADIAL_HUBER_STRATEGY,LOCAL_GAUSSIAN_GROSS_STRATEGY,TRIAD)
AMP_DENOM=sqrt(sum(float(a)*float(a) for a in ALL_AMPLITUDES))
BLOCK_PRECISION=((4.0/3.0,-2.0/3.0),(-2.0/3.0,4.0/3.0))
HYP_EDGE={'H_ab':('a','b'),'H_ac':('a','c'),'H_bc':('b','c')}

def generate_experiment_047_stream(seed,c):return generate_experiment_036_stream(seed,c)

def _apply_scale_free_precision(x):
 out=[0.0]*6
 for i,j in ((0,1),(2,3),(4,5)):
  out[i]=(4.0*x[i]-2.0*x[j])/3.0;out[j]=(4.0*x[j]-2.0*x[i])/3.0
 return tuple(out)

def _dot(a,b):return sum(float(x)*float(y) for x,y in zip(a,b))

def discovery_profile(mats):
 y=tuple(sum(float(ALL_AMPLITUDES[r-1])*float(mats[r][0][pair]) for r in range(1,6))/AMP_DENOM for pair in VECTOR)
 py=_apply_scale_free_precision(y);scores={}
 for h,u in TOPOLOGY_DIRECTIONS.items():
  pu=_apply_scale_free_precision(u);num=max(0.0,_dot(u,py));den=_dot(u,pu)
  if den<=0:raise FloatingPointError((h,den))
  scores[h]=(num*num)/den
 order=('H_ab','H_ac','H_bc');candidate=max(order,key=lambda h:(scores[h],-order.index(h)))
 return y,scores,candidate

def infer_cov_matched_eprocess(stream):
 mats={r:response_matrices(stream,r) for r in range(1,6)};y,scores,candidate=discovery_profile(mats);edge=HYP_EDGE[candidate]
 E=1.0;path=[]
 for r in range(1,6):
  C=mats[r][1];x1=C[edge];x2=C[(edge[1],edge[0])];f1=bet_factor(x1);f2=bet_factor(x2);E*=f1*f2
  path.append({'stage':r,'candidate':candidate,'e_value':E,'factors':(f1,f2),'responses':(x1,x2)})
 accepted=int(E>=E_THRESHOLD)
 return (groups_from_edges([edge]) if accepted else None),accepted,1-accepted,5,path,mats,y,scores

def _annotation(stream,accepted,abstain,path,mats,y,scores):
 cand=path[0]['candidate'];final=path[-1]['e_value']
 out={'probe_gain':stream['probe_gain'],'probe_stop_round':5 if accepted else 0,'probe_energy':sum(15.0*(float(a)**2) for a in ALL_AMPLITUDES),'probe_block_count':15,'probe_max_amplitude':float(max(ALL_AMPLITUDES)),
      'provenance_accepted':accepted,'provenance_abstain':abstain,'posterior_deploy_hypothesis':cand if accepted else '','posterior_at_deployment':'','posterior_implied_error_risk':'','posterior_expected_wrong_action_loss':'',
      'cov47_candidate':cand,'cov47_e_threshold':E_THRESHOLD,'cov47_e_final':final,'cov47_sigma_probe':SIGMA_PROBE,'cov47_discovery_acceptance':0,'cov47_candidate_reselected':0,'cov47_spec_issue':OPERATIVE_SPEC_ISSUE,
      'cov47_rule':'all-round discovery-only six-direction covariance-matched nonnegative-amplitude profile selector; Experiment-046 held-out confirmation; terminal E>=100','cov47_amp_denom':AMP_DENOM}
 for pair,val in zip(VECTOR,y):out['cov47_Y_'+''.join(pair)]=val
 for h,v in scores.items():out['cov47_Q_'+h]=v
 for r in range(1,6):
  target,(bd,bc)=split_indices(r);out[f'cov47_baseline_discovery_r{r}']=','.join(map(str,bd));out[f'cov47_baseline_confirmation_r{r}']=','.join(map(str,bc))
  for tgt,(td,tc) in target.items():out[f'cov47_target_discovery_r{r}_{tgt}']=','.join(map(str,td));out[f'cov47_target_confirmation_r{r}_{tgt}']=','.join(map(str,tc))
  D,C=mats[r]
  for i,j in EDGES:
   out[f'cov47_Ddisc_r{r}_{i}{j}']=D[(i,j)];out[f'cov47_Ddisc_r{r}_{j}{i}']=D[(j,i)];out[f'cov47_Dconf_r{r}_{i}{j}']=C[(i,j)];out[f'cov47_Dconf_r{r}_{j}{i}']=C[(j,i)]
  row=path[r-1];out[f'cov47_e_r{r}']=row['e_value'];out[f'cov47_factor_r{r}_forward']=row['factors'][0];out[f'cov47_factor_r{r}_reverse']=row['factors'][1];out[f'cov47_response_r{r}_forward']=row['responses'][0];out[f'cov47_response_r{r}_reverse']=row['responses'][1]
 return out

@contextmanager
def bind_experiment_047_stream(stream):
 targets=(('experiment_022','generate_stress_stream'),('experiment_029','generate_stress_stream'),('experiment_032','generate_stress_stream'))
 old=[]
 def fixed(*args,**kwargs):return deepcopy(stream)
 try:
  for mn,n in targets:
   m=importlib.import_module(mn);old.append((m,n,getattr(m,n)));setattr(m,n,fixed)
  yield
 finally:
  for m,n,v in reversed(old):setattr(m,n,v)

def run_experiment_047_strategy(seed,c,strategy,vals):
 if strategy not in STRATEGIES:raise ValueError(strategy)
 if strategy==WITHIN_SPLIT_E_STRATEGY:return run_experiment_046_strategy(seed,c,strategy,vals)
 if strategy==SYMMETRY_E_STRATEGY:return run_experiment_045_strategy(seed,c,strategy,vals)
 if strategy==DIRECTIONAL_GAUSSIAN_STRATEGY:return run_experiment_044_strategy(seed,c,strategy,vals)
 if strategy==ROBUST_STRATEGY:return run_experiment_036_strategy(seed,c,strategy,vals)
 if strategy==MODEL_AVERAGED_STRATEGY:return run_experiment_037_strategy(seed,c,strategy,vals)
 if strategy==RADIAL_HUBER_STRATEGY:return run_experiment_039_strategy(seed,c,strategy,vals)
 if strategy==LOCAL_GAUSSIAN_GROSS_STRATEGY:return run_experiment_042_strategy(seed,c,strategy,vals)
 stream=generate_experiment_047_stream(seed,c)
 if strategy!=COV_MATCHED_E_STRATEGY:
  with bind_experiment_047_stream(stream):rows=run_experiment_032_strategy(seed,c,strategy,vals)
 else:
  groups,accepted,abstain,stop,path,mats,y,scores=infer_cov_matched_eprocess(stream);ann=_annotation(stream,accepted,abstain,path,mats,y,scores);tau,kappa,k3,la,lb,lc,lab,lac,lbc,*_=vals
  if abstain:
   rows=run_triad_persistence_on_stream(seed,f'experiment047_{c["label"]}',tau,k3,stream)
   for r in rows:r['strategy']=COV_MATCHED_E_STRATEGY;r.update(ann)
  else:
   rows=_run_composed_gate(seed,f'experiment047_{c["label"]}',tau,k3,la,lb,lc,lab,lac,lbc,stream,ann,groups)
   for r in rows:r['strategy']=COV_MATCHED_E_STRATEGY
 for r in rows:
  r['experiment047_cell']=c['label'];r['experiment047_noise_family']=c['noise_family'];r['experiment047_no_tuning']=1
 return rows
