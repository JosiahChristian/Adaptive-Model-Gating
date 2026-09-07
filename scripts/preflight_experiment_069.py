#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src')); sys.path.insert(0,str(ROOT/'scripts'))
import scipy
import experiment_069 as e69
import experiment_061 as e61
import experiment_066 as e66
from experiment_051 import CELLS
from run_experiment_066_development_shard import _primary_one

SMOKE_XQ_SEED=90_100_000
SMOKE_PRIMARY_SEED=90_200_000

def all_reserved_intervals():
    intervals=[]
    for start,stop in list(e69.XQ_RANGES.values())+[e69.PRIMARY_RANGE]:
        for j in range(0,6): intervals.append((start+10_000_000*j,stop+10_000_000*j))
    return intervals

def outside(seed): return all(not a<=seed<b for a,b in all_reserved_intervals())

def main():
    assert scipy.__version__==e69.SCIPY_VERSION
    assert e69.provenance_integrity()
    assert outside(SMOKE_XQ_SEED) and all(outside(SMOKE_XQ_SEED+10_000_000*j) for j in range(1,6))
    # mechanics-only null smoke through frozen Q1 generator using a nonreserved synthetic interval start
    import experiment_068 as e68
    panel='CQ1'; source_start=SMOKE_XQ_SEED
    candidate=e68.external_candidate(SMOKE_XQ_SEED,source_start)
    reps=[e68.stress_replica(panel,SMOKE_XQ_SEED,source_start,j) for j in range(1,6)]
    assert [r['replica_seed'] for r in reps]==[SMOKE_XQ_SEED+10_000_000*j for j in range(1,6)]
    assert all(r['discovery_used'] is False for r in reps)
    for r in reps:
        scores=r['confirmation_scores']; expected=max(e69.CANDIDATE_ORDER,key=lambda h:(scores[h],-e69.CANDIDATE_ORDER.index(h)))
        assert expected==r['confirmation_candidate']
        m=max(scores.values()); assert int(sum(v==m for v in scores.values())>1)==r['topology_tie_flag']
    c=e68.c1_from_candidates(candidate,[r['confirmation_candidate'] for r in reps]); assert c['wrong_accept']==int(c['unanimous_match_count']==5)
    assert outside(SMOKE_PRIMARY_SEED) and all(outside(SMOKE_PRIMARY_SEED+10_000_000*j) for j in range(1,6))
    row=_primary_one(SMOKE_PRIMARY_SEED,CELLS[0])
    assert row['replica_discovery_used'] is False and row['confirmation_replica_count']==5
    assert row['m1_accept']==int(row['unanimous_match_count']==5)
    assert row['m1_wrong_accept']==int(row['m1_accept'] and not row['candidate_correct'])
    assert row['a0_wrong_accept']==int(row['a0_accept'] and not row['candidate_correct'])
    print('Experiment 069 prospective preflight passed: mechanics/provenance only; no XQ/P069/RQ/VQ/VP outcomes inspected')
if __name__=='__main__': main()
