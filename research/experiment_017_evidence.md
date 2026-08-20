# Experiment 017 evidence record

**Status:** scientifically complete against the prospectively frozen specification `research/experiment_017_spec.md`.

## Provenance

- Frozen specification commit: `f7063703d05dde472a1850d8add1dca66dd39fc4`
- Completed repaired request head: `f4966b630e4c3e2a10a7817fd2b1ed478ce1833c`
- Completed GitHub Actions run: `32307032766`
- Evidence artifact ID: `9388117581`
- Artifact size: `343623944` bytes
- Artifact SHA-256: `7818201d06caaca914030045b5dca2d08ca4c6d013827c3afe5b9b4f7cb0c70f`
- Coverage: `28 x 13 x 200 = 72,800` seed-strategy summaries
- Audit trace: `28 x 13 x 5 x 900 = 1,638,000` rows
- Evaluation seeds: `17000..17199`
- Bootstrap seed: `17017`
- Completion pointer: issue #21

The completed artifact contains `seed_summary.csv`, `audit_trace_seeds_17000_17004.csv`, and `report.json`. The bounded registration issue records the inherited round thresholds, new cumulative thresholds, disjoint calibration ranges, evaluation range, bootstrap seed, strategy set, audit seeds, and cell count.

## Preregistered result

### H1 — standard-gain selective recovery: supported

At `g_probe=1.00`, deployment coverage was `1.000`, accepted-partition precision was `1.000`, wrong-acceptance rate was `0.000`, and mean selective energy was `0.371625` at every A/B-fault magnitude. Selective-minus-naive early-loss differences were:

- magnitude 0.25: `-1.7429032834`, 95% CI `[-2.2114172095, -1.3155944231]`;
- magnitude 0.50: `-16.1703060907`, 95% CI `[-17.5789184399, -14.8054032322]`;
- magnitude 1.00: `-72.2326516466`, 95% CI `[-78.1217989978, -66.3536090376]`.

Adaptation-by-420 matched `triad_persistence` in all three cells. The frozen H1 criteria are satisfied.

### H2 — moderate-gain selective robustness: falsified by coverage

At `g_probe=0.50`, deployment coverage was only `0.595` at each magnitude, below the preregistered `>=0.75` requirement. Accepted-partition precision was nevertheless `1.000`, wrong-acceptance rate was `0.000`, and adaptation-by-420 matched `triad_persistence`.

Selective-minus-Experiment-016-sequential early-loss differences were favorable:

- magnitude 0.25: `-0.2090945184`, 95% CI `[-0.3862775625, -0.0679938498]`;
- magnitude 0.50: `-1.7235592293`, 95% CI `[-2.4798475394, -1.0410469947]`;
- magnitude 1.00: `-6.9150965998`, 95% CI `[-10.0276752892, -4.1447464160]`.

Mean selective energy was `0.781875`. H2 fails solely because coverage did not reach the frozen minimum.

### H3 — attenuation risk containment: supported

At `g_probe=0.375`, deployment coverage was `0.195`, abstention `0.805`, accepted precision `1.000`, and wrong acceptance `0.000`. At `g_probe=0.25`, deployment coverage was `0.015`, abstention `0.985`, accepted precision `1.000`, and wrong acceptance `0.000`.

For all six attenuation cells, selective-minus-triad early loss was exactly zero with CI `[0,0]`, and adaptation matched triad. The frozen H3 criteria are satisfied.

### H4 — severe-attenuation abstention: supported exactly

At `g_probe=0.125`, selective deployment coverage was `0.000` and abstention was `1.000` at all magnitudes. Wrong acceptance was `0.000`; accepted precision is correctly undefined because there were no accepted seeds. Selective-minus-triad early loss was exactly zero with CI `[0,0]`. The frozen H4 criteria are satisfied.

### H5 — cumulative-information gain: not supported

The preregistered mechanism criterion required cumulative round-4 partition correctness to exceed max-probe correctness by at least `0.10` absolute in a tested cell. Observed gains were smaller:

- `g_probe=0.375`: cumulative `0.535` vs max-probe `0.500`, difference `+0.035`;
- `g_probe=0.25`: cumulative `0.150` vs max-probe `0.095`, difference `+0.055`.

These rates were identical across the three fault magnitudes because provenance diagnostics are pre-event and magnitude-independent in the frozen construction. H5 is not supported.

### H6 — legitimate-drift non-destruction: supported exactly

At drift magnitudes 0.25, 0.50, and 1.00, relative excess early loss versus `triad_persistence` was exactly zero with CI `[0,0]`, and adaptation-by-420 gaps were zero.

### H7 — common-mode coefficient integrity: supported

Selective-minus-triad final absolute slope-error differences were:

- magnitude 0.25: `-0.0472304554`, 95% CI `[-0.0620507880, -0.0324777645]`;
- magnitude 0.50: `-0.0303278491`, 95% CI `[-0.0565153030, -0.0048275494]`;
- magnitude 1.00: `-0.0395450203`, 95% CI `[-0.0755812631, -0.0055874207]`.

All upper endpoints are below zero.

### H8 — primary-fault regression protection: supported exactly

At all three primary-fault magnitudes, selective-minus-triad final slope-error differences were exactly zero with CI `[0,0]`.

### H9 — coherent-all-auxiliary boundary: preserved negative result

Selective provenance does not establish truth when all auxiliaries are coherently corrupted. Selective-minus-triad early-loss penalties were:

- magnitude 0.25: `+1.8324348456`, 95% CI `[1.3837467425, 2.3253734913]`;
- magnitude 0.50: `+16.8230208053`, 95% CI `[15.4325242695, 18.2534670183]`;
- magnitude 1.00: `+77.4275225988`, 95% CI `[71.5655327103, 83.2498562139]`.

This remains an identifiability boundary rather than an execution defect.

## Frozen interpretation

Under the Experiment-017 falsification logic, the central selective-identifiability claim is **falsified because H2 failed its coverage criterion**, even though selective abstention strongly contained risk at lower gains and produced no wrong high-confidence acceptances in the tested seeds.

The result therefore supports a narrower statement: prospectively calibrated abstention can prevent weak diagnostic evidence from being converted into harmful provenance decisions, but the tested four-round cumulative rule does not provide enough deployment coverage at moderate response gain.

The next scientific question should not relax the confidence threshold after seeing this result. It should test whether additional independent evidence can increase moderate-gain coverage while preserving the already-observed precision/abstention safety boundary.