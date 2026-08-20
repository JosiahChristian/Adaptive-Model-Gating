# Experiment 025 — Conditional High-Noise Replicated Confirmation

Status: **FROZEN BEFORE ANY EXPERIMENT-025 OUTCOMES**

## Motivation
Experiment 022 identified a localized false-positive boundary under 1.50x diagnostic observation noise. Experiment 023 restored safety at the original boundary by globally scaling thresholds but reduced coverage. Experiment 024 restored safety with an uncertainty-aware edge-margin rule but reduced coverage further. Repeated confidence-threshold shaping is therefore not the next intervention. Earlier Experiments 018–019 showed that additional independent evidence can recover coverage without relaxing confidence.

## Frozen policy architecture
Experiment 025 is a conditional information-acquisition extension, not a threshold retuning experiment.

1. Estimate diagnostic noise from the pre-intervention probe baseline t=181..200 using the frozen Experiment-023 estimator.
2. If estimated diagnostic-noise factor <= 1.25, execute the inherited Experiment-021 qualification-aware policy exactly, with no changes.
3. If estimated diagnostic-noise factor > 1.25, execute the frozen Experiment-024 uncertainty-aware margin policy through its existing targeted round 5.
4. If that high-noise path accepts, stop exactly there.
5. If it abstains with a unique leading candidate edge, execute exactly one additional independent targeted confirmation round (round 6) on the two endpoints of that candidate edge. Round 6 uses amplitude 0.200 and two five-sample blocks at t=276..280 and t=281..285. No third-target block is allowed.
6. Combine the candidate edge's cumulative evidence through round 6 using the same amplitude-weighted normalization convention as prior cumulative probes. Competing edge scores remain their inherited latest values. Qualification requires both the inherited raw evidence floor and the frozen Experiment-024 standardized edge-separation criterion Z_MARGIN=2.128045234184984.
7. If round 6 does not qualify, abstain and execute triad_persistence exactly.

No selector ordering, operational gate, fallback rule, raw evidence floor, round-1..5 amplitude, or inherited threshold may be changed. Maximum probe amplitude remains 0.20.

## Primary question
Can one additional independent, same-amplitude targeted confirmation round recover useful high-noise coverage while preserving the zero-wrong-acceptance safety achieved by Experiment 024 and the nominal efficiency of Experiment 021?

## Evaluation
Use fresh seeds 25000..25199. No recalibration and no use of Experiment-025 outcomes for rule changes.

Evaluate 46 cells mirroring Experiment 024: gains 0.50, 0.425, 0.35 crossed with the same noise scales, plus healthy, drift, common-mode, primary-fault, and all-auxiliary negative-control cells. Comparators:
- Experiment-025 conditional replicated-confirmation strategy (primary)
- Experiment-024 uncertainty-aware margin strategy
- Experiment-023 noise-aware strategy
- Experiment-021 qualification-aware strategy
- triad_persistence

## Preregistered criteria
H1 Safety: zero wrong provenance acceptance across all Experiment-025 cells.

H2 High-noise precision: in every noise>=1.50 cell with at least 20 accepted seeds, precision >=0.99.

H3 Original-boundary recovery: at gain=0.50/noise=1.50, Experiment-025 coverage >=0.85 at every magnitude while wrong acceptance remains zero.

H4 Information value: at gain=0.50/noise=1.50, Experiment-025 coverage must exceed Experiment-024 coverage by at least 0.15 absolute and Experiment-023 coverage by at least 0.08 absolute, with zero wrong acceptance.

H5 Nominal exact preservation: for every seed with estimated noise factor <=1.25, Experiment-025 must exactly reproduce Experiment-021 acceptance, gate partition, adaptation signature, operational loss, and probe energy.

H6 Moderate-gain protection: at gain 0.425 and 0.35 with nominal noise, Experiment-025 coverage must be within 0.03 absolute of Experiment-021 and have zero wrong acceptance.

H7 Conditional burden: round 6 may execute only when estimated noise factor >1.25 and the Experiment-024 path would otherwise abstain. At gain=0.50/noise=1.50, mean total probe energy must remain <=1.35.

H8 Low-information conservatism: at gain=0.35 with noise>=1.50, adaptation rate may not exceed triad_persistence by more than 0.02.

H9 Fallback integrity: every final abstention must reproduce triad_persistence adaptation signature and operational loss exactly.

## Negative-control boundary
Coherent all-auxiliary corruption remains outside the identification claim. Failure to recover it is not a failure unless the policy makes a wrong positive provenance acceptance.

## Decision rule
If H1 fails, the added confirmation mechanism is not safe enough. If H1 passes but H3/H4 fail, additional same-amplitude evidence is insufficient to close the high-noise coverage gap and the lane should stop policy optimization and move to synthesis/boundary characterization rather than further threshold tuning. If H1, H3, H4, H5, and H9 pass, the conditional replicated-confirmation mechanism is supported as the final adaptive policy candidate for a synthesis/replication phase.
