#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'scripts'))

import experiment_061 as e61
import experiment_066 as e66
from experiment_051 import CELLS
from run_experiment_055 import calibration_values

CONFIRMATION_SCALARS_PER_REPLICA = 180
EXTRA_M1_CONFIRMATION_SCALARS = e66.REPLICA_COUNT * CONFIRMATION_SCALARS_PER_REPLICA


def _operational_loss(rows):
    return sum(float(r['sq_error']) for r in rows if 401 <= int(r['t']) <= 600)


def _primary_one(seed, c):
    source_stream = e61.generate_experiment_061_stream(seed, c)
    groups_a0, a0_accept, _, _, path, _, _, _, y_conf, scores_conf = e61.infer_confirmation_agreement_061(source_stream)
    candidate = path[0]['candidate']
    confirmation_candidate = path[0]['confirmation_candidate']
    if candidate not in e66.CANDIDATE_ORDER or confirmation_candidate not in e66.CANDIDATE_ORDER:
        raise AssertionError('source_candidate')

    source_contrasts = tuple(float(x) for row in path for x in row['pairwise_responses'])
    if len(source_contrasts) != 30:
        raise AssertionError('a0_contrast_count')
    reconstructed_wplus, reconstructed_ranks = e61.base.signed_rank_statistic_30(source_contrasts)
    if reconstructed_wplus != path[-1]['wplus'] or tuple(reconstructed_ranks) != tuple(path[-1]['ranks']):
        raise AssertionError('a0_rank_reconstruction')
    source_topology_scores = {h: float(scores_conf[h]) for h in e66.CANDIDATE_ORDER}
    reconstructed_confirmation = max(e66.CANDIDATE_ORDER, key=lambda h: (source_topology_scores[h], -e66.CANDIDATE_ORDER.index(h)))
    if reconstructed_confirmation != confirmation_candidate:
        raise AssertionError('a0_topology_reconstruction')
    reconstructed_a0 = int(reconstructed_wplus >= e61.W_CUTOFF and confirmation_candidate == candidate)
    if reconstructed_a0 != int(a0_accept):
        raise AssertionError('a0_accept_reconstruction')

    m1 = e66.primary_m1(seed, c, candidate)
    if any(r['discovery_used'] is not False for r in m1['replicas']):
        raise AssertionError('replica_discovery_leakage')

    candidate_groups = e61.base.groups_from_edges([e61.base.HYP_EDGE[candidate]])
    if a0_accept and groups_a0 != candidate_groups:
        raise AssertionError('a0_groups_reconstruction')

    vals = calibration_values()
    tau, _, k3, la, lb, lc, lab, lac, lbc, *_ = vals

    # Both source-stream policies are evaluated for every seed regardless of
    # M1/A0 decisions; decisions merely select a precomputed policy loss.
    fallback_rows = e61.base.run_triad_persistence_on_stream(
        seed, f'experiment066_fallback_{c["label"]}', tau, k3, source_stream
    )
    deploy_rows = e61.base._run_composed_gate(
        seed, f'experiment066_deploy_{c["label"]}', tau, k3,
        la, lb, lc, lab, lac, lbc, source_stream, {}, candidate_groups
    )
    fallback_loss = _operational_loss(fallback_rows)
    deploy_loss = _operational_loss(deploy_rows)

    m1_accept = int(m1['m1_accept'])
    a0_accept = int(a0_accept)
    truth = c['topology_truth']
    candidate_correct = int(candidate == truth)
    m1_correct = int(m1_accept and candidate_correct)
    a0_correct = int(a0_accept and candidate_correct)
    source_max = max(source_topology_scores.values())
    source_tie = int(sum(int(v == source_max) for v in source_topology_scores.values()) > 1)

    return {
        'panel': 'DP',
        'seed': int(seed),
        'cell': c['label'],
        'topology_truth': truth,
        'discovery_candidate': candidate,
        'candidate_correct': candidate_correct,
        'm1_accept': m1_accept,
        'm1_correct': m1_correct,
        'm1_wrong_accept': int(m1_accept and not candidate_correct),
        'm1_e_value': float(m1['e_value']),
        'unanimous_match_count': int(m1['unanimous_match_count']),
        'replicas': m1['replicas'],
        'a0_accept': a0_accept,
        'a0_correct': a0_correct,
        'a0_wrong_accept': int(a0_accept and not candidate_correct),
        'a0_wplus': int(reconstructed_wplus),
        'a0_w_cutoff': int(e61.W_CUTOFF),
        'a0_pairwise_confirmation': source_contrasts,
        'a0_ranks': tuple(int(x) for x in reconstructed_ranks),
        'a0_confirmation_candidate': confirmation_candidate,
        'a0_confirmation_profile': tuple(float(x) for x in y_conf),
        'a0_confirmation_scores': source_topology_scores,
        'a0_topology_tie_flag': source_tie,
        'a0_topology_agreement': int(confirmation_candidate == candidate),
        'fallback_operational_loss_401_600': fallback_loss,
        'deploy_candidate_operational_loss_401_600': deploy_loss,
        'm1_operational_loss_401_600': deploy_loss if m1_accept else fallback_loss,
        'a0_operational_loss_401_600': deploy_loss if a0_accept else fallback_loss,
        'confirmation_replica_count': e66.REPLICA_COUNT,
        'confirmation_scalars_per_replica': CONFIRMATION_SCALARS_PER_REPLICA,
        'extra_m1_confirmation_scalars': EXTRA_M1_CONFIRMATION_SCALARS,
        'source_discovery_stream_shared_with_a0': True,
        'replica_discovery_used': False,
        'no_tuning': True,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--panel')
    ap.add_argument('--cell-index', type=int)
    ap.add_argument('--seed-start', type=int)
    ap.add_argument('--seed-stop', type=int)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    if not e66.provenance_integrity():
        raise AssertionError('provenance_integrity')

    if a.panel:
        if any(x is not None for x in (a.cell_index, a.seed_start, a.seed_stop)):
            raise ValueError('panel mode forbids primary arguments')
        if a.panel not in e66.DEVELOPMENT_ROBUSTNESS_RANGES:
            raise ValueError(a.panel)
        start, stop = e66.DEVELOPMENT_ROBUSTNESS_RANGES[a.panel]
        rows = [e66.evaluate_robustness_draw(a.panel, seed, start) for seed in range(start, stop)]
        if [r['seed'] for r in rows] != list(range(start, stop)) or len(rows) != 2000:
            raise AssertionError('dq_coverage')
        meta = {
            'experiment': 66, 'role': 'development_robustness', 'panel': a.panel,
            'seed_range': [start, stop - 1], 'n': len(rows),
            'replica_count': 5, 'operative_spec_issue': 269,
            'provenance_closure_issue': 270, 'preflight_issue': 271,
            'null_panel': True, 'validation_seeds_touched': False, 'no_tuning': True,
        }
    else:
        if a.cell_index is None or not 0 <= a.cell_index < len(CELLS):
            raise ValueError('cell-index')
        if a.seed_start is None or a.seed_stop is None:
            raise ValueError('seed-start/seed-stop required')
        full_start, full_stop = e66.DEVELOPMENT_PRIMARY_RANGE
        start, stop = int(a.seed_start), int(a.seed_stop)
        if not (full_start <= start < stop <= full_stop):
            raise ValueError('development primary seed range')
        c = CELLS[a.cell_index]
        rows = [_primary_one(seed, c) for seed in range(start, stop)]
        if [r['seed'] for r in rows] != list(range(start, stop)) or len(rows) != stop - start:
            raise AssertionError('dp_shard_coverage')
        if any(r['cell'] != c['label'] or r['replica_discovery_used'] is not False for r in rows):
            raise AssertionError('dp_identity')
        meta = {
            'experiment': 66, 'role': 'development_primary_shard',
            'cell_index': a.cell_index, 'cell': c['label'],
            'seed_range': [start, stop - 1], 'n': len(rows),
            'paired_m1_a0': True, 'replica_count': 5,
            'extra_m1_confirmation_scalars_per_source_draw': EXTRA_M1_CONFIRMATION_SCALARS,
            'operative_spec_issue': 269, 'provenance_closure_issue': 270,
            'preflight_issue': 271, 'validation_seeds_touched': False, 'no_tuning': True,
        }

    with (out / 'rows.jsonl').open('w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, separators=(',', ':')) + '\n')
    (out / 'meta.json').write_text(json.dumps(meta, indent=2))


if __name__ == '__main__':
    main()
