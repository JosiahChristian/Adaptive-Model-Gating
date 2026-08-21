# Experiment 035 — Frozen Non-Gaussian Diagnostic-Noise Transfer

## Status
Prospectively frozen before any Experiment-035 outcome generation. Scientific contract mirrors issue #61.

## Question
Does the frozen Experiment-028 Gaussian directed-covariance posterior remain calibrated, and does the frozen Experiment-032 two-state deployment architecture remain safe/useful, when diagnostic probe noise is non-Gaussian but variance-matched?

## Frozen model/controller
No scientific parameter or rule may change. Preserve Experiment-028 posterior, Experiment-029 wrong-action cost 100 / fallback cost 1 / acceptance threshold 0.99, symmetric rounds 1..5, Experiment-031 causal context vote, Experiment-032 composition, inherited triad primary-fault veto, exact triad fallback, and all calibration constants. No likelihood refit, robustification, temperature scaling, clipping, threshold change, smoothing, or outcome-dependent selection.

## Noise families
Replace only diagnostic probe noise while preserving the exact probe signal geometry and physical/auxiliary stream.
- `laplace`: zero-mean Laplace with unit variance.
- `student_t3`: Student-t with 3 degrees of freedom, normalized by `sqrt(3)` to unit variance.
- `contaminated_gaussian`: 95% `N(0,1)` and 5% `N(0,25)`, divided by `sqrt(2.2)` so marginal variance is one.

For each family evaluate gain `{0.50,0.425}` × diagnostic-noise scale `{1.00,1.50}`, drift/fault magnitude `0.50`, historical true topology `H_ab`. Total 12 cells.

## Seeds
Evaluation seeds `35000..35999` (1,000 fresh seeds/cell). Audit seeds `35000..35004`. Bootstrap seed `35035`; 10,000 paired resamples where reported.

## Probability evaluation
On each identical non-Gaussian stream evaluate the unchanged Experiment-028 posterior after stages 1..5. Explicit truth is `H_ab`. Report multiclass Brier score, `-log P(H_ab)`, top-class accuracy, fixed-bin ECE of top probability vs correctness, entropy, and stagewise values.

## Deployment evaluation
Compare unchanged Experiment-032 composition, Experiment-029 posterior-risk gate, and `triad_persistence` on the identical stream. Report coverage, accepted precision, wrong acceptance, one-sided 95% Wilson upper bound, stop round/energy, operational loss `401..600`, final slope error, causal/inherited-veto violations, and exact fallback mismatches.

## Frozen criteria
- H1 probability validity at every stage.
- H2 deployment topology safety: every cell composed one-sided 95% Wilson upper bound on wrong acceptance `<=0.01`.
- H3 accepted precision `>=0.99` in every cell.
- H4 final-stage calibration: in every scale-1.00 cell Brier `<=0.12` and ECE `<=0.05`; scale-1.50 cells are calibration-characterization only.
- H5 moderate utility: for every family, gain 0.50/scale 1.00 coverage `>=0.90`; gain 0.425/scale 1.00 coverage `>=0.85`.
- H6 scale-1.50 coverage is characterization only; abstention is a valid safety response.
- H7 operational non-regression: composed mean operational loss may not exceed Experiment 029 by more than `0.05` in any cell.
- H8 zero direct causal violations and zero adaptations while inherited primary-fault veto is active.
- H9 exact fallback on every topology-abstaining seed.
- H10 frozen provenance: report records unchanged Gaussian likelihood, distribution definitions/variance normalization, seed range, 0.99/100:1 decision rule, context formula, no-recalibration flag, and code commit.

## Interpretation
Distributional likelihood transfer is supported only if H1-H10 all pass. If probability calibration fails while deployment safety passes, preserve that distinction: safe abstention does not imply calibrated probabilities. Do not repair or retune from Experiment-035 outcomes.
