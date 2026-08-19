from experiment_013 import health
from experiment_016 import _run_group_quorum,_run_naive,run_experiment_016_strategy
from experiment_017 import _fallback_rows,_run_cumulative_gate,generate_experiment_017_stream,infer_selective_cumulative


def _complete_new_rows(rows,stream,la,lb,lc,lab,lac,lbc):
    h=health(stream)
    for row in rows:
        t=row['t']
        m={x:int(h[x][t] is not None and h[x][t]>l) for x,l in [('a',la),('b',lb),('c',lc)]}
        dis={'ab':int(h['ab'][t] is not None and h['ab'][t]>lab),'ac':int(h['ac'][t] is not None and h['ac'][t]>lac),'bc':int(h['bc'][t] is not None and h['bc'][t]>lbc)}
        row.setdefault('anchor_mismatch',m['a']);row.setdefault('anchor_b_mismatch',m['b']);row.setdefault('anchor_c_mismatch',m['c'])
        row.setdefault('anchor_ab_disagreement',dis['ab']);row.setdefault('anchor_ac_disagreement',dis['ac']);row.setdefault('anchor_bc_disagreement',dis['bc'])
        for key in ('x_true','x_primary','x_r1','x_r2','z','z_b','z_c','probe_obs_a','probe_obs_b','probe_obs_c','probe_noise_a','probe_noise_b','probe_noise_c'):
            row.setdefault(key,stream[key][t])
    return rows


def run_experiment_017_strategy(seed,family,magnitude,strategy,tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu):
    stream=generate_experiment_017_stream(seed,family,magnitude);label=f'experiment017_{family}_{magnitude:.3f}'
    if strategy=='cumulative_provenance_quorum':
        rows=_run_cumulative_gate(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,stream,mu,nu,False)
        return _complete_new_rows(rows,stream,la,lb,lc,lab,lac,lbc)
    if strategy=='selective_cumulative_provenance_quorum':
        inferred,executed,stop,accepted,abstain,candidate=infer_selective_cumulative(stream,mu,nu)
        if abstain:
            rows=_fallback_rows(seed,family,magnitude,tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,stream,mu,nu,executed,candidate)
        else:
            rows=_run_cumulative_gate(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,stream,mu,nu,True)
        return _complete_new_rows(rows,stream,la,lb,lc,lab,lac,lbc)
    if strategy=='naive_three_anchor_quorum':
        return _run_naive(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,lambdas,stream)
    if strategy in ('oracle_provenance_quorum','max_probe_provenance_quorum','sequential_provenance_quorum'):
        mode={'oracle_provenance_quorum':'oracle','max_probe_provenance_quorum':'max','sequential_provenance_quorum':'sequential'}[strategy]
        return _run_group_quorum(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,lambdas,stream,mode)
    base={'drift_ab_gain0375':'drift_ab_fault','drift_ab_gain0125':'drift_ab_fault'}.get(family,family)
    return run_experiment_016_strategy(seed,base,magnitude,strategy,tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas)
