# Experiment 027 — Sequential Probabilistic Identifiability Calibration

## Status

Prospectively frozen before any Experiment-027 calibration or evaluation outcomes are generated.

This is the first experiment in Phase II. It is a model-validity study, not a policy-optimization study.

## Scientific question

Can a frozen sequential probabilistic model over the four structural hypotheses `H_ab`, `H_ac`, `H_bc`, and `H_null` produce calibrated provenance probabilities across the operating regions where Experiments 016–026 exposed a safety–coverage frontier?

## Fixed evidence representation

Experiment 027 reuses the existing diagnostic schedule through round 5 without changing probe amplitude, target order, timing, or sensing assumptions.

At each completed diagnostic stage r, form the three reciprocal cumulative edge scores

`Q_r = (Q_ab, Q_ac, Q_bc)`

using the same cumulative response construction already frozen in Experiments 017–021.

The probabilistic model receives only:

- the current three-vector `Q_r`;
- the pre-intervention diagnostic-noise estimate from t=181..200;
- the known cumulative amplitude geometry through that stage.

It does not receive the simulator family label, corruption magnitude, true gain, or true partition.

## Generative structural model

For a unique 2+1 provenance hypothesis H_e, where e is one of ab/ac/bc, the model assumes

`Q_r = beta * u_e + epsilon`,

where `u_e` is the unit vector selecting the candidate reciprocal edge, `beta >= 0` is an unknown nonnegative evidence amplitude, and `epsilon ~ N(0, Sigma_r)`.

`Sigma_r` is fixed analytically from the pre-intervention noise estimate and the known block/cumulative weighting geometry. The same scalar-noise approximation must be used for every hypothesis.

The nuisance amplitude beta is integrated out under the frozen half-normal prior

`beta ~ HalfNormal(scale = BETA_SCALE)`.

`BETA_SCALE` is derived once from the known maximum diagnostic response produced by gain 1.0 and amplitude 0.20; it is not fitted to Experiment-027 outcomes.

For `H_null`, use the zero-mean model

`Q_r = epsilon`.

The four structural priors are fixed uniformly at 0.25 each.

## Posterior computation

At every stage, compute normalized log marginal likelihoods for all four hypotheses and return posterior probabilities summing to one.

No posterior-temperature fitting, isotonic regression, Platt scaling, or other outcome-driven probability correction is permitted in Experiment 027.

## Sequential aspect

Posterior probabilities are recorded after rounds 1, 2, 3, 4, and 5 whenever those stages exist in the inherited diagnostic path.

Experiment 027 does not alter when probes are executed. For this model-validity study, the full preregistered evidence path needed for posterior evaluation is generated independently of any posterior decision.

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

## Seeds

Use 1,000 fresh evaluation seeds per cell:

`27000..27999`.

No Experiment-027 evaluation seed may overlap Phase-I evaluation or calibration seeds.

Audit seeds: `27000..27004`.

## Primary calibration metrics

For each stage and cell report:

1. multiclass Brier score;
2. multiclass log loss;
3. top-class accuracy;
4. expected calibration error using ten fixed confidence bins [0,.1),...,[.9,1.0];
5. reliability table: count, mean stated confidence, empirical correctness for each fixed bin;
6. posterior assigned to the true structural hypothesis when a unique structural truth exists;
7. posterior assigned to `H_null` for healthy and non-provenance controls.

The coherent all-auxiliary corruption cell is evaluated separately as an epistemic stress case; no unique structural hypothesis is labeled correct there.

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
At the final stage, mean maximum structural posterior at gain 0.35/noise 2.00 must be at least 0.10 lower than at gain 0.50/noise 1.00.

H6 — null discrimination:
For healthy, common-mode, and primary-fault controls, mean final posterior `P(H_null)` >= 0.80 and fewer than 2% of seeds may assign >0.90 posterior to any unique 2+1 structural hypothesis.

H7 — coherent-all-auxiliary boundary honesty:
The all-auxiliary coherent-corruption cell must be reported without treating any unique structural posterior as truth. The report must expose posterior entropy and maximum posterior rather than relabeling this case as solved.

H8 — no hidden retuning:
The report must record the fixed prior, beta prior scale, analytic variance formula, seed range, and exact code commit. No parameter may depend on Experiment-027 evaluation outcomes.

## Interpretation rule

Experiment 027 succeeds only as a probability-model validation if H1–H8 all pass.

If calibration fails, do not proceed to Bayes-policy optimization on these probabilities. The next phase decision must instead address the model assumption causing miscalibration.

If calibration succeeds, Experiment 028 may prospectively test a sequential Bayes-risk decision policy using the frozen Experiment-027 posterior model.
