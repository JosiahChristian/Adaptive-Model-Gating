from __future__ import annotations

import experiment_062 as base

OPERATIVE_SPEC_ISSUE = 241
CONFIRMATION_AGREEMENT_STRATEGY = base.CONFIRMATION_AGREEMENT_STRATEGY
SIGNED_RANK_30_STRATEGY = base.SIGNED_RANK_30_STRATEGY
STRATEGIES = base.STRATEGIES
CONTRAST_COUNT = base.CONTRAST_COUNT
W_CUTOFF = base.W_CUTOFF
P345_NUMERATOR = base.P345_NUMERATOR
P345_DENOMINATOR = base.P345_DENOMINATOR
P345 = base.P345
P344_NUMERATOR = base.P344_NUMERATOR
P344_DENOMINATOR = base.P344_DENOMINATOR
P344 = base.P344
ACCEPT_E = base.ACCEPT_E
PRIMARY_PROBE_ENERGY = base.PRIMARY_PROBE_ENERGY
split_indices_055 = base.split_indices_055
signed_rank_statistic_30 = base.signed_rank_statistic_30

PRIMARY_SEED_START = 71000
PRIMARY_SEED_STOP = 72000
AUDIT_SEEDS = tuple(range(71000, 71005))
BOOTSTRAP_SEED = 63063
BOOTSTRAP_RESAMPLES = 10000
ROBUSTNESS_SEED_RANGES = {
    'R1': (6351000, 6353000),
    'R2': (6353000, 6355000),
    'R3': (6355000, 6357000),
    'R4': (6357000, 6359000),
    'R5': (6359000, 6361000),
    'R6': (6361000, 6363000),
}


def generate_experiment_063_stream(seed, c):
    return base.generate_experiment_062_stream(seed, c)


def infer_confirmation_agreement_063(stream):
    return base.infer_confirmation_agreement_062(stream)


def run_experiment_063_strategy(seed, c, strategy, vals):
    rows = base.run_experiment_062_strategy(seed, c, strategy, vals)
    for row in rows:
        row['experiment063_cell'] = c['label']
        row['experiment063_noise_family'] = c['noise_family']
        row['experiment063_no_tuning'] = 1
        row['experiment063_utility_descriptive_only'] = 1
        row['experiment063_exact_repair_from_062'] = 1
        if strategy == CONFIRMATION_AGREEMENT_STRATEGY:
            row['rank63_spec_issue'] = OPERATIVE_SPEC_ISSUE
            row['rank63_candidate'] = row.get('rank62_candidate', '')
            row['rank63_confirmation_candidate'] = row.get('rank62_confirmation_candidate', '')
            row['rank63_confirmation_agreement'] = row.get('rank62_confirmation_agreement', 0)
            row['rank63_signed_rank_pass'] = row.get('rank62_signed_rank_pass', 0)
            row['rank63_wplus'] = row.get('rank62_wplus', '')
            row['rank63_w_cutoff'] = W_CUTOFF
            row['rank63_contrast_count'] = CONTRAST_COUNT
            row['rank63_no_extra_observations'] = 1
            row['rank63_candidate_reselected'] = 0
            row['rank63_rule'] = 'unchanged replicated repair: deploy iff W+>=345 passes for discovery-selected candidate and confirmation-only topology argmax agrees; agreement is veto-only'
    return rows
