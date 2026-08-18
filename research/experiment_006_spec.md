# Experiment 006 — Measurement-Noise Corruption Without System Drift

**Status:** prospective specification; committed before Experiment 006 implementation and evaluation.

## Motivation

Experiments 001–004 tested changes in the response mechanism or model specification, while Experiment 005 tested covariate shift with an unchanged conditional mean. A major remaining boundary is measurement corruption: residual error can increase because observations become noisier even when the underlying system dynamics and conditional mean remain unchanged.

Experiment 006 is a falsification-oriented sensor-noise test. It asks whether residual-threshold adaptation gates respond to increased observation noise as though the model itself requires updating, and whether persistence confirmation suppresses that potentially futile adaptation.

## Scientific question

When the true conditional mean remains `E[y*|x] = 1.5 x` but the observed outcome sensor acquires additional zero-mean Gaussian corruption, does persistence confirmation reduce reactive adaptation relative to simple threshold gating, and what prediction-loss or adaptation-burden consequence accompanies that conservatism?

A secondary question is whether persistent measurement corruption produces repeated refitting even though refitting cannot remove the added sensor variance.

## Shared system and frozen gate settings

Retain from prior experiments:

- `N_STEPS = 1200`;
- event onset `t=401`;
- initial fit interval `t=101..300`;
- AR(1) input process `x_t = 0.8 x_{t-1} + eta_t`, `eta_t ~ Normal(0, 0.5^2)`;
- the same linear OLS learner with slope and intercept only;
- underlying true response slope `1.5`;
- baseline process noise standard deviation `0.5`;
- the same test-then-train chronology;
- rolling squared-error window `20`;
- refit window `100`;
- persistence count `3`;
- the same stable-data threshold `tau` produced by `calibrate_tau()`;
- strategies: frozen, continuous, threshold, persistence.

No gate parameter is retuned for measurement corruption.

Evaluation seeds are frozen as `6000..6199`, disjoint from all prior calibration and evaluation seeds.

## Latent clean response

For every time step, generate the underlying clean response

`y*_t = 1.5 x_t + epsilon_t`,

where

`epsilon_t ~ Normal(0, 0.5^2)`.

The underlying system law does not change at the event.

## Measurement-corruption intervention

Observed outcomes are

`y_t = y*_t + c_t`,

where the sensor-corruption term is

`c_t = sigma_c,t * u_t`,

and

`u_t ~ Normal(0, 1)`.

The corruption draws `u_t` are generated independently of the input and baseline process-noise draws and are shared across matched strategies and event-duration cells for a given seed and magnitude.

Evaluate corruption standard deviations:

- `sigma_c ∈ {0.5, 1.0, 2.0}`.

For each magnitude evaluate two event classes:

1. **Transient corruption:** `sigma_c,t = sigma_c` exactly for `t=401..420`, then `sigma_c,t = 0` from `t=421` onward.
2. **Persistent corruption:** `sigma_c,t = sigma_c` for `t=401..1200`.

This yields 6 prospectively frozen cells.

For a given `seed, sigma_c`, transient and persistent observed streams must be identical through `t=420`. All four strategies within a cell receive exactly the same `x`, clean response, corruption realization, and observed `y` sequence.

## What remains unchanged

The underlying conditional mean remains

`E[y*_t | x_t] = 1.5 x_t`

throughout. The true slope, intercept, input process, baseline process-noise distribution, and learner model class do not change.

The intervention changes only measurement variance in the observed outcome. Therefore a gate response must not be described as detection of true parameter drift.

The evaluator may log `clean_y`, `sensor_unit_noise`, and `true_sigma_c`, but these are evaluator-only quantities and may not be used by the gate.

## Primary outcomes

### Transient-corruption cells

For each `sigma_c`, report the probability that each strategy adapts at least once during `t=401..420`.

The primary paired gate contrast is

`persistence adaptation indicator - threshold adaptation indicator`.

Report the paired mean difference and a 95% paired whole-seed bootstrap confidence interval.

### Persistent-corruption cells

For each `sigma_c`, report cumulative squared prediction loss against the **observed outcome** over `t=401..600`, matching the actual residual signal available to the gate.

The primary paired gate contrast is

`persistence observed-loss - threshold observed-loss`.

Report the paired mean difference and a 95% paired whole-seed bootstrap confidence interval.

## Clean-system prediction outcome

Because observed measurement corruption is irreducible by the learner, also preserve a secondary clean-target squared error

`(y*_t - y_hat_t)^2`

over `t=401..600` and `t=401..1200`.

This separates prediction quality relative to the underlying clean system from unavoidable sensor corruption. It is a secondary diagnostic and does not replace the prespecified observed-loss primary outcome.

For persistent cells report the paired mean difference

`persistence clean-target loss - threshold clean-target loss`

with a 95% paired whole-seed bootstrap confidence interval.

## Adaptation-burden outcome

For every persistent cell, report post-event adaptation count through `t=1200`.

The prespecified paired burden contrast is

`persistence adaptation count - threshold adaptation count`.

Report the paired mean difference and a 95% paired whole-seed bootstrap confidence interval.

## Secondary outcomes

Per seed/cell/strategy preserve:

- observed cumulative squared prediction loss over `t=401..600` and `t=401..1200`;
- clean-target cumulative squared prediction loss over the same horizons;
- whether adaptation occurs during `t=401..420`;
- first post-event adaptation time;
- adaptation delay from `t=401`;
- adaptation counts over `t=401..600` and `t=401..1200`;
- fitted slope and intercept before and after adaptation events.

Full time-step traces are preserved for audit seeds `6000..6004`. Complete per-seed summaries are preserved for all 6 cells and 200 seeds.

## Inference

The independent experimental unit is the whole generated seed/stream. Strategies are paired within seed and cell. Time steps are serially dependent and are not treated as independent replicates.

All confidence intervals use paired whole-seed bootstrap resampling with `10,000` replicates and deterministic per-cell bootstrap seeds fixed in the evaluation implementation before results are inspected.

No multiplicity-adjusted omnibus superiority claim is planned. Results are interpreted cell-wise as a robustness/falsification map.

## Prospective interpretation rules

Experiment 006 does **not** define success as persistence gating winning every cell.

Evidence of a measurement-noise false-adaptation vulnerability would consist of substantial gate activation or repeated adaptation despite the unchanged underlying system law.

If persistence reduces transient adaptation and/or persistent adaptation burden relative to threshold, that supports its interpretation as a conservative adaptation-rate limiter under sensor corruption.

If that reduction also improves clean-target prediction loss, it supports a bounded benefit from avoiding refits to corrupted observations.

If persistence reduces adaptation burden but worsens clean-target loss, the familiar conservatism-versus-responsiveness tradeoff remains relevant even under corruption.

If observed-loss differences are small while clean-target differences are meaningful, interpretation must emphasize that observed loss contains irreducible sensor variance.

If neither gate reacts materially at small corruption magnitudes, that is a detectability boundary and is not grounds for post hoc retuning.

Results must not be described as true system-drift detection because the underlying conditional mean is frozen by design.

## Required audit checks

Before accepting Experiment 006 evidence, independently verify at minimum:

- exact seed/cell/strategy coverage;
- matched `x`, baseline `epsilon`, corruption-unit-noise, clean response, and observed response across strategies within each seed/cell;
- identical transient and persistent streams through `t=420` within each matched `seed, sigma_c` pair;
- exact AR(1) input equation and innovation standard deviation `0.5`;
- exact clean-response equation `y* = 1.5 x + epsilon`;
- `true_sigma_c = 0` before `t=401`;
- transient `true_sigma_c = sigma_c` exactly for `t=401..420` and zero thereafter;
- persistent `true_sigma_c = sigma_c` through `t=1200`;
- exact observed-response equation `y = clean_y + true_sigma_c * sensor_unit_noise`;
- unchanged true slope and learner model class;
- unchanged frozen `tau`, rolling window, refit window, and persistence count;
- test-then-train prediction chronology at every audited time step;
- exact reproduction of observed-loss, clean-target-loss, adaptation, burden, and bootstrap contrasts from seed-level evidence.

## Claim boundary

Experiment 006 can establish evidence only for the specified additive zero-mean Gaussian outcome-measurement corruption under the frozen AR(1) input process, baseline Gaussian process noise, linear learner, gate settings, corruption magnitudes, durations, and seed distribution.

It does not establish robustness to biased sensors, input-sensor corruption, missingness, quantization, correlated or heavy-tailed noise, adversarial manipulation, multivariate sensor faults, real digital twins, or arbitrary data-quality failures.

No result from Experiment 006 may be used to claim general superiority of persistence gating or general sensor-fault robustness.