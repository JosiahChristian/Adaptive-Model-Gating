# Experiment 007 Evidence Record

## Provenance

- Frozen specification: `research/experiment_007_spec.md`
- Evaluation request: `evaluation_requests/experiment_007.request`
- GitHub Actions run: `32147093839`
- Producing commit: `cc3b516860a790b9741c8b7c166e298002f2af4c`
- Completed evidence pointer: issue `#10`
- Artifact: `experiment-007-evidence`
- Artifact ID: `9328440830`
- GitHub-recorded artifact SHA-256: `d6d78e775f02798c62c7b79da950a1748527380dc6452428efcca59aea2da847`
- Downloaded artifact SHA-256 independently verified equal to the GitHub digest.
- `test` job: completed / success
- `evaluate` job: completed / success

Contained files and independently verified SHA-256 values:

- `report.json` — `47009dbb6cfac6eb4d3b8d1901810ec0f544059ebc7b3925695b97d343f6a68f`
- `seed_summary.csv` — `b6dcec06778a6e2430ba8d6925b6888c8a7d45fa835bfb75b3375a2a2bc33c3a`
- `audit_trace_seeds_7000_7004.csv` — `1362659fdd8f401e9338469262ba4a2a8b6b62461aa7ce3df63e04883697ac05`

The full evidence remains in the Actions artifact. This compact record preserves provenance, independent audit checks, cell-level results, and the bounded conclusion.

## Frozen design

- Rolling-MSE threshold `tau`: `0.4749575582753968`
- Evaluation seeds: `7000..7199`
- Independent seeds per cell: `200`
- Input-sensor-noise standard deviations: `sigma_x ∈ {0.25, 0.5, 1.0}`
- Event classes: 20-step transient corruption and persistent corruption
- Strategies: frozen, continuous, threshold, persistence
- Latent physical input: AR(1) process with coefficient `0.8` and innovation SD `0.5`
- Physical response: `y = 1.5*x_true + epsilon`, `epsilon ~ N(0, 0.5^2)`
- Observed learner input: `x_obs = x_true + true_sigma_x*sensor_unit_noise`, with `sensor_unit_noise ~ N(0,1)`
- Learner and refit operator receive `x_obs`, not `x_true`
- Primary transient contrast: persistence minus threshold adaptation indicator over `t=401..420`
- Primary persistent contrast: persistence minus threshold operational loss over `t=401..600`
- Prespecified persistent diagnostics: latent-input loss, final absolute slope error relative to `1.5`, and adaptation burden through `t=1200`
- Resampling unit: whole seed, paired within cell

## Independent audit

The downloaded evidence passed the following checks:

- `seed_summary.csv` contains exactly `4,800` rows = 6 cells × 4 strategies × 200 seeds.
- Every cell-strategy group contains exactly 200 seeds covering `7000..7199`.
- `audit_trace_seeds_7000_7004.csv` contains exactly `108,000` rows = 5 audit seeds × 6 cells × 4 strategies × 900 scored time steps.
- Within every audited seed/cell/time point, all four strategies have identical `x_true`, `physical_epsilon`, `sensor_unit_noise`, `true_sigma_x`, `x_obs`, and `y`, confirming matched stochastic realizations.
- For each audited `seed, sigma_x` pair, transient and persistent streams are identical through `t=420`.
- The physical response equation `y = 1.5*x_true + physical_epsilon` reproduces to floating-point precision.
- The observed-input equation `x_obs = x_true + true_sigma_x*sensor_unit_noise` reproduces to floating-point precision.
- The learner input field `x` equals `x_obs` exactly at every audited time step; latent `x_true` is evaluator-only.
- `true_a` remains exactly `1.5` throughout; the latent physical response mechanism does not change.
- `true_sigma_x` is exactly zero before `t=401`; in transient cells it equals the frozen corruption level for `t=401..420` and returns to zero thereafter; in persistent cells it remains active through `t=1200`.
- Prediction chronology satisfies `y_hat = slope_before*x_obs + intercept_before` before any same-step adaptation.
- Latent-input diagnostic prediction satisfies `y_hat_latent = slope_before*x_true + intercept_before` and its error fields reproduce to floating-point precision.
- The 20-step rolling MSE statistic reproduces exactly from prior/current squared errors.
- Frozen, continuous, threshold, and persistence adaptation decisions reproduce exactly from the committed gate logic; persistence uses the same threshold and requires three consecutive exceedances before refitting.
- Model state carries correctly from each time step to the next; when adaptation occurs at audited `t>=400`, the post-adaptation slope/intercept reproduce from OLS on the last 100 observed `(x_obs, y)` pairs.
- Recomputed cell means, transient adaptation-rate contrasts, persistent operational-loss contrasts, latent-input-loss contrasts, final-slope-error contrasts, and adaptation-burden contrasts match `report.json` to numerical precision.
- Every prespecified paired 10,000-replicate whole-seed bootstrap interval reproduces exactly to floating-point precision using the frozen deterministic bootstrap seeds.

## Cell-level evidence

| sigma_x | class | threshold adapt 401-420 | persistence adapt 401-420 | P − T adapt diff | 95% CI | threshold operational loss 401-600 | persistence operational loss 401-600 | P − T operational loss | operational 95% CI | threshold latent loss 401-600 | persistence latent loss 401-600 | P − T latent loss | latent 95% CI | threshold final | persistence final | threshold abs slope err | persistence abs slope err | P − T slope err | slope 95% CI | threshold burden | persistence burden | P − T burden | burden 95% CI |
|---:|:---|---:|---:|---:|:---|---:|---:|---:|:---|---:|---:|---:|:---|---:|---:|---:|---:|---:|:---|---:|---:|---:|:---|
| 0.25 | transient | 0.335 | 0.225 | -0.110 | [-0.155, -0.070] | 53.996 | 53.919 | — | — | 51.011 | 50.928 | — | — | 1.499 | 1.498 | 0.049 | 0.048 | — | — | 13.160 | 3.340 | — | — |
| 0.25 | persistent | 0.335 | 0.225 | — | — | 77.750 | 77.849 | +0.100 | [-0.035, 0.242] | 52.764 | 52.661 | -0.103 | [-0.239, 0.028] | 1.363 | 1.367 | 0.138 | 0.135 | -0.0034 | [-0.0075, 0.0005] | 181.480 | 52.105 | -129.375 | [-133.795, -124.755] |
| 0.5 | transient | 0.940 | 0.865 | -0.075 | [-0.115, -0.040] | 63.938 | 64.105 | — | — | 52.892 | 52.958 | — | — | 1.490 | 1.481 | 0.056 | 0.063 | — | — | 31.785 | 9.700 | — | — |
| 0.5 | persistent | 0.940 | 0.865 | — | — | 139.229 | 140.036 | +0.807 | [0.702, 0.912] | 69.379 | 69.724 | +0.345 | [0.243, 0.438] | 1.071 | 1.071 | 0.429 | 0.429 | +0.00002 | [-0.0027, 0.0025] | 651.095 | 209.500 | -441.595 | [-445.045, -438.065] |
| 1.0 | transient | 1.000 | 1.000 | 0.000 | [0.000, 0.000] | 99.614 | 101.655 | — | — | 63.684 | 64.486 | — | — | 1.496 | 1.487 | 0.050 | 0.057 | — | — | 57.920 | 18.665 | — | — |
| 1.0 | persistent | 1.000 | 1.000 | — | — | 265.751 | 269.749 | +3.999 | [3.756, 4.254] | 139.072 | 140.722 | +1.650 | [1.496, 1.812] | 0.578 | 0.578 | 0.922 | 0.922 | +0.00049 | [-0.0010, 0.0021] | 783.190 | 259.445 | -523.745 | [-524.655, -522.740] |

Under persistent corruption, persistence reduces mean adaptation burden relative to threshold by approximately `71.3%`, `67.8%`, and `66.9%` as `sigma_x` increases. The burden intervals exclude zero in every persistent cell.

At `sigma_x=0.25`, persistence and threshold have statistically unresolved operational-loss, latent-input-loss, and final-slope-error differences. At `sigma_x=0.5` and `1.0`, persistence has significantly higher operational and latent-input loss than threshold, while final absolute slope-error differences remain unresolved. Thus fewer refits do not protect the coefficient from the underlying errors-in-variables contamination once persistent input corruption is strong.

The frozen model is an especially important coefficient-integrity reference. Its mean final slope remains `1.504` with mean absolute slope error `0.033` in every cell because it never refits on corrupted predictors. Under persistent corruption, threshold mean final slopes fall to `1.363`, `1.071`, and `0.578`; persistence falls to `1.367`, `1.071`, and `0.578`. The associated mean absolute slope errors rise to approximately `0.138`, `0.429`, and `0.922`. This is severe coefficient attenuation despite the unchanged physical slope of `1.5`.

## Scientifically bounded conclusion

Experiment 007 identifies a second sensor-corruption failure mode, distinct from Experiment 006 outcome-sensor noise.

When the predictor sensor is corrupted but the latent physical relation remains `y = 1.5*x_true + epsilon`, residual gating reacts strongly as corruption grows. Persistence suppresses transient adaptation relative to threshold at `sigma_x=0.25` and `0.5`, but the distinction collapses completely at `sigma_x=1.0`, where both gates adapt in every transient stream.

Under persistent input corruption, both adaptive gates repeatedly refit on contaminated predictors. Persistence reduces refit burden by roughly two-thirds or more, yet it does not preserve the latent physical coefficient: both threshold and persistence converge toward strongly attenuated slopes as corruption increases. The coefficient-integrity degradation is therefore driven by adapting with corrupted covariates, not solved by merely requiring persistence before adaptation.

At moderate and strong persistent corruption, persistence also incurs a statistically resolved operational and latent-input prediction-loss penalty relative to threshold while providing no resolved advantage in final slope error. This restores the responsiveness-versus-conservatism cost at these sensor-fault levels, but now on top of a deeper errors-in-variables failure shared by both gates.

The strongest bounded interpretation is that residual-only adaptation is vulnerable to two distinct sensing failures: corrupted outcomes can trigger false adaptation and degrade clean-target performance, while corrupted inputs can additionally contaminate parameter identification itself. Persistence confirmation remains useful as an adaptation-rate limiter, but it is not a sensor-fault discriminator and cannot by itself protect model coefficients from repeated refitting on corrupted predictor measurements.

The claim remains limited to additive Gaussian input-sensor noise under the frozen univariate AR(1) physical process, linear OLS learner, gate settings, event timing, corruption magnitudes, and seed distribution. It does not establish behavior under biased sensors, dropouts, missing data, correlated or heavy-tailed faults, multivariate measurement error, nonlinear systems, explicit sensor-health models, robust regression, state estimation, adversarial contamination, or real digital twins.
