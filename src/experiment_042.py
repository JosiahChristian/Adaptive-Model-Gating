from __future__ import annotations
from contextlib import contextmanager
from copy import deepcopy
from math import exp,isfinite,log,pi,sqrt
import importlib
from experiment_016 import groups_from_edges
from experiment_023 import diagnostic_noise_factor
from experiment_027 import HYPOTHESES,inject_symmetric_round5
from experiment_028 import BETA_SCALE,TOPOLOGY_DIRECTIONS,directed_stage,covariance_terms
from experiment_029 import ACCEPT_THRESHOLD,WRONG_COST,FALLBACK_COST,TRIAD,_annotation
from experiment_032 import COMPOSED_STRATEGY,_run_composed_gate,run_experiment_032_strategy
from experiment_036 import ROBUST_STRATEGY,BETA_GRID,BETA_STEP,BETA_MAX,generate_experiment_036_stream,run_experiment_036_strategy
from experiment_037 import MODEL_AVERAGED_STRATEGY,run_experiment_037_strategy
from experiment_038 import HUBER_STRATEGY,run_experiment_038_strategy
from experiment_039 import RADIAL_HUBER_STRATEGY,run_experiment_039_strategy
from experiment_040 import LOCAL_MIXTURE_STRATEGY,run_experiment_040_strategy
from experiment_041 import LOCAL_CAUCHY_STRATEGY,run_experiment_041_strategy

LOCAL_GAUSSIAN_GROSS_STRATEGY='variance_preserving_gaussian_gross_error_context_composed_risk_gate'
STRATEGIES=(LOCAL_GAUSSIAN_GROSS_STRATEGY,COMPOSED_STRATEGY,ROBUST_STRATEGY,MODEL_AVERAGED_STRATEGY,HUBER_STRATEGY,RADIAL_HUBER_STRATEGY,LOCAL_MIXTURE_STRATEGY,LOCAL_CAUCHY_STRATEGY,TRIAD)
CLEAN_WEIGHT=0.95
GROSS_WEIGHT=0.05
VARIANCE_RATIO=25.0
MIXTURE_VARIANCE=2.2
CLEAN_SCALE=1.0/MIXTURE_VARIANCE
GROSS_SCALE=VARIANCE_RATIO/MIXTURE_VARIANCE
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

def generate_experiment_042_stream(seed,c):return generate_experiment_036_stream(seed,c)

@contextmanager
def bind_experiment_042_stream(stream):
 targets=(('experiment_022','generate_stress_stream'),('experiment_029','generate_stress_stream'),('experiment_032','generate_stress_stream'))
 old=[]
 def fixed(*args,**kwargs):return deepcopy(stream)
 try:
  for mn,n in targets:
   m=importlib.import_module(mn);old.append((m,n,getattr(m,n)));setattr(m,n,fixed)
  yield
 finally:
  for m,n,v in reversed(old):setattr(m,n,v)

def _lse2(a,b):
 m=max(a,b);return m+log(exp(a-m)+exp(b-m))
def _log_halfnormal(beta):return log(sqrt(2.0/pi)/BETA_SCALE)-0.5*(beta/BETA_SCALE)**2
def _lse(xs):
 m=max(xs);return m+log(sum(exp(x-m) for x in xs))

def _block_mahalanobis(v,var,cov):
 det=var*var-cov*cov
 if var<=0 or det<=0:raise FloatingPointError((var,cov,det))
 out=[]
 for i,j in ((0,1),(2,3),(4,5)):
  a=float(v[i]);b=float(v[j]);q=(var*(a*a+b*b)-2.0*cov*a*b)/det
  out.append(max(0.0,q))
 return det,tuple(out)

def _log_scaled_gaussian_block(q,det,scale):
 if scale<=0:raise FloatingPointError(scale)
 return -log(2.0*pi)-0.5*log(det)-log(scale)-0.5*q/scale

def _log_local_gaussian_gross(v,var,cov):
 det,qs=_block_mahalanobis(v,var,cov);total=0.0
 for q in qs:
  lc=_log_scaled_gaussian_block(q,det,CLEAN_SCALE)
  lg=_log_scaled_gaussian_block(q,det,GROSS_SCALE)
  total+=_lse2(log(CLEAN_WEIGHT)+lc,log(GROSS_WEIGHT)+lg)
 return total

def posterior_local_gaussian_gross(y,var,cov):
 y=tuple(float(x) for x in y);logs={'H_null':log(0.25)+_log_local_gaussian_gross(y,var,cov)}
 for h,u in TOPOLOGY_DIRECTIONS.items():
  terms=[]
  for idx,beta in enumerate(BETA_GRID):
   r=tuple(y[k]-beta*float(u[k]) for k in range(6));w=.5 if idx in (0,len(BETA_GRID)-1) else 1.0
   terms.append(_log_local_gaussian_gross(r,var,cov)+_log_halfnormal(beta)+log(w*BETA_STEP))
  logs[h]=log(0.25)+_lse(terms)
 m=max(logs.values());w={h:exp(logs[h]-m) for h in HYPOTHESES};den=sum(w.values());post={h:w[h]/den for h in HYPOTHESES}
 if not all(isfinite(p) and 0<=p<=1 for p in post.values()) or abs(sum(post.values())-1)>1e-10:raise FloatingPointError(post)
 return post

def infer_local_gaussian_gross(stream):
 _,sigma_hat=diagnostic_noise_factor(stream);path=[]
 for stage in range(1,6):
  y=directed_stage(stream,stage);var,cov=covariance_terms(sigma_hat,stage);post=posterior_local_gaussian_gross(y,var,cov);cand=max(UNIQUE,key=lambda h:post[h]);p=float(post[cand])
  path.append({'stage':stage,'candidate':cand,'candidate_posterior':p,'posterior_error_risk':1-p,'expected_wrong_action_loss':WRONG_COST*(1-p),'posterior':post,'variance':var,'shared_covariance':cov,'mahalanobis_zero':0.0})
  if p>=ACCEPT_THRESHOLD:return groups_from_edges([EDGE[cand]]),1,0,stage,path
 return None,0,1,0,path

def run_experiment_042_strategy(seed,c,strategy,vals):
 if strategy not in STRATEGIES:raise ValueError(strategy)
 if strategy==ROBUST_STRATEGY:return run_experiment_036_strategy(seed,c,strategy,vals)
 if strategy==MODEL_AVERAGED_STRATEGY:return run_experiment_037_strategy(seed,c,strategy,vals)
 if strategy==HUBER_STRATEGY:return run_experiment_038_strategy(seed,c,strategy,vals)
 if strategy==RADIAL_HUBER_STRATEGY:return run_experiment_039_strategy(seed,c,strategy,vals)
 if strategy==LOCAL_MIXTURE_STRATEGY:return run_experiment_040_strategy(seed,c,strategy,vals)
 if strategy==LOCAL_CAUCHY_STRATEGY:return run_experiment_041_strategy(seed,c,strategy,vals)
 stream=generate_experiment_042_stream(seed,c)
 if strategy!=LOCAL_GAUSSIAN_GROSS_STRATEGY:
  with bind_experiment_042_stream(stream):rows=run_experiment_032_strategy(seed,c,strategy,vals)
 else:
  s=inject_symmetric_round5(stream);groups,accepted,abstain,stop,path=infer_local_gaussian_gross(s);ann=_annotation(s,groups,accepted,abstain,stop,path);tau,kappa,k3,la,lb,lc,lab,lac,lbc,*_=vals
  if abstain:
   from experiment_010 import run_triad_persistence_on_stream
   rows=run_triad_persistence_on_stream(seed,f'experiment042_{c["label"]}',tau,k3,stream)
   for r in rows:r['strategy']=LOCAL_GAUSSIAN_GROSS_STRATEGY;r.update(ann)
  else:
   rows=_run_composed_gate(seed,f'experiment042_{c["label"]}',tau,k3,la,lb,lc,lab,lac,lbc,s,ann,groups)
   for r in rows:r['strategy']=LOCAL_GAUSSIAN_GROSS_STRATEGY
 for r in rows:
  r['experiment042_cell']=c['label'];r['experiment042_noise_family']=c['noise_family'];r['gross_clean_weight']=CLEAN_WEIGHT;r['gross_error_weight']=GROSS_WEIGHT;r['gross_variance_ratio']=VARIANCE_RATIO;r['gross_mixture_variance']=MIXTURE_VARIANCE;r['gross_clean_scale']=CLEAN_SCALE;r['gross_component_scale']=GROSS_SCALE;r['robust_beta_step']=BETA_STEP;r['robust_beta_max']=BETA_MAX
 return rows

def evaluate_local_gaussian_gross_posterior(seed,c):
 s=inject_symmetric_round5(generate_experiment_042_stream(seed,c));_,sigma_hat=diagnostic_noise_factor(s);out=[]
 for stage in range(1,6):
  y=directed_stage(s,stage);var,cov=covariance_terms(sigma_hat,stage);post=posterior_local_gaussian_gross(y,var,cov);top=max(HYPOTHESES,key=lambda h:post[h])
  out.append({'seed':seed,'label':c['label'],'noise_family':c['noise_family'],'gain':c['gain'],'noise_scale':c['noise_scale'],'stage':stage,'top_hypothesis':top,'top_probability':post[top],'correct':int(top=='H_ab'),**{f'P_{h}':post[h] for h in HYPOTHESES}})
 return out
