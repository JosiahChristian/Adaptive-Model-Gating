# Experiment 014 — Prospective Dependence Learning From Observable Pre-Event Signatures

**Status:** prospectively frozen before any Experiment 014 outcome generation.

## Scientific boundary

Experiment 013 established a bounded positive result: provenance-aware corroboration can prevent raw sensor-count over-veto when the supplied failure-domain metadata is correct. It also established the next negative boundary: when physically common-cause A/B sources are falsely declared independent, the provenance-aware mechanism reproduces the naive failure mode. The remaining question is therefore whether useful failure-domain structure can be learned from observable historical behavior rather than provided as trusted oracle metadata.

Experiment 014 tests one deliberately bounded mechanism: infer auxiliary-source dependence groups from healthy pre-event residual-correlation signatures, freeze the inferred grouping before evaluation events, and then use the Experiment-013 provenance-aware quorum with those inferred groups. The experiment does not assume arbitrary hidden dependencies are discoverable. It tests only dependence that leaves a measurable pre-event signature under the frozen DGP.

No Experiment 014 outcome may be generated before this specification is committed. After freeze, hypotheses, DGP, cells, strategies, seeds, calibration/inference procedures, estimands, bootstrap rules, stopping criteria, audit requirements, and claim boundaries below are immutable in response to observed Experiment 014 outcomes.

## Hypotheses

### H1 — recoverable dependence learning
When A and B share the frozen observable healthy dependence signature and C does not, the learned-dependence gate identifies A/B as one inferred group often enough to recover the Experiment-013 G1 common-cause-fault advantage over naive raw sensor counting.

### H2 — common-mode input protection
With healthy auxiliaries and correctly recoverable dependence structure, learned-dependence corroboration improves final coefficient integrity relative to `triad_persistence` under input-family common-mode corruption.

### H3 — legitimate-drift non-destruction
With genuine physical drift and healthy auxiliaries, learned-dependence corroboration does not materially degrade early operational loss or adaptation relative to `triad_persistence`.

### H4 — primary-fault regression protection
Under primary-only input fault, learned-dependence corroboration does not materially worsen final coefficient integrity relative to `triad_persistence`.

### H5 — absent-signature identifiability boundary
If A/B retain a common failure mode but their healthy pre-event dependence signature is removed, the experiment does not assume passive historical data can recover that hidden dependence. Failure to group A/B is a preserved negative boundary.

### H6 — misleading-signature boundary
If healthy pre-event signatures suggest A/B dependence but the post-event physical common-cause fault instead couples B/C, the learned grouping is stale/misleading. Material over-veto or missed protection is a preserved negative finding.

### H7 — all-group coherent-fault boundary
If all auxiliary sources share coherent corruption, inferred dependence groups cannot establish truth from agreement alone. This remains a preserved identifiability boundary.

## Data-generating process

Inherit the scalar adaptive-model plant, event chronology, learner/refit law, primary-input-only learning, input-family channels, anchor equations, losses, and legacy thresholds from Experiment 013 unless explicitly extended below.

Use auxiliary anchors A, B, and C. In the standard recoverable-dependence DGP, A and B share a small zero-mean healthy group-level residual component `u_G1(t)` in addition to their independent measurement noises; C has no such component. This component is present throughout the pre-event healthy history and remains diagnostically observable without fault labels or latent truth. It is not itself treated as a failure and its scale is fixed below.

Let anchor-space measurements be expressed in latent-input units after division by the inherited anchor coefficient. Healthy residuals relative to the input-family consensus are:

- `e_A(t) = eta_A(t) + rho_sig * u_G1(t)`;
- `e_B(t) = eta_B(t) + rho_sig * u_G1(t)`;
- `e_C(t) = eta_C(t)`.

Here `eta_A`, `eta_B`, `eta_C`, and `u_G1` are mutually independent standard-normal unit streams scaled by the inherited anchor-noise scale; freeze `rho_sig = 0.35`. The implementation must pre-generate these streams before strategy execution. This signature is intentionally weak enough that grouping must be estimated statistically rather than deterministically read from metadata.

The `absent_signature` family sets `rho_sig = 0` while retaining A/B as the physical common-failure pair after the event. The `misleading_signature` family uses the standard A/B healthy signature before the event but applies post-event coherent common-cause corruption to B/C rather than A/B.

Event-time physical fault magnitudes and plant drift magnitudes inherit the Experiment-013 conventions. No inferred group may use event labels, future samples, latent state, or injected-fault identity.

## Frozen dependence inference procedure

Dependence groups are inferred **once per evaluation seed before the event** and then frozen for that run.

Use only pre-event diagnostic steps `101..300`. For each auxiliary anchor, form residuals against the input-family median in latent-input units. Compute Pearson correlation for residual pairs A/B, A/C, and B/C over those 200 steps.

Calibrate a single absolute-correlation grouping threshold `lambda_dep` from healthy-only calibration seeds exactly `1400..1599` under a null DGP with three independent auxiliary residuals (`rho_sig = 0`). For each calibration seed collect all three absolute pairwise correlations over steps `101..300`; set `lambda_dep` to the empirical 99th percentile using the inherited quantile convention.

At evaluation time, create an undirected edge between two anchors iff their absolute pre-event residual correlation is strictly greater than `lambda_dep`. Inferred provenance groups are the connected components of this three-node graph. This graph procedure is frozen; no tuning, tie-breaking change, clustering alternative, or outcome-dependent threshold modification is permitted.

Record the inferred group assignment and all three pre-event correlations in every seed summary and audit metadata.

## Frozen cells

Evaluate exactly 22 cells:

1. healthy, magnitude 0.00;
2–4. physical drift, magnitudes 0.25, 0.50, 1.00;
5–7. input-family common-mode corruption, magnitudes 0.25, 0.50, 1.00;
8–10. primary-only input fault, magnitudes 0.25, 0.50, 1.00;
11–13. physical drift + coherent A/B common-cause auxiliary fault with recoverable A/B healthy signature, magnitudes 0.25, 0.50, 1.00;
14–16. physical drift + coherent A/B common-cause auxiliary fault with **absent** healthy dependence signature, magnitudes 0.25, 0.50, 1.00;
17–19. physical drift + coherent B/C auxiliary fault after an A/B healthy dependence signature (`misleading_signature`), magnitudes 0.25, 0.50, 1.00;
20–22. physical drift + coherent all-auxiliary fault, magnitudes 0.25, 0.50, 1.00.

No cell may be added, removed, reweighted, or relabeled after outcomes are observed.

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
9. `oracle_provenance_quorum` — Experiment-013 provenance-aware rule supplied the physically correct A/B vs C grouping in recoverable/absent-signature cells and the physically correct post-event B/C vs A grouping in misleading-signature cells; this is an upper-bound comparator, not an deployable strategy;
10. `learned_provenance_quorum` — Experiment-013 provenance-aware rule using only the grouping inferred from steps `101..300` by the frozen procedure above.

Legacy strategies retain their prior frozen definitions. The oracle comparator may not influence learned grouping, calibration, or any other strategy.

## Calibration and seeds

- Preserve `tau`, `kappa`, `kappa3`, and all Experiment-013 anchor mismatch/cross-anchor thresholds by exact reproduction from prior frozen procedures.
- Calibrate only the new `lambda_dep` using null healthy-only seeds `1400..1599`.
- Evaluation seeds are exactly `14000..14199`, inclusive, 200 seeds per cell.
- Calibration seeds and evaluation seeds are disjoint and evaluation seeds are forbidden from threshold calibration.
- Bootstrap resampling uses exactly 10,000 paired resamples with RNG seed `14014`.
- Audit seeds are exactly `14000..14004`.

## Primary estimands

For every cell and strategy report at minimum:

- mean operational loss over steps `401..600`;
- mean latent loss over steps `401..600`;
- final absolute slope/coefficient error;
- adaptation-by-`t=420` rate;
- adaptation/update burden;
- input common-mode-suspect fraction;
- A/B/C mismatch and pairwise disagreement fractions;
- raw mismatch-vote count and inferred-group mismatch-vote count;
- veto burden;
- pre-event residual correlations `corr_AB`, `corr_AC`, `corr_BC`;
- inferred group assignment;
- indicator that the inferred grouping matches the physically correct common-failure partition for that cell, reported as an audit/diagnostic estimand only and never available to the learned strategy.

## Preregistered paired contrasts and criteria

All contrasts are paired by evaluation seed.

### C1 — recoverable A/B fault recovery
For each recoverable A/B common-fault magnitude compute early operational-loss difference:

`Delta_REC = loss(learned_provenance_quorum) - loss(naive_three_anchor_quorum)`.

H1 requires the 95% CI upper endpoint `< 0` at all three magnitudes, learned adaptation-by-420 no more than 0.10 below `triad_persistence`, and mean inferred-partition correctness at least `0.80` in the corresponding cells.

### C2 — common-mode coefficient integrity
For each input common-mode magnitude compute final absolute slope-error difference:

`Delta_CM = error(learned_provenance_quorum) - error(triad_persistence)`.

H2 is supported at a magnitude only if the 95% CI upper endpoint is `< 0`.

### C3 — legitimate-drift non-destruction
For each drift magnitude compute relative excess early loss:

`R = (L_learned - L_triad) / max(abs(L_triad), 1e-12)`.

H3 requires the 95% CI upper endpoint of mean `R` `< 0.10` and adaptation-by-420 no more than 0.10 below triad persistence at all three magnitudes.

### C4 — primary-fault regression
For each primary-fault magnitude compute final absolute slope-error difference learned minus triad. H4 requires the 95% CI upper endpoint `<= 0.01` at all three magnitudes.

### C5 — absent-signature boundary
For each absent-signature A/B common-fault magnitude report learned minus naive and learned minus oracle early loss, inferred-partition correctness, adaptation gap versus triad, and veto burden. No success threshold is assigned. Failure to recover the hidden A/B grouping is a preserved negative finding.

### C6 — misleading-signature boundary
For each misleading-signature B/C fault magnitude report learned minus oracle and learned minus triad early loss, inferred-group assignment frequencies, adaptation gap, and veto burden. No success threshold is assigned. Performance degradation caused by stale pre-event dependence structure is a preserved negative finding.

### C7 — all-auxiliary coherent-fault boundary
For each all-auxiliary coherent-fault magnitude report learned minus triad early loss, adaptation gap, and veto burden. No success threshold is assigned.

## Falsification logic

The central learned-dependence claim is falsified if H1 or H3 fails. H2 alone is insufficient. Failure of H4 establishes regression on an already-solved condition. H5–H7 are deliberate negative-boundary tests and may not be retuned away.

No dependence threshold, correlation window, edge rule, graph grouping rule, signature strength, cell, seed, bootstrap rule, strategy, estimand, or decision criterion may be changed after any Experiment 014 outcome is inspected.

## Audit requirements

The evidence artifact must permit independent verification of:

- exact `22 × 10 × 200 = 44,000` seed-strategy summaries;
- exact evaluation seeds `14000..14199` in every cell;
- exact new calibration seeds `1400..1599` and their disjointness from all evaluation seeds;
- exact reproduction of inherited thresholds;
- exact `rho_sig = 0.35` standard-signature construction and `rho_sig = 0` absent-signature construction;
- matched stochastic streams across strategies;
- pre-event correlation calculations over exactly steps `101..300`;
- exact `lambda_dep` reproduction and connected-component grouping semantics;
- oracle grouping isolation from the learned strategy;
- learner/refit use of `x_primary` only;
- all mismatch, disagreement, raw-vote, inferred-group-vote, and veto statistics;
- decision chronology and persistence state;
- operational/latent losses, coefficient integrity, adaptation burden, grouping accuracy diagnostics, and all paired contrasts;
- exact 10,000-resample intervals using bootstrap seed `14014`;
- deterministic equivalence between sharded merge/report formulas and the frozen monolithic formulas.

Record full time-step audit traces for evaluation seeds `14000..14004` for all cells and strategies. Expected audit rows: `22 × 10 × 5 × 900 = 990,000`.

## Execution safeguards

All Experiment 014 execution must comply with `research/execution_contract.md`: full unit tests, inherited-comparator compatibility checks, non-evaluation-seed all-strategy smoke testing through the real summary path, explicit comparator-semantics tests, exact shard coverage assertions, and request marker committed last.

Execution defects may be repaired after freeze only if they restore the frozen implementation contract without altering this specification.

## Claim boundary

A positive Experiment 014 may support only this bounded statement: **when common failure-domain dependence leaves the specified observable pre-event residual-correlation signature, a frozen data-driven grouping rule can recover enough dependence structure to reduce raw sensor-count over-veto without materially harming legitimate drift adaptation.**

It may not establish automatic discovery of arbitrary hidden dependencies, causal identification from passive data in general, robustness to dependence with no observable signature, robustness to post-calibration dependence changes, correctness under misleading historical signatures, or robustness when all auxiliary evidence shares coherent corruption.
