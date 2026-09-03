#!/usr/bin/env python3
import argparse
import json
import shutil
from pathlib import Path

DP_SHARD_N = 50
DP_SHARD_COUNT = 40
CELL_COUNT = 16
RECOVERY_HALF_N = 25
OPERATIVE_SPEC_ISSUE = 269
PROVENANCE_CLOSURE_ISSUE = 270
EXECUTION_CLOSURE_ISSUE = 272
RECOVERY_ISSUE = 273
INGESTION_CLOSURE_ISSUE = 275
CANONICAL_BATCH0_RUN_ID = 33531109410
DP_START = 6612000
DP_STOP = 6614000


def load_rows(path):
    return [json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()]


def write_rows(path, rows):
    with Path(path).open('w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, separators=(',', ':')) + '\n')


def collect(root):
    out = []
    for meta_path in sorted(Path(root).glob('**/meta.json')):
        rows_path = meta_path.with_name('rows.jsonl')
        if not rows_path.exists():
            raise AssertionError(f'missing_rows:{meta_path}')
        out.append((meta_path, json.loads(meta_path.read_text()), rows_path))
    return out


def expected_bounds(chunk):
    start = DP_START + DP_SHARD_N * chunk
    return start, start + DP_SHARD_N


def check_common(meta):
    if int(meta.get('experiment', -1)) != 66:
        raise AssertionError('experiment_identity')
    if int(meta.get('operative_spec_issue', -1)) != OPERATIVE_SPEC_ISSUE:
        raise AssertionError('operative_spec_identity')
    if int(meta.get('provenance_closure_issue', -1)) != PROVENANCE_CLOSURE_ISSUE:
        raise AssertionError('provenance_closure_identity')
    if int(meta.get('execution_closure_issue', -1)) != EXECUTION_CLOSURE_ISSUE:
        raise AssertionError('execution_closure_identity')
    if meta.get('validation_seeds_touched') not in (False, 0):
        raise AssertionError('validation_touched')
    if meta.get('no_tuning') not in (True, 1):
        raise AssertionError('no_tuning_identity')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    src = Path(a.root)
    out = Path(a.out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    recs = collect(src)
    dq = []
    canonical = {}
    recovery = {}

    for meta_path, meta, rows_path in recs:
        role = meta.get('role')
        if role == 'development_robustness':
            check_common(meta)
            dq.append((meta_path, meta, rows_path))
            continue
        if role == 'development_primary_shard':
            check_common(meta)
            c = int(meta.get('cell_index', -1)); k = int(meta.get('chunk_index', -1))
            if not (0 <= c < CELL_COUNT and 0 <= k < DP_SHARD_COUNT):
                raise AssertionError('canonical_key_bounds')
            key = (c, k)
            if key in canonical:
                raise AssertionError(f'duplicate_canonical:{key}')
            canonical[key] = (meta_path, meta, rows_path)
            continue
        if role == 'development_primary_recovery_subshard':
            check_common(meta)
            c = int(meta.get('cell_index', -1)); k = int(meta.get('chunk_index', -1)); h = int(meta.get('half_index', -1))
            if not (0 <= c < 6 and 0 <= k < DP_SHARD_COUNT and h in (0, 1)):
                raise AssertionError('recovery_key_bounds')
            if int(meta.get('execution_recovery_issue', -1)) != RECOVERY_ISSUE:
                raise AssertionError('recovery_issue_identity')
            if int(meta.get('source_canonical_run', -1)) != CANONICAL_BATCH0_RUN_ID:
                raise AssertionError('recovery_source_run')
            key = (c, k, h)
            if key in recovery:
                raise AssertionError(f'duplicate_recovery:{key}')
            recovery[key] = (meta_path, meta, rows_path)

    panels = sorted(str(m.get('panel')) for _, m, _ in dq)
    if panels != ['DQ1','DQ2','DQ3','DQ4','DQ5','DQ6']:
        raise AssertionError(f'dq_set:{panels}')
    for meta_path, meta, rows_path in dq:
        dest = out / f"DQ-{meta['panel']}"
        dest.mkdir()
        shutil.copy2(meta_path, dest / 'meta.json')
        shutil.copy2(rows_path, dest / 'rows.jsonl')

    manifest = {'experiment':66,'ingestion_closure_issue':INGESTION_CLOSURE_ISSUE,'dp':[],'dq_count':6}
    all_cell_seeds = {c: [] for c in range(CELL_COUNT)}

    for c in range(CELL_COUNT):
        for k in range(DP_SHARD_COUNT):
            key = (c, k)
            has_canonical = key in canonical
            halves = [(c, k, h) in recovery for h in (0, 1)]
            if has_canonical and any(halves):
                raise AssertionError(f'canonical_recovery_overlap:{key}')
            if has_canonical:
                meta_path, meta, rows_path = canonical[key]
                rows = load_rows(rows_path)
                source_paths = [str(meta_path.parent)]
                source_role = 'canonical'
            else:
                if halves != [True, True]:
                    raise AssertionError(f'missing_coordinate_or_half:{key}:{halves}')
                parts = []
                source_paths = []
                for h in (0, 1):
                    meta_path, meta, rows_path = recovery[(c, k, h)]
                    start, stop = expected_bounds(k)
                    hstart = start + h * RECOVERY_HALF_N
                    hstop = hstart + RECOVERY_HALF_N
                    rows_h = load_rows(rows_path)
                    if meta.get('seed_range') != [hstart, hstop - 1] or int(meta.get('n', -1)) != RECOVERY_HALF_N:
                        raise AssertionError(f'recovery_meta_coverage:{c}:{k}:{h}')
                    if [int(r['seed']) for r in rows_h] != list(range(hstart, hstop)):
                        raise AssertionError(f'recovery_row_coverage:{c}:{k}:{h}')
                    parts.extend(rows_h)
                    source_paths.append(str(meta_path.parent))
                rows = sorted(parts, key=lambda r: int(r['seed']))
                source_role = 'recovery_halves'

            start, stop = expected_bounds(k)
            seeds = [int(r['seed']) for r in rows]
            if len(rows) != DP_SHARD_N or seeds != list(range(start, stop)) or len(set(seeds)) != DP_SHARD_N:
                raise AssertionError(f'normalized_shard_coverage:{key}')
            all_cell_seeds[c].extend(seeds)
            dest = out / f'DP-cell-{c}-chunk-{k}'
            dest.mkdir()
            normalized_meta = {
                'experiment': 66,
                'role': 'development_primary_shard',
                'cell_index': c,
                'chunk_index': k,
                'seed_range': [start, stop - 1],
                'n': DP_SHARD_N,
                'paired_m1_a0': True,
                'replica_count': 5,
                'operative_spec_issue': OPERATIVE_SPEC_ISSUE,
                'provenance_closure_issue': PROVENANCE_CLOSURE_ISSUE,
                'execution_closure_issue': EXECUTION_CLOSURE_ISSUE,
                'validation_seeds_touched': False,
                'no_tuning': True,
                'normalized_under_ingestion_issue': INGESTION_CLOSURE_ISSUE,
                'source_role': source_role,
            }
            (dest / 'meta.json').write_text(json.dumps(normalized_meta, indent=2))
            write_rows(dest / 'rows.jsonl', rows)
            manifest['dp'].append({'cell_index':c,'chunk_index':k,'source_role':source_role,'source_paths':source_paths})

    if len(manifest['dp']) != CELL_COUNT * DP_SHARD_COUNT:
        raise AssertionError('normalized_coordinate_count')
    for c in range(CELL_COUNT):
        seeds = all_cell_seeds[c]
        if len(seeds) != DP_STOP - DP_START or seeds != list(range(DP_START, DP_STOP)) or len(set(seeds)) != DP_STOP - DP_START:
            raise AssertionError(f'cell_full_coverage:{c}')

    manifest['dp_coordinate_count'] = len(manifest['dp'])
    manifest['dp_paired_source_draws'] = CELL_COUNT * (DP_STOP - DP_START)
    manifest['scientific_values_inspected'] = False
    manifest['validation_seeds_touched'] = False
    manifest['no_tuning'] = True
    (out / 'ingestion_manifest.json').write_text(json.dumps(manifest, indent=2))
    print('normalized 6 DQ artifacts and 640 DP coordinates; exact provenance/seed coverage only; no scientific values summarized')


if __name__ == '__main__':
    main()
