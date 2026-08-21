# Experiment 036 — Robust tail-aware deployment

Prospectively frozen before any Experiment-036 outcomes. Operative preregistration: GitHub issue #66.

## Question
Can a fixed heavy-tailed directed-covariance likelihood restore the finite-sample deployment safety lost in Experiment 035 without sacrificing Gaussian in-distribution utility?

## Frozen architecture
Experiment-032 operational-context composition, triad primary-fault veto/fallback, probe schedule/amplitudes, wrong/fallback costs 100/1, and action threshold 0.99 remain unchanged. Baselines are the frozen Experiment-028 Gaussian posterior policy and triad persistence.

## Candidate
Use a multivariate Student-t directed-response likelihood with nu=3 and the same Experiment-028 analytic block covariance geometry. Preserve topology directions, equal topology/null priors, inherited positive half-normal amplitude prior/BETA_SCALE, sequential stopping, and 0.99 action threshold. Marginalize the positive amplitude by deterministic preregistered one-dimensional quadrature. No fitted nu, scale inflation, clipping, winsorization, temperature scaling, or threshold adjustment.

## Evaluation
Gaussian ID plus the exact Experiment-035 unit-variance Laplace, Student-t3, and 5% contaminated-Gaussian families. Gain {0.50, 0.425} x noise scale {1.00, 1.50}, magnitude 0.50, H_ab topology: 16 cells. Seeds 36000..36999, 1,000/cell. Audit seeds 36000..36004. Bootstrap seed 36036, 10,000 resamples where reported.

## Frozen criteria
H1 posterior validity. H2 robust-policy wrong-acceptance one-sided 95% Wilson upper <=0.01 in every cell. H3 accepted precision >=0.99 in every cell. H4 robust coverage >=0.90 at gain .50/noise 1.00 and >=0.85 at gain .425/noise 1.00 for every distribution. H5 Gaussian non-regression: coverage deficit vs frozen Gaussian <=0.03 and operational-loss increase <=0.05. H6 on every Experiment-035 cell where Gaussian violates H2/H3, robust policy must reduce wrong acceptance and satisfy H2/H3. H7 robust operational loss <= triad +0.20 every cell. H8 zero causal/inherited-veto violations. H9 exact fallback every abstaining seed. H10 provenance records nu, covariance, amplitude quadrature, seeds, distributions, threshold/costs, context rule, and no-tuning flag.

Experiment 036 supports robust distributional deployment only if H1-H10 all pass. Failures are preserved; no outcome-driven retuning.