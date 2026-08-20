# Experiment 021 — Prospective Qualification-Aware Early Targeting

**Status:** prospectively frozen before any Experiment 021 outcome generation.

## Scientific boundary

Experiment 020 established that round-3 edge selection followed by two-endpoint round-4 confirmation can reduce moderate-gain diagnostic burden while preserving coverage and precision. On the Experiment-020 evaluation seeds at `g_probe=0.50`, the early-targeted strategy achieved coverage `0.985`, precision `1.000`, wrong acceptance `0.000`, and mean energy `0.649875`, versus the inherited Experiment-019 comparator coverage `0.980` and mean energy `0.918875`.

Experiment 020 also exposed a standard-gain burden tradeoff: at `g_probe=1.00`, both strategies retained coverage and precision `1.000`, but Experiment 020 used mean energy `0.596875` versus `0.379125` for the inherited Experiment-019 comparator. The mechanism is structural: the Experiment-020 strategy enters its round-4 early-target layer after round 3 even when the inherited cumulative rule may already have confidence-qualified during rounds 1–3.

Experiment 021 therefore tests a qualification-aware dispatcher. It preserves all inherited confidence-qualified exits through rounds 1–3 exactly. Only cases still unresolved after round 3 may enter the frozen Experiment-020 early-targeted round-4 mechanism.

No new threshold, learned selector, diagnostic amplitude, block length, or calibration range is introduced. No Experiment 021 outcome may be generated before this specification is committed.

## Hypotheses

- **H1 — moderate-gain preservation:** qualification-aware dispatch retains Experiment-020 moderate-gain coverage, precision, safety, and energy efficiency.
- **H2 — standard-gain burden recovery:** honoring inherited round-1..3 qualification materially reduces standard-gain energy relative to Experiment 020 while preserving deployment quality.
- **H3 — dispatch validity:** whenever the inherited cumulative rule qualifies by round 1, 2, or 3, Experiment 021 produces the exact inherited Experiment-019 decision path and never executes the Experiment-020 early-targeted round 4.
- **H4 — unresolved-case preservation:** cases unresolved through round 3 are passed into the frozen Experiment-020 mechanism without any threshold or selector modification.
- **H5 — attenuation safety:** gains `0.375`, `0.25`, and `0.125` retain the safety/abstention behavior established in Experiment 020.
- **H6 — regression protection:** genuine drift, common-mode corruption, primary-only fault, and coherent-all-auxiliary boundary behavior are not materially degraded.

## Frozen mechanism

Generate the inherited Experiment-017 diagnostic stream and compute cumulative rounds 1, 2, and 3 using the frozen `mu_1..mu_3` and `nu_1..nu_3` thresholds.

For `r = 1,2,3` in order:

1. compute the inherited cumulative graph for round `r`;
2. if the graph is structurally decisive and its unique reciprocal edge exceeds inherited `nu_r`, immediately deploy the inferred partition;
3. execute no later diagnostic rounds;
4. operational behavior must be identical to the inherited Experiment-019 targeted strategy for the same seed/cell.

If no round 1–3 qualification occurs, dispatch the seed unchanged into the frozen Experiment-020 early-targeted strategy, including its round-3 leading-edge selector, early round-4 thresholds `mu_4^E`, `nu_4^E`, missing-third-block completion rule, targeted round-5 rule, and triad fallback.

The dispatcher may not use family labels, gain, oracle truth, post-event outcomes, or evaluation results.

## Frozen strategies

Evaluate exactly seventeen strategies: the sixteen frozen Experiment-020 strategies plus

17. `qualification_aware_early_targeted_replicated_selective_cumulative_provenance_quorum`.

The first sixteen retain their Experiment-020 meanings exactly. Only strategy 17 uses the new dispatcher.

## Frozen cells

Evaluate exactly the same 28 cells used by Experiments 017–020.

## Seeds and bootstrap

- all inherited calibration ranges remain unchanged;
- no new calibration is introduced;
- evaluation seeds: exactly `21000..21199`;
- 200 seeds per cell;
- paired bootstrap: 10,000 resamples, RNG seed `21021`;
- audit seeds: `21000..21004`.

These evaluation seeds are disjoint from all prior evaluation and calibration ranges.

## Primary estimands

Retain all Experiment-020 estimands and additionally record:

- inherited prequalification indicator;
- inherited prequalification round (`1`, `2`, `3`, or `0` if unresolved);
- Experiment-020 dispatcher-entry indicator;
- final coverage, precision, wrong acceptance, abstention;
- total diagnostic energy and target-block count;
- operational loss `401..600`;
- adaptation by 420;
- final coefficient error.

## Preregistered criteria

### C1 — moderate-gain preservation

At all three `g_probe=0.50` A/B-fault magnitudes require:

- final coverage `>=0.97`;
- coverage no more than `0.02` below Experiment 020;
- accepted precision `>=0.99`;
- wrong acceptance `<=0.01`;
- mean diagnostic energy `<=0.65`;
- qualification-aware-minus-Experiment020 early-loss bootstrap CI upper endpoint `<=0.02 * mean(Experiment020 early loss)`;
- adaptation-by-420 gap versus Experiment 020 `>=-0.05`.

### C2 — standard-gain burden recovery

At all three `g_probe=1.00` A/B-fault magnitudes require:

- coverage `>=0.99`;
- precision `>=0.99`;
- wrong acceptance `<=0.01`;
- mean energy `<=0.45`;
- mean energy at least `0.10` below Experiment 020;
- early-loss CI upper endpoint versus Experiment 020 `<=0.02 * mean(Experiment020 early loss)`;
- adaptation gap versus Experiment 020 `>=-0.05`.

Failure of the energy-reduction requirement falsifies H2.

### C3 — exact inherited early-exit preservation

For every seed/cell that confidence-qualifies during inherited rounds 1–3, compare strategy 17 with the inherited Experiment-019 targeted strategy. Require exact equality of:

- qualification round;
- accepted/abstained decision;
- accepted partition;
- operational adaptation sequence;
- operational loss;
- probe energy.

Any mismatch invalidates the implementation.

### C4 — unresolved dispatch preservation

For every seed unresolved through round 3, the Experiment-020 dispatcher-entry indicator must equal 1. The subsequent Experiment-020 mechanism must use exactly the frozen `mu_4^E`, `nu_4^E`, targeted round-5 thresholds, amplitudes, block lengths, and fallback rules.

### C5 — attenuation safety

At gains `0.375`, `0.25`, and `0.125` require:

- wrong acceptance `<=0.05` (`<=0.01` at `0.125`);
- early-loss CI upper endpoint versus `triad_persistence` `<=0.05 * mean(triad early loss)` (`<=0.02` fraction at `0.125`);
- adaptation gap versus triad `>=-0.10`;
- at `g_probe=0.125`, abstention `>=0.90`.

### C6 — regression protection

For genuine drift, common-mode corruption, and primary-only faults, require the same noninferiority protections used in Experiment 020 against the Experiment-020 strategy. Coherent-all-auxiliary corruption remains an explicit negative boundary with no truth-identifiability success claim.

## Frozen claim logic

The central Experiment-021 claim is **qualification-aware diagnostic efficiency**: a policy can combine inherited early confidence exits with Experiment-020 targeted confirmation so that diagnostic effort is spent only when evidence remains unresolved.

- H1 and H2 are required for the central claim.
- H3 is a mandatory implementation-validity condition.
- H4 verifies faithful dispatch into the frozen Experiment-020 mechanism.
- H5 and H6 are mandatory safety/regression protections.

No outcome-driven threshold, selector, amplitude, timing, or success-criterion modification is permitted after this freeze.
