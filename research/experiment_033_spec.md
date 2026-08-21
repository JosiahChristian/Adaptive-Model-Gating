# Experiment 033 — Frozen Two-State OOD Deployment Generalization

## Status
Prospectively frozen before any Experiment-033 outcomes are generated.

Experiment 032 validated the causal two-state architecture: the Experiment-028 directed-covariance topology posterior, Experiment-029 0.99 topology-risk rule, and Experiment-031 current-time operational-context vote composed without loss of frontier safety/utility and repaired common-mode regression. Experiment 033 is a generalization study only. It introduces no controller, posterior, threshold, context, probe, fallback, or calibration change.

## Scientific question
Does the fully frozen Experiment-032 two-state controller preserve calibrated topology safety and operational non-regression under new combinations of diagnostic attenuation, observation noise, event timing, asymmetric auxiliary corruption, and mixed common-mode nuisance that were not used to validate Experiment 032?

## Frozen controller
Use Experiment 032 exactly:
- Experiment-028 directed-covariance posterior unchanged;
- Experiment-029 wrong-action cost 100, fallback cost 1, acceptance threshold 0.99 unchanged;
- symmetric diagnostic rounds 1..5 unchanged;
- Experiment-031 current-time context vote unchanged;
- Experiment-032 rule that context may only remove the additional provenance-specific suspect veto unchanged;
- inherited triad primary-fault veto unchanged;
- exact triad persistence fallback on topology abstention unchanged.

No recalibration, new threshold, smoothing, persistence, fitted classifier, family label, or outcome-dependent selection is permitted.

## Comparators
On the identical stressed stream for every seed/cell:
1. Experiment-032 causal composed controller;
2. Experiment-029 posterior-risk gate;
3. triad_persistence.

## Frozen OOD matrix
All ordinary drift/fault cells use drift magnitude 0.50.

### A. New gain × noise combinations (12)
- gain {0.475, 0.45, 0.40, 0.375} × noise {1.10, 1.40};
- additional boundary cells: (0.45,1.75), (0.40,1.75), (0.35,1.25), (0.30,1.25).

### B. Timing × noise combinations (6)
- onset offset {-35,+35,+75} × noise {1.00,1.50}, gain 0.50.

### C. Asymmetric corruption × noise combinations (6)
- auxiliary fault scales {(0.75,1.25), (0.50,1.00), (1.00,1.75)} × noise {1.00,1.50}, gain 0.50.

### D. Mixed drift/common-mode + noise (3)
- drift magnitude 0.50 with common-mode magnitude {0.25,0.50,0.75}, diagnostic noise scale 1.25.

### E. New common-mode magnitudes (3)
- common-mode magnitude {0.15,0.75,1.25}.

Total: 30 frozen cells.

## Seeds
Use 500 fresh seeds per cell: `33000..33499`.
Audit seeds: `33000..33004`.
Bootstrap seed: `33033`; 10,000 resamples where paired intervals are reported.

## Primary summaries
For every cell/strategy report coverage, accepted precision, wrong acceptance, one-sided 95% Wilson upper bound, diagnostic stop round/energy, operational loss t=401..600, final slope error, adaptation signature, context-vote burden, direct context interventions, and exact fallback mismatches.

## Frozen success criteria
H1 — topology-layer identity: Experiment 033 composed controller must exactly match Experiment 029 on accept/abstain, deployed topology, stop round, posterior at deployment, and diagnostic energy for every seed/cell.

H2 — topology safety: in every one of the 30 cells, the Experiment-033 one-sided 95% Wilson upper bound on wrong acceptance must be <=0.01.

H3 — moderate combined-shift utility: for gain in {0.475,0.45} with noise in {1.10,1.40}, coverage >=0.90 and accepted precision >=0.99.

H4 — timing robustness: at noise 1.00 for all three timing offsets, coverage >=0.90 and precision >=0.99. At noise 1.50 for offsets -35 and +35, coverage >=0.80 and precision >=0.99. The +75/noise1.50 cell is safety-characterization only.

H5 — asymmetric-corruption robustness: at noise 1.00 all asymmetric cells require coverage >=0.85 and precision >=0.99; at noise 1.50 require coverage >=0.75 and precision >=0.99.

H6 — common-mode operational repair generalizes: at magnitudes 0.15, 0.75, and 1.25, Experiment 033 mean excess operational loss versus triad must be <=0.25, <=2.0, and <=50.0 respectively; whenever Experiment 029 excess is positive, Experiment 033 must reduce it by at least 80%.

H7 — non-common-mode OOD non-regression: across gain/noise, timing/noise, and asymmetric/noise cells, Experiment-033 mean operational loss may not exceed Experiment 029 by more than 0.05.

H8 — mixed-nuisance boundedness: in each mixed drift/common-mode/noise cell, Experiment 033 may not exceed triad persistence by more than 10.0 mean operational-loss units and may not exceed Experiment 029 by more than 0.05 when Experiment 029 is already better than triad. Mixed cells are explicitly characterization of interaction, not a claim of universal dominance.

H9 — causal and inherited-veto integrity: every direct context-mediated suspect-veto removal must have same-time context_vote_t=1, original suspect active, effective suspect removed, no triad primary-fault veto, and adaptation enabled; no Experiment-033 adaptation may occur when the inherited primary-fault veto is active.

H10 — exact fallback: for every topology-abstaining seed, Experiment 033 adaptation signature and operational loss must match triad_persistence exactly.

H11 — frozen provenance: report must record the 0.99 threshold / 100:1 loss ratio, exact context-vote formula, seed range, bootstrap seed, Experiment-032 composition identity, and code commit. No quantity may depend on Experiment-033 outcomes.

## Interpretation rule
Experiment 033 supports broader OOD deployment generalization only if H1-H11 all pass. If any criterion fails, preserve the frozen controller and treat the failing stress family as an empirical deployment boundary; do not retune Experiment 032 from Experiment-033 outcomes.
