#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
import experiment_051 as exp51
import run_experiment_051 as base

SEEDS=range(52000,53000)
AUDIT=set(range(52000,52005))
STRESS={
 'M1':(5251000,'round-wise heteroskedastic symmetric scales 0.75,1.00,1.25,1.50,1.75'),
 'M2':(5252000,'direction-wise heteroskedastic symmetric forward:reverse 1:1.5'),
 'M3':(5253000,'AR(1) symmetric Gaussian rho=0.30'),
 'M4':(5254000,'90/10 asymmetric contaminated Gaussian shift +0.50'),
}
OPERATIVE_SPEC_ISSUE=162

def configure():
 exp51.OPERATIVE_SPEC_ISSUE=OPERATIVE_SPEC_ISSUE
 base.OPERATIVE_SPEC_ISSUE=OPERATIVE_SPEC_ISSUE
 base.SEEDS=SEEDS
 base.AUDIT=AUDIT
 base.STRESS=STRESS

configure()
CELLS=exp51.CELLS
STRATEGIES=exp51.STRATEGIES
SIGNED_RANK_STRATEGY=exp51.SIGNED_RANK_STRATEGY
summary=base.summary
write_csv=base.write_csv
calibration_values=base.calibration_values

def run_experiment_052_strategy(seed,c,strategy,vals):
 configure();return exp51.run_experiment_051_strategy(seed,c,strategy,vals)

def report_from(rows):
 configure();r=base.report_from(rows);r['evaluation_seeds']=[52000,52999];r['audit_seeds']=[52000,52001,52002,52003,52004];r['bootstrap_seed']=52052;r['operative_spec_issue']=OPERATIVE_SPEC_ISSUE;r['replication_of_experiment051']=True;return r
