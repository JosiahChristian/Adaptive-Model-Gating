from __future__ import annotations

from statistics import mean

from experiment_055 import W_CUTOFF, signed_rank_statistic_30
from experiment_057 import EDGE_ORDER, _flatten_edge_confirmation, diagnostic_readout, split_contract

OPERATIVE_SPEC_ISSUE = 208
SOURCE_SEED_START = 58000
SOURCE_SEED_STOP = 63000
REPLICA_SEED_OFFSET = 10_000_000
CONTRAST_COUNT = 30
RANDOMIZATION_SEED = 58058
BOOTSTRAP_SEED = 58059
RANDOMIZATION_RESAMPLES = 100_000
BOOTSTRAP_RESAMPLES = 10_000


def replica_seed(source_seed: int) -> int:
    source_seed = int(source_seed)
    rep = source_seed + REPLICA_SEED_OFFSET
    if SOURCE_SEED_START <= rep < SOURCE_SEED_STOP:
        raise AssertionError((source_seed, rep, "replica/source collision"))
    return rep


def _edge_stats(values):
    vals = tuple(float(x) for x in values)
    if len(vals) != CONTRAST_COUNT:
        raise AssertionError(len(vals))
    wplus, ranks = signed_rank_statistic_30(vals)
    return {
        "wplus": int(wplus),
        "reference_accept": int(wplus >= W_CUTOFF),
        "sign_sum": int(sum(1 if x > 0 else -1 for x in vals)),
        "mean": float(mean(vals)),
        "ranks": tuple(int(x) for x in ranks),
    }


def independent_confirmation_readout(source_stream, replica_stream):
    """Frozen diagnostic readout: discovery only from source, confirmation from both streams."""
    source = diagnostic_readout(source_stream)
    selected = source["selected"]
    replica_vectors = {h: _flatten_edge_confirmation(replica_stream, h) for h in EDGE_ORDER}
    replica_stats = {h: _edge_stats(v) for h, v in replica_vectors.items()}
    return {
        "selected": selected,
        "selected_correct": int(selected == "H_ab"),
        "discovery_margin": float(source["discovery_margin"]),
        "discovery_scores": dict(source["discovery_scores"]),
        "source_vectors": dict(source["edge_vectors"]),
        "source_stats": dict(source["edge_stats"]),
        "replica_vectors": replica_vectors,
        "replica_stats": replica_stats,
        "source_selected_wplus": int(source["edge_stats"][selected]["wplus"]),
        "replica_selected_wplus": int(replica_stats[selected]["wplus"]),
        "source_selected_accept": int(source["edge_stats"][selected]["reference_accept"]),
        "replica_selected_accept": int(replica_stats[selected]["reference_accept"]),
    }


def frozen_contract():
    return {
        "operative_spec_issue": OPERATIVE_SPEC_ISSUE,
        "source_seed_range": (SOURCE_SEED_START, SOURCE_SEED_STOP - 1),
        "replica_seed_offset": REPLICA_SEED_OFFSET,
        "w_cutoff_reference_only": W_CUTOFF,
        "contrast_count": CONTRAST_COUNT,
        "randomization_seed": RANDOMIZATION_SEED,
        "randomization_resamples": RANDOMIZATION_RESAMPLES,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
        "split_contract": split_contract(),
        "diagnostic_only": True,
    }
