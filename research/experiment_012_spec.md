# Experiment 012 — Prospective Source-Trust Arbitration Under Conflicting Independent Evidence

**Status:** prospectively frozen before any Experiment 012 outcome generation.

## Scientific boundary

Experiments 010–011 establish two complementary limits. Three mutually agreeing input-family sensors cannot identify shared common-mode corruption from their own agreement alone; a structurally independent healthy process-side anchor can break that ambiguity, but a corrupted anchor can over-veto legitimate adaptation. Experiment 012 tests the next distinct boundary: whether redundancy across *structurally diverse evidence families* can arbitrate which source family is untrustworthy without latent truth and without merely transferring the over-veto failure.

No Experiment 012 outcome may be generated before this specification is committed. After freeze, hypotheses, cells, seeds, calibration rules, estimands, inference rules, stopping rules, falsification criteria, and claim boundaries below are immutable in response to observed Experiment 012 outcomes.

## Hypotheses

### H1 — common-mode protection
A dual-independent arbitration gate will improve coefficient integrity relative to Experiment 010 `triad_persistence` when the three input-family channels share common-mode corruption and both independent anchors remain healthy.

### H2 — single-anchor fault tolerance
When genuine physical drift occurs while exactly one independent anchor is corrupted, dual-independent arbitration will materially reduce the early operational-loss penalty relative to Experiment 011 `independent_persistence` while preserving adaptation.

### H3 — legitimate-drift non-destruction
With genuine physical drift and both independent anchors healthy, dual-independent arbitration will not materially degrade early operational loss relative to `triad_persistence`.

### H4 — primary-fault regression protection
Under primary-only input fault, dual-independent arbitration will not materially worsen final coefficient integrity relative to `triad_persistence`.

### H5 — unresolved shared auxiliary failure
If both independent anchors are corrupted coherently in a way that preserves their mutual agreement, the experiment does not assume the arbitration mechanism can identify that failure. This is an explicit falsification/boundary cell, not an omitted case.

## Data-generating process

Use the same scalar adaptive-model plant, event chronology, learner/refit law, primary-input use, stochastic-stream construction, noise laws, and operational/latent loss definitions frozen for Experiment 011 unless explicitly extended below.

The original three input-family streams remain exactly as in Experiment 011. Add two structurally independent process-side anchors, `anchor_a` and `anchor_b`. Conditional on latent physical state, their measurement noises are mutually independent and independent of all input-family sensing noises. Their healthy measurement law has the same scale/form as the Experiment 011 anchor law. Neither anchor may be used by the learner/refit itself; they are diagnostics for gating only.

Fault injections begin at the same frozen event time used by Experiment 011. Physical drift changes the latent plant exactly as previously defined. Input common-mode corruption affects the three input-family streams but not healthy anchors. `anchor_a_fault` affects only anchor A. `anchor_b_fault` affects only anchor B. `dual_anchor_fault` applies the same signed corruption magnitude to both anchors, preserving their agreement as a deliberate unresolved-boundary condition.

## Frozen cells

Evaluate exactly 19 cells:

1. healthy, magnitude 0.00;
2–4. physical drift, magnitudes 0.25, 0.50, 1.00;
5–7. input-family common-mode corruption, magnitudes 0.25, 0.50, 1.00;
8–10. primary-only input fault, magnitudes 0.25, 0.50, 1.00;
11–13. physical drift + anchor A fault, magnitudes 0.25, 0.50, 1.00;
14–16. physical drift + anchor B fault, magnitudes 0.25, 0.50, 1.00;
17–19. physical drift + coherent dual-anchor fault, magnitudes 0.25, 0.50, 1.00.

No cells may be added, removed, or reweighted after outcomes are observed.

## Frozen strategies

Evaluate exactly eight strategies on matched stochastic streams:

1. `frozen`;
2. `continuous`;
3. `threshold`;
4. `persistence`;
5. `health_persistence`;
6. `triad_persistence`;
7. `independent_persistence` — the frozen Experiment 011 single-anchor rule using anchor A;
8. `dual_independent_arbitration` — the new rule below.

Legacy strategies must retain their frozen prior definitions.

## Dual-independent arbitration rule

Let `M_A(t)` and `M_B(t)` be binary persistent mismatch indicators between the input-family consensus prediction and anchors A/B, respectively, each computed using its own healthy-calibrated mismatch threshold. Let `D_AB(t)` be a persistent disagreement indicator between anchors A and B using a separately calibrated healthy threshold.

The new strategy may veto adaptation for suspected input-family common-mode corruption **only when both anchors independently disagree with the input-family consensus while the anchors agree with one another**:

`common_mode_veto(t) = M_A(t) AND M_B(t) AND NOT D_AB(t)`.

When exactly one anchor disagrees with the input-family consensus and the two anchors disagree with one another, the rule must treat source identity as unresolved and must not issue an independent-source veto. Existing triad/health persistence logic remains operative. No latent state, injected-fault label, future sample, or oracle reliability flag may enter arbitration.

When both anchors agree with one another but disagree with the input-family family, the veto is allowed regardless of which family is actually corrupted; the coherent dual-anchor-fault cells deliberately test the resulting identifiability limit.

Persistence duration and chronology must be inherited from Experiment 011; no same-step look-ahead is allowed.

## Calibration

Calibration is healthy-only and outcome-independent.

- Preserve `tau`, `kappa`, and `kappa3` exactly from Experiment 011.
- Reproduce the Experiment 011 anchor-A threshold from its frozen healthy calibration procedure as an implementation check; do not retune it on Experiment 012 evaluation seeds.
- Calibrate the anchor-B mismatch threshold and A-vs-B disagreement threshold using healthy-only calibration seeds exactly `800..999`.
- Threshold-selection quantiles and persistence duration must use the same calibration convention as Experiment 011.
- Evaluation seeds are forbidden from calibration.
- Calibration seeds must never appear in evaluation summaries.

The implementation must record the exact reproduced/calibrated threshold values and calibration seed range in the final report.

## Evaluation seeds and matched randomness

Use exactly 200 evaluation seeds per cell: `12000..12199`, inclusive. Every strategy within a cell/seed must receive matched latent process noise and matched sensing-noise streams for every source it shares. Strategy choice must not alter random-number consumption for shared stochastic variables. Any strategy-specific diagnostic calculation must be deterministic conditional on the pre-generated streams.

## Primary estimands

For each cell and strategy report at minimum:

- mean operational loss over the frozen early post-event window `401..600`;
- mean latent loss over the same window;
- final absolute slope/coefficient error;
- adaptation-by-`t=420` rate;
- total adaptation/update burden;
- mean input-family common-mode-suspect fraction;
- mean anchor-A mismatch fraction;
- mean anchor-B mismatch fraction;
- mean A-vs-B disagreement fraction;
- mean independent veto count;
- coefficient-integrity summaries required by Experiments 010–011.

## Preregistered paired contrasts and decision criteria

All contrasts are seed-paired and use 10,000 bootstrap resamples with bootstrap RNG seed `12012`. Report mean paired difference and percentile 95% CI.

### C1: common-mode coefficient integrity
For each common-mode magnitude, compute

`Delta_CM = final_abs_slope_error(dual_independent_arbitration) - final_abs_slope_error(triad_persistence)`.

H1 is supported at a magnitude only if the 95% CI upper endpoint is `< 0`.

### C2: single-anchor-fault recovery
For each `drift + anchor A fault` magnitude, compute early operational-loss difference

`Delta_A = loss_401_600(dual_independent_arbitration) - loss_401_600(independent_persistence)`.

H2 requires the 95% CI upper endpoint `< 0` at all three magnitudes **and** dual-arbitration adaptation-by-420 must be no more than 0.10 below `triad_persistence` at each magnitude.

The anchor-B-fault cells are symmetry/generalization checks. Compute the analogous dual-arbitration minus `triad_persistence` early-loss contrast; failure of symmetry must be reported and bounds any claim.

### C3: legitimate-drift non-destruction
For each healthy-anchor physical-drift magnitude define per-seed relative excess early loss versus triad persistence:

`R = (L_dual - L_triad) / max(abs(L_triad), 1e-12)`.

H3 is supported only if the 95% CI upper endpoint of mean `R` is `< 0.10` at all three magnitudes.

### C4: primary-fault regression
For each primary-only fault magnitude compute paired final absolute slope-error difference dual arbitration minus triad persistence. H4 is supported only if the 95% CI upper endpoint is `<= 0.01` at all three magnitudes.

### C5: coherent dual-anchor-fault boundary
For each physical-drift + coherent dual-anchor-fault magnitude, report dual arbitration minus triad persistence early operational loss, adaptation-by-420 difference, and veto burden. No success threshold is assigned. These cells test whether coherent auxiliary agreement recreates the same identifiability class. Any material over-veto is a preserved negative finding, not grounds for retuning.

## Falsification logic

The central claim is falsified if H2 or H3 fails. H1 without H2 is insufficient: merely adding another healthy anchor is not considered successful source-trust arbitration if a single auxiliary failure still destroys legitimate adaptation. Failure of H4 bounds the mechanism as introducing unacceptable regression under the already-solved primary-fault case.

H5 is not a failure of implementation. If coherent dual-anchor corruption defeats the mechanism, the bounded conclusion must state that agreement among two auxiliary sources is still not evidence of truth when they share a failure mode.

No threshold, persistence duration, cell, seed, bootstrap rule, or criterion may be changed after any Experiment 012 evaluation outcome is inspected.

## Audit requirements

The evidence artifact must permit independent verification of:

- exact `19 × 8 × 200 = 30,400` seed-strategy summaries;
- exact evaluation seeds `12000..12199` in every cell;
- healthy-only calibration seeds `800..999`, disjoint from evaluation;
- exact preservation/reproduction of prior thresholds;
- matched stochastic streams across strategies;
- both anchor equations and independence construction;
- learner/refit use of `x_primary` only;
- pairwise input-family health statistics and triad logic;
- anchor mismatch and anchor-to-anchor disagreement statistics;
- chronology of persistence and veto decisions;
- operational and latent losses, coefficient integrity, and burden;
- all preregistered paired contrasts and 10,000-resample bootstrap intervals with seed `12012`;
- deterministic equivalence between sharded merge/report formulas and the frozen monolithic formulas.

Record full time-step audit traces for evaluation seeds `12000..12004` for all cells and strategies.

## Stopping and execution rules

Run the complete frozen evaluation once after implementation tests pass. Execution may be sharded by frozen cell. Execution defects may be repaired without changing this specification. A repair must not alter hypotheses, DGP, cells, strategies, seeds, thresholds/calibration rules, estimands, inference, or interpretation criteria. Retriggers after execution-only repairs must change only an execution/request marker or execution implementation and must preserve provenance.

## Claim boundary

A positive Experiment 012 may support only this bounded statement: under the specified independent-noise and single-auxiliary-fault model, requiring corroboration from two structurally diverse auxiliary sources can reduce dependence on either single auxiliary source while retaining protection against input-family common-mode corruption.

It may not establish universal fault identification, causal truth, arbitrary Byzantine robustness, or robustness to correlated/coherent auxiliary failures. Coherent dual-anchor corruption is explicitly outside any positive generalization and must remain visible in the evidence record.
