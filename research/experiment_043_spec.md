# Experiment 043 — Frozen Two-Stage Replicated Gaussian Posterior Acceptance

Prospectively frozen before any Experiment-043 outcomes.

The operative scientific contract is GitHub issue #102. Experiment 043 tests whether the unresolved finite-sample tail-risk boundary is primarily caused by acting on a single transient extreme posterior during sequential diagnostic probing.

Frozen candidate: exact Experiment-028/032 Gaussian directed-covariance posterior; six directed responses; inherited analytic three-block covariance; equal H_ab/H_ac/H_bc/H_null prior; inherited positive-amplitude marginalization; unchanged posterior threshold 0.99. Acceptance requires the same non-null topology candidate to have posterior >=0.99 on two consecutive diagnostic stages. First possible action is stage 2. A different candidate or a sub-threshold stage resets confirmation. No confirmation by stage 5 means exact inherited triad fallback.

Frozen deployment: wrong-action cost 100, fallback cost 1, Experiment-031 current-time causal context vote, Experiment-032 composition, inherited triad primary-fault veto and exact fallback, unchanged diagnostic probes and calibration constants.

Evaluation: Gaussian, Laplace, Student-t3, and contaminated-Gaussian diagnostic noise; gain 0.50/0.425 x noise scale 1.00/1.50; H_ab drift/fault magnitude 0.50; 16 cells; seeds 43000..43999; audit 43000..43004; bootstrap seed 43043.

Comparators: replicated Gaussian, frozen single-crossing Gaussian Experiment-032, frozen Student-t3 Experiment-036, frozen model-average Experiment-037, frozen block-radial Huber Experiment-039, frozen local Gaussian/Student-t3 Experiment-040, frozen local Gaussian/Cauchy Experiment-041, frozen benchmark-aligned Gaussian gross-error Experiment-042, and triad persistence.

Frozen H1-H12 and interpretation rule are exactly those in issue #102. No tuning of threshold, confirmation count, stage schedule, reset rule, likelihood, or other deployment parameters from Experiment-043 outcomes is permitted.