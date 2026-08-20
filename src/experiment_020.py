from __future__ import annotations
from copy import deepcopy
from math import sqrt
from statistics import mean

from adaptive_model_gating import empirical_quantile
from experiment_016 import ROUND_AMPLITUDES, groups_from_edges, partition_matches, round_response_matrix
from experiment_017 import generate_experiment_017_stream, infer_cumulative_round
from experiment_018 import _fallback as fallback018, _run_group_gate as run_group_gate018
from experiment_019 import PAIRS, TARGETED_AMPLITUDE, TARGETED_BLOCKS, run_experiment_019_strategy

EARLY_CALIBRATION_SEEDS=range(5000,6000)
EARLY_AMPLITUDE=0.200
EARLY_BLOCKS=(range(246,251),range(251,256))
MISSING_BLOCK=range(256,261)
EARLY_STRATEGY='early_targeted_replicated_selective_cumulative_provenance_quorum'

def leading_edge(q):
    vals=[(float(q[p]),p) for p in PAIRS]
    m=max(v for v,_ in vals);w=[p for v,p in vals if v==m]
    return w[0] if len(w)==1 else None

def _physical_groups():return {'a':'G1','b':'G1','c':'G2'}

def _blank_round4(stream):
    s=deepcopy(stream);gain=s['probe_gain'];groups=_physical_groups();original={'a':range(246,251),'b':range(251,256),'c':range(256,261)}
    for target,ts in original.items():
        for t in ts:
            for x in 'abc':
                if groups[x]==groups[target]:s[f'probe_obs_{x}'][t]-=gain*EARLY_AMPLITUDE
    return s

def _inject_target_block(stream,target,ts):
    gain=stream['probe_gain'];groups=_physical_groups()
    for t in ts:
        for x in 'abc':
            if groups[x]==groups[target]:stream[f'probe_obs_{x}'][t]+=gain*EARLY_AMPLITUDE

def prepare_early_round4(stream,pair):
    s=_blank_round4(stream)
    if pair is None:
        blocks={'a':range(246,251),'b':range(251,256),'c':range(256,261)}
        for target,ts in blocks.items():_inject_target_block(s,target,ts)
        return s,blocks,None
    blocks={pair[0]:EARLY_BLOCKS[0],pair[1]:EARLY_BLOCKS[1]}
    for target,ts in blocks.items():_inject_target_block(s,target,ts)
    missing=next(x for x in 'abc' if x not in pair)
    return s,blocks,missing

def complete_round4(stream,target_blocks,missing):
    s=deepcopy(stream);blocks=dict(target_blocks)
    if missing is not None:_inject_target_block(s,missing,MISSING_BLOCK);blocks[missing]=MISSING_BLOCK
    return s,blocks

def response_matrix_for_blocks(stream,blocks):
    baseline={x:mean(stream[f'probe_obs_{x}'][t] for t in range(181,201)) for x in 'abc'};R={}
    for obs in 'abc':
        for target in 'abc':R[(obs,target)]=mean(stream[f'probe_obs_{obs}'][t] for t in blocks[target])-baseline[obs]
    return R

def cumulative_with_custom_r4(stream,R4):
    Rs={r:round_response_matrix(stream,r) for r in range(1,4)};Rs[4]=R4;denom=sqrt(sum(d*d for d in ROUND_AMPLITUDES));C={}
    for i in 'abc':
        for j in 'abc':
            if i!=j:C[(i,j)]=sum(ROUND_AMPLITUDES[k-1]*Rs[k][(i,j)] for k in range(1,5))/denom
    Q={(i,j):min(C[(i,j)],C[(j,i)]) for i,j in PAIRS};return C,Q,Rs

def graph_from_q(Q,mu4,nu4):
    edges=[p for p in PAIRS if Q[p]>mu4];groups=groups_from_edges(edges);sizes=sorted(sum(1 for x in 'abc' if groups[x]==g) for g in set(groups.values()));structural=int(len(edges)==1 and sizes==[1,2]);qualified=int(structural and Q[edges[0]]>nu4);return groups,edges,structural,qualified

def early_selected_score(stream,pair,target_blocks):
    baseline={x:mean(stream[f'probe_obs_{x}'][t] for t in range(181,201)) for x in 'abc'};Rs={r:round_response_matrix(stream,r) for r in range(1,4)};denom=sqrt(sum(d*d for d in ROUND_AMPLITUDES));i,j=pair
    def r4(obs,target):return mean(stream[f'probe_obs_{obs}'][t] for t in target_blocks[target])-baseline[obs]
    def c(obs,target):return (sum(ROUND_AMPLITUDES[k-1]*Rs[k][(obs,target)] for k in range(1,4))+EARLY_AMPLITUDE*r4(obs,target))/denom
    cij,cji=c(i,j),c(j,i);return min(cij,cji),cij,cji

def round3_q(stream,mu,nu):return infer_cumulative_round(stream,mu,nu,3)[2]

def calibrate_early_thresholds(mu,nu):
    vals=[]
    for seed in EARLY_CALIBRATION_SEEDS:
        base=generate_experiment_017_stream(seed,'healthy',0.0,gain_override=0.0);pair=leading_edge(round3_q(base,mu,nu))
        if pair is None:continue
        s,blocks,_=prepare_early_round4(base,pair);vals.append(early_selected_score(s,pair,blocks)[0])
    if not vals:raise RuntimeError('no early-target null calibration values')
    return empirical_quantile(vals,0.99),empirical_quantile(vals,0.999)

def inject_targeted_round5_custom(stream,pair):
    s=deepcopy(stream)
    if pair is not None:
        for target,ts in zip(pair,TARGETED_BLOCKS):_inject_target_block(s,target,ts)
    return s

def targeted_score_custom(stream,pair,R4):
    Rs={r:round_response_matrix(stream,r) for r in range(1,4)};Rs[4]=R4;baseline={x:mean(stream[f'probe_obs_{x}'][t] for t in range(181,201)) for x in 'abc'};R5={}
    for obs in 'abc':
        for target,ts in zip(pair,TARGETED_BLOCKS):R5[(obs,target)]=mean(stream[f'probe_obs_{obs}'][t] for t in ts)-baseline[obs]
    amps=(0.025,0.050,0.100,0.200,0.200);denom=sqrt(sum(d*d for d in amps));i,j=pair
    def c(obs,target):return (sum(amps[k-1]*Rs[k][(obs,target)] for k in range(1,5))+TARGETED_AMPLITUDE*R5[(obs,target)])/denom
    cij,cji=c(i,j),c(j,i);return min(cij,cji),cij,cji,R5

def _after_full_round4(stream,blocks,q3,pair3,early_score,missing_flag,mu,nu,mu5t,nu5t):
    R4=response_matrix_for_blocks(stream,blocks);_,Q4,_=cumulative_with_custom_r4(stream,R4);groups,_,_,qualified=graph_from_q(Q4,mu[3],nu[3]);data={'q3':q3,'pair3':pair3,'early':int(pair3 is not None),'early_score':early_score,'early_qualified':0,'missing':missing_flag,'fallback':1,'R4':R4,'Q4':Q4,'round5':0,'pair5':None}
    if qualified:return groups,1,0,4,stream,data
    pair5=leading_edge(Q4)
    if pair5 is None:return None,0,1,0,stream,data
    s5=inject_targeted_round5_custom(stream,pair5);score,_,_,_=targeted_score_custom(s5,pair5,R4);edges5=[p for p in PAIRS if (score>mu5t if p==pair5 else Q4[p]>mu[3])];g5=groups_from_edges(edges5);sizes=sorted(sum(1 for x in 'abc' if g5[x]==g) for g in set(g5.values()));qual5=int(len(edges5)==1 and sizes==[1,2] and pair5 in edges5 and score>nu5t);data['round5']=1;data['pair5']=pair5
    return (g5 if qual5 else None),qual5,1-qual5,(5 if qual5 else 0),s5,data

def infer_early(stream,mu,nu,mu4e,nu4e,mu5t,nu5t):
    q3=round3_q(stream,mu,nu);pair3=leading_edge(q3)
    if pair3 is None:
        full,blocks,_=prepare_early_round4(stream,None);return _after_full_round4(full,blocks,q3,None,None,0,mu,nu,mu5t,nu5t)
    early,blocks,missing=prepare_early_round4(stream,pair3);escore,_,_=early_selected_score(early,pair3,blocks);edges=[p for p in PAIRS if (escore>mu4e if p==pair3 else q3[p]>mu[2])];groups=groups_from_edges(edges);sizes=sorted(sum(1 for x in 'abc' if groups[x]==g) for g in set(groups.values()));qualified=int(len(edges)==1 and sizes==[1,2] and pair3 in edges and escore>nu4e)
    if qualified:
        return groups,1,0,4,early,{'q3':q3,'pair3':pair3,'early':1,'early_score':escore,'early_qualified':1,'missing':0,'fallback':0,'R4':None,'Q4':None,'round5':0,'pair5':None}
    full,fullblocks=complete_round4(early,blocks,missing);return _after_full_round4(full,fullblocks,q3,pair3,escore,1,mu,nu,mu5t,nu5t)

def annotation(stream,mu,nu,mu4e,nu4e,mu5t,nu5t,accepted,abstain,stop,groups,data):
    if data['pair3'] is None:energy=0.796875;blocks=12
    else:energy=0.196875+0.4+(0.2 if data['missing'] else 0.0);blocks=9+2+(1 if data['missing'] else 0)
    if data['round5']:energy+=0.4;blocks+=2
    out={'probe_gain':stream['probe_gain'],'probe_stop_round':stop,'probe_energy':energy,'probe_block_count':blocks,'probe_max_amplitude':0.2,'provenance_accepted':accepted,'provenance_abstain':abstain,'accepted_partition_correct':partition_matches(groups) if accepted else '','early_targeted_round4_executed':data['early'],'early_selected_edge':''.join(data['pair3']) if data['pair3'] else '','early_selector_correct':int(data['pair3']==('a','b')) if data['pair3'] else '','early_mu_4':mu4e,'early_nu_4':nu4e,'early_r4_score':data['early_score'] if data['early_score'] is not None else '','early_r4_qualified':data['early_qualified'],'missing_third_block_executed':data['missing'],'fallback_completion':data['fallback'],'targeted_round5_executed':data['round5'],'targeted_selected_edge':''.join(data['pair5']) if data['pair5'] else '','mu_probe_5_targeted':mu5t,'nu_probe_5_targeted':nu5t}
    for p in PAIRS:out[f'early_q3_{p[0]}{p[1]}']=data['q3'][p]
    if data['Q4'] is not None:
        for p in PAIRS:out[f'fallback_q4_{p[0]}{p[1]}']=data['Q4'][p]
    return out

def run_experiment_020_strategy(seed,family,magnitude,strategy,tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5,mu5t,nu5t,mu4e,nu4e):
    if strategy!=EARLY_STRATEGY:return run_experiment_019_strategy(seed,family,magnitude,strategy,tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5,mu5t,nu5t)
    base=generate_experiment_017_stream(seed,family,magnitude);groups,accepted,abstain,stop,stream,data=infer_early(base,mu,nu,mu4e,nu4e,mu5t,nu5t);ann=annotation(stream,mu,nu,mu4e,nu4e,mu5t,nu5t,accepted,abstain,stop,groups,data)
    if abstain:
        rows=fallback018(seed,family,magnitude,tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5,stream,{1:None,2:None,3:None,4:None},groups)
        for r in rows:r['strategy']=EARLY_STRATEGY;r.update(ann)
        return rows
    rows=run_group_gate018(seed,f'experiment020_{family}_{magnitude:.3f}',tau,k3,la,lb,lc,lab,lac,lbc,stream,ann,groups)
    for r in rows:r['strategy']=EARLY_STRATEGY
    return rows
