from __future__ import annotations

import experiment_066 as exp66
from experiment_046 import cell as base_cell

OPERATIVE_SPEC_ISSUE = 301
CANDIDATE_ORDER = exp66.CANDIDATE_ORDER
REPLICA_COUNT = 5
REPLICA_SEED_STRIDE = 10_000_000
PRECISION_TARGET = 0.99
WRONG_ACCEPT_WILSON_TARGET = 0.01
WILSON_ALPHA = 0.05
COVERAGE_TARGET = 0.90
DEVELOPMENT_RANGE = (7_000_000, 7_004_000)
VALIDATION_RANGE = (7_004_000, 7_008_000)
DEVELOPMENT_N_PER_CELL = 4000
VALIDATION_N_PER_CELL = 4000

# Deterministic one-level extensions of the existing Experiment 046/051
# gain and noise-scale axes. The generator itself is unchanged.
SHIFTED_GAIN = 0.350
SHIFTED_NOISE_SCALE = 2.00
NOISE_FAMILIES = ('gaussian', 'laplace', 'student_t3', 'contaminated_gaussian')


def shifted_cells():
    out = []
    for nf in NOISE_FAMILIES:
        out.append(base_cell(f'{nf}_g{SHIFTED_GAIN:.3f}_n1.50', nf, SHIFTED_GAIN, 1.50))
        out.append(base_cell(f'{nf}_g0.425_n{SHIFTED_NOISE_SCALE:.2f}', nf, 0.425, SHIFTED_NOISE_SCALE))
        out.append(base_cell(f'{nf}_g{SHIFTED_GAIN:.3f}_n{SHIFTED_NOISE_SCALE:.2f}', nf, SHIFTED_GAIN, SHIFTED_NOISE_SCALE))
    if len(out) != 12 or len({c['label'] for c in out}) != 12:
        raise AssertionError('shifted_cell_identity')
    return tuple(out)


CELLS = shifted_cells()


def c1_primary(source_seed: int, cell, discovery_candidate: str):
    m1 = exp66.primary_m1(source_seed, cell, discovery_candidate)
    if any(r.get('discovery_used') is not False for r in m1['replicas']):
        raise AssertionError('replica_discovery_leakage')
    return m1


def provenance_integrity():
    return all((
        exp66.OPERATIVE_SPEC_ISSUE == 269,
        exp66.PROVENANCE_CLOSURE_ISSUE == 270,
        CANDIDATE_ORDER == ('H_ab', 'H_ac', 'H_bc'),
        REPLICA_COUNT == exp66.REPLICA_COUNT == 5,
        REPLICA_SEED_STRIDE == exp66.REPLICA_SEED_STRIDE == 10_000_000,
        len(CELLS) == 12,
        DEVELOPMENT_RANGE[1] - DEVELOPMENT_RANGE[0] == DEVELOPMENT_N_PER_CELL,
        VALIDATION_RANGE[1] - VALIDATION_RANGE[0] == VALIDATION_N_PER_CELL,
        DEVELOPMENT_RANGE[1] <= VALIDATION_RANGE[0],
        PRECISION_TARGET == 0.99,
        WRONG_ACCEPT_WILSON_TARGET == 0.01,
        WILSON_ALPHA == 0.05,
        COVERAGE_TARGET == 0.90,
        all(c['topology_truth'] == 'H_ab' and c['family'] == 'drift_ab_fault' and c['magnitude'] == 0.50 for c in CELLS),
        exp66.provenance_integrity(),
    ))
