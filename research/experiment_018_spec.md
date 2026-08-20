# Experiment 018 — Prospective Confirmatory Replication for Selective Interventional Provenance

**Status:** prospectively frozen before any Experiment 018 outcome generation.

## Scientific boundary

Experiment 017 produced a mixed but informative result. Its selective cumulative provenance rule had zero wrong high-confidence acceptances in the tested seeds and fell back exactly to `triad_persistence` when diagnostic evidence was insufficient. Standard-gain behavior satisfied all frozen criteria, attenuation-risk containment succeeded at gains 0.375 and 0.25, and gain 0.125 produced complete abstention. However, the central Experiment-017 claim was falsified because deployment coverage at `g_probe=0.50` was only `0.595`, below the preregistered `>=0.75` criterion, despite accepted-partition precision `1.000`.

Experiment 017 also failed to show a large cumulative-information gain from merely pooling the original four rounds: final cumulative partition correctness exceeded the single maximum-probe round by only `+0.035` at gain 0.375 and `+0.055` at gain 0.25, below the frozen `+0.10` mechanism threshold.

The next question is therefore not whether to relax the confidence requirement after seeing these outcomes, and not whether to increase intervention amplitude. Experiment 018 tests whether **one additional independent confirmatory replication at the already-tested maximum amplitude can raise moderate-gain selective deployment coverage while preserving precision, low-gain abstention safety, and a bounded diagnostic burden**.

No Experiment 018 outcome may be generated before this specification is committed. After freeze, DGP, intervention chronology, calibration, cumulative statistic, confirmation rule, cells, strategies, seeds, estimands, contrasts, criteria, audit requirements, and claim boundaries below are immutable in response to outcomes.

## Hypotheses

- **H1 — standard-gain preservation:** the replicated selective strategy preserves the high-coverage, high-precision, low-burden standard-gain behavior established in Experiment 017.
- **H2 — moderate-gain coverage rescue:** at `g_probe=0.50`, one additional independent maximum-amplitude confirmation round raises selective deployment coverage to the previously missed 0.75 target without sacrificing accepted-partition precision or operational safety.
- **H3 — rescued-decision validity:** decisions newly accepted only after the confirmatory round remain physically correct at high precision rather than converting uncertainty into false confidence.
- **H4 — attenuation risk containment:** at `g_probe=0.375` and `0.25`, the extra evidence does not create material gating harm or an excessive wrong-acceptance rate.
- **H5 — severe-attenuation abstention:** at `g_probe=0.125`, the strategy still predominantly abstains and remains near fallback behavior.
- **H6 — bounded replication burden:** the moderate-gain coverage test is achieved, if at all, without unbounded diagnostic energy; the single extra round is the only new intervention budget.
- **H7 — legitimate-drift non-destruction:** replicated selective probing does not materially degrade genuine-drift adaptation versus `triad_persistence`.
- **H8 — common-mode input protection:** when provenance is identifiable and auxiliaries are healthy, replicated selective provenance improves final coefficient integrity versus `triad_persistence` under input-family common-mode corruption.
- **H9 — primary-fault regression protection:** replicated selective provenance does not materially worsen final coefficient integrity versus `triad_persistence` under primary-only input fault.
- **H10 — coherent-all-auxiliary boundary preservation:** additional diagnostic replication still cannot turn provenance structure into a truth certificate when all auxiliary evidence is coherently corrupted.

## Inherited plant, sensing, learner, and gate

Inherit the Experiment-017 scalar plant, event time `t=401`, initial learner/refit law, `x_primary`-only learning, input-family channels, A/B/C auxiliary anchor equations, physical/noise streams, persistence chronology, mismatch thresholds, operational losses, A/B-vs-C physical provenance partition, provenance-aware quorum logic, triad fallback, and all legacy strategy semantics unless explicitly changed below.

All diagnostic intervention remains pre-event and diagnostic-only. It may not modify `x_true`, `x_primary`, `x_r1`, `x_r2`, `y`, the plant coefficient, operational A/B/C anchor measurements, or learner/refit data.

## Frozen intervention chronology

Retain the Experiment-017 baseline and first four rounds exactly:

- baseline diagnostic steps `181..200`;
- round 1, amplitude `d1=0.025`: A `201..205`, B `206..210`, C `211..215`;
- round 2, amplitude `d2=0.050`: A `216..220`, B `221..225`, C `226..230`;
- round 3, amplitude `d3=0.100`: A `231..235`, B `236..240`, C `241..245`;
- round 4, amplitude `d4=0.200`: A `246..250`, B `251..255`, C `256..260`.

Add exactly one confirmatory replication round:

- **round 5, amplitude `d5=0.200`: A `261..265`, B `266..270`, C `271..275`.**

Round 5 uses fresh pre-generated diagnostic noise and the same physical diagnostic response law as all prior rounds. No intervention amplitude above `0.200` is permitted.

Diagnostic readout noise remains independent Gaussian with `sigma_probe=0.05` latent-input units. During a target-j block, every auxiliary source in j's physical failure domain receives response `g_probe * d_r`; sources outside that physical domain receive zero response. Gain is never directly supplied to the deployable rule.

## Inherited Experiment-017 thresholds

Reproduce the four Experiment-016 round thresholds from calibration seeds `1800..1999` and the Experiment-017 cumulative thresholds `mu_1..mu_4`, `nu_1..nu_4` from calibration seeds `2000..2999` exactly.

These inherited values are frozen comparators and may not be recomputed from Experiment-018 evaluation data.

## Round-5 cumulative statistic

Retain the Experiment-017 signed cumulative statistic for rounds 1–4. Extend it to round 5 using the frozen amplitude vector

`[0.025, 0.050, 0.100, 0.200, 0.200]`.

For every ordered off-diagonal channel/target pair `(i,j)`, after completed round `r` define

`C_r(i,j) = sum_{k=1..r} d_k * R_k(i,j) / sqrt(sum_{k=1..r} d_k^2)`.

For each unordered pair define

`Q_r(i,j) = min(C_r(i,j), C_r(j,i))`.

The graph and decisiveness semantics remain unchanged: a base reciprocal edge exists iff `Q_r(i,j) > mu_r`; the graph is structurally decisive iff it contains exactly one reciprocal edge producing one two-source component and one singleton; a decisive graph is confidence-qualified iff that single edge additionally satisfies `Q_r(i,j) > nu_r`.

No fitted gain estimate, posterior model, absolute-value conversion, outcome-dependent weighting, threshold relaxation, or alternate clustering is permitted.

## New round-5 null calibration

Use exactly calibration seeds `3000..3999`, disjoint from all inherited calibration ranges and all Experiment-018 evaluation seeds.

For each seed, generate the full five-round diagnostic chronology with physical challenge response set to zero. Compute the round-5 cumulative statistics over exactly the six ordered off-diagonal pairs.

Using the inherited empirical-quantile convention, freeze:

- `mu_5` = empirical 99th percentile of round-5 null cumulative statistics;
- `nu_5` = empirical 99.9th percentile of round-5 null cumulative statistics.

Only `mu_5` and `nu_5` are newly calibrated. Rounds 1–4 retain the already-frozen Experiment-017 cumulative thresholds exactly.

Evaluation seeds may not contribute to any calibration.

## Frozen replicated selective rule

The new deployable strategy is `replicated_selective_cumulative_provenance_quorum`.

1. Execute the Experiment-017 selective cumulative rule through round 4 exactly.
2. If any round 1–4 is confidence-qualified, accept immediately and stop exactly as Experiment 017 did; round 5 is not observed.
3. If no round 1–4 qualifies, execute all three round-5 target blocks at amplitude 0.20.
4. Compute `C_5`, `Q_5`, the base reciprocal graph, structural decisiveness, and confidence qualification using frozen `mu_5` and `nu_5`.
5. If round 5 is confidence-qualified, accept that partition.
6. Otherwise abstain from provenance deployment and use exact inherited `triad_persistence` post-event behavior.

No unqualified round-4 or round-5 partition may influence gating after abstention. Oracle labels may not influence inference, stopping, or fallback.

## Diagnostic burden

Retain the energy definition

`E_probe = sum_{executed target blocks} 5 * d(block)^2`.

The original four-round ladder has energy `0.796875`.

The confirmatory round adds exactly `3 * 5 * 0.2^2 = 0.600000` energy when executed.

Therefore the maximum Experiment-018 replicated-selective energy is exactly `1.396875`. No strategy may execute further replication or stronger intervention.

## Frozen cells

Evaluate exactly the same 28 physical cells as Experiment 017:

1. healthy, magnitude 0.00, `g_probe=1.00`;
2–4. genuine physical drift, magnitudes 0.25, 0.50, 1.00, `g_probe=1.00`;
5–7. input-family common-mode corruption, magnitudes 0.25, 0.50, 1.00, `g_probe=1.00`;
8–10. primary-only input fault, magnitudes 0.25, 0.50, 1.00, `g_probe=1.00`;
11–13. physical drift + coherent A/B common-cause auxiliary fault, magnitudes 0.25, 0.50, 1.00, `g_probe=1.00`;
14–16. same A/B common-fault cells with `g_probe=0.50`;
17–19. same A/B common-fault cells with `g_probe=0.375`;
20–22. same A/B common-fault cells with `g_probe=0.25`;
23–25. same A/B common-fault cells with `g_probe=0.125`;
26–28. physical drift + coherent all-auxiliary fault, magnitudes 0.25, 0.50, 1.00, `g_probe=1.00`.

No cell may be added, removed, reweighted, or relabeled after outcomes are observed.

## Frozen strategies

Evaluate exactly fourteen strategies on matched operational stochastic streams:

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
14. `replicated_selective_cumulative_provenance_quorum`.

The first thirteen strategies retain their Experiment-017 meanings exactly and do not gain access to round-5 information. Only the new strategy may use round 5.

## Seeds and bootstrap

- Inherited probe calibration: exactly `1800..1999`.
- Inherited Experiment-017 cumulative calibration: exactly `2000..2999`.
- New round-5 null calibration: exactly `3000..3999`.
- Evaluation seeds: exactly `18000..18199`, inclusive, 200 per cell.
- Bootstrap: exactly 10,000 paired resamples with RNG seed `18018`.
- Audit seeds: exactly `18000..18004`.
- All calibration and evaluation ranges remain disjoint.

## Primary estimands

Report all inherited Experiment-017 operational, latent, coefficient, adaptation, vote, veto, provenance, stopping, precision, coverage, and burden estimands.

For the replicated strategy additionally record:

- whether round 5 was executed;
- round-5 signed 3x3 response matrix;
- six round-5 cumulative `C_5(i,j)` values;
- `Q_5` for AB, AC, BC;
- `mu_5` and `nu_5`;
- round-5 base reciprocal edges;
- round-5 structural-decisiveness and confidence-qualified indicators;
- round-5 inferred partition;
- final accepted/abstained status;
- whether acceptance was newly rescued by round 5;
- physical correctness of newly rescued acceptance as audit-only truth information;
- total energy and target-block count.

Define:

- **round-4 coverage** = coverage the unchanged Experiment-017 selective rule would have achieved before round 5;
- **final replicated coverage** = coverage after the possible round-5 confirmation;
- **absolute coverage gain** = final replicated coverage minus round-4 coverage;
- **rescue fraction among round-4 abstainers** = newly accepted round-5 seeds divided by round-4 abstaining seeds;
- **rescued-decision precision** = physically correct newly accepted round-5 seeds divided by all newly accepted round-5 seeds.

If there are zero newly rescued seeds, rescued-decision precision is undefined rather than set to 1.0.

## Preregistered contrasts and criteria

All loss/error contrasts are paired by evaluation seed.

### C1 — standard-gain preservation

For each `g_probe=1.00` A/B-fault magnitude report replicated-selective coverage, accepted precision, wrong acceptance, selective-minus-naive early loss, adaptation gap, and energy.

H1 requires at all three magnitudes:

- coverage `>=0.90`;
- accepted-partition precision `>=0.99`;
- wrong-acceptance rate `<=0.01`;
- selective-minus-naive early-loss CI upper endpoint `<0`;
- mean energy `<0.45`;
- adaptation-by-420 no more than 0.10 below `triad_persistence`.

### C2 — moderate-gain coverage rescue

For each `g_probe=0.50` A/B-fault magnitude report round-4 coverage, final replicated coverage, absolute coverage gain, replicated-minus-original-selective early loss, accepted precision, wrong acceptance, adaptation gap, and energy.

H2 requires at all three magnitudes:

- final replicated coverage `>=0.75`;
- absolute coverage gain `>=0.15`;
- accepted-partition precision `>=0.95`;
- wrong-acceptance rate `<=0.05`;
- replicated-minus-original-selective early-loss CI upper endpoint `<=0.02 * mean(original selective early loss)`;
- adaptation-by-420 no more than 0.10 below `triad_persistence`.

### C3 — rescued-decision validity

For each `g_probe=0.50` magnitude report the rescue fraction among round-4 abstainers and rescued-decision precision.

H3 requires at all three magnitudes:

- rescue fraction among round-4 abstainers `>=0.35`;
- rescued-decision precision `>=0.95`;
- no more than 0.02 absolute increase in overall wrong-acceptance rate versus the original Experiment-017 selective comparator.

### C4 — attenuation risk containment

For each `g_probe=0.375` and `0.25` A/B-fault magnitude report coverage, coverage gain, accepted precision, wrong acceptance, replicated-minus-triad early loss, replicated-minus-original-selective early loss, adaptation gap, and energy.

H4 requires at all six cells:

- wrong-acceptance rate `<=0.05`;
- replicated-minus-triad early-loss CI upper endpoint `<=0.05 * mean(triad early loss)`;
- adaptation-by-420 no more than 0.10 below `triad_persistence`.

No minimum deployment coverage is assigned at these attenuated gains.

### C5 — severe-attenuation abstention

For each `g_probe=0.125` A/B-fault magnitude report final coverage, abstention, wrong acceptance, replicated-minus-triad early loss, and energy.

H5 requires at all three magnitudes:

- abstention rate `>=0.90`;
- wrong-acceptance rate `<=0.01`;
- replicated-minus-triad early-loss CI upper endpoint `<=0.02 * mean(triad early loss)`.

### C6 — bounded replication burden

At each `g_probe=0.50` A/B-fault magnitude report mean replicated-selective energy, mean original-selective energy, round-5 execution rate, and energy difference.

H6 requires mean replicated-selective energy `<=1.10` at all three magnitudes. This is a burden criterion, not a plant-loss penalty.

### C7 — legitimate-drift non-destruction

For each genuine-drift magnitude compute relative excess early loss

`R = (L_replicated - L_triad) / max(abs(L_triad),1e-12)`.

H7 requires CI upper endpoint of mean `R <0.10` and adaptation-by-420 no more than 0.10 below triad at all magnitudes.

### C8 — common-mode coefficient integrity

For each common-mode magnitude compute final absolute slope-error difference `replicated - triad`.

H8 is supported at a magnitude iff the CI upper endpoint is `<0`.

### C9 — primary-fault regression

For each primary-fault magnitude compute final absolute slope-error difference `replicated - triad`.

H9 requires CI upper endpoint `<=0.01` at all three magnitudes.

### C10 — coherent-all-auxiliary boundary

For each all-auxiliary-fault magnitude report replicated-minus-triad early loss, coverage, accepted precision, wrong acceptance, adaptation gap, round-5 execution, and energy.

No success threshold is assigned. Additional replication may not be interpreted as truth identification when every auxiliary source shares coherent corruption.

## Falsification logic

The central confirmatory-replication claim is falsified if H1, H2, H3, H4, H5, H6, or H7 fails its frozen criteria.

H8 alone cannot rescue central failure. H9 failure establishes regression on an already-solved condition. H10 is a deliberate negative boundary and may not be retuned away.

If round 5 increases coverage by accepting incorrect partitions, that is a scientific failure rather than evidence that the confidence threshold should be relaxed or recalibrated post hoc.

If round 5 preserves precision but does not reach the moderate-gain coverage target, the conclusion is that one independent replication at the same amplitude is insufficient under the tested signal/noise regime.

## Audit requirements

The evidence artifact must permit independent verification of:

- exact `28 x 14 x 200 = 78,400` seed-strategy summaries;
- evaluation seeds exactly `18000..18199` in every cell;
- inherited calibration ranges `1800..1999` and `2000..2999` reproduced exactly;
- new round-5 null calibration seeds exactly `3000..3999`;
- exact five-round chronology and maximum amplitude `0.200`;
- fresh pre-generated round-5 noise and matched operational streams;
- exact inherited thresholds plus frozen `mu_5` and `nu_5`;
- exact cumulative-statistic extension through round 5;
- exact no-future-round access for strategies stopping before round 5;
- exact abstention fallback equivalence to `triad_persistence`;
- exact maximum energy `1.396875` and round-5 incremental energy `0.600000`;
- oracle isolation;
- `x_primary`-only learner/refit use;
- exact 10,000-resample bootstrap with seed `18018`;
- deterministic equivalence of sharded and monolithic report formulas.

Record full time-step audit traces for seeds `18000..18004` for all cells and strategies. Expected audit rows: `28 x 14 x 5 x 900 = 1,764,000`.

## Execution safeguards

All execution must comply with `research/execution_contract.md`. Full unit tests and an all-strategy non-evaluation-seed smoke through the real summary path must pass before any request marker is committed.

The request marker must be committed last. Completion registration must remain bounded and point to the evidence artifact rather than embedding the full report.

Execution defects may be repaired after freeze only to restore this frozen contract without changing scientific hypotheses, thresholds, cells, strategies, seeds, estimands, criteria, or claim boundaries.

## Claim boundary

A positive Experiment 018 may support only this bounded statement: **under the specified diagnostic-access, noise, gain, and failure-domain model, one additional independent confirmation round at the already-tested maximum intervention amplitude can increase moderate-gain selective provenance coverage while preserving prospectively calibrated precision, conservative fallback, and a finite diagnostic burden.**

It may not establish optimal replication count, optimal intervention design, arbitrary intervention safety, universal causal discovery, calibration outside the tested DGP, truth identification under coherent all-auxiliary corruption, or robustness to untested gains/noise levels.