# Experiment 017 — Prospective Selective Cumulative Interventional Provenance

**Status:** prospectively frozen before any Experiment 017 outcome generation.

## Scientific boundary

Experiment 016 established a bounded positive result and a bounded failure mode. Under the frozen diagnostic-access model, sequential intervention retained oracle-equivalent behavior in the fully responsive A/B-fault regime while reducing diagnostic energy, but recovery degraded under response attenuation: approximately 86% partition recovery at `g_probe=0.50`, approximately 13% at `g_probe=0.25`, and exhaustion of the finite ladder at low gain. Coherent corruption of all auxiliary evidence remained unresolved.

The remaining question is not whether more intervention can always recover truth. It is whether a deployable gate can use **cumulative evidence from an already-bounded intervention ladder, qualify its own provenance decision, and abstain to a conservative inherited fallback when the diagnostic evidence is insufficient**.

Experiment 017 therefore tests selective deployment under identifiability uncertainty. It does not add intervention amplitude beyond Experiment 016, does not use post-event data for provenance inference, and does not attempt to solve the coherent-all-auxiliary truth-identification boundary.

No Experiment 017 outcome may be generated before this specification is committed. After freeze, DGP, probe ladder, calibration, cumulative statistic, stopping rule, abstention rule, cells, strategies, seeds, estimands, contrasts, criteria, audit requirements, and claim boundaries below are immutable in response to outcomes.

## Hypotheses

- **H1 — standard-gain selective recovery:** at `g_probe=1.00`, cumulative selective provenance accepts high-confidence A/B-vs-C structure frequently enough to preserve the operational advantage of provenance-aware gating while retaining the intervention-efficiency benefit established in Experiment 016.
- **H2 — moderate-gain selective robustness:** at `g_probe=0.50`, cumulative evidence plus abstention preserves useful deployment coverage with high accepted-partition precision and is not materially worse than the Experiment-016 sequential strategy.
- **H3 — attenuation risk containment:** at `g_probe=0.375` and `0.25`, selective abstention prevents the low-identifiability regime from turning into material gating harm relative to the inherited `triad_persistence` fallback.
- **H4 — severe-attenuation abstention:** at `g_probe=0.125`, the strategy mostly abstains and numerically approaches fallback behavior rather than forcing a provenance decision.
- **H5 — cumulative-information gain:** pooling all executed rounds can recover more provenance information at the final round than the single-round maximum-probe rule under at least part of the attenuated-gain regime.
- **H6 — legitimate-drift non-destruction:** selective cumulative probing does not materially degrade genuine-drift adaptation versus `triad_persistence`.
- **H7 — common-mode input protection:** when provenance is identifiable and auxiliaries are healthy, selective cumulative provenance improves final coefficient integrity versus `triad_persistence` under input-family common-mode corruption.
- **H8 — primary-fault regression protection:** selective cumulative provenance does not materially worsen final coefficient integrity versus `triad_persistence` under primary-only input fault.
- **H9 — coherent-all-auxiliary boundary preservation:** high-confidence provenance structure still does not establish truth when all auxiliary evidence is corrupted coherently.

## Inherited plant, sensing, learner, and operational gate

Inherit the Experiment-016 scalar plant, event time `t=401`, initial learner/refit law, `x_primary`-only learning, input-family channels, A/B/C auxiliary anchor equations, physical/noise streams, persistence chronology, mismatch thresholds, losses, A/B-vs-C physical provenance partition, operational provenance-aware quorum logic, and all legacy strategy semantics unless explicitly changed below.

All probe activity remains diagnostic-only and pre-event. It may not modify `x_true`, `x_primary`, `x_r1`, `x_r2`, `y`, the plant coefficient, operational A/B/C anchor measurements, or learner/refit data.

## Frozen intervention ladder

Use the Experiment-016 diagnostic chronology exactly:

- baseline diagnostic steps `181..200`;
- round 1, amplitude `d1=0.025`: A `201..205`, B `206..210`, C `211..215`;
- round 2, amplitude `d2=0.050`: A `216..220`, B `221..225`, C `226..230`;
- round 3, amplitude `d3=0.100`: A `231..235`, B `236..240`, C `241..245`;
- round 4, amplitude `d4=0.200`: A `246..250`, B `251..255`, C `256..260`.

Diagnostic readout noise remains independent Gaussian with `sigma_probe=0.05` latent-input units and is pre-generated before strategy execution.

During a target-j block, every auxiliary source in j's physical failure domain receives response `g_probe * d_r`; sources outside the target's physical domain receive zero response. Gain is part of the physical diagnostic pathway and is never supplied directly to a deployable inference rule.

## Inherited Experiment-016 round thresholds

Reproduce the four Experiment-016 round-specific `lambda_probe_1..lambda_probe_4` values exactly from the frozen null-calibration procedure and seeds `1800..1999`. They remain the thresholds used by the inherited `max_probe_provenance_quorum` and `sequential_provenance_quorum` comparators.

Evaluation seeds may not contribute to threshold reproduction.

## New cumulative evidence statistic

For each completed round `r`, compute the signed block-mean-minus-baseline response matrix `R_k(i,j)` for every executed round `k <= r`, using the same baseline mean over steps `181..200` as Experiment 016.

For every ordered off-diagonal channel/target pair `(i,j)`, define the cumulative intervention statistic

`C_r(i,j) = sum_{k=1..r} d_k * R_k(i,j) / sqrt(sum_{k=1..r} d_k^2)`.

Only the six ordered off-diagonal pairs are used for edge inference. Diagonal responses are retained for audit but do not create graph edges.

The statistic is one-sided because the physical diagnostic challenge direction is frozen positive. No absolute-value transformation, fitted gain estimate, posterior model, amplitude retuning, or outcome-dependent weighting is permitted.

## New cumulative null calibration

Use exactly null-calibration seeds `2000..2999`, disjoint from all inherited calibration seeds and all evaluation seeds.

For each calibration seed, generate the full Experiment-017 diagnostic noise chronology with physical challenge response fixed to zero. For each round `r`, collect `C_r(i,j)` over exactly the six ordered off-diagonal pairs.

Using the inherited empirical-quantile convention, set:

- `mu_r` = empirical 99th percentile of the round-r null cumulative statistics;
- `nu_r` = empirical 99.9th percentile of the round-r null cumulative statistics.

All eight new thresholds `mu_1..mu_4` and `nu_1..nu_4` are frozen before evaluation. Evaluation outcomes may not alter them.

## Frozen cumulative graph rule

At completed round `r`, define the three undirected candidate pair scores

`Q_r(i,j) = min(C_r(i,j), C_r(j,i))` for pairs AB, AC, and BC.

Place a **base reciprocal edge** `(i,j)` iff `Q_r(i,j) > mu_r`.

The round-r cumulative graph is **structurally decisive** iff it contains exactly one base reciprocal edge, producing exactly one two-source component and one singleton component.

A structurally decisive graph is **confidence-qualified** iff its single reciprocal edge additionally satisfies `Q_r(i,j) > nu_r`.

All comparisons are strict `>` comparisons.

## Frozen selective stopping and abstention rule

The new deployable `selective_cumulative_provenance_quorum` executes rounds in order.

After each completed round:

1. compute all cumulative statistics using only rounds executed so far;
2. infer the cumulative base graph;
3. if the graph is structurally decisive and confidence-qualified, accept its partition and stop immediately;
4. otherwise continue to the next round if one remains;
5. after round 4, if no round has been confidence-qualified, **abstain from provenance deployment**.

After an accepted stop, no later-round diagnostic observation may be consulted. All noise streams remain pre-generated only for matched reproducibility.

When the strategy abstains, its post-event operational behavior is exactly the inherited `triad_persistence` strategy. It may not use the unqualified cumulative partition, the Experiment-016 round partition, or oracle labels for gating.

The strategy must record whether it accepted or abstained, the accepted round if any, the candidate round-4 partition if no acceptance occurred, and all cumulative statistics from executed rounds.

## Forced cumulative comparator

Add `cumulative_provenance_quorum` as a mechanistic comparator.

It always executes all four rounds, computes the round-4 cumulative base graph using `mu_4`, converts connected components directly into provenance groups, and deploys those groups without the `nu_4` confidence requirement or abstention.

This comparator exists only to separate **cumulative information pooling** from **selective abstention**. It is not the preferred deployable strategy and may fail under weak identifiability.

## Probe burden

Retain the Experiment-016 frozen diagnostic-energy definition:

`E_probe = sum_{executed target blocks} 5 * d(block)^2`.

Also report executed target-block count, stopping round, and maximum amplitude reached.

Selective probing executes every round through and including its accepted stopping round; if it abstains, it executes all four rounds. `cumulative_provenance_quorum` always executes all four rounds. `max_probe_provenance_quorum` executes only round 4. Legacy/oracle/no-probe strategies have zero probe energy.

The full four-round ladder has frozen energy `0.796875`; the fixed round-4 maximum comparator has frozen energy `0.600000`.

## Frozen cells

Evaluate exactly 28 cells:

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

Evaluate exactly thirteen strategies on matched operational stochastic streams:

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
13. `selective_cumulative_provenance_quorum`.

Legacy meanings remain frozen. Oracle labels may not influence either new deployable cumulative strategy.

## Seeds and bootstrap

- Preserve all inherited non-probe thresholds by exact reproduction.
- Reproduce Experiment-016 round thresholds from calibration seeds exactly `1800..1999`.
- New cumulative null-calibration seeds: exactly `2000..2999`.
- Evaluation seeds: exactly `17000..17199`, inclusive, 200 per cell.
- Bootstrap: exactly 10,000 paired resamples with RNG seed `17017`.
- Audit seeds: exactly `17000..17004`.
- All calibration and evaluation seed sets must remain disjoint.

## Primary estimands

For every cell/strategy report at minimum all inherited operational, latent, coefficient, adaptation, vote, veto, and loss estimands plus, where applicable:

- round-specific signed 3x3 response matrices;
- cumulative `C_r(i,j)` values for all six ordered off-diagonal pairs;
- `Q_r` values for AB, AC, and BC;
- `mu_r` and `nu_r` thresholds;
- base reciprocal edges;
- structural-decisiveness indicator;
- confidence-qualified indicator;
- inferred partition at every executed round;
- accepted partition, if any;
- accepted stopping round, if any;
- abstention indicator;
- candidate round-4 partition on abstention;
- physically correct partition-match indicator as audit-only information;
- maximum amplitude reached;
- executed target-block count;
- `E_probe`.

For selective strategies additionally report:

- **deployment coverage** = fraction of seeds with accepted provenance;
- **abstention rate** = `1 - deployment coverage`;
- **accepted-partition precision** = fraction of accepted seeds with physically correct partition;
- **wrong-acceptance rate** = fraction of all seeds that accept an incorrect partition.

If a cell has zero accepted seeds, accepted-partition precision is reported as undefined and is not silently converted to 1.0.

## Preregistered contrasts and criteria

All contrasts are paired by evaluation seed unless a rate is explicitly defined over seeds.

### C1 — standard-gain selective recovery

For each `g_probe=1.00` A/B-fault magnitude, report selective-minus-naive early loss, deployment coverage, accepted-partition precision, wrong-acceptance rate, stopping-round distribution, and probe energy.

H1 requires at all three magnitudes:

- early-loss CI upper endpoint for `selective - naive < 0`;
- deployment coverage `>=0.90`;
- accepted-partition precision `>=0.99`;
- wrong-acceptance rate `<=0.01`;
- mean selective probe energy `<0.75 * 0.600000`;
- adaptation-by-420 no more than 0.10 below `triad_persistence`.

### C2 — moderate-gain selective robustness

For each `g_probe=0.50` A/B-fault magnitude, report selective-minus-Experiment-016-sequential early loss, deployment coverage, accepted-partition precision, wrong-acceptance rate, stopping distribution, and energy.

H2 requires at all three magnitudes:

- deployment coverage `>=0.75`;
- accepted-partition precision `>=0.95`;
- wrong-acceptance rate `<=0.05`;
- CI upper endpoint of `selective - sequential` early loss `<=0.02 * mean(sequential early loss)`;
- adaptation-by-420 no more than 0.10 below `triad_persistence`.

### C3 — attenuation risk containment

For each `g_probe=0.375` and `0.25` A/B-fault magnitude, report selective-minus-triad early loss, selective-minus-sequential early loss, deployment coverage, abstention rate, accepted-partition precision, wrong-acceptance rate, final slope error, veto burden, stopping distribution, and energy.

H3 requires at all six cells:

- CI upper endpoint of `selective - triad` early loss `<=0.05 * mean(triad early loss)`;
- wrong-acceptance rate `<=0.05`;
- adaptation-by-420 no more than 0.10 below `triad_persistence`.

No minimum deployment coverage is assigned in these boundary cells; abstention is a valid safety response.

### C4 — severe-attenuation abstention

For each `g_probe=0.125` A/B-fault magnitude, report the same selective diagnostics as C3.

H4 requires at all three magnitudes:

- abstention rate `>=0.90`;
- wrong-acceptance rate `<=0.01`;
- CI upper endpoint of `selective - triad` early loss `<=0.02 * mean(triad early loss)`.

This criterion tests graceful fallback, not successful provenance recovery.

### C5 — cumulative-information gain

For each `g_probe=0.375` and `0.25` A/B-fault magnitude, compare final round-4 partition correctness for `cumulative_provenance_quorum` versus `max_probe_provenance_quorum`.

H5 is supported at a gain/magnitude cell iff cumulative partition correctness exceeds max-probe partition correctness by at least 0.10 absolute. Report all six cells independently; H5 is an information-pooling mechanism test and is not required to rescue the central selective-safety claim.

### C6 — legitimate-drift non-destruction

For each genuine-drift magnitude compute relative excess early loss

`R = (L_selective - L_triad) / max(abs(L_triad), 1e-12)`.

H6 requires CI upper endpoint of mean `R < 0.10` and adaptation-by-420 no more than 0.10 below triad at all three magnitudes.

### C7 — common-mode coefficient integrity

For each common-mode magnitude compute final absolute slope-error difference `selective - triad`.

H7 is supported at a magnitude iff the CI upper endpoint is `<0`.

### C8 — primary-fault regression

For each primary-fault magnitude compute final absolute slope-error difference `selective - triad`.

H8 requires CI upper endpoint `<=0.01` at all three magnitudes.

### C9 — coherent-all-auxiliary boundary

For each all-auxiliary-fault magnitude report selective-minus-triad early loss, deployment coverage, accepted-partition precision, wrong-acceptance rate, adaptation gap, veto burden, stopping round, and probe energy.

No success threshold is assigned. A confidence-qualified provenance partition must not be interpreted as a truth certificate when every auxiliary source is coherently corrupted.

## Falsification logic

The central selective-identifiability claim is falsified if H1, H2, H3, H4, or H6 fails its frozen criteria.

H5 tests whether cumulative pooling itself adds identifiable structure and may fail without invalidating a pure abstention-safety result. H7 alone cannot rescue failure of the central selective criteria. H8 failure establishes regression on an already-solved primary-fault condition. H9 is a deliberate negative boundary and may not be retuned away.

A low deployment-coverage result is not automatically a defect when the specification assigns no minimum coverage. A wrong high-confidence acceptance is more serious than an abstention and must remain visible in the evidence.

## Audit requirements

The evidence artifact must permit independent verification of:

- exact `28 x 13 x 200 = 72,800` seed-strategy summaries;
- evaluation seeds exactly `17000..17199` in every cell;
- inherited probe-calibration seeds exactly `1800..1999` and new cumulative calibration seeds exactly `2000..2999`, all disjoint from evaluation;
- exact baseline and four-round challenge chronology;
- exact amplitudes `[0.025,0.050,0.100,0.200]`, `sigma_probe=0.05`, and gain constructions;
- pre-generation and matched operational streams;
- exact Experiment-016 round thresholds and exact new `mu_r`/`nu_r` thresholds;
- exact signed cumulative-statistic formula;
- exact reciprocal-edge, decisiveness, confidence, stopping, and abstention chronology;
- absence of future-round access after accepted stopping;
- exact fallback equivalence to `triad_persistence` on abstained seeds;
- exact probe-energy calculation;
- oracle isolation;
- `x_primary`-only learner/refit use;
- inherited mismatch/disagreement/vote/veto chronology and all losses/contrasts;
- exact 10,000-resample bootstrap with seed `17017`;
- deterministic equivalence of sharded and monolithic report formulas.

Record full time-step audit traces for seeds `17000..17004` for all cells and strategies. Expected audit rows: `28 x 13 x 5 x 900 = 1,638,000`.

## Execution safeguards

All execution must comply with `research/execution_contract.md`, including inherited-comparator compatibility, RNG-safe aliases, full unit tests, comparator-semantics checks, a non-evaluation-seed all-strategy smoke through the real summary path, exact schema/coverage assertions, and request marker committed last.

Execution defects may be repaired after freeze only to restore this frozen contract without altering the science above.

In addition, the Experiment-016 registration failure is now a frozen infrastructure lesson:

- requested workflows must keep GitHub Issue bodies bounded and must never embed the full report in an Issue body;
- completion registration must contain only concise provenance, status, key bounded findings, and artifact identifiers/digests;
- the full report remains in the uploaded evidence artifact;
- a registration-only failure after successful scientific merge/upload must be recoverable without rerunning evaluation.

## Claim boundary

A positive Experiment 017 may support only this bounded statement: **under the specified diagnostic-access, noise, gain, and failure-domain model, cumulative intervention evidence with a prospectively calibrated confidence requirement can support selective provenance deployment, including conservative abstention when the finite diagnostic ladder does not provide sufficient evidence.**

It may not establish universal causal discovery, optimal experiment design, arbitrary intervention safety, calibrated confidence outside the tested DGP, truth identification under coherent compromise of all auxiliary evidence, or robustness below/above untested gain and noise regimes.
