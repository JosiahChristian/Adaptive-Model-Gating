# Experiment 008 — Sensor-Health-Aware Adaptation Gating

**Status:** prospective specification; frozen before Experiment 008 implementation and evaluation.

## Motivation

Experiments 006 and 007 identified two distinct failures of residual-only adaptation gating when the latent physical system is unchanged:

- outcome-sensor corruption can trigger false adaptation and degrade clean-target performance;
- input-sensor corruption can trigger repeated refitting on contaminated predictors and severely damage coefficient integrity.

Persistence confirmation reduces refit burden but is not a sensor-fault discriminator. Experiment 008 therefore tests a principled intervention: separate model-error evidence from independently available sensor-health evidence before allowing adaptation.

The intervention must not use evaluator-only latent truth. It receives only a learner-visible primary input sensor, an independently noisy redundant reference sensor, observed outcomes, and legitimate past history.

## Scientific question

Can a sensor-health-aware persistence gate suppress adaptation caused by primary input-sensor corruption while retaining responsiveness to genuine physical response drift?

The study has two necessary halves:

1. **fault rejection:** under unchanged physical dynamics and corrupted primary input sensing, does the health-aware gate reduce false adaptation, coefficient contamination, and clean/latent prediction degradation relative to ordinary persistence gating?
2. **drift retention:** when the physical response slope genuinely changes but sensor agreement remains healthy, does the health-aware gate preserve adaptation responsiveness and prediction quality rather than vetoing legitimate adaptation?

A result on fault cells alone is insufficient. The intervention is scientifically useful only if fault rejection is not purchased by indiscriminate refusal to adapt.

## Shared timing, learner, and residual gate settings

Retain:

- `N_STEPS = 1200`;
- event onset `t=401`;
- initial fit interval `t=101..300`;
- linear OLS learner with slope and intercept;
- baseline physical slope `1.5`;
- physical response noise SD `0.5`;
- rolling prediction-MSE window `20`;
- refit window `100`;
- residual persistence count `3`;
- the same residual threshold `tau = calibrate_tau()` used by prior experiments;
- strict test-then-train chronology.

No existing residual-gate parameter is retuned.

Evaluation seeds are frozen as `8000..8199`, disjoint from all prior calibration and evaluation seeds.

## Latent physical input and response

Generate latent input

`x_true,t = 0.8 x_true,t-1 + eta_t`,

with `eta_t ~ Normal(0, 0.5^2)` and `x_true,0 = 0`.

Physical outcomes follow

`y_t = a_t x_true,t + epsilon_t`,

with `epsilon_t ~ Normal(0, 0.5^2)`.

Before the event, `a_t = 1.5`.

## Learner-visible redundant sensing

The adaptive learner uses a **primary input sensor** `x_primary,t`.

A separate **reference sensor** `x_ref,t` is available only to the sensor-health monitor. It is not evaluator truth and is not used directly in OLS fitting or residual prediction.

Generate an independent reference-sensor noise draw `r_t ~ Normal(0,1)` and fix reference-sensor noise SD

`sigma_ref = 0.05`.

Then

`x_ref,t = x_true,t + 0.05 r_t`.

For the primary sensor, generate an independent unit-noise draw `u_t ~ Normal(0,1)`.

Outside primary-sensor fault intervals,

`x_primary,t = x_true,t`.

During a primary-sensor corruption interval,

`x_primary,t = x_true,t + sigma_x u_t`.

The learner, residual gate, and all OLS refits use `x_primary`, never `x_true` or `x_ref`.

The health monitor may use current and past `(x_primary, x_ref)` values only.

## Sensor-health statistic and frozen threshold

Define sensor disagreement

`d_t = x_primary,t - x_ref,t`.

Define the rolling sensor-disagreement MSE over the most recent 20 samples:

`H_t = mean(d_j^2)` over the same 20-step rolling window convention used by the residual statistic.

Calibrate a sensor-health threshold `kappa` **before evaluation** from disjoint stable calibration seeds `200..399` using the exact stable sensing law above (`x_primary=x_true`, `x_ref=x_true+0.05 r`).

Pool all eligible 20-step rolling `H_t` values from those calibration streams and define

`kappa = empirical 0.99 quantile` using the repository's existing deterministic empirical-quantile convention.

The calibration seeds `200..399` are used only for `kappa`; evaluation remains `8000..8199`.

No Experiment 008 evaluation result may be inspected before `kappa` calibration code and all evaluation rules are committed.

## Health-aware gate

Compare five strategies:

1. **frozen** — never refit;
2. **continuous** — existing continuous refit baseline;
3. **threshold** — existing residual-threshold gate;
4. **persistence** — existing 3-consecutive-exceedance residual persistence gate;
5. **health_persistence** — same residual threshold, same 3-consecutive residual persistence requirement, plus a sensor-health veto.

For `health_persistence`, at time `t`:

- update the residual persistence state exactly as the ordinary persistence gate does;
- compute `H_t` only from learner-visible primary/reference sensor history;
- declare `sensor_unhealthy_t = 1` iff a 20-sample `H_t` exists and `H_t > kappa`;
- permit a refit only when the ordinary persistence condition is satisfied **and** `sensor_unhealthy_t = 0`.

If the residual persistence condition is satisfied while the sensor is unhealthy, the adaptation is vetoed for that time step. The residual persistence streak then resets exactly as it would after an ordinary persistence adaptation attempt. This reset rule is frozen to avoid repeated immediate attempts during a known-unhealthy interval.

The gate may not use `x_true`, `true_sigma_x`, `true_a`, event class, event duration, future values, or evaluator-only diagnostics.

## Frozen evaluation cells

### A. Primary-input sensor-fault cells

Keep the physical response law unchanged: `a_t = 1.5` for all `t`.

Evaluate `sigma_x ∈ {0.25, 0.5, 1.0}` under:

- **transient fault:** corruption exactly `t=401..420`, then `sigma_x,t=0`;
- **persistent fault:** corruption `t=401..1200`.

This yields 6 sensor-fault cells.

### B. Genuine physical-drift cells

Keep both sensors healthy for the entire stream (`x_primary=x_true`; reference sensor retains only its fixed SD `0.05` noise).

At `t=401`, change the true physical slope persistently to

`a_t = 1.5 + delta_a`,

with

`delta_a ∈ {0.25, 0.5, 1.0}`.

This yields 3 genuine-drift cells.

Total frozen evaluation map: 9 cells × 5 strategies × 200 seeds.

For each seed and magnitude, stochastic latent-input, physical-noise, primary-sensor-unit-noise, and reference-sensor-noise draws are generated once and shared across matched strategies. Sensor-fault transient/persistent streams with the same `seed, sigma_x` must be identical through `t=420`.

## Primary outcomes

### Fault rejection: transient sensor-fault cells

For each `sigma_x`, report adaptation probability during the true fault interval `t=401..420`.

Primary paired intervention contrast:

`health_persistence adaptation indicator - persistence adaptation indicator`.

Report paired mean difference and 95% paired whole-seed bootstrap interval.

### Fault rejection: persistent sensor-fault cells

Primary physical-integrity endpoint:

`abs(final_fitted_slope - 1.5)` at `t=1200`.

Primary paired intervention contrast:

`health_persistence final slope-error magnitude - persistence final slope-error magnitude`.

Report paired mean difference and 95% paired whole-seed bootstrap interval.

Also report operational loss, latent-input diagnostic loss, and adaptation burden.

### Drift retention: genuine physical-drift cells

Primary responsiveness endpoint: cumulative squared operational prediction loss over `t=401..600`.

Primary paired intervention contrast:

`health_persistence loss - persistence loss`.

Report paired mean difference and 95% paired whole-seed bootstrap interval.

Also report adaptation probability by `t=420`, first adaptation time/delay, and adaptation burden.

## Sensor-health classification diagnostics

Because true fault labels are evaluator-only and known in simulation, report—but never feed to the gate—the following diagnostics:

- fraction of fault-active time steps classified `sensor_unhealthy=1`;
- fraction of healthy time steps classified `sensor_unhealthy=1`;
- per-seed whether the monitor flags at least once during `t=401..420`;
- time from event onset to first sensor-unhealthy flag.

These are mechanism diagnostics, not independent experimental replicates.

## Prediction and coefficient diagnostics

For every strategy preserve:

- operational loss using learner-visible `x_primary`;
- evaluator-only latent-input prediction loss using the same current model evaluated at `x_true`;
- adaptation counts and timing;
- fitted slope/intercept trajectory;
- final slope and absolute error relative to the true current physical slope.

For sensor-fault cells the physical slope target is always `1.5`.
For genuine-drift cells the final physical slope target is `1.5 + delta_a`.

## Success and falsification rules

Experiment 008 does **not** define success as the new gate winning every endpoint.

A bounded useful intervention requires both:

1. **fault rejection evidence:** health-aware persistence materially reduces false adaptation and/or coefficient damage under sensor faults relative to ordinary persistence; and
2. **drift retention evidence:** it does not materially impair genuine-drift responsiveness across the frozen drift cells.

Specific interpretations:

- If fault adaptation and coefficient contamination fall while genuine-drift loss/adaptation remain comparable, this supports a bounded benefit from separating sensor-health evidence from model-error evidence.
- If fault rejection improves but genuine-drift response becomes materially worse, the intervention merely moves the conservatism tradeoff and is not a clean discriminator.
- If the health monitor fails to identify fault cells, the proposed sensor-health statistic is inadequate.
- If health-aware persistence still contaminates coefficients under faults despite correctly flagging the sensor, the veto/refit mechanism is inadequate.
- If ordinary persistence already matches health-aware persistence, redundant health evidence adds little under this frozen design.

No result may be generalized beyond the explicit sensing architecture and fault/drift families tested.

## Inference

The whole seed/stream is the independent unit. Strategies are paired within seed and cell. Use 10,000-replicate paired whole-seed bootstrap intervals with deterministic per-cell bootstrap seeds frozen in the evaluation runner before results are inspected.

No omnibus superiority claim is planned. Cell-wise contrasts form a falsification map.

## Required audit checks

Before accepting Experiment 008 evidence independently verify at minimum:

- exact 9-cell × 5-strategy × 200-seed coverage;
- evaluation seeds exactly `8000..8199` and health-calibration seeds exactly `200..399`;
- exact `kappa` reproduction from stable calibration streams without evaluation-seed leakage;
- matched latent/input/noise draws across strategies;
- transient/persistent fault streams identical through `t=420`;
- exact latent AR(1), physical-response, primary-sensor, and reference-sensor equations;
- reference-sensor SD exactly `0.05` and independence from primary sensor noise;
- learner/refits use `x_primary` only;
- health monitor uses only learner-visible `x_primary` and `x_ref` history;
- rolling health statistic and `sensor_unhealthy` decisions reproduce exactly;
- health-aware veto and streak-reset behavior reproduce exactly;
- unchanged residual `tau`, rolling window, refit window, persistence count, and OLS operator;
- test-then-train chronology;
- exact primary and secondary paired contrasts and bootstrap intervals.

Full traces are required for audit seeds `8000..8004`; complete per-seed summaries are required for all cells.

## Claim boundary

Experiment 008 can establish evidence only for a redundant-sensor architecture with one primary input sensor, one independent low-noise reference sensor, additive Gaussian primary-sensor faults, the specified persistent linear physical drifts, the frozen AR(1) input process, Gaussian response noise, linear OLS learner, calibrated disagreement statistic, thresholds, event timing, magnitudes, and seed distributions.

It does not establish general sensor-fault diagnosis, robustness to common-mode sensor failure, biased or drifting reference sensors, correlated sensor faults, sensor dropouts, multivariate state estimation, nonlinear systems, adversarial manipulation, arbitrary concept drift, or real digital twins.

The redundant reference sensor is additional information not available to Experiments 001–007; any benefit must be attributed to that explicit sensing assumption rather than to persistence gating alone.