from __future__ import annotations
from contextlib import contextmanager
from copy import deepcopy
from math import exp,isfinite,log,sqrt
import importlib
from experiment_016 import SIGMA_PROBE
from experiment_022 import generate_stress_stream
from experiment_023 import diagnostic_noise_factor
from experiment_027 import HYPOTHESES,inject_symmetric_round5
from experiment_028 import BETA_SCALE,TOPOLOGY_DIRECTIONS,directed_stage,covariance_terms
from experiment_029 import ACCEPT_THRESHOLD,WRONG_COST,FALLBACK_COST,TRIAD,_annotation
from experiment_032 import COMPOSED_STRATEGY,_run_composed_gate,run_experiment_032_strategy
from experiment_035 import NOISE_FAMILIES,generate_experiment_035_stream

ROBUST_STRATEGY='student_t3_directed_covariance_context_composed_risk_gate'
STRATEGIES=(ROBUST_STRATEGY,COMPOSED_STRATEGY,TRIAD)
NU=3.0
BETA_MAX=1.20
BETA_STEP=0.01
BETA_GRID=tuple(round(i*BETA_STEP,10) for i in range(int(BETA_MAX/BETA_STEP)+1))
UNIQUE=('H_ab','H_ac','H_bc')
EDGE={'H_ab':('a','b'),'H_ac':('a','c'),'H_bc':('b','c')}

def cell(label,nf,gain,scale):
    return {'label':label,'kind':'noise','family':'drift_ab_fault','magnitude':0.50,'noise_family':nf,'gain':float(gain),'noise_scale':float(scale),'topology_truth':'H_ab'}
def frozen_cells():
    out=[]
    for nf in ('gaussian',)+NOISE_FAMILIES:
        for g in (0.50,0.425):
            for s in (1.00,1.50):out.append(cell(f'{nf}_g{g:.3f}_n{s:.2f}',nf,g,s))
    if len(out)!=16:raise AssertionError(len(out))
    return tuple(out)
CELLS=frozen_cells()

def _gaussian_probe_only(seed,c):
    base={'label':c['label'],'kind':'gain','family':'drift_ab_fault','magnitude':0.50,'gain':float(c['gain'])}
    s=generate_stress_stream(seed,base);scale=float(c['noise_scale'])
    for t in range(1,len(s['probe_obs_a'])):
        for x in 'abc':
            old=float(s[f'probe_noise_{x}'][t]);signal=float(s[f'probe_obs_{x}'][t])-SIGMA_PROBE*old
            s[f'probe_noise_{x}'][t]=scale*old;s[f'probe_obs_{x}'][t]=signal+SIGMA_PROBE*scale*old
    s['probe_noise_family']='gaussian';s['probe_noise_scale']=scale
    return s

def generate_experiment_036_stream(seed,c):
    if c['noise_family']=='gaussian':return _gaussian_probe_only(seed,c)
    return generate_experiment_035_stream(seed,c)

@contextmanager
def bind_experiment_036_stream(stream):
    targets=(('experiment_022','generate_stress_stream'),('experiment_029','generate_stress_stream'),('experiment_032','generate_stress_stream'))
    old=[]
    def fixed(*args,**kwargs):return deepcopy(stream)
    try:
        for mn,n in targets:
            m=importlib.import_module(mn);old.append((m,n,getattr(m,n)));setattr(m,n,fixed)
        yield
    finally:
        for m,n,v in reversed(old):setattr(m,n,v)

def _precision_quad(v,var,cov):
    sv=var/3.0;sc=cov/3.0;det=sv*sv-sc*sc
    if det<=0:raise FloatingPointError((sv,sc))
    q=0.0
    for i,j in ((0,1),(2,3),(4,5)):
        a,b=float(v[i]),float(v[j]);q+=(sv*(a*a+b*b)-2.0*sc*a*b)/det
    return q

def _log_t_kernel(v,var,cov):return -0.5*(NU+6.0)*log(1.0+_precision_quad(v,var,cov)/NU)
def _log_halfnormal(beta):return log(sqrt(2.0/3.141592653589793)/BETA_SCALE)-0.5*(beta/BETA_SCALE)**2
def _logsumexp(xs):
    m=max(xs);return m+log(sum(exp(x-m) for x in xs))
def posterior_from_student_t(y,var,cov):
    y=tuple(float(x) for x in y);logs={'H_null':log(0.25)+_log_t_kernel(y,var,cov)}
    for h,u in TOPOLOGY_DIRECTIONS.items():
        terms=[]
        for idx,beta in enumerate(BETA_GRID):
            r=tuple(y[k]-beta*float(u[k]) for k in range(6));w=0.5 if idx in (0,len(BETA_GRID)-1) else 1.0
            terms.append(_log_t_kernel(r,var,cov)+_log_halfnormal(beta)+log(w*BETA_STEP))
        logs[h]=log(0.25)+_logsumexp(terms)
    m=max(logs.values());w={h:exp(logs[h]-m) for h in HYPOTHESES};z=sum(w.values());post={h:w[h]/z for h in HYPOTHESES}
    if not all(isfinite(p) and 0<=p<=1 for p in post.values()) or abs(sum(post.values())-1)>1e-10:raise FloatingPointError(post)
    return post

def infer_robust(stream):
    _,sigma_hat=diagnostic_noise_factor(stream);path=[]
    for stage in range(1,6):
        y=directed_stage(stream,stage);var,cov=covariance_terms(sigma_hat,stage);post=posterior_from_student_t(y,var,cov);candidate=max(UNIQUE,key=lambda h:post[h]);p=float(post[candidate])
        path.append({'stage':stage,'candidate':candidate,'candidate_posterior':p,'posterior_error_risk':1-p,'expected_wrong_action_loss':WRONG_COST*(1-p),'posterior':post,'variance':var,'shared_covariance':cov,'mahalanobis_zero':0.0})
        if p>=ACCEPT_THRESHOLD:
            from experiment_016 import groups_from_edges
            return groups_from_edges([EDGE[candidate]]),1,0,stage,path
    return None,0,1,0,path

def run_experiment_036_strategy(seed,c,strategy,vals):
    if strategy not in STRATEGIES:raise ValueError(strategy)
    stream=generate_experiment_036_stream(seed,c)
    if strategy!=ROBUST_STRATEGY:
        with bind_experiment_036_stream(stream):rows=run_experiment_032_strategy(seed,c,strategy,vals)
    else:
        s=inject_symmetric_round5(stream);groups,accepted,abstain,stop,path=infer_robust(s);ann=_annotation(s,groups,accepted,abstain,stop,path);tau,kappa,k3,la,lb,lc,lab,lac,lbc,*_=vals
        if abstain:
            with bind_experiment_036_stream(stream):rows=run_experiment_032_strategy(seed,c,TRIAD,vals)
            for r in rows:r['strategy']=ROBUST_STRATEGY;r.update(ann)
        else:
            rows=_run_composed_gate(seed,f'experiment036_{c["label"]}',tau,k3,la,lb,lc,lab,lac,lbc,s,ann,groups)
            for r in rows:r['strategy']=ROBUST_STRATEGY
    for r in rows:
        r['experiment036_cell']=c['label'];r['experiment036_noise_family']=c['noise_family'];r['robust_df']=NU;r['robust_beta_step']=BETA_STEP;r['robust_beta_max']=BETA_MAX
    return rows

def evaluate_robust_posterior(seed,c):
    s=inject_symmetric_round5(generate_experiment_036_stream(seed,c));_,sigma_hat=diagnostic_noise_factor(s);out=[]
    for stage in range(1,6):
        y=directed_stage(s,stage);var,cov=covariance_terms(sigma_hat,stage);post=posterior_from_student_t(y,var,cov);top=max(HYPOTHESES,key=lambda h:post[h])
        out.append({'seed':seed,'label':c['label'],'noise_family':c['noise_family'],'gain':c['gain'],'noise_scale':c['noise_scale'],'stage':stage,'top_hypothesis':top,'top_probability':post[top],'correct':int(top=='H_ab'),**{f'P_{h}':post[h] for h in HYPOTHESES}})
    return out
