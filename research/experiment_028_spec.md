# Experiment 028 — Directed-Response Covariance Calibration

## Status

Prospectively frozen before any Experiment-028 evaluation outcomes are generated.

Experiment 027 failed its calibration gate (H2/H3) while preserving probability validity, information ordering, and boundary honesty. Experiment 028 addresses the specific likelihood misspecification identified prospectively from that failure. It is still a model-validity experiment; no Bayes-risk control policy is permitted yet.

## Scientific question

Does replacing the non-Gaussian reciprocal minimum statistic and diagonal covariance approximation with the six directed cumulative responses and their analytic shared-baseline covariance produce calibrated topology probabilities across the Phase-I frontier?

## Frozen hypotheses

The four topology hypotheses remain exactly:

- `H_ab`
- `H_ac`
- `H_bc`
- `H_null`

For ordinary simulator cells, the diagnostic response topology is `H_ab`. `H_null` means insufficient/no unique directed topology evidence; it is not a fault/no-fault label. Coherent all-auxiliary corruption remains an operationally unresolved stress case and is not scored as a solved provenance truth.

Uniform prior probability 0.25 is retained for all four hypotheses.

## Evidence representation

At each stage r=1..5, use the six directed cumulative responses

`Y_r = (C_ab, C_ac, C_ba, C_bc, C_ca, C_cb)`.

No `min(C_ij,C_ji)` transformation is used by the new model.

The directed cumulative responses use the same inherited probe schedule and amplitude weights as Experiment 027. No probe timing, amplitude, target order, gain, or sensing assumption changes.

## Analytic covariance

Let completed-stage amplitudes be `a_1..a_r`, let

- `S1 = sum a_k`
- `S2 = sum a_k^2`
- `sigma_hat` be the pre-intervention diagnostic-noise estimate from t=181..200.

Each directed cumulative response has variance

`v_r = sigma_hat^2 * [1/5 + S1^2/(20*S2)]`.

Two directed cumulative responses sharing the same observed channel but using different targets share the same baseline estimate and therefore have covariance

`c_r = sigma_hat^2 * S1^2/(20*S2)`.

Responses from different observed channels have covariance zero under the frozen simulator noise model.

Thus `Sigma_r` is block diagonal with three identical 2x2 blocks `[[v_r,c_r],[c_r,v_r]]`, using observation-channel blocks `(C_ab,C_ac)`, `(C_ba,C_bc)`, `(C_ca,C_cb)`.

No empirical covariance estimate from Experiment-027 or Experiment-028 outcomes is permitted.

## Structural means and beta prior

For topology `H_ab`, the mean direction has unit entries at `C_ab` and `C_ba`, zero elsewhere. `H_ac` uses `C_ac,C_ca`; `H_bc` uses `C_bc,C_cb`.

For a unique topology H_e,

`Y_r | beta,H_e ~ N(beta*u_e, Sigma_r)`, with `beta >= 0`.

Retain the Experiment-027 prior exactly:

`beta ~ HalfNormal(scale=0.20)`.

For `H_null`, `Y_r ~ N(0,Sigma_r)`.

The half-normal nuisance amplitude must be marginalized analytically. No numerical parameter fitting to evaluation outcomes is allowed.

## Frozen comparator

On every Experiment-028 seed/cell/stage, also compute the unchanged Experiment-027 Q-based posterior. This is a comparator only. It may not be altered, temperature-scaled, or recalibrated.

## Evaluation matrix

Use exactly the same 15 conceptual cells as Experiment 027:

- gain 0.50 × noise {1.00,1.25,1.50,2.00}
- gain 0.425 × noise {1.00,1.50,2.00}
- gain 0.35 × noise {1.00,1.50,2.00}
- healthy
- genuine drift magnitude 0.50
- common-mode magnitude 0.50
- primary fault magnitude 0.50
- coherent all-auxiliary corruption magnitude 0.50

Use 1,000 fresh seeds per cell: `28000..28999`.

Audit seeds: `28000..28004`.

No Experiment-028 evaluation seed overlaps Experiment 027 or Phase I.

## Metrics

For both the new directed-covariance posterior and frozen Experiment-027 comparator, report per cell/stage:

- multiclass Brier score;
- multiclass log loss;
- top-class accuracy;
- fixed-bin ten-bin ECE;
- reliability table;
- mean true-topology posterior for ordinary cells;
- mean maximum posterior and entropy;
- `P(H_null)` diagnostics;
- finite/proper probability checks.

The all-auxiliary coherent-corruption case reports entropy and maximum posterior only as an epistemic stress case.

## Frozen success criteria

H1 — proper probabilities:
Every new posterior is finite, nonnegative, and sums to one within 1e-10.

H2 — key-frontier calibration:
At gain=0.50/noise=1.50, final-stage new-model ECE <=0.05 and Brier <=0.12.

H3 — mild-shift calibration:
At gain=0.50/noise=1.25 and gain=0.425/noise=1.00, final-stage new-model ECE <=0.04 in both cells.

H4 — prospective improvement over the frozen Experiment-027 likelihood:
At gain=0.50/noise=1.50 on the same Experiment-028 seeds, new-model final ECE must be at least 0.02 lower than the frozen Experiment-027 comparator ECE, without Brier worsening by more than 0.01.

H5 — nominal non-regression:
At gain=0.50/noise=1.00, new-model final Brier <=0.03, ECE <=0.03, and top-class accuracy >=0.98.

H6 — sequential information behavior:
For each gain=0.50 noise cell, mean posterior on true `H_ab` must not decrease by more than 0.02 from stage 3 to stage 5.

H7 — frontier uncertainty:
Final mean maximum posterior at gain=0.35/noise=2.00 must be at least 0.10 lower than at gain=0.50/noise=1.00.

H8 — boundary honesty:
The coherent all-auxiliary cell is reported without declaring a unique topology operationally solved; entropy and maximum posterior must be exposed.

H9 — no hidden fitting:
The report must record the uniform prior, beta scale, analytic covariance formulas, exact seed range, and exact code commit. No model parameter may depend on Experiment-027/028 evaluation outcomes.

## Interpretation rule

Experiment 028 validates the directed-covariance probability model only if H1-H9 all pass.

If it succeeds, Experiment 029 may prospectively test a sequential Bayes-risk decision policy using the frozen Experiment-028 posterior.

If it fails, do not optimize a decision rule on these probabilities. The next experiment must address the remaining generative-model misspecification or formally conclude that the current Gaussian topology family is inadequate.
