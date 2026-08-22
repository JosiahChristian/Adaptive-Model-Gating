# Experiment 038 — Frozen Locally Robust Huber Likelihood

Prospectively frozen before any Experiment-038 outcomes.

The operative scientific contract is GitHub issue #74. Experiment 038 tests whether a proper locally robust Huber residual likelihood can preserve the heavy-tail safety achieved by Experiments 036–037 while recovering the Gaussian coverage lost by globally heavy-tailed likelihoods.

Frozen candidate: six directed Experiment-028 responses; inherited analytic three-block covariance; exact per-block whitening; Huber cutoff c=1.345; normalized product Huber density on six whitened coordinates; equal H_ab/H_ac/H_bc/H_null prior; inherited HalfNormal(BETA_SCALE) amplitude prior; deterministic trapezoid beta grid 0..1.20 step 0.01.

Frozen deployment: wrong-action cost 100, fallback cost 1, threshold 0.99, Experiment-031 causal context vote, Experiment-032 composition, inherited triad primary-fault veto and exact fallback, unchanged diagnostic probe schedule/amplitudes and calibration constants.

Evaluation: Gaussian, Laplace, Student-t3, and contaminated-Gaussian diagnostic noise; gain 0.50/0.425 x noise scale 1.00/1.50; H_ab drift/fault magnitude 0.50; 16 cells; seeds 38000..38999; audit 38000..38004; bootstrap seed 38038.

Comparators: Huber composed, frozen Gaussian Experiment-032, frozen Student-t3 Experiment-036, frozen model-average Experiment-037, triad persistence.

Frozen H1–H10 and interpretation rule are exactly those in issue #74. No tuning from Experiment-038 outcomes is permitted.