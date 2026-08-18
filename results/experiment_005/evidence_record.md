# Experiment 005 Evidence Record

## Provenance

- Frozen specification: `research/experiment_005_spec.md`
- Evaluation request: `evaluation_requests/experiment_005.request`
- GitHub Actions run: `32138775700`
- Producing commit: `a817d99554d102185ea54349f76541b05078bba2`
- Completed evidence pointer: issue `#6`
- Artifact: `experiment-005-evidence`
- Artifact ID: `9325237058`
- GitHub-recorded artifact SHA-256: `f645ebc8426c639fbdb21696b2b24ffe601022fafaba1e1202477d2639f3625d`
- Downloaded artifact SHA-256 independently verified equal to the GitHub digest.
- `test` job: completed / success
- `evaluate` job: completed / success

Contained files and independently verified SHA-256 values:

- `report.json` — `87ae7b8dacbbabc283ae1e11c9bc63ac8b0a1d3fc3a176c25fb60f8443875b9a`
- `seed_summary.csv` — `b57715f4293935357bdf4fac523bbaf88df326c34f35481ccfcc4420514d32c1`
- `audit_trace_seeds_5000_5004.csv` — `001f9ec29603f1335d2fa1ab1aed091f5f731e7b0d0a30806bcdfa33831fa1d0`

## Frozen design

- `tau = 0.4749575582753968`
- evaluation seeds `5000..5199`
- 200 independent seeds per cell
- `mu ∈ {0.5, 1.0, 2.0}`
- 20-step transient and persistent covariate-shift classes
- latent input `z_t = 0.8 z_{t-1} + eta_t`, `eta_t ~ N(0,0.5^2)`
- observed input `x_t = z_t + true_mu_t`
- unchanged conditional law `y_t = 1.5 x_t + epsilon_t`, `epsilon_t ~ N(0,0.5^2)`
- strategies: frozen, continuous, threshold, persistence
- primary transient contrast: persistence minus threshold adaptation indicator over `t=401..420`
- primary persistent contrast: persistence minus threshold loss over `t=401..600`
- persistent burden contrast: persistence minus threshold adaptation count through `t=1200`

## Independent audit

The downloaded evidence passed these checks:

- `seed_summary.csv` contains exactly `4,800` rows = 6 cells × 4 strategies × 200 seeds.
- Every cell-strategy group contains exactly 200 seeds covering `5000..5199`.
- `audit_trace_seeds_5000_5004.csv` contains exactly `108,000` rows = 5 audit seeds × 6 cells × 4 strategies × 900 scored time steps.
- Within audited seed/cell/time points, all four strategies share identical `x`, `y`, `latent_z`, `true_mu`, and `true_a` values.
- Matched transient and persistent streams are identical through `t=420` within each audited `seed, mu` pair.
- `x_t = latent_z_t + true_mu_t` holds to floating-point precision.
- `true_mu` is zero before `t=401`, active exactly on `t=401..420` in transient cells, and active through `t=1200` in persistent cells.
- `true_a` remains exactly `1.5` throughout; there is no response-slope change.
- A single frozen `tau = 0.4749575582753968` is used throughout the audit trace.
- Test-then-train chronology reproduces as `y_hat = slope_before * x + intercept_before` to numerical precision.
- Recomputed cell means, adaptation rates, paired contrasts, and all prespecified bootstrap intervals reproduce the report; numerical endpoint differences are at floating-point representation scale only (≤ about `3.1e-16`).

## Cell-level evidence

| mu | class | threshold adapt 401-420 | persistence adapt 401-420 | P−T adapt diff | 95% CI | threshold loss 401-600 | persistence loss 401-600 | P−T loss | loss 95% CI | threshold burden 401-1200 | persistence burden 401-1200 | P−T burden | burden 95% CI |
|---:|:---|---:|---:|---:|:---|---:|---:|---:|:---|---:|---:|---:|:---|
| 0.5 | transient | 0.020 | 0.010 | -0.010 | [-0.025, 0.000] | 50.372 | 50.264 | — | — | 7.755 | 1.820 | — | — |
| 0.5 | persistent | 0.020 | 0.010 | — | — | 50.401 | 50.340 | -0.061 | [-0.135, 0.002] | 7.970 | 1.845 | -6.125 | [-7.160, -5.120] |
| 1.0 | transient | 0.020 | 0.005 | -0.015 | [-0.035, 0.000] | 50.370 | 50.283 | — | — | 7.720 | 1.815 | — | — |
| 1.0 | persistent | 0.020 | 0.005 | — | — | 50.553 | 50.592 | +0.039 | [-0.068, 0.159] | 8.155 | 1.925 | -6.230 | [-7.305, -5.245] |
| 2.0 | transient | 0.030 | 0.010 | -0.020 | [-0.040, -0.005] | 50.407 | 50.363 | — | — | 7.665 | 1.825 | — | — |
| 2.0 | persistent | 0.030 | 0.010 | — | — | 51.359 | 51.390 | +0.031 | [-0.067, 0.133] | 8.465 | 2.105 | -6.360 | [-7.480, -5.305] |

The frozen strategy remains an important reference because the true conditional response mechanism never changes. Over `t=401..600`, frozen mean loss is `50.265`, `50.496`, and `51.503` in the three persistent cells, respectively. Adaptive strategies do not show a systematic predictive advantage over this unchanged-model reference.

## Scientifically bounded conclusion

Experiment 005 constrains rather than straightforwardly extends the earlier responsiveness-versus-conservatism phenomenon.

Under the specified additive mean shifts in `P(x)` with exactly unchanged `P(y|x)`, both residual gates are largely insensitive during the true shift interval: threshold adaptation rates are only `0.02`, `0.02`, and `0.03`, while persistence rates are `0.01`, `0.005`, and `0.01`. Only the strongest transient cell has a paired 95% interval fully below zero; the two smaller-shift intervals include zero at the upper endpoint.

Across persistent cells, persistence substantially reduces long-horizon adaptation burden relative to threshold gating, with all three paired burden intervals strictly below zero. However, the persistence-minus-threshold prediction-loss intervals all include zero. Thus there is no supported persistent-cell prediction-loss separation between the two residual gates under this frozen pure covariate-shift family.

The strongest interpretation is that the frozen residual detector is relatively insensitive to these additive operating-region shifts when the conditional response law remains correct. Persistence still suppresses accumulated false/redundant refitting over long horizons, but the pronounced responsiveness cost seen under true conditional drift and structural mismatch is not reproduced here.

This is scientifically useful negative evidence. It indicates that the previously observed tradeoff is not merely an automatic consequence of any distributional change in the input stream.

The claim remains limited to the specified additive mean shifts, latent AR(1) process, Gaussian noise, correctly specified linear learner, gate settings, magnitudes, durations, and seed distribution. No conclusion is established for variance shifts, changing autocorrelation, support violations, multivariate shift, label shift, sensor faults, adversarial manipulation, nonlinear dynamics, real digital twins, or arbitrary concept drift.
