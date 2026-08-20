# Experiment 019 — Prospective Adaptive Edge-Targeted Confirmation

**Status:** prospectively frozen before any Experiment 019 outcome generation.

## Scientific boundary

Experiment 018 established that one additional independent confirmation round at the already-frozen maximum amplitude `0.20` repairs the Experiment-017 moderate-gain (`g_probe=0.50`) coverage failure: coverage increased from `0.640` to `0.895`, accepted and rescued-decision precision were `1.000`, wrong acceptance remained `0.000`, and mean diagnostic energy was `1.003875`. It also showed a partial coverage increase at `g_probe=0.375` (`0.445`) while preserving safe abstention at gains `0.25` and `0.125`.

Experiment 018 therefore supports additional independent evidence, but its fifth round always spends three target blocks whenever the four-round selective rule abstains. The next scientific question is whether this confirmation can be made **information-efficient** by spending new diagnostic budget only on the reciprocal edge that is already the leading candidate after round 4.

Experiment 019 does not relax confidence thresholds, increase intervention amplitude, add additional rounds, use outcome data for target selection, or attempt to solve the coherent-all-auxiliary truth-identifiability boundary.

No Experiment 019 outcome may be generated before this specification is committed. After freeze, the plant, streams, candidate-selection rule, intervention chronology, calibration, strategies, cells, seeds, estimands, criteria, and claim boundaries below are immutable in response to outcomes.

## Hypotheses

- **H1 — moderate-gain efficiency:** at `g_probe=0.50`, adaptive edge-targeted confirmation preserves most of Experiment-018 final deployment coverage and precision while reducing mean diagnostic energy.
- **H2 — standard-gain preservation:** at `g_probe=1.00`, the targeted strategy retains the already-established high-coverage, high-precision behavior without extra burden when round 4 already qualifies.
- **H3 — candidate-target validity:** among seeds requiring confirmation, the frozen round-4 leading-edge rule selects the physically correct reciprocal edge often enough for targeted replication to be useful; selection quality is audit-only and may not alter deployment.
- **H4 — attenuation safety:** at gains `0.375`, `0.25`, and `0.125`, targeting does not create excess wrong acceptance or operational harm relative to the Experiment-018 full-confirmation strategy or `triad_persistence`.
- **H5 — legitimate-drift non-destruction:** genuine drift behavior remains materially unchanged versus `triad_persistence`.
- **H6 — fault regression protection:** common-mode input and primary-only fault protections established in Experiment 018 are not materially degraded.
- **H7 — coherent-all-auxiliary boundary preservation:** targeted confirmation must not be interpreted as a truth certificate when all auxiliary evidence is coherently corrupted.

## Inherited model and first four rounds

Inherit Experiment 018's plant, sensing, learner, operational gate, physical A/B-vs-C provenance partition, diagnostic-only intervention law, all operational stochastic streams, first four diagnostic rounds, Experiment-016 round thresholds, Experiment-017 cumulative thresholds `mu_1..mu_4` and `nu_1..nu_4`, event time, losses, fallback behavior, and legacy strategy semantics exactly.

Retain the baseline `181..200` and rounds 1–4 exactly:

- round 1 `d1=0.025`, A `201..205`, B `206..210`, C `211..215`;
- round 2 `d2=0.050`, A `216..220`, B `221..225`, C `226..230`;
- round 3 `d3=0.100`, A `231..235`, B `236..240`, C `241..245`;
- round 4 `d4=0.200`, A `246..250`, B `251..255`, C `256..260`.

All first-four-round deploy/stop behavior is inherited unchanged.

## Frozen leading-edge selector

The selector is evaluated **only when the Experiment-017 selective cumulative rule has not confidence-qualified by the end of round 4**.

Using the already-computed round-4 reciprocal scores

`Q_4(AB), Q_4(AC), Q_4(BC)`, define the leading edge as the unique pair with the largest `Q_4` value.

- If there is a unique maximum, select that pair.
- Exact numerical ties select no pair and immediately abstain to `triad_persistence`.
- No oracle labels, operational post-event values, family names, known gain, candidate physical truth, or Experiment-018 outcomes may affect selection.

The selector itself does not authorize deployment. It only determines which two target blocks receive the confirmatory intervention.

## Edge-targeted round 5

Use the same round-5 amplitude ceiling `0.200`, the same fresh diagnostic noise convention, and the same physical response law as Experiment 018.

For selected edge:

- AB: challenge A at `261..265`, challenge B at `266..270`; no C challenge;
- AC: challenge A at `261..265`, challenge C at `266..270`; no B challenge;
- BC: challenge B at `261..265`, challenge C at `266..270`; no A challenge.

Only two five-step target blocks are executed. All diagnostic activity ends by step `270`, still strictly before the operational event at `401`.

The incremental targeted-confirmation energy is exactly

`2 * 5 * 0.2^2 = 0.400000`.

The maximum total energy if all first four rounds and targeted confirmation execute is therefore exactly `1.196875`, compared with Experiment 018's full-confirmation maximum `1.396875`.

No sixth round, third target block, stronger amplitude, longer block, or threshold relaxation is permitted.

## Targeted confirmation statistic

For the selected pair `(i,j)`, compute the two ordered round-5 responses needed for reciprocal evidence: response of i while targeting j and response of j while targeting i.

Extend only that selected pair's cumulative signed statistic using amplitudes `[0.025,0.050,0.100,0.200,0.200]` exactly as in Experiment 018. The other two pairwise `Q` values remain frozen at their round-4 values and receive no imputed round-5 observation.

Define the targeted round-5 graph by:

- selected pair: compare its updated `Q_5^targeted` to newly calibrated targeted `mu_5^T` and `nu_5^T`;
- nonselected pairs: retain their round-4 base-edge status using inherited `mu_4`; they cannot become newly confidence-qualified.

Deployment is permitted only if the resulting graph contains exactly one reciprocal edge, yielding one two-source component and one singleton, and the selected edge exceeds `nu_5^T`.

Otherwise abstain and use exact inherited `triad_persistence` behavior.

## New null calibration

Use exactly seeds `4000..4999`, disjoint from every inherited calibration range and all evaluation seeds.

For each seed, generate zero-response diagnostic streams and apply the frozen leading-edge selector to the round-4 null scores. For seeds with a unique selected pair, execute the corresponding two-block targeted round 5 and collect the selected pair's updated reciprocal cumulative statistic.

Freeze:

- `mu_5^T` = empirical 99th percentile of targeted selected-edge null statistics;
- `nu_5^T` = empirical 99.9th percentile of targeted selected-edge null statistics.

If a null seed has an exact selector tie, it contributes no targeted statistic. Evaluation data may not contribute to calibration.

## Frozen cells

Evaluate exactly the same 28 cells as Experiments 017 and 018:

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

No cells may be added, removed, relabeled, reweighted, or selected after outcomes.

## Frozen strategies

Evaluate exactly fifteen strategies:

1. `frozen`;
2. `continuous`;
3. `threshold`;
4. `persistence`;
5. `health_persistence`;
6. `triad_persistence`;
7. `independent_persistence`;
8. `naive_three_anchor_quorum`;
9. `oracle_provenance_quorum`;
10. `max_probe_provenance_quorum`;
11. `sequential_provenance_quorum`;
12. `cumulative_provenance_quorum`;
13. `selective_cumulative_provenance_quorum`;
14. `replicated_selective_cumulative_provenance_quorum` (Experiment-018 full-confirmation comparator);
15. `targeted_replicated_selective_cumulative_provenance_quorum` (new deployable strategy).

The first fourteen retain their Experiment-018 meanings exactly. Only strategy 15 may use the edge-targeted round-5 observations.

## Seeds and bootstrap

- inherited round calibration: `1800..1999`;
- inherited cumulative calibration: `2000..2999`;
- inherited full round-5 calibration: `3000..3999`;
- new targeted round-5 calibration: `4000..4999`;
- evaluation seeds: exactly `19000..19199`, inclusive;
- 200 seeds per cell;
- paired bootstrap: 10,000 resamples, RNG seed `19019`;
- audit seeds: `19000..19004`.

All calibration and evaluation ranges are disjoint.

## Primary estimands

Retain all Experiment-018 estimands. For the targeted strategy additionally record:

- round-4 leading edge and its three `Q_4` values;
- selector tie indicator;
- audit-only leading-edge physical correctness;
- targeted round-5 execution indicator;
- selected target identities;
- targeted `mu_5^T`, `nu_5^T`;
- selected-edge updated reciprocal score;
- final graph edges;
- confidence-qualified indicator;
- final accepted/abstained state;
- accepted-partition correctness as audit-only truth;
- total probe energy and target-block count.

## Preregistered contrasts and criteria

### C1 — moderate-gain efficiency

For all three `g_probe=0.50` A/B-fault magnitudes compare targeted strategy with Experiment-018 full confirmation.

H1 requires at all three magnitudes:

- targeted final coverage `>=0.85`;
- targeted coverage no more than `0.05` absolute below full-confirmation coverage;
- accepted precision `>=0.95`;
- wrong acceptance `<=0.05`;
- targeted-minus-full early-loss bootstrap CI upper endpoint `<=0.02 * mean(full early loss)`;
- adaptation-by-420 no more than `0.10` below `triad_persistence`;
- mean targeted energy `<=0.95`;
- mean targeted energy at least `0.05` below mean full-confirmation energy.

Failure of either coverage noninferiority or energy reduction falsifies the central efficiency claim even if precision remains high.

### C2 — standard-gain preservation

At all three `g_probe=1.00` A/B-fault magnitudes require:

- coverage `>=0.90`;
- accepted precision `>=0.99`;
- wrong acceptance `<=0.01`;
- mean energy `<0.45`;
- adaptation gap versus triad `>=-0.10`.

### C3 — leading-edge selector validity

Among seeds entering targeted confirmation in each A/B-fault gain family, report the audit-only fraction in which the selected leading edge matches the true A/B reciprocal edge.

H3 requires selector correctness `>=0.80` at `g_probe=0.50`. No minimum is assigned at lower gains; those are characterization boundaries.

### C4 — attenuation safety

At all `g_probe=0.375`, `0.25`, and `0.125` A/B-fault cells require:

- wrong acceptance `<=0.05` (`<=0.01` at gain `0.125`);
- targeted-minus-triad early-loss CI upper endpoint `<=0.05 * mean(triad early loss)` (`<=0.02` fraction at gain `0.125`);
- adaptation gap versus triad `>=-0.10`.

At `g_probe=0.125`, abstention must remain `>=0.90`.

### C5 — legitimate-drift non-destruction

For each genuine-drift magnitude, relative excess early-loss CI upper endpoint versus triad must remain `<0.10`, and adaptation gap must be `>=-0.10`.

### C6 — common-mode and primary-fault regression protection

For common-mode corruption, final coefficient-error difference versus the Experiment-018 full-confirmation comparator must have paired-bootstrap CI upper endpoint `<=0.05` at all magnitudes.

For primary-only fault, the same noninferiority criterion applies.

### C7 — coherent-all-auxiliary negative boundary

Report targeted-minus-triad early loss and accepted provenance rate in coherent-all-auxiliary cells. No success claim is assigned. Any apparent provenance confidence is explicitly not evidence of truth identifiability.

## Frozen claim logic

The central Experiment-019 claim is **adaptive confirmation efficiency**: after four rounds fail to qualify, the existing round-4 reciprocal scores contain enough directional information to focus the confirmatory intervention on two targets and preserve most of the Experiment-018 rescue while reducing diagnostic energy.

- H1 is required for the central efficiency claim.
- H2–H6 are required regression/safety protections.
- H3 supplies the mechanistic explanation and must pass at `g_probe=0.50`.
- H7 remains an explicit unsolved boundary.

A precision-only result with materially reduced coverage does not count as success. An energy-only result with materially reduced coverage does not count as success. Thresholds, selector rules, amplitudes, and criteria may not be changed after outcomes are observed.
