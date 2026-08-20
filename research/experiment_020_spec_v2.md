# Experiment 020 — Corrected Prospective Early Edge-Targeted Confirmation

**Status:** prospectively frozen before any Experiment 020 calibration or evaluation outcome generation. This specification supersedes the pre-outcome draft at commit `2ac9ce07e35fd4d77a5029ccf80b0a5aa9c77916` for the reason documented in `research/experiment_020_revision_note.md`.

## Scientific question

Experiment 019 showed that after four full diagnostic rounds, targeting the leading reciprocal edge for confirmation yields `0.995` coverage, `1.000` precision, and mean energy `0.923875` at `g_probe=0.50`. Experiment 020 asks whether useful targeting can begin one round earlier, after round 3, to reduce mean diagnostic burden while preserving the validated Experiment-019 comparator as a separate benchmark.

## Inherited system

Inherit Experiment 019's plant, learner, operational gate, physical A/B-vs-C provenance structure, stochastic laws, rounds 1–3, legacy strategies, cells, event timing, and operational metrics exactly.

Rounds 1–3 remain:

- `0.025`: A `201..205`, B `206..210`, C `211..215`;
- `0.050`: A `216..220`, B `221..225`, C `226..230`;
- `0.100`: A `231..235`, B `236..240`, C `241..245`.

## Round-3 selector

Using the inherited cumulative round-3 reciprocal scores `Q3(AB)`, `Q3(AC)`, and `Q3(BC)`, select the unique maximum. Exact ties select no pair.

The selector may use only pre-event diagnostic information. It may not use family labels, gain labels, oracle truth, evaluation outcomes, or post-event operational information.

## Early targeted round 4

If a unique pair is selected, execute exactly two five-step amplitude-`0.200` blocks:

- AB: A `246..250`, B `251..255`;
- AC: A `246..250`, C `251..255`;
- BC: B `246..250`, C `251..255`.

The early decision occurs after step `255`. Total energy through that point is exactly `0.596875`.

For the selected pair, extend its cumulative reciprocal statistic through the new round-4 observations. Nonselected pair scores remain at round-3 values.

## Early calibration

Use null seeds exactly `5000..5999`, disjoint from all inherited calibration and evaluation seeds.

For each null seed with a unique round-3 leader, execute the corresponding two targeted round-4 blocks and collect the updated selected-edge reciprocal statistic.

Freeze:

- `mu4E`: empirical 99th percentile;
- `nu4E`: empirical 99.9th percentile.

Early deployment is allowed only if exactly one reciprocal edge remains and the selected edge exceeds `nu4E`.

## Continuation when early targeting does not qualify

If the early decision does not qualify, execute the omitted third target as a fresh five-step amplitude-`0.200` block at `256..260`.

The resulting three-target round-4 data are **not claimed to be numerically identical to Experiment 019**, because target timing/noise assignments can differ. Instead, compute a completed-round-4 cumulative graph from the actually observed three target responses and apply the inherited Experiment-019 structural and confidence logic with the same frozen `mu4` and `nu4` thresholds.

If that completed round 4 still does not qualify, apply the frozen Experiment-019 leading-edge selector to this completed-round-4 graph and execute its two-target round-5 confirmation at `261..270`, using the inherited targeted thresholds `mu5T` and `nu5T`. If qualification still fails, abstain to exact inherited `triad_persistence` behavior.

Thus the corrected strategy changes only diagnostic scheduling; it does not relax thresholds, increase amplitude, add a sixth round, or alter the operational fallback.

If the round-3 selector ties, execute the standard three-target round 4 and then continue under the same completed-round-4 / inherited targeted-round-5 logic.

## Frozen cells and strategies

Evaluate the same 28 cells as Experiments 017–019.

Evaluate the fifteen Experiment-019 strategies unchanged plus one new strategy:

`early_targeted_replicated_selective_cumulative_provenance_quorum`.

Experiment 019's `targeted_replicated_selective_cumulative_provenance_quorum` is the primary efficiency comparator.

## Seeds

- inherited probe calibration: `1800..1999`;
- inherited cumulative calibration: `2000..2999`;
- inherited full round-5 calibration: `3000..3999`;
- inherited targeted round-5 calibration: `4000..4999`;
- new early-target calibration: `5000..5999`;
- evaluation seeds: exactly `20000..20199`;
- audit seeds: `20000..20004`;
- bootstrap seed: `20020`;
- bootstrap resamples: `10000`.

## Hypotheses and criteria

### H1 — moderate-gain early-target efficiency

At all three `g_probe=0.50` A/B-fault magnitudes, compared with Experiment 019:

- final coverage `>=0.95`;
- coverage gap `>=-0.03`;
- accepted precision `>=0.99`;
- wrong acceptance `<=0.01`;
- adaptation-by-420 gap `>=-0.05`;
- early-loss paired-bootstrap CI upper endpoint `<=0.02 * mean(Experiment019 early loss)`;
- mean diagnostic energy `<=0.75`;
- mean energy reduction `>=0.12`.

Coverage noninferiority and energy reduction are both required for the central claim.

### H2 — round-3 selector validity

Among `g_probe=0.50` A/B-fault seeds entering early targeting, selector correctness must be `>=0.90`.

### H3 — standard-gain preservation

At all `g_probe=1.00` A/B-fault magnitudes:

- coverage `>=0.99`;
- precision `>=0.99`;
- wrong acceptance `<=0.01`;
- mean energy `<=0.60`;
- adaptation gap versus Experiment 019 `>=-0.05`.

### H4 — attenuation safety

At gains `0.375`, `0.25`, and `0.125`:

- wrong acceptance `<=0.05` (`<=0.01` at `0.125`);
- targeted-minus-triad early-loss CI upper endpoint `<=0.05 * mean(triad loss)` (`<=0.02` fraction at `0.125`);
- adaptation gap versus triad `>=-0.10`;
- at `0.125`, abstention `>=0.90`.

### H5 — inherited regression protection

For genuine drift, relative excess early-loss CI upper endpoint versus Experiment 019 must remain `<0.05` and adaptation gap `>=-0.05`.

For common-mode and primary-only faults, final coefficient-error difference versus Experiment 019 must have paired-bootstrap CI upper endpoint `<=0.05` at all magnitudes.

### H6 — continuation-path audit

Report, without using it for tuning:

- early qualification rate;
- omitted-third-block execution rate;
- later targeted-round-5 execution rate;
- total block-count distribution;
- mean energy by family/gain;
- final decision agreement with Experiment 019.

No exact numerical equality to Experiment 019 is required because the corrected continuation schedule uses fresh time-indexed diagnostic noise.

### H7 — coherent-all-auxiliary boundary

Report accepted provenance rate and early loss versus triad in coherent-all-auxiliary cells. No truth-identifiability success claim is assigned.

## Claim logic

The central claim is narrower than the original draft: **round-3 evidence can support an energy-saving early targeting layer while preserving final decision quality relative to Experiment 019.** H1 is required for the central claim; H2–H5 are required mechanistic/safety protections. H6 is characterization. H7 remains explicitly unsolved.

No thresholds, amplitudes, selector rules, schedules, cells, seeds, or criteria may be modified after Experiment-020 calibration or evaluation outcomes are observed.
