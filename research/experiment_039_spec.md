# Experiment 039 — Frozen Block-Radial 95% Gaussian-Core Huber Likelihood

Prospectively frozen before any Experiment-039 outcomes.

The operative scientific contract is GitHub issue #77. Experiment 039 tests whether robustness localized at the inherited two-dimensional covariance-block level can preserve central Gaussian evidence while downweighting unusually large block residuals.

Frozen candidate: six directed Experiment-028 responses arranged as three inherited analytic 2-D covariance blocks; exact per-block whitening; radial Mahalanobis norm r=sqrt(z1^2+z2^2); block-radial Huber loss rho_c(r)=0.5*r^2 for r<=c and c*r-0.5*c^2 otherwise; c=sqrt(chi2_{2,0.95})=sqrt(-2 ln 0.05) approximately 2.44774683068; proper normalized isotropic 2-D radial Huber density per block; product across three blocks with covariance Jacobian; equal H_ab/H_ac/H_bc/H_null prior; inherited HalfNormal(BETA_SCALE) amplitude prior; deterministic trapezoid beta grid 0..1.20 step 0.01.

Frozen deployment: wrong-action cost 100, fallback cost 1, threshold 0.99, Experiment-031 causal context vote, Experiment-032 composition, inherited triad primary-fault veto and exact fallback, unchanged diagnostic probe schedule/amplitudes and calibration constants.

Evaluation: Gaussian, Laplace, Student-t3, and contaminated-Gaussian diagnostic noise; gain 0.50/0.425 x noise scale 1.00/1.50; H_ab drift/fault magnitude 0.50; 16 cells; seeds 39000..39999; audit 39000..39004; bootstrap seed 39039.

Comparators: block-radial Huber composed, frozen Gaussian Experiment-032, frozen Student-t3 Experiment-036, frozen model-average Experiment-037, frozen coordinatewise Huber Experiment-038, triad persistence.

Frozen H1-H11 and interpretation rule are exactly those in issue #77. No tuning from Experiment-039 outcomes is permitted.
