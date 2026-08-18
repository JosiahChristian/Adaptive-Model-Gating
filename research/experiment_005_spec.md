# Experiment 005 — Covariate Shift Without Conditional Drift

**Status:** prospective specification; committed before Experiment 005 implementation and evaluation.

## Motivation

Experiments 001–004 changed the response-generating relation while retaining the same AR(1) input process. The accumulated evidence therefore does not establish how threshold and persistence-aware adaptation gating behave when the distribution of inputs changes while the conditional response law remains unchanged.

Experiment 005 is a falsification-oriented covariate-shift test. It changes where the system operates in input space without changing the true mapping from input to outcome. This directly tests whether a prediction-error gate can mistake a change in operating distribution for evidence that the predictive relationship itself has changed.

## Scientific question

When the input distribution shifts but the true conditional law `P(y|x)` remains exactly the same, does persistence confirmation reduce reactive adaptation relative to simple threshold gating, and what prediction-loss consequence accompanies that conservatism?

A secondary question is whether a persistent change in operating region causes repeated adaptation even though the learner's model class remains correctly specified.

## Shared system and frozen gate settings

Retain from prior experiments:

- `N_STEPS = 1200`;
- event onset `t=401`;
- initial fit interval `t=101..300`;
- the same linear OLS learner with slope and intercept only;
- true response slope `1.5`;
- Gaussian observation noise with standard deviation `0.5`;
- the same test-then-train chronology;
- rolling squared-error window `20`;
- refit window `100`;
- persistence count `3`;
- the same stable-data threshold `tau` produced by `calibrate_tau()`;
- strategies: frozen, continuous, threshold, persistence.

No gate parameter is retuned for covariate shift.

Evaluation seeds are frozen as `5000..5199`, disjoint from all prior calibration and evaluation seeds.

## Baseline latent input process

Generate a latent baseline process `z_t` using the same stochastic dynamics used previously:

`z_t = 0.8 z_{t-1} + eta_t`,

where

`eta_t ~ Normal(0, 0.5^2)`.

Use `z_0 = 0`.

Before the event, observed input is

`x_t = z_t`.

## Covariate-shift intervention

At `t=401`, shift the observed operating region by an additive mean offset `mu` while leaving the latent AR(1) trajectory and outcome noise realization unchanged:

`x_t = z_t + mu_t`.

Evaluate shift magnitudes:

- `mu ∈ {0.5, 1.0, 2.0}`.

For each magnitude evaluate two event classes:

1. **Transient covariate shift:** `mu_t = mu` for exactly `t=401..420`, then `mu_t = 0` from `t=421` onward.
2. **Persistent covariate shift:** `mu_t = mu` for `t=401..1200`.

This yields 6 prospectively frozen cells.

Because the same latent `z_t` and observation-noise draws are used for matched streams, transient and persistent cells with the same `seed, mu` must be identical through `t=420` and differ only in whether the mean offset remains active afterward.

The transient intervention reverts exactly at `t=421`; there is no AR-state carryover from the shift because the intervention is applied to observed `x_t`, not to the latent `z_t` dynamics.

## Unchanged conditional response law

For every time step and every cell, generate outcomes as

`y_t = 1.5 x_t + epsilon_t`,

with

`epsilon_t ~ Normal(0, 0.5^2)`.

Thus

`E[y_t | x_t] = 1.5 x_t`

before, during, and after the shift.

There is no true slope drift, intercept drift, nonlinear term, label shift, or observation-noise change. The learner's linear model class remains correctly specified throughout.

The evaluator must preserve/log the true shift offset `true_mu`, but the gate may not use `true_mu`, the event label, event duration, future inputs, or future losses.

## Why this is a covariate-shift test

The intervention changes the marginal distribution `P(x)` while leaving `P(y|x)` fixed. Any gate activation is therefore a response to realized prediction-error evidence under a new operating distribution, not to a change in the true conditional response mechanism.

Refitting may still alter finite-sample coefficient estimates and can therefore change realized prediction loss. That possibility is part of the experiment and must not be described post hoc as proof of underlying concept drift.

## Primary outcomes

### Transient covariate-shift cells

For each `mu`, report the probability that each strategy adapts at least once during the true shift interval `t=401..420`.

The primary paired gate contrast is

`persistence adaptation indicator - threshold adaptation indicator`.

Report the paired mean difference and a 95% paired whole-seed bootstrap confidence interval.

### Persistent covariate-shift cells

For each `mu`, report cumulative squared prediction loss over `t=401..600`.

The primary paired gate contrast is

`persistence loss - threshold loss`.

Report the paired mean difference and a 95% paired whole-seed bootstrap confidence interval.

## Adaptation-burden outcome

For every persistent cell, preserve the number of post-event adaptations through `t=1200`.

The prespecified paired burden contrast is

`persistence adaptation count - threshold adaptation count`.

Report the paired mean difference and a 95% paired whole-seed bootstrap confidence interval.

This quantity measures adaptation burden/churn. It is not a substitute for predictive loss.

## Stable-reference outcome

Because the conditional response mechanism is unchanged, report the frozen-strategy loss in every cell as an important reference. A finding that adaptive strategies materially outperform the frozen learner must be interpreted as finite-sample re-estimation benefit under a new input distribution, not as correction of a changed true response law.

No claim that adaptation was scientifically necessary is permitted solely because it reduced realized loss.

## Secondary outcomes

Per seed/cell/strategy preserve:

- cumulative squared prediction loss over `t=401..600` and `t=401..1200`;
- whether adaptation occurs during `t=401..420`;
- first post-event adaptation time;
- adaptation delay from `t=401`;
- adaptation counts over `t=401..600` and `t=401..1200`;
- fitted slope and intercept before and after adaptation events.

Full time-step traces are preserved for audit seeds `5000..5004`. Complete per-seed summaries are preserved for all 6 cells and 200 seeds.

## Inference

The independent experimental unit is the whole generated seed/stream. Strategies are paired within seed and cell. Time steps are serially dependent and are not treated as independent replicates.

All confidence intervals use paired whole-seed bootstrap resampling with `10,000` replicates and deterministic per-cell bootstrap seeds frozen in the evaluation implementation before results are inspected.

No multiplicity-adjusted omnibus superiority claim is planned. Cell-wise results form a robustness/falsification map.

## Prospective interpretation rules

Experiment 005 does **not** define success as persistence gating winning every cell.

Evidence that the prior conservatism-versus-responsiveness mechanism survives pure covariate shift would consist of a systematic reduction in gate-triggered adaptation for persistence relative to threshold gating, accompanied by an explicitly quantified prediction-loss consequence.

If threshold and persistence behave nearly identically, the prior distinction is constrained under covariate shift.

If persistence reduces adaptation burden but increases prediction loss, that supports the same conservatism-versus-responsiveness interpretation observed previously.

If persistence reduces both adaptation burden and prediction loss, that supports a bounded benefit under this covariate-shift family, but does not establish general superiority.

If neither gate reacts materially, that is evidence that the frozen residual detector is relatively insensitive to these shifts when `P(y|x)` remains unchanged.

If adaptive strategies react strongly despite no conditional drift, that is evidence of a false-adaptation vulnerability of residual-threshold gating under changed operating distributions.

Results must not be described as concept-drift detection because the true conditional response law is frozen by design.

## Required audit checks

Before accepting Experiment 005 evidence, independently verify at minimum:

- exact seed/cell/strategy coverage;
- matched latent `z_t` and observation-noise realizations across strategies within seed/cell;
- identical matched transient/persistent streams through `t=420` within each `seed, mu` pair;
- exact latent AR(1) equation and innovation standard deviation `0.5`;
- `true_mu = 0` before `t=401`;
- transient `true_mu = mu` exactly for `t=401..420` and exactly zero thereafter;
- persistent `true_mu = mu` through `t=1200`;
- exact observed-input relation `x_t = z_t + true_mu_t`;
- exact unchanged response equation `y_t = 1.5 x_t + epsilon_t`;
- unchanged observation-noise distribution;
- unchanged linear learner and OLS refit operator;
- unchanged frozen `tau`, rolling window, refit window, and persistence count;
- test-then-train prediction chronology at every audited time step;
- exact reproduction of reported paired contrasts and bootstrap intervals from seed-level evidence.

## Claim boundary

Experiment 005 can establish evidence only for the specified additive input-mean shifts under the frozen latent AR(1) process, Gaussian noise, correctly specified linear learner, gate settings, magnitudes, durations, and seed distribution.

It does not establish robustness to arbitrary covariate shift, variance shifts, changing autocorrelation, support violations beyond the tested offsets, multivariate distribution shift, label shift, sensor faults, missing data, adversarial manipulation, nonlinear dynamics, real digital twins, or arbitrary concept drift.

No result from Experiment 005 may be used to claim general superiority of persistence gating or general distribution-shift robustness.