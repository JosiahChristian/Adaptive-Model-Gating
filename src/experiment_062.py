from __future__ import annotations

import experiment_061 as base

OPERATIVE_SPEC_ISSUE = 235
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


def generate_experiment_062_stream(seed, c):
    return base.generate_experiment_061_stream(seed, c)


def infer_confirmation_agreement_062(stream):
    return base.infer_confirmation_agreement_061(stream)


def run_experiment_062_strategy(seed, c, strategy, vals):
    rows = base.run_experiment_061_strategy(seed, c, strategy, vals)
    for row in rows:
        row['experiment062_cell'] = c['label']
        row['experiment062_noise_family'] = c['noise_family']
        row['experiment062_no_tuning'] = 1
        row['experiment062_exact_replication_of_061'] = 1
        if strategy == CONFIRMATION_AGREEMENT_STRATEGY:
            row['rank62_spec_issue'] = OPERATIVE_SPEC_ISSUE
            row['rank62_candidate'] = row.get('rank61_candidate', '')
            row['rank62_confirmation_candidate'] = row.get('rank61_confirmation_candidate', '')
            row['rank62_confirmation_agreement'] = row.get('rank61_confirmation_agreement', 0)
            row['rank62_signed_rank_pass'] = row.get('rank61_signed_rank_pass', 0)
            row['rank62_wplus'] = row.get('rank61_wplus', '')
            row['rank62_w_cutoff'] = W_CUTOFF
            row['rank62_contrast_count'] = CONTRAST_COUNT
            row['rank62_no_extra_observations'] = 1
            row['rank62_candidate_reselected'] = 0
            row['rank62_rule'] = 'exact replication of Experiment 061: deploy iff unchanged W+>=345 passes and confirmation-only topology argmax agrees; agreement is veto-only'
    return rows
