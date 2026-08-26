#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
import experiment_059 as exp59
import run_experiment_055 as base
from experiment_051 import CELLS

SEEDS=range(63000,64000)
AUDIT=set(range(63000,63005))
STRESS={
 'M1':(5951000,'round-wise heteroskedastic symmetric scales 0.75,1.00,1.25,1.50,1.75'),
 'M2':(5952000,'direction-wise heteroskedastic symmetric forward:reverse 1:1.5'),
 'M3':(5953000,'AR(1) symmetric Gaussian rho=0.30'),
 'M4':(5954000,'90/10 asymmetric contaminated Gaussian shift +0.50'),
}
STRATEGIES=exp59.STRATEGIES
SIGNED_RANK_30_STRATEGY=exp59.SIGNED_RANK_30_STRATEGY
W_CUTOFF=exp59.W_CUTOFF
P345_NUMERATOR=exp59.P345_NUMERATOR;P345_DENOMINATOR=exp59.P345_DENOMINATOR
P344_NUMERATOR=exp59.P344_NUMERATOR;P344_DENOMINATOR=exp59.P344_DENOMINATOR
OPERATIVE_SPEC_ISSUE=215

base.SEEDS=SEEDS;base.AUDIT=AUDIT;base.STRESS=STRESS
calibration_values=base.calibration_values
write_csv=base.write_csv
summary=base.summary
exact_tail=base.exact_tail


def run_experiment_059_strategy(seed,c,strategy,vals):
    return exp59.run_experiment_059_strategy(seed,c,strategy,vals)


def report_from(rows):
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
        'experiment':59,
        'evaluation_seeds':[63000,63999],
        'audit_seeds':[63000,63001,63002,63003,63004],
        'bootstrap_seed':59059,
        'operative_spec_issue':OPERATIVE_SPEC_ISSUE,
        'replication_of_experiment055_056':True,
        'provenance_validation':'actual rank55_spec_issue values independently required to equal 215 before inherited report calculation',
        'no_tuning':True,
    })
    return rep
