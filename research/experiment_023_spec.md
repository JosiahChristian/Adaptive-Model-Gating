# Experiment 023 — Prospective Noise-Aware Confidence Qualification

Status: **FROZEN BEFORE ANY EXPERIMENT-023 OUTCOMES**

## Motivation
Experiment 022 established a narrow out-of-distribution failure boundary for the frozen Experiment-021 policy. H3, H4, H5, and H6 passed, while H1 safety and H2 precision failed only under the 1.50x observation-noise stress. In each such cell, 187/200 seeds were accepted, 184 were correct, and 3 were wrong (precision 0.983957; wrong acceptance 0.015). No retrospective change to Experiment 021 is permitted.

Experiment 023 tests whether this boundary is caused by a confidence rule whose null thresholds do not scale with diagnostic variance.

## Frozen policy change
All Experiment-021 selector logic, probe amplitudes, target ordering, stopping structure, fallback behavior, and operational gate logic remain unchanged.

The only new mechanism is an analytic per-seed diagnostic-noise scale factor derived exclusively from the pre-intervention probe baseline `t=181..200`.

For each channel x in {a,b,c}, compute its baseline mean over `181..200`. Pool the 60 centered baseline probe observations and compute the sample standard deviation

`s_hat = sqrt(sum((obs - channel_mean)^2) / 57)`.

The inherited reference diagnostic standard deviation is `SIGMA_PROBE = 0.05`. Freeze

`noise_factor = max(1.0, s_hat / SIGMA_PROBE)`.

No calibration seeds or Experiment-023 outcomes contribute to this factor.

Every provenance threshold used by the qualification-aware Experiment-021 path is multiplied by `noise_factor` for that seed:

- round-1..4 cumulative `mu` and `nu` thresholds;
- early-targeted round-4 `mu_4_early` and `nu_4_early`;
- full round-5 `mu_5` and `nu_5` where inherited by dispatch;
- targeted round-5 `mu_5_targeted` and `nu_5_targeted`.

No other threshold is changed. The same factor is applied from round 1 onward, so a high-noise seed cannot prequalify using unscaled confidence thresholds.

## Strategies
Evaluate exactly five strategies:

1. Experiment-023 noise-aware qualification-aware strategy (primary);
2. frozen Experiment-021 qualification-aware strategy;
3. frozen Experiment-020 early-targeted strategy;
4. frozen Experiment-019 targeted strategy;
5. `triad_persistence`.

## Evaluation distribution
Use fresh evaluation seeds exactly `23000..23199`, 200 seeds per cell, with no recalibration.

Evaluate the following prospective cells at each drift/A-B-fault magnitude `0.25`, `0.50`, and `1.00`:

- gain 0.50 with observation-noise multipliers `1.00`, `1.25`, `1.50`, `1.75`, and `2.00`;
- gain 0.425 with noise multipliers `1.00`, `1.50`, and `2.00`;
- gain 0.35 with noise multipliers `1.00`, `1.50`, and `2.00`.

Also retain healthy, genuine drift, common-mode, primary-fault, and coherent-all-auxiliary controls at the inherited nominal noise level.

The stream-generation semantics are inherited from Experiment 022. Only the specified gain/noise combinations are changed.

## Primary preregistered criteria

### H1 — restored safety
Across every Experiment-023 cell, the primary strategy must make **zero wrong provenance acceptances**.

### H2 — high-noise precision
For every noise >=1.50 cell with at least 20 accepted seeds, accepted precision must be >=0.99. Cells with fewer than 20 acceptances are reported without a precision-generalization claim.

### H3 — useful high-noise coverage
At gain 0.50 and noise 1.50, primary coverage must be >=0.85 at every magnitude. At noise 1.75 and 2.00, coverage is reported as a robustness boundary and is not required to exceed 0.85, provided H1 holds.

### H4 — nominal non-regression
At gain 0.50/noise 1.00, primary coverage must be within 0.03 absolute of frozen Experiment 021, accepted precision must be >=0.99, and mean probe energy may exceed Experiment 021 by no more than 0.05.

### H5 — moderate-gain preservation
At gain 0.425/noise 1.00 and gain 0.35/noise 1.00, primary coverage must remain within 0.03 absolute of Experiment 021 and wrong acceptance must remain zero.

### H6 — conservative low-information behavior
For any cell in which the primary strategy abstains, its operational behavior must fall back exactly to the inherited triad behavior. Adaptation rate must not exceed triad by more than 0.02 in cells with gain <=0.35 and noise >=1.50.

### H7 — mechanism validity
`noise_factor` must be computed only from `t=181..200` probe observations and must not use family label, gain, magnitude, oracle partition, post-event observations, or evaluation aggregate outcomes. For nominal-noise controls, report the empirical distribution of `noise_factor`; no post-hoc clipping or retuning is permitted.

## Secondary analyses
Report coverage, precision, wrong acceptance, abstention, probe energy, prequalification/dispatch rates, estimated `noise_factor`, operational loss, adaptation rate, final coefficient error, and paired bootstrap intervals. Report safety/coverage curves jointly versus gain and noise.

## Decision rule
If H1 passes and H3/H4 pass, the Experiment-022 safety boundary is considered mechanistically repaired by variance-aware confidence scaling. If H1 passes but H3 fails, scaling is safe but too conservative. If H1 fails, analytic variance scaling alone is insufficient and the next experiment must test independent confirmation or a different uncertainty model. No Experiment-023 outcome may be used to modify this specification.