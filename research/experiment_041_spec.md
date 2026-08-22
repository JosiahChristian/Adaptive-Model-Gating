# Experiment 041 — Frozen Local Gaussian/Cauchy Gross-Error Mixture

Prospectively frozen before any Experiment-041 outcomes.

The operative scientific contract is GitHub issue #90. Experiment 041 tests whether the successful local probabilistic architecture from Experiment 040 can preserve near-Gaussian evidence while a substantially heavier-tailed gross-error component absorbs sparse extreme diagnostic blocks strongly enough to restore the finite-sample safety boundary.

Frozen candidate: six directed Experiment-028 responses arranged as three inherited analytic 2-D covariance blocks; per block p(r)=0.95*N_2(r;0,Sigma)+0.05*t_{nu=1,2}(r;0,Sigma), where the Student-t df=1 component is the proper normalized 2-D multivariate Cauchy with density [2*pi*|Sigma|^(1/2)]^-1*(1+r' Sigma^-1 r)^(-3/2). The latent component is marginalized independently within each block. Equal H_ab/H_ac/H_bc/H_null prior; inherited HalfNormal(BETA_SCALE) amplitude prior; deterministic trapezoid beta grid 0..1.20 step 0.01.

Frozen deployment: wrong-action cost 100, fallback cost 1, threshold 0.99, Experiment-031 current-time causal context vote, Experiment-032 composition, inherited triad primary-fault veto and exact fallback, unchanged diagnostic probe schedule/amplitudes and calibration constants.

Evaluation: Gaussian, Laplace, Student-t3, and contaminated-Gaussian diagnostic noise; gain 0.50/0.425 x noise scale 1.00/1.50; H_ab drift/fault magnitude 0.50; 16 cells; seeds 41000..41999; audit 41000..41004; bootstrap seed 41041; 10,000 paired resamples where reported.

Comparators: local Gaussian/Cauchy composed, frozen Gaussian Experiment-032, frozen Student-t3 Experiment-036, frozen global model-average Experiment-037, frozen coordinatewise Huber Experiment-038, frozen block-radial Huber Experiment-039, frozen local Gaussian/Student-t3 Experiment-040, triad persistence.

Frozen H1-H11 and interpretation rule are exactly those in issue #90. No tuning from Experiment-041 outcomes is permitted.