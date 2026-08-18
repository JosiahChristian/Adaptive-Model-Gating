# Experiment 009 — Reference-Sensor Failure and Common-Mode Corruption

**Status:** prospective specification; frozen before Experiment 009 implementation and evaluation.

## Motivation

Experiment 008 showed that sensor-health-aware persistence can suppress false adaptation and preserve coefficient integrity when the primary sensor is corrupted but an independent low-noise reference sensor remains trustworthy. That benefit depends on an explicit sensing assumption: the reference channel must provide information that is at least partly independent of the primary failure.

Experiment 009 attacks that assumption directly with two qualitatively distinct failure modes:

1. **common-mode corruption**, where both primary and reference sensors share the same corrupting component, so sensor disagreement may remain deceptively healthy while the learner receives corrupted inputs;
2. **reference-sensor corruption during genuine physical drift**, where the primary sensor remains correct but the reference channel becomes unreliable, potentially causing the health-aware gate to veto legitimate adaptation.

The purpose is not to make the intervention look robust. The purpose is to identify where the Experiment 008 architecture fails and whether those failures are detectable from its own logged health signals.

## Scientific questions

### A. Common-mode fault escape

When the same additive corruption enters both primary and reference sensors, does the health monitor fail to flag sensor unhealthiness, allowing the health-aware gate to behave like ordinary persistence and contaminate the fitted physical coefficient?

### B. Reference-fault over-veto under real drift

When the primary sensor is healthy and the physical slope genuinely changes, but the reference sensor is corrupted, does the health-aware gate incorrectly veto needed adaptation and materially worsen drift responsiveness relative to ordinary persistence?

## Shared model, timing, and residual settings

Retain unchanged:

- `N_STEPS = 1200`;
- event onset `t=401`;
- initial fit interval `t=101..300`;
- latent physical input AR(1) coefficient `0.8` with innovation SD `0.5`;
- linear OLS learner with slope and intercept;
- baseline physical slope `1.5`;
- physical response noise SD `0.5`;
- rolling residual-MSE window `20`;
- refit window `100`;
- residual persistence count `3`;
- residual threshold `tau = calibrate_tau()`;
- health threshold `kappa = calibrate_kappa()` from the already frozen Experiment 008 stable sensing architecture and calibration seeds `200..399`;
- nominal reference-sensor SD `0.05`;
- strict test-then-train chronology.

No residual or health threshold is retuned.

Evaluation seeds are frozen as `9000..9199`, disjoint from all prior calibration and evaluation seeds.

## Latent physical process

Generate

`x_true,t = 0.8 x_true,t-1 + eta_t`,

with `eta_t ~ Normal(0, 0.5^2)` and `x_true,0 = 0`.

Generate outcomes

`y_t = a_t x_true,t + epsilon_t`,

with `epsilon_t ~ Normal(0, 0.5^2)`.

## Sensor noise draws

For every seed generate independent standard-normal streams:

- `u_t` — common/primary corruption draw;
- `r_t` — nominal reference-noise draw;
- `q_t` — reference-fault-only corruption draw.

All strategies within a matched seed/cell share identical latent and noise realizations.

## Family A — persistent common-mode sensor corruption

Keep the physical system unchanged:

`a_t = 1.5` for all `t`.

For `t < 401`:

- `x_primary,t = x_true,t`;
- `x_ref,t = x_true,t + 0.05 r_t`.

For `t >= 401`, inject the same corruption into both sensors:

- `x_primary,t = x_true,t + sigma_cm u_t`;
- `x_ref,t = x_true,t + sigma_cm u_t + 0.05 r_t`.

Evaluate

`sigma_cm ∈ {0.25, 0.5, 1.0}`.

Because the shared corruption cancels from `x_primary - x_ref`, the expected disagreement statistic remains governed primarily by the nominal `0.05` reference noise. This is intentionally a hard falsification of disagreement-only health monitoring.

The learner and all OLS refits use `x_primary` only.

## Family B — genuine physical drift plus persistent reference-sensor corruption

Keep the primary sensor healthy:

`x_primary,t = x_true,t` for all `t`.

At `t=401`, change the physical slope persistently to

`a_t = 1.5 + delta_a`.

Simultaneously corrupt only the reference sensor:

`x_ref,t = x_true,t + 0.05 r_t + sigma_ref_fault q_t`, for `t>=401`.

Before `t=401`, reference sensing remains nominal:

`x_ref,t = x_true,t + 0.05 r_t`.

Evaluate matched magnitudes

`delta_a = sigma_ref_fault ∈ {0.25, 0.5, 1.0}`.

This family asks whether the health-aware gate confuses reference-channel degradation with primary-sensor unreliability and therefore vetoes legitimate model adaptation.

## Frozen evaluation map

Total cells: 6.

- 3 persistent common-mode-fault cells: `sigma_cm ∈ {0.25, 0.5, 1.0}`;
- 3 persistent physical-drift + reference-fault cells: matched `delta_a = sigma_ref_fault ∈ {0.25, 0.5, 1.0}`.

Strategies:

1. `frozen`;
2. `continuous`;
3. `threshold`;
4. `persistence`;
5. `health_persistence`.

Total evaluation: 6 cells × 5 strategies × 200 seeds.

## Learner-visible information

The learner and residual gate receive only `(x_primary, y)` plus legitimate model/history state.

The health-aware gate additionally receives `x_ref` history and the frozen `kappa`.

No strategy may use:

- `x_true`;
- `true_sigma_cm`;
- `true_sigma_ref_fault`;
- `true_a`;
- fault-family labels;
- latent noise draws;
- future observations or evaluator-only diagnostics.

## Family A primary endpoint — coefficient integrity under common-mode fault

For each common-mode cell, primary endpoint:

`abs(final_fitted_slope - 1.5)` at `t=1200`.

Primary paired intervention contrast:

`health_persistence slope-error magnitude - persistence slope-error magnitude`.

Report mean paired difference and 95% paired whole-seed bootstrap interval.

Also report:

- fraction of post-event steps flagged `sensor_unhealthy`;
- adaptation burden through `t=1200`;
- operational loss over `t=401..600`;
- latent-input diagnostic loss over `t=401..600`.

Interpretation rule: if health flags remain near nominal while coefficient contamination is not improved relative to ordinary persistence, that is evidence of common-mode fault escape.

## Family B primary endpoint — drift responsiveness under reference fault

For each drift-plus-reference-fault cell, primary endpoint:

cumulative operational squared prediction loss over `t=401..600`.

Primary paired intervention contrast:

`health_persistence loss - persistence loss`.

Report mean paired difference and 95% paired whole-seed bootstrap interval.

Also report:

- adaptation probability by `t=420`;
- first adaptation delay among seeds where both strategies adapt;
- adaptation burden through `t=1200`;
- fraction of post-event steps flagged `sensor_unhealthy`;
- final slope error relative to the true final physical slope `1.5 + delta_a`.

Interpretation rule: materially higher loss and/or materially lower adaptation under health-aware persistence indicates over-veto caused by reference-sensor failure.

## Counterfactual latent-input diagnostic

For all cells, evaluate each current fitted model on `x_true` as an evaluator-only diagnostic:

`y_hat_latent,t = slope_before*x_true,t + intercept_before`.

Preserve latent-input squared loss over `t=401..600` and `t=401..1200`.

This quantity is never gate-visible.

## Health-monitor diagnostics

Preserve per time step:

- `sensor_health_mse`;
- `sensor_unhealthy`;
- `health_veto`;
- primary-reference disagreement;
- first post-event health flag and delay.

For Family A, the key mechanism diagnostic is whether common-mode corruption remains invisible to disagreement monitoring.

For Family B, the key mechanism diagnostic is whether reference corruption generates persistent health flags despite a healthy primary sensor.

## Inference

The independent unit is the whole seed/stream. Strategies are paired within seed and cell. Use `10,000`-replicate paired whole-seed bootstrap intervals with deterministic per-cell bootstrap seeds frozen in the evaluation runner before results are inspected.

No omnibus superiority claim is planned.

## Prospective interpretation rules

Experiment 009 is explicitly a falsification study of the Experiment 008 architecture.

- If common-mode corruption escapes health monitoring and health-aware persistence contaminates coefficients similarly to ordinary persistence, the redundant-disagreement intervention has a bounded common-mode failure.
- If reference-only corruption during genuine drift causes health-aware persistence to veto legitimate adaptation and worsen prediction loss, the intervention depends critically on reference-channel trustworthiness.
- If neither failure occurs, that would support stronger-than-expected robustness under these specific fault constructions.
- Negative findings must be preserved without redefining success criteria after results are observed.

## Required audit checks

Before accepting evidence verify at minimum:

- exact 6-cell × 5-strategy × 200-seed coverage;
- evaluation seeds exactly `9000..9199`;
- unchanged `tau` and exact reproduction of `kappa` from Experiment 008 calibration rules/seeds;
- matched latent and noise realizations across strategies;
- exact latent AR(1) and physical response equations;
- exact Family A equations, including identical shared `sigma_cm*u_t` corruption in both sensors;
- exact Family B equations, including healthy `x_primary=x_true`, genuine slope drift, and reference-only `sigma_ref_fault*q_t` corruption;
- nominal reference SD `0.05` before all events;
- learner/refits use `x_primary` only;
- health monitor uses only `x_primary` and `x_ref` history;
- rolling health statistic, `sensor_unhealthy`, veto behavior, and streak reset reproduce exactly;
- unchanged residual persistence and OLS logic;
- test-then-train chronology;
- exact primary/secondary contrasts and bootstrap intervals.

Full time-step traces are required for audit seeds `9000..9004`; complete per-seed summaries are required for every cell.

## Claim boundary

Experiment 009 can establish evidence only for the specified additive-Gaussian common-mode and reference-only sensor faults, the redundant two-sensor architecture, persistent linear slope drifts, univariate AR(1) input process, OLS learner, frozen residual and health thresholds, timing, magnitudes, and seed distribution.

It does not establish behavior for arbitrary correlated faults, slowly biased sensors, sensor dropouts, Byzantine/adversarial sensors, more than two sensors, voting or state-estimation architectures, nonlinear dynamics, multivariate systems, or real digital twins.
