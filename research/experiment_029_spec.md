# Experiment 029 — Sequential Posterior-Risk Deployment

## Status

Prospectively frozen before any Experiment-029 evaluation outcome is generated.

Experiment 028 validated the directed-response covariance posterior under all frozen H1–H9 calibration criteria. Experiment 029 is the first Phase-II deployment-policy study. It does not modify or recalibrate the Experiment-028 probability model.

## Scientific question

Can a sequential deployment rule based on the calibrated Experiment-028 posterior convert probability calibration into a safety-supported operating policy while preserving useful provenance coverage and bounded diagnostic burden across the Phase-I frontier?

## Frozen posterior model

Use the Experiment-028 directed-covariance posterior exactly as validated:

- hypotheses: `H_ab`, `H_ac`, `H_bc`, `H_null`;
- uniform prior 0.25 each;
- half-normal evidence-amplitude prior scale 0.20;
- six directed cumulative responses;
- analytic shared-baseline covariance;
- pre-intervention noise estimate only;
- no probability recalibration, temperature, fitted multiplier, or posterior correction.

## Frozen terminal loss

The terminal action loss is fixed prospectively:

- correct unique-topology deployment: 0;
- wrong unique-topology deployment: 100;
- persistence fallback: 1.

For a candidate unique topology with posterior probability `p`, expected deployment loss is `100*(1-p)`. Therefore deployment is permitted only when

`100*(1-p) <= 1`, i.e. `p >= 0.99`.

The 0.99 threshold is derived only from the frozen loss ratio and is not fitted to Experiment-028 or Experiment-029 outcomes.

## Sequential rule

After each symmetric diagnostic stage r=1..5:

1. compute the frozen Experiment-028 posterior;
2. identify the highest-posterior unique topology among `H_ab/H_ac/H_bc`;
3. if its posterior is >=0.99, deploy that topology and stop diagnostics;
4. otherwise, if r<5, execute the next already-frozen symmetric diagnostic round;
5. if stage 5 still does not qualify, abstain and use `triad_persistence` exactly.

`H_null` is never itself deployed as a provenance partition.

No target selection, threshold learning, changed probe amplitude, changed round timing, or added sensing is allowed.

## Comparator policies

Evaluate on the same seed/cell realizations:

1. Experiment-029 sequential posterior-risk policy;
2. frozen Experiment-021 qualification-aware policy;
3. `triad_persistence` fallback.

Experiment 021 is a mechanistic/efficiency comparator, not a source of thresholds for Experiment 029.

## Evaluation matrix

Use the ten critical Phase-I frontier cells:

- gain 0.50 × noise {1.00,1.25,1.50,2.00};
- gain 0.425 × noise {1.00,1.50,2.00};
- gain 0.35 × noise {1.00,1.50,2.00}.

All use `drift_ab_fault`, magnitude 0.50.

Add five controls:

- healthy;
- genuine drift magnitude 0.50;
- common-mode magnitude 0.50;
- primary fault magnitude 0.50;
- coherent all-auxiliary corruption magnitude 0.50.

Total: 15 frozen cells.

## Seeds

Use 1,000 fresh evaluation seeds per cell:

`29000..29999`.

Audit seeds: `29000..29004`.

No seed overlaps Experiments 027–028 or Phase I.

## Primary summaries

For every strategy/cell report:

- provenance deployment coverage;
- wrong-acceptance rate per evaluation seed;
- accepted precision;
- one-sided 95% Wilson upper bound on wrong-acceptance probability;
- diagnostic stop-round distribution;
- mean diagnostic energy;
- operational adaptation rate in t=401..420;
- operational loss in t=401..600;
- final slope error;
- exact fallback-equivalence mismatches for abstained Experiment-029 seeds.

For Experiment 029 additionally report posterior probability at deployment, posterior-implied error risk `1-p`, and whether the fixed 0.99 rule was obeyed exactly.

The all-auxiliary coherent-corruption cell remains an operationally unresolved stress case and must not be counted as a solved provenance truth.

## Frozen success criteria

H1 — decision-rule integrity:
Every Experiment-029 accepted seed must have deployed at the earliest stage whose highest unique-topology posterior is >=0.99. No seed with posterior <0.99 may deploy. Every nonqualified stage-5 seed must abstain.

H2 — safety support across the frontier:
For each of the ten gain/noise frontier cells, the one-sided 95% Wilson upper bound on Experiment-029 wrong acceptance must be <=0.01.

H3 — key-frontier utility:
At gain=0.50/noise=1.50, Experiment-029 deployment coverage must be >=0.85 and accepted precision >=0.99.

H4 — mild-shift utility:
At gain=0.50/noise=1.25, coverage >=0.90; at gain=0.425/noise=1.00, coverage >=0.85. Accepted precision must be >=0.99 in both cells.

H5 — severe-frontier conservatism:
At gain=0.35/noise=2.00, Experiment-029 wrong-acceptance Wilson upper bound <=0.01 and deployment coverage must be at least 0.10 lower than at gain=0.50/noise=1.00.

H6 — bounded burden:
At gain=0.50/noise=1.00 mean diagnostic energy <=0.80; at gain=0.50/noise=1.50 mean diagnostic energy <=1.20. Maximum probe amplitude remains 0.20.

H7 — operational non-regression in supported cells:
At gain=0.50/noise in {1.00,1.25,1.50}, mean operational loss t=401..600 may not exceed `triad_persistence` by more than 0.02, and final slope error may not exceed it by more than 0.02.

H8 — exact fallback:
For every Experiment-029 abstained seed, adaptation signature and operational loss must match `triad_persistence` exactly on the same stressed stream.

H9 — controls and boundary honesty:
Healthy, genuine drift, common-mode, and primary-fault controls must be reported without operational regression relative to `triad_persistence`. Coherent all-auxiliary corruption must remain explicitly labeled operationally unresolved; successful topology inference may not be described as solving that corruption case.

H10 — frozen-model provenance:
The report must record Experiment-028 model constants, loss ratio 100:1, acceptance threshold 0.99, exact seed range, and exact code commit. No quantity may be fitted from Experiment-029 outcomes.

## Interpretation rule

Experiment 029 supports the Phase-II deployment claim only if H1–H10 all pass.

If it passes, the next experiment may test value-of-information / adaptive stopping or a broader OOD deployment study while keeping the posterior and terminal loss frozen.

If it fails, do not change the 0.99 threshold post hoc. Diagnose whether failure comes from residual posterior calibration, insufficient evidence acquisition, or operational mismatch between response topology and safe adaptation.