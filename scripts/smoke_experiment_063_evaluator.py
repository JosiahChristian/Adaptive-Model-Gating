#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
import run_experiment_063 as r

assert r.OPERATIVE_SPEC_ISSUE==241
assert r.IMPLEMENTATION_CLOSURE_ISSUE==243
assert list(r.SEEDS)==list(range(71000,72000))
assert r.AUDIT==set(range(71000,71005))
assert r.W_CUTOFF==345
assert r.BOOTSTRAP_SEED==63063 and r.BOOTSTRAP_RESAMPLES==10000
assert r.STRESS_CANDIDATE_ORDER==('H_ab','H_ac','H_bc')
assert r.ROBUSTNESS_SEED_RANGES=={
    'R1':(6351000,6353000),'R2':(6353000,6355000),'R3':(6355000,6357000),
    'R4':(6357000,6359000),'R5':(6359000,6361000),'R6':(6361000,6363000)}
assert r.exact_tail(345)==(r.P345_NUMERATOR,r.P345_DENOMINATOR)
assert r.exact_tail(344)==(r.P344_NUMERATOR,r.P344_DENOMINATOR)

# Nonreserved primary-path integrity smoke. Reserved primary seeds are 71000..71999.
# Reuse the already-validated Experiment 062 evaluator smoke seed so this
# implementation-only check exercises the same strict nonzero/unique-rank
# integrity path without touching any Experiment 063 reserved outcome.
seed=620621;c=r.CELLS[0];vals=r.calibration_values()
rows=r.run_experiment_063_strategy(seed,c,r.PRIMARY_STRATEGY,vals)
s=r.summary(rows,c)
assert r.integrity(s)
assert str(s['rank63_candidate'])==str(s['rank55_candidate'])
assert int(float(s['rank63_candidate_reselected']))==0
assert int(float(s['rank63_no_extra_observations']))==1

# Nonreserved stress-generator smoke. Frozen R1-R6 ranges are not touched here.
for i,panel in enumerate(('R1','R2','R3','R4','R5','R6')):
    start=r.ROBUSTNESS_SEED_RANGES[panel][0]
    x=r._stress_one(panel,630640+i,start)
    assert x['seed']==630640+i
    assert x['discovery_candidate'] in r.STRESS_CANDIDATE_ORDER
    assert x['confirmation_candidate'] in r.STRESS_CANDIDATE_ORDER
    assert 0<=x['wplus']<=465
    assert x['comparator_accept'] in (0,1) and x['repaired_accept'] in (0,1)
    assert x['repaired_accept']<=x['comparator_accept']
print('Experiment 063 evaluator prospective smoke passed')
