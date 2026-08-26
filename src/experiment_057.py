from __future__ import annotations

from itertools import product
from statistics import mean

from experiment_047 import HYP_EDGE, discovery_profile
from experiment_055 import (
    W_CUTOFF,
    response_matrices_055,
    pairwise_confirmation_055,
    signed_rank_statistic_30,
    split_indices_055,
)

OPERATIVE_SPEC_ISSUE = 202
EDGE_ORDER = ("H_ab", "H_ac", "H_bc")
CONTRAST_COUNT = 30
ROUND_COUNT = 5
CONTRASTS_PER_ROUND = 6


def _flatten_edge_confirmation(stream, edge_name):
    edge = HYP_EDGE[edge_name]
    values = []
    for r in range(1, ROUND_COUNT + 1):
        pairs = pairwise_confirmation_055(stream, r, edge)
        flat = tuple(x for pair in pairs for x in pair)
        if len(flat) != CONTRASTS_PER_ROUND:
            raise AssertionError((edge_name, r, len(flat)))
        values.extend(float(x) for x in flat)
    if len(values) != CONTRAST_COUNT:
        raise AssertionError((edge_name, len(values)))
    return tuple(values)


def diagnostic_readout(stream):
    """Return frozen Experiment 057 diagnostic quantities without changing deployment."""
    mats = {r: response_matrices_055(stream, r) for r in range(1, ROUND_COUNT + 1)}
    y, scores, selected = discovery_profile(mats)
    if selected not in EDGE_ORDER:
        raise AssertionError(selected)
    ordered_scores = sorted((float(v), h) for h, v in scores.items())
    margin = ordered_scores[-1][0] - ordered_scores[-2][0]
    edge_vectors = {h: _flatten_edge_confirmation(stream, h) for h in EDGE_ORDER}
    edge_stats = {}
    for h, values in edge_vectors.items():
        wplus, ranks = signed_rank_statistic_30(values)
        edge_stats[h] = {
            "wplus": int(wplus),
            "reference_accept": int(wplus >= W_CUTOFF),
            "sign_sum": int(sum(1 if x > 0 else -1 for x in values)),
            "mean": float(mean(values)),
            "ranks": tuple(int(x) for x in ranks),
        }
    cyclic = EDGE_ORDER[(EDGE_ORDER.index(selected) + 1) % len(EDGE_ORDER)]
    return {
        "selected": selected,
        "cyclic_control": cyclic,
        "discovery_margin": float(margin),
        "discovery_scores": {h: float(scores[h]) for h in EDGE_ORDER},
        "edge_vectors": edge_vectors,
        "edge_stats": edge_stats,
        "selected_wplus": edge_stats[selected]["wplus"],
        "selected_reference_accept": edge_stats[selected]["reference_accept"],
        "cyclic_reference_accept": edge_stats[cyclic]["reference_accept"],
    }


def round_block_randomization(values):
    """Enumerate all 2^5 round-block sign flips; diagnostic only."""
    vals = tuple(float(x) for x in values)
    if len(vals) != CONTRAST_COUNT:
        raise AssertionError(len(vals))
    observed, _ = signed_rank_statistic_30(vals)
    exceed = 0
    stats = []
    for signs in product((-1.0, 1.0), repeat=ROUND_COUNT):
        flipped = []
        for r, s in enumerate(signs):
            lo = r * CONTRASTS_PER_ROUND
            hi = lo + CONTRASTS_PER_ROUND
            flipped.extend(s * x for x in vals[lo:hi])
        wplus, _ = signed_rank_statistic_30(flipped)
        stats.append(int(wplus))
        exceed += int(wplus >= observed)
    return {
        "observed_wplus": int(observed),
        "tail_numerator": int(exceed),
        "tail_denominator": 2 ** ROUND_COUNT,
        "tail": float(exceed / (2 ** ROUND_COUNT)),
        "minimum_attainable_tail": float(1 / (2 ** ROUND_COUNT)),
        "reference_accept": int(observed >= W_CUTOFF),
        "block_tail_le_0_01": bool(exceed / (2 ** ROUND_COUNT) <= 0.01),
        "enumerated_wplus": tuple(stats),
    }


def split_contract():
    out = {}
    for r in range(1, ROUND_COUNT + 1):
        target, (bd, bc) = split_indices_055(r)
        if len(bd) != 1 or len(bc) != 3 or set(bd) & set(bc):
            raise AssertionError((r, bd, bc))
        for tgt, (td, tc) in target.items():
            if len(td) != 2 or len(tc) != 3 or set(td) & set(tc):
                raise AssertionError((r, tgt, td, tc))
        out[r] = {"baseline_discovery": tuple(bd), "baseline_confirmation": tuple(bc), "target": target}
    return out
