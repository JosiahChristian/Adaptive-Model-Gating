from experiment_016 import _run_group_quorum,_run_naive,run_experiment_016_strategy
from experiment_017 import NEW_STRATEGIES,_fallback_rows,_run_cumulative_gate,generate_experiment_017_stream,infer_selective_cumulative

PROBE_STRATEGIES={
 'naive_three_anchor_quorum','oracle_provenance_quorum','max_probe_provenance_quorum','sequential_provenance_quorum'
}


def run_experiment_017_strategy(seed,family,magnitude,strategy,tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu):
    stream=generate_experiment_017_stream(seed,family,magnitude);label=f'experiment017_{family}_{magnitude:.3f}'
    if strategy=='cumulative_provenance_quorum':
        return _run_cumulative_gate(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,stream,mu,nu,False)
    if strategy=='selective_cumulative_provenance_quorum':
        inferred,executed,stop,accepted,abstain,candidate=infer_selective_cumulative(stream,mu,nu)
        if abstain:return _fallback_rows(seed,family,magnitude,tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,stream,mu,nu,executed,candidate)
        return _run_cumulative_gate(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,stream,mu,nu,True)
    if strategy=='naive_three_anchor_quorum':
        return _run_naive(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,lambdas,stream)
    if strategy in ('oracle_provenance_quorum','max_probe_provenance_quorum','sequential_provenance_quorum'):
        mode={'oracle_provenance_quorum':'oracle','max_probe_provenance_quorum':'max','sequential_provenance_quorum':'sequential'}[strategy]
        return _run_group_quorum(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,lambdas,stream,mode)
    base={'drift_ab_gain0375':'drift_ab_fault','drift_ab_gain0125':'drift_ab_fault'}.get(family,family)
    return run_experiment_016_strategy(seed,base,magnitude,strategy,tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas)
