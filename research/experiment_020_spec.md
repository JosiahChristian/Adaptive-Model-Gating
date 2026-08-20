# Experiment 020 — Prospective Early Edge-Targeted Round-4 Confirmation

**Status:** prospectively corrected and frozen before any Experiment 020 calibration or evaluation outcome generation.

## Scientific boundary

Experiment 019 established adaptive edge-targeted confirmation efficiency after four full diagnostic rounds. At `g_probe=0.50`, targeted coverage was `0.995`, precision `1.000`, wrong acceptance `0.000`, and mean diagnostic energy `0.923875`.

Experiment 020 asks whether the reciprocal edge can be selected one round earlier, after round 3, so that round 4 initially challenges only the two endpoints of the leading candidate edge. If the early targeted round-4 evidence is insufficient, the strategy executes the missing third round-4 block and then applies the inherited Experiment-019 decision rules to the completed three-target round-4 evidence.

A pre-implementation review identified an impossible invariant in the initial draft: because diagnostic noise is time-indexed, reordering a target block cannot reproduce Experiment 019's seedwise round-4 scores exactly. This correction is made before any Experiment 020 calibration or evaluation outcome exists. Experiment 020 therefore tests **distributionally equivalent fallback-rule preservation**, not impossible pathwise equality.

No Experiment 020 outcome may be generated before this corrected specification is committed. After this correction freeze, selector rules, chronology, calibration ranges, cells, seeds, thresholds, comparators, estimands, and success criteria below are immutable in response to outcomes.

## Hypotheses

- **H1 — early-target efficiency:** at `g_probe=0.50`, round-3 selection plus two-endpoint round-4 confirmation reduces mean diagnostic energy relative to Experiment 019 while retaining high final coverage and precision.
- **H2 — fallback-rule preservation:** when early targeting does not qualify, completing the third round-4 target and applying the inherited Experiment-019 rules preserves coverage, precision, operational behavior, and safety to preregistered noninferiority tolerances. Exact seedwise score equality is neither required nor claimed.
- **H3 — round-3 selector validity:** the unique leading edge after round 3 is sufficiently accurate at moderate gain for early targeting to be useful.
- **H4 — standard-gain preservation:** `g_probe=1.00` behavior remains high-coverage/high-precision and does not incur greater mean burden than Experiment 019.
- **H5 — attenuation safety:** at gains `0.375`, `0.25`, and `0.125`, the early layer does not increase wrong acceptance or operational loss relative to Experiment 019 or `triad_persistence`.
- **H6 — inherited regression protection:** genuine drift, common-mode corruption, and primary-only faults remain materially unchanged.
- **H7 — coherent-all-auxiliary boundary preservation:** apparent provenance confidence remains explicitly non-identifying when all auxiliary evidence is coherently corrupted.

## Inherited model and rounds 1–3

Inherit Experiment 019's plant, sensing, learner, operational gate, physical A/B-vs-C provenance partition, diagnostic noise law, calibration conventions, event time, losses, fallback behavior, and all legacy strategy semantics exactly.

Retain baseline `181..200` and rounds 1–3 exactly:

- round 1: amplitude `0.025`, A `201..205`, B `206..210`, C `211..215`;
- round 2: amplitude `0.050`, A `216..220`, B `221..225`, C `226..230`;
- round 3: amplitude `0.100`, A `231..235`, B `236..240`, C `241..245`.

The cumulative round-3 reciprocal scores `Q_3(AB)`, `Q_3(AC)`, and `Q_3(BC)` are computed exactly as inherited from Experiment 017.

## Frozen round-3 leading-edge selector

After round 3, identify the unique pair with the largest `Q_3` value.

- A unique maximum selects that pair for early round-4 targeting.
- An exact numerical tie selects no pair; in that case execute the complete inherited three-block round 4 and continue under the Experiment-019 rules.
- The selector may use only round-1..3 diagnostic observations and frozen statistics.
- It may not use family labels, known gain, oracle truth, post-event operational values, or evaluation outcomes.

## Early targeted round 4

Round-4 amplitude remains exactly `0.200`.

For a selected pair `(i,j)`, challenge `i` during `246..250` and `j` during `251..255`. The unselected target is not challenged before the early decision.

The incremental early-target round-4 energy is exactly `2 * 5 * 0.2^2 = 0.400000`. Rounds 1–3 consume exactly `0.196875`, so energy at the early decision point is exactly `0.596875`.

## Early targeted round-4 statistic and calibration

For the selected pair, extend its cumulative signed statistic using amplitudes `[0.025, 0.050, 0.100, 0.200]` and the two selected round-4 reciprocal responses. Nonselected pairs retain their round-3 status and cannot newly confidence-qualify at the early decision.

Use new null calibration seeds exactly `5000..5999`, disjoint from all inherited calibration ranges and evaluation seeds.

For each zero-response calibration seed:

1. compute the frozen round-3 leading-edge selector;
2. if there is a unique selected pair, execute the two corresponding early round-4 blocks;
3. collect the selected pair's updated reciprocal cumulative statistic.

Freeze:

- `mu_4^E` = empirical 99th percentile of selected-edge null statistics;
- `nu_4^E` = empirical 99.9th percentile of selected-edge null statistics.

Early deployment is permitted only if the early graph contains exactly one reciprocal edge, producing one two-source component and one singleton, and the selected edge exceeds `nu_4^E`. Otherwise continue to fallback completion.

## Fallback completion and inherited rule application

If the early targeted decision does not qualify, challenge the sole unselected target during `256..260` at amplitude `0.200`.

After this block, there is exactly one five-step amplitude-0.200 response for each target identity A, B, and C. Because target chronology differs from Experiment 019 for some selected pairs, the resulting seedwise response matrix is **not required to equal** Experiment 019's matrix. It is generated under the same physical response law, amplitude, duration, and independent-noise distribution.

Apply the inherited round-4 cumulative graph thresholds and the inherited Experiment-019 round-4 leading-edge selector/targeted-round-5 deployment logic without threshold relaxation or outcome-dependent modification. The fallback claim is therefore rule-level and distributional, not pathwise.

If the round-3 selector ties, execute A `246..250`, B `251..255`, C `256..260` exactly as Experiment 019 and continue under the inherited rules.

## Frozen cells

Evaluate exactly the same 28 cells as Experiments 017–019:

1. healthy magnitude 0.00;
2–4. genuine drift magnitudes 0.25, 0.50, 1.00;
5–7. common-mode input corruption magnitudes 0.25, 0.50, 1.00;
8–10. primary-only input fault magnitudes 0.25, 0.50, 1.00;
11–13. drift + coherent A/B auxiliary fault at `g_probe=1.00`;
14–16. same A/B fault at `g_probe=0.50`;
17–19. same A/B fault at `g_probe=0.375`;
20–22. same A/B fault at `g_probe=0.25`;
23–25. same A/B fault at `g_probe=0.125`;
26–28. drift + coherent all-auxiliary fault at `g_probe=1.00`.

## Frozen strategies

Evaluate exactly sixteen strategies: the fifteen frozen Experiment-019 strategies plus

16. `early_targeted_replicated_selective_cumulative_provenance_quorum`.

The first fifteen retain their Experiment-019 meanings exactly. Only strategy 16 may use the early round-3 selector and reordered round-4 observations.

## Seeds and bootstrap

- inherited round calibration: `1800..1999`;
- inherited cumulative calibration: `2000..2999`;
- inherited full round-5 calibration: `3000..3999`;
- inherited targeted round-5 calibration: `4000..4999`;
- new early-target round-4 calibration: `5000..5999`;
- evaluation seeds: exactly `20000..20199`;
- 200 seeds per cell;
- paired bootstrap: 10,000 resamples, RNG seed `20020`;
- audit seeds: `20000..20004`.

All calibration and evaluation ranges are disjoint.

## Primary estimands

Retain all Experiment-019 estimands. For the new strategy additionally record:

- round-3 `Q_3` values;
- round-3 selected edge and tie indicator;
- audit-only round-3 selector correctness;
- early round-4 execution indicator;
- `mu_4^E`, `nu_4^E`;
- early selected-edge updated score;
- early structural/qualified state;
- missing-third-block execution indicator;
- fallback-completion indicator;
- later Experiment-019 targeted-round-5 execution indicator;
- final accepted/abstained state;
- accepted-partition correctness as audit-only truth;
- total target-block count and diagnostic energy.

## Preregistered contrasts and criteria

### C1 — moderate-gain early-target efficiency

At all three `g_probe=0.50` A/B-fault magnitudes compare the new strategy with Experiment 019.

H1 requires:

- final coverage `>=0.95`;
- coverage no more than `0.03` absolute below Experiment 019;
- accepted precision `>=0.99`;
- wrong acceptance `<=0.01`;
- early-loss difference versus Experiment 019 paired-bootstrap CI upper endpoint `<=0.02 * mean(Experiment019 early loss)`;
- adaptation-by-420 gap versus Experiment 019 `>=-0.05`;
- mean diagnostic energy `<=0.75`;
- mean energy at least `0.12` below Experiment 019.

Failure of either coverage noninferiority or the energy-reduction requirement falsifies the central claim.

### C2 — fallback-rule preservation

Across cells/seeds entering fallback completion, compare the new strategy with Experiment 019 using paired evaluation seeds. Require:

- final coverage gap versus Experiment 019 `>=-0.03` in each A/B-fault gain/magnitude cell;
- accepted precision `>=0.99` whenever at least one decision is accepted;
- wrong acceptance `<=0.01` at gains `1.00`, `0.50`, and `0.125`, and `<=0.05` at gains `0.375` and `0.25`;
- early-loss difference versus Experiment 019 paired-bootstrap CI upper endpoint `<=0.05 * mean(Experiment019 early loss)` in each A/B-fault cell;
- adaptation-by-420 gap versus Experiment 019 `>=-0.10`.

Failure of these fallback noninferiority conditions falsifies H2. No exact seedwise score equality is tested.

### C3 — round-3 selector validity

Among `g_probe=0.50` A/B-fault seeds entering early targeting, selector correctness must be `>=0.90`.

### C4 — standard-gain preservation

At all three `g_probe=1.00` A/B-fault magnitudes require:

- coverage `>=0.99`;
- precision `>=0.99`;
- wrong acceptance `<=0.01`;
- mean energy `<=0.60`;
- adaptation gap versus Experiment 019 `>=-0.05`.

### C5 — attenuation safety

At all `g_probe=0.375`, `0.25`, and `0.125` A/B-fault cells require:

- wrong acceptance `<=0.05` (`<=0.01` at `0.125`);
- early-loss CI upper endpoint versus `triad_persistence` `<=0.05 * mean(triad early loss)` (`<=0.02` fraction at `0.125`);
- adaptation gap versus triad `>=-0.10`.

At `g_probe=0.125`, abstention must remain `>=0.90`.

### C6 — inherited regression protection

For every genuine-drift magnitude, relative excess early-loss CI upper endpoint versus Experiment 019 must remain `<0.05` and adaptation gap `>=-0.05`.

For common-mode and primary-only faults, final coefficient-error difference versus Experiment 019 must have paired-bootstrap CI upper endpoint `<=0.05` at all magnitudes.

### C7 — coherent-all-auxiliary negative boundary

Report early-targeted-minus-triad early loss and accepted provenance rate. No success claim is assigned; apparent provenance confidence remains explicitly non-identifying.

## Frozen claim logic

The central Experiment-020 claim is **earlier adaptive targeting efficiency**: round-3 reciprocal evidence contains enough directional information to focus round-4 intervention on two targets, permit safe early qualification in a useful subset of moderate-gain cases, and reduce mean diagnostic burden while retaining the validated Experiment-019 decision rules as a distributionally equivalent fallback after completion.

- H1 is required for the central claim.
- H2 is a mandatory fallback-validity condition.
- H3 provides the mechanistic explanation.
- H4–H6 are mandatory safety/regression protections.
- H7 remains an explicit unsolved truth-identifiability boundary.

No outcome-driven threshold, selector, amplitude, timing, or success-criterion modification is permitted after this corrected freeze.
