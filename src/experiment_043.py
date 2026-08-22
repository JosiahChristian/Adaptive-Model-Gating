from __future__ import annotations
from contextlib import contextmanager
from copy import deepcopy
import importlib
from experiment_016 import groups_from_edges
from experiment_023 import diagnostic_noise_factor
from experiment_027 import HYPOTHESES,inject_symmetric_round5
from experiment_028 import directed_stage,covariance_terms,posterior_from_directed
from experiment_029 import ACCEPT_THRESHOLD,WRONG_COST,FALLBACK_COST,TRIAD,_annotation
from experiment_032 import COMPOSED_STRATEGY,_run_composed_gate,run_experiment_032_strategy
from experiment_036 import ROBUST_STRATEGY,generate_experiment_036_stream,run_experiment_036_strategy
from experiment_037 import MODEL_AVERAGED_STRATEGY,run_experiment_037_strategy
from experiment_039 import RADIAL_HUBER_STRATEGY,run_experiment_039_strategy
from experiment_040 import LOCAL_MIXTURE_STRATEGY,run_experiment_040_strategy
from experiment_041 import LOCAL_CAUCHY_STRATEGY,run_experiment_041_strategy
from experiment_042 import LOCAL_GAUSSIAN_GROSS_STRATEGY,run_experiment_042_strategy

OPERATIVE_SPEC_ISSUE=102
REPLICATED_GAUSSIAN_STRATEGY='two_stage_replicated_gaussian_posterior_context_composed_risk_gate'
CONFIRMATIONS_REQUIRED=2
STRATEGIES=(REPLICATED_GAUSSIAN_STRATEGY,COMPOSED_STRATEGY,ROBUST_STRATEGY,MODEL_AVERAGED_STRATEGY,RADIAL_HUBER_STRATEGY,LOCAL_MIXTURE_STRATEGY,LOCAL_CAUCHY_STRATEGY,LOCAL_GAUSSIAN_GROSS_STRATEGY,TRIAD)
UNIQUE=('H_ab','H_ac','H_bc')
EDGE={'H_ab':('a','b'),'H_ac':('a','c'),'H_bc':('b','c')}

def cell(label,nf,gain,scale):return {'label':label,'kind':'noise','family':'drift_ab_fault','magnitude':0.50,'noise_family':nf,'gain':float(gain),'noise_scale':float(scale),'topology_truth':'H_ab'}
def frozen_cells():
 out=[]
 for nf in ('gaussian','laplace','student_t3','contaminated_gaussian'):
  for g in (0.50,0.425):
   for s in (1.00,1.50):out.append(cell(f'{nf}_g{g:.3f}_n{s:.2f}',nf,g,s))
 if len(out)!=16:raise AssertionError(len(out))
 return tuple(out)
CELLS=frozen_cells()

def generate_experiment_043_stream(seed,c):return generate_experiment_036_stream(seed,c)

@contextmanager
def bind_experiment_043_stream(stream):
 targets=(('experiment_022','generate_stress_stream'),('experiment_029','generate_stress_stream'),('experiment_032','generate_stress_stream'))
 old=[]
 def fixed(*args,**kwargs):return deepcopy(stream)
 try:
  for mn,n in targets:
   m=importlib.import_module(mn);old.append((m,n,getattr(m,n)));setattr(m,n,fixed)
  yield
 finally:
  for m,n,v in reversed(old):setattr(m,n,v)

def infer_replicated_gaussian(stream):
 _,sigma_hat=diagnostic_noise_factor(stream);path=[];last_crossing=None;run=0;resets=0
 for stage in range(1,6):
  y=directed_stage(stream,stage);var,cov=covariance_terms(sigma_hat,stage);post,logs,quad=posterior_from_directed(y,var,cov)
  cand=max(UNIQUE,key=lambda h:post[h]);p=float(post[cand]);cross=int(p>=ACCEPT_THRESHOLD);reset=0
  if cross:
   if last_crossing==cand:run+=1
   else:
    if last_crossing is not None:resets+=1;reset=1
    last_crossing=cand;run=1
  else:
   if last_crossing is not None:resets+=1;reset=1
   last_crossing=None;run=0
  confirmed=int(cross and run>=CONFIRMATIONS_REQUIRED)
  row={'stage':stage,'candidate':cand,'candidate_posterior':p,'posterior_error_risk':1.0-p,'expected_wrong_action_loss':WRONG_COST*(1.0-p),'posterior':post,'variance':var,'shared_covariance':cov,'mahalanobis_zero':quad,'threshold_crossing':cross,'confirmation_run':run,'confirmation_reset':reset,'confirmation_resets_total':resets,'confirmed':confirmed}
  path.append(row)
  if confirmed:return groups_from_edges([EDGE[cand]]),1,0,stage,path
 return None,0,1,0,path

def _replication_annotation(path,accepted,stop):
 out={'replication_confirmations_required':CONFIRMATIONS_REQUIRED,'replication_rule':'same candidate >=0.99 on two consecutive stages','replication_reset_rule':'different candidate or sub-threshold stage resets','replication_resets_total':path[-1]['confirmation_resets_total'] if path else 0,'replication_confirmed':int(bool(accepted))}
 for s in path:
  r=s['stage'];out[f'replication_r{r}_threshold_crossing']=s['threshold_crossing'];out[f'replication_r{r}_confirmation_run']=s['confirmation_run'];out[f'replication_r{r}_confirmation_reset']=s['confirmation_reset'];out[f'replication_r{r}_confirmed']=s['confirmed']
 if accepted:
  cur=path[stop-1];prev=path[stop-2]
  out['replication_previous_candidate']=prev['candidate'];out['replication_previous_posterior']=prev['candidate_posterior'];out['replication_accept_candidate']=cur['candidate'];out['replication_accept_posterior']=cur['candidate_posterior']
 else:
  out['replication_previous_candidate']='';out['replication_previous_posterior']='';out['replication_accept_candidate']='';out['replication_accept_posterior']=''
 return out

def run_experiment_043_strategy(seed,c,strategy,vals):
 if strategy not in STRATEGIES:raise ValueError(strategy)
 if strategy==ROBUST_STRATEGY:return run_experiment_036_strategy(seed,c,strategy,vals)
 if strategy==MODEL_AVERAGED_STRATEGY:return run_experiment_037_strategy(seed,c,strategy,vals)
 if strategy==RADIAL_HUBER_STRATEGY:return run_experiment_039_strategy(seed,c,strategy,vals)
 if strategy==LOCAL_MIXTURE_STRATEGY:return run_experiment_040_strategy(seed,c,strategy,vals)
 if strategy==LOCAL_CAUCHY_STRATEGY:return run_experiment_041_strategy(seed,c,strategy,vals)
 if strategy==LOCAL_GAUSSIAN_GROSS_STRATEGY:return run_experiment_042_strategy(seed,c,strategy,vals)
 stream=generate_experiment_043_stream(seed,c)
 if strategy!=REPLICATED_GAUSSIAN_STRATEGY:
  with bind_experiment_043_stream(stream):rows=run_experiment_032_strategy(seed,c,strategy,vals)
 else:
  s=inject_symmetric_round5(stream);groups,accepted,abstain,stop,path=infer_replicated_gaussian(s);ann=_annotation(s,groups,accepted,abstain,stop,path);ann.update(_replication_annotation(path,accepted,stop));tau,kappa,k3,la,lb,lc,lab,lac,lbc,*_=vals
  if abstain:
   from experiment_010 import run_triad_persistence_on_stream
   rows=run_triad_persistence_on_stream(seed,f'experiment043_{c["label"]}',tau,k3,stream)
   for r in rows:r['strategy']=REPLICATED_GAUSSIAN_STRATEGY;r.update(ann)
  else:
   rows=_run_composed_gate(seed,f'experiment043_{c["label"]}',tau,k3,la,lb,lc,lab,lac,lbc,s,ann,groups)
   for r in rows:r['strategy']=REPLICATED_GAUSSIAN_STRATEGY
 for r in rows:
  r['experiment043_cell']=c['label'];r['experiment043_noise_family']=c['noise_family'];r['experiment043_confirmations_required']=CONFIRMATIONS_REQUIRED
 return rows

def evaluate_gaussian_posterior(seed,c):
 s=inject_symmetric_round5(generate_experiment_043_stream(seed,c));_,sigma_hat=diagnostic_noise_factor(s);out=[]
 for stage in range(1,6):
  y=directed_stage(s,stage);var,cov=covariance_terms(sigma_hat,stage);post,logs,quad=posterior_from_directed(y,var,cov);top=max(HYPOTHESES,key=lambda h:post[h])
  out.append({'seed':seed,'label':c['label'],'noise_family':c['noise_family'],'gain':c['gain'],'noise_scale':c['noise_scale'],'stage':stage,'top_hypothesis':top,'top_probability':post[top],'correct':int(top=='H_ab'),**{f'P_{h}':post[h] for h in HYPOTHESES}})
 return out
