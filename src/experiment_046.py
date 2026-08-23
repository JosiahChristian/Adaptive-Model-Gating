from __future__ import annotations
from contextlib import contextmanager
from copy import deepcopy
from math import isfinite,tanh
from statistics import mean
import importlib
from experiment_010 import run_triad_persistence_on_stream
from experiment_016 import SIGMA_PROBE,ROUND_BLOCKS,groups_from_edges
from experiment_018 import ROUND5_BLOCKS,ALL_AMPLITUDES
from experiment_029 import TRIAD
from experiment_032 import COMPOSED_STRATEGY,_run_composed_gate,run_experiment_032_strategy
from experiment_036 import ROBUST_STRATEGY,generate_experiment_036_stream,run_experiment_036_strategy
from experiment_037 import MODEL_AVERAGED_STRATEGY,run_experiment_037_strategy
from experiment_039 import RADIAL_HUBER_STRATEGY,run_experiment_039_strategy
from experiment_040 import LOCAL_MIXTURE_STRATEGY,run_experiment_040_strategy
from experiment_041 import LOCAL_CAUCHY_STRATEGY,run_experiment_041_strategy
from experiment_042 import LOCAL_GAUSSIAN_GROSS_STRATEGY,run_experiment_042_strategy
from experiment_043 import REPLICATED_GAUSSIAN_STRATEGY,run_experiment_043_strategy
from experiment_044 import DIRECTIONAL_GAUSSIAN_STRATEGY,run_experiment_044_strategy
from experiment_045 import SYMMETRY_E_STRATEGY,run_experiment_045_strategy

OPERATIVE_SPEC_ISSUE=120
WITHIN_SPLIT_E_STRATEGY='within_round_split_symmetry_eprocess_context_composed_risk_gate'
E_THRESHOLD=100.0
BASELINE_SLICES={1:range(181,185),2:range(185,189),3:range(189,193),4:range(193,197),5:range(197,201)}
EDGES=(('a','b'),('a','c'),('b','c'))
HYP={('a','b'):'H_ab',('a','c'):'H_ac',('b','c'):'H_bc'}
STRATEGIES=(WITHIN_SPLIT_E_STRATEGY,SYMMETRY_E_STRATEGY,COMPOSED_STRATEGY,REPLICATED_GAUSSIAN_STRATEGY,DIRECTIONAL_GAUSSIAN_STRATEGY,ROBUST_STRATEGY,MODEL_AVERAGED_STRATEGY,RADIAL_HUBER_STRATEGY,LOCAL_MIXTURE_STRATEGY,LOCAL_CAUCHY_STRATEGY,LOCAL_GAUSSIAN_GROSS_STRATEGY,TRIAD)

def cell(label,nf,gain,scale):return {'label':label,'kind':'noise','family':'drift_ab_fault','magnitude':0.50,'noise_family':nf,'gain':float(gain),'noise_scale':float(scale),'topology_truth':'H_ab'}
def frozen_cells():
 out=[]
 for nf in ('gaussian','laplace','student_t3','contaminated_gaussian'):
  for g in (0.50,0.425):
   for s in (1.00,1.50):out.append(cell(f'{nf}_g{g:.3f}_n{s:.2f}',nf,g,s))
 if len(out)!=16:raise AssertionError(len(out))
 return tuple(out)
CELLS=frozen_cells()

def generate_experiment_046_stream(seed,c):return generate_experiment_036_stream(seed,c)
def _target_blocks(r):return ROUND_BLOCKS[r] if r<=4 else ROUND5_BLOCKS

def split_indices(r):
 blocks=_target_blocks(r);b=tuple(BASELINE_SLICES[r]);target={k:(tuple(ts)[:2],tuple(ts)[2:]) for k,ts in blocks.items()}
 return target,(b[:2],b[2:])

def response_matrices(stream,r):
 target,(bd,bc)=split_indices(r);disc={};conf={}
 for obs in 'abc':
  base_d=mean(float(stream[f'probe_obs_{obs}'][t]) for t in bd)
  base_c=mean(float(stream[f'probe_obs_{obs}'][t]) for t in bc)
  for tgt,(td,tc) in target.items():
   disc[(obs,tgt)]=mean(float(stream[f'probe_obs_{obs}'][t]) for t in td)-base_d
   conf[(obs,tgt)]=mean(float(stream[f'probe_obs_{obs}'][t]) for t in tc)-base_c
 return disc,conf

def _sign(x):return 1.0 if x>0 else (-1.0 if x<0 else 0.0)
def bet_factor(x):
 x=float(x);m=1.0+_sign(x)*tanh(abs(x)/SIGMA_PROBE)
 if not isfinite(m) or m<0.0:raise FloatingPointError((x,m))
 return m

def infer_within_split_eprocess(stream):
 mats={r:response_matrices(stream,r) for r in range(1,6)}
 scores={e:sum(float(ALL_AMPLITUDES[r-1])*(mats[r][0][e]+mats[r][0][(e[1],e[0])]) for r in range(1,6)) for e in EDGES}
 edge=max(EDGES,key=lambda e:(scores[e],-EDGES.index(e)));candidate=HYP[edge]
 E=1.0;path=[]
 for r in range(1,6):
  C=mats[r][1];x1=C[edge];x2=C[(edge[1],edge[0])];f1=bet_factor(x1);f2=bet_factor(x2);E*=f1*f2
  path.append({'stage':r,'candidate':candidate,'e_value':E,'factors':(f1,f2),'responses':(x1,x2)})
 accepted=int(E>=E_THRESHOLD)
 return (groups_from_edges([edge]) if accepted else None),accepted,1-accepted,5,path,mats,scores

def _annotation(stream,accepted,abstain,path,mats,scores):
 cand=path[0]['candidate'];final=path[-1]['e_value']
 out={'probe_gain':stream['probe_gain'],'probe_stop_round':5 if accepted else 0,'probe_energy':sum(15.0*(float(a)**2) for a in ALL_AMPLITUDES),'probe_block_count':15,'probe_max_amplitude':float(max(ALL_AMPLITUDES)),
      'provenance_accepted':accepted,'provenance_abstain':abstain,'posterior_deploy_hypothesis':cand if accepted else '','posterior_at_deployment':'','posterior_implied_error_risk':'','posterior_expected_wrong_action_loss':'',
      'within_candidate':cand,'within_e_threshold':E_THRESHOLD,'within_e_final':final,'within_sigma_probe':SIGMA_PROBE,'within_discovery_acceptance':0,'within_candidate_reselected':0,
      'within_rule':'all-round amplitude-weighted discovery on 2/5 target + 2/4 baseline; held-out 3/5 target + 2/4 baseline confirmation; terminal E>=100','within_spec_issue':OPERATIVE_SPEC_ISSUE}
 for e,v in scores.items():out['within_discovery_score_'+''.join(e)]=v
 for r in range(1,6):
  target,(bd,bc)=split_indices(r);out[f'within_baseline_discovery_r{r}']=','.join(map(str,bd));out[f'within_baseline_confirmation_r{r}']=','.join(map(str,bc))
  for tgt,(td,tc) in target.items():out[f'within_target_discovery_r{r}_{tgt}']=','.join(map(str,td));out[f'within_target_confirmation_r{r}_{tgt}']=','.join(map(str,tc))
  D,C=mats[r]
  for i,j in EDGES:
   out[f'within_Ddisc_r{r}_{i}{j}']=D[(i,j)];out[f'within_Ddisc_r{r}_{j}{i}']=D[(j,i)];out[f'within_Dconf_r{r}_{i}{j}']=C[(i,j)];out[f'within_Dconf_r{r}_{j}{i}']=C[(j,i)]
  row=path[r-1];out[f'within_e_r{r}']=row['e_value'];out[f'within_factor_r{r}_forward']=row['factors'][0];out[f'within_factor_r{r}_reverse']=row['factors'][1];out[f'within_response_r{r}_forward']=row['responses'][0];out[f'within_response_r{r}_reverse']=row['responses'][1]
 return out

@contextmanager
def bind_experiment_046_stream(stream):
 targets=(('experiment_022','generate_stress_stream'),('experiment_029','generate_stress_stream'),('experiment_032','generate_stress_stream'))
 old=[]
 def fixed(*args,**kwargs):return deepcopy(stream)
 try:
  for mn,n in targets:
   m=importlib.import_module(mn);old.append((m,n,getattr(m,n)));setattr(m,n,fixed)
  yield
 finally:
  for m,n,v in reversed(old):setattr(m,n,v)

def run_experiment_046_strategy(seed,c,strategy,vals):
 if strategy not in STRATEGIES:raise ValueError(strategy)
 if strategy==SYMMETRY_E_STRATEGY:return run_experiment_045_strategy(seed,c,strategy,vals)
 if strategy==REPLICATED_GAUSSIAN_STRATEGY:return run_experiment_043_strategy(seed,c,strategy,vals)
 if strategy==DIRECTIONAL_GAUSSIAN_STRATEGY:return run_experiment_044_strategy(seed,c,strategy,vals)
 if strategy==ROBUST_STRATEGY:return run_experiment_036_strategy(seed,c,strategy,vals)
 if strategy==MODEL_AVERAGED_STRATEGY:return run_experiment_037_strategy(seed,c,strategy,vals)
 if strategy==RADIAL_HUBER_STRATEGY:return run_experiment_039_strategy(seed,c,strategy,vals)
 if strategy==LOCAL_MIXTURE_STRATEGY:return run_experiment_040_strategy(seed,c,strategy,vals)
 if strategy==LOCAL_CAUCHY_STRATEGY:return run_experiment_041_strategy(seed,c,strategy,vals)
 if strategy==LOCAL_GAUSSIAN_GROSS_STRATEGY:return run_experiment_042_strategy(seed,c,strategy,vals)
 stream=generate_experiment_046_stream(seed,c)
 if strategy!=WITHIN_SPLIT_E_STRATEGY:
  with bind_experiment_046_stream(stream):rows=run_experiment_032_strategy(seed,c,strategy,vals)
 else:
  groups,accepted,abstain,stop,path,mats,scores=infer_within_split_eprocess(stream);ann=_annotation(stream,accepted,abstain,path,mats,scores);tau,kappa,k3,la,lb,lc,lab,lac,lbc,*_=vals
  if abstain:
   rows=run_triad_persistence_on_stream(seed,f'experiment046_{c["label"]}',tau,k3,stream)
   for r in rows:r['strategy']=WITHIN_SPLIT_E_STRATEGY;r.update(ann)
  else:
   rows=_run_composed_gate(seed,f'experiment046_{c["label"]}',tau,k3,la,lb,lc,lab,lac,lbc,stream,ann,groups)
   for r in rows:r['strategy']=WITHIN_SPLIT_E_STRATEGY
 for r in rows:
  r['experiment046_cell']=c['label'];r['experiment046_noise_family']=c['noise_family'];r['experiment046_no_tuning']=1
 return rows
