# Experiment 022 — Prospective Generalization and Boundary Validation

Status: **FROZEN BEFORE ANY EXPERIMENT-022 OUTCOMES**

## Motivation
Experiments 019–021 established a qualification-aware targeted provenance rule with high precision and reduced diagnostic energy on the inherited three-channel synthetic benchmark. Experiment 022 deliberately stops optimizing the rule. It tests whether the frozen Experiment-021 policy generalizes beyond the exact evaluation distribution used to develop it.

## Frozen policy
The Experiment-021 qualification-aware strategy is frozen without threshold, selector, amplitude, stopping-rule, fallback, or calibration changes. Experiment 022 may change only the evaluation distribution and reporting harness.

## Primary question
Does the frozen Experiment-021 policy retain safety, partition precision, useful coverage, and its energy advantage under out-of-distribution nuisance and gain conditions?

## Evaluation dimensions
Use fresh seeds 22000–22199 and no recalibration. Evaluate the existing benchmark controls plus prospective stress conditions spanning:

1. probe gain values between and outside previously emphasized points: 0.45, 0.425, 0.35, 0.30, 0.20, 0.10;
2. observation-noise scale multipliers: 0.75, 1.25, 1.50;
3. nuisance timing offsets relative to the inherited fault/drift onset: -20, +20, +50 samples;
4. asymmetric auxiliary corruption, where the two auxiliary channels no longer share equal corruption magnitude;
5. mixed drift + common-mode nuisance conditions not used to choose the Experiment-021 dispatcher.

Implementation may add stream-generation parameters needed to realize these stressors, but must not inspect Experiment-022 outcomes to alter the frozen policy.

## Comparators
- Experiment-021 qualification-aware strategy (primary)
- Experiment-020 early-targeted strategy
- Experiment-019 targeted strategy
- triad_persistence safety comparator

## Primary preregistered criteria
H1 Safety: zero wrong provenance acceptance across every Experiment-022 stress cell.

H2 Precision: among accepted partitions, precision >= 0.99 in every cell with at least 20 accepted seeds; otherwise report the exact binomial count without claiming precision generalization.

H3 Moderate-information utility: for gain >= 0.35 stress cells representing the inherited drift_ab structure, Experiment-021 coverage >= 0.90 unless the corresponding Experiment-020 coverage is below 0.90; in that case Experiment-021 must remain within 0.03 absolute coverage of Experiment 020.

H4 Conservative low-information behavior: at gain <= 0.20, wrong acceptance remains zero and Experiment-021 must not increase adaptation rate relative to triad_persistence by more than 0.02.

H5 Energy: wherever Experiment-021 and Experiment-020 coverage differ by <= 0.03 absolute, Experiment-021 mean probe energy must be <= Experiment-020 mean probe energy + 0.01.

H6 Inherited dispatch integrity: every seed classified as inherited-prequalified must reproduce the corresponding Experiment-019 stop round, acceptance decision, gate partition, adaptation signature, operational loss, and probe energy exactly.

## Secondary analyses
Report coverage/abstention curves versus gain, energy-versus-coverage tradeoffs, prequalification/dispatch rates, operational loss, adaptation rate, final coefficient error, and paired bootstrap intervals. Stress dimensions are interpreted individually; no post-hoc threshold retuning is permitted.

## Negative-control boundary
The coherent all-auxiliary corruption case remains outside the identification claim. Failure to recover that unidentifiable case is not counted against H1–H6 unless the policy makes a wrong positive acceptance.

## Decision rule
If H1 and H6 fail, the current policy is not considered robust enough for the lane's main claim. If H1/H6 pass but H3/H5 fail, the result defines a generalization/efficiency boundary rather than authorizing retrospective retuning. Any subsequent adaptation must be a separately frozen experiment.
