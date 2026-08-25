#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
import experiment_056 as exp56
import run_experiment_055 as base
from experiment_051 import CELLS

SEEDS=range(56000,57000)
AUDIT=set(range(56000,56005))
STRESS={
 'M1':(5651000,'round-wise heteroskedastic symmetric scales 0.75,1.00,1.25,1.50,1.75'),
 'M2':(5652000,'direction-wise heteroskedastic symmetric forward:reverse 1:1.5'),
 'M3':(5653000,'AR(1) symmetric Gaussian rho=0.30'),
 'M4':(5654000,'90/10 asymmetric contaminated Gaussian shift +0.50'),
}
STRATEGIES=exp56.STRATEGIES
SIGNED_RANK_30_STRATEGY=exp56.SIGNED_RANK_30_STRATEGY
W_CUTOFF=exp56.W_CUTOFF
P345_NUMERATOR=exp56.P345_NUMERATOR;P345_DENOMINATOR=exp56.P345_DENOMINATOR
P344_NUMERATOR=exp56.P344_NUMERATOR;P344_DENOMINATOR=exp56.P344_DENOMINATOR
OPERATIVE_SPEC_ISSUE=196

# Reuse the already-frozen Experiment 055 evaluator logic while replacing only
# prospective replication seeds/stress ranges and provenance identifier.
base.SEEDS=SEEDS;base.AUDIT=AUDIT;base.STRESS=STRESS
calibration_values=base.calibration_values
write_csv=base.write_csv
summary=base.summary
exact_tail=base.exact_tail


def run_experiment_056_strategy(seed,c,strategy,vals):
    return exp56.run_experiment_056_strategy(seed,c,strategy,vals)


def report_from(rows):
    # The Experiment 055 report code contains a hard-coded check for its own
    # operative issue (190). Validate the actual Experiment 056 provenance
    # independently, then use a metadata-only copy for inherited calculations.
    primary=[r for r in rows if r.get('strategy')==SIGNED_RANK_30_STRATEGY]
    provenance_ok=bool(primary) and all(int(float(r.get('rank55_spec_issue',0) or 0))==OPERATIVE_SPEC_ISSUE for r in primary)
    calc=[]
    for r in rows:
        x=dict(r)
        if x.get('strategy')==SIGNED_RANK_30_STRATEGY:
            x['rank55_spec_issue']=190
        calc.append(x)
    base.SEEDS=SEEDS;base.AUDIT=AUDIT;base.STRESS=STRESS
    rep=base.report_from(calc)
    if not provenance_ok:
        rep['hypotheses']['H2']=False;rep['hypotheses']['H16']=False
    rep['all_hypotheses_pass']=all(rep['hypotheses'].values())
    rep.update({
        'experiment':56,
        'evaluation_seeds':[56000,56999],
        'audit_seeds':[56000,56001,56002,56003,56004],
        'bootstrap_seed':56056,
        'operative_spec_issue':OPERATIVE_SPEC_ISSUE,
        'replication_of_experiment055':True,
        'provenance_validation':'actual rank55_spec_issue values independently required to equal 196 before inherited report calculation',
        'no_tuning':True,
    })
    return rep
