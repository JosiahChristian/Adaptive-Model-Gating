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
from experiment_008 import run_health_persistence_on_stream

SIGMA_REF = 0.05
TRIAD_CALIBRATION_SEEDS = range(200, 400)


def generate_triad_stream(seed, family, magnitude):
    if magnitude < 0:
        raise ValueError("magnitude must be nonnegative")
    if family not in {"primary_fault", "drift_reference_fault", "common_mode"}:
        raise ValueError(family)

    rng = Random(seed)
    x_true = [0.0] * (N_STEPS + 1)
    x_p = [0.0] * (N_STEPS + 1)
    x_r1 = [0.0] * (N_STEPS + 1)
    x_r2 = [0.0] * (N_STEPS + 1)
    ys = [0.0] * (N_STEPS + 1)
    a_values = [BASELINE_A] * (N_STEPS + 1)
    physical_eps = [0.0] * (N_STEPS + 1)
    primary_unit = [0.0] * (N_STEPS + 1)
    r1_unit = [0.0] * (N_STEPS + 1)
    r2_unit = [0.0] * (N_STEPS + 1)
    ref_fault_unit = [0.0] * (N_STEPS + 1)
    common_unit = [0.0] * (N_STEPS + 1)
    primary_fault_sigma = [0.0] * (N_STEPS + 1)
    ref1_fault_sigma = [0.0] * (N_STEPS + 1)
    common_sigma = [0.0] * (N_STEPS + 1)

    for t in range(1, N_STEPS + 1):
        x_true[t] = 0.8 * x_true[t - 1] + rng.gauss(0, 0.5)
        physical_eps[t] = rng.gauss(0, 0.5)
        primary_unit[t] = rng.gauss(0, 1.0)
        r1_unit[t] = rng.gauss(0, 1.0)
        r2_unit[t] = rng.gauss(0, 1.0)
        ref_fault_unit[t] = rng.gauss(0, 1.0)
        common_unit[t] = rng.gauss(0, 1.0)

        active = t >= EVENT_T
        x_p[t] = x_true[t]
        x_r1[t] = x_true[t] + SIGMA_REF * r1_unit[t]
        x_r2[t] = x_true[t] + SIGMA_REF * r2_unit[t]

        if family == "primary_fault" and active:
            primary_fault_sigma[t] = magnitude
            x_p[t] += magnitude * primary_unit[t]
        elif family == "drift_reference_fault" and active:
            ref1_fault_sigma[t] = magnitude
            x_r1[t] += magnitude * ref_fault_unit[t]
            a_values[t] = BASELINE_A + magnitude
        elif family == "common_mode" and active:
            common_sigma[t] = magnitude
            shared = magnitude * common_unit[t]
            x_p[t] += shared
            x_r1[t] += shared
            x_r2[t] += shared

        ys[t] = a_values[t] * x_true[t] + physical_eps[t]

    return {
        "x_primary": x_p,
        "x_ref": x_r1,
        "x_r1": x_r1,
        "x_r2": x_r2,
        "x_true": x_true,
        "y": ys,
        "a": a_values,
        "true_sigma_x": primary_fault_sigma,
        "primary_fault_sigma": primary_fault_sigma,
        "ref1_fault_sigma": ref1_fault_sigma,
        "common_sigma": common_sigma,
        "physical_epsilon": physical_eps,
        "primary_unit_noise": primary_unit,
        "reference_unit_noise": r1_unit,
        "r1_unit_noise": r1_unit,
        "r2_unit_noise": r2_unit,
        "ref_fault_unit_noise": ref_fault_unit,
        "common_unit_noise": common_unit,
    }


def rolling_pairwise_health(stream):
    out = {
        "h_p_r1": [None] * (N_STEPS + 1),
        "h_p_r2": [None] * (N_STEPS + 1),
        "h_r1_r2": [None] * (N_STEPS + 1),
    }
    buffers = {k: [] for k in out}
    for t in range(1, N_STEPS + 1):
        values = {
            "h_p_r1": (stream["x_primary"][t] - stream["x_r1"][t]) ** 2,
            "h_p_r2": (stream["x_primary"][t] - stream["x_r2"][t]) ** 2,
            "h_r1_r2": (stream["x_r1"][t] - stream["x_r2"][t]) ** 2,
        }
        for key, value in values.items():
            buffers[key].append(value)
            if len(buffers[key]) >= ROLLING_WINDOW:
                out[key][t] = mean(buffers[key][-ROLLING_WINDOW:])
    return out


def stable_triad_calibration_values(seeds=TRIAD_CALIBRATION_SEEDS):
    vals = []
    for seed in seeds:
        stream = generate_triad_stream(seed, "primary_fault", 0.0)
        health = rolling_pairwise_health(stream)
        for key in ("h_p_r1", "h_p_r2", "h_r1_r2"):
            vals.extend(v for v in health[key][1:] if v is not None)
    return vals


def calibrate_kappa3():
    return empirical_quantile(stable_triad_calibration_values(), 0.99)


def classify_triad(h_p_r1, h_p_r2, h_r1_r2, kappa3):
    if h_p_r1 is None or h_p_r2 is None or h_r1_r2 is None:
        return 0, 0, 0, "not_ready"
    pr1_bad = h_p_r1 > kappa3
    pr2_bad = h_p_r2 > kappa3
    r12_bad = h_r1_r2 > kappa3
    primary_bad = int(pr1_bad and pr2_bad and not r12_bad)
    r1_bad = int(pr1_bad and r12_bad and not pr2_bad)
    r2_bad = int(pr2_bad and r12_bad and not pr1_bad)
    if primary_bad:
        label = "primary_bad"
    elif r1_bad:
        label = "reference1_bad"
    elif r2_bad:
        label = "reference2_bad"
    else:
        label = "no_single_channel_diagnosis"
    return primary_bad, r1_bad, r2_bad, label


def _annotate_rows(rows, stream, kappa3):
    health = rolling_pairwise_health(stream)
    for row in rows:
        t = row["t"]
        pbad, r1bad, r2bad, label = classify_triad(
            health["h_p_r1"][t], health["h_p_r2"][t], health["h_r1_r2"][t], kappa3
        )
        row["x_true"] = stream["x_true"][t]
        row["x_primary"] = stream["x_primary"][t]
        row["x_r1"] = stream["x_r1"][t]
        row["x_r2"] = stream["x_r2"][t]
        row["physical_epsilon"] = stream["physical_epsilon"][t]
        row["primary_unit_noise"] = stream["primary_unit_noise"][t]
        row["r1_unit_noise"] = stream["r1_unit_noise"][t]
        row["r2_unit_noise"] = stream["r2_unit_noise"][t]
        row["ref_fault_unit_noise"] = stream["ref_fault_unit_noise"][t]
        row["common_unit_noise"] = stream["common_unit_noise"][t]
        row["primary_fault_sigma"] = stream["primary_fault_sigma"][t]
        row["ref1_fault_sigma"] = stream["ref1_fault_sigma"][t]
        row["common_sigma"] = stream["common_sigma"][t]
        row["h_p_r1"] = health["h_p_r1"][t]
        row["h_p_r2"] = health["h_p_r2"][t]
        row["h_r1_r2"] = health["h_r1_r2"][t]
        row["kappa3"] = kappa3
        row["primary_bad"] = pbad
        row["reference1_bad"] = r1bad
        row["reference2_bad"] = r2bad
        row["triad_state"] = label
        row.setdefault("triad_veto", 0)
        latent_hat = row["slope_before"] * stream["x_true"][t] + row["intercept_before"]
        row["y_hat_latent"] = latent_hat
        latent_error = stream["y"][t] - latent_hat
        row["latent_input_error"] = latent_error
        row["latent_input_sq_error"] = latent_error * latent_error
    return rows


def run_triad_persistence_on_stream(seed, condition_label, tau, kappa3, stream):
    x_p = stream["x_primary"]
    ys = stream["y"]
    model = initial_model(x_p, ys)
    sq_errors = []
    pair_buffers = {"h_p_r1": [], "h_p_r2": [], "h_r1_r2": []}
    streak = 0
    rows = []

    for t in range(INITIAL_FIT_END + 1, N_STEPS + 1):
        slope_before = model.slope
        intercept_before = model.intercept
        y_hat = model.predict(x_p[t])
        error = ys[t] - y_hat
        sq_error = error * error
        sq_errors.append(sq_error)
        rolling_mse = mean(sq_errors[-ROLLING_WINDOW:]) if len(sq_errors) >= ROLLING_WINDOW else None

        pair_values = {
            "h_p_r1": (x_p[t] - stream["x_r1"][t]) ** 2,
            "h_p_r2": (x_p[t] - stream["x_r2"][t]) ** 2,
            "h_r1_r2": (stream["x_r1"][t] - stream["x_r2"][t]) ** 2,
        }
        h = {}
        for key, value in pair_values.items():
            pair_buffers[key].append(value)
            h[key] = mean(pair_buffers[key][-ROLLING_WINDOW:]) if len(pair_buffers[key]) >= ROLLING_WINDOW else None
        pbad, r1bad, r2bad, label = classify_triad(h["h_p_r1"], h["h_p_r2"], h["h_r1_r2"], kappa3)

        residual_ready = False
        if rolling_mse is not None:
            streak = streak + 1 if rolling_mse > tau else 0
            residual_ready = streak >= PERSISTENCE_COUNT

        adapt = residual_ready and not pbad
        triad_veto = residual_ready and bool(pbad)
        if residual_ready:
            streak = 0
        if adapt:
            model = refit(x_p, ys, t)

        latent_hat = slope_before * stream["x_true"][t] + intercept_before
        latent_error = ys[t] - latent_hat
        rows.append({
            "seed": seed,
            "condition": condition_label,
            "strategy": "triad_persistence",
            "t": t,
            "x": x_p[t],
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
            "x_primary": x_p[t],
            "x_r1": stream["x_r1"][t],
            "x_r2": stream["x_r2"][t],
            "physical_epsilon": stream["physical_epsilon"][t],
            "primary_unit_noise": stream["primary_unit_noise"][t],
            "r1_unit_noise": stream["r1_unit_noise"][t],
            "r2_unit_noise": stream["r2_unit_noise"][t],
            "ref_fault_unit_noise": stream["ref_fault_unit_noise"][t],
            "common_unit_noise": stream["common_unit_noise"][t],
            "primary_fault_sigma": stream["primary_fault_sigma"][t],
            "ref1_fault_sigma": stream["ref1_fault_sigma"][t],
            "common_sigma": stream["common_sigma"][t],
            "h_p_r1": h["h_p_r1"],
            "h_p_r2": h["h_p_r2"],
            "h_r1_r2": h["h_r1_r2"],
            "kappa3": kappa3,
            "primary_bad": pbad,
            "reference1_bad": r1bad,
            "reference2_bad": r2bad,
            "triad_state": label,
            "triad_veto": int(triad_veto),
            "y_hat_latent": latent_hat,
            "latent_input_error": latent_error,
            "latent_input_sq_error": latent_error * latent_error,
        })
    return rows


def run_experiment_010_strategy(seed, family, magnitude, strategy, tau, kappa, kappa3):
    allowed = {"frozen", "continuous", "threshold", "persistence", "health_persistence", "triad_persistence"}
    if strategy not in allowed:
        raise ValueError(strategy)
    stream = generate_triad_stream(seed, family, magnitude)
    label = f"triad_{family}_{magnitude:.2f}_persistent"

    if strategy == "triad_persistence":
        return run_triad_persistence_on_stream(seed, label, tau, kappa3, stream)
    if strategy == "health_persistence":
        rows = run_health_persistence_on_stream(seed, label, tau, kappa, stream)
        return _annotate_rows(rows, stream, kappa3)

    rows = run_strategy_on_stream(
        seed, label, strategy, tau, stream["x_primary"], stream["y"], stream["a"]
    )
    return _annotate_rows(rows, stream, kappa3)
