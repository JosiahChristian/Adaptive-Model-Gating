#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from run_experiment_061 import *

assert list(SEEDS)==list(range(69000,70000))
assert AUDIT==set(range(69000,69005))
assert len(CELLS)==16 and PRIMARY_STRATEGY in STRATEGIES and COMPARATOR_STRATEGY in STRATEGIES
assert W_CUTOFF==345
assert exact_tail(345)==(P345_NUMERATOR,P345_DENOMINATOR)
assert exact_tail(344)==(P344_NUMERATOR,P344_DENOMINATOR)
vals=calibration_values();assert isinstance(vals,tuple) and len(vals)>=9

# Nonreserved implementation-only evaluator smoke. Reserved Experiment 061
# scientific seeds are 69000..69999.
c=CELLS[0];seed=610611
pr=run_experiment_061_strategy(seed,c,PRIMARY_STRATEGY,vals)
cr=run_experiment_061_strategy(seed,c,COMPARATOR_STRATEGY,vals)
p=summary(pr,c);q=summary(cr,c)
assert integrity(p)
assert int(float(p['rank61_spec_issue']))==226
assert int(float(p['rank61_contrast_count']))==30
assert int(float(p['rank61_w_cutoff']))==345
assert int(float(p['rank61_no_extra_observations']))==1
assert int(float(p['rank61_candidate_reselected']))==0
assert p['rank61_candidate']==q['rank55_candidate']
assert int(float(p['rank61_wplus']))==int(float(q['rank55_wplus']))
for r in range(1,6):
    assert p[f'rank55_baseline_discovery_r{r}']==q[f'rank55_baseline_discovery_r{r}']
    assert p[f'rank55_baseline_confirmation_r{r}']==q[f'rank55_baseline_confirmation_r{r}']
    for k in range(1,7):
        assert float(p[f'rank55_pair_response_r{r}_{k}'])==float(q[f'rank55_pair_response_r{r}_{k}'])
assert int(float(p['coverage']))==int(int(float(p['rank61_signed_rank_pass'])) and int(float(p['rank61_confirmation_agreement'])))
print('Experiment 061 evaluator prospective smoke passed')
