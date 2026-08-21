from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from math import log, sqrt
from random import Random
import importlib

from adaptive_model_gating import N_STEPS
from experiment_016 import SIGMA_PROBE
from experiment_022 import generate_stress_stream
from experiment_023 import diagnostic_noise_factor
from experiment_027 import inject_symmetric_round5, HYPOTHESES
from experiment_028 import directed_stage, covariance_terms, posterior_from_directed
from experiment_029 import POSTERIOR_RISK_STRATEGY, TRIAD
from experiment_032 import COMPOSED_STRATEGY, run_experiment_032_strategy

STRATEGIES=(COMPOSED_STRATEGY,POSTERIOR_RISK_STRATEGY,TRIAD)
NOISE_FAMILIES=('laplace','student_t3','contaminated_gaussian')


def cell(label,noise_family,gain,noise_scale):
    return {'label':label,'kind':'likelihood_transfer','family':'drift_ab_fault','magnitude':0.50,
            'noise_family':noise_family,'gain':float(gain),'noise_scale':float(noise_scale),'topology_truth':'H_ab'}


def frozen_cells():
    out=[]
    for nf in NOISE_FAMILIES:
        for g in (0.50,0.425):
            for s in (1.00,1.50):
                out.append(cell(f'{nf}_g{g:.3f}_n{s:.2f}',nf,g,s))
    if len(out)!=12: raise AssertionError(len(out))
    return tuple(out)

CELLS=frozen_cells()


def _unit_noise(rng,family):
    if family=='laplace':
        # Laplace(0,b), Var=2b^2=1.
        u=max(min(rng.random(),1.0-1e-15),1e-15)-0.5
        return -((1.0/sqrt(2.0)))*(1.0 if u<0 else -1.0)*log(1.0-2.0*abs(u))
    if family=='student_t3':
        z=rng.gauss(0.0,1.0);chi=sum(rng.gauss(0.0,1.0)**2 for _ in range(3))
        return (z/sqrt(chi/3.0))/sqrt(3.0)
    if family=='contaminated_gaussian':
        z=rng.gauss(0.0,5.0 if rng.random()<0.05 else 1.0)
        return z/sqrt(2.2)
    raise ValueError(family)


def generate_experiment_035_stream(seed,c):
    base_cell={'label':c['label'],'kind':'gain','family':'drift_ab_fault','magnitude':0.50,'gain':float(c['gain'])}
    s=generate_stress_stream(seed,base_cell)
    rng=Random(int(seed)+35035000+NOISE_FAMILIES.index(c['noise_family'])*1000000)
    scale=float(c['noise_scale'])
    for t in range(1,N_STEPS+1):
        for x in 'abc':
            old=float(s[f'probe_noise_{x}'][t]);signal=float(s[f'probe_obs_{x}'][t])-SIGMA_PROBE*old
            u=_unit_noise(rng,c['noise_family'])
            s[f'probe_noise_{x}'][t]=scale*u
            s[f'probe_obs_{x}'][t]=signal+SIGMA_PROBE*scale*u
    s['probe_noise_family']=c['noise_family'];s['probe_noise_scale']=scale
    return s


@contextmanager
def bind_experiment_035_stream(stream):
    targets=(('experiment_022','generate_stress_stream'),('experiment_029','generate_stress_stream'),('experiment_032','generate_stress_stream'))
    old=[]
    def fixed(*args,**kwargs): return deepcopy(stream)
    try:
        for modname,name in targets:
            mod=importlib.import_module(modname);old.append((mod,name,getattr(mod,name)));setattr(mod,name,fixed)
        yield
    finally:
        for mod,name,value in reversed(old):setattr(mod,name,value)


def run_experiment_035_strategy(seed,c,strategy,vals):
    if strategy not in STRATEGIES: raise ValueError(strategy)
    stream=generate_experiment_035_stream(seed,c)
    with bind_experiment_035_stream(stream):
        rows=run_experiment_032_strategy(seed,c,strategy,vals)
    for r in rows:
        r['experiment035_cell']=c['label'];r['experiment035_noise_family']=c['noise_family'];r['experiment035_noise_scale']=c['noise_scale'];r['experiment035_topology_truth']='H_ab'
    return rows


def evaluate_experiment_035_posterior(seed,c):
    stream=inject_symmetric_round5(generate_experiment_035_stream(seed,c));_,sigma_hat=diagnostic_noise_factor(stream);rows=[]
    for stage in range(1,6):
        y=directed_stage(stream,stage);var,cov=covariance_terms(sigma_hat,stage);post,logs,quad=posterior_from_directed(y,var,cov);top=max(HYPOTHESES,key=lambda h:post[h])
        rows.append({'seed':int(seed),'label':c['label'],'noise_family':c['noise_family'],'gain':float(c['gain']),'noise_scale':float(c['noise_scale']),
                     'stage':stage,'topology_truth':'H_ab','top_hypothesis':top,'top_probability':float(post[top]),'correct':int(top=='H_ab'),
                     'sigma_hat':float(sigma_hat),'entropy':-sum(p*log(max(p,1e-300)) for p in post.values()),'mahalanobis_zero':float(quad),
                     **{f'P_{h}':float(post[h]) for h in HYPOTHESES}})
    return rows
