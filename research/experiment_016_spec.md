# Experiment 016 — Prospective Budgeted Sequential Interventional Provenance Identification

**Status:** prospectively frozen before any Experiment 016 outcome generation.

## Scientific boundary

Experiment 015 established a bounded positive result: under the frozen diagnostic-access model, a fixed `delta_probe=0.20` challenge recovered the A/B-vs-C failure partition perfectly in the standard cells and made the deployable interventional provenance gate numerically match the oracle comparator on the preregistered A/B-fault early-loss contrast. It also established a sharp negative boundary: the fixed weak probe `delta_probe=0.025` recovered the partition in only 1.5% of seeds.

The remaining question is therefore not whether active information can help, but whether the required information can be acquired **adaptively under a bounded diagnostic-intervention budget when response strength is not assumed known in advance**. Experiment 016 freezes one sequential escalation rule and tests whether it can spend less probe energy in easy/high-response cases, escalate when necessary, preserve legitimate adaptation, and expose rather than hide low-gain identifiability failure.

No Experiment 016 outcome may be generated before this specification is committed. After freeze, DGP, probe ladder, stopping rule, cells, strategies, seeds, calibration, estimands, contrasts, criteria, audit requirements, and claim boundaries below are immutable in response to outcomes.

## Hypotheses

- **H1 — budgeted standard-gain recovery:** with standard domain response gain, sequential probing recovers the A/B-vs-C partition sufficiently well to outperform naive raw-sensor quorum under A/B common-cause auxiliary fault.
- **H2 — intervention-efficiency gain:** under standard gain, sequential probing uses materially less diagnostic energy than an always-maximal fixed-probe comparator while preserving oracle-level early-loss performance.
- **H3 — moderate-gain escalation:** when diagnostic response gain is reduced to 0.50, sequential probing escalates probe strength and retains useful partition recovery without material early-loss disadvantage versus the always-maximal comparator.
- **H4 — low-gain boundary:** when diagnostic response gain is 0.25, the bounded ladder may be insufficient; partition failure and associated gating degradation are preserved negative findings.
- **H5 — legitimate-drift non-destruction:** sequential diagnostic probing does not materially degrade genuine-drift adaptation versus `triad_persistence`.
- **H6 — common-mode input protection:** with identifiable provenance and healthy auxiliaries, sequential interventional provenance improves final coefficient integrity versus `triad_persistence` under input-family common-mode corruption.
- **H7 — primary-fault regression protection:** sequential interventional provenance does not materially worsen final coefficient integrity versus `triad_persistence` under primary-only input fault.
- **H8 — all-auxiliary coherent-fault boundary:** provenance identification still cannot establish truth when all auxiliary evidence is corrupted coherently.

## Inherited plant and sensing

Inherit the Experiment-015 scalar plant, event time `t=401`, initial learner/refit law, `x_primary`-only learning, input-family channels, A/B/C auxiliary anchor equations, physical/noise streams, persistence chronology, mismatch thresholds, losses, and A/B-vs-C physical provenance partition unless explicitly changed below.

All probe activity remains diagnostic-only and pre-event. It may not modify `x_true`, `x_primary`, `x_r1`, `x_r2`, `y`, the plant coefficient, operational A/B/C anchor measurements, or learner/refit data.

## Frozen sequential probe ladder

Use baseline diagnostic steps `181..200` exactly as in Experiment 015. Use steps `201..260` for four ordered rounds, each containing one five-step challenge for A, B, and C:

- round 1, amplitude `d1=0.025`: A `201..205`, B `206..210`, C `211..215`;
- round 2, amplitude `d2=0.050`: A `216..220`, B `221..225`, C `226..230`;
- round 3, amplitude `d3=0.100`: A `231..235`, B `236..240`, C `241..245`;
- round 4, amplitude `d4=0.200`: A `246..250`, B `251..255`, C `256..260`.

Diagnostic readout noise remains independent Gaussian with `sigma_probe=0.05` latent-input units and is pre-generated before strategy execution.

During a target-j block, every auxiliary source in j's physical failure domain receives response `g_probe * d_r`, where `d_r` is the current round amplitude and `g_probe` is the cell's frozen diagnostic response gain. Sources outside the target's physical domain receive zero response.

Three gain regimes are used below: `g_probe=1.00`, `0.50`, and `0.25`. Gain is part of the physical diagnostic pathway and is not supplied to the deployable sequential inference rule.

## Null calibration

Calibrate four round-specific positive thresholds `lambda_probe_1..lambda_probe_4` using null-intervention calibration seeds exactly `1800..1999`. Generate the same baseline and diagnostic noise, set all physical challenge responses to zero, and for each round collect absolute five-step block-mean-minus-baseline responses for all nine channel/target combinations. For each round set its threshold to the empirical 99th percentile using the inherited quantile convention.

Evaluation seeds may not contribute to calibration.

## Frozen round-level inference

At each completed round r, compute the 3x3 response matrix from that round's three target blocks relative to each channel's baseline mean over `181..200`. For each pair `(i,j)`, place an undirected shared-domain edge iff both `R_r[i,j] > lambda_probe_r` and `R_r[j,i] > lambda_probe_r`. Groups are connected components of the resulting three-node graph.

The round-level rule uses strict `>` comparisons. No amplitude normalization, posterior fitting, alternate clustering, or outcome-dependent tuning is permitted.

## Frozen sequential stopping rule

The deployable `sequential_provenance_quorum` starts with round 1 and proceeds in order. After each round:

1. infer the round-level partition by the frozen reciprocal-edge rule;
2. call the partition **decisive** iff it contains exactly two connected components, one component has exactly two sources, the other exactly one source, and there is exactly one undirected reciprocal edge in the graph;
3. stop immediately at the first decisive round;
4. if rounds 1–3 are non-decisive, escalate to the next round;
5. after round 4, use the round-4 partition whether decisive or not.

No post-event data or later-round diagnostic noise may be consulted after an early stop. For audit reproducibility all diagnostic noise streams are still pre-generated.

## Always-maximal comparator

`max_probe_provenance_quorum` uses only round 4 (`d4=0.20`) and always incurs that round's three five-step challenges. It applies the same round-level reciprocal-edge inference rule and is a deployable fixed-strength comparator, not an oracle.

The existing `oracle_provenance_quorum` remains an upper-bound comparator supplied the true A/B-vs-C partition and performs no provenance inference.

## Probe burden

For a strategy that executes a set of target blocks B, define frozen diagnostic energy

`E_probe = sum_{block in B} 5 * d(block)^2`.

Also report total challenged target-block count and maximum amplitude reached. Probe energy is an information-acquisition burden estimand only; it does not enter the plant loss.

For sequential probing, executed rounds are all rounds up to and including the stopping round. For max-probe, only the three round-4 target blocks are executed. Legacy/oracle/no-probe strategies have zero probe energy.

## Frozen cells

Evaluate exactly 22 cells:

1. healthy, magnitude 0.00, `g_probe=1.00`;
2–4. genuine physical drift, magnitudes 0.25, 0.50, 1.00, `g_probe=1.00`;
5–7. input-family common-mode corruption, magnitudes 0.25, 0.50, 1.00, `g_probe=1.00`;
8–10. primary-only input fault, magnitudes 0.25, 0.50, 1.00, `g_probe=1.00`;
11–13. physical drift + coherent A/B common-cause auxiliary fault, magnitudes 0.25, 0.50, 1.00, `g_probe=1.00`;
14–16. same A/B common-fault cells with `g_probe=0.50`;
17–19. same A/B common-fault cells with `g_probe=0.25`;
20–22. physical drift + coherent all-auxiliary fault, magnitudes 0.25, 0.50, 1.00, `g_probe=1.00`.

No cell may be added, removed, reweighted, or relabeled after outcomes are observed.

## Frozen strategies

Evaluate exactly eleven strategies on matched operational stochastic streams:

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
11. `sequential_provenance_quorum`.

Legacy meanings remain frozen. Oracle labels may not influence either deployable probe strategy.

## Seeds and bootstrap

- Preserve all inherited thresholds by exact reproduction.
- New null-probe calibration seeds: exactly `1800..1999`.
- Evaluation seeds: exactly `16000..16199`, inclusive, 200 per cell.
- Bootstrap: exactly 10,000 paired resamples with RNG seed `16016`.
- Audit seeds: exactly `16000..16004`.
- Calibration and evaluation seeds must remain disjoint.

## Primary estimands

For every cell/strategy report at minimum all inherited operational/latent/coefficient/adaptation/veto estimands plus:

- round-specific 3x3 response matrices for every executed round;
- inferred partition used by the strategy;
- physically correct partition-match indicator as audit-only information;
- stopping round;
- decisive/non-decisive status;
- maximum amplitude reached;
- executed target-block count;
- `E_probe`;
- round-specific thresholds.

## Preregistered contrasts and criteria

All contrasts are paired by evaluation seed.

### C1 — standard-gain A/B recovery
For each `g_probe=1.00` A/B-fault magnitude, compute early loss `sequential - naive`. H1 requires CI upper endpoint `<0`, adaptation-by-420 no more than 0.10 below triad, and mean partition correctness `>=0.80` at all three magnitudes.

### C2 — standard-gain efficiency
For each `g_probe=1.00` A/B-fault magnitude report `sequential - oracle` early loss and the paired difference `E_sequential - E_max`. H2 requires sequential-minus-oracle early-loss CI upper endpoint `<=0.02*mean(oracle loss)` and mean sequential probe energy `<0.75 * mean max-probe energy` at all three magnitudes.

### C3 — moderate-gain escalation
For each `g_probe=0.50` A/B-fault magnitude report partition correctness, stopping-round distribution, sequential-minus-max early loss, and probe energy. H3 requires partition correctness `>=0.80`, sequential-minus-max early-loss CI upper endpoint `<=0.02*mean(max-probe loss)`, and adaptation-by-420 no more than 0.10 below triad at all three magnitudes.

### C4 — low-gain boundary
For each `g_probe=0.25` A/B-fault magnitude report partition correctness, stopping distribution, sequential-minus-max and sequential-minus-oracle early loss, adaptation gap, veto burden, and probe energy. No success threshold is assigned.

### C5 — legitimate-drift non-destruction
For each genuine-drift magnitude compute relative excess early loss `R=(L_sequential-L_triad)/max(abs(L_triad),1e-12)`. H5 requires CI upper endpoint of mean R `<0.10` and adaptation-by-420 no more than 0.10 below triad at all three magnitudes.

### C6 — common-mode coefficient integrity
For each common-mode magnitude compute final absolute slope-error difference `sequential - triad`. H6 is supported at a magnitude iff CI upper endpoint `<0`.

### C7 — primary-fault regression
For each primary-fault magnitude compute final slope-error difference `sequential - triad`. H7 requires CI upper endpoint `<=0.01` at all three magnitudes.

### C8 — all-auxiliary coherent-fault boundary
For each all-auxiliary fault magnitude report sequential-minus-triad early loss, adaptation gap, veto burden, stopping round, and probe energy. No success threshold is assigned.

## Falsification logic

The central budgeted-probing claim is falsified if H1, H2, or H5 fails. H3 tests whether adaptive escalation remains useful under moderate response attenuation. H4 and H8 are deliberate negative boundaries and may not be retuned away. H6 alone cannot rescue failure of H1/H2/H5. H7 failure establishes regression on an already-solved condition.

## Audit requirements

The evidence artifact must permit independent verification of:

- exact `22 × 11 × 200 = 48,400` seed-strategy summaries;
- evaluation seeds exactly `16000..16199` in every cell;
- calibration seeds exactly `1800..1999`, null-only, with no leakage;
- exact baseline and four-round block chronology;
- exact amplitudes `[0.025,0.050,0.100,0.200]`, `sigma_probe=0.05`, and gain constructions;
- pre-generation and matched operational streams;
- exact round thresholds, response matrices, reciprocal-edge rule, decisiveness rule, stopping chronology, and absence of future-round access after stopping;
- exact probe-energy calculation;
- oracle isolation;
- `x_primary`-only learner/refit use;
- inherited mismatch/disagreement/vote/veto chronology and all losses/contrasts;
- exact 10,000-resample bootstrap with seed `16016`;
- deterministic equivalence of sharded and monolithic report formulas.

Record full time-step audit traces for seeds `16000..16004` for all cells and strategies. Expected audit rows: `22 × 11 × 5 × 900 = 1,089,000`.

## Execution safeguards

All execution must comply with `research/execution_contract.md`, including inherited-comparator compatibility, RNG-safe aliases, full unit tests, comparator-semantics checks, a non-evaluation-seed all-strategy smoke through the real summary path, exact schema/coverage assertions, and request marker committed last.

Execution defects may be repaired after freeze only to restore this frozen contract without altering the science above.

## Claim boundary

A positive Experiment 016 may support only this bounded statement: **under the specified diagnostic-access and gain model, a frozen sequential escalation rule can reduce diagnostic intervention burden while retaining useful provenance identification and adaptive-gating performance.**

It may not establish optimal experiment design, safety of arbitrary probing, universal response-gain adaptation, causal discovery without diagnostic access, robustness below the tested gain/noise regime, or truth identification when all auxiliary evidence shares coherent corruption.