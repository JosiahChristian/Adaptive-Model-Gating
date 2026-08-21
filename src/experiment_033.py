from __future__ import annotations

from experiment_016 import partition_matches
from experiment_018 import _run_group_gate as run_group_gate018
from experiment_021 import run_experiment_021_strategy
from experiment_022 import (
    _apply_noise_scale,_asym_stream,_base,_mixed_stream,_timing_stream,bind_stressed_stream,
)
from experiment_027 import inject_symmetric_round5
from experiment_029 import POSTERIOR_RISK_STRATEGY,TRIAD,_annotation,infer_posterior_risk
from experiment_032 import COMPOSED_STRATEGY,_run_composed_gate

STRATEGIES=(COMPOSED_STRATEGY,POSTERIOR_RISK_STRATEGY,TRIAD)


def generate_experiment_033_stream(seed,c):
    kind=c['kind'];m=float(c['magnitude'])
    if kind=='gain_noise':
        return _apply_noise_scale(_base(seed,'drift_ab_fault',m,c['gain']),m,c['noise_scale'])
    if kind=='timing_noise':
        return _apply_noise_scale(_timing_stream(seed,m,0.50,c['timing_offset']),m,c['noise_scale'])
    if kind=='asym_noise':
        return _apply_noise_scale(_asym_stream(seed,m,0.50,c['scale_a'],c['scale_b']),m,c['noise_scale'])
    if kind=='mixed_noise':
        return _apply_noise_scale(_mixed_stream(seed,m,1.0,c['common_magnitude']),m,c['noise_scale'])
    if kind=='common_mode':
        return _base(seed,'common_mode',m,None)
    raise ValueError(kind)


def _triad_rows(seed,c,vals,stream):
    with bind_stressed_stream(stream):
        rows=run_experiment_021_strategy(seed,c['family'],float(c['magnitude']),TRIAD,*vals)
    return rows


def run_experiment_033_strategy(seed,c,strategy,vals):
    if strategy not in STRATEGIES:raise ValueError(strategy)
    stream=inject_symmetric_round5(generate_experiment_033_stream(seed,c))
    if strategy==TRIAD:
        rows=_triad_rows(seed,c,vals,stream)
    else:
        groups,accepted,abstain,stop,path=infer_posterior_risk(stream)
        ann=_annotation(stream,groups,accepted,abstain,stop,path)
        tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5,mu5t,nu5t,mu4e,nu4e=vals
        if abstain:
            rows=_triad_rows(seed,c,vals,stream)
            for r in rows:
                r['strategy']=strategy;r.update(ann)
                if strategy==COMPOSED_STRATEGY:
                    r['context_vote_t']=0;r['context_removed_suspect_veto']=0;r['triad_primary_bad']=int(r.get('primary_bad',0) or 0)
        elif strategy==POSTERIOR_RISK_STRATEGY:
            rows=run_group_gate018(seed,f'experiment033_{c["label"]}_029',tau,k3,la,lb,lc,lab,lac,lbc,stream,ann,groups)
            for r in rows:r['strategy']=POSTERIOR_RISK_STRATEGY
        else:
            rows=_run_composed_gate(seed,f'experiment033_{c["label"]}',tau,k3,la,lb,lc,lab,lac,lbc,stream,ann,groups)
    for r in rows:
        r['experiment033_cell']=c['label'];r['experiment033_kind']=c['kind']
        r['experiment033_gain']=c.get('gain',stream.get('probe_gain',''))
        r['experiment033_noise_scale']=c.get('noise_scale',1.0)
        r['experiment033_timing_offset']=c.get('timing_offset',0)
        r['experiment033_scale_a']=c.get('scale_a',1.0);r['experiment033_scale_b']=c.get('scale_b',1.0)
        r['experiment033_common_magnitude']=c.get('common_magnitude',0.0)
        r['experiment033_topology_correct']=partition_matches(groups) if strategy!=TRIAD and accepted else '' if strategy!=TRIAD else ''
    return rows
