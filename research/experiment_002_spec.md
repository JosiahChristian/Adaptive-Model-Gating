# Experiment 002 — Change-Magnitude × Transient-Duration Response Surface

**Status:** prospective specification committed after Experiment 001 and before Experiment 002 evaluation.

## Motivation from Experiment 001

Experiment 001 showed a two-sided tradeoff in the tested setting: relative to the simple threshold gate, the persistence-aware gate adapted less often during the 20-step transient event but accumulated more loss after persistent drift. Experiment 002 does not retune Experiment 001. It asks whether that tradeoff is robust or highly dependent on event magnitude and transient duration.

## Scientific question

How do change magnitude and transient duration alter the responsiveness-versus-unnecessary-adaptation tradeoff between a simple rolling-error threshold gate and the same gate with persistence confirmation?

## Fixed simulator and model

Retain the Experiment 001 simulator, prediction model, chronology, refit operator, rolling statistic, and calibration procedure unless explicitly changed below:

`x_t = 0.8 x_(t-1) + eta_t`

`y_t = a_t x_t + epsilon_t`

with `eta_t ~ Normal(0, 0.5^2)`, `epsilon_t ~ Normal(0, 0.5^2)`, and baseline `a=1.5`.

Each run contains 1,200 time steps. The initial OLS model is fitted on `t=101..300`; clean pre-event evaluation is `t=301..400`; the event begins at `t=401`. Refit uses the most recent 100 eligible observations. Rolling MSE uses the most recent 20 realized prediction errors.

The threshold `tau` is calibrated exactly as in Experiment 001: the empirical 99th percentile of eligible stable-stream rolling MSE values from calibration seeds `0..199` under the frozen initial model. Persistence requires three consecutive threshold exceedances and resets after adaptation.

## Strategies

All four Experiment 001 strategies are retained for context:

- B0 Frozen
- B1 Continuous
- B2 Threshold
- G Persistence-aware

The primary scientific comparison remains `G` versus `B2`.

## Factor grid

### Parameter-change magnitude

The event changes the slope from `1.5` to:

- `1.60` (`delta_a = 0.10`)
- `1.75` (`delta_a = 0.25`)
- `2.00` (`delta_a = 0.50`)
- `2.50` (`delta_a = 1.00`)

### Transient duration

For transient conditions, the changed slope remains active for exactly:

- 5 observations
- 20 observations
- 50 observations

and then returns to `1.5`.

This produces 12 transient cells.

### Persistent conditions

For each of the four change magnitudes, the changed slope begins at `t=401` and remains active through the rest of the stream. This produces four persistent cells.

### Stable reference

A stable condition with no parameter change is retained as a common false-alarm reference.

## Matched-onset requirement

For a given seed and change magnitude, transient and persistent streams must be numerically identical through the full duration of the corresponding transient event. The gate never receives event duration or condition labels.

## Seeds

Calibration remains `0..199` and is not changed based on Experiment 001 outcomes.

Experiment 002 evaluation seeds are `2000..2199`, giving 200 independently generated streams per grid cell and no overlap with Experiment 001 evaluation seeds.

The same seed is reused across strategies and factor cells to support paired comparisons. Consequently, factor-cell estimates are correlated; cells are not treated as independent experiments.

## Primary evidence representation

Experiment 002 is a response-surface/robustness study. Every prespecified factor cell is reported. No subset of favorable magnitudes or durations may be selected as the headline result.

Two dimensions remain separate rather than being combined with an arbitrary post-hoc utility weight:

### Transient adaptation surface

For each of the 12 transient cells, report the probability that each strategy triggers at least one adaptation during the true transient interval.

For each seed, also compute the unweighted mean of the 12 cell indicators for `G` and `B2`. The paired `G-B2` difference in this seed-level mean is the overall transient-adaptation summary.

### Persistent-loss surface

For each of the four persistent magnitudes, report cumulative squared prediction loss over `t=401..600` for all strategies and paired `G-B2` loss differences.

Because raw loss naturally scales with change magnitude, no post-hoc weighted average of the four raw loss cells is used as a global superiority score. Cell-specific differences and their pattern across magnitude are primary evidence.

## Stable false-alarm evidence

Experiment 001 exposed substantial long-horizon false-alarm accumulation. Experiment 002 therefore explicitly reports, in stable streams:

- probability of at least one adaptation during `t=401..600`;
- probability of at least one adaptation during `t=401..1200`;
- number of adaptations over both horizons.

This evidence is reported for B2 and G and is not omitted if unfavorable.

## Secondary outcomes

Per cell and strategy, preserve:

- first post-event adaptation time;
- adaptation delay for persistent conditions;
- adaptation count;
- cumulative squared-loss trajectory;
- model slope/intercept trajectories;
- prediction/error/rolling-statistic chronology needed for audit.

## Statistical unit and uncertainty

The experimental unit is the independently generated seed/stream.

For each paired strategy contrast, resample whole seeds with replacement and recompute the statistic. Report 95% paired seed-bootstrap intervals using 10,000 resamples. Time steps and factor cells are never treated as independent replicates.

For the overall 12-cell transient summary, resample seeds and retain all 12 cells for each selected seed so cross-cell dependence is preserved.

## Interpretation rules

Experiment 002 is intended to identify where the Experiment 001 tradeoff persists, reverses, disappears, or becomes trivial.

The following are scientifically meaningful outcomes:

- persistence confirmation reduces transient adaptation broadly but consistently increases persistent loss;
- benefit appears only for longer transients or larger changes;
- benefit disappears for short events because neither gate reacts;
- both gates become effectively equivalent for large, obvious changes;
- long-horizon stable false alarms remain high, showing the threshold design itself needs improvement;
- B2 and G are nearly indistinguishable across the grid, weakening the case that the persistence mechanism adds useful structure.

No result is converted into a general digital-twin or concept-drift claim.

## Claim boundary

Experiment 002 can establish only how the specified four adaptation strategies behave across the prespecified magnitude-duration grid in this controlled linear system.

It cannot establish optimal gating, broad concept-drift superiority, adversarial robustness, causal attribution of change, or transfer to nonlinear/real systems.

## Next planned study if warranted

The next prospectively distinct study is gradual drift. It must be separately specified before evaluation and may not be used to retune or reinterpret Experiment 002 after observing its results.
