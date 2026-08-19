# Experiment 011 — Independent-Evidence Gating Against Common-Mode Sensor Corruption

**Status:** prospective specification; frozen before Experiment 011 implementation and evaluation.

## Motivation

Experiment 010 established a bounded three-sensor result. Majority/consistency structure can distinguish one bad channel from two agreeing channels, but an all-channel common-mode disturbance remains internally indistinguishable because the same corruption can preserve pairwise agreement. Experiment 011 tests whether a structurally different, independently generated process-side observable can break that common-mode identifiability limit without suppressing adaptation to genuine physical drift.

The new source is deliberately **not** a fourth copy of the learner input sensor. It is an auxiliary observable with a different frozen physical relationship to the latent state and an independent noise/failure pathway. The intervention may use that auxiliary observable only for adaptation gating; prediction and OLS refitting continue to use the primary learner sensor exactly as before.

A deliberate auxiliary-source failure family is preserved prospectively. If common-mode protection works only while the new independent source is trustworthy, that dependency must be reported as the new claim boundary rather than hidden.

## Scientific questions

Can an independent-evidence gate:

1. detect all-three-input common-mode corruption that escapes the Experiment 010 triad agreement monitor;
2. preserve ordinary triad responsiveness to genuine physical slope drift when the auxiliary source is healthy;
3. retain the Experiment 010 protection against primary-only sensor faults; and
4. expose whether failure of the independent auxiliary source creates a new over-veto mode during genuine physical drift?

## Shared learner, process, and timing

Retain unchanged from Experiment 010:

- `N_STEPS = 1200`;
- event onset `t=401`;
- initial fit interval `t=101..300`;
- latent input AR(1) coefficient `0.8`;
- latent innovation SD `0.5`;
- univariate linear OLS learner with slope and intercept;
- baseline physical slope `1.5`;
- physical response-noise SD `0.5`;
- rolling residual-MSE window `20`;
- refit window `100`;
- persistence count `3`;
- residual threshold `tau` unchanged;
- triad pairwise threshold `kappa3` unchanged from Experiment 010;
- nominal reference-sensor SD `0.05`;
- strict test-then-train chronology.

No previously frozen residual, persistence, OLS, or triad parameter may be retuned.

Evaluation seeds are frozen as `11000..11199`, disjoint from all prior calibration and evaluation seeds.

Full time-step traces are required for audit seeds `11000..11004`; complete seed summaries are required for every cell and strategy.

## Latent physical process

Generate

`x_true,t = 0.8 x_true,t-1 + eta_t`,

with `eta_t ~ Normal(0, 0.5^2)` and `x_true,0 = 0`.

Generate the primary physical outcome

`y_t = a_t x_true,t + epsilon_t`,

with `epsilon_t ~ Normal(0, 0.5^2)`.

Before any physical-drift event, `a_t = 1.5`.

## Existing three learner-visible input sensors

Outside fault intervals:

- `x_p = x_true`;
- `x_r1 = x_true + 0.05 r1`;
- `x_r2 = x_true + 0.05 r2`;

where `r1` and `r2` are independent standard-normal streams.

The learner predicts and refits using `x_p` only. The references remain monitor-only.

All Experiment 010 pairwise health statistics and single-channel diagnosis rules are retained exactly:

- `H_p,r1`;
- `H_p,r2`;
- `H_r1,r2`;
- `primary_bad`;
- `reference_1_bad`;
- `reference_2_bad`;
- `no_single_channel_diagnosis`.

Define

`triad_consistent_t = 1`

iff all three currently available 20-step pairwise disagreement MSE values are `<= kappa3`. Otherwise `triad_consistent_t = 0`.

## Structurally independent auxiliary observable

Add one gate-visible process-side observable `z_t` with the frozen healthy law

`z_t = beta * x_true,t + xi_t`,

where

- `beta = 0.8` is fixed and known to the monitor;
- `xi_t ~ Normal(0, 0.08^2)`;
- `xi_t` is independent of latent innovations, physical response noise, all input-sensor noises, and all fault draws.

The monitor may form the normalized auxiliary estimate

`x_a,t = z_t / 0.8`.

Thus the normalized auxiliary noise SD is `0.1` under the healthy law.

This observable is structurally different from the three input channels because it is generated through a separate physical measurement relationship and independent noise/failure pathway. It is never used by the learner for prediction or OLS fitting.

## Anchor-consistency statistic

At each step define the robust triad center

`x_med,t = median(x_p,t, x_r1,t, x_r2,t)`.

Once 20 samples exist, define rolling auxiliary disagreement

`G_t = mean((x_med - x_a)^2)`

over the most recent 20 samples.

The auxiliary monitor is intended to detect a failure mode in which the three input channels remain mutually consistent but jointly disagree with the independent process-side observable.

## Frozen auxiliary calibration

Calibrate one new threshold `lambda_anchor` prospectively using calibration seeds exactly `600..799`, which must be verified during implementation to be disjoint from all evaluation seeds used in Experiments 001–011.

For each calibration seed, generate the fully healthy sensing law for `t=1..300` with no event or physical drift. Compute valid `G_t` values over the stable interval `t=101..300`. Pool those values across calibration seeds and set `lambda_anchor` using the same empirical `0.99` quantile convention used for the previously frozen health thresholds.

Evaluation seeds may not participate in this calibration. `lambda_anchor` may not be retuned after any Experiment 011 evaluation result is inspected.

## Independent-evidence diagnosis rule

Define

`anchor_mismatch_t = 1[G_t > lambda_anchor]`.

Define

`common_mode_suspect_t = 1`

iff both conditions hold:

1. `triad_consistent_t = 1`; and
2. `anchor_mismatch_t = 1`.

The new gate does not claim to know whether disagreement is caused by the three-input family or by the auxiliary source itself. `common_mode_suspect` is therefore an operational consistency state, not latent fault truth.

## Independent-evidence persistence strategy

Add strategy `independent_persistence` alongside the six Experiment 010 strategies:

1. `frozen`;
2. `continuous`;
3. `threshold`;
4. `persistence`;
5. `health_persistence`;
6. `triad_persistence`;
7. `independent_persistence`.

`independent_persistence` uses the same residual threshold and three-consecutive-exceedance logic as ordinary persistence.

When residual persistence becomes ready:

- veto if `primary_bad=1`;
- otherwise veto if `common_mode_suspect=1`;
- otherwise permit the ordinary OLS refit on `x_p` only;
- reset the residual persistence streak after either a permitted or vetoed adaptation attempt, exactly matching the prior intervention chronology.

The strategy may use only current/past `x_p`, `x_r1`, `x_r2`, `z`, observed `y`, residual history, and model state. It may not use latent truth, event labels, fault magnitudes, future observations, or evaluator-only variables.

## Random-stream matching

For every evaluation seed generate matched independent streams for:

- latent innovations `eta`;
- physical response noise `epsilon`;
- reference noises `r1`, `r2`;
- auxiliary healthy noise `xi`;
- primary/common-mode corruption draw `c`;
- primary-only corruption draw `u`;
- auxiliary-fault draw `d`.

All strategies within a seed/cell must share exactly the same underlying realizations.

## Frozen evaluation families

Use magnitudes `m in {0.25, 0.5, 1.0}` unless otherwise stated.

### H. Healthy no-event control

One control cell with no post-401 event:

- `a_t = 1.5` for all `t`;
- all three input sensors remain healthy;
- `z_t = 0.8*x_true,t + xi_t` for all `t`.

This cell measures false auxiliary mismatch, false common-mode suspicion, false veto, and unnecessary adaptation effects.

### A. Genuine physical slope drift with healthy sensing

At `t>=401`:

- `a_t = 1.5 + m`;
- `x_p = x_true`;
- `x_r1 = x_true + 0.05*r1`;
- `x_r2 = x_true + 0.05*r2`;
- `z = 0.8*x_true + xi`.

Because the drift changes the `y`-versus-`x_true` relationship but not the auxiliary `z`-versus-`x_true` relationship, a healthy independent-evidence monitor should remain permissive while residual persistence triggers legitimate adaptation.

### B. All-three-input common-mode corruption with healthy auxiliary source

Physical law remains unchanged: `a_t = 1.5`.

At `t>=401`, generate one shared `c_t ~ Normal(0,1)` and apply:

- `x_p = x_true + m*c_t`;
- `x_r1 = x_true + 0.05*r1 + m*c_t`;
- `x_r2 = x_true + 0.05*r2 + m*c_t`;
- `z = 0.8*x_true + xi`.

This exactly preserves the Experiment 010 common-mode structure across the three input channels while leaving the auxiliary source independent. Pairwise triad disagreement may remain healthy, but `x_med` should diverge from the auxiliary estimate when the corruption is large enough.

### C. Primary-only sensor fault with healthy references and auxiliary source

Physical law remains unchanged: `a_t = 1.5`.

At `t>=401`:

- `x_p = x_true + m*u_t`;
- `x_r1 = x_true + 0.05*r1`;
- `x_r2 = x_true + 0.05*r2`;
- `z = 0.8*x_true + xi`.

This checks that adding the auxiliary pathway does not destroy the Experiment 010 single-primary-fault protection. Because the triad median remains supported by the two healthy references, the new common-mode path should not be required for this family.

### D. Genuine physical drift plus auxiliary-source corruption

At `t>=401`:

- `a_t = 1.5 + m`;
- `x_p = x_true`;
- `x_r1 = x_true + 0.05*r1`;
- `x_r2 = x_true + 0.05*r2`;
- `z = 0.8*x_true + xi + 0.8*m*d_t`, with `d_t ~ Normal(0,1)`.

Equivalently, the normalized auxiliary estimate receives additive corruption of magnitude `m`.

This family deliberately attacks the new architecture. The three input sensors are mutually healthy and support legitimate drift adaptation, while the auxiliary source becomes unreliable. If `independent_persistence` over-vetoes here, the correct conclusion is that the common-mode solution depends on auxiliary-source trustworthiness.

## Frozen evaluation map

Total cells: 13.

- 1 healthy no-event control cell;
- 3 genuine physical-drift cells;
- 3 all-three-input common-mode corruption cells;
- 3 primary-only sensor-fault cells;
- 3 physical-drift + auxiliary-fault cells.

Strategies: 7.

Evaluation total: `13 cells × 7 strategies × 200 seeds = 18,200` seed-strategy summaries.

## Primary outcomes and paired contrasts

### Family B — common-mode corruption

Primary endpoint: final absolute fitted-slope error relative to `1.5`.

Primary paired contrast:

`independent_persistence slope-error - triad_persistence slope-error`.

A materially negative contrast supports the claim that the independent observable breaks the specific Experiment 010 common-mode identifiability limit.

Also report:

- operational loss over `401..600` and `401..1200`;
- evaluator-only latent-input loss over both horizons;
- adaptation burden;
- common-mode-suspect fraction and onset;
- auxiliary mismatch fraction;
- veto count.

### Family A — genuine physical drift

Primary responsiveness endpoint: cumulative operational squared prediction loss over `401..600`.

Primary paired contrast:

`independent_persistence loss - triad_persistence loss`.

Also compute per-seed relative excess loss

`R = (L_independent - L_triad) / max(L_triad, 1e-12)`.

The preregistered non-destruction criterion is that the upper endpoint of the 95% paired whole-seed bootstrap interval for mean `R` is `< 0.10`.

This is a bounded non-inferiority-style rule: the new gate must not increase early drift-response loss by 10% or more on average under the healthy auxiliary law.

Also report adaptation probability by `t=420`, first adaptation delay, adaptation burden, final slope error relative to `1.5+m`, auxiliary mismatch fraction, and veto count.

### Family C — primary-only fault

Primary safeguard endpoint: final absolute fitted-slope error relative to `1.5`.

Primary paired contrast:

`independent_persistence slope-error - triad_persistence slope-error`.

The purpose is regression protection, not a new superiority claim. Report adaptation burden, primary-bad fraction, common-mode-suspect fraction, and veto decomposition.

### Family D — drift plus auxiliary fault

Primary failure-boundary endpoint: cumulative operational squared prediction loss over `401..600`.

Primary paired contrast:

`independent_persistence loss - triad_persistence loss`.

A materially positive contrast indicates a new auxiliary-failure over-veto boundary. This family is not allowed to be omitted or reclassified as irrelevant if it is unfavorable.

Also report adaptation probability by `t=420`, first adaptation delay, adaptation burden, auxiliary mismatch fraction, common-mode-suspect fraction, veto count, and final slope error relative to `1.5+m`.

### Healthy control

Report:

- auxiliary mismatch fraction after `t=401`;
- common-mode-suspect fraction after `t=401`;
- veto count;
- adaptation count;
- operational loss;
- final fitted-slope error.

No superiority claim is attached to the control cell.

## Veto decomposition

For `independent_persistence`, preserve separate per-step indicators and per-seed counts for:

- `veto_primary_bad`;
- `veto_common_mode_suspect`;
- total veto;
- permitted adaptation attempt.

If both veto conditions happen simultaneously, record both diagnostic indicators but increment total veto only once.

## Diagnostic outcomes

Preserve per seed/cell/strategy:

- operational loss over `401..600` and `401..1200`;
- evaluator-only latent-input loss over the same horizons;
- adaptation indicator over `401..420`;
- first adaptation time and delay;
- adaptation counts through `600` and `1200`;
- final slope and absolute slope error relative to the true final physical slope;
- all three rolling triad health statistics;
- `primary_bad`, `reference_1_bad`, `reference_2_bad` fractions/onsets;
- `x_med`;
- `x_a`;
- rolling `G_t`;
- `anchor_mismatch` fraction/onset;
- `triad_consistent` fraction;
- `common_mode_suspect` fraction/onset;
- veto decomposition.

Full time-step traces for audit seeds must include every gate-visible variable required to reproduce decisions from history.

## Inference

Whole seed/stream is the independent unit. Strategies are paired within seed and cell.

Use `10,000`-replicate paired whole-seed bootstrap intervals with deterministic per-cell/per-contrast bootstrap seeds frozen in the evaluation runner before results are inspected.

The main scientific claims are cell-family-specific. No omnibus superiority claim is planned.

For the genuine-drift non-destruction criterion, bootstrap the whole-seed mean of `R` exactly as defined above.

## Prospective interpretation rules

A bounded Experiment 011 success requires all of the following under a **healthy auxiliary source**:

1. common-mode corruption cells: `independent_persistence` materially improves coefficient integrity relative to `triad_persistence` for at least the larger corruption magnitudes, with the paired interval supporting the direction of improvement;
2. genuine physical-drift cells: the preregistered early-loss non-destruction criterion is satisfied;
3. primary-only fault cells: the new strategy does not erase the existing triad protection mechanism;
4. healthy control: the new auxiliary path does not create a large false-veto regime.

The auxiliary-fault family is a prospective failure-boundary test. If it causes over-veto during genuine drift, the correct claim is not general fault tolerance. The bounded claim becomes: an independently generated, trustworthy process-side observable can break the specified three-input common-mode ambiguity, while loss of that auxiliary source creates a new identifiability/trust boundary.

If common-mode corruption remains undetected despite the healthy auxiliary source, Experiment 011 fails its central intervention hypothesis.

If genuine physical drift is materially suppressed even while the auxiliary source is healthy, Experiment 011 fails its responsiveness requirement.

Negative findings must be preserved without post hoc threshold retuning or family removal.

## Required audit checks

Before accepting Experiment 011 evidence independently verify at minimum:

- exact 13-cell × 7-strategy × 200-seed coverage;
- evaluation seeds exactly `11000..11199`;
- audit seeds exactly `11000..11004`;
- auxiliary calibration seeds exactly `600..799` and disjointness from all evaluation seeds;
- unchanged `tau` and exact Experiment 010 `kappa3` reproduction;
- exact `beta=0.8` and healthy auxiliary noise SD `0.08`;
- exact normalized auxiliary noise SD `0.1`;
- exact calibration interval `t=101..300` and 20-step `G_t` statistic;
- exact empirical `0.99` quantile convention for `lambda_anchor`;
- no evaluation leakage into calibration;
- exact latent AR(1) and physical-response equations;
- exact healthy triad sensing equations;
- exact Experiment 010 common-mode reuse of the same `c_t` in all three input channels;
- exact primary-only fault equations;
- exact auxiliary-fault equation and `0.8*m*d_t` scaling;
- learner/refit use of `x_p` only;
- auxiliary `z` used only by the monitor;
- exact triad median definition;
- exact `triad_consistent`, `anchor_mismatch`, and `common_mode_suspect` rules;
- exact veto precedence and streak reset behavior;
- matched random streams across strategies;
- strict test-then-train chronology;
- exact primary/secondary contrasts;
- exact genuine-drift relative excess-loss definition and `<0.10` upper-CI criterion;
- exact deterministic bootstrap seeds and 10,000-replicate whole-seed bootstrap implementation;
- complete seed summaries and required audit traces.

## Claim boundary

Experiment 011 can establish evidence only for the specified univariate AR(1) process, linear OLS learner, persistent Gaussian fault families, three-input sensing architecture, one structurally independent auxiliary observable with fixed `beta=0.8`, frozen noise laws, thresholds, event timing, magnitudes, and seed distributions.

It does not establish robustness to arbitrary auxiliary-model misspecification, simultaneous common-mode corruption of both the input-sensor family and the auxiliary source, multiple independent auxiliary failures, adversarial/Byzantine corruption, bias/stuck/dropout faults, nonlinear or multivariate dynamics, changing auxiliary physics, state-estimation architectures, or real digital twins.

The experiment is specifically a test of whether **cross-structure evidence** can break one previously demonstrated common-mode ambiguity without sacrificing adaptation under the frozen healthy-auxiliary drift family.
