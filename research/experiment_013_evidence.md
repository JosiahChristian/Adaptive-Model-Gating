# Experiment 013 — Audited Evidence Record

**Status:** completed and independently audited against the prospectively frozen specification `research/experiment_013_spec.md`.

## Provenance

- completed Actions run: `32275083856`
- head/request commit: `dda4fbc1502500ad86d47ac3c2a9857ebf830c84`
- artifact: `experiment-013-evidence`
- artifact size: `210098220` bytes
- GitHub artifact digest: `sha256:0ba4b945ac83aeb92143a506feae471bf2fe4c3f9b7699b73047ccdbf84687cf`
- independently reproduced SHA-256: `0ba4b945ac83aeb92143a506feae471bf2fe4c3f9b7699b73047ccdbf84687cf`

The unit-test job, non-evaluation-seed execution smoke test, all 22 frozen cell shards, deterministic merge, artifact upload, and evidence registration passed.

## Structural audit

Independent artifact inspection verified:

- exactly `39,600 = 22 cells × 9 strategies × 200 seeds` seed-strategy summaries;
- exactly 22 frozen cells and all nine frozen strategies;
- exactly evaluation seeds `13000..13199` in every cell;
- exactly `891,000 = 22 × 9 × 5 × 900` time-step audit rows;
- audit seeds `13000..13004`;
- new healthy-only anchor-C calibration seeds `1000..1199`;
- bootstrap seed `13013`;
- reproduced legacy thresholds `tau=0.4749575582753968`, `kappa=0.004715841027139986`, `kappa3=0.008353014684419843`, anchor-A/B thresholds from prior frozen procedures, and new frozen anchor-C/cross-group thresholds recorded in the merged report.

## Preregistered results

### H1 — common-mode input protection

Provenance-aware quorum minus triad-persistence final absolute slope error:

- magnitude 0.25: mean `-0.04236`, 95% CI `[-0.05632, -0.02842]` — supported;
- magnitude 0.50: mean `-0.02417`, 95% CI `[-0.05022, 0.00153]` — not supported under the strict preregistered criterion because the CI upper endpoint crosses zero;
- magnitude 1.00: mean `-0.04875`, 95% CI `[-0.08499, -0.01418]` — supported.

Thus common-mode coefficient-integrity improvement is positive at two of three tested magnitudes, but not uniformly established.

### H2 — coherent G1(A/B) common-cause fault recovery

Provenance-aware quorum minus naive three-anchor sensor-count quorum early operational loss:

- magnitude 0.25: `-2.1241`, CI `[-2.6469, -1.6385]`;
- magnitude 0.50: `-17.0236`, CI `[-18.4987, -15.5582]`;
- magnitude 1.00: `-71.0470`, CI `[-76.9723, -65.1826]`.

Adaptation-by-420 gap versus triad persistence is exactly `0.0` at all three magnitudes. H2 is supported at all frozen magnitudes.

### H3 — G2(C) single-fault tolerance

Relative excess early loss versus triad persistence is exactly `0.0` with bootstrap CI `[0.0, 0.0]` and adaptation gap `0.0` at all three magnitudes. H3 is supported.

### H4 — legitimate-drift non-destruction

Relative excess early loss versus triad persistence is exactly `0.0` with bootstrap CI `[0.0, 0.0]` at all three drift magnitudes. H4 is supported.

### H5 — primary-fault regression protection

Final absolute slope-error difference versus triad persistence is exactly `0.0` with CI `[0.0, 0.0]` at all three magnitudes. H5 is supported.

## Preserved negative boundaries

### H6 — provenance metadata misspecification

When physically common-cause A/B corruption is falsely declared as distinct provenance groups, the provenance-aware rule collapses to the naive failure mode. Early-loss penalties versus triad persistence rise from about `+2.12` to `+71.05`, and the adaptation-by-420 gap worsens to `-0.755` at magnitude 1.0. This is a preserved negative result: the mechanism does not discover hidden dependence automatically.

### H7 — all-provenance coherent corruption

When all declared provenance groups share coherent corruption, early-loss penalties versus triad persistence are about `+2.15`, `+17.67`, and `+75.39` across the three magnitudes; at magnitude 1.0 the adaptation-by-420 gap is `-0.78`. Provenance labels cannot establish truth when all declared independent domains actually fail coherently.

## Bounded conclusion

Experiment 013 supports the central preregistered claim: **with correct declared provenance/failure-domain metadata, counting corroboration across distinct provenance groups rather than raw sensors can eliminate the specified over-veto caused by common-cause corruption within one declared auxiliary domain while preserving legitimate drift adaptation and prior primary-fault behavior.**

The evidence does **not** establish automatic discovery of hidden dependence, correctness of provenance metadata, arbitrary Byzantine robustness, or universal robustness to coherent corruption spanning all declared provenance groups. H1 was not uniformly supported at the middle common-mode magnitude and must remain reported as such.
