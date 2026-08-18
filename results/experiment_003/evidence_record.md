# Experiment 003 Evidence Record

## Provenance

- Frozen specification: `research/experiment_003_spec.md`
- Evaluation request: `evaluation_requests/experiment_003.request`
- GitHub Actions run: `32104987039`
- Producing commit: `b2feddbcb6a492804daab53a5e42981d51685ef1`
- Completed evidence pointer: issue `#4`
- Artifact: `experiment-003-evidence`
- Artifact ID: `9313098177`
- GitHub-recorded artifact SHA-256: `510db1dcd30e1e711e0bcb7716b929daac74a50fa9ea507b47c54be398a4ec4d`
- Downloaded artifact SHA-256 independently verified equal to the GitHub digest.
- `test` job: completed / success
- `evaluate` job: completed / success

Contained files and independently verified SHA-256 values:

- `report.json` — `c7601a40d7080c471ae2e8c854a913f626ab60721f1c0a9bc39cb13f5cf0c7ea`
- `seed_summary.csv` — `2914a6a3d7b9aec7bed33829dfefb2b7407bfb3f36e5076fd5ebc0a05b65cb93`
- `audit_trace_seeds_3000_3004.csv` — `bb6d605604bcd3245788bfac464f93c576968952bd1262e757661c76aeb88020`

The full evidence remains in the Actions artifact. This compact record preserves provenance, audit checks, cell-level results, and the bounded conclusion.

## Frozen design

- Rolling-MSE threshold `tau`: `0.4749575582753968`
- Evaluation seeds: `3000..3199`
- Independent seeds per cell: `200`
- Drift magnitudes: `delta_a ∈ {0.25, 0.5, 1.0}`
- Ramp durations: `r ∈ {20, 50, 100, 200}`
- Strategies: frozen, continuous, threshold, persistence
- Primary loss horizon: `t=401..800`
- Primary paired contrast: persistence loss minus threshold loss
- Resampling unit: whole seed, paired within cell

## Audit

The downloaded evidence passed the following independent checks:

- `seed_summary.csv` contains exactly `9,600` rows = 12 cells × 4 strategies × 200 seeds.
- Every cell-strategy group contains exactly 200 seeds, covering the complete frozen seed range `3000..3199`.
- Recomputed mean losses, during-ramp adaptation rates, and persistence-minus-threshold mean loss differences match `report.json` exactly to numerical precision.
- All 12 reported 95% paired whole-seed bootstrap intervals reproduce exactly using the per-cell deterministic bootstrap seeds in `scripts/run_experiment_003.py`.
- `audit_trace_seeds_3000_3004.csv` contains exactly `216,000` rows = 5 audit seeds × 12 cells × 4 strategies × 900 scored time steps.
- Within each seed/cell/time point, all four strategies share identical `x`, `y`, and `true_a`, confirming matched stochastic realizations.
- The audited `true_a` traces exactly follow the frozen linear-ramp formula and remain at the target value after ramp completion.
- Every audited prediction satisfies the test-then-train chronology: `y_hat = slope_before * x + intercept_before` before any same-step adaptation.
- A single frozen `tau` value is used throughout the audit trace.

## Cell-level evidence

| delta_a | ramp | threshold loss | persistence loss | P − T loss | 95% paired CI | threshold adapt during ramp | persistence adapt during ramp |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.25 | 20 | 107.888 | 109.248 | +1.360 | [0.913, 1.847] | 0.040 | 0.025 |
| 0.25 | 50 | 107.744 | 108.897 | +1.153 | [0.717, 1.623] | 0.115 | 0.070 |
| 0.25 | 100 | 107.260 | 108.591 | +1.331 | [0.849, 1.841] | 0.270 | 0.200 |
| 0.25 | 200 | 106.714 | 107.559 | +0.845 | [0.534, 1.190] | 0.420 | 0.325 |
| 0.50 | 20 | 113.780 | 116.002 | +2.222 | [1.794, 2.694] | 0.110 | 0.040 |
| 0.50 | 50 | 112.984 | 114.780 | +1.796 | [1.388, 2.238] | 0.340 | 0.220 |
| 0.50 | 100 | 112.037 | 113.713 | +1.676 | [1.282, 2.082] | 0.575 | 0.470 |
| 0.50 | 200 | 111.831 | 113.689 | +1.858 | [1.413, 2.319] | 0.820 | 0.705 |
| 1.00 | 20 | 128.291 | 131.764 | +3.473 | [3.043, 3.946] | 0.430 | 0.265 |
| 1.00 | 50 | 125.597 | 128.945 | +3.347 | [2.875, 3.840] | 0.865 | 0.750 |
| 1.00 | 100 | 122.870 | 126.594 | +3.723 | [3.270, 4.200] | 0.990 | 0.965 |
| 1.00 | 200 | 121.441 | 124.539 | +3.098 | [2.661, 3.547] | 1.000 | 1.000 |

The persistence penalty relative to threshold is approximately `0.79%` to `3.03%` of threshold loss across the 12 cells.

## Scientifically bounded conclusion

Within this frozen controlled linear system, the responsiveness-versus-conservatism distinction survives gradual persistent drift.

Persistence gating adapted during the ramp less often than threshold gating in 11 of 12 cells and tied it in the strongest, slowest cell (`delta_a=1.0`, `r=200`), where both adapted during the ramp for every seed. That is a systematic conservative shift, but not a universal separation.

The conservative shift came with a consistent prediction-loss cost. Persistence had higher mean `t=401..800` loss than threshold in all 12 cells, and every prespecified paired bootstrap interval for persistence-minus-threshold loss excluded zero on the positive side. The loss penalty was modest in relative terms in this experiment, ranging from about 0.79% to 3.03% of threshold loss, but it was systematic rather than negligible in the inferential sense used here.

Experiment 003 therefore supports generalization of the earlier **tradeoff phenomenon** from abrupt change to the specified gradual persistent drifts. It does **not** support general superiority of persistence gating. It also exposes a boundary: for sufficiently strong and slow drift, the during-ramp adaptation distinction can disappear even though persistence still incurs greater cumulative loss.

The claim remains limited to the specified simulated linear dynamics, noise process, frozen threshold and persistence count, ramp magnitudes/durations, and seed distribution. No conclusion is established for nonlinear dynamics, sensor faults, adversarial changes, real digital twins, or arbitrary concept drift.
