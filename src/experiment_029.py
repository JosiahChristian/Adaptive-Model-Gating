from __future__ import annotations

from experiment_016 import groups_from_edges, partition_matches
from experiment_018 import ALL_AMPLITUDES, _run_group_gate as run_group_gate018
from experiment_022 import bind_stressed_stream, generate_stress_stream, run_experiment_022_strategy
from experiment_023 import diagnostic_noise_factor
from experiment_027 import inject_symmetric_round5
from experiment_028 import HYPOTHESES, covariance_terms, directed_stage, posterior_from_directed

POSTERIOR_RISK_STRATEGY='sequential_directed_covariance_posterior_risk_gate'
QUALIFICATION_AWARE_STRATEGY='qualification_aware_early_targeted_replicated_selective_cumulative_provenance_quorum'
TRIAD='triad_persistence'
WRONG_COST=100.0
FALLBACK_COST=1.0
ACCEPT_THRESHOLD=1.0-(FALLBACK_COST/WRONG_COST)
UNIQUE=('H_ab','H_ac','H_bc')
EDGE={'H_ab':('a','b'),'H_ac':('a','c'),'H_bc':('b','c')}


def infer_posterior_risk(stream):
    _,sigma_hat=diagnostic_noise_factor(stream);path=[]
    for stage in range(1,6):
        y=directed_stage(stream,stage);var,cov=covariance_terms(sigma_hat,stage);post,logs,quad=posterior_from_directed(y,var,cov)
        candidate=max(UNIQUE,key=lambda h:post[h]);p=float(post[candidate]);risk=WRONG_COST*(1.0-p)
        row={'stage':stage,'candidate':candidate,'candidate_posterior':p,'posterior_error_risk':1.0-p,'expected_wrong_action_loss':risk,
             'posterior':post,'variance':var,'shared_covariance':cov,'mahalanobis_zero':quad}
        path.append(row)
        if p>=ACCEPT_THRESHOLD:
            return groups_from_edges([EDGE[candidate]]),1,0,stage,path
    return None,0,1,0,path


def _energy(stop,path):
    stages=(stop if stop else len(path))
    return sum(15.0*(float(ALL_AMPLITUDES[r-1])**2) for r in range(1,stages+1))


def _annotation(stream,groups,accepted,abstain,stop,path):
    last=path[(stop-1) if stop else -1]
    out={'probe_gain':stream['probe_gain'],'probe_stop_round':stop,'probe_energy':_energy(stop,path),'probe_block_count':3*(stop if stop else len(path)),
         'probe_max_amplitude':float(ALL_AMPLITUDES[(stop if stop else len(path))-1]),'provenance_accepted':accepted,'provenance_abstain':abstain,
         'accepted_partition_correct':partition_matches(groups) if accepted else '',
         'posterior_risk_wrong_cost':WRONG_COST,'posterior_risk_fallback_cost':FALLBACK_COST,'posterior_risk_accept_threshold':ACCEPT_THRESHOLD,
         'posterior_deploy_hypothesis':last['candidate'] if accepted else '',
         'posterior_at_deployment':last['candidate_posterior'] if accepted else '',
         'posterior_implied_error_risk':last['posterior_error_risk'] if accepted else '',
         'posterior_expected_wrong_action_loss':last['expected_wrong_action_loss'] if accepted else ''}
    for s in path:
        r=s['stage'];out[f'posterior_r{r}_candidate']=s['candidate'];out[f'posterior_r{r}_candidate_p']=s['candidate_posterior'];out[f'posterior_r{r}_error_risk']=s['posterior_error_risk']
        for h in HYPOTHESES:out[f'posterior_r{r}_{h}']=s['posterior'][h]
    return out


def run_experiment_029_strategy(seed,c,strategy,vals):
    if strategy!=POSTERIOR_RISK_STRATEGY:
        if strategy not in (QUALIFICATION_AWARE_STRATEGY,TRIAD):raise ValueError(strategy)
        return run_experiment_022_strategy(seed,c,strategy,vals)
    stream=inject_symmetric_round5(generate_stress_stream(seed,c));groups,accepted,abstain,stop,path=infer_posterior_risk(stream);ann=_annotation(stream,groups,accepted,abstain,stop,path)
    tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5,mu5t,nu5t,mu4e,nu4e=vals
    if abstain:
        with bind_stressed_stream(stream):rows=run_experiment_022_strategy(seed,c,TRIAD,vals)
        for r in rows:r['strategy']=POSTERIOR_RISK_STRATEGY;r.update(ann)
    else:
        rows=run_group_gate018(seed,f'experiment029_{c["label"]}',tau,k3,la,lb,lc,lab,lac,lbc,stream,ann,groups)
        for r in rows:r['strategy']=POSTERIOR_RISK_STRATEGY
    for r in rows:
        r['experiment029_cell']=c['label'];r['experiment029_kind']=c['kind'];r['experiment029_gain']=c.get('gain',stream.get('probe_gain',''));r['experiment029_noise_scale']=c.get('noise_scale',1.0)
    return rows
