# Reusable Evaluation Execution Contract

This file records execution safeguards learned from repaired frozen evaluations. It is infrastructure policy, not a scientific specification, and must not be used to retune hypotheses or interpretation after outcomes are observed.

## Mandatory pre-evaluation gates

Every future requested-evaluation workflow must complete these checks before launching the expensive evaluation matrix:

1. **Full unit-test suite.** Exercise all new scientific mechanism semantics and inherited comparators used by the experiment.
2. **Legacy compatibility contract.** Any new stream supplied to inherited strategies must expose every diagnostic field those strategies read, including aliases/metadata. Compatibility aliases must not introduce extra random draws or alter the frozen stochastic stream.
3. **All-strategy execution smoke test.** Using seeds that are disjoint from both calibration and frozen evaluation seeds, execute every frozen strategy through the same summary/serialization path used by shards. Assert expected row count and required output fields.
4. **Comparator-semantics test.** When a new strategy is defined relative to a comparator, explicitly test the distinction encoded in the prospective specification (for example, raw sensor-count corroboration versus provenance-group corroboration). Do not allow shared helper logic to erase the intended comparison.
5. **Artifact-schema contract.** Assert that all strategies emit every field consumed by summary, audit, merge, and report code. Shared annotation layers must populate diagnostic/latent-loss fields for legacy strategies that do not emit them natively.
6. **Shard coverage assertions.** Deterministic merge must reject missing/extra cells, strategies, seeds, or audit rows; reject threshold inconsistencies across shards; and assert the preregistered exact total counts.
7. **Request marker last.** The expensive evaluation request may be committed only after the above implementation and gates exist. Execution-only repair retriggers must change only implementation/infrastructure and the request marker, never the frozen scientific specification.

## Failure classes this contract prevents

The safeguards above directly address observed execution defects:

- inherited comparators failing on missing legacy stream keys;
- accidental changes in RNG consumption while adding compatibility fields;
- summary code requiring fields absent from base legacy strategies;
- unit tests passing while shard serialization/summary paths still crash;
- comparator implementation accidentally reusing the new mechanism's semantics and invalidating a preregistered contrast;
- expensive matrices launching before a representative all-strategy execution path has succeeded.

## Scientific-boundary rule

Execution defects may be repaired after prospective freeze only when the repair restores the already-frozen implementation contract. Repairs may not alter hypotheses, DGP semantics, frozen cells, strategies, seed ranges, calibration procedures, thresholds, estimands, bootstrap rules, success/falsification criteria, or claim boundaries in response to observed scientific outcomes.
