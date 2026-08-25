#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
import experiment_051 as exp51
import run_experiment_051 as base

SEEDS=range(53000,54000)
AUDIT=set(range(53000,53005))
STRESS={
 'M1':(5351000,'round-wise heteroskedastic symmetric scales 0.75,1.00,1.25,1.50,1.75'),
 'M2':(5352000,'direction-wise heteroskedastic symmetric forward:reverse 1:1.5'),
 'M3':(5353000,'AR(1) symmetric Gaussian rho=0.30'),
 'M4':(5354000,'90/10 asymmetric contaminated Gaussian shift +0.50'),
}
OPERATIVE_SPEC_ISSUE=168

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

def run_experiment_053_strategy(seed,c,strategy,vals):
 configure();return exp51.run_experiment_051_strategy(seed,c,strategy,vals)

def report_from(rows):
 configure();r=base.report_from(rows);r['evaluation_seeds']=[53000,53999];r['audit_seeds']=[53000,53001,53002,53003,53004];r['bootstrap_seed']=53053;r['operative_spec_issue']=OPERATIVE_SPEC_ISSUE;r['clean_provenance_replication_of_experiment052']=True;return r
