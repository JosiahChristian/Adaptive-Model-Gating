# Experiment 030 — Topology Posterior Decision-Sufficiency Replication

## Status

Prospectively frozen before any Experiment-030 evaluation outcome is generated.

Experiment 029 validated the calibrated Experiment-028 topology posterior as a statistically safe provenance classifier under the frozen 0.99 posterior-risk rule, but failed H9 because operational loss under common-mode corruption regressed relative to `triad_persistence`. Experiment 030 does not alter the posterior, the 0.99 rule, the probe schedule, or either operational gate. It is a decision-sufficiency characterization study.

## Scientific question

Is the calibrated topology posterior a sufficient state variable for deciding whether the provenance-aware operational veto is beneficial, or does the paired action value of that veto change materially across later operational disturbance contexts even when topology confidence is high?

## Frozen policies

Evaluate exactly two frozen operational policies on the same seed/cell stream:

1. Experiment-029 `sequential_directed_covariance_posterior_risk_gate`;
2. `triad_persistence`.

Experiment-029 remains exactly as frozen:

- Experiment-028 directed-covariance posterior;
- wrong topology action cost 100;
- fallback cost 1;
- deployment threshold 0.99;
- symmetric rounds 1..5;
- no posterior recalibration;
- no threshold change;
- no changed operational logic.

The Experiment-030 code may summarize paired outcomes but may not modify either policy.

## Evaluation cells

Use seven prospectively fixed cells:

- `healthy`;
- `drift_0.50`;
- `common_mode_0.25`;
- `common_mode_0.50`;
- `common_mode_1.00`;
- `g0.500_n1.00` using `drift_ab_fault`, magnitude 0.50;
- `g0.500_n1.50` using `drift_ab_fault`, magnitude 0.50.

The simulator family label is available only to the evaluator for stratified reporting. It is never supplied to either policy.

## Seeds

Use 1,000 fresh seeds per cell:

`30000..30999`.

Audit seeds: `30000..30004`.

No Experiment-030 seed overlaps any prior evaluation or calibration range.

## Paired action-value summaries

For every seed/cell compute:

- Experiment-029 provenance deployment/abstention;
- posterior probability at deployment;
- operational loss `L = sum sq_error` over t=401..600;
- final absolute slope error;
- adaptation signature;
- diagnostic energy.

Define paired differences on the same seed:

`Delta_L = L_029 - L_triad`

and

`Delta_S = slope_error_029 - slope_error_triad`.

Positive `Delta_L` means the provenance-aware posterior-risk policy has worse predictive operational loss than `triad_persistence`. Negative `Delta_S` means it has better final parameter fidelity.

For each cell report means, medians, and fixed 10,000-resample paired bootstrap 95% intervals for `Delta_L` and `Delta_S`. Bootstrap seed is fixed at `30030`.

## Frozen hypotheses

H1 — high topology-confidence condition:

In `common_mode_0.50` and `g0.500_n1.00`, Experiment-029 topology deployment coverage must be at least 0.95 and accepted precision at least 0.99. This establishes that the action-value comparison is not being driven primarily by topology uncertainty.

H2 — replicated common-mode predictive-loss penalty:

For `common_mode_0.50`, mean `Delta_L > 0` and the paired-bootstrap 95% lower bound for mean `Delta_L` must be > 0.

H3 — supported drift/fault non-regression:

For `g0.500_n1.00`, mean `Delta_L <= 0.02` and the paired-bootstrap 95% upper bound must be <= 0.05.

H4 — context-dependent action-value interaction:

The difference in paired mean action value

`mean(Delta_L_common_mode_0.50) - mean(Delta_L_g0.500_n1.00)`

must be at least 5.0, and a paired-seed bootstrap of this difference must have a 95% lower bound > 0. The bootstrap pairs seed index across the two cells but does not assume the two simulator trajectories are identical.

H5 — common-mode objective conflict:

At `common_mode_0.50`, mean `Delta_L > 0` while mean `Delta_S < 0`. This records the predicted tradeoff between predictive operational loss and parameter fidelity rather than collapsing both objectives into one post-hoc score.

H6 — benign/control preservation:

For `healthy` and `drift_0.50`, absolute mean `Delta_L <= 0.02`. For `primary_fault` no separate Experiment-030 cell is introduced; its non-regression was already supported in Experiment 029 and is not re-tested here.

H7 — common-mode scaling is reported without tuning:

`common_mode_0.25`, `common_mode_0.50`, and `common_mode_1.00` must all be reported with the same frozen policies and summaries. No magnitude may be removed or reweighted after outcomes are observed.

H8 — no policy contamination:

The report must record that family labels are evaluator-only, both policy implementations are inherited unchanged, the 0.99 threshold remains cost-derived, and no Experiment-030 outcome changes any decision rule.

## Interpretation rule

Experiment 030 supports the decision-insufficiency claim if H1-H8 all pass.

If supported, Phase II must not attempt another topology-threshold or probe tweak. The next experiment should introduce and independently validate an operational-state/action-value model using evidence available at adaptation time before that model is allowed to alter deployment decisions.

If H2 or H4 fails, the Experiment-029 common-mode regression should be treated as sample-specific until a different explanation is established.
