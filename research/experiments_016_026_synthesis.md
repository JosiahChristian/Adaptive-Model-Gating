# Experiments 016–026 Synthesis

## Status

This document closes the current Adaptive-Model-Gating provenance-policy optimization phase. Experiment 026 is the high-powered characterization study that determines how the earlier mechanism results should be interpreted.

Experiment 026 used 1,000 fresh seeds per critical cell, five frozen strategies, no recalibration, and one-sided 95% Wilson upper bounds on wrong acceptance. The frozen safety-support rule was an upper bound <= 0.01; utility at the key moderate-information cells required coverage >= 0.85.

## High-powered conclusions

- At gain 0.50 with nominal or mild observation noise (noise scale <= 1.25), the Experiment-021 qualification-aware early-targeted policy is jointly supported. At gain 0.50/noise 1.00, coverage was 0.992 with 0 wrong acceptances in 1,000 seeds and mean diagnostic energy 0.632475. At gain 0.50/noise 1.25, coverage was 0.966 with 1 wrong acceptance; the one-sided 95% Wilson upper bound was 0.004470.
- At gain 0.425/noise 1.00, Experiments 021, 023, and 025 are jointly supported. Experiment 021 and Experiment 025 each reached coverage 0.950 with 0 wrong acceptances in 1,000 seeds.
- At gain 0.50/noise 1.50, no evaluated policy is jointly supported. Experiment 021 preserves high coverage (0.928) but has 5 wrong acceptances in 1,000 seeds, giving a one-sided 95% Wilson upper bound of 0.010235, just outside the frozen safety criterion. Experiment 023, Experiment 024, and Experiment 025 satisfy the safety bound but reach coverage only 0.726, 0.548, and 0.763 respectively.
- At gain 0.425/noise 1.50, no evaluated policy is jointly supported. Experiment 021 reaches coverage 0.821 but fails the safety bound; the more conservative policies satisfy the safety bound but cover only 0.521, 0.362, and 0.555.
- At gain 0.35, the provenance problem becomes utility-limited even under nominal noise. At gain 0.35/noise 1.00 the highest observed coverage is 0.790. Under noise 1.50 and 2.00, the more permissive Experiment-021 policy increasingly violates the risk bound, while conservative policies remain safer but have low coverage.
- At gain 0.35/noise 2.00, Experiment 021 produced 37 wrong acceptances in 1,000 seeds (wrong-acceptance rate 0.037; one-sided 95% Wilson upper bound 0.04813), marking a clear unsupported region for that policy.

## Mechanistic interpretation

Experiments 017–021 established that cumulative evidence, selective abstention, confirmatory probing, targeted confirmation, and qualification-aware dispatch can recover provenance efficiently when diagnostic identifiability is adequate. Experiments 022–025 then showed that observation-noise shift exposes a safety–coverage tradeoff: stricter uncertainty handling reduces false acceptance but loses useful coverage, while additional same-amplitude evidence recovers some coverage but does not remove the frontier.

Experiment 026 demonstrates that earlier 0/200 wrong-error observations were not evidence of a literally zero-error policy. Samples of 200 were appropriate for mechanism discovery, but rare-error claims require higher-powered replication and explicit uncertainty bounds.

## Research claim boundary

The current evidence supports an operating-region claim, not a universal-policy claim:

> Qualification-aware targeted provenance gating can provide high-coverage, low-energy, safety-supported adaptation when diagnostic gain is moderate and observation noise is nominal to mildly elevated; outside that identifiable region, the system must trade coverage for safety and should abstain to the inherited persistence fallback.

Coherent corruption of all auxiliary channels remains an unresolved epistemic boundary. It must not be represented as solved provenance recovery.

## Stopping rule

Do not continue this phase by tuning thresholds, adding incremental probe rounds, or selecting a post-hoc winner on the existing benchmark. Experiments 016–026 have already characterized the empirical safety–coverage–energy frontier.

A future research phase should introduce a genuinely new source of information or theory, such as calibrated posterior risk, sequential decision theory, formal identifiability bounds, or additional independent sensing. That phase should be preregistered independently from this optimization sequence.

## Provenance

Experiment 026 completed in Actions run 32425453463 at request head `9631b6e6c217b75afd59ec1a9dd78b92aed536c8`. Evidence artifact SHA-256: `312d05199ae211cdfc4927dbba5fc4975d57d855283556d890de5fbab620857e`.
