# Adaptive Model Gating

Evidence-first computational research on when an adaptive model should update in response to changing observations.

## Research question

When transient and persistent disturbances initially produce similar prediction-error evidence, does requiring temporal persistence before model adaptation improve the tradeoff between unnecessary adaptation and delayed response to genuine persistent drift?

## Current scope

The first study uses a controlled linear dynamical regression system with known ground truth. It compares four strategies under stable, transient-change, and persistent-change conditions:

- **B0 — Frozen:** no post-training adaptation.
- **B1 — Continuous:** refit after every eligible observation.
- **B2 — Threshold gate:** adapt when a calibrated rolling prediction-loss threshold is exceeded.
- **G — Persistence-aware gate:** use the same loss statistic and threshold as B2, but require sustained threshold exceedance before adaptation.

The purpose of the initial experiment is to isolate the adaptation decision. All adaptive strategies therefore use the same model-refitting operator.

## Evidence policy

This repository is an experimental evidence base, not a manuscript or publication claim. Results, including negative or failed results, will be preserved. Evaluation rules are frozen before test results are inspected. Claims will remain limited to what the committed artifacts support.

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
