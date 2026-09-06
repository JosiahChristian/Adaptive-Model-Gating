from __future__ import annotations

import experiment_061 as exp61
import experiment_064 as exp64

OPERATIVE_SPEC_ISSUE = 287
PROVENANCE_CLOSURE_ISSUE = 288
CANDIDATE_ORDER = exp64.CANDIDATE_ORDER
REPLICA_COUNT = 5
REPLICA_SEED_STRIDE = 10_000_000
ALPHA_FAMILYWISE = 0.05
FAMILY_COUNT = 6
ALPHA_FAMILY = ALPHA_FAMILYWISE / FAMILY_COUNT
ERROR_TARGET = 0.01
SCIPY_VERSION = '1.17.0'

CALIBRATION_RANGES = {
    'CQ1': (6800000, 6808000),
    'CQ2': (6808000, 6816000),
    'CQ3': (6816000, 6824000),
    'CQ4': (6824000, 6832000),
    'CQ5': (6832000, 6840000),
    'CQ6': (6840000, 6848000),
}
RESERVED_CONFIRMATION_RANGES = {
    'XQ1': (6848000, 6856000),
    'XQ2': (6856000, 6864000),
    'XQ3': (6864000, 6872000),
    'XQ4': (6872000, 6880000),
    'XQ5': (6880000, 6888000),
    'XQ6': (6888000, 6896000),
}


def q_family(panel: str) -> str:
    if panel.startswith('CQ') or panel.startswith('XQ'):
        q = panel[2:]
    else:
        raise ValueError(panel)
    if q not in {'1','2','3','4','5','6'}:
        raise ValueError(panel)
    return f'Q{q}'


def replica_seed(source_seed: int, replica_index: int) -> int:
    if not 1 <= replica_index <= REPLICA_COUNT:
        raise ValueError(replica_index)
    return int(source_seed) + REPLICA_SEED_STRIDE * replica_index


def external_candidate(source_seed: int, source_start: int) -> str:
    return CANDIDATE_ORDER[(int(source_seed) - int(source_start)) % len(CANDIDATE_ORDER)]


def _tie_flag(scores) -> int:
    vals = [float(scores[h]) for h in CANDIDATE_ORDER]
    m = max(vals)
    return int(sum(int(v == m) for v in vals) > 1)


def confirmation_cube_details(cube):
    mats = {}
    for r in range(1, 6):
        conf = {
            pair: sum(cube[(r, pair)]) / 3.0
            for h in CANDIDATE_ORDER
            for pair in exp64.EDGE_PAIRS[h]
        }
        mats[r] = ({}, conf)
    y_conf, scores_conf, candidate = exp61.confirmation_profile_061(mats)
    if candidate != exp64.confirmation_candidate(cube):
        raise AssertionError('confirmation_candidate_reconstruction')
    return {
        'confirmation_candidate': candidate,
        'confirmation_profile': tuple(float(x) for x in y_conf),
        'confirmation_scores': {h: float(scores_conf[h]) for h in CANDIDATE_ORDER},
        'topology_tie_flag': _tie_flag(scores_conf),
    }


def stress_replica(panel: str, source_seed: int, source_start: int, replica_index: int):
    family = q_family(panel)
    rs = replica_seed(source_seed, replica_index)
    shifted_start = int(source_start) + REPLICA_SEED_STRIDE * replica_index
    generated_candidate, _, cube = exp64.stress_cube(family, rs, shifted_start)
    expected = external_candidate(source_seed, source_start)
    if generated_candidate != expected:
        raise AssertionError('candidate_cycle_mapping')
    return {
        'replica_index': replica_index,
        'replica_seed': rs,
        'discovery_used': False,
        **confirmation_cube_details(cube),
    }


def c1_from_candidates(candidate: str, replica_candidates):
    labels = tuple(replica_candidates)
    if candidate not in CANDIDATE_ORDER:
        raise ValueError(candidate)
    if len(labels) != REPLICA_COUNT:
        raise AssertionError('replica_count')
    if any(c not in CANDIDATE_ORDER for c in labels):
        raise AssertionError('replica_candidate')
    unanimous_match_count = sum(int(c == candidate) for c in labels)
    wrong_accept = int(unanimous_match_count == REPLICA_COUNT)
    return {
        'unanimous_match_count': unanimous_match_count,
        'wrong_accept': wrong_accept,
    }


def evaluate_calibration_draw(panel: str, source_seed: int, source_start: int | None = None):
    ranges = CALIBRATION_RANGES if panel.startswith('CQ') else RESERVED_CONFIRMATION_RANGES
    if panel not in ranges:
        raise ValueError(panel)
    if source_start is None:
        source_start = ranges[panel][0]
    candidate = external_candidate(source_seed, source_start)
    replicas = tuple(stress_replica(panel, source_seed, source_start, j) for j in range(1, REPLICA_COUNT + 1))
    c1 = c1_from_candidates(candidate, [r['confirmation_candidate'] for r in replicas])
    return {
        'panel': panel,
        'seed': int(source_seed),
        'q_family': q_family(panel),
        'source_candidate': candidate,
        'replicas': replicas,
        'unanimous_match_count': c1['unanimous_match_count'],
        'wrong_accept': c1['wrong_accept'],
        'no_tuning': True,
        'calibration_only': True,
    }


def provenance_integrity():
    all_ranges = list(CALIBRATION_RANGES.values()) + list(RESERVED_CONFIRMATION_RANGES.values())
    return all((
        exp61.OPERATIVE_SPEC_ISSUE == 226,
        exp64.OPERATIVE_SPEC_ISSUE == 250,
        exp64.PROVENANCE_CLOSURE_ISSUE == 251,
        exp64.IMPLEMENTATION_CLOSURE_ISSUE == 252,
        CANDIDATE_ORDER == ('H_ab','H_ac','H_bc'),
        REPLICA_COUNT == 5,
        REPLICA_SEED_STRIDE == 10_000_000,
        ALPHA_FAMILYWISE == 0.05,
        FAMILY_COUNT == 6,
        abs(ALPHA_FAMILY - (0.05/6.0)) < 1e-15,
        ERROR_TARGET == 0.01,
        all(stop-start == 8000 for start, stop in all_ranges),
        max(stop for _, stop in CALIBRATION_RANGES.values()) <= min(start for start, _ in RESERVED_CONFIRMATION_RANGES.values()),
        exp64.provenance_integrity(),
    ))
