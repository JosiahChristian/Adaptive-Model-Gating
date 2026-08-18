# Experiment 004 Evidence Record

## Provenance

- Frozen specification: `research/experiment_004_spec.md`
- Evaluation request: `evaluation_requests/experiment_004.request`
- GitHub Actions run: `32109466969`
- Producing commit: `a00f931b62e0408d9a422e66854a2da89f736580`
- Completed evidence pointer: issue `#5`
- Artifact: `experiment-004-evidence`
- Artifact ID: `9314439015`
- GitHub-recorded artifact SHA-256: `1acbc72ec4f8fae8cc1500eef66839351a775292154a0c1954b4979d2768de79`
- Downloaded artifact SHA-256 independently verified equal to the GitHub digest.
- `test` job: completed / success
- `evaluate` job: completed / success

Contained files and independently verified SHA-256 values:

- `report.json` — `476074892316fd331d19e2dee3275a96724d0d9162628b95e8184ba183672182`
- `seed_summary.csv` — `53e38689fd3ed1339e4f30e2d60e44ec8fe9a05990f56652ed009797ab45528c`
- `audit_trace_seeds_4000_4004.csv` — `a645782ed8b88ed749d7ad1e8e1e06f4aaf673616038486e07e298e90127aa0b`

The full evidence remains in the Actions artifact. This compact record preserves provenance, independent audit checks, cell-level results, and the bounded conclusion.

## Frozen design

- Rolling-MSE threshold `tau`: `0.4749575582753968`
- Evaluation seeds: `4000..4199`
- Independent seeds per cell: `200`
- Structural-mismatch magnitudes: `gamma ∈ {0.25, 0.5, 1.0}`
- Event classes: 20-step transient mismatch and persistent mismatch
- Strategies: frozen, continuous, threshold, persistence
- Learner: unchanged linear OLS model with slope and intercept only
- True post-event mismatch: `y_t = 1.5 x_t + gamma x_t^2 + epsilon_t`
- Primary transient contrast: persistence minus threshold adaptation indicator over `t=401..420`
- Primary persistent contrast: persistence minus threshold loss over `t=401..600`
- Persistent churn contrast: persistence minus threshold adaptation count through `t=1200`
- Resampling unit: whole seed, paired within cell

## Independent audit

The downloaded evidence passed the following checks:

- `seed_summary.csv` contains exactly `4,800` rows = 6 cells × 4 strategies × 200 seeds.
- Every cell-strategy group contains exactly 200 seeds covering `4000..4199`.
- `audit_trace_seeds_4000_4004.csv` contains exactly `108,000` rows = 5 audit seeds × 6 cells × 4 strategies × 900 scored time steps.
- Within every audited seed/cell/time point, all four strategies have identical `x`, `y`, `true_a`, and `true_gamma`, confirming matched stochastic realizations.
- For each audited `seed, gamma` pair, transient and persistent streams are identical through `t=420`.
- Independent regeneration from the frozen structural-mismatch equation reproduces audited `x`, `y`, and `true_gamma` to floating-point precision.
- `true_a` remains exactly `1.5` throughout; the structural change is exclusively the quadratic term.
- `true_gamma` is exactly zero before `t=401`; in transient cells it equals the frozen `gamma` for `t=401..420` and returns to zero thereafter; in persistent cells it remains active through `t=1200`.
- The audited prediction chronology satisfies `y_hat = slope_before * x + intercept_before` before any same-step adaptation, to numerical precision.
- When no adaptation occurs, `slope_after` and `intercept_after` equal their pre-decision values exactly.
- A single frozen `tau = 0.4749575582753968` is used throughout the audit trace; the shared implementation retains rolling window 20, refit window 100, persistence count 3, and the same linear OLS adaptation operator.
- Recomputed cell means and adaptation rates match `report.json` to numerical precision.
- All six prespecified primary paired bootstrap intervals reproduce exactly from seed-level evidence using the frozen deterministic bootstrap seeds.
- All three persistent-cell churn contrasts and their paired bootstrap intervals reproduce exactly.

## Cell-level evidence

| gamma | class | threshold adapt 401-420 | persistence adapt 401-420 | P − T adapt diff | 95% CI | threshold loss 401-600 | persistence loss 401-600 | P − T loss | loss 95% CI | threshold churn 401-1200 | persistence churn 401-1200 | P − T churn | churn 95% CI |
|---:|:---|---:|---:|---:|:---|---:|---:|---:|:---|---:|---:|---:|:---|
| 0.25 | transient | 0.240 | 0.170 | -0.070 | [-0.105, -0.035] | 53.680 | 53.746 | — | — | 12.165 | 3.130 | — | — |
| 0.25 | persistent | 0.240 | 0.170 | — | — | 66.295 | 67.225 | +0.930 | [0.696, 1.167] | 85.525 | 25.900 | -59.625 | [-62.985, -56.215] |
| 0.50 | transient | 0.540 | 0.490 | -0.050 | [-0.080, -0.025] | 59.702 | 60.339 | — | — | 21.575 | 6.225 | — | — |
| 0.50 | persistent | 0.540 | 0.490 | — | — | 103.128 | 107.373 | +4.246 | [3.747, 4.780] | 302.205 | 94.200 | -208.005 | [-214.015, -202.095] |
| 1.00 | transient | 0.875 | 0.825 | -0.050 | [-0.080, -0.025] | 81.645 | 83.827 | — | — | 39.070 | 11.925 | — | — |
| 1.00 | persistent | 0.875 | 0.825 | — | — | 250.256 | 264.700 | +14.444 | [12.881, 16.166] | 648.100 | 210.735 | -437.365 | [-442.230, -432.550] |

For persistent mismatch, the persistence loss penalty relative to threshold increases with mismatch magnitude: approximately `1.40%`, `4.12%`, and `5.77%` for `gamma = 0.25, 0.5, 1.0`, respectively. Over the same cells, persistence reduces mean post-event adaptation count through `t=1200` by approximately `69.7%`, `68.8%`, and `67.5%` relative to threshold.

## Scientifically bounded conclusion

Experiment 004 supports extension of the previously observed responsiveness-versus-conservatism phenomenon to this frozen quadratic structural-mismatch family, but it does not show general superiority of persistence gating.

In all three transient-mismatch cells, persistence adapts less often during the true 20-step mismatch interval than threshold gating, and each prespecified paired interval excludes zero on the negative side. The conservative shift therefore survives a change that lies outside the learner's model class.

Under persistent structural mismatch, persistence sharply reduces repeated adaptation churn relative to threshold gating in all three cells. However, that reduction is accompanied by consistently higher prediction loss, and all three prespecified paired loss intervals exclude zero on the positive side. The loss penalty grows with mismatch magnitude while the relative churn reduction remains large.

The strongest interpretation is therefore not that persistence solves model mismatch. Rather, persistence confirmation acts as a substantial adaptation-rate limiter when residual error cannot be eliminated by the available linear learner, trading less repeated refitting for worse predictive responsiveness. This is consistent with the earlier conservatism-versus-responsiveness mechanism and exposes an additional computational-burden dimension under structural misspecification.

The claim remains limited to the specified quadratic mismatch, AR(1) input process, Gaussian noise, frozen linear learner, gate settings, event timing, magnitudes, and seed distribution. No conclusion is established for arbitrary nonlinear dynamics, distribution shift, sensor faults, missing data, adversarial changes, multivariate systems, real digital twins, or optimally specified nonlinear learners.
