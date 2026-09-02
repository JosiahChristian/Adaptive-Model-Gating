#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))

import experiment_066 as e66
from experiment_051 import CELLS
from run_experiment_066_development_shard import _primary_one

CANONICAL_RUN_ID = 33531109410
RECOVERY_ISSUE = 273
DP_SHARD_N = 50
RECOVERY_HALF_N = 25
DP_SHARD_COUNT = 40


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cell-index', type=int, required=True)
    ap.add_argument('--chunk-index', type=int, required=True)
    ap.add_argument('--half-index', type=int, required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()

    if not e66.provenance_integrity():
        raise AssertionError('provenance_integrity')
    if not 0 <= a.cell_index < 6:
        raise ValueError('cell-index')
    if not 0 <= a.chunk_index < DP_SHARD_COUNT:
        raise ValueError('chunk-index')
    if a.half_index not in (0, 1):
        raise ValueError('half-index')

    full_start, full_stop = e66.DEVELOPMENT_PRIMARY_RANGE
    if full_stop - full_start != DP_SHARD_N * DP_SHARD_COUNT:
        raise AssertionError('dp_partition')
    start = full_start + DP_SHARD_N * a.chunk_index + RECOVERY_HALF_N * a.half_index
    stop = start + RECOVERY_HALF_N
    chunk_start = full_start + DP_SHARD_N * a.chunk_index
    if not (chunk_start <= start < stop <= chunk_start + DP_SHARD_N):
        raise AssertionError('recovery_bounds')

    cell = CELLS[a.cell_index]
    rows = [_primary_one(seed, cell) for seed in range(start, stop)]
    if len(rows) != RECOVERY_HALF_N or [int(r['seed']) for r in rows] != list(range(start, stop)):
        raise AssertionError('recovery_coverage')
    if any(r['cell'] != cell['label'] or r['replica_discovery_used'] is not False for r in rows):
        raise AssertionError('recovery_identity')

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    with (out / 'rows.jsonl').open('w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, separators=(',', ':')) + '\n')
    meta = {
        'experiment': 66,
        'role': 'development_primary_recovery_subshard',
        'cell_index': a.cell_index,
        'chunk_index': a.chunk_index,
        'half_index': a.half_index,
        'cell': cell['label'],
        'seed_range': [start, stop - 1],
        'n': len(rows),
        'paired_m1_a0': True,
        'replica_count': 5,
        'operative_spec_issue': 269,
        'provenance_closure_issue': 270,
        'execution_closure_issue': 272,
        'execution_recovery_issue': RECOVERY_ISSUE,
        'source_canonical_run': CANONICAL_RUN_ID,
        'validation_seeds_touched': False,
        'no_tuning': True,
    }
    (out / 'meta.json').write_text(json.dumps(meta, indent=2))


if __name__ == '__main__':
    main()
