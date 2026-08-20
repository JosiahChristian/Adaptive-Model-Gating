from __future__ import annotations
from math import sqrt
from experiment_016 import SIGMA_PROBE
from experiment_021 import QUALIFICATION_AWARE_STRATEGY, run_experiment_021_strategy
from experiment_022 import bind_stressed_stream, generate_stress_stream, run_experiment_022_strategy

NOISE_AWARE_STRATEGY='noise_aware_qualification_aware_early_targeted_replicated_selective_cumulative_provenance_quorum'
BASELINES=range(181,201)


def diagnostic_noise_factor(stream):
    vals=[]
    for x in 'abc':
        obs=[float(stream[f'probe_obs_{x}'][t]) for t in BASELINES]
        m=sum(obs)/len(obs)
        vals.extend(v-m for v in obs)
    s_hat=sqrt(sum(v*v for v in vals)/57.0)
    return max(1.0,s_hat/SIGMA_PROBE),s_hat


def scale_thresholds(vals,factor):
    v=list(vals)
    # vals = tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5,mu5t,nu5t,mu4e,nu4e
    v[10]=tuple(float(x)*factor for x in v[10])
    v[11]=tuple(float(x)*factor for x in v[11])
    for i in (12,13,14,15,16,17):v[i]=float(v[i])*factor
    return tuple(v)


def run_experiment_023_strategy(seed,c,strategy,vals):
    if strategy!=NOISE_AWARE_STRATEGY:
        return run_experiment_022_strategy(seed,c,strategy,vals)
    stream=generate_stress_stream(seed,c)
    factor,s_hat=diagnostic_noise_factor(stream)
    scaled=scale_thresholds(vals,factor)
    with bind_stressed_stream(stream):
        rows=run_experiment_021_strategy(seed,c['family'],float(c['magnitude']),QUALIFICATION_AWARE_STRATEGY,*scaled)
    for r in rows:
        r['strategy']=NOISE_AWARE_STRATEGY
        r['experiment023_cell']=c['label'];r['experiment023_kind']=c['kind']
        r['diagnostic_noise_factor']=factor;r['diagnostic_noise_sd_hat']=s_hat
        r['experiment023_gain']=c.get('gain',stream.get('probe_gain',''))
        r['experiment023_noise_scale']=c.get('noise_scale',1.0)
    return rows
