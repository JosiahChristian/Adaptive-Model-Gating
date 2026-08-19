# Experiment 013 — Prospective Provenance-Aware Corroboration Under Common-Cause Auxiliary Dependence

**Status:** prospectively frozen before any Experiment 013 outcome generation.

## Scientific boundary

Experiment 012 established that corroboration across two healthy structurally diverse auxiliary anchors can break the input-family common-mode ambiguity and tolerate either single auxiliary failure, while coherent corruption of both auxiliary anchors recreates the identifiability failure. The next scientifically distinct boundary is therefore not raw sensor count. It is whether *observable provenance structure* can prevent multiple measurements sharing one upstream failure domain from being mistaken for independent corroboration.

Experiment 013 tests a bounded mechanism: count corroboration by declared provenance/failure domain rather than by sensor. Anchors A and B belong to the same declared provenance group `G1`; anchor C belongs to distinct group `G2`. The experiment asks whether a provenance-aware gate can avoid the over-veto caused by coherent A/B corruption while preserving common-mode input protection, without latent truth, injected-fault labels, or oracle reliability flags.

No Experiment 013 outcome may be generated before this specification is committed. After freeze, hypotheses, DGP, cells, strategies, seeds, calibration, estimands, inference, stopping rules, falsification criteria, audit requirements, and claim boundaries below are immutable in response to observed Experiment 013 outcomes.

## Hypotheses

### H1 — common-mode input protection
With healthy auxiliary provenance groups, provenance-aware corroboration improves final coefficient integrity relative to `triad_persistence` under input-family common-mode corruption.

### H2 — shared-G1 fault tolerance
During genuine physical drift plus coherent corruption of A and B, provenance-aware corroboration materially reduces early operational-loss over-veto relative to a naive sensor-count quorum while preserving adaptation.

### H3 — distinct-G2 single-fault tolerance
During genuine physical drift plus corruption of C only, provenance-aware corroboration does not materially degrade early operational loss or adaptation relative to `triad_persistence`.

### H4 — legitimate-drift non-destruction
With genuine physical drift and all auxiliary sources healthy, provenance-aware corroboration does not materially degrade early operational loss relative to `triad_persistence`.

### H5 — primary-fault regression protection
Under primary-only input fault, provenance-aware corroboration does not materially worsen final coefficient integrity relative to `triad_persistence`.

### H6 — provenance-model misspecification boundary
If A and B are actually common-cause dependent but are falsely declared as distinct provenance groups, the experiment does not assume the mechanism can identify that hidden dependence. This is an explicit negative-boundary condition.

### H7 — all-provenance coherent-fault boundary
If both declared provenance groups are coherently corrupted, provenance diversity cannot establish truth from agreement alone. This is an explicit negative boundary.

## Data-generating process

Inherit the scalar adaptive-model plant, event chronology, learner/refit law, primary-input use, stochastic-stream construction, operational/latent losses, input-family sensing equations, and frozen legacy thresholds from Experiment 012 unless explicitly extended below.

Retain input-family channels exactly as before. Use three process-side auxiliary anchors A, B, and C. A and B are separate measurements in declared provenance group `G1`; C is in distinct provenance group `G2`. Healthy conditional measurement noise is independently generated for each physical measurement, but the DGP additionally supports a group-level common-cause corruption applied coherently to A and B. C is unaffected by G1 common-cause corruption. No auxiliary anchor may enter the learner/refit; all are gating diagnostics only.

Faults begin at the inherited frozen event time. Physical drift changes latent plant dynamics exactly as previously defined. Input common-mode corruption affects the three input-family channels only. `g1_common_fault` applies the same signed corruption magnitude to A and B. `g2_fault` affects C only. `all_aux_fault` applies coherent same-signed corruption to A, B, and C. `misdeclared_g1_fault` uses the same physical corruption as `g1_common_fault` but supplies the gate with deliberately incorrect provenance metadata declaring A and B as distinct groups; this tests dependence-model misspecification, not detection from latent truth.

## Frozen cells

Evaluate exactly 22 cells:

1. healthy, magnitude 0.00;
2–4. physical drift, magnitudes 0.25, 0.50, 1.00;
5–7. input-family common-mode corruption, magnitudes 0.25, 0.50, 1.00;
8–10. primary-only input fault, magnitudes 0.25, 0.50, 1.00;
11–13. physical drift + coherent G1(A/B) fault, magnitudes 0.25, 0.50, 1.00;
14–16. physical drift + G2(C) fault, magnitudes 0.25, 0.50, 1.00;
17–19. physical drift + misdeclared G1(A/B) fault, magnitudes 0.25, 0.50, 1.00;
20–22. physical drift + coherent all-auxiliary fault, magnitudes 0.25, 0.50, 1.00.

No cell may be added, removed, or reweighted after outcomes are observed.

## Frozen strategies

Evaluate exactly nine strategies on matched stochastic streams:

1. `frozen`;
2. `continuous`;
3. `threshold`;
4. `persistence`;
5. `health_persistence`;
6. `triad_persistence`;
7. `independent_persistence` — frozen Experiment 011 anchor-A rule;
8. `naive_three_anchor_quorum` — sensor-count rule defined below;
9. `provenance_aware_quorum` — new rule defined below.

Legacy strategies retain their prior frozen definitions.

## Naive three-anchor quorum

Let persistent mismatch indicators `M_A(t)`, `M_B(t)`, and `M_C(t)` indicate disagreement of each anchor with the input-family consensus using separately healthy-calibrated thresholds. The naive comparator may veto for suspected input-family common-mode corruption when at least two of the three anchor mismatch indicators are active and the mismatching anchors mutually agree under their calibrated pairwise disagreement thresholds. It counts sensors, not provenance groups.

## Provenance-aware quorum

The gate receives only declared provenance-group membership, not reliability or fault labels. Under correct metadata, A and B map to `G1`, C maps to `G2`.

For each group, define a persistent group mismatch vote as active only if at least one member anchor mismatches the input-family consensus. Multiple mismatching members of the same provenance group contribute **one vote total**. A provenance-aware independent-source veto is permitted only when mismatch votes are active in at least two distinct declared provenance groups and representative evidence across those groups is mutually consistent under healthy-calibrated cross-group disagreement thresholds.

Thus coherent A/B disagreement with the input family contributes one `G1` vote and cannot by itself veto adaptation. A/B plus C corroboration can veto. If metadata incorrectly declares A and B distinct, the mechanism must use the supplied metadata exactly; it may not infer hidden common cause from the injected-fault label or latent state.

Existing triad/health persistence remains operative. Persistence duration and decision chronology are inherited from Experiment 012. No same-step look-ahead, future sample, latent truth, injected-fault label, or oracle reliability may enter the rule.

## Calibration

Calibration is healthy-only and outcome-independent.

- Preserve `tau`, `kappa`, `kappa3`, and prior anchor-A threshold exactly by reproduction from prior frozen procedures.
- Reproduce anchor-B thresholds from Experiment 012 as an implementation check.
- Calibrate anchor-C mismatch and required A/C and B/C cross-group disagreement thresholds using healthy-only seeds exactly `1000..1199`.
- Use the same quantile and persistence conventions frozen in Experiment 012.
- Evaluation seeds are forbidden from calibration and calibration seeds may not appear in evaluation summaries.
- Record all reproduced/calibrated values and calibration ranges in the final report.

## Evaluation seeds and matched randomness

Use exactly 200 evaluation seeds per cell: `13000..13199`, inclusive. Every strategy within a cell/seed receives matched latent process noise and all shared sensing-noise streams. Pre-generate all streams before strategy execution so strategy choice cannot alter random-number consumption. Strategy-specific diagnostics are deterministic conditional on those streams and declared provenance metadata.

## Primary estimands

For every cell and strategy report at minimum:

- mean operational loss over steps `401..600`;
- mean latent loss over `401..600`;
- final absolute slope/coefficient error;
- adaptation-by-`t=420` rate;
- total update/adaptation burden;
- input-family common-mode-suspect fraction;
- mismatch fraction for A, B, and C;
- A/B, A/C, and B/C disagreement fractions;
- raw sensor mismatch-vote count;
- distinct provenance-group mismatch-vote count;
- independent/provenance veto count;
- coefficient-integrity summaries inherited from Experiments 010–012.

## Preregistered paired contrasts and criteria

All contrasts are seed-paired. Use 10,000 bootstrap resamples with bootstrap RNG seed `13013`; report mean paired difference and percentile 95% CI.

### C1 — common-mode coefficient integrity
For each input common-mode magnitude compute final absolute slope-error difference:

`Delta_CM = error(provenance_aware_quorum) - error(triad_persistence)`.

H1 is supported at a magnitude only if the 95% CI upper endpoint is `< 0`.

### C2 — coherent G1 fault recovery
For each `drift + g1_common_fault` magnitude compute early operational-loss difference:

`Delta_G1 = loss(provenance_aware_quorum) - loss(naive_three_anchor_quorum)`.

H2 requires the 95% CI upper endpoint `< 0` at all three magnitudes and provenance-aware adaptation-by-420 no more than 0.10 below `triad_persistence` at each magnitude.

### C3 — G2 single-fault tolerance
For each `drift + g2_fault` magnitude compute relative excess early loss versus triad persistence:

`R_G2 = (L_provenance - L_triad) / max(abs(L_triad), 1e-12)`.

H3 requires the 95% CI upper endpoint of mean `R_G2` `< 0.10` and adaptation-by-420 no more than 0.10 below triad persistence at all three magnitudes.

### C4 — legitimate-drift non-destruction
For each healthy-auxiliary physical-drift magnitude compute

`R = (L_provenance - L_triad) / max(abs(L_triad), 1e-12)`.

H4 requires the 95% CI upper endpoint of mean `R` `< 0.10` at all three magnitudes.

### C5 — primary-fault regression
For each primary-only fault magnitude compute final absolute slope-error difference provenance-aware minus triad persistence. H5 requires the 95% CI upper endpoint `<= 0.01` at all three magnitudes.

### C6 — provenance misspecification boundary
For each `drift + misdeclared_g1_fault` magnitude report provenance-aware minus triad early operational loss, adaptation-by-420 difference, and veto burden. No success threshold is assigned. Material over-veto is a preserved negative finding and bounds any claim to correctness of the supplied provenance model.

### C7 — all-auxiliary coherent-fault boundary
For each `drift + all_aux_fault` magnitude report provenance-aware minus triad early operational loss, adaptation-by-420 difference, and veto burden. No success threshold is assigned. Material over-veto is a preserved identifiability boundary.

## Falsification logic

The central claim is falsified if H2, H3, or H4 fails. H1 alone is insufficient. Failure of H5 bounds the mechanism as regressing on an already-solved primary-fault condition. H6 and H7 are deliberate negative-boundary tests and may not be retuned away.

No threshold, persistence duration, cell, seed, bootstrap rule, provenance mapping in the correctly declared cells, estimand, or decision criterion may be changed after any Experiment 013 outcome is inspected.

## Audit requirements

The evidence artifact must permit independent verification of:

- exact `22 × 9 × 200 = 39,600` seed-strategy summaries;
- exact evaluation seeds `13000..13199` in every cell;
- healthy-only new calibration seeds `1000..1199`, disjoint from evaluation and prior calibration ranges;
- exact reproduction of inherited thresholds;
- matched stochastic streams across strategies;
- A/B/C measurement equations and G1 common-cause construction;
- declared provenance mapping supplied to each cell, including deliberate misspecification only in the frozen misspecification cells;
- learner/refit use of `x_primary` only;
- input-family health/triad logic;
- all anchor mismatch, pairwise disagreement, raw-vote, provenance-vote, and veto statistics;
- decision chronology and persistence state;
- operational/latent losses, coefficient integrity, and burden;
- all preregistered paired contrasts and 10,000-resample intervals using seed `13013`;
- deterministic equivalence between sharded merge/report formulas and the frozen monolithic formulas.

Record full time-step audit traces for evaluation seeds `13000..13004` for all cells and strategies. Expected audit rows: `22 × 9 × 5 × 900 = 891,000`.

## Stopping and execution rules

Run the complete frozen evaluation once after implementation tests pass. Execution may be sharded by frozen cell. Execution defects may be repaired without changing this specification. Repairs must not alter hypotheses, DGP, cells, strategies, seeds, calibration, provenance semantics, estimands, inference, or interpretation criteria. Retriggers after execution-only repair must preserve provenance and change only execution implementation and/or an execution request marker.

## Claim boundary

A positive Experiment 013 may support only this bounded statement: under the specified model and correct declared provenance/failure-domain metadata, counting corroboration across distinct provenance groups rather than raw sensors can reduce vulnerability to common-cause corruption within one declared auxiliary failure domain while retaining protection against input-family common-mode corruption.

It may not establish automatic discovery of hidden dependencies, correctness of provenance metadata, universal causal truth, arbitrary Byzantine robustness, or robustness when all declared provenance groups share coherent corruption. Misdeclared dependence and all-provenance coherent corruption remain explicit negative boundaries.