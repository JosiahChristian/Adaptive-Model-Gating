# Experiment 031 — Operational Context Sufficiency Validation

## Status

Prospectively frozen before any Experiment-031 evaluation outcome is generated.

Experiment 030 established, on 1,000 fresh paired seeds per cell, that calibrated topology confidence is not sufficient for operational action choice: the Experiment-029 provenance veto is neutral/non-regressive in supported drift/fault contexts but harmful under common-mode corruption despite essentially identical topology confidence.

Experiment 031 is a context-model validation study. It does not modify the Experiment-028 posterior, the Experiment-029 0.99 topology-risk threshold, the diagnostic probe schedule, or any operational policy.

## Scientific question

Can the already-existing independent-anchor geometry provide an outcome-independent observable signal that distinguishes common-mode input corruption from supported drift/provenance-fault contexts before action composition?

## Frozen context statistic

Use only pre-action operational diagnostics already defined in Experiment 013:

- anchor mismatch indicators `m_a,m_b,m_c` from the frozen healthy-calibrated anchor thresholds;
- anchor-pair disagreement indicators `d_ab,d_ac,d_bc` from the frozen healthy-calibrated pair thresholds;
- triad-consistency indicator from the frozen Experiment-010 threshold.

For each seed, evaluate the fixed window t=401..420 and define per-time-step

`broad_anchor_mismatch = 1[m_a + m_b + m_c >= 2]`

`anchor_consensus = 1[d_ab + d_ac + d_bc == 0]`

`common_mode_context_vote = triad_consistent * broad_anchor_mismatch * anchor_consensus`.

The seed-level context score is the fraction of t=401..420 time steps with `common_mode_context_vote=1`.

The binary context call is prospectively fixed as

`common_mode_context = 1[score >= 0.50]`.

The 0.50 majority rule is structural and is not fitted to Experiment-030 or Experiment-031 outcomes.

## Critical prohibition

No Experiment-031 family label, simulator latent variable, future operational loss, topology posterior, or action result may enter the context statistic. Family labels are evaluator-only truth labels.

No threshold calibration, logistic regression, decision tree, posterior fitting, temperature scaling, or post-hoc feature selection is permitted.

## Evaluation cells

Use seven frozen contexts:

- healthy;
- genuine drift magnitude 0.50;
- primary fault magnitude 0.50;
- common-mode magnitude 0.25;
- common-mode magnitude 0.50;
- common-mode magnitude 1.00;
- drift-ab-fault magnitude 0.50 at gain=0.50/noise=1.00.

For the drift-ab-fault cell, use the same stressed-stream construction as Experiments 022–030.

## Seeds

Use 1,000 fresh evaluation seeds per cell:

`31000..31999`.

Audit seeds: `31000..31004`.

No seed overlaps Experiments 027–030 or Phase I.

## Primary metrics

Report per cell:

- mean context score;
- median context score;
- binary common-mode-call rate;
- 95% Wilson interval for the call rate;
- distributions of broad-anchor-mismatch fraction, anchor-consensus fraction, and triad-consistency fraction.

For common-mode cells, the binary call is a positive prediction. For healthy, drift, primary-fault, and supported drift-ab-fault, it is a false positive.

Also report a pooled context classification table over the seven frozen cells and the fixed t=401..420 window.

## Frozen success criteria

H1 — implementation integrity:
Every context score is in [0,1], uses exactly 20 time steps (401..420), and the binary call equals `score >= 0.50` exactly.

H2 — common-mode sensitivity:
At common-mode magnitude 0.50 and 1.00, binary context-call rate >=0.90 in each cell.

H3 — low-magnitude sensitivity:
At common-mode magnitude 0.25, binary context-call rate >=0.70.

H4 — supported drift/fault specificity:
At drift-ab-fault gain=0.50/noise=1.00, false common-mode-call rate <=0.05.

H5 — genuine-drift specificity:
At genuine drift magnitude 0.50, false common-mode-call rate <=0.05.

H6 — healthy specificity:
At healthy, false common-mode-call rate <=0.05.

H7 — primary-fault specificity:
At primary fault magnitude 0.50, false common-mode-call rate <=0.10.

H8 — geometric separation:
Mean context score at common-mode magnitude 0.50 must exceed the supported drift-ab-fault mean context score by at least 0.50.

H9 — no hidden fitting:
The report must record the exact statistic, 0.50 majority threshold, frozen inherited calibration values, seed range, and exact code commit. No quantity may depend on Experiment-031 outcomes.

## Interpretation rule

Experiment 031 validates the operational-context signal only if H1-H9 all pass.

If it succeeds, Experiment 032 may prospectively compose the validated context call with the frozen Experiment-029 topology-risk rule and test whether context-aware veto composition removes the common-mode regression without sacrificing supported-frontier safety/utility.

If it fails, do not tune the 0.50 threshold post hoc. The next study must address which observable operational-state information is missing.