#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

import experiment_067 as e67

SMOKE_START = 90_100_000
SMOKE_SEED = 90_100_001


def all_reserved_and_derived_intervals():
    out = []
    for start, stop in list(e67.DEVELOPMENT_RANGES.values()) + list(e67.RESERVED_REPLICATION_RANGES.values()):
        out.append((start, stop))
        for j in range(1, e67.REPLICA_COUNT + 1):
            out.append((start + e67.REPLICA_SEED_STRIDE*j, stop + e67.REPLICA_SEED_STRIDE*j))
    return out


def outside_reserved(seed):
    return all(not (a <= seed < b) for a,b in all_reserved_and_derived_intervals())


def main():
    assert e67.provenance_integrity()
    assert e67.CANDIDATE_ORDER == ('H_ab','H_ac','H_bc')
    assert e67.REPLICA_COUNT == 5
    seeds = [SMOKE_SEED] + [e67.replica_seed(SMOKE_SEED,j) for j in range(1,6)]
    assert len(seeds) == len(set(seeds)) and all(outside_reserved(s) for s in seeds)
    row = e67.evaluate_diagnostic_draw('ZQ1', SMOKE_SEED, SMOKE_START)
    assert row['seed'] == SMOKE_SEED and row['source_candidate'] in e67.CANDIDATE_ORDER
    assert len(row['replicas']) == 5
    assert [r['replica_index'] for r in row['replicas']] == [1,2,3,4,5]
    assert [r['replica_seed'] for r in row['replicas']] == [e67.replica_seed(SMOKE_SEED,j) for j in range(1,6)]
    assert all(r['discovery_used'] is False for r in row['replicas'])
    for r in row['replicas']:
        assert len(r['confirmation_profile']) == 6
        assert set(r['confirmation_scores']) == set(e67.CANDIDATE_ORDER)
        scores = r['confirmation_scores']
        reconstructed = max(e67.CANDIDATE_ORDER, key=lambda h: (float(scores[h]), -e67.CANDIDATE_ORDER.index(h)))
        assert reconstructed == r['confirmation_candidate']
        mx = max(float(scores[h]) for h in e67.CANDIDATE_ORDER)
        tie = int(sum(int(float(scores[h]) == mx) for h in e67.CANDIDATE_ORDER) > 1)
        assert tie == int(r['topology_tie_flag'])
    print('Experiment 067 prospective preflight passed: diagnostic mechanics, five-replica mapping, reconstructable topology evidence, and reserved-seed isolation verified; no ZQ/RQ outcomes executed.')

if __name__ == '__main__':
    main()
