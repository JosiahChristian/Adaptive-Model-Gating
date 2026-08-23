from __future__ import annotations
from contextlib import contextmanager
from copy import deepcopy
from math import isfinite,tanh
from statistics import mean
import importlib
from experiment_010 import run_triad_persistence_on_stream
from experiment_016 import SIGMA_PROBE,ROUND_BLOCKS,groups_from_edges
from experiment_018 import ROUND5_BLOCKS,ALL_AMPLITUDES
from experiment_029 import WRONG_COST,FALLBACK_COST,TRIAD
from experiment_032 import COMPOSED_STRATEGY,_run_composed_gate,run_experiment_032_strategy
from experiment_036 import ROBUST_STRATEGY,generate_experiment_036_stream,run_experiment_036_strategy
from experiment_037 import MODEL_AVERAGED_STRATEGY,run_experiment_037_strategy
from experiment_039 import RADIAL_HUBER_STRATEGY,run_experiment_039_strategy
from experiment_040 import LOCAL_MIXTURE_STRATEGY,run_experiment_040_strategy
from experiment_041 import LOCAL_CAUCHY_STRATEGY,run_experiment_041_strategy
from experiment_042 import LOCAL_GAUSSIAN_GROSS_STRATEGY,run_experiment_042_strategy
from experiment_043 import REPLICATED_GAUSSIAN_STRATEGY,run_experiment_043_strategy
from experiment_044 import DIRECTIONAL_GAUSSIAN_STRATEGY,run_experiment_044_strategy

OPERATIVE_SPEC_ISSUE=115
SYMMETRY_E_STRATEGY='sample_split_symmetry_eprocess_context_composed_risk_gate'
E_THRESHOLD=100.0
BASELINE_SLICES={1:range(181,185),2:range(185,189),3:range(189,193),4:range(193,197),5:range(197,201)}
EDGES=(('a','b'),('a','c'),('b','c'))
HYP={('a','b'):'H_ab',('a','c'):'H_ac',('b','c'):'H_bc'}
EDGE_BY_H={v:k for k,v in HYP.items()}
STRATEGIES=(SYMMETRY_E_STRATEGY,COMPOSED_STRATEGY,REPLICATED_GAUSSIAN_STRATEGY,DIRECTIONAL_GAUSSIAN_STRATEGY,ROBUST_STRATEGY,MODEL_AVERAGED_STRATEGY,RADIAL_HUBER_STRATEGY,LOCAL_MIXTURE_STRATEGY,LOCAL_CAUCHY_STRATEGY,LOCAL_GAUSSIAN_GROSS_STRATEGY,TRIAD)

def cell(label,nf,gain,scale):return {'label':label,'kind':'noise','family':'drift_ab_fault','magnitude':0.50,'noise_family':nf,'gain':float(gain),'noise_scale':float(scale),'topology_truth':'H_ab'}
def frozen_cells():
 out=[]
 for nf in ('gaussian','laplace','student_t3','contaminated_gaussian'):
  for g in (0.50,0.425):
   for s in (1.00,1.50):out.append(cell(f'{nf}_g{g:.3f}_n{s:.2f}',nf,g,s))
 if len(out)!=16:raise AssertionError(len(out))
 return tuple(out)
CELLS=frozen_cells()

def generate_experiment_045_stream(seed,c):return generate_experiment_036_stream(seed,c)

def _target_blocks(r):return ROUND_BLOCKS[r] if r<=4 else ROUND5_BLOCKS

def split_response_matrix(stream,r):
 b=BASELINE_SLICES[r];blocks=_target_blocks(r);out={}
 for obs in 'abc':
  base=mean(float(stream[f'probe_obs_{obs}'][t]) for t in b)
  for target,ts in blocks.items():out[(obs,target)]=mean(float(stream[f'probe_obs_{obs}'][t]) for t in ts)-base
 return out

def _sign(x):return 1.0 if x>0 else (-1.0 if x<0 else 0.0)
def bet_factor(x):
 x=float(x);m=1.0+_sign(x)*tanh(abs(x)/SIGMA_PROBE)
 if not isfinite(m) or m<0.0:raise FloatingPointError((x,m))
 return m

def infer_symmetry_eprocess(stream):
 mats={r:split_response_matrix(stream,r) for r in range(1,6)}
 scores={e:mats[1][e]+mats[1][(e[1],e[0])] for e in EDGES}
 edge=max(EDGES,key=lambda e:(scores[e],-EDGES.index(e)))
 candidate=HYP[edge];E=1.0;path=[{'stage':1,'candidate':candidate,'discovery_score':scores[edge],'e_value':E,'crossing':0,'factors':()}]
 stop=0
 for r in range(2,6):
  x1=mats[r][edge];x2=mats[r][(edge[1],edge[0])];f1=bet_factor(x1);f2=bet_factor(x2);E*=f1*f2;cross=int(E>=E_THRESHOLD)
  path.append({'stage':r,'candidate':candidate,'discovery_score':scores[edge],'e_value':E,'crossing':cross,'factors':(f1,f2),'responses':(x1,x2)})
  if cross:
   stop=r;break
 if stop:return groups_from_edges([edge]),1,0,stop,path,mats,scores
 return None,0,1,0,path,mats,scores

def _energy(stop,path):
 n=stop if stop else 5
 return sum(15.0*(float(ALL_AMPLITUDES[r-1])**2) for r in range(1,n+1))

def _annotation(stream,groups,accepted,abstain,stop,path,mats,scores):
 last=path[(stop-1) if stop else -1];cand=path[0]['candidate']
 out={'probe_gain':stream['probe_gain'],'probe_stop_round':stop,'probe_energy':_energy(stop,path),'probe_block_count':3*(stop if stop else 5),'probe_max_amplitude':float(ALL_AMPLITUDES[(stop if stop else 5)-1]),
      'provenance_accepted':accepted,'provenance_abstain':abstain,'posterior_deploy_hypothesis':cand if accepted else '','posterior_at_deployment':'','posterior_implied_error_risk':'','posterior_expected_wrong_action_loss':'',
      'symmetry_candidate':cand,'symmetry_discovery_score':path[0]['discovery_score'],'symmetry_e_threshold':E_THRESHOLD,'symmetry_e_final':last['e_value'],'symmetry_sigma_probe':SIGMA_PROBE,
      'symmetry_discovery_acceptance':0,'symmetry_candidate_reselected':0,'symmetry_rule':'m(x)=1+sgn(x)*tanh(|x|/0.05); E>=100','symmetry_spec_issue':OPERATIVE_SPEC_ISSUE}
 for e,v in scores.items():out['symmetry_discovery_score_'+''.join(e)]=v
 for r in range(1,6):
  out[f'symmetry_baseline_start_r{r}']=BASELINE_SLICES[r].start;out[f'symmetry_baseline_stop_r{r}']=BASELINE_SLICES[r].stop-1
  M=mats[r]
  for i,j in EDGES:
   out[f'symmetry_D_r{r}_{i}{j}']=M[(i,j)];out[f'symmetry_D_r{r}_{j}{i}']=M[(j,i)]
 for row in path:
  r=row['stage'];out[f'symmetry_e_r{r}']=row['e_value'];out[f'symmetry_cross_r{r}']=row['crossing']
  if r>=2:
   out[f'symmetry_factor_r{r}_forward']=row['factors'][0];out[f'symmetry_factor_r{r}_reverse']=row['factors'][1]
   out[f'symmetry_response_r{r}_forward']=row['responses'][0];out[f'symmetry_response_r{r}_reverse']=row['responses'][1]
 return out

@contextmanager
def bind_experiment_045_stream(stream):
 targets=(('experiment_022','generate_stress_stream'),('experiment_029','generate_stress_stream'),('experiment_032','generate_stress_stream'))
 old=[]
 def fixed(*args,**kwargs):return deepcopy(stream)
 try:
  for mn,n in targets:
   m=importlib.import_module(mn);old.append((m,n,getattr(m,n)));setattr(m,n,fixed)
  yield
 finally:
  for m,n,v in reversed(old):setattr(m,n,v)

def run_experiment_045_strategy(seed,c,strategy,vals):
 if strategy not in STRATEGIES:raise ValueError(strategy)
 if strategy==REPLICATED_GAUSSIAN_STRATEGY:return run_experiment_043_strategy(seed,c,strategy,vals)
 if strategy==DIRECTIONAL_GAUSSIAN_STRATEGY:return run_experiment_044_strategy(seed,c,strategy,vals)
 if strategy==ROBUST_STRATEGY:return run_experiment_036_strategy(seed,c,strategy,vals)
 if strategy==MODEL_AVERAGED_STRATEGY:return run_experiment_037_strategy(seed,c,strategy,vals)
 if strategy==RADIAL_HUBER_STRATEGY:return run_experiment_039_strategy(seed,c,strategy,vals)
 if strategy==LOCAL_MIXTURE_STRATEGY:return run_experiment_040_strategy(seed,c,strategy,vals)
 if strategy==LOCAL_CAUCHY_STRATEGY:return run_experiment_041_strategy(seed,c,strategy,vals)
 if strategy==LOCAL_GAUSSIAN_GROSS_STRATEGY:return run_experiment_042_strategy(seed,c,strategy,vals)
 stream=generate_experiment_045_stream(seed,c)
 if strategy!=SYMMETRY_E_STRATEGY:
  with bind_experiment_045_stream(stream):rows=run_experiment_032_strategy(seed,c,strategy,vals)
 else:
  groups,accepted,abstain,stop,path,mats,scores=infer_symmetry_eprocess(stream);ann=_annotation(stream,groups,accepted,abstain,stop,path,mats,scores);tau,kappa,k3,la,lb,lc,lab,lac,lbc,*_=vals
  if abstain:
   rows=run_triad_persistence_on_stream(seed,f'experiment045_{c["label"]}',tau,k3,stream)
   for r in rows:r['strategy']=SYMMETRY_E_STRATEGY;r.update(ann)
  else:
   rows=_run_composed_gate(seed,f'experiment045_{c["label"]}',tau,k3,la,lb,lc,lab,lac,lbc,stream,ann,groups)
   for r in rows:r['strategy']=SYMMETRY_E_STRATEGY
 for r in rows:
  r['experiment045_cell']=c['label'];r['experiment045_noise_family']=c['noise_family'];r['experiment045_no_tuning']=1
 return rows
