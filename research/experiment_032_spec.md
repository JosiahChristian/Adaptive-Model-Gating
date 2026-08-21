# Experiment 032 — Causal Two-State Topology + Operational-Context Composition

## Status

Prospectively frozen before any Experiment-032 evaluation outcomes are generated.

Experiment 028 validated the directed-covariance topology posterior. Experiment 029 showed that a 0.99 posterior-risk deployment rule is safe and useful across the gain/noise frontier but operationally regresses in common-mode. Experiment 030 replicated that the action-value sign depends on operational context even at essentially identical topology confidence. Experiment 031 independently validated a non-fitted common-mode context geometry.

Experiment 032 is the first composition study. It does not modify the Experiment-028 posterior, the Experiment-029 0.99 topology threshold, the probe schedule, or the inherited triad operational rule.

## Scientific question

Can the validated topology-risk gate and the independently validated operational-context signal be composed causally so that common-mode operational regression is removed without sacrificing the frontier safety/utility properties established by Experiment 029?

## Frozen topology layer

Use Experiment 029 exactly for diagnostic acquisition and topology qualification:

- Experiment-028 directed-covariance posterior unchanged;
- unique-topology deployment threshold `p >= 0.99` unchanged;
- symmetric rounds 1..5 unchanged;
- wrong-action cost 100 and fallback cost 1 unchanged;
- exact triad persistence fallback when no topology qualifies unchanged.

Experiment 032 must make exactly the same provenance accept/abstain and diagnostic stop-round decision as Experiment 029 on the same seed/stream.

## Frozen causal context signal

Use the per-time vote already defined inside Experiment 031, evaluated from information available at time t only:

`context_vote_t = triad_consistent_t * 1[m_a+m_b+m_c >= 2] * 1[d_ab+d_ac+d_bc == 0]`

where mismatch/disagreement indicators use the inherited frozen thresholds `k3, la, lb, lc, lab, lac, lbc`.

The Experiment-031 retrospective 20-step average and seed-level 0.50 threshold are NOT used to make online decisions in Experiment 032, because doing so inside t=401..420 would leak future observations. Experiment 032 uses only the current-time binary vote.

No fitted smoothing length, persistence count, context probability, family label, or learned classifier is permitted.

## Composed operational rule

For a seed that fails topology qualification after stage 5, use `triad_persistence` exactly as Experiment 029 already does.

For a seed that qualifies a unique topology:

1. retain the Experiment-029 group-conditioned operational gate;
2. at every operational time t, compute the inherited residual-ready condition and triad primary-fault veto exactly as before;
3. compute the Experiment-029 provenance-specific `suspect` veto exactly as before;
4. compute `context_vote_t` causally;
5. if `context_vote_t == 1`, the provenance-specific suspect veto is disabled for that time step, so the adaptation decision reduces to the inherited triad decision `ready and not primary_bad`;
6. if `context_vote_t == 0`, retain the Experiment-029 decision `ready and not (primary_bad or suspect)`.

Thus operational context may only remove the additional provenance-specific veto. It may never disable the inherited triad primary-fault veto, alter residual readiness, create a new adaptation trigger, or change the topology decision.

## Comparators

On every seed/cell evaluate:

1. Experiment-032 causal composed controller;
2. frozen Experiment-029 posterior-risk gate;
3. `triad_persistence`.

## Evaluation matrix

Use the ten Phase-I frontier cells:

- gain 0.50 × noise {1.00,1.25,1.50,2.00};
- gain 0.425 × noise {1.00,1.50,2.00};
- gain 0.35 × noise {1.00,1.50,2.00};

all under `drift_ab_fault`, magnitude 0.50.

Add controls:

- healthy;
- genuine drift magnitude 0.50;
- primary fault magnitude 0.50;
- common-mode magnitude 0.25;
- common-mode magnitude 0.50;
- common-mode magnitude 1.00;
- coherent all-auxiliary corruption magnitude 0.50.

Total: 17 frozen cells.

## Seeds

Use 1,000 fresh evaluation seeds per cell:

`32000..32999`.

Audit seeds: `32000..32004`.

No seed overlaps Experiments 027–031 or Phase I.

## Primary summaries

For every strategy/cell report:

- provenance coverage, accepted precision, wrong acceptance, one-sided 95% Wilson upper bound;
- diagnostic stop-round distribution and mean diagnostic energy;
- operational loss t=401..600;
- final slope error;
- adaptation signature;
- exact fallback mismatches.

For Experiment 032 additionally report:

- context-vote fraction in t=401..420 and t=401..600;
- count of residual-ready opportunities where context removed the Experiment-029 suspect veto;
- count of actual adaptation decisions changed relative to Experiment 029;
- paired operational-loss difference versus Experiment 029 and versus triad persistence;
- paired bootstrap 95% intervals using fixed bootstrap seed 32032 and 10,000 resamples.

## Frozen success criteria

H1 — topology-layer identity:
For every seed/cell, Experiment 032 must exactly match Experiment 029 on provenance accepted/abstained status, accepted topology, diagnostic stop round, posterior at deployment, and diagnostic energy.

H2 — frontier safety preservation:
For each of the ten gain/noise frontier cells, the one-sided 95% Wilson upper bound on Experiment-032 wrong acceptance must be <= 0.01.

H3 — frontier utility preservation:
At gain=0.50/noise=1.50, coverage >=0.85 and accepted precision >=0.99. At gain=0.50/noise=1.25, coverage >=0.90. At gain=0.425/noise=1.00, coverage >=0.85 and precision >=0.99.

H4 — common-mode repair at magnitude 0.50:
The mean paired operational-loss excess of Experiment 032 versus triad persistence must be <= 2.0, and Experiment 032 must reduce the same-seed Experiment-029 common-mode excess loss by at least 80%.

H5 — common-mode repair scales:
At common-mode magnitude 0.25, mean paired excess loss versus triad persistence <=0.25. At magnitude 1.00, Experiment 032 must reduce the same-seed Experiment-029 excess loss by at least 80% and have mean excess <=35.0.

H6 — supported-frontier non-regression:
At gain=0.50/noise in {1.00,1.25,1.50}, Experiment-032 mean operational loss may not exceed Experiment 029 by more than 0.02 and final slope error may not exceed Experiment 029 by more than 0.02.

H7 — control non-regression:
Healthy, genuine-drift, and primary-fault mean operational loss may not exceed triad persistence by more than 0.02; coherent all-auxiliary corruption remains explicitly operationally unresolved.

H8 — causal context integrity:
Every context-mediated decision change must be attributable to `context_vote_t == 1` at that same time t. No future window summary, family label, or post-t observation may influence the action.

H9 — inherited triad veto preservation:
No Experiment-032 adaptation may occur at a time when the inherited Experiment-029/triad primary-fault veto is active.

H10 — exact fallback:
For every Experiment-032 seed that abstains on topology, adaptation signature and operational loss must match `triad_persistence` exactly.

H11 — frozen-model provenance:
The report must record Experiment-028 posterior constants, Experiment-029 0.99 threshold/loss ratio, inherited context thresholds, exact context-vote formula, seed range, bootstrap seed, and exact code commit. No quantity may depend on Experiment-032 outcomes.

## Interpretation rule

Experiment 032 supports the first two-state deployment architecture only if H1–H11 all pass.

If it succeeds, the next experiment should be a broader OOD deployment/generalization study with both topology and context layers frozen.

If it fails, do not retune the 0.99 posterior threshold or fit the context vote to Experiment-032 outcomes. Diagnose whether failure arises from false context intervention, insufficient common-mode detection at decision time, or an operational objective conflict requiring an explicit action-value model.