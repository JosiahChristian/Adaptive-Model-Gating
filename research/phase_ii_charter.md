# Adaptive-Model-Gating Phase II Charter

## Status

Phase I (Experiments 016–026) is closed. Its result is an empirically characterized safety–coverage–energy frontier, not a universally dominant provenance gate.

Phase II begins from a new scientific premise: when auxiliary provenance is uncertain, the system should reason explicitly about uncertainty over competing provenance hypotheses and the decision cost of acting on the wrong partition.

This phase must not retrospectively retune the Experiment-021/023/024/025 thresholds. Those policies remain frozen comparators.

## Phase-II research question

Can a probabilistic sequential identifiability model produce calibrated, decision-useful estimates of provenance risk across the operating regions where Phase I exposed a safety–coverage tradeoff?

The object of study is no longer a raw score threshold. It is the posterior or likelihood-supported uncertainty over mutually exclusive provenance hypotheses and the resulting Bayes risk of accepting, continuing to acquire evidence, or abstaining.

## Hypothesis space

For the three-channel diagnostic problem, the first Phase-II model will reason over four mutually exclusive structural hypotheses:

- `H_ab`: channels a and b share the corrupted provenance group; c is separate.
- `H_ac`: channels a and c share the corrupted provenance group; b is separate.
- `H_bc`: channels b and c share the corrupted provenance group; a is separate.
- `H_null`: the evidence does not support a unique 2+1 provenance partition.

The all-auxiliary coherent-corruption case remains outside the identifiable truth set and must continue to be treated as an epistemic boundary, not silently folded into a correct-partition class.

## Decision actions

A sequential rule may take one of three actions after each evidence stage:

1. accept a unique provenance partition;
2. acquire the next preregistered diagnostic block if one remains;
3. abstain to the inherited `triad_persistence` fallback.

The model must expose its estimated risk for the chosen action. It may not encode a hidden deterministic threshold rule under a probabilistic label.

## Phase-II methodological requirements

- Any prior, likelihood family, nuisance treatment, loss matrix, and decision boundary must be frozen before evaluation outcomes are observed.
- Hyperparameters may be derived analytically from the simulator or from disjoint calibration/null seeds, but not from Phase-I evaluation outcomes.
- Calibration quality must be evaluated directly. A low empirical error rate is not sufficient if stated posterior risks are miscalibrated.
- Rare-error claims require high-powered evaluation and explicit confidence intervals.
- Phase-I policies remain frozen comparators; they are not modified to make Phase II look better.
- Probe amplitude and sensing assumptions remain unchanged in the first Phase-II experiment so that any gain comes from the probabilistic decision model rather than additional information.

## Initial Phase-II sequence

Experiment 027: probabilistic identifiability calibration. Build and validate a sequential structural likelihood/posterior model and test whether its stated wrong-acceptance probabilities are calibrated across the Phase-I frontier.

Only if Experiment 027 establishes usable calibration should a later experiment optimize a Bayes decision policy around those probabilities. This separates model validity from policy optimization.

## Stopping rule

If the probabilistic model cannot achieve adequate calibration without outcome-fitted corrections, Phase II must stop or change modeling assumptions. Do not repair a failed probability model by simply searching a new decision threshold on the same evaluation set.
