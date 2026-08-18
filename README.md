# Adaptive Model Gating

Evidence-first computational research on when an adaptive model should update in response to changing observations.

## Research question

When transient and persistent disturbances initially produce similar prediction-error evidence, does requiring temporal persistence before model adaptation improve the tradeoff between unnecessary adaptation and delayed response to genuine persistent drift?

## Experiment 001 — current evidence

The first study uses a controlled linear dynamical regression system with known ground truth and compares four strategies:

- **B0 — Frozen:** no post-training adaptation.
- **B1 — Continuous:** refit after every eligible observation.
- **B2 — Threshold gate:** adapt when a calibrated rolling prediction-loss threshold is exceeded.
- **G — Persistence-aware gate:** use the same loss statistic and threshold as B2, but require sustained threshold exceedance before adaptation.

The frozen evaluation used 200 independent simulation seeds per condition. Transient and persistent changes were generated identically for their first 20 post-event observations, so future event duration was not available to the gate during matched onset.

Relative to the simple threshold gate, persistence confirmation reduced the transient-event adaptation rate from **0.395 to 0.285**. The paired difference was **-0.110**, with a 95% whole-seed bootstrap interval of approximately **[-0.155, -0.070]**.

That reduction came with slower response to persistent drift. Mean persistent-condition cumulative squared loss over the frozen `t=401..600` horizon was **62.62** for the threshold gate and **63.92** for the persistence gate. The persistence-minus-threshold difference was **+1.298**, with a 95% paired whole-seed bootstrap interval approximately **[+1.03, +1.59]**.

Continuous adaptation had the lowest persistent-drift loss (**56.68**) but, by construction, adapted throughout every transient stream. The frozen model avoided adaptation but had substantially higher persistent-drift loss (**84.92**).

Experiment 001 therefore shows a **responsiveness-versus-unnecessary-adaptation tradeoff**, not general superiority of persistence gating. Long-horizon false-alarm accumulation also remains important: at least one post-event adaptation occurred in about 78% of stable threshold-gate streams and 58.5% of stable persistence-gate streams.

See `results/experiment_001/evidence_record.md` for provenance, artifact digests, seed-level audit results, and current claim boundaries.

## Experiment 003 — gradual persistent drift

Experiment 003 prospectively extended the same frozen gate settings to 12 gradual persistent-drift cells: `delta_a ∈ {0.25, 0.5, 1.0}` crossed with ramp durations `{20, 50, 100, 200}`, using 200 new seeds per cell and no retuning.

Persistence gating adapted during the ramp less often than the simple threshold gate in **11 of 12 cells** and tied it in the strongest, slowest cell, where both gates adapted during the ramp for every seed. The conservative shift therefore survived gradual drift, but it was not universal.

That conservatism carried a consistent loss cost. Persistence had higher mean cumulative squared prediction loss over `t=401..800` in **all 12 cells**. Every prespecified paired whole-seed bootstrap interval for persistence-minus-threshold loss excluded zero on the positive side. The relative mean-loss penalty ranged from approximately **0.79% to 3.03%** of threshold loss across the frozen cells.

The bounded conclusion is that the earlier **responsiveness-versus-conservatism tradeoff generalizes to the specified gradual persistent drifts** in this controlled linear system. Experiment 003 does not establish general superiority of persistence gating, and the threshold/persistence distinction can disappear at the during-ramp adaptation endpoint under sufficiently strong, slow drift.

See `results/experiment_003/evidence_record.md` for run provenance, artifact digests, cell-level evidence, independent audit checks, and the full claim boundary.

## Evidence policy

This repository is an experimental evidence base, not a manuscript or publication claim. Results, including negative or failed results, are preserved. Evaluation rules are frozen before test results are inspected. Claims remain limited to what committed artifacts support.

## Decision-time boundary

At time `t`, a gate may use only information legitimately available through `t`: current/past inputs, predictions, already-realized outcomes, residual history, prior adaptation decisions, and current model state. Hidden regime labels, true generating parameters, future observations, future loss, event duration, and future adaptation performance are evaluator-only information.

Each observation follows a test-then-train chronology:

`input -> prediction -> outcome reveal -> error -> gate decision -> optional refit -> next step`

## Experimental unit

The independent experimental unit is the independently generated simulation seed/stream. Time steps within a stream are serially dependent and are not treated as independent replicates. Strategy comparisons are paired within the same generated stream.

## Planned research sequence

This repository begins the first of four planned research threads:

1. Adaptation gating under drift/noise
2. Early-warning signals before failure
3. Cause-of-change attribution
4. Simulation-to-decision reliability under model mismatch

Only Thread 1 is studied here. Later threads will not be presented as findings of this repository unless they are prospectively designed and implemented as separate evidence-generating studies.
