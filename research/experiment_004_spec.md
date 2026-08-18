# Experiment 004 — Structural Model Mismatch

**Status:** prospective specification; committed before Experiment 004 implementation and evaluation.

## Motivation

Experiments 001–003 established a responsiveness–conservatism tradeoff for threshold versus persistence-aware adaptation gating in a controlled linear system under abrupt and gradual slope changes. Those experiments leave open whether the observed distinction survives when prediction error is caused by structural model mismatch rather than a change that the fitted linear model can represent exactly.

Experiment 004 is a falsification-oriented extension. The data-generating process becomes nonlinear after the event, while the learner and adaptation operator remain the same linear OLS model used in prior experiments. No gate parameter is retuned.

## Scientific question

When a previously correct linear learner encounters an unmodeled nonlinear term, does persistence confirmation continue to produce a meaningful conservative shift relative to simple threshold gating, and what prediction-loss or adaptation-churn cost accompanies that shift?

A secondary question is whether persistence confirmation is more useful when the structural mismatch is transient than when it is persistent and therefore cannot be removed by repeated linear refitting.

## Shared system and frozen gate settings

Retain from the prior experiments:

- the same AR(1) input process;
- Gaussian observation noise with the same variance;
- event onset `t=401`;
- `N_STEPS=1200`;
- the same initial fit interval `t=101..300`;
- the same linear OLS prediction model with slope and intercept only;
- the same test-then-train decision chronology;
- rolling squared-error window `20`;
- refit window `100`;
- persistence count `3`;
- the same stable-data calibrated threshold `tau` produced by `calibrate_tau()`;
- the same four strategies: frozen, continuous, threshold, persistence.

The gate and learner are not given the true nonlinear coefficient, event duration, regime label, future observations, or any other evaluator-only information.

Evaluation seeds are frozen as `4000..4199`, disjoint from all prior calibration and evaluation seeds.

## Nonlinear generating process

Before the event, retain the correctly specified baseline system:

`y_t = 1.5 x_t + epsilon_t`.

Beginning at `t=401`, introduce a quadratic term while keeping the true linear slope fixed at `1.5`:

`y_t = 1.5 x_t + gamma x_t^2 + epsilon_t`.

The learner remains linear:

`y_hat_t = beta_1 x_t + beta_0`.

Thus the post-event quadratic component is intentionally outside the learner's model class. Re-fitting can change the best local linear approximation but cannot represent the true quadratic relation exactly.

Evaluate nonlinear magnitudes:

- `gamma ∈ {0.25, 0.5, 1.0}`.

For each magnitude evaluate two event-duration classes:

1. **Transient mismatch:** the quadratic term is active for exactly `20` observations, `t=401..420`, then disappears completely.
2. **Persistent mismatch:** the quadratic term begins at `t=401` and remains active through `t=1200`.

This yields 6 prospectively frozen cells. Within each `gamma`, transient and persistent streams are identical through `t=420` for a given seed. All four strategies within a seed/cell use the same generated `x`, noise realization, and resulting `y` stream.

## Why this is a structural-mismatch test

The true post-event system contains a feature (`x^2`) absent from the adaptive learner. Unlike the slope changes in Experiments 001–003, repeated linear OLS adaptation cannot make the model class correctly specified. The experiment therefore tests gate behavior when elevated residual loss may persist even after adaptation.

The experiment does not add a quadratic learner or retune the detector after inspecting results. Doing either would answer a different question.

## Primary outcomes

### Transient-mismatch cells

For each `gamma`, report the probability that each strategy adapts at least once during the true mismatch interval `t=401..420`.

The primary paired gate contrast is:

`persistence transient-adaptation indicator - threshold transient-adaptation indicator`.

Report the mean paired difference and a 95% paired whole-seed bootstrap confidence interval.

### Persistent-mismatch cells

For each `gamma`, report cumulative squared prediction loss over `t=401..600`.

The primary paired gate contrast is:

`persistence loss - threshold loss`.

Report the mean paired difference and a 95% paired whole-seed bootstrap confidence interval.

## Adaptation-churn outcome

Because structural mismatch cannot be eliminated by the linear learner, preserve and report the number of post-event adaptations through `t=1200` for threshold and persistence gating in every cell.

For persistent-mismatch cells, the prespecified churn contrast is:

`persistence adaptation count - threshold adaptation count`.

Report the paired mean difference and a 95% paired whole-seed bootstrap confidence interval.

This outcome is interpreted descriptively as computational/adaptation burden. It is not substituted for prediction loss when judging predictive performance.

## Secondary outcomes

Per seed/cell/strategy preserve:

- cumulative squared prediction loss over `t=401..600` and `t=401..1200`;
- whether adaptation occurs during `t=401..420`;
- first post-event adaptation time;
- adaptation delay from `t=401`;
- adaptation counts over `t=401..600` and `t=401..1200`;
- fitted slope and intercept before and after adaptation events.

Full time-step traces are preserved for audit seeds `4000..4004`. Complete per-seed summaries are preserved for all 6 cells and all 200 seeds.

## Inference

The independent experimental unit is the whole generated seed/stream. Strategies are paired within the same seed and cell. Time steps are not treated as independent replicates.

All confidence intervals use paired whole-seed bootstrap resampling with `10,000` replicates and deterministic per-cell bootstrap seeds fixed in the evaluation implementation before results are inspected.

No multiplicity-adjusted omnibus superiority claim is planned. Results are interpreted cell-wise as a robustness/falsification map of the previously observed gating tradeoff.

## Prospective interpretation rules

Experiment 004 does **not** define success as persistence gating winning every cell.

Evidence that the prior tradeoff survives structural mismatch would require a systematic conservative shift—principally fewer transient-event adaptations and/or lower persistent adaptation churn for persistence than threshold gating—together with a clearly reported prediction-loss consequence.

If persistence and threshold behave nearly identically across mismatch magnitudes, the earlier distinction is constrained rather than generalized.

If persistence reduces adaptation but has consistently worse predictive loss, that supports continuation of the responsiveness–conservatism interpretation rather than superiority.

If persistence reduces both futile adaptation churn and prediction loss under persistent mismatch, that is evidence of a setting in which persistence confirmation may be beneficial, but the claim remains limited to this frozen structural-mismatch family.

If persistence performs uniformly worse in both adaptation burden and predictive loss, that is evidence against extending the mechanism to structural mismatch.

Nonresponse at small `gamma` is interpreted as a detectability boundary and is not grounds for post hoc threshold retuning.

## Required audit checks

Before accepting Experiment 004 evidence, independently verify at minimum:

- exact seed/cell/strategy coverage;
- matched stochastic realizations across strategies within seed/cell;
- identical transient and persistent streams through `t=420` within each matched `seed, gamma` pair;
- exact quadratic generating equation and event duration;
- absence of the quadratic term before `t=401` and after `t=420` in transient cells;
- persistence of the quadratic term through the end of persistent cells;
- unchanged linear learner class and OLS refit operator;
- unchanged frozen `tau`, rolling window, refit window, and persistence count;
- test-then-train prediction chronology at every audited time step;
- exact reproduction of reported paired contrasts and bootstrap intervals from seed-level evidence.

## Claim boundary

Experiment 004 can establish evidence only for the specified quadratic structural mismatch under the frozen stochastic process, learner, gate settings, magnitudes, durations, and seed distribution.

It does not establish robustness to arbitrary nonlinear dynamics, changing input distributions, heteroskedastic or non-Gaussian noise, sensor faults, missing data, adversarial manipulation, multivariate systems, real digital twins, arbitrary concept drift, or an optimally specified nonlinear learner.

No result from Experiment 004 may be used to claim general superiority of persistence gating unless such a claim is directly supported by the prespecified outcomes and remains explicitly bounded to the tested system.