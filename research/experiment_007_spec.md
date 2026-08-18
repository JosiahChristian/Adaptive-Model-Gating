# Experiment 007 — Input-Sensor Corruption With Unchanged Physical Dynamics

**Status:** prospective specification; frozen before Experiment 007 implementation and evaluation.

## Motivation

Experiment 006 showed that residual-only adaptation gating can falsely adapt under outcome-sensor corruption even though the underlying physical response law remains unchanged. That experiment corrupted the observed target while preserving the predictor.

Experiment 007 attacks a different sensing failure mode: corruption of the measured input itself. This creates an errors-in-variables problem. The latent physical state and physical response law remain unchanged, but the adaptive learner receives a corrupted predictor and may therefore alter its fitted coefficients in response to sensor degradation rather than physical drift.

The experiment is designed to distinguish three quantities that must not be conflated:

1. operational prediction quality using the corrupted measured input;
2. physical-law coefficient integrity relative to the unchanged latent system;
3. adaptation burden caused by sensor corruption.

## Scientific question

When the latent system is unchanged but the measured predictor becomes noisy, does persistence confirmation reduce false/reactive adaptation relative to simple threshold gating, and does reduced adaptation better preserve the physical model parameters?

A secondary question is whether refitting on corrupted inputs causes systematic slope attenuation or other coefficient contamination under persistent sensor noise.

## Shared system and frozen gate settings

Retain unchanged:

- `N_STEPS = 1200`;
- event onset `t=401`;
- initial fit interval `t=101..300`;
- linear OLS learner with slope and intercept only;
- physical response slope `1.5`;
- baseline physical response noise standard deviation `0.5`;
- rolling squared-error window `20`;
- refit window `100`;
- persistence count `3`;
- the same stable-data threshold `tau` produced by `calibrate_tau()`;
- strategies: frozen, continuous, threshold, persistence;
- test-then-train chronology.

No gate parameter is retuned.

Evaluation seeds are frozen as `7000..7199`, disjoint from all prior calibration and evaluation seeds.

## Latent physical input process

Generate latent physical input `x_true,t` by

`x_true,t = 0.8 x_true,t-1 + eta_t`,

where

`eta_t ~ Normal(0, 0.5^2)`

and `x_true,0 = 0`.

## Unchanged physical response law

Generate the physical target as

`y_t = 1.5 x_true,t + epsilon_t`,

with

`epsilon_t ~ Normal(0, 0.5^2)`.

This law is unchanged at all times and in all cells. There is no physical slope drift, intercept drift, nonlinear term, output-noise change, or latent-state intervention.

## Input-sensor corruption intervention

The learner does not receive `x_true,t` after corruption begins. Instead it receives

`x_obs,t = x_true,t + sigma_x,t * nu_t`,

where

`nu_t ~ Normal(0,1)`.

The latent `x_true,t`, physical response noise `epsilon_t`, and unit sensor-noise draws `nu_t` are generated once per seed and shared across all matched strategies.

Evaluate corruption magnitudes

- `sigma_x ∈ {0.25, 0.5, 1.0}`.

For each magnitude evaluate two event classes:

1. **Transient input-sensor corruption:** `sigma_x,t = sigma_x` for exactly `t=401..420`, then `sigma_x,t = 0` from `t=421` onward.
2. **Persistent input-sensor corruption:** `sigma_x,t = sigma_x` for `t=401..1200`.

This yields 6 frozen cells.

Transient and persistent cells with the same `seed, sigma_x` must be identical through `t=420`.

## Learner-visible stream

The learner and gate receive only the measured stream `(x_obs,t, y_t)` plus legitimately available history and model state.

The gate may not use:

- `x_true,t`;
- `true_sigma_x`;
- unit sensor-noise draws;
- event class or duration;
- future observations or future loss;
- evaluator-only coefficient-integrity metrics.

All fitting and refitting uses `x_obs`, never `x_true`.

## Why this differs from concept drift

The physical law `y = 1.5 x_true + epsilon` remains fixed. However, the statistical relation between `y` and the corrupted measured predictor `x_obs` changes because of measurement error. Therefore results must not be described as physical concept drift.

A change in fitted slope under persistent corruption is evidence of errors-in-variables contamination, not evidence that the true system slope changed.

## Primary outcomes

### Transient cells

For each `sigma_x`, report whether each strategy adapts at least once during `t=401..420`.

Primary paired contrast:

`persistence adaptation indicator - threshold adaptation indicator`.

Report the paired mean difference and 95% paired whole-seed bootstrap interval.

### Persistent cells

The primary predictive endpoint is cumulative operational squared loss over `t=401..600`, using the actual learner-visible input:

`(y_t - y_hat_t)^2`, where `y_hat_t = model_t(x_obs,t)` before same-step adaptation.

Primary paired contrast:

`persistence operational loss - threshold operational loss`.

Report the paired mean difference and 95% paired whole-seed bootstrap interval.

## Coefficient-integrity outcome

For each persistent cell preserve the post-event fitted slope trajectory and the final slope after `t=1200`.

Define slope-error magnitude at the end of the stream as

`abs(final_fitted_slope - 1.5)`.

The prespecified paired coefficient-integrity contrast is

`persistence final slope-error magnitude - threshold final slope-error magnitude`.

Report the paired mean difference and 95% paired whole-seed bootstrap interval.

A negative value means persistence better preserves the true physical slope. This is an evaluator-only physical-integrity metric; it is not available to the gate.

## Adaptation-burden outcome

For every persistent cell preserve post-event adaptation count through `t=1200`.

Prespecified paired contrast:

`persistence adaptation count - threshold adaptation count`.

Report mean difference and 95% paired whole-seed bootstrap interval.

## Counterfactual latent-input diagnostic

For audit and secondary analysis only, evaluate each strategy's current fitted model on the latent physical input at each time step:

`y_hat_latent,t = slope_before * x_true,t + intercept_before`.

Define latent-input clean squared error

`(y_t - y_hat_latent,t)^2`.

This metric isolates coefficient contamination from instantaneous input-sensor corruption. It must not be presented as an operationally available prediction score because the learner does not observe `x_true` during corruption.

Report cumulative latent-input clean loss over `t=401..600` and `t=401..1200` as secondary diagnostics.

## Stable/frozen reference

The frozen strategy is an important reference because its coefficients cannot be contaminated by corrupted-input refitting. Under persistent sensor corruption it may still have poor operational loss because it must predict from corrupted `x_obs`; that does not imply its physical coefficients are wrong.

Interpret predictive loss and coefficient integrity separately.

## Secondary outcomes

Per seed/cell/strategy preserve:

- operational loss over `t=401..600` and `t=401..1200`;
- latent-input clean loss over the same horizons;
- adaptation during `t=401..420`;
- first post-event adaptation time and delay;
- adaptation counts over `t=401..600` and `t=401..1200`;
- slope/intercept before and after each adaptation;
- final fitted slope and intercept;
- final slope-error magnitude.

Full time-step traces are required for audit seeds `7000..7004`; complete per-seed summaries are required for all 6 cells and 200 seeds.

## Inference

The independent experimental unit is the whole seed/stream. Strategies are paired within seed and cell. Time steps are serially dependent and are not independent replicates.

Use paired whole-seed bootstrap inference with `10,000` replicates and deterministic per-cell bootstrap seeds frozen in the evaluation implementation before results are inspected.

No multiplicity-adjusted omnibus superiority claim is planned. Cell-wise results form a falsification/robustness map.

## Prospective interpretation rules

Experiment 007 does not define success as persistence winning every cell.

- If persistence reduces adaptation burden and also preserves slope integrity, that supports a bounded sensor-fault robustness benefit.
- If persistence reduces adaptation burden but coefficient integrity and operational loss are unchanged, its role is primarily computational conservatism.
- If persistence reduces adaptation burden but worsens operational loss, that supports the familiar conservatism-versus-responsiveness tradeoff under input corruption.
- If both gates adapt strongly and both slopes become contaminated, that is evidence that persistence confirmation alone is insufficient against sustained input-sensor failure.
- If the frozen model preserves coefficient integrity while adaptive strategies drift away from 1.5, that is evidence that adaptation itself can damage a correct physical model under errors-in-variables contamination.

No result may be described as successful physical-drift detection because no physical drift occurs by design.

## Required audit checks

Before accepting evidence, independently verify at minimum:

- exact 6-cell × 4-strategy × 200-seed coverage;
- seeds exactly `7000..7199`;
- matched latent `x_true`, physical response-noise draws, and sensor-unit-noise draws across strategies within seed/cell;
- matched transient/persistent streams through `t=420`;
- exact latent AR(1) equation and innovation standard deviation `0.5`;
- exact physical response equation `y = 1.5*x_true + epsilon` with unchanged noise standard deviation `0.5`;
- exact observed-input equation `x_obs = x_true + true_sigma_x * sensor_unit_noise`;
- `true_sigma_x=0` before `t=401`;
- transient corruption exactly on `t=401..420` and zero thereafter;
- persistent corruption active through `t=1200`;
- learner fitting/refitting uses `x_obs` only;
- evaluator-only `x_true` is never passed into the gate or refit operator;
- unchanged `tau`, rolling window, refit window, persistence count, and OLS operator;
- test-then-train chronology;
- exact recomputation of operational loss, latent-input clean loss, adaptation burden, final slope error, paired contrasts, and bootstrap intervals.

## Claim boundary

Experiment 007 can establish evidence only for the specified additive Gaussian input-sensor corruption under the frozen latent AR(1) process, Gaussian physical response noise, univariate linear physical system, OLS learner, gate settings, magnitudes, durations, and seed distribution.

It does not establish robustness to biased sensors, stuck sensors, dropouts, quantization, correlated sensor noise, multivariate sensor faults, calibration drift, missing data, adversarial manipulation, arbitrary errors-in-variables settings, real digital twins, or arbitrary physical concept drift.

No result may be used to claim general superiority of persistence gating or general sensor-fault robustness.