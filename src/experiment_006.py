from __future__ import annotations
from random import Random
from adaptive_model_gating import BASELINE_A, EVENT_T, N_STEPS, run_strategy_on_stream

TRANSIENT_CORRUPTION_DURATION = 20


def generate_measurement_corruption_stream(seed, sigma_c, transient_duration=None):
    if sigma_c < 0:
        raise ValueError("sigma_c must be nonnegative")
    if transient_duration is not None and transient_duration <= 0:
        raise ValueError("transient_duration must be positive or None")

    rng = Random(seed)
    xs = [0.0] * (N_STEPS + 1)
    ys = [0.0] * (N_STEPS + 1)
    clean_ys = [0.0] * (N_STEPS + 1)
    a_values = [BASELINE_A] * (N_STEPS + 1)
    sigma_values = [0.0] * (N_STEPS + 1)
    baseline_eps = [0.0] * (N_STEPS + 1)
    sensor_unit = [0.0] * (N_STEPS + 1)

    for t in range(1, N_STEPS + 1):
        xs[t] = 0.8 * xs[t - 1] + rng.gauss(0, 0.5)
        baseline_eps[t] = rng.gauss(0, 0.5)
        sensor_unit[t] = rng.gauss(0, 1.0)
        active = t >= EVENT_T and (
            transient_duration is None or t < EVENT_T + transient_duration
        )
        sigma_values[t] = sigma_c if active else 0.0
        clean_ys[t] = BASELINE_A * xs[t] + baseline_eps[t]
        ys[t] = clean_ys[t] + sigma_values[t] * sensor_unit[t]

    return xs, ys, clean_ys, a_values, sigma_values, baseline_eps, sensor_unit


def run_measurement_corruption_strategy(seed, sigma_c, transient_duration, strategy, tau):
    xs, ys, clean_ys, a_values, sigma_values, baseline_eps, sensor_unit = (
        generate_measurement_corruption_stream(seed, sigma_c, transient_duration)
    )
    duration_label = (
        "persistent" if transient_duration is None else f"transient_d_{transient_duration}"
    )
    rows = run_strategy_on_stream(
        seed,
        f"measurement_noise_sigma_{sigma_c:.2f}_{duration_label}",
        strategy,
        tau,
        xs,
        ys,
        a_values,
    )
    for row in rows:
        t = row["t"]
        row["clean_y"] = clean_ys[t]
        row["baseline_epsilon"] = baseline_eps[t]
        row["sensor_unit_noise"] = sensor_unit[t]
        row["true_sigma_c"] = sigma_values[t]
        clean_error = clean_ys[t] - row["y_hat"]
        row["clean_target_error"] = clean_error
        row["clean_target_sq_error"] = clean_error * clean_error
    return rows
