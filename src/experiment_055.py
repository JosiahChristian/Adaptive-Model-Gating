from __future__ import annotations
from statistics import mean

from experiment_010 import run_triad_persistence_on_stream
from experiment_016 import groups_from_edges
from experiment_018 import ALL_AMPLITUDES, ROUND5_BLOCKS
from experiment_028 import VECTOR
from experiment_032 import _run_composed_gate
from experiment_046 import E_THRESHOLD, BASELINE_SLICES, _target_blocks
from experiment_047 import AMP_DENOM, HYP_EDGE, discovery_profile
from experiment_054 import STRATEGIES as EXP054_STRATEGIES, generate_experiment_054_stream, run_experiment_054_strategy

OPERATIVE_SPEC_ISSUE = 190
SIGNED_RANK_30_STRATEGY = 'covariance_matched_discovery_30contrast_exact_signed_rank_context_composed_risk_gate'
STRATEGIES = (SIGNED_RANK_30_STRATEGY,) + EXP054_STRATEGIES
CONTRAST_COUNT = 30
W_CUTOFF = 345
P345_NUMERATOR = 10555320
P345_DENOMINATOR = 1073741824
P345 = P345_NUMERATOR / P345_DENOMINATOR
P344_NUMERATOR = 11193679
P344_DENOMINATOR = 1073741824
P344 = P344_NUMERATOR / P344_DENOMINATOR
ACCEPT_E = 1.0 / P345
PRIMARY_PROBE_ENERGY = sum(15.0 * (float(a) ** 2) for a in ALL_AMPLITUDES)


def generate_experiment_055_stream(seed, c):
    return generate_experiment_054_stream(seed, c)


def split_indices_055(r):
    blocks = _target_blocks(r)
    b = tuple(BASELINE_SLICES[r])
    target = {k: (tuple(ts)[:2], tuple(ts)[2:]) for k, ts in blocks.items()}
    return target, (b[:1], b[1:])


def response_matrices_055(stream, r):
    target, (bd, bc) = split_indices_055(r)
    if len(bd) != 1 or len(bc) != 3:
        raise AssertionError((r, bd, bc))
    disc = {}
    conf = {}
    for obs in 'abc':
        base_d = mean(float(stream[f'probe_obs_{obs}'][t]) for t in bd)
        base_c = mean(float(stream[f'probe_obs_{obs}'][t]) for t in bc)
        for tgt, (td, tc) in target.items():
            if len(td) != 2 or len(tc) != 3:
                raise AssertionError((r, tgt, td, tc))
            disc[(obs, tgt)] = mean(float(stream[f'probe_obs_{obs}'][t]) for t in td) - base_d
            conf[(obs, tgt)] = mean(float(stream[f'probe_obs_{obs}'][t]) for t in tc) - base_c
    return disc, conf


def pairwise_confirmation_055(stream, r, edge):
    target, (bd, bc) = split_indices_055(r)
    if len(bc) != 3:
        raise AssertionError((r, bc))
    out = []
    for obs, tgt in (edge, (edge[1], edge[0])):
        tc = target[tgt][1]
        if len(tc) != 3:
            raise AssertionError((r, tgt, tc))
        vals = tuple(float(stream[f'probe_obs_{obs}'][tc[k]]) - float(stream[f'probe_obs_{obs}'][bc[k]]) for k in range(3))
        out.append(vals)
    return tuple(out)


def signed_rank_statistic_30(values):
    vals = tuple(float(x) for x in values)
    if len(vals) != CONTRAST_COUNT:
        raise AssertionError(len(vals))
    if any(x == 0.0 for x in vals):
        raise AssertionError('zero confirmation contrast')
    absvals = [abs(x) for x in vals]
    if len(set(absvals)) != CONTRAST_COUNT:
        raise AssertionError('tied absolute confirmation contrasts')
    order = sorted(range(CONTRAST_COUNT), key=lambda i: absvals[i])
    ranks = [0] * CONTRAST_COUNT
    for rank, i in enumerate(order, 1):
        ranks[i] = rank
    wplus = sum(ranks[i] for i, x in enumerate(vals) if x > 0.0)
    return wplus, tuple(ranks)


def infer_30contrast_exact_signed_rank(stream):
    mats = {r: response_matrices_055(stream, r) for r in range(1, 6)}
    y, scores, candidate = discovery_profile(mats)
    edge = HYP_EDGE[candidate]
    path = []
    all_values = []
    for r in range(1, 6):
        pairs = pairwise_confirmation_055(stream, r, edge)
        flat = tuple(x for pair in pairs for x in pair)
        all_values.extend(flat)
        E = 0.0
        wplus = ''
        ranks = ()
        if r == 5:
            wplus, ranks = signed_rank_statistic_30(all_values)
            E = ACCEPT_E if wplus >= W_CUTOFF else 0.0
        path.append({'stage': r, 'candidate': candidate, 'e_value': E, 'pairwise_responses': flat, 'wplus': wplus, 'ranks': ranks})
    final = path[-1]['e_value']
    accepted = int(final >= E_THRESHOLD)
    return (groups_from_edges([edge]) if accepted else None), accepted, 1 - accepted, 5, path, mats, y, scores


def _annotation(stream, accepted, abstain, path, mats, y, scores):
    cand = path[0]['candidate']
    final = path[-1]['e_value']
    wplus = path[-1]['wplus']
    out = {
        'probe_gain': stream['probe_gain'], 'probe_stop_round': 5 if accepted else 0,
        'probe_energy': PRIMARY_PROBE_ENERGY, 'probe_block_count': 15,
        'probe_max_amplitude': float(max(ALL_AMPLITUDES)), 'provenance_accepted': accepted,
        'provenance_abstain': abstain, 'posterior_deploy_hypothesis': cand if accepted else '',
        'posterior_at_deployment': '', 'posterior_implied_error_risk': '', 'posterior_expected_wrong_action_loss': '',
        'rank55_candidate': cand, 'rank55_e_threshold': E_THRESHOLD, 'rank55_e_final': final,
        'rank55_discovery_acceptance': 0, 'rank55_candidate_reselected': 0, 'rank55_spec_issue': OPERATIVE_SPEC_ISSUE,
        'rank55_rule': 'Experiment-047 discovery with baseline 1/3 reallocation; 30 disjoint primary-stream contrasts; exact one-sided Wilcoxon signed-rank W+>=345',
        'rank55_amp_denom': AMP_DENOM, 'rank55_contrast_count': CONTRAST_COUNT,
        'rank55_w_cutoff': W_CUTOFF, 'rank55_wplus': wplus,
        'rank55_p345_numerator': P345_NUMERATOR, 'rank55_p345_denominator': P345_DENOMINATOR, 'rank55_p345': P345,
        'rank55_p344_numerator': P344_NUMERATOR, 'rank55_p344_denominator': P344_DENOMINATOR, 'rank55_p344': P344,
        'rank55_accept_e': ACCEPT_E,
        'rank55_validity_model': 'independent continuous symmetric confirmation contrasts conditional on discovery and absolute magnitudes',
        'rank55_no_extra_observations': 1, 'rank55_no_replicate': 1,
    }
    for pair, val in zip(VECTOR, y):
        out['rank55_Y_' + ''.join(pair)] = val
    for h, v in scores.items():
        out['rank55_Q_' + h] = v
    all_values = []
    for r in range(1, 6):
        target, (bd, bc) = split_indices_055(r)
        out[f'rank55_baseline_discovery_r{r}'] = ','.join(map(str, bd))
        out[f'rank55_baseline_confirmation_r{r}'] = ','.join(map(str, bc))
        for tgt, (td, tc) in target.items():
            out[f'rank55_target_discovery_r{r}_{tgt}'] = ','.join(map(str, td))
            out[f'rank55_target_confirmation_r{r}_{tgt}'] = ','.join(map(str, tc))
        D, _ = mats[r]
        for i, j in (('a', 'b'), ('a', 'c'), ('b', 'c')):
            out[f'rank55_Ddisc_r{r}_{i}{j}'] = D[(i, j)]
            out[f'rank55_Ddisc_r{r}_{j}{i}'] = D[(j, i)]
        row = path[r - 1]
        out[f'rank55_e_r{r}'] = row['e_value']
        for k, x in enumerate(row['pairwise_responses'], 1):
            out[f'rank55_pair_response_r{r}_{k}'] = x
            all_values.append(x)
    if path[-1]['ranks']:
        for k, rank in enumerate(path[-1]['ranks'], 1):
            out[f'rank55_rank_{k}'] = rank
    out['rank55_zero_count'] = sum(int(x == 0.0) for x in all_values)
    out['rank55_abs_tie_count'] = CONTRAST_COUNT - len(set(abs(x) for x in all_values))
    return out


def run_experiment_055_strategy(seed, c, strategy, vals):
    if strategy not in STRATEGIES:
        raise ValueError(strategy)
    if strategy != SIGNED_RANK_30_STRATEGY:
        return run_experiment_054_strategy(seed, c, strategy, vals)
    stream = generate_experiment_055_stream(seed, c)
    groups, accepted, abstain, stop, path, mats, y, scores = infer_30contrast_exact_signed_rank(stream)
    ann = _annotation(stream, accepted, abstain, path, mats, y, scores)
    tau, kappa, k3, la, lb, lc, lab, lac, lbc, *_ = vals
    if abstain:
        rows = run_triad_persistence_on_stream(seed, f'experiment055_{c["label"]}', tau, k3, stream)
        for row in rows:
            row['strategy'] = SIGNED_RANK_30_STRATEGY
            row.update(ann)
    else:
        rows = _run_composed_gate(seed, f'experiment055_{c["label"]}', tau, k3, la, lb, lc, lab, lac, lbc, stream, ann, groups)
        for row in rows:
            row['strategy'] = SIGNED_RANK_30_STRATEGY
    for row in rows:
        row['experiment055_cell'] = c['label']
        row['experiment055_noise_family'] = c['noise_family']
        row['experiment055_no_tuning'] = 1
    return rows
