# Experiment 012 — Bounded Evidence Record

**Status:** completed prospective evidence; scientific specification remains frozen.

## Provenance

- Frozen/requested evaluation head: `78d8b2d10b92275dfd849b4e87c529420e60a631`
- GitHub Actions run: `32238603241`
- Merged artifact: `experiment-012-evidence`
- Artifact size: `146731830` bytes
- GitHub digest: `sha256:f9bf96bd6e0e1a7083b61decd09e920a894583582a3fa34508a8aecba5b1676e`
- Independent downloaded ZIP SHA-256 reproduced exactly: `f9bf96bd6e0e1a7083b61decd09e920a894583582a3fa34508a8aecba5b1676e`.

## Structural audit

Independent artifact inspection verified:

- exactly `30,400 = 19 cells × 8 strategies × 200 seeds` seed-strategy summaries;
- exactly 200 distinct evaluation seeds per cell, `12000..12199`;
- exactly the eight frozen strategies;
- anchor-A calibration range `600..799`, dual-anchor healthy calibration range `800..999`, both disjoint from evaluation;
- bootstrap seed `12012`;
- audit seeds exactly `12000..12004`;
- exactly `684,000 = 19 × 8 × 5 × 900` time-step audit rows, with 900 rows for every cell/strategy/audit-seed tuple;
- final report records the frozen/reproduced thresholds and all preregistered paired contrasts.

## Preregistered decisions

### H1 — common-mode protection: supported at all three magnitudes

Dual-independent arbitration minus triad-persistence final absolute slope-error differences:

- magnitude 0.25: mean `-0.04084`, 95% CI `[-0.05487, -0.02644]`;
- magnitude 0.50: mean `-0.03554`, 95% CI `[-0.05635, -0.01491]`;
- magnitude 1.00: mean `-0.02684`, 95% CI `[-0.05019, -0.00455]`.

All preregistered CI upper endpoints are below zero.

### H2 — single-anchor fault tolerance: supported for anchor A, with symmetry check passing for anchor B

Under genuine drift plus anchor-A fault, dual arbitration minus Experiment-011 single-anchor `independent_persistence` early operational loss:

- magnitude 0.25: `-2.4067`, 95% CI `[-2.9138, -1.9213]`;
- magnitude 0.50: `-17.7725`, 95% CI `[-19.2722, -16.3009]`;
- magnitude 1.00: `-79.3353`, 95% CI `[-85.1179, -73.4610]`.

The adaptation-by-420 gap versus triad persistence is `0.0` at every magnitude, satisfying the no-more-than-0.10 degradation requirement. For anchor-B fault, dual arbitration minus triad persistence early loss is exactly `0.0` with `[0.0, 0.0]` intervals at all three magnitudes, so the preregistered symmetry/generalization check does not expose an asymmetry.

### H3 — legitimate-drift non-destruction: supported

For healthy-anchor physical drift, the preregistered relative-excess-loss contrast versus triad persistence is exactly `0.0` with `[0.0, 0.0]` intervals at magnitudes 0.25, 0.50, and 1.00. All upper endpoints are below `0.10`.

### H4 — primary-fault regression protection: supported

Dual arbitration minus triad-persistence final absolute slope-error difference is exactly `0.0`, 95% CI `[0.0, 0.0]`, at all three primary-fault magnitudes; all upper endpoints satisfy the frozen `<= 0.01` criterion.

### H5 — coherent dual-anchor-fault boundary: negative boundary preserved

When both auxiliary anchors are corrupted coherently during genuine physical drift, their agreement is not evidence of truth. Dual arbitration minus triad persistence early operational loss is:

- magnitude 0.25: `+2.3083`, 95% CI `[1.8476, 2.8092]`, adaptation-by-420 gap `-0.07`;
- magnitude 0.50: `+16.9778`, 95% CI `[15.5291, 18.4787]`, adaptation gap `-0.325`;
- magnitude 1.00: `+72.7948`, 95% CI `[67.0702, 78.6265]`, adaptation gap `-0.805`.

This is the explicit preregistered identifiability boundary, not an implementation failure and not grounds for retuning.

## Bounded conclusion

Experiment 012 supports the frozen bounded claim: under the specified independent-noise and single-auxiliary-fault model, requiring corroboration from two structurally diverse auxiliary sources reduces dependence on either single auxiliary source while retaining protection against input-family common-mode corruption. It does **not** establish universal fault identification, Byzantine robustness, causal truth, or robustness to correlated/coherent auxiliary failures.

The remaining falsification boundary is no longer single-source reliability. It is **common-cause dependence across nominally independent evidence sources**: when multiple sources share an unmodeled failure mode, agreement can recreate the same identifiability class seen in the original input-family common-mode case. Any subsequent experiment should address observable evidence of source dependence or provenance diversity without using latent truth; simply adding more agreeing sensors would not be scientifically distinct.
