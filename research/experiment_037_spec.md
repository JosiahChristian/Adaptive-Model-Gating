# Experiment 037 — Frozen Likelihood-Family Model Averaging

Status: prospectively frozen before any Experiment-037 outcomes. Operative contract: issue #69.

Experiment 037 tests equal-prior Bayesian model averaging over the frozen Gaussian and Student-t(df=3) directed-covariance likelihood families. Model priors are 0.5/0.5; topology priors are 0.25 each for H_ab/H_ac/H_bc/H_null. Both families use the inherited six directed responses, covariance geometry, HalfNormal(BETA_SCALE) positive-amplitude prior, and deterministic beta grid 0..1.20 step 0.01. Proper normalized likelihoods are used before marginalizing amplitude and then likelihood family.

The deployment architecture is unchanged: wrong-action cost 100, fallback cost 1, threshold 0.99, Experiment-031 causal context vote, Experiment-032 composition, inherited triad veto/fallback, and frozen probe schedule/calibration constants.

Evaluation: 16 cells = Gaussian, Laplace, Student-t3, contaminated Gaussian x gain {0.50,0.425} x noise scale {1.00,1.50}; 1,000 fresh seeds 37000..37999 per cell. Comparators are the model-averaged composed policy, frozen Gaussian composed policy, frozen Student-t3 composed policy, and triad persistence.

Success criteria H1-H10 are exactly those preregistered in issue #69. No model-weight fitting, threshold tuning, likelihood selection rule, or outcome-driven modification is permitted.