# Experiment 003 — Gradual Drift

**Status:** prospective specification; committed before Experiment 003 evaluation.

## Motivation

Experiments 001–002 used abrupt parameter changes. Experiment 003 tests whether the observed responsiveness–conservatism tradeoff survives when persistent change develops gradually.

## Scientific question

Under gradual persistent parameter drift, does the persistence-aware gate retain its conservative adaptation behavior without incurring a disproportionate prediction-loss penalty relative to the simple threshold gate?

## Shared system

Retain the Experiment 001 simulator, prediction model, adaptation operator, decision-time contract, rolling MSE statistic, frozen threshold `tau`, rolling window 20, refit window 100, and persistence count 3. No gate parameter is retuned for gradual drift.

Evaluation seeds are `3000..3199`, disjoint from prior calibration/evaluation seeds.

## Gradual persistent drift

Event onset remains `t=401`. For a target change magnitude `delta_a`, the true slope changes linearly from 1.5 to `1.5 + delta_a` over a frozen ramp duration `r`, then remains at the target value.

Evaluate:

- `delta_a ∈ {0.25, 0.5, 1.0}`
- `r ∈ {20, 50, 100, 200}` observations

This yields 12 gradual-persistent cells.

The slope at ramp step `j=1..r` is:

`a_t = 1.5 + delta_a * (j / r)`

and remains `1.5 + delta_a` after the ramp completes.

## Baselines

Evaluate the same four strategies:

- frozen
- continuous
- threshold
- persistence

All strategies share the same stochastic realization within each seed/cell.

## Primary outcome

For each gradual-persistent cell, report cumulative squared prediction loss over `t=401..800`. The longer frozen horizon is used because ramps up to 200 observations require enough post-ramp time to measure response consequences.

The primary paired contrast is:

`persistence loss - threshold loss`

with 95% paired whole-seed bootstrap confidence intervals.

## Secondary outcomes

Per seed/cell preserve:

- whether each strategy adapts during the ramp;
- first post-event adaptation time;
- adaptation delay from event onset;
- total adaptations through `t=800` and `t=1200`;
- cumulative squared prediction loss;
- model parameter estimates.

Full time-step traces are preserved for audit seeds `3000..3004`; complete per-seed summaries are preserved for all cells and seeds.

## Interpretation

Experiment 003 does not define success as persistence gating winning every cell.

Evidence that the earlier tradeoff generalizes would consist of systematic differences between persistence and threshold gating that remain interpretable as conservatism versus responsiveness across ramp speeds and magnitudes.

If persistence gating is uniformly worse, or if the threshold/persistence distinction largely disappears under gradual drift, that constrains the phenomenon to abrupt-change settings.

If neither gate responds meaningfully to slow/small drift, that is an informative detectability boundary rather than grounds for retuning after evaluation.

## Claim boundary

This experiment can only inform gradual persistent drift in the specified controlled linear system. It does not establish performance under nonlinear dynamics, sensor faults, adversarial manipulation, real digital twins, or arbitrary concept drift.
