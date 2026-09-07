from __future__ import annotations

import experiment_068 as exp68
import experiment_066 as exp66
from experiment_051 import CELLS

OPERATIVE_SPEC_ISSUE = 292
PROVENANCE_CLOSURE_ISSUE = 293
CANDIDATE_ORDER = exp68.CANDIDATE_ORDER
REPLICA_COUNT = 5
REPLICA_SEED_STRIDE = 10_000_000
XQ_RANGES = dict(exp68.RESERVED_CONFIRMATION_RANGES)
PRIMARY_RANGE = (6_900_000, 6_904_000)
PRIMARY_CELL_COUNT = 16
SCIPY_VERSION = '1.17.0'
ALPHA_FAMILY = 0.05 / 6.0
ERROR_TARGET = 0.01
PRECISION_TARGET = 0.99
PRIMARY_WILSON_ALPHA = 0.05
COVERAGE_TARGET = 0.90


def evaluate_xq_draw(panel: str, source_seed: int):
    if panel not in XQ_RANGES:
        raise ValueError(panel)
    start, stop = XQ_RANGES[panel]
    if not start <= source_seed < stop:
        raise ValueError(source_seed)
    return exp68.evaluate_calibration_draw(panel, source_seed, start)


def c1_primary(source_seed: int, cell, discovery_candidate: str):
    m1 = exp66.primary_m1(source_seed, cell, discovery_candidate)
    if any(r.get('discovery_used') is not False for r in m1['replicas']):
        raise AssertionError('replica_discovery_leakage')
    return m1


def provenance_integrity():
    return all((
        exp68.OPERATIVE_SPEC_ISSUE == 287,
        exp68.PROVENANCE_CLOSURE_ISSUE == 288,
        exp66.OPERATIVE_SPEC_ISSUE == 269,
        exp66.PROVENANCE_CLOSURE_ISSUE == 270,
        CANDIDATE_ORDER == ('H_ab','H_ac','H_bc'),
        REPLICA_COUNT == exp66.REPLICA_COUNT == exp68.REPLICA_COUNT == 5,
        REPLICA_SEED_STRIDE == exp66.REPLICA_SEED_STRIDE == exp68.REPLICA_SEED_STRIDE == 10_000_000,
        len(CELLS) == PRIMARY_CELL_COUNT,
        PRIMARY_RANGE[1] - PRIMARY_RANGE[0] == 4000,
        all(stop-start == 8000 for start,stop in XQ_RANGES.values()),
        abs(ALPHA_FAMILY - 0.05/6.0) < 1e-15,
        ERROR_TARGET == 0.01,
        PRECISION_TARGET == 0.99,
        PRIMARY_WILSON_ALPHA == 0.05,
        COVERAGE_TARGET == 0.90,
        exp68.provenance_integrity(),
    ))
