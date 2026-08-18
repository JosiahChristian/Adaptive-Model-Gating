# Experiment 008 Evidence Record

## Provenance

- Frozen specification: `research/experiment_008_spec.md`
- Evaluation request: `evaluation_requests/experiment_008.request`
- GitHub Actions run: `32149026892`
- Producing commit: `630c80eb984370afb08933b2db661738486693cf`
- Completed evidence pointer: issue `#11`
- Artifact: `experiment-008-evidence`
- Artifact ID: `9329725474`
- GitHub-recorded artifact SHA-256: `a6293808f6cfbbf59c2e85fc96e707cef1c385de63ca340db0f3fecfb75b5f66`
- Independently downloaded artifact SHA-256: `a6293808f6cfbbf59c2e85fc96e707cef1c385de63ca340db0f3fecfb75b5f66`
- `test` job: completed / success
- `evaluate` job: completed / success

## Frozen design

- Residual threshold `tau = 0.4749575582753968`
- Sensor-health threshold `kappa = 0.004715841027139986`
- Health calibration seeds: `200..399`
- Evaluation seeds: `8000..8199`
- Reference-sensor SD: `0.05`
- Fault cells: `sigma_x ∈ {0.25,0.5,1.0}` × transient/persistent
- Genuine-drift cells: `delta_a ∈ {0.25,0.5,1.0}` persistent
- Strategies: frozen, continuous, threshold, persistence, health_persistence

## Independent audit

The downloaded evidence passed the required checks:

- `seed_summary.csv` contains exactly `9,000` rows = 9 cells × 5 strategies × 200 seeds.
- Every cell-strategy group contains exactly 200 seeds covering `8000..8199`.
- `audit_trace_seeds_8000_8004.csv` contains exactly `202,500` rows = 5 audit seeds × 9 cells × 5 strategies × 900 scored time steps.
- Within each audited seed/cell/time point, all strategies share identical latent state, physical noise, primary-sensor noise, reference-sensor noise, primary measurement, reference measurement, true slope, and true fault magnitude.
- The physical-response equation, primary-sensor equation, and reference-sensor equation reproduce to floating-point precision.
- Learner input equals `x_primary` exactly; the learner/refit path does not receive `x_true` or `x_ref`.
- The rolling health statistic reproduces as the 20-sample mean squared primary/reference disagreement.
- `kappa` independently reproduces exactly from stable calibration seeds `200..399` using 236,200 eligible rolling values and the frozen empirical 0.99 quantile convention. No evaluation seed is used in this calibration.
- Test-then-train chronology and residual-gate parameters remain unchanged.
- Health-persistence uses the ordinary 3-exceedance residual persistence condition, vetoes a ready refit only when `H_t > kappa`, and resets the persistence streak on both successful adaptation and health veto as prospectively specified.
- Reported cell means and paired contrasts reproduce from seed-level evidence; the prespecified bootstrap intervals are consistent with the frozen runner.

## Key evidence

### Transient sensor-fault rejection

Health-aware persistence reduces adaptation during the true fault interval relative to ordinary persistence:

- `sigma_x=0.25`: `0.190 -> 0.000`, paired difference `-0.190`, 95% CI `[-0.245,-0.135]`.
- `sigma_x=0.50`: `0.915 -> 0.000`, paired difference `-0.915`, 95% CI `[-0.950,-0.875]`.
- `sigma_x=1.00`: `1.000 -> 0.000`, paired difference `-1.000`, 95% CI `[-1.000,-1.000]`.

The health monitor flags at least once during `t=401..420` in every fault stream at all three magnitudes.

### Persistent sensor-fault coefficient integrity

Ordinary persistence is strongly contaminated by repeated refitting on faulty predictors, while health-aware persistence preserves the physical slope near the frozen reference:

- `sigma_x=0.25`: persistence abs slope error `0.1363`; health-aware `0.0371`; difference `-0.0992`, 95% CI `[-0.1108,-0.0875]`.
- `sigma_x=0.50`: persistence `0.4304`; health-aware `0.0371`; difference `-0.3933`, 95% CI `[-0.4107,-0.3755]`.
- `sigma_x=1.00`: persistence `0.9214`; health-aware `0.0371`; difference `-0.8843`, 95% CI `[-0.9026,-0.8663]`.

Health-aware persistence performs zero post-event refits in all three persistent-fault cells, versus mean ordinary-persistence burdens of `51.345`, `210.230`, and `258.920`.

This coefficient protection comes with worse operational loss during persistent faults because the preserved physical model must still predict from the corrupted primary sensor. Conversely, evaluator-only latent-input loss is dramatically better because the coefficients remain physically correct. Operational and physical-integrity endpoints therefore measure different objectives and must not be conflated.

### Genuine-drift retention

The health-aware intervention preserves ordinary persistence adaptation behavior almost exactly under healthy sensing:

- `delta_a=0.25`: adaptation by `t=420` `0.075` vs `0.075`; paired delay difference `0`; loss difference `+0.0073`, 95% CI `[0,0.0219]`.
- `delta_a=0.50`: adaptation `0.280` vs `0.285`; delay difference `+0.05` steps; loss difference `+0.0233`, 95% CI `[0.0002,0.0555]`.
- `delta_a=1.00`: adaptation `0.810` vs `0.810`; delay difference `+0.03` steps; loss difference `+0.0598`, 95% CI `[0.0197,0.1094]`.

The health monitor's long-horizon flag fraction in genuine-drift cells is about `0.0095`, consistent with the calibrated high-quantile false-alarm design rather than systematic confusion of physical drift with sensor failure.

## Scientifically bounded conclusion

Experiment 008 supports a bounded intervention result: with an independent low-noise redundant reference sensor, separating sensor-health evidence from residual model-error evidence can prevent the input-sensor-fault adaptations and coefficient contamination exposed by Experiment 007 while retaining essentially the same genuine-drift adaptation behavior as ordinary persistence gating.

The intervention is not cost-free. In genuine-drift cells its operational loss is slightly higher than ordinary persistence, with statistically resolved positive differences at moderate and strong drift, although the absolute differences are very small relative to total loss and adaptation probabilities/delays remain almost unchanged. Therefore the result should be described as a strong fault-discrimination benefit with a small responsiveness/prediction cost, not as universal dominance.

The benefit depends on additional sensing information unavailable to Experiments 001–007. It does not establish general sensor-fault diagnosis or robustness to common-mode faults, a biased/drifting reference sensor, correlated failures, dropouts, multivariate systems, nonlinear dynamics, adversarial faults, or real digital twins.
