from __future__ import annotations

import experiment_055 as base

OPERATIVE_SPEC_ISSUE = 226
CONFIRMATION_AGREEMENT_STRATEGY = 'covariance_matched_discovery_30contrast_exact_signed_rank_confirmation_topology_agreement_context_composed_risk_gate'
SIGNED_RANK_30_STRATEGY = base.SIGNED_RANK_30_STRATEGY
STRATEGIES = (CONFIRMATION_AGREEMENT_STRATEGY,) + base.STRATEGIES
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


def generate_experiment_061_stream(seed, c):
    return base.generate_experiment_055_stream(seed, c)


def confirmation_profile_061(mats):
    # Use the already-held-out confirmation response matrices with the exact
    # fixed discovery-profile transform and deterministic tie order. No margin
    # or fitted threshold is introduced.
    confirmation_as_profile = {r: (mats[r][1], mats[r][1]) for r in range(1, 6)}
    return base.discovery_profile(confirmation_as_profile)


def infer_confirmation_agreement_061(stream):
    mats = {r: base.response_matrices_055(stream, r) for r in range(1, 6)}
    y_disc, scores_disc, discovery_candidate = base.discovery_profile(mats)
    y_conf, scores_conf, confirmation_candidate = confirmation_profile_061(mats)
    edge = base.HYP_EDGE[discovery_candidate]
    path = []
    all_values = []
    for r in range(1, 6):
        pairs = base.pairwise_confirmation_055(stream, r, edge)
        flat = tuple(x for pair in pairs for x in pair)
        all_values.extend(flat)
        wplus = ''
        ranks = ()
        signed_rank_pass = 0
        if r == 5:
            wplus, ranks = base.signed_rank_statistic_30(all_values)
            signed_rank_pass = int(wplus >= W_CUTOFF)
        agreement = int(confirmation_candidate == discovery_candidate)
        repaired_accept = int(r == 5 and signed_rank_pass and agreement)
        path.append({
            'stage': r,
            'candidate': discovery_candidate,
            'confirmation_candidate': confirmation_candidate,
            'agreement': agreement,
            'signed_rank_pass': signed_rank_pass,
            'e_value': ACCEPT_E if repaired_accept else 0.0,
            'pairwise_responses': flat,
            'wplus': wplus,
            'ranks': ranks,
        })
    accepted = int(path[-1]['e_value'] >= base.E_THRESHOLD)
    groups = base.groups_from_edges([edge]) if accepted else None
    return groups, accepted, 1 - accepted, 5, path, mats, y_disc, scores_disc, y_conf, scores_conf


def _annotation_061(stream, accepted, abstain, path, mats, y_disc, scores_disc, y_conf, scores_conf):
    # Preserve the underlying rank55 evidence fields as diagnostics, then add
    # immutable Experiment 061 repair fields for the actual deployment rule.
    rank55_ann = base._annotation(stream, int(path[-1]['signed_rank_pass']), 1 - int(path[-1]['signed_rank_pass']), path, mats, y_disc, scores_disc)
    discovery_candidate = path[0]['candidate']
    confirmation_candidate = path[0]['confirmation_candidate']
    rank55_ann.update({
        'provenance_accepted': accepted,
        'provenance_abstain': abstain,
        'posterior_deploy_hypothesis': discovery_candidate if accepted else '',
        'probe_stop_round': 5 if accepted else 0,
        'rank61_candidate': discovery_candidate,
        'rank61_confirmation_candidate': confirmation_candidate,
        'rank61_confirmation_agreement': int(discovery_candidate == confirmation_candidate),
        'rank61_signed_rank_pass': int(path[-1]['signed_rank_pass']),
        'rank61_e_threshold': base.E_THRESHOLD,
        'rank61_e_final': path[-1]['e_value'],
        'rank61_wplus': path[-1]['wplus'],
        'rank61_w_cutoff': W_CUTOFF,
        'rank61_contrast_count': CONTRAST_COUNT,
        'rank61_spec_issue': OPERATIVE_SPEC_ISSUE,
        'rank61_no_extra_observations': 1,
        'rank61_candidate_reselected': 0,
        'rank61_rule': 'deploy iff frozen discovery candidate has W+>=345 and confirmation-only covariance-matched topology argmax agrees; agreement is veto-only',
    })
    for pair, val in zip(base.VECTOR, y_conf):
        rank55_ann['rank61_Yconf_' + ''.join(pair)] = val
    for h, val in scores_conf.items():
        rank55_ann['rank61_Qconf_' + h] = val
    return rank55_ann


def run_experiment_061_strategy(seed, c, strategy, vals):
    if strategy not in STRATEGIES:
        raise ValueError(strategy)
    if strategy != CONFIRMATION_AGREEMENT_STRATEGY:
        rows = base.run_experiment_055_strategy(seed, c, strategy, vals)
        for row in rows:
            row['experiment061_cell'] = c['label']
            row['experiment061_noise_family'] = c['noise_family']
            row['experiment061_no_tuning'] = 1
        return rows

    stream = generate_experiment_061_stream(seed, c)
    groups, accepted, abstain, stop, path, mats, y_disc, scores_disc, y_conf, scores_conf = infer_confirmation_agreement_061(stream)
    ann = _annotation_061(stream, accepted, abstain, path, mats, y_disc, scores_disc, y_conf, scores_conf)
    tau, kappa, k3, la, lb, lc, lab, lac, lbc, *_ = vals
    if abstain:
        rows = base.run_triad_persistence_on_stream(seed, f'experiment061_{c["label"]}', tau, k3, stream)
        for row in rows:
            row['strategy'] = CONFIRMATION_AGREEMENT_STRATEGY
            row.update(ann)
    else:
        rows = base._run_composed_gate(seed, f'experiment061_{c["label"]}', tau, k3, la, lb, lc, lab, lac, lbc, stream, ann, groups)
        for row in rows:
            row['strategy'] = CONFIRMATION_AGREEMENT_STRATEGY
    for row in rows:
        row['experiment061_cell'] = c['label']
        row['experiment061_noise_family'] = c['noise_family']
        row['experiment061_no_tuning'] = 1
        row['experiment061_confirmation_agreement_repair'] = 1
    return rows
