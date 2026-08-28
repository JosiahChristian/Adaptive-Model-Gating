from __future__ import annotations

import experiment_064 as exp64

OPERATIVE_SPEC_ISSUE = 258
PROVENANCE_CLOSURE_ISSUE = 259
ARCHITECTURES = exp64.ARCHITECTURES
CANDIDATE_ORDER = exp64.CANDIDATE_ORDER

DEVELOPMENT_ROBUSTNESS_RANGES = {
    'DQ1': (6500000, 6502000),
    'DQ2': (6502000, 6504000),
    'DQ3': (6504000, 6506000),
    'DQ4': (6506000, 6508000),
    'DQ5': (6508000, 6510000),
    'DQ6': (6510000, 6512000),
}
DEVELOPMENT_PRIMARY_RANGE = (6512000, 6514000)
VALIDATION_ROBUSTNESS_RANGES = {
    'VQ1': (6514000, 6517000),
    'VQ2': (6517000, 6520000),
    'VQ3': (6520000, 6523000),
    'VQ4': (6523000, 6526000),
    'VQ5': (6526000, 6529000),
    'VQ6': (6529000, 6532000),
}
VALIDATION_PRIMARY_RANGE = (6532000, 6535000)


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


def m0_from_cube(candidate, vectors, cube):
    confirmation_candidate = exp64.confirmation_candidate(cube)
    agreement = int(candidate == confirmation_candidate)
    underlying = {}
    details = {}
    for architecture in ARCHITECTURES:
        decision, detail = exp64._underlying_accept(architecture, candidate, vectors, cube)
        underlying[architecture] = int(decision)
        details[architecture] = detail
    all_four_accept = int(all(underlying[a] == 1 for a in ARCHITECTURES))
    m0_accept = int(all_four_accept and agreement)
    return {
        'discovery_candidate': candidate,
        'confirmation_candidate': confirmation_candidate,
        'topology_agreement': agreement,
        'underlying_accept': underlying,
        'underlying_detail': details,
        'all_four_accept': all_four_accept,
        'm0_accept': m0_accept,
    }


def evaluate_robustness_draw(panel: str, seed: int, start: int | None = None):
    family = q_family(panel)
    if start is None:
        ranges = DEVELOPMENT_ROBUSTNESS_RANGES if panel.startswith('DQ') else VALIDATION_ROBUSTNESS_RANGES
        start = ranges[panel][0]
    candidate, vectors, cube = exp64.stress_cube(family, seed, start)
    row = m0_from_cube(candidate, vectors, cube)
    row.update({'panel': panel, 'seed': seed, 'q_family': family})
    return row


def provenance_integrity():
    return all((
        exp64.OPERATIVE_SPEC_ISSUE == 250,
        exp64.PROVENANCE_CLOSURE_ISSUE == 251,
        exp64.IMPLEMENTATION_CLOSURE_ISSUE == 252,
        exp64.ARCHITECTURES == ('A0', 'A1', 'A2', 'A3'),
        exp64.W_CUTOFF == 345,
        exp64.provenance_integrity(),
    ))
