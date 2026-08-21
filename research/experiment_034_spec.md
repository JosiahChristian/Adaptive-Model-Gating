# Experiment 034 — Frozen Topology-Permutation Structural Transfer

## Status
Prospectively frozen before any Experiment-034 outcomes are generated.

Experiments 028–033 validated a directed-covariance topology posterior, a 0.99 cost-derived topology-risk decision rule, an independently validated causal operational-context vote, their two-state composition, and broader combined-shift OOD generalization. However, every scientific stream used the same physical diagnostic response topology: `H_ab` (`a/b | c`). Experiment 034 tests structural transfer rather than another nuisance-grid expansion.

## Scientific question
Does the fully frozen Experiment-032 architecture transfer without recalibration when the simulator's true diagnostic response topology is permuted to `H_ac` (`a/c | b`) or `H_bc` (`b/c | a`), including matching coherent auxiliary-fault geometry and operational common-mode contexts?

## Frozen controller
No decision rule changes are permitted. Preserve exactly:
- Experiment-028 directed-covariance posterior and uniform structural prior;
- Experiment-029 wrong-action cost 100, fallback cost 1, acceptance threshold 0.99;
- symmetric diagnostic rounds 1..5 and amplitudes;
- Experiment-031 current-time context vote;
- Experiment-032 context composition;
- inherited triad primary-fault veto;
- exact triad fallback on topology abstention;
- all calibration constants inherited from the pre-Experiment-034 record.

No probability recalibration, threshold change, topology-specific tuning, label-specific prior, fitted classifier, smoothing, or outcome-dependent rule is permitted.

## Structural intervention
For each seed, begin from the same inherited latent/noise realization used by the frozen simulator, then change only structural topology as follows.

### Probe response topology
Reconstruct probe observations from the stored probe-noise draws and the frozen round amplitudes, replacing the historical `H_ab` grouping with the cell's true topology:
- `H_ac`: `{a,c}` respond together and `{b}` is separate;
- `H_bc`: `{b,c}` respond together and `{a}` is separate.
All five symmetric rounds use the permuted topology. Probe gain and noise scale remain those specified by the cell.

### Matching auxiliary-fault geometry
For drift/fault cells, move the inherited coherent auxiliary corruption from the historical `a,b` pair to the topology's paired channels while preserving the same seedwise corruption draw and magnitude:
- `H_ac`: fault enters anchors `a,c`;
- `H_bc`: fault enters anchors `b,c`.
No new random draw is introduced.

Healthy and common-mode cells have no topology-specific auxiliary fault; only their physical diagnostic response topology is permuted.

## Comparators
On the identical permuted-topology stream for every seed/cell:
1. frozen Experiment-032 causal-context composed posterior-risk gate;
2. frozen Experiment-029 posterior-risk gate;
3. triad_persistence.

## Frozen matrix
For each topology `H_ac` and `H_bc`, evaluate these nine contexts (18 cells total):
1. drift/fault, gain 0.50, noise 1.00;
2. drift/fault, gain 0.50, noise 1.50;
3. drift/fault, gain 0.425, noise 1.00;
4. drift/fault, gain 0.40, noise 1.40;
5. drift/fault, gain 0.35, noise 1.25;
6. drift/fault, onset offset +35, gain 0.50, noise 1.50;
7. healthy, magnitude 0.00;
8. common-mode magnitude 0.50;
9. common-mode magnitude 1.00.

## Seeds
Use 500 fresh seeds per cell: `34000..34499`.
Audit seeds: `34000..34004`.
Bootstrap seed: `34034`; 10,000 paired resamples where intervals are reported.

## Truth and summaries
Experiment 034 MUST NOT reuse the historical `partition_matches(..., default=H_ab)` field as truth. The evaluator must score the deployed hypothesis directly against the explicit cell truth `H_ac` or `H_bc`.

For every cell/strategy report coverage, explicit-topology accepted precision, wrong acceptance, one-sided 95% Wilson upper bound, stop round, probe energy, operational loss `t=401..600`, final slope error, adaptation signature, context-vote burden, direct context interventions, inherited-veto violations, and fallback mismatches.

## Frozen success criteria
H1 — explicit topology safety: in every cell, the composed controller's one-sided 95% Wilson upper bound on wrong acceptance against the explicit `H_ac/H_bc` truth must be <=0.01.

H2 — nominal topology transfer: for each topology at gain 0.50/noise 1.00, coverage >=0.95 and accepted precision >=0.99.

H3 — noisy/moderate transfer: for each topology, gain 0.50/noise 1.50 requires coverage >=0.80 and precision >=0.99; gain 0.425/noise 1.00 requires coverage >=0.85 and precision >=0.99. Gain 0.40/noise 1.40 and gain 0.35/noise 1.25 are safety/coverage characterization cells and remain subject to H1.

H4 — timing transfer: for each topology at onset +35/noise 1.50, coverage >=0.80 and accepted precision >=0.99.

H5 — healthy topology identification: for each topology's healthy cell, coverage >=0.95 and accepted precision >=0.99. This is identification of physical diagnostic response topology, not a fault declaration.

H6 — common-mode operational repair transfers: at common-mode 0.50 and 1.00 for each topology, composed mean excess operational loss versus triad must be <=2.0 and <=35.0 respectively; whenever Experiment 029 excess is positive, composed must reduce it by at least 80%.

H7 — label symmetry: for matched `H_ac` versus `H_bc` cells, absolute coverage difference <=0.05, absolute wrong-acceptance difference <=0.005, and absolute mean operational-loss difference <=0.10, except common-mode cells where operational-loss symmetry tolerance is <=1.0.

H8 — non-common-mode operational non-regression: in drift/fault, timing, and healthy cells, composed mean operational loss may not exceed Experiment 029 by more than 0.05.

H9 — causal and inherited-veto integrity: every direct context-mediated suspect-veto removal must have same-time context vote, original suspect active, effective suspect removed, no triad primary-fault veto, and adaptation enabled; no composed adaptation may occur while the inherited primary-fault veto is active.

H10 — exact fallback: for every topology-abstaining seed, composed adaptation signature and operational loss must match triad_persistence exactly on the identical permuted stream.

H11 — frozen provenance/truth integrity: report must record explicit topology truth, seed range, 0.99 threshold / 100:1 loss ratio, context formula, no-recalibration flag, and code commit. All correctness metrics must use explicit cell topology rather than the historical `H_ab` helper.

## Interpretation rule
Experiment 034 supports structural topology transfer only if H1–H11 all pass. Any failure is a structural external-validity boundary. Preserve the frozen controller and do not introduce topology-specific retuning from Experiment-034 outcomes.
