#!/usr/bin/env python3
import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import experiment_061 as e61
import experiment_066 as e66
from experiment_051 import CELLS

Z = 1.6448536269514722
DP_SHARD_N = 50
DP_SHARD_COUNT = 40
OPERATIVE_SPEC_ISSUE = 269
PROVENANCE_CLOSURE_ISSUE = 270
PREFLIGHT_ISSUE = 271
EXECUTION_CLOSURE_ISSUE = 272


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


def records(root):
    out = []
    for meta_path in sorted(Path(root).glob('**/meta.json')):
        rows_path = meta_path.with_name('rows.jsonl')
        if not rows_path.exists():
            raise AssertionError(f'missing_rows:{meta_path}')
        out.append((meta_path, json.loads(meta_path.read_text()), load_rows(rows_path)))
    return out


def topology_candidate(scores):
    if set(scores) != set(e66.CANDIDATE_ORDER):
        raise AssertionError('topology_score_keys')
    return max(e66.CANDIDATE_ORDER, key=lambda h: (float(scores[h]), -e66.CANDIDATE_ORDER.index(h)))


def tie_flag(scores):
    vals = [float(scores[h]) for h in e66.CANDIDATE_ORDER]
    m = max(vals)
    return int(sum(int(v == m) for v in vals) > 1)


def check_replica(replica, source_seed, expected_index):
    if int(replica['replica_index']) != expected_index:
        raise AssertionError('replica_index')
    if int(replica['replica_seed']) != e66.replica_seed(source_seed, expected_index):
        raise AssertionError('replica_seed_mapping')
    if len(replica['confirmation_profile']) != 6:
        raise AssertionError('confirmation_profile_shape')
    if topology_candidate(replica['confirmation_scores']) != replica['confirmation_candidate']:
        raise AssertionError('replica_topology_reconstruction')
    if tie_flag(replica['confirmation_scores']) != int(replica['topology_tie_flag']):
        raise AssertionError('replica_tie_reconstruction')
    if replica.get('discovery_used', False) not in (False, 0):
        raise AssertionError('replica_discovery_leakage')


def check_m1_row(row):
    seed = int(row['seed'])
    replicas = row['replicas']
    if len(replicas) != e66.REPLICA_COUNT:
        raise AssertionError('replica_count')
    for j, replica in enumerate(replicas, 1):
        check_replica(replica, seed, j)
    decision = e66.m1_from_candidates(row['discovery_candidate'], [r['confirmation_candidate'] for r in replicas])
    if int(row['unanimous_match_count']) != int(decision['unanimous_match_count']):
        raise AssertionError('unanimity_reconstruction')
    if int(row['m1_accept']) != int(decision['m1_accept']):
        raise AssertionError('m1_accept_reconstruction')
    stored_e = float(row.get('m1_e_value', row.get('e_value')))
    if abs(stored_e - float(decision['e_value'])) > 1e-12:
        raise AssertionError('m1_e_reconstruction')


def check_primary_row(row, cell):
    check_m1_row(row)
    if row['topology_truth'] != cell['topology_truth']:
        raise AssertionError('topology_truth')
    candidate_correct = int(row['discovery_candidate'] == cell['topology_truth'])
    if int(row['candidate_correct']) != candidate_correct:
        raise AssertionError('candidate_correct')
    contrasts = tuple(float(x) for x in row['a0_pairwise_confirmation'])
    wplus, ranks = e61.base.signed_rank_statistic_30(contrasts)
    if wplus != int(row['a0_wplus']) or tuple(int(x) for x in ranks) != tuple(int(x) for x in row['a0_ranks']):
        raise AssertionError('a0_rank_reconstruction')
    if int(row['a0_w_cutoff']) != e61.W_CUTOFF or e61.W_CUTOFF != 345:
        raise AssertionError('a0_cutoff')
    conf = topology_candidate(row['a0_confirmation_scores'])
    if conf != row['a0_confirmation_candidate']:
        raise AssertionError('a0_confirmation_candidate')
    if tie_flag(row['a0_confirmation_scores']) != int(row['a0_topology_tie_flag']):
        raise AssertionError('a0_topology_tie')
    agreement = int(conf == row['discovery_candidate'])
    if agreement != int(row['a0_topology_agreement']):
        raise AssertionError('a0_agreement')
    a0 = int(wplus >= 345 and agreement)
    if a0 != int(row['a0_accept']):
        raise AssertionError('a0_accept')
    if int(row['a0_correct']) != int(a0 and candidate_correct) or int(row['a0_wrong_accept']) != int(a0 and not candidate_correct):
        raise AssertionError('a0_correctness')
    m1 = int(row['m1_accept'])
    if int(row['m1_correct']) != int(m1 and candidate_correct) or int(row['m1_wrong_accept']) != int(m1 and not candidate_correct):
        raise AssertionError('m1_correctness')
    fallback = float(row['fallback_operational_loss_401_600'])
    deploy = float(row['deploy_candidate_operational_loss_401_600'])
    if abs(float(row['m1_operational_loss_401_600']) - (deploy if m1 else fallback)) > 1e-12:
        raise AssertionError('m1_loss_assignment')
    if abs(float(row['a0_operational_loss_401_600']) - (deploy if a0 else fallback)) > 1e-12:
        raise AssertionError('a0_loss_assignment')
    if int(row['confirmation_replica_count']) != 5 or int(row['confirmation_scalars_per_replica']) != 180 or int(row['extra_m1_confirmation_scalars']) != 900:
        raise AssertionError('resource_accounting')
    if row.get('replica_discovery_used') not in (False, 0):
        raise AssertionError('replica_discovery_used')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    recs = records(args.root)
    integrity = bool(e66.provenance_integrity())
    raw_manifest = []

    dq_report = {}
    for panel, (start, stop) in e66.DEVELOPMENT_ROBUSTNESS_RANGES.items():
        matches = [(p, m, r) for p, m, r in recs if m.get('role') == 'development_robustness' and m.get('panel') == panel]
        if len(matches) != 1:
            raise AssertionError(f'dq_artifact_count:{panel}:{len(matches)}')
        p, meta, rows = matches[0]
        expected = list(range(start, stop))
        if meta.get('seed_range') != [start, stop - 1] or int(meta.get('n', -1)) != 2000 or [int(r['seed']) for r in rows] != expected:
            raise AssertionError(f'dq_coverage:{panel}')
        if int(meta.get('execution_closure_issue', -1)) != EXECUTION_CLOSURE_ISSUE:
            raise AssertionError('dq_execution_identity')
        for r in rows:
            if r['panel'] != panel or r['q_family'] != e66.q_family(panel) or r.get('null_panel') is not True:
                raise AssertionError('dq_identity')
            check_m1_row(r)
        accepted = sum(int(r['m1_accept']) for r in rows)
        upper = wilson_upper(accepted, len(rows))
        dq_report[panel] = {
            'seed_range': [start, stop - 1], 'n': len(rows), 'accepted_n': accepted,
            'wrong_n': accepted, 'wrong_acceptance': accepted / len(rows),
            'wrong_wilson_upper_95': upper, 'G_066_DQ_pass': bool(upper <= 0.01),
            'topology_tie_count': sum(int(rep['topology_tie_flag']) for r in rows for rep in r['replicas']),
        }
        raw_manifest.append(str(p.with_name('rows.jsonl')))

    dp_by_cell = {i: [] for i in range(len(CELLS))}
    seen_keys = set()
    for p, meta, rows in recs:
        if meta.get('role') != 'development_primary_shard':
            continue
        cell_i = int(meta.get('cell_index', -1))
        chunk_i = int(meta.get('chunk_index', -1))
        if not (0 <= cell_i < len(CELLS) and 0 <= chunk_i < DP_SHARD_COUNT):
            raise AssertionError('dp_key_bounds')
        key = (cell_i, chunk_i)
        if key in seen_keys:
            raise AssertionError('duplicate_dp_shard')
        seen_keys.add(key)
        start = e66.DEVELOPMENT_PRIMARY_RANGE[0] + DP_SHARD_N * chunk_i
        stop = start + DP_SHARD_N
        if meta.get('seed_range') != [start, stop - 1] or int(meta.get('n', -1)) != DP_SHARD_N:
            raise AssertionError('dp_meta_bounds')
        if int(meta.get('execution_closure_issue', -1)) != EXECUTION_CLOSURE_ISSUE:
            raise AssertionError('dp_execution_identity')
        if [int(r['seed']) for r in rows] != list(range(start, stop)):
            raise AssertionError('dp_shard_coverage')
        cell = CELLS[cell_i]
        for r in rows:
            if r['panel'] != 'DP' or r['cell'] != cell['label']:
                raise AssertionError('dp_row_identity')
            check_primary_row(r, cell)
        dp_by_cell[cell_i].extend(rows)
        raw_manifest.append(str(p.with_name('rows.jsonl')))

    expected_keys = {(c, k) for c in range(len(CELLS)) for k in range(DP_SHARD_COUNT)}
    if seen_keys != expected_keys:
        missing = sorted(expected_keys - seen_keys)
        extra = sorted(seen_keys - expected_keys)
        raise AssertionError(f'dp_shard_set:missing={missing[:10]}:extra={extra[:10]}')

    dp_report = {}
    all_dp = []
    full_start, full_stop = e66.DEVELOPMENT_PRIMARY_RANGE
    for i, cell in enumerate(CELLS):
        rows = sorted(dp_by_cell[i], key=lambda r: int(r['seed']))
        seeds = [int(r['seed']) for r in rows]
        if len(rows) != 2000 or seeds != list(range(full_start, full_stop)) or len(set(seeds)) != 2000:
            raise AssertionError(f'dp_cell_coverage:{i}')
        all_dp.extend(rows)
        accepted = sum(int(r['m1_accept']) for r in rows)
        correct = sum(int(r['m1_correct']) for r in rows)
        wrong = sum(int(r['m1_wrong_accept']) for r in rows)
        precision = correct / accepted if accepted else None
        upper = wilson_upper(wrong, len(rows))
        cell_pass = bool(upper <= 0.01 and (accepted == 0 or precision >= 0.99))
        dp_report[cell['label']] = {
            'n': len(rows), 'accepted_n': accepted, 'correct_n': correct, 'wrong_n': wrong,
            'coverage': accepted / len(rows), 'precision': precision,
            'wrong_acceptance': wrong / len(rows), 'wrong_wilson_upper_95': upper,
            'G_066_cell_pass': cell_pass,
            'a0_accepted_n': sum(int(r['a0_accept']) for r in rows),
            'mean_m1_operational_loss_401_600': sum(float(r['m1_operational_loss_401_600']) for r in rows) / len(rows),
            'mean_a0_operational_loss_401_600': sum(float(r['a0_operational_loss_401_600']) for r in rows) / len(rows),
            'replica_topology_tie_count': sum(int(rep['topology_tie_flag']) for r in rows for rep in r['replicas']),
            'a0_topology_tie_count': sum(int(r['a0_topology_tie_flag']) for r in rows),
        }

    if len(all_dp) != 32000:
        raise AssertionError('dp_paired_draw_count')
    m1_accept = sum(int(r['m1_accept']) for r in all_dp)
    a0_accept = sum(int(r['a0_accept']) for r in all_dp)
    ratio = m1_accept / a0_accept if a0_accept else None
    coverage_pass = bool(a0_accept > 0 and ratio >= 0.90)
    dq_pass = all(v['G_066_DQ_pass'] for v in dq_report.values())
    dp_cells_pass = all(v['G_066_cell_pass'] for v in dp_report.values())
    gate = bool(integrity and dq_pass and dp_cells_pass and coverage_pass)

    report = {
        'experiment': 66, 'phase': 'development',
        'operative_spec_issue': OPERATIVE_SPEC_ISSUE,
        'provenance_closure_issue': PROVENANCE_CLOSURE_ISSUE,
        'preflight_issue': PREFLIGHT_ISSUE,
        'execution_closure_issue': EXECUTION_CLOSURE_ISSUE,
        'integrity_pass': bool(integrity),
        'development_robustness': dq_report,
        'DP': {
            'seed_range': [full_start, full_stop - 1], 'cell_count': len(CELLS),
            'paired_draws': len(all_dp), 'M1_accept_count': m1_accept, 'A0_accept_count': a0_accept,
            'M1_coverage': m1_accept / len(all_dp), 'A0_coverage': a0_accept / len(all_dp),
            'coverage_ratio_M1_over_A0': ratio, 'coverage_ratio_gate_ge_0_90': coverage_pass,
            'extra_M1_confirmation_scalars_per_source_draw': 900,
            'confirmation_replica_count': 5,
            'cells': dp_report,
            'mean_M1_operational_loss_401_600': sum(float(r['m1_operational_loss_401_600']) for r in all_dp) / len(all_dp),
            'mean_A0_operational_loss_401_600': sum(float(r['a0_operational_loss_401_600']) for r in all_dp) / len(all_dp),
            'operational_loss_role': 'descriptive/resource-aware reporting; not a G-066 numerical gate',
        },
        'G_066_pass': gate,
        'interpretation_branch': 'PROCEED_TO_RESERVED_VALIDATION' if gate else 'STOP_NO_VALIDATION',
        'validation_seeds_touched': False,
        'no_tuning': True,
        'raw_manifest': raw_manifest,
    }
    (out / 'development_report.json').write_text(json.dumps(report, indent=2))
    (out / 'decision.txt').write_text('PASS\n' if gate else 'FAIL\n')


if __name__ == '__main__':
    main()
