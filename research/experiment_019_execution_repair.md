# Experiment 019 — Execution-only CI repair

Experiment 019 remains scientifically frozen at commit `81cc36c19e82e8ddd4f89bcfa6b6eabcf63c0f83`.

The first requested evaluation failed before a completed Experiment 019 evidence registration was produced. The repair made no changes to the frozen DGP, intervention amplitudes, target-selection rule, calibration ranges, evaluation cells, evaluation seeds, estimands, hypotheses, or preregistered criteria.

Two execution-guard corrections were made:

1. The fallback regression test no longer assumes that a particular stochastic evaluation seed must abstain. It now forces the abstention branch deterministically with unreachable confidence thresholds and verifies exact operational equivalence to `triad_persistence`.
2. The all-strategy smoke test now uses seed `19999`, which is outside the frozen Experiment 019 evaluation range `19000..19199` and outside all calibration ranges, so smoke validation does not inspect a frozen evaluation seed.

The frozen Experiment 019 evaluation was retriggered by request commit `18e524fd545be7f959530384535c3d1fb55c982c`.

Any completed scientific interpretation must use only the subsequently registered frozen evidence artifact and must not treat the failed execution attempt as scientific evidence.
