from __future__ import annotations

import experiment_061 as exp61
import experiment_063 as exp63
import experiment_064 as exp64

OPERATIVE_SPEC_ISSUE = 269
PROVENANCE_CLOSURE_ISSUE = 270
CANDIDATE_ORDER = exp64.CANDIDATE_ORDER
REPLICA_COUNT = 5
REPLICA_SEED_STRIDE = 10_000_000
STRUCTURAL_E_ACCEPT = 243.0
E_THRESHOLD = 100.0

DEVELOPMENT_ROBUSTNESS_RANGES = {
    'DQ1': (6600000, 6602000),
    'DQ2': (6602000, 6604000),
    'DQ3': (6604000, 6606000),
    'DQ4': (6606000, 6608000),
    'DQ5': (6608000, 6610000),
    'DQ6': (6610000, 6612000),
}
DEVELOPMENT_PRIMARY_RANGE = (6612000, 6614000)
VALIDATION_ROBUSTNESS_RANGES = {
    'VQ1': (6614000, 6617000),
    'VQ2': (6617000, 6620000),
    'VQ3': (6620000, 6623000),
    'VQ4': (6623000, 6626000),
    'VQ5': (6626000, 6629000),
    'VQ6': (6629000, 6632000),
}
VALIDATION_PRIMARY_RANGE = (6632000, 6635000)


def q_family(panel: str) -> str:
    if panel.startswith('DQ'):
        q = panel[2:]
    elif panel.startswith('VQ'):
        q = panel[2:]
    else:
        raise ValueError(panel)
    if q not in {'1', '2', '3', '4', '5', '6'}:
        raise ValueError(panel)
    return f'Q{q}'


def replica_seed(source_seed: int, replica_index: int) -> int:
    if not 1 <= replica_index <= REPLICA_COUNT:
        raise ValueError(replica_index)
    return int(source_seed) + REPLICA_SEED_STRIDE * replica_index


def external_candidate(source_seed: int, source_start: int) -> str:
    return CANDIDATE_ORDER[(int(source_seed) - int(source_start)) % len(CANDIDATE_ORDER)]


def _tie_flag(scores) -> int:
    values = [float(scores[h]) for h in CANDIDATE_ORDER]
    maximum = max(values)
    return int(sum(int(v == maximum) for v in values) > 1)


def m1_from_candidates(candidate: str, replica_candidates):
    candidates = tuple(replica_candidates)
    if candidate not in CANDIDATE_ORDER:
        raise ValueError(candidate)
    if len(candidates) != REPLICA_COUNT:
        raise AssertionError('replica_count')
    if any(c not in CANDIDATE_ORDER for c in candidates):
        raise AssertionError('replica_candidate')
    unanimous_n = sum(int(c == candidate) for c in candidates)
    accepted = int(unanimous_n == REPLICA_COUNT)
    e_value = STRUCTURAL_E_ACCEPT if accepted else 0.0
    if int(e_value >= E_THRESHOLD) != accepted:
        raise AssertionError('e_equivalence')
    return {
        'discovery_candidate': candidate,
        'replica_confirmation_candidates': candidates,
        'unanimous_match_count': unanimous_n,
        'm1_accept': accepted,
        'e_value': e_value,
    }


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
    shifted_start = source_start + REPLICA_SEED_STRIDE * replica_index
    generated_candidate, _, cube = exp64.stress_cube(family, rs, shifted_start)
    expected = external_candidate(source_seed, source_start)
    if generated_candidate != expected:
        raise AssertionError('candidate_cycle_mapping')
    detail = confirmation_cube_details(cube)
    return {
        'replica_index': replica_index,
        'replica_seed': rs,
        **detail,
    }


def evaluate_robustness_draw(panel: str, source_seed: int, source_start: int | None = None):
    ranges = DEVELOPMENT_ROBUSTNESS_RANGES if panel.startswith('DQ') else VALIDATION_ROBUSTNESS_RANGES
    if panel not in ranges:
        raise ValueError(panel)
    if source_start is None:
        source_start = ranges[panel][0]
    candidate = external_candidate(source_seed, source_start)
    replicas = tuple(stress_replica(panel, source_seed, source_start, j) for j in range(1, REPLICA_COUNT + 1))
    decision = m1_from_candidates(candidate, [r['confirmation_candidate'] for r in replicas])
    return {
        'panel': panel,
        'seed': int(source_seed),
        'q_family': q_family(panel),
        'discovery_candidate': candidate,
        'replicas': replicas,
        'unanimous_match_count': decision['unanimous_match_count'],
        'm1_accept': decision['m1_accept'],
        'e_value': decision['e_value'],
        'null_panel': True,
        'no_tuning': True,
    }


def primary_confirmation_replica(source_seed: int, cell, replica_index: int):
    rs = replica_seed(source_seed, replica_index)
    stream = exp63.generate_experiment_063_stream(rs, cell)
    mats = {r: exp61.base.response_matrices_055(stream, r) for r in range(1, 6)}
    y_conf, scores_conf, confirmation_candidate = exp61.confirmation_profile_061(mats)
    return {
        'replica_index': replica_index,
        'replica_seed': rs,
        'confirmation_candidate': confirmation_candidate,
        'confirmation_profile': tuple(float(x) for x in y_conf),
        'confirmation_scores': {h: float(scores_conf[h]) for h in CANDIDATE_ORDER},
        'topology_tie_flag': _tie_flag(scores_conf),
        'discovery_used': False,
    }


def primary_m1(source_seed: int, cell, discovery_candidate: str):
    replicas = tuple(primary_confirmation_replica(source_seed, cell, j) for j in range(1, REPLICA_COUNT + 1))
    decision = m1_from_candidates(discovery_candidate, [r['confirmation_candidate'] for r in replicas])
    return {
        'discovery_candidate': discovery_candidate,
        'replicas': replicas,
        'unanimous_match_count': decision['unanimous_match_count'],
        'm1_accept': decision['m1_accept'],
        'e_value': decision['e_value'],
    }


def provenance_integrity():
    return all((
        exp61.OPERATIVE_SPEC_ISSUE == 226,
        exp63.OPERATIVE_SPEC_ISSUE == 241,
        exp64.OPERATIVE_SPEC_ISSUE == 250,
        exp64.PROVENANCE_CLOSURE_ISSUE == 251,
        exp64.IMPLEMENTATION_CLOSURE_ISSUE == 252,
        CANDIDATE_ORDER == ('H_ab', 'H_ac', 'H_bc'),
        REPLICA_COUNT == 5,
        REPLICA_SEED_STRIDE == 10_000_000,
        3 ** REPLICA_COUNT == 243,
        1.0 / 243.0 <= 0.01,
        1.0 / 81.0 > 0.01,
        STRUCTURAL_E_ACCEPT == 243.0,
        E_THRESHOLD == 100.0,
        exp64.provenance_integrity(),
    ))
