# Experiment 018 — Completed Evidence Record

**Status:** completed frozen evaluation; interpreted only against the prospectively frozen Experiment 018 specification.

## Provenance

- Frozen scientific specification commit: `7de632c0f05a3ec492473dbbec62863dacc5b9a5`
- Requested/evaluated head: `f307091a9a1de42b193a87ee6cbbe9f5604fba32`
- GitHub Actions run: `32316552597`
- Evidence artifact: `experiment-018-evidence`
- Artifact id: `9390491423`
- Artifact size: `369435648` bytes
- Artifact SHA-256: `cfcabf044a057d3b654b93955a4bee987f5277e347afcfa741130314538c8800`
- Evaluation seeds: `18000..18199`
- Round-5 calibration seeds: `3000..3999`
- `mu_5 = 0.07296131069038679`
- `nu_5 = 0.10105196806592914`

## Primary result

Experiment 018 supports the preregistered confirmatory-replication mechanism. Holding the maximum intervention amplitude fixed at `0.20`, one additional independent confirmation round rescued the moderate-gain deployment-coverage failure observed in Experiment 017 without sacrificing accepted-decision precision or operational safety.

At `g_probe=0.50`, for all three A/B-fault magnitudes:

- round-4 selective coverage: `0.640`;
- final replicated-selective coverage: `0.895`;
- absolute coverage gain: `+0.255`;
- rescue fraction among round-4 abstainers: `0.7083333333`;
- accepted-partition precision: `1.000`;
- rescued-decision precision: `1.000`;
- wrong-acceptance rate: `0.000`;
- wrong-acceptance increase versus Experiment-017 selective comparator: `0.000`;
- replicated-minus-original-selective early-loss difference: `0.000`, bootstrap 95% CI `[0.000, 0.000]`;
- adaptation gap versus `triad_persistence`: `0.000`;
- mean replicated diagnostic energy: `1.003875`;
- round-5 execution rate: `0.360`.

Therefore H2, H3, and H6 pass their frozen criteria.

## Standard-gain preservation

At `g_probe=1.00` in the A/B coherent-fault cells, all three magnitudes achieved:

- coverage `1.000`;
- accepted precision `1.000`;
- wrong acceptance `0.000`;
- adaptation gap versus triad `0.000`;
- mean energy `0.3766875`.

Replicated-selective minus naive early-loss differences were strictly favorable at all magnitudes, with bootstrap 95% CI upper endpoints below zero. H1 passes.

## Attenuation boundary

At `g_probe=0.375`, final coverage increased to `0.445` from the inherited selective comparator by `+0.260`, while accepted precision remained `1.000`, wrong acceptance remained `0.000`, and replicated-minus-triad early-loss differences were exactly zero on the matched seeds.

At `g_probe=0.25`, final coverage was only `0.050` despite the additional confirmation round. Accepted precision remained `1.000`, wrong acceptance remained `0.000`, and fallback behavior remained operationally identical to triad on abstaining seeds.

At `g_probe=0.125`, final coverage was `0.000`, abstention was `1.000`, wrong acceptance was `0.000`, and replicated-minus-triad early-loss difference was exactly zero. H4 and H5 pass their frozen safety criteria.

This establishes a sharper empirical identifiability boundary: one additional maximum-amplitude confirmation round is sufficient to rescue `g_probe=0.50`, partially improves `0.375`, but does not materially rescue `0.25` and correctly gives up at `0.125`.

## Regression protections

For genuine physical drift, relative excess early loss versus `triad_persistence` was exactly zero at all three magnitudes and the adaptation gap was zero. H7 passes.

For common-mode input corruption, replicated selective provenance improved final coefficient error versus `triad_persistence` at all three magnitudes; paired mean differences were negative with bootstrap intervals not crossing zero. H8 passes.

For primary-only input fault, final coefficient-error difference versus `triad_persistence` was exactly zero at all three magnitudes. H9 passes.

## Coherent-all-auxiliary negative boundary

When all auxiliary evidence was coherently corrupted, the replicated provenance strategy still confidently recovered provenance structure but that structure did not certify truth. Relative to `triad_persistence`, early operational loss was materially worse at every magnitude (`+2.146`, `+17.320`, `+76.118` respectively, with strictly positive bootstrap intervals). This preserves the preregistered unsolved boundary rather than converting provenance confidence into a truth claim. H10 is therefore interpreted as boundary preservation, not success on the corrupted-all-auxiliary task.

## Scientific conclusion

Experiment 018 repairs the specific Experiment-017 moderate-gain coverage failure under the frozen intervention ceiling. The evidence supports a sequential-information interpretation: when provenance is physically identifiable but a four-round ladder is underpowered, one independent confirmatory observation at the same maximum amplitude can recover substantial deployment coverage without relaxing confidence thresholds or increasing intervention strength.

The result does **not** justify unlimited repeated probing. The next experiment must therefore test whether the remaining `g_probe=0.375` abstention mass can be recovered by a more information-efficient confirmation design under an explicit total diagnostic budget, while preserving the successful low-gain abstention and coherent-all-auxiliary negative boundary.
