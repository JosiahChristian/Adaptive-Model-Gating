from __future__ import annotations
from contextlib import contextmanager
from copy import deepcopy
from math import exp,isfinite,lgamma,log,pi,sqrt
import importlib
from experiment_016 import groups_from_edges
from experiment_023 import diagnostic_noise_factor
from experiment_027 import HYPOTHESES,inject_symmetric_round5
from experiment_028 import BETA_SCALE,TOPOLOGY_DIRECTIONS,directed_stage,covariance_terms
from experiment_029 import ACCEPT_THRESHOLD,WRONG_COST,FALLBACK_COST,TRIAD,_annotation
from experiment_032 import COMPOSED_STRATEGY,_run_composed_gate,run_experiment_032_strategy
from experiment_036 import ROBUST_STRATEGY,NU,BETA_MAX,BETA_STEP,BETA_GRID,generate_experiment_036_stream,run_experiment_036_strategy

MODEL_AVERAGED_STRATEGY='gaussian_student_t3_model_averaged_context_composed_risk_gate'
STRATEGIES=(MODEL_AVERAGED_STRATEGY,COMPOSED_STRATEGY,ROBUST_STRATEGY,TRIAD)
MODEL_PRIOR={'gaussian':0.5,'student_t3':0.5}
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

def generate_experiment_037_stream(seed,c):return generate_experiment_036_stream(seed,c)

@contextmanager
def bind_experiment_037_stream(stream):
 targets=(('experiment_022','generate_stress_stream'),('experiment_029','generate_stress_stream'),('experiment_032','generate_stress_stream'))
 old=[]
 def fixed(*args,**kwargs):return deepcopy(stream)
 try:
  for mn,n in targets:
   m=importlib.import_module(mn);old.append((m,n,getattr(m,n)));setattr(m,n,fixed)
  yield
 finally:
  for m,n,v in reversed(old):setattr(m,n,v)

def _quad(v,var,cov):
 det=var*var-cov*cov
 if det<=0:raise FloatingPointError((var,cov))
 q=0.0
 for i,j in ((0,1),(2,3),(4,5)):
  a,b=float(v[i]),float(v[j]);q+=(var*(a*a+b*b)-2.0*cov*a*b)/det
 return q

def _logdet(var,cov):
 d=var*var-cov*cov
 if d<=0:raise FloatingPointError((var,cov))
 return 3.0*log(d)

def _log_gaussian(v,var,cov):return -3.0*log(2.0*pi)-0.5*_logdet(var,cov)-0.5*_quad(v,var,cov)
def _log_student_t(v,var,cov):
 sv,sc=var/3.0,cov/3.0;d=6.0
 return lgamma((NU+d)/2.0)-lgamma(NU/2.0)-0.5*d*log(NU*pi)-0.5*_logdet(sv,sc)-0.5*(NU+d)*log(1.0+_quad(v,sv,sc)/NU)
def _log_halfnormal(beta):return log(sqrt(2.0/pi)/BETA_SCALE)-0.5*(beta/BETA_SCALE)**2
def _lse(xs):
 m=max(xs);return m+log(sum(exp(x-m) for x in xs))
def _family_logs(y,var,cov,family):
 ld=_log_gaussian if family=='gaussian' else _log_student_t
 out={'H_null':ld(y,var,cov)}
 for h,u in TOPOLOGY_DIRECTIONS.items():
  terms=[]
  for idx,beta in enumerate(BETA_GRID):
   r=tuple(float(y[k])-beta*float(u[k]) for k in range(6));w=.5 if idx in (0,len(BETA_GRID)-1) else 1.0
   terms.append(ld(r,var,cov)+_log_halfnormal(beta)+log(w*BETA_STEP))
  out[h]=_lse(terms)
 return out

def posterior_model_averaged(y,var,cov):
 fam={m:_family_logs(y,var,cov,m) for m in MODEL_PRIOR};joint={};toplog={}
 for h in HYPOTHESES:
  xs=[log(0.25)+log(MODEL_PRIOR[m])+fam[m][h] for m in MODEL_PRIOR];joint[h]=_lse(xs)
 m=max(joint.values());w={h:exp(joint[h]-m) for h in HYPOTHESES};z=sum(w.values());post={h:w[h]/z for h in HYPOTHESES}
 evid={model:_lse([log(0.25)+fam[model][h] for h in HYPOTHESES])+log(MODEL_PRIOR[model]) for model in MODEL_PRIOR};em=max(evid.values());ew={k:exp(v-em) for k,v in evid.items()};ez=sum(ew.values());mp={k:v/ez for k,v in ew.items()}
 if not all(isfinite(p) and 0<=p<=1 for p in post.values()) or abs(sum(post.values())-1)>1e-10:raise FloatingPointError(post)
 return post,mp

def infer_model_averaged(stream):
 _,sigma_hat=diagnostic_noise_factor(stream);path=[]
 for stage in range(1,6):
  y=directed_stage(stream,stage);var,cov=covariance_terms(sigma_hat,stage);post,mp=posterior_model_averaged(y,var,cov);cand=max(UNIQUE,key=lambda h:post[h]);p=float(post[cand])
  path.append({'stage':stage,'candidate':cand,'candidate_posterior':p,'posterior_error_risk':1-p,'expected_wrong_action_loss':WRONG_COST*(1-p),'posterior':post,'variance':var,'shared_covariance':cov,'mahalanobis_zero':0.0,'model_posterior':mp})
  if p>=ACCEPT_THRESHOLD:return groups_from_edges([EDGE[cand]]),1,0,stage,path
 return None,0,1,0,path

def run_experiment_037_strategy(seed,c,strategy,vals):
 if strategy not in STRATEGIES:raise ValueError(strategy)
 stream=generate_experiment_037_stream(seed,c)
 if strategy==ROBUST_STRATEGY:return run_experiment_036_strategy(seed,c,strategy,vals)
 if strategy!=MODEL_AVERAGED_STRATEGY:
  with bind_experiment_037_stream(stream):rows=run_experiment_032_strategy(seed,c,strategy,vals)
 else:
  s=inject_symmetric_round5(stream);groups,accepted,abstain,stop,path=infer_model_averaged(s);ann=_annotation(s,groups,accepted,abstain,stop,path);tau,kappa,k3,la,lb,lc,lab,lac,lbc,*_=vals
  if abstain:
   from experiment_010 import run_triad_persistence_on_stream
   rows=run_triad_persistence_on_stream(seed,f'experiment037_{c["label"]}',tau,k3,stream)
   for r in rows:r['strategy']=MODEL_AVERAGED_STRATEGY;r.update(ann)
  else:
   rows=_run_composed_gate(seed,f'experiment037_{c["label"]}',tau,k3,la,lb,lc,lab,lac,lbc,s,ann,groups)
   for r in rows:r['strategy']=MODEL_AVERAGED_STRATEGY
 for r in rows:
  r['experiment037_cell']=c['label'];r['experiment037_noise_family']=c['noise_family'];r['model_prior_gaussian']=.5;r['model_prior_student_t3']=.5
 return rows

def evaluate_model_averaged_posterior(seed,c):
 s=inject_symmetric_round5(generate_experiment_037_stream(seed,c));_,sigma_hat=diagnostic_noise_factor(s);out=[]
 for stage in range(1,6):
  y=directed_stage(s,stage);var,cov=covariance_terms(sigma_hat,stage);post,mp=posterior_model_averaged(y,var,cov);top=max(HYPOTHESES,key=lambda h:post[h])
  out.append({'seed':seed,'label':c['label'],'noise_family':c['noise_family'],'gain':c['gain'],'noise_scale':c['noise_scale'],'stage':stage,'top_hypothesis':top,'top_probability':post[top],'correct':int(top=='H_ab'),'P_model_gaussian':mp['gaussian'],'P_model_student_t3':mp['student_t3'],**{f'P_{h}':post[h] for h in HYPOTHESES}})
 return out
