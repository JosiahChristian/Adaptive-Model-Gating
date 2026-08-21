# Experiment 027 — Sequential Probabilistic Identifiability Calibration

## Status

Prospectively frozen before any Experiment-027 calibration or evaluation outcomes are generated.

This is the first experiment in Phase II. It is a model-validity study, not a policy-optimization study.

Prospective design correction: before implementation or outcome generation, the hypothesis semantics were corrected so that `H_ab/H_ac/H_bc` denote diagnostic response topology rather than fault presence. The simulator's active probes reveal the fixed physical response grouping `a/b | c` even in healthy and non-provenance control streams; therefore labeling those controls as ground-truth `H_null` would be internally inconsistent. `H_null` now denotes insufficient/no unique response-topology evidence under the probabilistic model. This correction was made before any Experiment-027 outcomes existed.

## Scientific question

Can a frozen sequential probabilistic model over the four response-topology hypotheses `H_ab`, `H_ac`, `H_bc`, and `H_null` produce calibrated probabilities across the operating regions where Experiments 016–026 exposed a safety–coverage frontier?

The probabilities are probabilities about the diagnostic response topology, not direct probabilities that a fault is present. A later decision model would have to combine topology uncertainty with the adaptation/fault state.

## Fixed evidence representation

Experiment 027 reuses the existing symmetric diagnostic schedule through round 5 without changing probe amplitude, target order, timing, or sensing assumptions.

At each completed diagnostic stage r, form the three reciprocal cumulative edge scores

`Q_r = (Q_ab, Q_ac, Q_bc)`

using the same cumulative response construction already frozen in Experiments 017–018.

The probabilistic model receives only:

- the current three-vector `Q_r`;
- the pre-intervention diagnostic-noise estimate from t=181..200;
- the known cumulative amplitude geometry through that stage.

It does not receive the simulator family label, corruption magnitude, true gain, or response-topology label.

## Generative structural model

For a unique response-topology hypothesis H_e, where e is one of ab/ac/bc, the model assumes

`Q_r = beta * u_e + epsilon`,

where `u_e` is the unit vector selecting the candidate reciprocal edge, `beta >= 0` is an unknown nonnegative evidence amplitude, and `epsilon ~ N(0, Sigma_r)`.

`Sigma_r` is fixed analytically from the pre-intervention noise estimate and the known block/cumulative weighting geometry. The same scalar-noise approximation must be used for every hypothesis.

The nuisance amplitude beta is integrated out under the frozen half-normal prior

`beta ~ HalfNormal(scale = BETA_SCALE)`.

`BETA_SCALE = 0.20`, the known maximum single-round diagnostic response amplitude at gain 1.0. It is not fitted to Experiment-027 outcomes.

For `H_null`, use the zero-mean model

`Q_r = epsilon`.

The four structural priors are fixed uniformly at 0.25 each.

## Analytic variance approximation

Let the completed round amplitudes be `a_1,...,a_r`, let `A2 = sum(a_k^2)`, and `A1 = sum(a_k)`. For each directed cumulative response statistic, the scalar variance approximation is frozen as

`sigma_C^2 = sigma_hat^2 * [1/5 + (A1^2 / A2)/20]`,

where `sigma_hat` is estimated only from probe observations at t=181..200.

The reciprocal `Q` statistics are treated with this same scalar variance as a deliberate Gaussian approximation. Experiment 027 tests whether that approximation is calibrated; it may fail.

## Posterior computation

At every stage, compute normalized log marginal likelihoods for all four hypotheses and return posterior probabilities summing to one.

For a candidate edge coordinate, integrating a Gaussian observation over the half-normal beta prior yields the frozen skew-normal marginal implied by `BETA_SCALE` and `sigma_C`. The two noncandidate coordinates retain zero-mean Gaussian likelihoods. `H_null` uses three zero-mean Gaussian coordinates.

No posterior-temperature fitting, isotonic regression, Platt scaling, or other outcome-driven probability correction is permitted in Experiment 027.

## Sequential aspect

Posterior probabilities are recorded after rounds 1, 2, 3, 4, and 5.

Experiment 027 does not alter when probes are executed. For this model-validity study, all five symmetric diagnostic rounds are generated for every seed so posterior calibration can be evaluated stage-by-stage independently of any posterior decision.

## Evaluation cells

Use a focused frontier matrix drawn prospectively from the Phase-I synthesis:

- gain 0.50 × noise {1.00, 1.25, 1.50, 2.00}
- gain 0.425 × noise {1.00, 1.50, 2.00}
- gain 0.35 × noise {1.00, 1.50, 2.00}

for drift-ab-fault magnitude 0.50.

Add controls:

- healthy;
- genuine drift magnitude 0.50;
- common-mode magnitude 0.50;
- primary fault magnitude 0.50;
- coherent all-auxiliary corruption magnitude 0.50.

Total: 15 frozen cells.

For every ordinary cell, the simulator's diagnostic response topology is `H_ab`; this includes healthy, genuine-drift, common-mode, and primary-fault controls because the active-probe physical grouping remains `a/b | c`.

The coherent all-auxiliary corruption cell is retained as an epistemic stress case. Although the probe response topology is still physically `a/b | c`, no unique 2+1 provenance partition is operationally sufficient to identify truth in that corruption regime. Its posterior is therefore reported descriptively and is not used to claim operational provenance correctness.

## Seeds

Use 1,000 fresh evaluation seeds per cell:

`27000..27999`.

No Experiment-027 evaluation seed may overlap Phase-I evaluation or calibration seeds.

Audit seeds: `27000..27004`.

## Primary calibration metrics

For each stage and ordinary cell report:

1. multiclass Brier score using `H_ab` as the response-topology truth;
2. multiclass log loss;
3. top-class accuracy;
4. expected calibration error using ten fixed confidence bins [0,.1),...,[.9,1.0];
5. reliability table: count, mean stated confidence, empirical top-class correctness for each fixed bin;
6. posterior assigned to the true `H_ab` response topology;
7. posterior assigned to `H_null` as a measure of insufficient-evidence probability.

The coherent all-auxiliary corruption cell is evaluated separately as an epistemic stress case; the report must expose posterior entropy and maximum posterior without treating the response-topology posterior as proof that the operational provenance problem is solved.

## Frozen success criteria

H1 — finite/proper probabilities:
Every posterior is finite, nonnegative, and sums to one within 1e-10.

H2 — calibration at the key moderate frontier:
At gain 0.50/noise 1.50, final-stage ECE <= 0.05 and multiclass Brier score <= 0.12.

H3 — calibration under mild shift:
At gain 0.50/noise 1.25 and gain 0.425/noise 1.00, final-stage ECE <= 0.04.

H4 — monotone information value:
For each gain=0.50 noise cell, mean posterior probability assigned to the true `H_ab` must not decrease by more than 0.02 from stage 3 to the final stage.

H5 — uncertainty tracks the Phase-I frontier:
At the final stage, mean maximum posterior at gain 0.35/noise 2.00 must be at least 0.10 lower than at gain 0.50/noise 1.00.

H6 — control topology calibration:
For healthy, genuine-drift, common-mode, and primary-fault controls, final-stage top-class accuracy for `H_ab` >= 0.95 and mean `P(H_ab)` >= 0.90. This is a response-topology claim only, not a claim that a fault is present.

H7 — coherent-all-auxiliary boundary honesty:
The all-auxiliary coherent-corruption cell must be reported without treating the `H_ab` response-topology posterior as proof of correct operational provenance. The report must expose posterior entropy, maximum posterior, and an explicit `operational_truth_unresolved=true` marker.

H8 — no hidden retuning:
The report must record the fixed prior, `BETA_SCALE=0.20`, analytic variance formula, seed range, and exact code commit. No parameter may depend on Experiment-027 evaluation outcomes.

## Interpretation rule

Experiment 027 succeeds only as a probability-model validation if H1–H8 all pass.

If calibration fails, do not proceed to Bayes-policy optimization on these probabilities. The next phase decision must instead address the model assumption causing miscalibration.

If calibration succeeds, Experiment 028 may prospectively test a sequential Bayes-risk decision policy using the frozen Experiment-027 posterior model together with a separate fault/adaptation state model.
