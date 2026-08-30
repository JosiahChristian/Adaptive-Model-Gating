#!/usr/bin/env python3
import argparse
import concurrent.futures
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import experiment_065 as e
from experiment_051 import CELLS

CANONICAL_CHUNKS = 16
SUBSHARDS_PER_CHUNK = 5
SUBSHARD_N = 25
MAX_LOCAL_WORKERS = 4
RECOVERY_ISSUE = 267
CANONICAL_RUN_ID = 33220329747


def plan_ranges(cell_index: int, chunk_index: int):
    if not 0 <= cell_index < len(CELLS):
        raise ValueError('cell-index')
    if not 0 <= chunk_index < CANONICAL_CHUNKS:
        raise ValueError('chunk-index')
    full_start, full_stop = e.DEVELOPMENT_PRIMARY_RANGE
    chunk_n = (full_stop - full_start) // CANONICAL_CHUNKS
    if chunk_n != 125 or (full_stop - full_start) % CANONICAL_CHUNKS:
        raise AssertionError('canonical_chunk_partition')
    start = full_start + chunk_index * chunk_n
    stop = start + chunk_n
    ranges = [(s, min(s + SUBSHARD_N, stop)) for s in range(start, stop, SUBSHARD_N)]
    if len(ranges) != SUBSHARDS_PER_CHUNK:
        raise AssertionError('recovery_subshard_count')
    if any(b - a != SUBSHARD_N for a, b in ranges):
        raise AssertionError('recovery_subshard_size')
    flattened = [seed for a, b in ranges for seed in range(a, b)]
    if flattened != list(range(start, stop)):
        raise AssertionError('recovery_partition_coverage')
    return ranges


def run_one(cell_index: int, start: int, stop: int, out_root: Path):
    out = out_root / f'seeds-{start}-{stop - 1}'
    cmd = [
        sys.executable,
        str(ROOT / 'scripts' / 'run_experiment_065_development_shard.py'),
        '--cell-index', str(cell_index),
        '--seed-start', str(start),
        '--seed-stop', str(stop),
        '--out', str(out),
    ]
    subprocess.run(cmd, cwd=ROOT, check=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cell-index', type=int, required=True)
    ap.add_argument('--chunk-index', type=int, required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--plan-only', action='store_true')
    args = ap.parse_args()

    ranges = plan_ranges(args.cell_index, args.chunk_index)
    if args.plan_only:
        for start, stop in ranges:
            print(f'{args.cell_index},{args.chunk_index},{start},{stop}')
        return

    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_LOCAL_WORKERS) as executor:
        futures = [executor.submit(run_one, args.cell_index, start, stop, out_root) for start, stop in ranges]
        for future in futures:
            future.result()

    metas = sorted(out_root.glob('seeds-*/meta.json'))
    rows = sorted(out_root.glob('seeds-*/rows.jsonl'))
    if len(metas) != SUBSHARDS_PER_CHUNK or len(rows) != SUBSHARDS_PER_CHUNK:
        raise AssertionError('recovery_outputs_missing')


if __name__ == '__main__':
    main()
