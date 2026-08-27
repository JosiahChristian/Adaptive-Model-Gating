#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from run_experiment_062 import *

assert list(SEEDS)==list(range(70000,71000))
assert AUDIT==set(range(70000,70005))
assert len(CELLS)==16 and PRIMARY_STRATEGY in STRATEGIES and COMPARATOR_STRATEGY in STRATEGIES
assert W_CUTOFF==345
assert exact_tail(345)==(P345_NUMERATOR,P345_DENOMINATOR)
assert exact_tail(344)==(P344_NUMERATOR,P344_DENOMINATOR)
vals=calibration_values();assert isinstance(vals,tuple) and len(vals)>=9

# Nonreserved implementation-only evaluator smoke. Reserved Experiment 062
# scientific seeds are 70000..70999.
c=CELLS[0];seed=620621
pr=run_experiment_062_strategy(seed,c,PRIMARY_STRATEGY,vals)
cr=run_experiment_062_strategy(seed,c,COMPARATOR_STRATEGY,vals)
p=summary(pr,c);q=summary(cr,c)
assert integrity(p)
assert int(float(p['rank62_spec_issue']))==235
assert int(float(p['rank62_contrast_count']))==30
assert int(float(p['rank62_w_cutoff']))==345
assert int(float(p['rank62_no_extra_observations']))==1
assert int(float(p['rank62_candidate_reselected']))==0
assert p['rank62_candidate']==q['rank55_candidate']
assert int(float(p['rank62_wplus']))==int(float(q['rank55_wplus']))
for r in range(1,6):
    assert p[f'rank55_baseline_discovery_r{r}']==q[f'rank55_baseline_discovery_r{r}']
    assert p[f'rank55_baseline_confirmation_r{r}']==q[f'rank55_baseline_confirmation_r{r}']
    for k in range(1,7):
        assert float(p[f'rank55_pair_response_r{r}_{k}'])==float(q[f'rank55_pair_response_r{r}_{k}'])
assert int(float(p['coverage']))==int(int(float(p['rank62_signed_rank_pass'])) and int(float(p['rank62_confirmation_agreement'])))
print('Experiment 062 evaluator prospective smoke passed')
