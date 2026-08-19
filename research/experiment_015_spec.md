# Experiment 015 — Prospective Interventional Provenance Identification

**Status:** prospectively frozen before any Experiment 015 outcome generation.

## Scientific boundary

Experiment 014 established that passive pre-event residual correlation is not a reliable general substitute for structural provenance: the frozen learner sometimes reduced over-veto when its observational signature aligned with the true failure structure, but exact partition recovery was poor and absent/misleading signatures produced large failures. Experiment 015 tests the next scientifically distinct information source: controlled pre-event diagnostic intervention.

The question is whether a small known challenge applied to auxiliary-source support domains can identify shared failure domains well enough to approach the oracle provenance gate, while preserving legitimate adaptation and without using latent truth, event labels, future samples, or injected-fault identity.

No Experiment 015 outcome may be generated before this specification is committed. After freeze, the DGP, interventions, hypotheses, cells, strategies, seeds, calibration, estimands, contrasts, criteria, audit rules, and claim boundaries below are immutable in response to outcomes.

## Hypotheses

- **H1 — interventional recovery:** when A and B share a failure domain, the frozen challenge-response rule recovers the A/B-vs-C partition often enough to outperform naive raw-sensor quorum under A/B common-cause auxiliary fault.
- **H2 — oracle approach:** under the same A/B common-fault cells, interventional provenance has no material early-loss disadvantage versus the oracle provenance comparator.
- **H3 — common-mode input protection:** with healthy auxiliaries, interventional provenance improves final coefficient integrity versus `triad_persistence` under input-family common-mode corruption.
- **H4 — legitimate-drift non-destruction:** diagnostic intervention and the inferred grouping do not materially degrade genuine-drift adaptation versus `triad_persistence`.
- **H5 — primary-fault regression protection:** interventional provenance does not materially worsen final coefficient integrity versus `triad_persistence` under primary-only input fault.
- **H6 — weak-intervention boundary:** if the challenge response is too weak relative to diagnostic noise, partition recovery may fail; this is preserved rather than retuned.
- **H7 — actuator-coupling boundary:** if the diagnostic intervention itself cross-couples unrelated domains, inferred provenance may be wrong; this is preserved rather than retuned.
- **H8 — all-auxiliary coherent-fault boundary:** even correctly identified provenance cannot establish truth when all auxiliary evidence shares coherent corruption.

## Inherited plant and operational sensing

Inherit from Experiment 014 the scalar plant, event time `t=401`, initial learner/refit law, `x_primary`-only learning, input-family channels, A/B/C auxiliary anchor equations, physical-noise construction, persistence chronology, legacy thresholds, losses, and matched-stream requirement except where explicitly extended below.

The standard physical failure partition is A/B in domain `G1` and C in domain `G2`. The misleading passive signature from Experiment 014 is not used for identification in this experiment; passive residual correlations remain audit diagnostics only.

## Frozen diagnostic intervention

The intervention is performed before adaptive evaluation begins, during steps `201..260`, while the initial model is still in its pre-evaluation period. It modifies only auxiliary diagnostic measurements, never `x_true`, `x_primary`, `x_r1`, `x_r2`, `y`, the plant coefficient, or the learner/refit data.

Three deterministic 20-step challenge blocks are applied:

- steps `201..220`: challenge source A support domain;
- steps `221..240`: challenge source B support domain;
- steps `241..260`: challenge source C support domain.

Freeze standard challenge amplitude `delta_probe = 0.20` in latent-input units. During the block targeting source `j`, every auxiliary source in the **same physical failure domain** as `j` receives additive diagnostic response `+delta_probe` in latent-input units, while sources in other domains receive zero intervention response. Independent diagnostic readout noise is Gaussian with frozen standard deviation `sigma_probe = 0.05` latent-input units and is pre-generated for A/B/C at all steps. The operational anchor measurements outside these diagnostic responses retain the inherited stochastic construction.

The `weak_probe` family uses the same physical A/B-vs-C partition but freezes `delta_probe = 0.025`. The `cross_coupled_probe` family uses standard `delta_probe = 0.20` but, during A- and B-targeted blocks only, C receives an additional response `gamma_probe * delta_probe` with frozen `gamma_probe = 0.80`, despite C belonging physically to `G2`. This represents an intervention actuator whose challenge pathway itself is not domain-specific.

No post-event fault outcome, latent state, or physical group label is available to the inference algorithm.

## Frozen interventional inference rule

For each evaluation seed, infer groups once using only steps `201..260`, then freeze the grouping before step 301.

For each targeted challenge block and each observed auxiliary channel, compute the mean diagnostic residual relative to that channel's mean over baseline steps `181..200`. Let `R[i,j]` be the mean response of observed channel `i` during the block targeting source `j`.

Calibrate a single positive response threshold `lambda_probe` using healthy null-intervention calibration seeds exactly `1600..1799`: generate the same diagnostic readout noise but set all probe amplitudes to zero; collect absolute block-mean residual responses for all nine `(i,j)` channel/target combinations; set `lambda_probe` to the empirical 99th percentile using the inherited quantile convention.

For each pair of sources `(i,j)`, place an undirected shared-domain edge iff **both** `R[i,j] > lambda_probe` and `R[j,i] > lambda_probe`. Inferred provenance groups are the connected components of this three-node graph. Strict `>` comparisons are frozen. No alternative clustering, tuning, sign rule, normalization, or outcome-dependent adjustment is permitted.

Record the full 3×3 response matrix, inferred partition, and oracle-match indicator as diagnostics. The oracle match indicator is never available to the deployable strategy.

## Frozen cells

Evaluate exactly 22 cells:

1. healthy, magnitude 0.00;
2–4. genuine physical drift, magnitudes 0.25, 0.50, 1.00;
5–7. input-family common-mode corruption, magnitudes 0.25, 0.50, 1.00;
8–10. primary-only input fault, magnitudes 0.25, 0.50, 1.00;
11–13. physical drift + coherent A/B common-cause auxiliary fault under the standard probe, magnitudes 0.25, 0.50, 1.00;
14–16. physical drift + coherent A/B common-cause auxiliary fault under `weak_probe`, magnitudes 0.25, 0.50, 1.00;
17–19. physical drift + coherent A/B common-cause auxiliary fault under `cross_coupled_probe`, magnitudes 0.25, 0.50, 1.00;
20–22. physical drift + coherent all-auxiliary fault under the standard probe, magnitudes 0.25, 0.50, 1.00.

No cell may be added, removed, relabeled, or reweighted after outcomes are observed.

## Frozen strategies

Evaluate exactly ten strategies on matched stochastic streams:

1. `frozen`;
2. `continuous`;
3. `threshold`;
4. `persistence`;
5. `health_persistence`;
6. `triad_persistence`;
7. `independent_persistence`;
8. `naive_three_anchor_quorum`;
9. `oracle_provenance_quorum` — supplied the true A/B-vs-C physical partition, upper-bound only;
10. `interventional_provenance_quorum` — uses only the frozen challenge-response grouping rule above.

Legacy and oracle strategies retain prior meanings and may not influence interventional inference.

## Calibration and seeds

- Preserve `tau`, `kappa`, `kappa3`, and all inherited anchor thresholds by exact reproduction from prior frozen procedures.
- New `lambda_probe` calibration seeds: exactly `1600..1799`, null intervention only.
- Evaluation seeds: exactly `15000..15199`, inclusive, 200 per cell.
- Bootstrap: exactly 10,000 paired resamples with RNG seed `15015`.
- Audit seeds: exactly `15000..15004`.
- Calibration and evaluation seed sets must remain disjoint.

## Primary estimands

For every cell/strategy report at minimum: operational and latent loss over `401..600`, final absolute slope error, adaptation-by-420 rate, update burden, veto burden, input common-mode-suspect fraction, A/B/C mismatch and cross-anchor disagreement fractions, raw and provenance-group mismatch votes, all nine diagnostic response-matrix entries, inferred group assignment, inferred-partition correctness, and probe configuration.

## Preregistered contrasts

All contrasts are paired by evaluation seed.

### C1 — standard A/B common-fault recovery
For each standard A/B common-fault magnitude compute early loss `interventional - naive`. H1 requires the 95% CI upper endpoint `< 0`, adaptation-by-420 no more than 0.10 below triad persistence, and mean partition correctness `>= 0.80` at all three magnitudes.

### C2 — oracle approach
For each standard A/B common-fault magnitude compute early loss `interventional - oracle`. H2 requires the 95% CI upper endpoint `<= 0.02 * mean(oracle loss)` at all three magnitudes.

### C3 — common-mode coefficient integrity
For each input common-mode magnitude compute final absolute slope-error difference `interventional - triad`. H3 is supported at a magnitude iff the 95% CI upper endpoint `< 0`.

### C4 — legitimate-drift non-destruction
For each drift magnitude compute `R=(L_interventional-L_triad)/max(abs(L_triad),1e-12)`. H4 requires the 95% CI upper endpoint of mean R `< 0.10` and adaptation-by-420 no more than 0.10 below triad at all three magnitudes.

### C5 — primary-fault regression
For each primary-fault magnitude compute final slope-error difference `interventional - triad`. H5 requires the 95% CI upper endpoint `<= 0.01` at all three magnitudes.

### C6 — weak-probe boundary
For each weak-probe A/B fault magnitude report partition correctness, interventional-minus-naive and interventional-minus-oracle early loss, adaptation gap, and veto burden. No success threshold is assigned.

### C7 — cross-coupled-probe boundary
For each cross-coupled-probe A/B fault magnitude report inferred partition frequencies, partition correctness, interventional-minus-oracle and interventional-minus-triad early loss, adaptation gap, and veto burden. No success threshold is assigned.

### C8 — all-auxiliary coherent-fault boundary
For each all-auxiliary fault magnitude report interventional-minus-triad early loss, adaptation gap, and veto burden. No success threshold is assigned.

## Falsification logic

The central interventional-identification claim is falsified if H1 or H4 fails. H2 quantifies approach to oracle but cannot rescue H1/H4. H3 alone is insufficient. H5 failure establishes regression. H6–H8 are deliberate negative-boundary tests and may not be retuned away.

## Audit requirements

The evidence artifact must permit independent verification of:

- exact `22 × 10 × 200 = 44,000` seed-strategy summaries;
- exact evaluation seeds `15000..15199` in every cell;
- calibration seeds `1600..1799`, null-probe calibration only, and no leakage;
- exact `delta_probe`, `sigma_probe`, weak-probe, and cross-coupling constructions;
- exact baseline `181..200` and challenge blocks `201..220`, `221..240`, `241..260`;
- exact 3×3 response calculations, `lambda_probe`, reciprocal-edge rule, and connected components;
- matched stochastic streams and pre-generation of diagnostic noises;
- isolation of oracle labels from interventional inference;
- `x_primary`-only learner/refit use;
- chronology, mismatch/disagreement/vote/veto statistics, losses, coefficient integrity, burden, contrasts, and bootstrap intervals;
- deterministic equivalence between monolithic and sharded report formulas.

Record full time-step audit traces for seeds `15000..15004` for all cells and strategies. Expected audit rows: `22 × 10 × 5 × 900 = 990,000`.

## Execution safeguards

All execution must comply with `research/execution_contract.md`: full unit tests, inherited-comparator compatibility checks, RNG-safe legacy aliases, comparator-semantics tests, non-evaluation-seed all-strategy smoke through the real shard-summary path, exact schema/coverage assertions, and request marker committed last.

Execution defects may be repaired after freeze only to restore this frozen contract; scientific definitions above may not change.

## Claim boundary

A positive Experiment 015 may support only this bounded statement: **under the specified diagnostic-access model, controlled pre-event challenge-response information can identify shared auxiliary failure domains sufficiently well to improve provenance-aware adaptive gating relative to naive sensor counting without materially harming legitimate drift adaptation.**

It may not establish automatic causal discovery from passive data, universal provenance identification, safety of arbitrary interventions, robustness to weak or cross-coupled actuators, or truth identification when all auxiliary evidence shares coherent corruption.
