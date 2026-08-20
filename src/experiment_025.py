from __future__ import annotations
from copy import deepcopy
from math import sqrt
from statistics import mean

from experiment_016 import round_response_matrix
from experiment_018 import _fallback as fallback018, _run_group_gate as run_group_gate018
from experiment_019 import PAIRS
from experiment_020 import response_matrix_for_blocks, targeted_score_custom
from experiment_021 import QUALIFICATION_AWARE_STRATEGY
from experiment_022 import bind_stressed_stream, generate_stress_stream, run_experiment_022_strategy
from experiment_023 import diagnostic_noise_factor
from experiment_024 import MARGIN_STRATEGY, Z_MARGIN, infer_margin_policy, margin_stats

CONDITIONAL_CONFIRMATION_STRATEGY='conditional_high_noise_replicated_confirmation_qualification_aware_provenance_quorum'
NOISE_TRIGGER=1.25
ROUND6_AMPLITUDE=0.200
ROUND6_BLOCKS=(range(276,281),range(281,286))
ALL6_AMPLITUDES=(0.025,0.050,0.100,0.200,0.200,0.200)


def _physical_groups():return {'a':'G1','b':'G1','c':'G2'}


def inject_round6(stream,pair):
    s=deepcopy(stream);groups=_physical_groups();gain=float(s['probe_gain'])
    for target,ts in zip(pair,ROUND6_BLOCKS):
        for t in ts:
            for x in 'abc':
                if groups[x]==groups[target]:s[f'probe_obs_{x}'][t]+=gain*ROUND6_AMPLITUDE
    return s


def _blocks_from_trace(trace):
    p=trace.get('pair3')
    if p is None:return {'a':range(246,251),'b':range(251,256),'c':range(256,261)}
    missing=next(x for x in 'abc' if x not in p)
    return {p[0]:range(246,251),p[1]:range(251,256),missing:range(256,261)}


def round6_candidate_score(stream,pair,trace):
    blocks=_blocks_from_trace(trace);R4=response_matrix_for_blocks(stream,blocks)
    _,_,_,R5=targeted_score_custom(stream,pair,R4)
    baseline={x:mean(stream[f'probe_obs_{x}'][t] for t in range(181,201)) for x in 'abc'}
    R6={}
    for obs in 'abc':
        for target,ts in zip(pair,ROUND6_BLOCKS):R6[(obs,target)]=mean(stream[f'probe_obs_{obs}'][t] for t in ts)-baseline[obs]
    Rs={r:round_response_matrix(stream,r) for r in range(1,4)};Rs[4]=R4
    denom=sqrt(sum(a*a for a in ALL6_AMPLITUDES));i,j=pair
    def c(obs,target):
        total=sum(ALL6_AMPLITUDES[k-1]*Rs[k][(obs,target)] for k in range(1,5))
        total+=ROUND6_AMPLITUDE*R5[(obs,target)]+ROUND6_AMPLITUDE*R6[(obs,target)]
        return total/denom
    cij,cji=c(i,j),c(j,i)
    return min(cij,cji),cij,cji,R6,R4


def infer_conditional_confirmation(stream,vals,sigma_hat):
    tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5,mu5t,nu5t,mu4e,nu4e=vals
    groups,accepted,abstain,stop,used,trace=infer_margin_policy(stream,mu,mu5t,mu4e,sigma_hat)
    data={'margin_trace':trace,'round6_executed':0,'round6_pair':None,'round6_score':None,'round6_z':None,'round6_margin':None,'round6_second':None,'round6_qualified':0}
    if accepted:return groups,1,0,stop,used,data
    pair=trace.get('pair5')
    if pair is None:return None,0,1,0,used,data
    s6=inject_round6(used,pair);score,_,_,_,_=round6_candidate_score(s6,pair,trace)
    q4=trace.get('Q4') or {};competitors=[float(q4[p]) for p in PAIRS if p!=pair]
    if len(competitors)!=2:return None,0,1,0,s6,data
    second=max(competitors);q6=dict(q4);q6[pair]=float(score)
    margin,se,z,_=margin_stats(q6,pair,sigma_hat)
    qualified=int(float(score)>float(mu5t) and z>=Z_MARGIN)
    data.update({'round6_executed':1,'round6_pair':pair,'round6_score':float(score),'round6_z':float(z),'round6_margin':float(margin),'round6_second':float(second),'round6_qualified':qualified})
    if qualified:
        from experiment_016 import groups_from_edges
        return groups_from_edges([pair]),1,0,6,s6,data
    return None,0,1,0,s6,data


def _high_noise_annotation(stream,accepted,abstain,stop,groups,data,sigma_hat,factor):
    trace=data['margin_trace']
    # inherited 024 energy plus exactly two new 0.2x5 blocks if round 6 executes
    if trace['pair3'] is None:energy=0.796875;blocks=12
    else:energy=0.196875+0.4+(0.2 if trace['missing'] else 0.0);blocks=11+(1 if trace['missing'] else 0)
    if trace['round5']:energy+=0.4;blocks+=2
    if data['round6_executed']:energy+=0.4;blocks+=2
    out={'probe_gain':stream['probe_gain'],'probe_stop_round':stop,'probe_energy':energy,'probe_block_count':blocks,'probe_max_amplitude':0.2,
         'provenance_accepted':accepted,'provenance_abstain':abstain,'accepted_partition_correct':'' if not accepted else __import__('experiment_016').partition_matches(groups),
         'diagnostic_noise_sd_hat':sigma_hat,'diagnostic_noise_factor':factor,'conditional_high_noise_branch':1,
         'round6_executed':data['round6_executed'],'round6_selected_edge':''.join(data['round6_pair']) if data['round6_pair'] else '',
         'round6_score':data['round6_score'] if data['round6_score'] is not None else '',
         'round6_z_margin':data['round6_z'] if data['round6_z'] is not None else '',
         'round6_margin':data['round6_margin'] if data['round6_margin'] is not None else '',
         'round6_second_score':data['round6_second'] if data['round6_second'] is not None else '',
         'round6_qualified':data['round6_qualified'],'margin_z_cutoff':Z_MARGIN}
    return out


def run_experiment_025_strategy(seed,c,strategy,vals):
    if strategy!=CONDITIONAL_CONFIRMATION_STRATEGY:
        if strategy==MARGIN_STRATEGY:
            from experiment_024 import run_experiment_024_strategy
            return run_experiment_024_strategy(seed,c,strategy,vals)
        from experiment_023 import NOISE_AWARE_STRATEGY,run_experiment_023_strategy
        if strategy==NOISE_AWARE_STRATEGY:return run_experiment_023_strategy(seed,c,strategy,vals)
        return run_experiment_022_strategy(seed,c,strategy,vals)
    stream=generate_stress_stream(seed,c);factor,sigma_hat=diagnostic_noise_factor(stream)
    if factor<=NOISE_TRIGGER:
        rows=run_experiment_022_strategy(seed,c,QUALIFICATION_AWARE_STRATEGY,vals)
        for r in rows:
            r['strategy']=CONDITIONAL_CONFIRMATION_STRATEGY;r['conditional_high_noise_branch']=0;r['diagnostic_noise_factor']=factor;r['diagnostic_noise_sd_hat']=sigma_hat;r['round6_executed']=0;r['experiment025_cell']=c['label'];r['experiment025_kind']=c['kind']
        return rows
    groups,accepted,abstain,stop,used,data=infer_conditional_confirmation(stream,vals,sigma_hat)
    tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5,mu5t,nu5t,mu4e,nu4e=vals
    ann=_high_noise_annotation(used,accepted,abstain,stop,groups,data,sigma_hat,factor)
    if abstain:
        with bind_stressed_stream(used):rows=run_experiment_022_strategy(seed,c,'triad_persistence',vals)
        for r in rows:r['strategy']=CONDITIONAL_CONFIRMATION_STRATEGY;r.update(ann)
    else:
        rows=run_group_gate018(seed,f'experiment025_{c["label"]}',tau,k3,la,lb,lc,lab,lac,lbc,used,ann,groups)
        for r in rows:r['strategy']=CONDITIONAL_CONFIRMATION_STRATEGY
    for r in rows:r['experiment025_cell']=c['label'];r['experiment025_kind']=c['kind'];r['experiment025_gain']=c.get('gain',used.get('probe_gain',''));r['experiment025_noise_scale']=c.get('noise_scale',1.0)
    return rows
