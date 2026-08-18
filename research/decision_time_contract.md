# Decision-Time Information Contract

This contract applies to Experiment 001 and is intended to prevent retrospective information from entering an online adaptation decision.

## Gate-permitted information at time t

A strategy may use:

- inputs observed through `t`;
- predictions generated through `t`;
- outcomes that have actually been revealed through `t`;
- residuals/errors whose corresponding outcomes have been revealed;
- rolling statistics computed exclusively from those realized errors;
- current model parameters;
- previous adaptation decisions;
- time/index information available to the running algorithm.

## Evaluator-only information

A strategy may not use:

- stable/transient/persistent condition label;
- true generating parameter `a_t`;
- true event annotation or future event duration;
- future inputs or outcomes;
- future prediction errors;
- future model performance;
- whether a currently observed change will later revert;
- statistics computed from the completed trajectory unless used only after the run for evaluation.

## Required chronology

Prediction must precede outcome reveal. Scoring must precede any model update using that outcome. Any refit performed after observing `y_t` affects predictions beginning at `t+1`, never the already-scored prediction at `t`.

## Audit requirement

Generated evidence should preserve enough per-time-step information to reconstruct:

`seed, condition, t, x_t, y_t, y_hat_t, error, rolling statistic, threshold state, adaptation decision, model parameters before/after decision`.

A future analysis that violates this contract is a separate analysis and must not be presented as the prospectively specified Experiment 001 result.
