# Experiment 024 — Uncertainty-Aware Edge-Margin Qualification

Status: **FROZEN BEFORE ANY EXPERIMENT-024 OUTCOMES**

## Motivation
Experiment 022 exposed a localized safety failure under 1.50x observation noise. Experiment 023 showed that the pre-intervention diagnostic-noise estimator tracks the imposed scale accurately and that global threshold multiplication can restore safety at gain=0.50/noise=1.50, but only by reducing coverage to 0.725. Global multiplication is therefore too blunt: it suppresses absolute signal rather than directly testing whether the leading reciprocal provenance edge is distinguishable from its competitors.

## Frozen mechanism
Experiment 024 preserves the Experiment-021 qualification-aware targeting architecture, intervention amplitudes, block schedule, target ordering, raw structural evidence floors, operational gate, and triad fallback. It introduces only an uncertainty-aware confidence test for a candidate provenance edge.

For every decision point that produces reciprocal-edge scores `Q_ab`, `Q_ac`, `Q_bc`:

1. The candidate edge is the unique largest `Q` score. Ties abstain/continue under the inherited stopping logic.
2. The candidate must still clear the inherited raw structural floor (`mu`) for the corresponding round/path. No raw evidence floor is lowered.
3. Let `Q_(1)` be the candidate score and `Q_(2)` the second-largest reciprocal-edge score. Define the edge margin `M = Q_(1) - Q_(2)`.
4. Estimate diagnostic standard deviation using only pre-intervention probe observations `probe_obs_a/b/c` at t=181..200 after channel-centering, exactly as in Experiment 023. Denote this `sigma_hat`.
5. Use the conservative analytic cumulative-score standard error `se_C = sigma_hat * sqrt(0.3325)`. The constant is frozen from the five-sample target-block mean plus shared twenty-sample baseline contribution under the inherited four-round weighted cumulative statistic; it is not fitted to any Experiment-022/023 outcome.
6. Use `se_margin = sqrt(2) * se_C` as a conservative standard error for the difference between the top two reciprocal-edge scores.
7. Confidence qualification requires `M / max(se_margin, 1e-12) >= Z_MARGIN`, where `Z_MARGIN = 2.128045234184984` (one-sided Gaussian 98.333...% quantile, corresponding to Bonferroni allocation of a 5% family-wise ambiguity budget across three candidate-edge comparisons).
8. For targeted round-5 qualification, the same standardized margin rule is applied to the updated candidate score versus the two competing inherited round-4 scores. For the two-block early round-4 path, the selected candidate must clear its inherited early raw floor and the same standardized margin test against the two round-3 competitor scores.

The inherited absolute high-confidence `nu` threshold is replaced only for the new Experiment-024 strategy by the standardized margin criterion above. `mu` floors remain unchanged. No other policy element changes.

## Comparators
- Experiment-024 uncertainty-aware margin strategy (primary)
- Experiment-023 global variance-scaled strategy
- Experiment-021 qualification-aware strategy
- Experiment-020 early-targeted strategy
- triad_persistence

## Fresh evaluation
Use seeds 24000..24199, disjoint from all earlier evaluation and calibration seeds. No recalibration.

Evaluate 46 frozen cells:
- gain 0.50 with noise scales 1.00, 1.25, 1.50, 1.75, 2.00, all three magnitudes;
- gain 0.425 with noise scales 1.00, 1.50, 2.00, all three magnitudes;
- gain 0.35 with noise scales 1.00, 1.50, 2.00, all three magnitudes;
- healthy control;
- drift, common_mode, primary_fault, and coherent-all-auxiliary negative control at magnitudes 0.25, 0.50, 1.00.

## Preregistered criteria
H1 Restored safety: zero wrong provenance acceptance across all 46 cells.

H2 High-noise precision: for every noise>=1.50 cell with at least 20 accepted seeds, accepted-partition precision >=0.99.

H3 Recovery of useful high-noise coverage: at gain=0.50, noise=1.50, coverage >=0.85 at every magnitude.

H4 Improvement over Experiment 023 at the original boundary: at gain=0.50, noise=1.50, Experiment-024 coverage exceeds Experiment-023 coverage by >=0.08 absolute at every magnitude while wrong acceptance remains zero.

H5 Nominal non-regression: at gain=0.50, noise=1.00, coverage is no more than 0.03 below Experiment 021, precision >=0.99, and mean probe energy is no more than 0.05 above Experiment 021.

H6 Moderate-gain preservation: at gain 0.425 and 0.35 with noise=1.00, coverage is no more than 0.03 below Experiment 021 and wrong acceptance is zero.

H7 Low-information conservatism: at gain=0.35 with noise>=1.50, adaptation rate does not exceed triad_persistence by more than 0.02.

H8 Fallback integrity: every abstaining Experiment-024 seed reproduces triad_persistence adaptation signature and operational loss exactly.

## Negative-control boundary
Coherent all-auxiliary corruption remains outside the identification claim. Non-recovery is not a failure unless the strategy makes a wrong positive provenance acceptance.

## Decision rule
If H1 fails, uncertainty-aware margin qualification is not sufficient for the lane's safety claim. If H1 passes but H3/H4 fail, the result establishes that ambiguity-aware confidence is safe but still too conservative; no post-hoc change to `Z_MARGIN` is permitted. Any alternative confidence construction must be a separately frozen experiment.
