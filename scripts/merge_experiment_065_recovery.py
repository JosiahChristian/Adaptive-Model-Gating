#!/usr/bin/env python3
import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import experiment_065 as e
from experiment_051 import CELLS

Z = 1.6448536269514722
CANONICAL_RUN_ID = 33220329747
CANONICAL_CHUNKS = 16
CANONICAL_CHUNK_N = 125
RECOVERY_SUBSHARD_N = 25
RECOVERY_ISSUE = 267
PRIOR_REPAIR_ISSUE = 265


def wilson_upper(k, n):
    if n <= 0:
        return 1.0
    p = k / n
    den = 1 + Z * Z / n
    center = (p + Z * Z / (2 * n)) / den
    rad = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / den
    return min(1.0, center + rad)


def load_rows(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def artifact_records(root):
    records = []
    for meta_path in sorted(Path(root).glob('**/meta.json')):
        meta = json.loads(meta_path.read_text())
        rows_path = meta_path.with_name('rows.jsonl')
        if not rows_path.exists():
            raise AssertionError(f'missing_rows:{meta_path}')
        records.append((meta_path, meta, load_rows(rows_path)))
    return records


def canonical_chunk_bounds(chunk):
    start, stop = e.DEVELOPMENT_PRIMARY_RANGE
    if stop - start != CANONICAL_CHUNKS * CANONICAL_CHUNK_N:
        raise AssertionError('canonical_partition')
    cs = start + chunk * CANONICAL_CHUNK_N
    return cs, cs + CANONICAL_CHUNK_N


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--canonical-root', required=True)
    ap.add_argument('--recovery-root', required=True)
    ap.add_argument('--manifest', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(Path(args.manifest).read_text())
    if manifest.get('experiment') != 65 or manifest.get('execution_repair_issue') != RECOVERY_ISSUE:
        raise AssertionError('manifest_identity')
    if manifest.get('canonical_run_id') != CANONICAL_RUN_ID:
        raise AssertionError('manifest_canonical_run')
    if manifest.get('canonical_head_sha') != 'b50cec02a327ffdf8b4490ceae079ede087cff02':
        raise AssertionError('manifest_canonical_head')
    if manifest.get('no_tuning') is not True or manifest.get('validation_seeds_touched') is not False:
        raise AssertionError('manifest_science_boundary')

    frozen_success = sorted((int(x['cell_index']), int(x['chunk_index'])) for x in manifest['canonical_successful_dp'])
    if len(frozen_success) != len(set(frozen_success)):
        raise AssertionError('manifest_duplicate_success')
    if any(not (0 <= c < len(CELLS) and 0 <= k < CANONICAL_CHUNKS) for c, k in frozen_success):
        raise AssertionError('manifest_success_bounds')

    canonical = artifact_records(args.canonical_root)
    recovery = artifact_records(args.recovery_root)
    integrity = bool(e.provenance_integrity())
    raw_manifest = []

    dq = {}
    for panel, (start, stop) in e.DEVELOPMENT_ROBUSTNESS_RANGES.items():
        matches = [(p, m, r) for p, m, r in canonical if m.get('role') == 'development_robustness' and m.get('panel') == panel]
        if len(matches) != 1:
            raise AssertionError(f'dq_artifact_count:{panel}:{len(matches)}')
        p, meta, rows = matches[0]
        seeds = [int(r['seed']) for r in rows]
        expected = list(range(start, stop))
        ok = (
            meta.get('experiment') == 65
            and meta.get('seed_range') == [start, stop - 1]
            and int(meta.get('n', -1)) == 2000
            and len(rows) == 2000
            and seeds == expected
            and len(set(seeds)) == 2000
            and all(r.get('panel') == panel and r.get('q_family') == e.q_family(panel) for r in rows)
        )
        integrity = integrity and ok
        accepted = sum(int(r['m0_accept']) for r in rows)
        wrong = accepted
        upper = wilson_upper(wrong, len(rows))
        precision = 0.0 if accepted else None
        panel_pass = bool(upper <= 0.01 and (accepted == 0 or precision >= 0.99))
        dq[panel] = {
            'seed_range': [start, stop - 1], 'n': len(rows), 'accepted_n': accepted,
            'wrong_n': wrong, 'wrong_acceptance': wrong / len(rows),
            'wrong_wilson_upper_95': upper, 'precision': precision,
            'G_065_DQ_pass': panel_pass, 'null_panel': True,
        }
        raw_manifest.append(str(p.with_name('rows.jsonl')))

    canonical_dp = {}
    discovered_success = []
    for p, meta, rows in canonical:
        if meta.get('role') != 'development_primary_chunk':
            continue
        cell = int(meta.get('cell_index', -1))
        chunk = int(meta.get('chunk_index', -1))
        if not (0 <= cell < len(CELLS) and 0 <= chunk < CANONICAL_CHUNKS):
            raise AssertionError('canonical_dp_bounds')
        if int(meta.get('execution_repair_issue', -1)) != PRIOR_REPAIR_ISSUE:
            raise AssertionError('canonical_dp_repair_identity')
        cs, ce = canonical_chunk_bounds(chunk)
        seeds = [int(r['seed']) for r in rows]
        ok = (
            meta.get('seed_range') == [cs, ce - 1]
            and int(meta.get('n', -1)) == CANONICAL_CHUNK_N
            and len(rows) == CANONICAL_CHUNK_N
            and seeds == list(range(cs, ce))
            and len(set(seeds)) == CANONICAL_CHUNK_N
            and all(r.get('panel') == 'DP' and r.get('cell') == CELLS[cell]['label'] and int(r.get('shared_primary_stream', 0)) == 1 for r in rows)
        )
        integrity = integrity and ok
        key = (cell, chunk)
        if key in canonical_dp:
            raise AssertionError('duplicate_canonical_chunk')
        canonical_dp[key] = rows
        discovered_success.append(key)
        raw_manifest.append(str(p.with_name('rows.jsonl')))

    if sorted(discovered_success) != frozen_success:
        raise AssertionError('canonical_success_manifest_mismatch')

    expected_keys = {(c, k) for c in range(len(CELLS)) for k in range(CANONICAL_CHUNKS)}
    success_keys = set(frozen_success)
    missing_keys = expected_keys - success_keys

    recovery_by_key = {key: [] for key in missing_keys}
    for p, meta, rows in recovery:
        if meta.get('role') != 'development_primary_recovery_subshard':
            continue
        cell = int(meta.get('cell_index', -1))
        if not 0 <= cell < len(CELLS):
            raise AssertionError('recovery_cell_bounds')
        if int(meta.get('execution_repair_issue', -1)) != RECOVERY_ISSUE or int(meta.get('source_canonical_run', -1)) != CANONICAL_RUN_ID:
            raise AssertionError('recovery_identity')
        start_seed, end_seed_inclusive = [int(x) for x in meta.get('seed_range', [])]
        stop_seed = end_seed_inclusive + 1
        if stop_seed - start_seed > RECOVERY_SUBSHARD_N or stop_seed - start_seed <= 0:
            raise AssertionError('recovery_subshard_size')
        base_start, _ = e.DEVELOPMENT_PRIMARY_RANGE
        chunk = (start_seed - base_start) // CANONICAL_CHUNK_N
        if not 0 <= chunk < CANONICAL_CHUNKS:
            raise AssertionError('recovery_chunk_bounds')
        cs, ce = canonical_chunk_bounds(chunk)
        if not (cs <= start_seed < stop_seed <= ce):
            raise AssertionError('recovery_crosses_chunk')
        key = (cell, chunk)
        if key not in missing_keys:
            raise AssertionError('recovery_overlaps_preserved_canonical')
        seeds = [int(r['seed']) for r in rows]
        ok = (
            int(meta.get('n', -1)) == stop_seed - start_seed
            and seeds == list(range(start_seed, stop_seed))
            and len(set(seeds)) == len(seeds)
            and all(r.get('panel') == 'DP' and r.get('cell') == CELLS[cell]['label'] and int(r.get('shared_primary_stream', 0)) == 1 for r in rows)
        )
        integrity = integrity and ok
        recovery_by_key[key].extend(rows)
        raw_manifest.append(str(p.with_name('rows.jsonl')))

    dp_rows = []
    for cell in range(len(CELLS)):
        cell_rows = []
        for chunk in range(CANONICAL_CHUNKS):
            key = (cell, chunk)
            cs, ce = canonical_chunk_bounds(chunk)
            if key in success_keys:
                rows = canonical_dp[key]
            else:
                rows = sorted(recovery_by_key[key], key=lambda r: int(r['seed']))
                seeds = [int(r['seed']) for r in rows]
                if len(rows) != CANONICAL_CHUNK_N or seeds != list(range(cs, ce)) or len(set(seeds)) != CANONICAL_CHUNK_N:
                    raise AssertionError(f'incomplete_recovery:{cell}:{chunk}')
            cell_rows.extend(rows)
        cell_rows = sorted(cell_rows, key=lambda r: int(r['seed']))
        start, stop = e.DEVELOPMENT_PRIMARY_RANGE
        cell_seeds = [int(r['seed']) for r in cell_rows]
        integrity = integrity and len(cell_rows) == 2000 and cell_seeds == list(range(start, stop)) and len(set(cell_seeds)) == 2000
        dp_rows.extend(cell_rows)

    start, stop = e.DEVELOPMENT_PRIMARY_RANGE
    expected_n = (stop - start) * len(CELLS)
    integrity = integrity and len(dp_rows) == expected_n
    m0 = sum(int(r['m0_accept']) for r in dp_rows)
    a0 = sum(int(r['a0_accept']) for r in dp_rows)
    subset_ok = all(not int(r['m0_accept']) or int(r['a0_accept']) for r in dp_rows)
    integrity = integrity and subset_ok
    ratio = m0 / a0 if a0 else None
    coverage_pass = bool(a0 > 0 and ratio >= 0.90)
    m0_loss = sum(float(r['m0_operational_loss_401_600']) for r in dp_rows) / len(dp_rows)
    a0_loss = sum(float(r['a0_operational_loss_401_600']) for r in dp_rows) / len(dp_rows)
    dq_pass = all(v['G_065_DQ_pass'] for v in dq.values())
    gate = bool(integrity and dq_pass and coverage_pass)

    report = {
        'experiment': 65,
        'phase': 'development',
        'operative_spec_issue': 258,
        'provenance_closure_issue': 259,
        'execution_closure_issue': 261,
        'prior_execution_repair_issue': PRIOR_REPAIR_ISSUE,
        'execution_recovery_issue': RECOVERY_ISSUE,
        'canonical_run_id': CANONICAL_RUN_ID,
        'canonical_successful_dp_chunks': [{'cell_index': c, 'chunk_index': k} for c, k in frozen_success],
        'recovered_missing_dp_chunks': len(missing_keys),
        'integrity_pass': bool(integrity),
        'development_robustness': dq,
        'DP': {
            'seed_range': [start, stop - 1], 'cell_count': len(CELLS),
            'paired_draws': len(dp_rows), 'M0_accept_count': m0, 'A0_accept_count': a0,
            'M0_coverage': m0 / len(dp_rows), 'A0_coverage': a0 / len(dp_rows),
            'coverage_ratio_M0_over_A0': ratio, 'coverage_ratio_gate_ge_0_90': coverage_pass,
            'subset_M0_of_A0': subset_ok,
            'mean_M0_operational_loss_401_600': m0_loss,
            'mean_A0_operational_loss_401_600': a0_loss,
            'mean_operational_loss_delta_M0_minus_A0': m0_loss - a0_loss,
            'operational_loss_role': 'descriptive only; not a G-065 gate',
        },
        'G_065_pass': gate,
        'interpretation_branch': 'PROCEED_TO_RESERVED_VALIDATION' if gate else 'STOP_NO_VALIDATION',
        'validation_seeds_touched': False,
        'no_tuning': True,
        'raw_manifest': raw_manifest,
    }
    (out / 'development_report.json').write_text(json.dumps(report, indent=2))
    (out / 'decision.txt').write_text('PASS\n' if gate else 'FAIL\n')


if __name__ == '__main__':
    main()
