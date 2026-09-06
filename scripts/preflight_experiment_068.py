#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')

import scipy
from scipy.stats import beta
import experiment_068 as exp

SMOKE_START = 90_000_000
SMOKE_SEED = 90_000_007


def overlaps(v, ranges):
    return any(a <= v < b for a,b in ranges)


def main():
    assert exp.provenance_integrity()
    assert exp.CANDIDATE_ORDER == ('H_ab','H_ac','H_bc')
    assert exp.REPLICA_COUNT == 5
    assert exp.REPLICA_SEED_STRIDE == 10_000_000
    assert scipy.__version__ == exp.SCIPY_VERSION == '1.17.0'
    assert abs(exp.ALPHA_FAMILY - (0.05/6.0)) < 1e-15
    assert exp.ERROR_TARGET == 0.01
    assert set(exp.CALIBRATION_RANGES) == {f'CQ{i}' for i in range(1,7)}
    assert set(exp.RESERVED_CONFIRMATION_RANGES) == {f'XQ{i}' for i in range(1,7)}
    assert all(b-a == 8000 for a,b in exp.CALIBRATION_RANGES.values())
    assert all(b-a == 8000 for a,b in exp.RESERVED_CONFIRMATION_RANGES.values())

    reserved = list(exp.CALIBRATION_RANGES.values()) + list(exp.RESERVED_CONFIRMATION_RANGES.values())
    reserved += [(6724000,6748000)]  # Experiment 067 RQ1-RQ6 union
    reserved += [(6614000,6635000)]  # Experiment 066 VQ1-VQ6/VP union
    for j in range(0,6):
        assert not overlaps(SMOKE_SEED + j*exp.REPLICA_SEED_STRIDE, reserved)

    candidate = exp.external_candidate(SMOKE_SEED, SMOKE_START)
    reps = [exp.stress_replica('CQ1', SMOKE_SEED, SMOKE_START, j) for j in range(1,6)]
    assert all(r['discovery_used'] is False for r in reps)
    assert [r['replica_seed'] for r in reps] == [SMOKE_SEED + j*10_000_000 for j in range(1,6)]
    assert all(r['confirmation_candidate'] in exp.CANDIDATE_ORDER for r in reps)
    assert all(set(r['confirmation_scores']) == set(exp.CANDIDATE_ORDER) for r in reps)
    for r in reps:
        scores=r['confirmation_scores']; m=max(scores.values())
        reconstructed=min(exp.CANDIDATE_ORDER, key=lambda h: (-float(scores[h]), exp.CANDIDATE_ORDER.index(h)))
        tie=int(sum(int(float(scores[h]) == float(m)) for h in exp.CANDIDATE_ORDER)>1)
        assert reconstructed == r['confirmation_candidate']
        assert tie == int(r['topology_tie_flag'])
    c1=exp.c1_from_candidates(candidate,[r['confirmation_candidate'] for r in reps])
    assert c1['wrong_accept'] == int(c1['unanimous_match_count'] == 5)

    # Verify exact formula mechanics only; no reserved outcome is consumed.
    x,n=0,8000
    u=float(beta.ppf(1-exp.ALPHA_FAMILY, x+1, n-x))
    assert 0.0 < u < 1.0
    print('Experiment 068 prospective preflight PASS: mechanics/statistic verified on nonreserved smoke only; no CQ/XQ/RQ/VQ/VP outcomes inspected')

if __name__ == '__main__':
    main()
