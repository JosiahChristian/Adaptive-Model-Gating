# Experiment 022 — Stress Realization Contract

Status: **FROZEN BEFORE ANY EXPERIMENT-022 OUTCOMES**

This file operationalizes the already-frozen Experiment-022 specification at commit `68c54649abf806bd8e776dedb60df8fe29a2e896`. It changes only the evaluation distribution and reporting harness. The Experiment-021 policy, all inherited thresholds, selectors, amplitudes, stop rules, fallbacks, and calibrations remain unchanged.

## Evaluation seeds and strategies

Use seeds `22000..22199` inclusive, 200 seeds per cell. Evaluate exactly four strategies in every cell:

1. `qualification_aware_early_targeted_replicated_selective_cumulative_provenance_quorum`;
2. `early_targeted_replicated_selective_cumulative_provenance_quorum`;
3. `targeted_replicated_selective_cumulative_provenance_quorum`;
4. `triad_persistence`.

All four strategies must receive the same preconstructed stressed stream for a given seed/cell. No comparator may silently regenerate an in-distribution stream.

## Cell matrix

### A. Inherited controls — 28 cells

Reuse the exact 28 Experiment-021 cells: healthy 0.00 plus magnitudes 0.25, 0.50, and 1.00 for `drift`, `common_mode`, `primary_fault`, `drift_ab_fault`, `drift_ab_gain050`, `drift_ab_gain0375`, `drift_ab_gain025`, `drift_ab_gain0125`, and `drift_all_aux_fault`.

### B. Probe-gain interpolation/extrapolation — 18 cells

For the inherited `drift_ab_fault` physical structure, use gains `0.45`, `0.425`, `0.35`, `0.30`, `0.20`, and `0.10`, each at magnitudes 0.25, 0.50, and 1.00.

### C. Observation-noise scale — 9 cells

At inherited `drift_ab_fault` structure with probe gain `0.50`, use observation-noise multipliers `0.75`, `1.25`, and `1.50`, each at magnitudes 0.25, 0.50, and 1.00.

The multiplier is applied prospectively to all modeled observation-noise components while preserving latent physical trajectories and corruption signals: reference-channel noise, anchor-channel noise, and diagnostic probe noise. The underlying unit-noise draws remain identical for paired strategy comparison.

### D. Nuisance timing offset — 9 cells

At inherited `drift_ab_fault` structure with probe gain `0.50`, keep physical drift onset at the inherited event time and shift only the coherent A/B auxiliary-corruption onset by `-20`, `+20`, or `+50` samples. Evaluate magnitudes 0.25, 0.50, and 1.00.

### E. Asymmetric auxiliary corruption — 9 cells

At inherited `drift_ab_fault` structure with probe gain `0.50`, replace equal coherent A/B corruption amplitudes with fixed channel-scale pairs `(1.00,0.50)`, `(1.00,1.50)`, and `(0.50,1.50)` applied to A-anchor (`z`) and B-anchor (`z_b`) corruption respectively. Evaluate magnitudes 0.25, 0.50, and 1.00. The same frozen unit-noise realization drives both channels; only amplitude symmetry is broken.

### F. Mixed drift + common-mode nuisance — 3 cells

Use genuine drift magnitudes 0.25, 0.50, and 1.00 beginning at the inherited event time, plus simultaneous common-mode input corruption of the same numeric magnitude applied to primary and both reference inputs from the same event time onward. Probe gain remains 1.00.

Total: **76 frozen cells**.

## Stress construction

Each stressed stream begins from the inherited Experiment-017/016 generator and is transformed before policy execution. Stress generation may use inherited latent/unit-noise arrays, but must not use policy outcomes. For gain-only cells, only diagnostic response gain changes. For observation-noise cells, the latent trajectory and fault/drift components are held fixed while the explicit modeled observation-noise terms are rescaled. For timing/asymmetry/mixed cells, signals are reconstructed directly from inherited unit-noise arrays and frozen model constants.

## Pairing and audit

All four strategies use the same seed and same stressed stream realization. Audit seeds are `22000..22004`. Paired bootstrap uses 10,000 resamples with RNG seed `22022`.

No implementation choice in this contract may be changed after Experiment-022 outcomes are generated.