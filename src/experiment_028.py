from __future__ import annotations

from math import erf, exp, isfinite, log, sqrt

from experiment_016 import ROUND_AMPLITUDES
from experiment_017 import cumulative_statistics
from experiment_018 import ALL_AMPLITUDES, cumulative5_statistics
from experiment_023 import diagnostic_noise_factor
from experiment_027 import (
    BETA_SCALE, HYPOTHESES, evaluate_posterior_path as evaluate_q_posterior_path,
    inject_symmetric_round5,
)
from experiment_022 import generate_stress_stream

VECTOR=(('a','b'),('a','c'),('b','a'),('b','c'),('c','a'),('c','b'))
TOPOLOGY_DIRECTIONS={
    'H_ab':(1.0,0.0,1.0,0.0,0.0,0.0),
    'H_ac':(0.0,1.0,0.0,0.0,1.0,0.0),
    'H_bc':(0.0,0.0,0.0,1.0,0.0,1.0),
}
BLOCKS=((0,1),(2,3),(4,5))


def directed_stage(stream,stage):
    if stage in (1,2,3,4):C,_=cumulative_statistics(stream,stage)
    elif stage==5:C,_=cumulative5_statistics(stream)
    else:raise ValueError(stage)
    return tuple(float(C[p]) for p in VECTOR)


def covariance_terms(sigma_hat,stage):
    amps=ROUND_AMPLITUDES[:stage] if stage<=4 else ALL_AMPLITUDES
    s1=sum(float(a) for a in amps);s2=sum(float(a)*float(a) for a in amps)
    shared=(float(sigma_hat)**2)*(s1*s1)/(20.0*s2)
    var=(float(sigma_hat)**2)*(1.0/5.0)+(shared)
    var=max(var,1e-18)
    # Numerical guard only; analytic construction always has var > shared >= 0.
    shared=min(max(shared,0.0),var*(1.0-1e-12))
    return var,shared


def _apply_precision(x,var,cov):
    det=var*var-cov*cov
    if det<=0.0:raise FloatingPointError((var,cov,det))
    out=[0.0]*6
    for i,j in BLOCKS:
        out[i]=(var*x[i]-cov*x[j])/det
        out[j]=(var*x[j]-cov*x[i])/det
    return tuple(out)


def _dot(a,b):return sum(float(x)*float(y) for x,y in zip(a,b))


def _normal_cdf(x):return 0.5*(1.0+erf(float(x)/sqrt(2.0)))


def posterior_from_directed(y,var,cov):
    py=_apply_precision(y,var,cov);d=_dot(y,py);logs={'H_null':log(0.25)}
    for h,u in TOPOLOGY_DIRECTIONS.items():
        pu=_apply_precision(u,var,cov)
        a=_dot(u,pu)+(1.0/(BETA_SCALE*BETA_SCALE))
        b=_dot(u,py)
        z=b/sqrt(a)
        cdf=max(_normal_cdf(z),1e-300)
        # Exact half-normal nuisance-amplitude marginal likelihood ratio vs H_null.
        log_bf=log(2.0)-log(BETA_SCALE)-0.5*log(a)+(b*b)/(2.0*a)+log(cdf)
        logs[h]=log(0.25)+log_bf
    m=max(logs.values());w={h:exp(logs[h]-m) for h in HYPOTHESES};den=sum(w.values())
    post={h:w[h]/den for h in HYPOTHESES}
    if not all(isfinite(p) and p>=0.0 for p in post.values()):raise FloatingPointError(post)
    if abs(sum(post.values())-1.0)>1e-10:raise FloatingPointError(sum(post.values()))
    return post,logs,d


def evaluate_directed_posterior_path(seed,cell):
    stream=inject_symmetric_round5(generate_stress_stream(seed,cell));_,sigma_hat=diagnostic_noise_factor(stream);rows=[]
    for stage in range(1,6):
        y=directed_stage(stream,stage);var,cov=covariance_terms(sigma_hat,stage);post,logs,quad=posterior_from_directed(y,var,cov)
        top=max(HYPOTHESES,key=lambda h:post[h])
        r={'seed':int(seed),'label':cell['label'],'kind':cell['kind'],'family':cell['family'],'magnitude':float(cell['magnitude']),
           'gain':float(cell.get('gain',stream.get('probe_gain',1.0))),'noise_scale':float(cell.get('noise_scale',1.0)),
           'stage':stage,'model':'directed_covariance','sigma_hat':float(sigma_hat),'covariance_variance':float(var),'covariance_shared_baseline':float(cov),
           'beta_scale':BETA_SCALE,'top_hypothesis':top,'top_probability':float(post[top]),'posterior_entropy':-sum(p*log(max(p,1e-300)) for p in post.values()),'mahalanobis_zero':float(quad)}
        for p,val in zip(VECTOR,y):r['C_'+''.join(p)]=float(val)
        for h in HYPOTHESES:r['P_'+h]=float(post[h]);r['logml_'+h]=float(logs[h])
        rows.append(r)
    return rows


def evaluate_both_paths(seed,cell):
    new=evaluate_directed_posterior_path(seed,cell)
    old=evaluate_q_posterior_path(seed,cell)
    for r in old:r['model']='q_diagonal_experiment027'
    return new+old
