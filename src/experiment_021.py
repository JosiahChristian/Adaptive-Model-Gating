from __future__ import annotations

from experiment_017 import generate_experiment_017_stream, infer_cumulative_round
from experiment_019 import run_experiment_019_strategy
from experiment_020 import EARLY_STRATEGY, run_experiment_020_strategy

QUALIFICATION_AWARE_STRATEGY='qualification_aware_early_targeted_replicated_selective_cumulative_provenance_quorum'
TARGETED_019='targeted_replicated_selective_cumulative_provenance_quorum'


def inherited_prequalification_round(stream,mu,nu):
    for rnd in (1,2,3):
        data=infer_cumulative_round(stream,mu,nu,rnd)
        if data[5]:
            return rnd
    return 0


def _mark(rows,prequal_round,entered_020):
    for row in rows:
        row['strategy']=QUALIFICATION_AWARE_STRATEGY
        row['inherited_prequalified']=int(prequal_round>0)
        row['inherited_prequalification_round']=prequal_round
        row['experiment020_dispatch_entry']=int(entered_020)
    return rows


def run_experiment_021_strategy(seed,family,magnitude,strategy,tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5,mu5t,nu5t,mu4e,nu4e):
    if strategy!=QUALIFICATION_AWARE_STRATEGY:
        return run_experiment_020_strategy(seed,family,magnitude,strategy,tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5,mu5t,nu5t,mu4e,nu4e)

    stream=generate_experiment_017_stream(seed,family,magnitude)
    prequal=inherited_prequalification_round(stream,mu,nu)
    if prequal:
        rows=run_experiment_019_strategy(seed,family,magnitude,TARGETED_019,tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5,mu5t,nu5t)
        actual=int(rows[0].get('probe_stop_round',0))
        if actual!=prequal:
            raise AssertionError(f'inherited early-exit mismatch: predicted {prequal}, inherited path stopped {actual}')
        return _mark(rows,prequal,False)

    rows=run_experiment_020_strategy(seed,family,magnitude,EARLY_STRATEGY,tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5,mu5t,nu5t,mu4e,nu4e)
    return _mark(rows,0,True)
