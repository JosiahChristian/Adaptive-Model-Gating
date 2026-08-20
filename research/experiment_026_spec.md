# Experiment 026 — High-Power Rare-Error and Coverage Frontier Characterization

## Status
Prospectively frozen before any Experiment 026 outcome generation.

## Motivation
Experiments 022–025 established that apparent zero-error behavior at n=200 is not stable enough to treat as a literal zero-error property. Experiment 025, using fresh seeds, observed rare wrong acceptances in the low-noise branch inherited exactly from Experiment 021, while conditional round-6 confirmation improved high-noise coverage without reaching the preregistered utility target. The correct next step is estimation, not another policy modification.

## Scientific question
Across the critical gain/noise boundary, what are the high-powered empirical wrong-acceptance, coverage, precision, abstention, and diagnostic-energy profiles of the frozen Experiment-021, Experiment-023, Experiment-024, and Experiment-025 policies?

## Policies
No policy may be modified, recalibrated, or retuned in Experiment 026. Evaluate exactly these frozen strategies:

1. `qualification_aware_early_targeted_replicated_selective_cumulative_provenance_quorum` (Experiment 021)
2. `noise_aware_qualification_aware_early_targeted_replicated_selective_cumulative_provenance_quorum` (Experiment 023)
3. `uncertainty_aware_margin_qualification_aware_early_targeted_replicated_selective_cumulative_provenance_quorum` (Experiment 024)
4. `conditional_high_noise_replicated_confirmation_qualification_aware_provenance_quorum` (Experiment 025)
5. `triad_persistence` fallback comparator

All inherited calibrations, intervention amplitudes, diagnostic block schedules, selectors, confidence rules, noise trigger, round-6 logic, and fallback semantics are frozen exactly as previously implemented.

## Fresh evaluation seeds
- Evaluation seeds: `26000..26999` inclusive (1,000 seeds per cell).
- Audit seeds: `26000..26004` inclusive.
- No Experiment 026 seed may overlap prior evaluation or calibration ranges.

## Frozen cells
Ten cells are selected prospectively to characterize the empirically relevant frontier without a post-hoc combinatorial search:

1. `healthy_0.00`
2. `drift_0.50`
3. `g0.500_n1.00_0.50`
4. `g0.500_n1.25_0.50`
5. `g0.500_n1.50_0.50`
6. `g0.425_n1.00_0.50`
7. `g0.425_n1.50_0.50`
8. `g0.350_n1.00_0.50`
9. `g0.350_n1.50_0.50`
10. `g0.350_n2.00_0.50`

The gain/noise cells use the same frozen stress construction introduced in Experiments 022–025. No new stress realization is introduced.

## Primary estimands
For each strategy × cell:
- provenance coverage
- provenance abstention
- accepted-decision precision
- wrong-acceptance rate (wrong accepted decisions divided by all seeds)
- mean probe energy
- post-event operational adaptation rate
- mean operational loss over t=401..600

For wrong-acceptance rate, report the one-sided 95% Wilson upper confidence bound (WUCB). For coverage, report the two-sided 95% Wilson interval.

## Prospective interpretation rules
Experiment 026 is primarily an estimation study, not a mechanism pass/fail experiment. Nevertheless, the following deployment-relevance labels are frozen prospectively:

### Safety-supported cell
A strategy-cell is `safety_supported` iff the one-sided 95% Wilson upper confidence bound for wrong acceptance is <= 0.01.

### Utility-supported moderate-information cell
For gain >= 0.425, a strategy-cell is `utility_supported` iff coverage >= 0.85.

### Jointly supported cell
A moderate-information strategy-cell is `jointly_supported` iff both `safety_supported` and `utility_supported` are true.

### Low-information conservatism
For gain = 0.35 and noise >= 1.50, record whether adaptation rate exceeds `triad_persistence` by more than 0.02. This is descriptive boundary evidence and must not be optimized after observation.

## Primary questions
Q1. On nominal/moderate-noise gain=0.50 and gain=0.425 cells, does Experiment 021 remain safety-supported at n=1,000, or were its earlier near-perfect results finite-sample optimism?

Q2. At gain=0.50/noise=1.50, which of Experiments 023–025 lies on the empirical safety/coverage/energy Pareto frontier?

Q3. Does Experiment 025's conditional round-6 path provide a reproducible coverage gain over Experiment 024 while remaining safety-supported?

Q4. At gain=0.35, does any provenance policy remain jointly useful under increasing observation noise, or does the evidence support conservative fallback as the defensible boundary?

## Falsification / anti-overclaiming rules
- Zero observed wrong acceptances must never be described as proof of zero true error.
- Claims about low error must reference the frozen Wilson upper bound.
- No policy threshold, trigger, amplitude, selector, or block schedule may be changed based on Experiment 026 outcomes.
- If no single strategy dominates the safety/coverage/energy frontier, the result must be reported as a tradeoff frontier rather than selecting a winner post hoc.
- The coherent-all-auxiliary corruption boundary remains unsolved unless directly tested and supported; Experiment 026 does not redefine that boundary.

## Workload
- 10 cells × 5 strategies × 1,000 seeds = 50,000 seed-strategy summaries.
- Audit traces only for the five frozen audit seeds: 10 × 5 × 5 × 900 = 225,000 audit rows.
- Use disk-backed audit writing and streaming merge.

## Completion contract
The Experiment 026 report must contain all cell/strategy counts, Wilson intervals/bounds, frozen interpretation labels, exact seed ranges, strategy names, row-count assertions, and artifact provenance. Completion registration must remain bounded and point to the full evidence artifact.