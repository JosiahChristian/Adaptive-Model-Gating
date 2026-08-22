# Experiment 042 — Frozen Variance-Preserving Benchmark-Aligned Gaussian Gross-Error Mixture

Prospectively frozen before any Experiment-042 outcomes.

The operative scientific contract is GitHub issue #96. Experiment 042 is a mechanism-identification test of whether the remaining robustness/coverage tradeoff is primarily caused by misspecifying the scale location of sparse gross errors rather than by the decision rule itself. It is not proposed as a universal deployment distribution.

Frozen candidate: six directed Experiment-028 responses in the inherited three analytic 2-D covariance blocks. For each block with marginal covariance Sigma, use the proper mixture 0.95*N_2(0,Sigma/2.2) + 0.05*N_2(0,25*Sigma/2.2), with independent per-block latent marginalization by log-sum-exp. The 0.95/0.05 weights, 25:1 gross/clean variance ratio, and 2.2 covariance normalization are inherited directly from the contaminated-Gaussian family frozen in Experiment 035; the mixture covariance is exactly Sigma. Retain equal H_ab/H_ac/H_bc/H_null priors, inherited HalfNormal(BETA_SCALE) amplitude prior, and deterministic trapezoid beta grid 0..1.20 step 0.01.

Frozen deployment: wrong-action cost 100, fallback cost 1, threshold 0.99, Experiment-031 current-time causal context vote, Experiment-032 composition, inherited triad primary-fault veto and exact fallback, unchanged diagnostic probe schedule/amplitudes and calibration constants.

Evaluation: Gaussian, Laplace, Student-t3, and contaminated-Gaussian diagnostic noise; gain 0.50/0.425 x noise scale 1.00/1.50; H_ab drift/fault magnitude 0.50; 16 cells; seeds 42000..42999; audit 42000..42004; bootstrap seed 42042.

Comparators: Experiment-042 two-Gaussian local mixture, frozen Gaussian Experiment-032, frozen Student-t3 Experiment-036, frozen global model-average Experiment-037, frozen coordinatewise Huber Experiment-038, frozen block-radial Huber Experiment-039, frozen local Gaussian/Student-t3 Experiment-040, frozen local Gaussian/Cauchy Experiment-041, and triad persistence.

Frozen H1-H12 and interpretation rule are exactly those in issue #96. No tuning from Experiment-042 outcomes is permitted.