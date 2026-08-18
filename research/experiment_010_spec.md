# Experiment 010 — Three-Sensor Fault-Tolerant Adaptation Gating

**Status:** prospective specification; frozen before Experiment 010 implementation and evaluation.

## Motivation

Experiment 008 showed that a two-sensor disagreement veto can suppress false adaptation and preserve coefficient integrity when the primary sensor alone is corrupted and the reference sensor is independently trustworthy. Experiment 009 then falsified any broad interpretation of that result: common-mode corruption can evade pairwise disagreement monitoring, and a corrupted reference sensor can wrongly veto legitimate physical-drift adaptation.

Experiment 010 tests a stronger but still explicit sensing architecture: one primary learner sensor plus two independently noisy reference sensors. The intervention uses majority/consistency structure to distinguish a single bad channel from genuine model drift. It is not allowed to use latent truth, event labels, future observations, or any evaluator-only variable.

The experiment also preserves a deliberate common-mode failure family. A three-sensor agreement scheme should not be credited with robustness against a disturbance that shifts all channels together unless the data actually support that claim.

## Scientific question

Can a three-sensor consistency gate:

1. reject primary-sensor-driven false adaptation when two independent references agree;
2. avoid the Experiment 009 over-veto failure when one reference sensor is bad but the primary sensor and the other reference agree;
3. retain ordinary persistence responsiveness to genuine physical drift; and
4. expose, rather than conceal, any residual vulnerability to all-channel common-mode corruption?

## Shared learner and timing

Retain unchanged:

- `N_STEPS = 1200`;
- event onset `t=401`;
- initial fit interval `t=101..300`;
- univariate linear OLS learner with slope and intercept;
- baseline physical slope `1.5`;
- physical response-noise SD `0.5`;
- rolling residual-MSE window `20`;
- refit window `100`;
- persistence count `3`;
- residual threshold `tau = calibrate_tau()` from all prior experiments;
- strict test-then-train chronology.

No residual-gate parameter is retuned.

Evaluation seeds are frozen as `10000..10199`, disjoint from prior calibration and evaluation seeds.

## Latent physical process

Generate latent physical input

`x_true,t = 0.8 x_true,t-1 + eta_t`,

with `eta_t ~ Normal(0, 0.5^2)` and `x_true,0=0`.

Generate physical outcome

`y_t = a_t x_true,t + epsilon_t`,

with `epsilon_t ~ Normal(0,0.5^2)`.

Before the event, `a_t=1.5`.

## Three learner-visible sensors

The learner receives only the **primary** sensor `x_p` for prediction and OLS refitting.

Two redundant reference channels `x_r1` and `x_r2` are available only to the health/consistency monitor.

Outside fault intervals:

- `x_p = x_true`;
- `x_r1 = x_true + 0.05 r1`, with `r1 ~ Normal(0,1)`;
- `x_r2 = x_true + 0.05 r2`, with `r2 ~ Normal(0,1)`;

where all innovation, physical-noise, and sensor-noise draws are mutually independent except where a common-mode intervention explicitly reuses the same corruption draw.

The learner and refit operator must never use `x_true`, `x_r1`, or `x_r2`; they use `x_p` only.

## Pairwise consistency statistics

For each pair `(i,j)` in `{(p,r1),(p,r2),(r1,r2)}`, define rolling disagreement MSE over the most recent 20 samples:

`H_ij,t = mean((x_i - x_j)^2)`.

Reuse the exact Experiment 008 stable calibration framework with seeds `200..399`, now calibrating one common pairwise threshold `kappa3` from pooled stable reference-like pairwise disagreement values under the frozen healthy triad sensing law. The empirical 0.99 quantile convention is unchanged. Evaluation seeds may not participate in `kappa3` calibration.

## Triad classification rule

At time `t`, once all three 20-step pairwise statistics exist, classify the **primary sensor as bad** iff:

- `H_p,r1 > kappa3`,
- `H_p,r2 > kappa3`, and
- `H_r1,r2 <= kappa3`.

Interpretation: both references disagree with the primary while agreeing with each other.

Classify **reference 1 as bad** iff:

- `H_p,r1 > kappa3`,
- `H_r1,r2 > kappa3`, and
- `H_p,r2 <= kappa3`.

Classify **reference 2 as bad** analogously.

Otherwise classify the triad state as `no_single_channel_diagnosis`.

The adaptation veto is triggered **only** by `primary_bad=1`. A diagnosed bad reference must not veto model adaptation, because the learner uses the primary sensor and the other reference can still support its health.

## Triad persistence strategy

Add strategy `triad_persistence` alongside:

- frozen;
- continuous;
- threshold;
- persistence;
- health_persistence (Experiment 008 two-sensor comparator);
- triad_persistence.

`triad_persistence` uses the same residual threshold and three-consecutive-exceedance logic as ordinary persistence. When residual persistence becomes ready:

- if `primary_bad=0`, permit the ordinary OLS refit on `x_p`;
- if `primary_bad=1`, veto the refit;
- reset the residual persistence streak after either a permitted or vetoed adaptation attempt, matching the Experiment 008 intervention convention.

The gate may use only current/past `x_p`, `x_r1`, `x_r2`, observed `y`, residual history, and model state.

## Frozen evaluation families

Evaluate three persistent event families at magnitudes `m ∈ {0.25, 0.5, 1.0}`.

### A. Primary-only sensor fault

Physical law remains unchanged: `a_t=1.5`.

For `t>=401`:

- `x_p = x_true + m*u`;
- `x_r1 = x_true + 0.05*r1`;
- `x_r2 = x_true + 0.05*r2`.

This tests whether the triad correctly vetoes false adaptation and preserves coefficient integrity.

### B. Genuine physical drift plus reference-1 fault

Primary sensor remains healthy. At `t>=401`:

- physical slope becomes `a_t = 1.5 + m`;
- `x_p = x_true`;
- `x_r1 = x_true + 0.05*r1 + m*v`;
- `x_r2 = x_true + 0.05*r2`.

Here `v ~ Normal(0,1)` is independent reference-fault noise. This family attacks the exact Experiment 009 over-veto failure. The triad should identify reference 1 as the outlier and must not veto legitimate drift adaptation merely because one reference is bad.

### C. All-channel common-mode corruption

Physical law remains unchanged: `a_t=1.5`.

At `t>=401`, generate one shared corruption draw `c_t ~ Normal(0,1)` and apply:

- `x_p = x_true + m*c_t`;
- `x_r1 = x_true + 0.05*r1 + m*c_t`;
- `x_r2 = x_true + 0.05*r2 + m*c_t`.

Because all channels share the same corruption component, pairwise disagreement may remain near the healthy regime. This family is included prospectively as a likely failure boundary, not as a hidden post hoc challenge.

Total frozen map: 9 cells × 6 strategies × 200 seeds.

## Primary outcomes

### Primary-only fault cells

Primary intervention endpoint: final absolute slope error relative to `1.5`.

Primary paired contrast:

`triad_persistence final slope-error - health_persistence final slope-error`.

A negative contrast supports added robustness from the third sensor relative to the two-sensor architecture.

Also compare triad versus ordinary persistence for adaptation burden, operational loss, and latent-input loss.

### Drift + reference-1 fault cells

Primary responsiveness endpoint: cumulative operational loss over `t=401..600`.

Primary paired contrast:

`triad_persistence loss - health_persistence loss`.

A strongly negative contrast would demonstrate recovery from the two-sensor over-veto failure.

Also report adaptation probability by `t=420`, first adaptation delay, adaptation burden, final slope error relative to `1.5+m`, and reference-1 diagnosis frequency.

### Common-mode cells

Primary failure-boundary endpoint: final absolute slope error relative to `1.5`.

Primary paired contrast:

`triad_persistence final slope-error - ordinary persistence final slope-error`.

If the interval includes zero while all channels remain mutually consistent, that supports the expected limitation: three-channel agreement alone does not identify common-mode corruption.

## Diagnostic outcomes

Preserve per seed/cell/strategy:

- operational loss over `401..600` and `401..1200`;
- evaluator-only latent-input loss over the same horizons;
- adaptation indicator over `401..420`;
- first adaptation time and delay;
- adaptation counts through `600` and `1200`;
- primary-bad, reference-1-bad, reference-2-bad diagnosis fractions and onset flags;
- triad veto count;
- all three rolling pairwise health statistics;
- final slope and final absolute slope error relative to the true final physical slope.

Full time-step traces are required for audit seeds `10000..10004`; complete seed summaries are required for all cells.

## Inference

Whole seed/stream is the independent unit. Strategies are paired within seed/cell. Use 10,000-replicate paired whole-seed bootstrap intervals with deterministic per-cell bootstrap seeds frozen in the evaluation runner before results are inspected.

No omnibus superiority claim is planned.

## Prospective interpretation rules

A bounded successful intervention requires all of the following:

1. primary-only fault cells: triad_persistence materially reduces coefficient contamination and false refitting;
2. drift-plus-reference-fault cells: triad_persistence restores legitimate adaptation relative to two-sensor health_persistence;
3. healthy/reference-fault diagnosis behavior matches the intended single-channel logic without latent-truth access;
4. common-mode limitations are reported faithfully rather than treated as success.

If triad_persistence suppresses genuine drift because one reference fails, it does not solve Experiment 009.

If it protects against single-channel faults but fails under common-mode corruption, the correct claim is fault tolerance to **one-channel-at-a-time sensing faults under two-channel agreement**, not general sensor-fault robustness.

## Required audit checks

Before accepting evidence independently verify at minimum:

- exact 9-cell × 6-strategy × 200-seed coverage;
- seeds exactly `10000..10199`;
- triad calibration seeds exactly `200..399`, with no evaluation leakage;
- exact `kappa3` reproduction;
- matched latent/input/response/sensor-noise draws across strategies;
- exact AR(1) and physical-response equations;
- exact healthy triad sensing equations and reference noise SD `0.05`;
- exact primary-only fault equations;
- exact drift-plus-reference-1-fault equations;
- exact common-mode reuse of the same `c_t` in all three channels;
- learner/refit use of `x_p` only;
- exact pairwise rolling health statistics;
- exact single-channel diagnosis rules;
- veto only when `primary_bad=1`;
- residual persistence streak reset after permitted/vetoed attempts;
- unchanged residual `tau`, rolling window, refit window, persistence count, OLS operator, and chronology;
- exact primary/secondary contrasts and all bootstrap intervals.

## Claim boundary

Experiment 010 can establish evidence only for the specified three-sensor architecture, independent low-noise references, one-channel-at-a-time Gaussian faults, the frozen common-mode family, persistent linear physical drifts, AR(1) latent input, Gaussian response noise, linear OLS learner, thresholds, event timing, magnitudes, and seed distributions.

It does not establish robustness to two simultaneously independent bad channels, Byzantine/adversarial sensors, bias/stuck/dropout faults, non-Gaussian or correlated reference failures beyond the frozen common-mode family, multivariate state estimation, nonlinear dynamics, arbitrary fault isolation, or real digital twins.
