from __future__ import annotations
from random import Random
from statistics import mean

from adaptive_model_gating import (
    BASELINE_A,
    EVENT_T,
    INITIAL_FIT_END,
    N_STEPS,
    PERSISTENCE_COUNT,
    ROLLING_WINDOW,
    empirical_quantile,
    initial_model,
    refit,
    run_strategy_on_stream,
)

SIGMA_REF = 0.05
TRANSIENT_FAULT_DURATION = 20
HEALTH_CALIBRATION_SEEDS = range(200, 400)


def generate_sensor_health_stream(
    seed,
    *,
    sigma_x=0.0,
    transient_fault_duration=None,
    delta_a=0.0,
):
    if sigma_x < 0 or delta_a < 0:
        raise ValueError("sigma_x and delta_a must be nonnegative")
    if transient_fault_duration is not None and transient_fault_duration <= 0:
        raise ValueError("transient_fault_duration must be positive or None")
    if sigma_x > 0 and delta_a > 0:
        raise ValueError("Experiment 008 cells isolate sensor fault from physical drift")

    rng = Random(seed)
    x_true = [0.0] * (N_STEPS + 1)
    x_primary = [0.0] * (N_STEPS + 1)
    x_ref = [0.0] * (N_STEPS + 1)
    ys = [0.0] * (N_STEPS + 1)
    a_values = [BASELINE_A] * (N_STEPS + 1)
    sigma_values = [0.0] * (N_STEPS + 1)
    physical_eps = [0.0] * (N_STEPS + 1)
    primary_unit = [0.0] * (N_STEPS + 1)
    reference_unit = [0.0] * (N_STEPS + 1)

    for t in range(1, N_STEPS + 1):
        x_true[t] = 0.8 * x_true[t - 1] + rng.gauss(0, 0.5)
        physical_eps[t] = rng.gauss(0, 0.5)
        primary_unit[t] = rng.gauss(0, 1.0)
        reference_unit[t] = rng.gauss(0, 1.0)

        fault_active = sigma_x > 0 and t >= EVENT_T and (
            transient_fault_duration is None
            or t < EVENT_T + transient_fault_duration
        )
        sigma_values[t] = sigma_x if fault_active else 0.0
        x_primary[t] = x_true[t] + sigma_values[t] * primary_unit[t]
        x_ref[t] = x_true[t] + SIGMA_REF * reference_unit[t]

        a_values[t] = BASELINE_A + (delta_a if delta_a > 0 and t >= EVENT_T else 0.0)
        ys[t] = a_values[t] * x_true[t] + physical_eps[t]

    return {
        "x_primary": x_primary,
        "x_ref": x_ref,
        "x_true": x_true,
        "y": ys,
        "a": a_values,
        "true_sigma_x": sigma_values,
        "physical_epsilon": physical_eps,
        "primary_unit_noise": primary_unit,
        "reference_unit_noise": reference_unit,
    }


def rolling_health_values(x_primary, x_ref):
    values = [None] * (N_STEPS + 1)
    sq = []
    for t in range(1, N_STEPS + 1):
        d = x_primary[t] - x_ref[t]
        sq.append(d * d)
        if len(sq) >= ROLLING_WINDOW:
            values[t] = mean(sq[-ROLLING_WINDOW:])
    return values


def stable_health_calibration_values(seeds=HEALTH_CALIBRATION_SEEDS):
    vals = []
    for seed in seeds:
        stream = generate_sensor_health_stream(seed)
        h = rolling_health_values(stream["x_primary"], stream["x_ref"])
        vals.extend(v for v in h[1:] if v is not None)
    return vals


def calibrate_kappa():
    return empirical_quantile(stable_health_calibration_values(), 0.99)


def _annotate_rows(rows, stream, kappa):
    health = rolling_health_values(stream["x_primary"], stream["x_ref"])
    for row in rows:
        t = row["t"]
        h = health[t]
        row["x_true"] = stream["x_true"][t]
        row["x_primary"] = stream["x_primary"][t]
        row["x_ref"] = stream["x_ref"][t]
        row["physical_epsilon"] = stream["physical_epsilon"][t]
        row["primary_unit_noise"] = stream["primary_unit_noise"][t]
        row["reference_unit_noise"] = stream["reference_unit_noise"][t]
        row["true_sigma_x"] = stream["true_sigma_x"][t]
        row["sensor_health_mse"] = h
        row["kappa"] = kappa
        row["sensor_unhealthy"] = int(h is not None and h > kappa)
        latent_hat = row["slope_before"] * stream["x_true"][t] + row["intercept_before"]
        row["y_hat_latent"] = latent_hat
        latent_error = stream["y"][t] - latent_hat
        row["latent_input_error"] = latent_error
        row["latent_input_sq_error"] = latent_error * latent_error
        row.setdefault("health_veto", 0)
    return rows


def run_health_persistence_on_stream(seed, condition_label, tau, kappa, stream):
    x_primary = stream["x_primary"]
    ys = stream["y"]
    model = initial_model(x_primary, ys)
    sq_errors = []
    disagreement_sq = []
    streak = 0
    rows = []

    for t in range(INITIAL_FIT_END + 1, N_STEPS + 1):
        slope_before = model.slope
        intercept_before = model.intercept
        y_hat = model.predict(x_primary[t])
        error = ys[t] - y_hat
        sq_error = error * error
        sq_errors.append(sq_error)
        rolling_mse = (
            mean(sq_errors[-ROLLING_WINDOW:])
            if len(sq_errors) >= ROLLING_WINDOW
            else None
        )

        disagreement = x_primary[t] - stream["x_ref"][t]
        disagreement_sq.append(disagreement * disagreement)
        health_mse = (
            mean(disagreement_sq[-ROLLING_WINDOW:])
            if len(disagreement_sq) >= ROLLING_WINDOW
            else None
        )
        sensor_unhealthy = health_mse is not None and health_mse > kappa

        residual_ready = False
        if rolling_mse is not None:
            streak = streak + 1 if rolling_mse > tau else 0
            residual_ready = streak >= PERSISTENCE_COUNT

        adapt = residual_ready and not sensor_unhealthy
        health_veto = residual_ready and sensor_unhealthy
        if residual_ready:
            streak = 0
        if adapt:
            model = refit(x_primary, ys, t)

        latent_hat = slope_before * stream["x_true"][t] + intercept_before
        latent_error = ys[t] - latent_hat
        rows.append({
            "seed": seed,
            "condition": condition_label,
            "strategy": "health_persistence",
            "t": t,
            "x": x_primary[t],
            "y": ys[t],
            "y_hat": y_hat,
            "error": error,
            "sq_error": sq_error,
            "rolling_mse": rolling_mse,
            "tau": tau,
            "adapt": int(adapt),
            "true_a": stream["a"][t],
            "slope_before": slope_before,
            "intercept_before": intercept_before,
            "slope_after": model.slope,
            "intercept_after": model.intercept,
            "x_true": stream["x_true"][t],
            "x_primary": x_primary[t],
            "x_ref": stream["x_ref"][t],
            "physical_epsilon": stream["physical_epsilon"][t],
            "primary_unit_noise": stream["primary_unit_noise"][t],
            "reference_unit_noise": stream["reference_unit_noise"][t],
            "true_sigma_x": stream["true_sigma_x"][t],
            "sensor_health_mse": health_mse,
            "kappa": kappa,
            "sensor_unhealthy": int(sensor_unhealthy),
            "health_veto": int(health_veto),
            "y_hat_latent": latent_hat,
            "latent_input_error": latent_error,
            "latent_input_sq_error": latent_error * latent_error,
        })
    return rows


def run_experiment_008_strategy(
    seed,
    cell_type,
    magnitude,
    duration,
    strategy,
    tau,
    kappa,
):
    if strategy not in {"frozen", "continuous", "threshold", "persistence", "health_persistence"}:
        raise ValueError(strategy)

    if cell_type == "fault":
        stream = generate_sensor_health_stream(
            seed,
            sigma_x=magnitude,
            transient_fault_duration=duration,
        )
        label = (
            f"health_fault_sigma_{magnitude:.2f}_persistent"
            if duration is None
            else f"health_fault_sigma_{magnitude:.2f}_transient_d_{duration}"
        )
    elif cell_type == "drift":
        if duration is not None:
            raise ValueError("Experiment 008 drift cells are persistent")
        stream = generate_sensor_health_stream(seed, delta_a=magnitude)
        label = f"health_drift_da_{magnitude:.2f}_persistent"
    else:
        raise ValueError(cell_type)

    if strategy == "health_persistence":
        return run_health_persistence_on_stream(seed, label, tau, kappa, stream)

    rows = run_strategy_on_stream(
        seed,
        label,
        strategy,
        tau,
        stream["x_primary"],
        stream["y"],
        stream["a"],
    )
    return _annotate_rows(rows, stream, kappa)
