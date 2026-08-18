# Experiment 006 Evidence Record

## Provenance

- Frozen specification: `research/experiment_006_spec.md`
- Evaluation request: `evaluation_requests/experiment_006.request`
- GitHub Actions run: `32144962230`
- Producing commit: `91569c5a80172a07bac4557f4dd07b9b3f5d9bcb`
- Completed evidence pointer: issue `#9`
- Artifact: `experiment-006-evidence`
- Artifact ID: `9327696375`
- GitHub-recorded artifact SHA-256: `a12bcf8d58172d936b792b04ff2f7284ed3fd1b3b3a4f9062a1b24d6d37db435`
- Downloaded artifact SHA-256 independently verified equal to the GitHub digest.
- `test` job: completed / success
- `evaluate` job: completed / success

Contained files and independently verified SHA-256 values:

- `report.json` — `a78d995799651c06f805a3ee62c30f2b65c87829befd8326855f946b56b4ad0f`
- `seed_summary.csv` — `54df4d4ff9ffe66df512e4709385a83b4a4e56a57cc3c60abe12dbd5d658d28c`
- `audit_trace_seeds_6000_6004.csv` — `3e934a8910d26b9b58e21867da0b35cc7d28dab36e4437450e6a2d32163d45a1`

The full evidence remains in the Actions artifact. This compact record preserves provenance, independent audit checks, cell-level results, and the bounded conclusion.

## Frozen design

- Rolling-MSE threshold `tau`: `0.4749575582753968`
- Evaluation seeds: `6000..6199`
- Independent seeds per cell: `200`
- Additional outcome-sensor-noise standard deviations: `sigma_c ∈ {0.5, 1.0, 2.0}`
- Event classes: 20-step transient corruption and persistent corruption
- Strategies: frozen, continuous, threshold, persistence
- Learner: unchanged linear OLS model with slope and intercept only
- Clean response: `clean_y = 1.5*x + epsilon`, `epsilon ~ N(0, 0.5^2)`
- Observed response: `y = clean_y + true_sigma_c * sensor_unit_noise`, with `sensor_unit_noise ~ N(0,1)`
- Primary transient contrast: persistence minus threshold adaptation indicator over `t=401..420`
- Primary persistent contrast: persistence minus threshold observed loss over `t=401..600`
- Prespecified persistent clean-target contrast: persistence minus threshold clean-target loss over `t=401..600`
- Persistent burden contrast: persistence minus threshold adaptation count through `t=1200`
- Resampling unit: whole seed, paired within cell

## Independent audit

The downloaded evidence passed the following checks:

- `seed_summary.csv` contains exactly `4,800` rows = 6 cells × 4 strategies × 200 seeds.
- Every cell-strategy group contains exactly 200 seeds covering `6000..6199`.
- `audit_trace_seeds_6000_6004.csv` contains exactly `108,000` rows = 5 audit seeds × 6 cells × 4 strategies × 900 scored time steps.
- Within every audited seed/cell/time point, all four strategies have identical `x`, `clean_y`, `baseline_epsilon`, `sensor_unit_noise`, `true_sigma_c`, `y`, and `true_a`, confirming matched stochastic realizations.
- For each audited `seed, sigma_c` pair, transient and persistent streams are identical through `t=420`.
- The clean response equation `clean_y = 1.5*x + baseline_epsilon` reproduces to floating-point precision.
- The observed response equation `y = clean_y + true_sigma_c*sensor_unit_noise` reproduces to floating-point precision.
- `true_a` remains exactly `1.5` throughout; the underlying system mapping does not change.
- `true_sigma_c` is exactly zero before `t=401`; in transient cells it equals the frozen corruption level for `t=401..420` and returns to zero thereafter; in persistent cells it remains active through `t=1200`.
- Clean-target error and squared-error fields reproduce exactly to floating-point precision from `clean_y - y_hat`.
- The audited prediction chronology satisfies `y_hat = slope_before*x + intercept_before` before any same-step adaptation, to numerical precision.
- When no adaptation occurs, `slope_after` and `intercept_after` equal their pre-decision values exactly.
- A single frozen `tau = 0.4749575582753968` is used throughout; the shared implementation retains rolling window 20, refit window 100, persistence count 3, and the same linear OLS adaptation operator.
- Recomputed cell means, adaptation rates, observed-loss contrasts, clean-target-loss contrasts, and burden contrasts match `report.json` to numerical precision.
- All transient primary paired bootstrap intervals, persistent observed-loss intervals, clean-target-loss intervals, and burden intervals reproduce from seed-level evidence using the frozen deterministic bootstrap seeds; numerical differences are only floating-point representation at approximately `1e-15` scale.

## Cell-level evidence

| sigma_c | class | threshold adapt 401-420 | persistence adapt 401-420 | P − T adapt diff | 95% CI | threshold observed loss 401-600 | persistence observed loss 401-600 | P − T observed loss | observed 95% CI | threshold clean loss 401-600 | persistence clean loss 401-600 | P − T clean loss | clean 95% CI | threshold burden 401-1200 | persistence burden 401-1200 | P − T burden | burden 95% CI |
|---:|:---|---:|---:|---:|:---|---:|---:|---:|:---|---:|---:|---:|:---|---:|---:|---:|:---|
| 0.5 | transient | 0.595 | 0.475 | -0.120 | [-0.165, -0.075] | 56.354 | 56.323 | — | — | 51.487 | 51.463 | — | — | 17.885 | 4.830 | — | — |
| 0.5 | persistent | 0.595 | 0.475 | — | — | 102.299 | 102.340 | +0.041 | [-0.041, 0.123] | 52.185 | 52.228 | +0.043 | [-0.017, 0.103] | 434.225 | 132.650 | -301.575 | [-306.580, -296.585] |
| 1.0 | transient | 0.995 | 0.990 | -0.005 | [-0.015, 0.000] | 71.533 | 71.556 | — | — | 52.264 | 52.290 | — | — | 38.305 | 11.465 | — | — |
| 1.0 | persistent | 0.995 | 0.990 | — | — | 255.814 | 255.733 | -0.081 | [-0.207, 0.049] | 54.957 | 54.995 | +0.037 | [-0.038, 0.112] | 790.340 | 262.650 | -527.690 | [-528.235, -527.145] |
| 2.0 | transient | 1.000 | 1.000 | 0.000 | [0.000, 0.000] | 130.971 | 131.130 | — | — | 54.292 | 54.451 | — | — | 47.355 | 14.700 | — | — |
| 2.0 | persistent | 1.000 | 1.000 | — | — | 869.419 | 869.176 | -0.242 | [-0.643, 0.163] | 65.483 | 65.583 | +0.100 | [-0.041, 0.251] | 798.220 | 265.655 | -532.565 | [-532.755, -532.370] |

Under persistent corruption, persistence reduces mean adaptation burden relative to threshold by approximately `69.5%`, `66.8%`, and `66.7%` as `sigma_c` increases. Yet the threshold and persistence observed-loss intervals all include zero, as do all clean-target-loss intervals.

The frozen strategy is an important reference because the true system mapping is unchanged. Its mean clean-target loss over `t=401..600` is `50.814` in every persistent corruption cell, while threshold clean-target loss rises to `52.185`, `54.957`, and `65.483`; persistence rises to `52.228`, `54.995`, and `65.583`. Relative to frozen, these correspond to approximately `2.7%`, `8.2%`, and `28.9%` larger clean-target loss for the threshold gate, with nearly identical degradation for persistence.

## Scientifically bounded conclusion

Experiment 006 exposes a strong false-adaptation vulnerability of residual-threshold gating under outcome-sensor noise.

The underlying system and clean conditional relation remain unchanged, but added measurement noise drives the residual statistic above the frozen threshold. At the mildest transient corruption level, persistence meaningfully suppresses adaptation relative to threshold. At higher corruption levels the distinction collapses because both gates almost always adapt during the 20-step corruption interval: `99.5%` versus `99.0%` at `sigma_c=1.0`, and `100%` versus `100%` at `sigma_c=2.0`.

Under persistent corruption, both residual gates repeatedly refit despite the unchanged true mapping. Persistence dramatically limits that computational burden, reducing adaptation counts by roughly two-thirds, but this does not produce a detectable advantage in observed prediction loss or clean-target loss relative to threshold gating.

More importantly, both adaptive gates degrade clean-target performance relative to the frozen model as corruption increases. Because the frozen learner is already correctly specified and the underlying clean law does not change, this shows that repeated adaptation to corrupted outcomes can actively move the fitted model away from the stable latent relationship. The degradation is substantial at the strongest corruption level.

The strongest interpretation is therefore not simply another responsiveness-versus-conservatism result. Experiment 006 identifies a qualitatively different failure mode: residual-only adaptation logic cannot distinguish genuine model drift from sufficiently strong measurement corruption. Persistence confirmation reduces refit burden, but it does not prevent near-certain false adaptation under strong sensor noise and does not restore the clean-system performance of the frozen model.

The claim remains limited to additive Gaussian outcome-sensor noise under the frozen AR(1) input process, correctly specified linear learner, gate settings, event timing, corruption magnitudes, and seed distribution. It does not establish behavior under input-sensor noise, bias faults, dropouts, missing data, heavy-tailed corruption, temporally correlated faults, adversarial contamination, multivariate systems, nonlinear dynamics, or real digital twins.
