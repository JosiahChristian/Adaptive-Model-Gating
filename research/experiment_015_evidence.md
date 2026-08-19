# Experiment 015 — Audited Evidence Record

**Status:** completed and independently audited against the prospectively frozen specification `research/experiment_015_spec.md`.

## Provenance

- Frozen specification commit: `6910956eceb9f12a26acf4501d9f99ffbcfe2494`
- Requested evaluation head: `45b29d421eaa4ffc4a1588fb3c882ca49724f546`
- Completed GitHub Actions run: `32291987666`
- Evidence artifact: `experiment-015-evidence`
- Artifact size: `207632559` bytes
- GitHub artifact digest: `sha256:4d129d57bbcb1dab9943a4562204d0b2f9f60fcd63265e4cf1a4feb5e7d992a9`
- Independently reproduced archive SHA-256: `4d129d57bbcb1dab9943a4562204d0b2f9f60fcd63265e4cf1a4feb5e7d992a9`

The unit-test job passed both the full repository test suite and `scripts/smoke_experiment_015.py`; all 22 frozen shard jobs passed; deterministic merge/evaluate, evidence upload, and completion registration passed.

## Structural audit

Independent artifact inspection verified:

- exactly `22 × 10 × 200 = 44,000` seed-strategy summaries;
- exactly 22 frozen cells, each with 2,000 summaries;
- exactly ten frozen strategies in every cell;
- evaluation seeds exactly `15000..15199` in every cell;
- calibration seeds recorded as exactly `1600..1799`, disjoint from evaluation seeds;
- bootstrap seed exactly `15015`;
- audit seeds exactly `15000..15004`;
- exactly `22 × 10 × 5 × 900 = 990,000` audit-trace rows;
- inherited thresholds reproduced as `tau=0.4749575582753968`, `kappa=0.004715841027139986`, `kappa3=0.008353014684419843`, `lambda_anchor_a=0.019710908213588067`, `lambda_anchor_b=0.01949100023700612`, `lambda_anchor_ab=0.038141341507558275`, `lambda_anchor_c=0.019710460820349236`, `lambda_anchor_ac=0.03721489946742156`, and `lambda_anchor_bc=0.03722678624274793`;
- new null-probe threshold `lambda_probe=0.03967498123713802`;
- frozen probe parameters `delta_probe=0.20`, `sigma_probe=0.05`, and `gamma_probe=0.80`.

The artifact records the full 3×3 challenge-response matrix, inferred group labels, probe configuration, mismatch/vote/veto diagnostics, learner state, physical/sensor streams, losses, and audit chronology required by the frozen specification.

## Preregistered results

### H1 — interventional recovery: supported

Under standard coherent A/B auxiliary fault, `interventional_provenance_quorum` recovered the intended A/B-vs-C partition in `200/200` seeds at every magnitude. Its paired early-loss differences versus `naive_three_anchor_quorum` were:

- magnitude 0.25: `-0.5422112389`, 95% CI `[-0.7590154412, -0.3437083047]`;
- magnitude 0.50: `-2.8928173588`, 95% CI `[-3.5490118950, -2.2756190307]`;
- magnitude 1.00: `-7.9668923032`, 95% CI `[-9.3654693758, -6.6196190573]`.

Adaptation-by-420 was identical to `triad_persistence` in all three cells. The frozen H1 criteria are satisfied at all three magnitudes.

### H2 — oracle approach: supported exactly in the tested standard condition

For all three standard A/B-fault magnitudes, `interventional_provenance_quorum` and `oracle_provenance_quorum` had exactly zero paired early-loss difference, with bootstrap CI `[0, 0]`. Under the frozen diagnostic-access construction, intervention recovered enough structure to reproduce the oracle gate numerically in this condition.

### H3 — common-mode input protection: supported at all three magnitudes

Final absolute slope-error differences, interventional minus `triad_persistence`, were:

- magnitude 0.25: `-0.0295780078`, 95% CI `[-0.0446687682, -0.0143359685]`;
- magnitude 0.50: `-0.0322772385`, 95% CI `[-0.0553957333, -0.0095536437]`;
- magnitude 1.00: `-0.0494455659`, 95% CI `[-0.0812054974, -0.0198102879]`.

All frozen interval criteria are satisfied.

### H4 — legitimate-drift non-destruction: supported exactly

At physical-drift magnitudes 0.25, 0.50, and 1.00, relative excess early loss versus `triad_persistence` was exactly zero with CI `[0,0]`, and adaptation-by-420 gaps were exactly zero.

### H5 — primary-fault regression protection: supported exactly

At primary-fault magnitudes 0.25, 0.50, and 1.00, final slope-error differences versus `triad_persistence` were exactly zero with CI `[0,0]`.

## Preserved negative and stress boundaries

### H6 — weak intervention

The weak probe (`delta_probe=0.025`) recovered the intended partition in only `3/200 = 1.5%` of seeds. It therefore largely collapsed toward naive raw-sensor behavior. Interventional-minus-oracle early-loss penalties increased with fault magnitude:

- `+0.5427444764`, CI `[0.3443361172, 0.7594741586]` at 0.25;
- `+2.8573017966`, CI `[2.2448776875, 3.5197164938]` at 0.50;
- `+7.7851883720`, CI `[6.4423088495, 9.1652969042]` at 1.00.

This is a clear signal-to-noise/identifiability boundary: intervention is informative only when its observable response exceeds the frozen diagnostic-noise and threshold regime.

### H7 — frozen cross-coupled actuator stress

The specified `gamma_probe=0.80` cross-coupling did **not** destroy identification under the reciprocal-edge rule: partition correctness was `199/200 = 99.5%`, and interventional performance matched the oracle exactly in the reported paired early-loss contrasts. This is a useful stress result but does not establish robustness to arbitrary cross-coupled actuators; the frozen claim boundary remains unchanged.

### H8 — coherent all-auxiliary corruption

Correctly identifying the A/B-vs-C provenance partition does not establish truth when all auxiliary evidence is corrupted coherently. Interventional-minus-triad early-loss penalties were:

- `+1.9679633329`, CI `[1.5143468544, 2.4552852346]` at 0.25;
- `+18.4161849170`, CI `[16.8997019649, 20.0141567889]` at 0.50;
- `+79.6009583881`, CI `[73.5257771811, 85.9379601993]` at 1.00.

At magnitude 1.0, adaptation-by-420 was 0.80 lower than `triad_persistence`. This remains an identifiability boundary, not an execution defect.

## Bounded conclusion

Experiment 015 supports the preregistered central claim under the specified diagnostic-access model: **controlled pre-event challenge-response information can identify the tested shared auxiliary failure domain sufficiently well to improve provenance-aware adaptive gating relative to naive sensor counting without materially harming legitimate drift adaptation.** In the standard A/B-vs-C condition, the deployable interventional gate reached the oracle comparator exactly on the preregistered early-loss contrast.

The result does not establish universal causal discovery, safety or feasibility of arbitrary interventions, robustness when diagnostic excitation is too weak, robustness to arbitrary actuator cross-coupling, or truth identification when all auxiliary evidence shares coherent corruption. The weak-probe and all-auxiliary negative findings are retained as first-class evidence.