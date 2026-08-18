# Experiment 001 — Persistence-Aware Adaptation Gating

**Status:** prospective specification; no evaluation results inspected at time of commitment.

## Scientific question

When transient and persistent changes initially provide the same generating evidence, does persistence confirmation alter the tradeoff between unnecessary adaptation to temporary change and delayed response to persistent change relative to frozen, continuous, and simple-threshold baselines?

## Simulator

For each independently generated stream:

`x_t = 0.8 x_(t-1) + eta_t`

`y_t = a_t x_t + epsilon_t`

with:

- `eta_t ~ Normal(0, 0.5^2)`
- `epsilon_t ~ Normal(0, 0.5^2)`
- baseline `a_t = 1.5`

Each run contains 1,200 time steps.

## Timeline

- `t = 1..300`: initial model-fitting history
- `t = 301..400`: clean pre-event evaluation/baseline
- event begins at `t = 401`
- primary persistent-loss horizon: `t = 401..600`
- remainder through `t = 1200` is retained for secondary trajectory/recovery evidence

The initial predictive model is ordinary least squares with intercept, fitted on observations `101..300`.

## Evaluation conditions

### Stable

`a_t = 1.5` throughout.

### Transient parameter change

At `t = 401`, `a_t` changes from `1.5` to `2.0`. The changed parameter remains active for exactly 20 observations (`t = 401..420`) and returns to `1.5` at `t = 421`.

### Persistent parameter change

At `t = 401`, `a_t` changes from `1.5` to `2.0` and remains `2.0` thereafter.

### Matched-onset property

Transient and persistent conditions use the same generating parameter during the first 20 post-event observations. The gate is never given the condition label or future event duration. Thus event duration cannot legitimately distinguish the two conditions during their matched onset.

## Adaptation operator

Whenever a strategy adapts, it refits the same ordinary least-squares model with intercept on the most recent 100 eligible observations available at that decision time.

The adaptation operator is held constant across adaptive strategies so the experiment focuses on the timing/gating decision.

## Strategies

### B0 — Frozen

No post-initial-fit model updates.

### B1 — Continuous

After each realized outcome becomes available, refit using the trailing 100 eligible observations for use at the next prediction step.

### B2 — Threshold gate

Compute a rolling mean squared prediction error over the most recent 20 realized prediction errors. Adapt when this statistic exceeds the frozen calibrated threshold `tau`.

### G — Persistence-aware gate

Use the same rolling statistic and the same `tau` as B2. Adapt only after the threshold-exceedance condition is satisfied on three consecutive eligible evaluations.

After an adaptation, the consecutive-exceedance counter resets to zero.

## Calibration

Calibration seeds: `0..199`.

Evaluation seeds: `1000..1199`.

There is no seed overlap.

The threshold `tau` is the empirical 99th percentile of eligible 20-observation rolling MSE values obtained from stable calibration streams under the frozen initial model. The threshold is fixed before evaluation streams are analyzed.

No parameter is retuned in response to evaluation results.

## Decision-time chronology

At every time step:

1. observe `x_t`;
2. predict `y_hat_t` using the current model;
3. reveal `y_t`;
4. record prediction error;
5. update the permitted rolling gate statistic;
6. choose adapt or retain;
7. if adaptation is triggered, refit using only data available through `t`;
8. proceed to `t+1`.

The evaluator may know condition labels, true `a_t`, and the true event onset. Gates may not.

## Experimental unit and dependence

The independent experimental unit is one independently generated seed/stream. Time points within a stream are serially dependent and are not independent replicates.

All four strategies are evaluated on the same stochastic realization within a seed. Strategy comparisons are therefore paired by seed.

## Primary outcomes

Two primary dimensions are reported separately rather than combined using post-hoc utility weights.

### Persistent post-event cumulative squared prediction loss

For each evaluation seed in the persistent condition:

`L_persistent = sum_{t=401}^{600} (y_t - y_hat_t)^2`

### Transient adaptation indicator

For each evaluation seed in the transient condition:

`F_transient = 1` if the strategy triggers at least one gated/refit adaptation during `t = 401..420`; otherwise `0`.

For B1, continuous updating during the transient interval is recorded as adaptation by construction. B0 has no adaptations by construction.

## Secondary outcomes

Preserve per seed:

- stable-condition adaptation occurrence and count;
- transient-condition adaptation occurrence and count;
- persistent-condition adaptation occurrence and count;
- first adaptation time;
- persistent adaptation delay from `t=401`;
- cumulative squared error trajectories;
- post-event recovery trajectory;
- model parameter trajectories (`a_hat`, intercept);
- all predictions, outcomes, errors, gate statistics, and adaptation decisions needed to audit chronology.

## Statistical reporting

Report strategy-level point estimates and paired strategy differences at the seed level.

Uncertainty for paired comparisons is estimated by resampling whole evaluation seeds with replacement and recomputing the paired statistic. Report 95% paired seed-bootstrap confidence intervals. Individual time points are never resampled or treated as independent observations for inferential uncertainty.

The initial evaluation uses 200 evaluation seeds per condition. Evaluation size is fixed prospectively rather than extended until a desired result appears.

## Interpretation rules

The persistence-aware strategy is not declared generally superior merely because it wins one endpoint.

Interpretation must consider both primary dimensions. In particular:

- lower transient adaptation with severe persistent-loss inflation is a responsiveness cost, not an unqualified success;
- lower persistent loss accompanied by indiscriminate transient adaptation does not establish useful gating;
- if B2 performs similarly to G, persistence confirmation has not demonstrated meaningful added value in this experiment;
- if continuous adaptation dominates the tested tradeoff, the proposed gating advantage is not supported in this system;
- if frozen performance is comparable under persistent drift, the manipulation is not sufficiently consequential to support a gating conclusion.

No universal numerical superiority threshold is introduced after evaluation results are observed. Effect estimates and uncertainty are reported transparently.

## Claim boundary

Experiment 001 can, at most, support a statement about the tested controlled linear system, specified event structure, adaptation operator, and frozen gates.

It cannot establish optimal adaptation gating, general digital-twin superiority, adversarial robustness, general concept-drift detection performance, or generalization across model classes and environments.

## Planned follow-on studies

Only if scientifically informative after Experiment 001:

1. change-magnitude × transient-duration response surface;
2. gradual drift;
3. recurrent regimes;
4. sensor corruption/fault;
5. only later, explicitly adversarial perturbations.

These are not part of Experiment 001 and cannot be used to retroactively tune its specification.
