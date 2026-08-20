from __future__ import annotations
from math import sqrt

from experiment_016 import groups_from_edges, partition_matches
from experiment_017 import cumulative_statistics
from experiment_018 import _fallback as fallback018, _run_group_gate as run_group_gate018
from experiment_019 import PAIRS
from experiment_020 import (
    prepare_early_round4, complete_round4, early_selected_score,
    response_matrix_for_blocks, cumulative_with_custom_r4,
    inject_targeted_round5_custom, targeted_score_custom,
)
from experiment_023 import diagnostic_noise_factor
from experiment_022 import bind_stressed_stream, generate_stress_stream, run_experiment_022_strategy

MARGIN_STRATEGY='uncertainty_aware_margin_qualification_aware_early_targeted_replicated_selective_cumulative_provenance_quorum'
Z_MARGIN=2.128045234184984
SE_C_COEFF=sqrt(0.3325)


def leading(q):
    vals=sorted(((float(v),p) for p,v in q.items()),reverse=True)
    if len(vals)<2 or vals[0][0]==vals[1][0]:return None
    return vals[0][1]


def margin_stats(q,candidate,sigma_hat):
    top=float(q[candidate]);others=[float(q[p]) for p in PAIRS if p!=candidate];second=max(others)
    se_c=max(float(sigma_hat)*SE_C_COEFF,1e-12);se_margin=sqrt(2.0)*se_c
    margin=top-second;z=margin/se_margin
    return margin,se_margin,z,second


def qualify_q(q,raw_floor,sigma_hat):
    cand=leading(q)
    if cand is None:return None,0,None
    margin,se,z,second=margin_stats(q,cand,sigma_hat)
    ok=int(float(q[cand])>float(raw_floor) and z>=Z_MARGIN)
    return cand,ok,{'candidate':cand,'score':float(q[cand]),'second':second,'margin':margin,'se_margin':se,'z_margin':z,'raw_floor':float(raw_floor)}


def q_for_round(stream,rnd):
    C,Rs=cumulative_statistics(stream,rnd);q={(i,j):min(C[(i,j)],C[(j,i)]) for i,j in PAIRS};return q,C,Rs


def _groups(pair):
    return groups_from_edges([pair]) if pair is not None else None


def infer_margin_policy(stream,mu,mu5t,mu4e,sigma_hat):
    trace={'stages':[],'early':0,'missing':0,'round5':0,'pair3':None,'pair5':None,'Q4':None}
    # Qualification-aware exits through rounds 1..3.
    for rnd in (1,2,3):
        q,_,_=q_for_round(stream,rnd);cand,ok,st=qualify_q(q,mu[rnd-1],sigma_hat);trace['stages'].append({'stage':f'r{rnd}',**(st or {})})
        if ok:
            return _groups(cand),1,0,rnd,stream,trace
    # Early-target round 4 uses the unique round-3 leader for target selection.
    q3,_,_=q_for_round(stream,3);pair3=leading(q3);trace['pair3']=pair3
    if pair3 is None:
        full,blocks,_=prepare_early_round4(stream,None)
    else:
        trace['early']=1
        early,blocks,missing=prepare_early_round4(stream,pair3)
        escore,_,_=early_selected_score(early,pair3,blocks)
        qearly=dict(q3);qearly[pair3]=float(escore)
        margin,se,z,second=margin_stats(qearly,pair3,sigma_hat)
        ok=int(float(escore)>float(mu4e) and z>=Z_MARGIN)
        trace['stages'].append({'stage':'early_r4','candidate':pair3,'score':float(escore),'second':second,'margin':margin,'se_margin':se,'z_margin':z,'raw_floor':float(mu4e)})
        if ok:
            return _groups(pair3),1,0,4,early,trace
        full,blocks=complete_round4(early,blocks,missing);trace['missing']=1
    # Full round 4 ambiguity-aware qualification.
    R4=response_matrix_for_blocks(full,blocks);_,q4,_=cumulative_with_custom_r4(full,R4);trace['Q4']=q4
    pair4,ok4,st4=qualify_q(q4,mu[3],sigma_hat);trace['stages'].append({'stage':'full_r4',**(st4 or {})})
    if ok4:return _groups(pair4),1,0,4,full,trace
    # Targeted round 5 updates only the leading round-4 edge and compares its
    # updated score against the two inherited round-4 competitors.
    pair5=leading(q4);trace['pair5']=pair5
    if pair5 is None:return None,0,1,0,full,trace
    s5=inject_targeted_round5_custom(full,pair5);score,_,_,_=targeted_score_custom(s5,pair5,R4);q5=dict(q4);q5[pair5]=float(score)
    margin,se,z,second=margin_stats(q5,pair5,sigma_hat);ok5=int(float(score)>float(mu5t) and z>=Z_MARGIN);trace['round5']=1
    trace['stages'].append({'stage':'targeted_r5','candidate':pair5,'score':float(score),'second':second,'margin':margin,'se_margin':se,'z_margin':z,'raw_floor':float(mu5t)})
    if ok5:return _groups(pair5),1,0,5,s5,trace
    return None,0,1,0,s5,trace


def _annotation(stream,accepted,abstain,stop,groups,trace,sigma_hat):
    # Energy mirrors the inherited 020 path exactly.
    if trace['pair3'] is None:energy=0.796875;blocks=12
    else:energy=0.196875+0.4+(0.2 if trace['missing'] else 0.0);blocks=11+(1 if trace['missing'] else 0)
    if trace['round5']:energy+=0.4;blocks+=2
    out={'probe_gain':stream['probe_gain'],'probe_stop_round':stop,'probe_energy':energy,'probe_block_count':blocks,'probe_max_amplitude':0.2,
         'provenance_accepted':accepted,'provenance_abstain':abstain,'accepted_partition_correct':partition_matches(groups) if accepted else '',
         'diagnostic_noise_sd_hat':sigma_hat,'margin_z_cutoff':Z_MARGIN,'margin_se_c_coeff':SE_C_COEFF,
         'early_targeted_round4_executed':trace['early'],'missing_third_block_executed':trace['missing'],'targeted_round5_executed':trace['round5'],
         'early_selected_edge':''.join(trace['pair3']) if trace['pair3'] else '','targeted_selected_edge':''.join(trace['pair5']) if trace['pair5'] else ''}
    for idx,st in enumerate(trace['stages'],1):
        out[f'margin_stage_{idx}']=st.get('stage','');out[f'margin_stage_{idx}_edge']=''.join(st['candidate']) if st.get('candidate') else ''
        for k in ('score','second','margin','se_margin','z_margin','raw_floor'):
            out[f'margin_stage_{idx}_{k}']=st.get(k,'')
    return out


def run_experiment_024_strategy(seed,c,strategy,vals):
    if strategy!=MARGIN_STRATEGY:return run_experiment_022_strategy(seed,c,strategy,vals)
    stream=generate_stress_stream(seed,c);_,sigma_hat=diagnostic_noise_factor(stream)
    # vals = tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5,mu5t,nu5t,mu4e,nu4e
    tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5,mu5t,nu5t,mu4e,nu4e=vals
    groups,accepted,abstain,stop,used_stream,trace=infer_margin_policy(stream,mu,mu5t,mu4e,sigma_hat)
    ann=_annotation(used_stream,accepted,abstain,stop,groups,trace,sigma_hat)
    if abstain:
        with bind_stressed_stream(used_stream):
            rows=run_experiment_022_strategy(seed,c,'triad_persistence',vals)
        for r in rows:r['strategy']=MARGIN_STRATEGY;r.update(ann)
    else:
        rows=run_group_gate018(seed,f'experiment024_{c["label"]}',tau,k3,la,lb,lc,lab,lac,lbc,used_stream,ann,groups)
        for r in rows:r['strategy']=MARGIN_STRATEGY
    for r in rows:
        r['experiment024_cell']=c['label'];r['experiment024_kind']=c['kind'];r['experiment024_noise_scale']=c.get('noise_scale',1.0);r['experiment024_gain']=c.get('gain',used_stream.get('probe_gain',''))
    return rows
