#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))

import experiment_061 as e61
import experiment_066 as e66
from experiment_051 import CELLS

SMOKE_STRESS_START = 90_000_000
SMOKE_STRESS_SEED = 90_000_001
SMOKE_PRIMARY_SEED = 90_002_000


def _all_reserved_and_derived_intervals():
    intervals = []
    source_ranges = list(e66.DEVELOPMENT_ROBUSTNESS_RANGES.values()) + [e66.DEVELOPMENT_PRIMARY_RANGE]
    source_ranges += list(e66.VALIDATION_ROBUSTNESS_RANGES.values()) + [e66.VALIDATION_PRIMARY_RANGE]
    for start, stop in source_ranges:
        intervals.append((start, stop))
        for j in range(1, e66.REPLICA_COUNT + 1):
            intervals.append((start + e66.REPLICA_SEED_STRIDE * j, stop + e66.REPLICA_SEED_STRIDE * j))
    return intervals


def _outside_reserved(seed):
    return all(not (start <= seed < stop) for start, stop in _all_reserved_and_derived_intervals())


def _check_replica(r):
    assert len(r['confirmation_profile']) == 6
    assert set(r['confirmation_scores']) == set(e66.CANDIDATE_ORDER)
    scores = r['confirmation_scores']
    reconstructed = max(e66.CANDIDATE_ORDER, key=lambda h: (float(scores[h]), -e66.CANDIDATE_ORDER.index(h)))
    assert reconstructed == r['confirmation_candidate']
    maximum = max(float(scores[h]) for h in e66.CANDIDATE_ORDER)
    tie = int(sum(int(float(scores[h]) == maximum) for h in e66.CANDIDATE_ORDER) > 1)
    assert tie == int(r['topology_tie_flag'])


def main():
    assert e66.provenance_integrity()
    assert e66.CANDIDATE_ORDER == ('H_ab', 'H_ac', 'H_bc')
    assert e66.REPLICA_COUNT == 5
    assert 3 ** e66.REPLICA_COUNT == 243
    assert 1.0 / 243.0 <= 0.01 < 1.0 / 81.0
    assert e66.STRUCTURAL_E_ACCEPT == 243.0
    assert e66.E_THRESHOLD == 100.0

    smoke_seeds = [SMOKE_STRESS_SEED, SMOKE_PRIMARY_SEED]
    for source_seed in tuple(smoke_seeds):
        smoke_seeds.extend(e66.replica_seed(source_seed, j) for j in range(1, e66.REPLICA_COUNT + 1))
    assert all(_outside_reserved(s) for s in smoke_seeds)
    assert len(smoke_seeds) == len(set(smoke_seeds))

    stress = e66.evaluate_robustness_draw('DQ1', SMOKE_STRESS_SEED, SMOKE_STRESS_START)
    assert stress['seed'] == SMOKE_STRESS_SEED
    assert len(stress['replicas']) == 5
    assert [r['replica_index'] for r in stress['replicas']] == [1, 2, 3, 4, 5]
    assert [r['replica_seed'] for r in stress['replicas']] == [e66.replica_seed(SMOKE_STRESS_SEED, j) for j in range(1, 6)]
    for r in stress['replicas']:
        _check_replica(r)
    assert stress['m1_accept'] in (0, 1)
    assert int(stress['e_value'] >= 100.0) == stress['m1_accept']

    cell = CELLS[0]
    source_stream = e61.generate_experiment_061_stream(SMOKE_PRIMARY_SEED, cell)
    _, _, _, _, path, _, _, _, _, _ = e61.infer_confirmation_agreement_061(source_stream)
    source_candidate = path[0]['candidate']
    primary = e66.primary_m1(SMOKE_PRIMARY_SEED, cell, source_candidate)
    assert len(primary['replicas']) == 5
    assert all(r['discovery_used'] is False for r in primary['replicas'])
    assert all(r['replica_seed'] == e66.replica_seed(SMOKE_PRIMARY_SEED, r['replica_index']) for r in primary['replicas'])
    for r in primary['replicas']:
        _check_replica(r)
    assert int(primary['e_value'] >= 100.0) == primary['m1_accept']

    print('Experiment 066 prospective preflight passed: frozen five-replica topology-unanimity mechanics, reconstructable evidence fields, and nonreserved smoke isolation verified; no reserved outcomes executed.')


if __name__ == '__main__':
    main()
