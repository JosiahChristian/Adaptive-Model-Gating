#!/usr/bin/env python3
import math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
import experiment_054 as e
from run_experiment_051 import calibration_values

# Structural constants frozen in prospective issue #173.
assert e.OPERATIVE_SPEC_ISSUE==173
assert e.CONTRAST_COUNT==20
assert e.FAMILIES==('sign','wilcoxon','normal')
assert e.THETAS==(0.5,1.0,2.0,4.0)
assert e.COMPONENT_COUNT==12
assert e.ACCEPT_PATTERN_COUNT==10485
assert e.NULL_PATTERN_COUNT==1048576
assert e.P_STAR==10485/1048576
assert e.ACCEPT_E>=100.0
assert len(e.SCORE_MAPS['sign'])==len(e.SCORE_MAPS['wilcoxon'])==len(e.SCORE_MAPS['normal'])==20
assert all(x==1.0 for x in e.SCORE_MAPS['sign'])
assert e.SCORE_MAPS['wilcoxon']==tuple(r/20.0 for r in range(1,21))
assert abs(e.SCORE_MAPS['normal'][-1]-1.0)<1e-15

# Independently enumerate the full conditional fair-sign null before any evaluation request.
b=e.enumerate_null_boundary()
assert b['pattern_count']==1048576
assert b['accepted_count']==10485
assert abs(b['accepted_low']-e.BF_ACCEPTED_LOW)<5e-11,(b['accepted_low'],e.BF_ACCEPTED_LOW)
assert abs(b['rejected_high']-e.BF_REJECTED_HIGH)<5e-11,(b['rejected_high'],e.BF_REJECTED_HIGH)
assert e.BF_REJECTED_HIGH < e.BF_CUTOFF < e.BF_ACCEPTED_LOW
assert abs(b['cutoff']-8.473649256901517)<1e-15
assert abs(b['p_star']-0.009999275207519531)<1e-18
assert abs(b['accept_e']-100.0072484501669)<1e-12

# Rank-map and BF implementation checks on deterministic non-tied values.
vals=tuple((i+1)*(1.0 if i%3 else -1.0) for i in range(20))
bf,ranks,signs=e.family_mixture_statistic(vals)
assert ranks==tuple(range(1,21))
assert signs==tuple(1 if x>0 else -1 for x in vals)
assert math.isfinite(bf) and bf>0

# One full candidate execution verifies integration without creating an evaluation result set.
c=e.exp51.CELLS[0];rows=e.run_experiment_054_strategy(54000,c,e.FAMILY_MIXTURE_STRATEGY,calibration_values())
assert rows and all(r['strategy']==e.FAMILY_MIXTURE_STRATEGY for r in rows)
r0=rows[0]
assert int(r0['mix54_spec_issue'])==173
assert int(r0['mix54_contrast_count'])==20
assert int(r0['mix54_component_count'])==12
assert int(r0['experiment054_no_tuning'])==1
assert str(r0['experiment054_cell'])==c['label']
assert float(r0['mix54_bf_cutoff'])==e.BF_CUTOFF
assert float(r0['mix54_accept_e'])==e.ACCEPT_E
print('Experiment 054 prospective smoke passed; exhaustive null boundary verified before evaluation.')
