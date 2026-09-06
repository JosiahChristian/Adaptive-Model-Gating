from __future__ import annotations

import experiment_061 as exp61
import experiment_064 as exp64

OPERATIVE_SPEC_ISSUE = 279
PROVENANCE_CLOSURE_ISSUE = 280
CANDIDATE_ORDER = exp64.CANDIDATE_ORDER
REPLICA_COUNT = 5
REPLICA_SEED_STRIDE = 10_000_000

DEVELOPMENT_RANGES = {
    'ZQ1': (6700000, 6704000),
    'ZQ2': (6704000, 6708000),
    'ZQ3': (6708000, 6712000),
    'ZQ4': (6712000, 6716000),
    'ZQ5': (6716000, 6720000),
    'ZQ6': (6720000, 6724000),
}
RESERVED_REPLICATION_RANGES = {
    'RQ1': (6724000, 6728000),
    'RQ2': (6728000, 6732000),
    'RQ3': (6732000, 6736000),
    'RQ4': (6736000, 6740000),
    'RQ5': (6740000, 6744000),
    'RQ6': (6744000, 6748000),
}


def q_family(panel: str) -> str:
    if panel.startswith('ZQ') or panel.startswith('RQ'):
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
    shifted_start = source_start + REPLICA_SEED_STRIDE * replica_index
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


def evaluate_diagnostic_draw(panel: str, source_seed: int, source_start: int | None = None):
    ranges = DEVELOPMENT_RANGES if panel.startswith('ZQ') else RESERVED_REPLICATION_RANGES
    if panel not in ranges:
        raise ValueError(panel)
    if source_start is None:
        source_start = ranges[panel][0]
    candidate = external_candidate(source_seed, source_start)
    replicas = tuple(stress_replica(panel, source_seed, source_start, j) for j in range(1, REPLICA_COUNT + 1))
    return {
        'panel': panel,
        'seed': int(source_seed),
        'q_family': q_family(panel),
        'source_candidate': candidate,
        'replicas': replicas,
        'no_tuning': True,
        'diagnostic_only': True,
    }


def provenance_integrity():
    return all((
        exp61.OPERATIVE_SPEC_ISSUE == 226,
        exp64.OPERATIVE_SPEC_ISSUE == 250,
        exp64.PROVENANCE_CLOSURE_ISSUE == 251,
        exp64.IMPLEMENTATION_CLOSURE_ISSUE == 252,
        CANDIDATE_ORDER == ('H_ab','H_ac','H_bc'),
        REPLICA_COUNT == 5,
        REPLICA_SEED_STRIDE == 10_000_000,
        all(stop-start == 4000 for start, stop in DEVELOPMENT_RANGES.values()),
        all(stop-start == 4000 for start, stop in RESERVED_REPLICATION_RANGES.values()),
        exp64.provenance_integrity(),
    ))
