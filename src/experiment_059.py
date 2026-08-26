from __future__ import annotations

import experiment_055 as base

OPERATIVE_SPEC_ISSUE = 215
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


def configure():
    # Branch-C confirmatory replication after Experiment 058: inherit the
    # Experiment 055/056 scientific architecture unchanged. Only provenance
    # and prospectively reserved fresh seeds change in the evaluator wrapper.
    base.OPERATIVE_SPEC_ISSUE = OPERATIVE_SPEC_ISSUE


def generate_experiment_059_stream(seed, c):
    configure()
    return base.generate_experiment_055_stream(seed, c)


def run_experiment_059_strategy(seed, c, strategy, vals):
    configure()
    rows = base.run_experiment_055_strategy(seed, c, strategy, vals)
    for row in rows:
        row['experiment059_cell'] = c['label']
        row['experiment059_noise_family'] = c['noise_family']
        row['experiment059_no_tuning'] = 1
        row['experiment059_confirmatory_replication'] = 1
    return rows
