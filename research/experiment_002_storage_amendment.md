# Experiment 002 Storage and Provenance Amendment

**Status:** committed before Experiment 002 evaluation.

Experiment 002 spans 17 factor/reference cells, 200 evaluation seeds per cell, four strategies, and hundreds of post-fit time steps. A complete per-time-step trace for every combination would produce multi-gigabyte evidence files while remaining exactly regenerable from deterministic seeds and the producing revision.

To preserve auditability without unnecessary storage inflation, Experiment 002 will retain:

1. complete per-seed summaries for every prespecified factor cell and strategy;
2. complete time-step traces for predetermined audit seeds `2000..2004` across every cell and strategy;
3. the compact aggregate report generated from the full seed summary;
4. the producing Git commit SHA, GitHub Actions run ID, artifact ID/name, and GitHub-recorded artifact SHA-256;
5. SHA-256 digests for every file in the evidence artifact;
6. deterministic regeneration code for any omitted full time-step trace.

The audit-seed subset is frozen prospectively and is not selected after observing outcomes. Statistical inference is computed from the complete 200-seed summaries, not from the five audit traces.

This amendment changes storage only. It does not change the simulator, factor grid, strategies, calibration, endpoints, experimental unit, or interpretation rules in `research/experiment_002_spec.md`.
