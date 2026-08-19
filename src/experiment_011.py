from __future__ import annotations
from random import Random
from statistics import mean, median

from adaptive_model_gating import (
    BASELINE_A, EVENT_T, INITIAL_FIT_END, N_STEPS, PERSISTENCE_COUNT,
    ROLLING_WINDOW, empirical_quantile, initial_model, refit, run_strategy_on_stream,
)
from experiment_008 import run_health_persistence_on_stream
from experiment_010 import SIGMA_REF, classify_triad, rolling_pairwise_health, run_triad_persistence_on_stream

BETA_ANCHOR = 0.8
SIGMA_ANCHOR = 0.08
ANCHOR_CALIBRATION_SEEDS = range(600, 800)
FAMILIES = {"healthy", "drift", "common_mode", "primary_fault", "drift_anchor_fault"}


def generate_experiment_011_stream(seed, family, magnitude):
    if family not in FAMILIES:
        raise ValueError(family)
    if magnitude < 0:
        raise ValueError("magnitude must be nonnegative")
    rng = Random(seed)
    keys = ("x_true", "x_primary", "x_r1", "x_r2", "z", "y", "a", "physical_epsilon",
            "r1_unit_noise", "r2_unit_noise", "anchor_unit_noise", "common_unit_noise",
            "primary_unit_noise", "anchor_fault_unit_noise", "true_sigma_x")
    s = {k: [0.0] * (N_STEPS + 1) for k in keys}
    s["a"] = [BASELINE_A] * (N_STEPS + 1)
    for t in range(1, N_STEPS + 1):
        s["x_true"][t] = 0.8 * s["x_true"][t-1] + rng.gauss(0, 0.5)
        s["physical_epsilon"][t] = rng.gauss(0, 0.5)
        s["r1_unit_noise"][t] = rng.gauss(0, 1)
        s["r2_unit_noise"][t] = rng.gauss(0, 1)
        s["anchor_unit_noise"][t] = rng.gauss(0, 1)
        s["common_unit_noise"][t] = rng.gauss(0, 1)
        s["primary_unit_noise"][t] = rng.gauss(0, 1)
        s["anchor_fault_unit_noise"][t] = rng.gauss(0, 1)
        xt = s["x_true"][t]
        s["x_primary"][t] = xt
        s["x_r1"][t] = xt + SIGMA_REF * s["r1_unit_noise"][t]
        s["x_r2"][t] = xt + SIGMA_REF * s["r2_unit_noise"][t]
        s["z"][t] = BETA_ANCHOR * xt + SIGMA_ANCHOR * s["anchor_unit_noise"][t]
        if t >= EVENT_T:
            if family == "drift":
                s["a"][t] = BASELINE_A + magnitude
            elif family == "common_mode":
                shared = magnitude * s["common_unit_noise"][t]
                s["x_primary"][t] += shared
                s["x_r1"][t] += shared
                s["x_r2"][t] += shared
                s["true_sigma_x"][t] = magnitude
            elif family == "primary_fault":
                s["x_primary"][t] += magnitude * s["primary_unit_noise"][t]
                s["true_sigma_x"][t] = magnitude
            elif family == "drift_anchor_fault":
                s["a"][t] = BASELINE_A + magnitude
                s["z"][t] += BETA_ANCHOR * magnitude * s["anchor_fault_unit_noise"][t]
        s["y"][t] = s["a"][t] * xt + s["physical_epsilon"][t]
    s["x_ref"] = s["x_r1"]
    s["reference_unit_noise"] = s["r1_unit_noise"]
    return s


def rolling_anchor_health(stream):
    g = [None] * (N_STEPS + 1)
    x_med = [0.0] * (N_STEPS + 1)
    x_a = [0.0] * (N_STEPS + 1)
    buf = []
    for t in range(1, N_STEPS + 1):
        x_med[t] = median((stream["x_primary"][t], stream["x_r1"][t], stream["x_r2"][t]))
        x_a[t] = stream["z"][t] / BETA_ANCHOR
        buf.append((x_med[t] - x_a[t]) ** 2)
        if len(buf) >= ROLLING_WINDOW:
            g[t] = mean(buf[-ROLLING_WINDOW:])
    return x_med, x_a, g


def stable_anchor_calibration_values(seeds=ANCHOR_CALIBRATION_SEEDS):
    vals = []
    for seed in seeds:
        stream = generate_experiment_011_stream(seed, "healthy", 0.0)
        _, _, g = rolling_anchor_health(stream)
        vals.extend(g[t] for t in range(101, 301) if g[t] is not None)
    return vals


def calibrate_lambda_anchor():
    return empirical_quantile(stable_anchor_calibration_values(), 0.99)


def _annotate(rows, stream, kappa3, lambda_anchor):
    h = rolling_pairwise_health(stream)
    xm, xa, g = rolling_anchor_health(stream)
    for row in rows:
        t = row["t"]
        pbad, r1bad, r2bad, label = classify_triad(h["h_p_r1"][t], h["h_p_r2"][t], h["h_r1_r2"][t], kappa3)
        ready = all(h[k][t] is not None for k in h)
        consistent = int(ready and all(h[k][t] <= kappa3 for k in h))
        mismatch = int(g[t] is not None and g[t] > lambda_anchor)
        suspect = int(consistent and mismatch)
        row.update({"x_true": stream["x_true"][t], "x_primary": stream["x_primary"][t], "x_r1": stream["x_r1"][t],
                    "x_r2": stream["x_r2"][t], "z": stream["z"][t], "x_med": xm[t], "x_a": xa[t], "g_anchor": g[t],
                    "lambda_anchor": lambda_anchor, "h_p_r1": h["h_p_r1"][t], "h_p_r2": h["h_p_r2"][t],
                    "h_r1_r2": h["h_r1_r2"][t], "kappa3": kappa3, "primary_bad": pbad,
                    "reference1_bad": r1bad, "reference2_bad": r2bad, "triad_state": label,
                    "triad_consistent": consistent, "anchor_mismatch": mismatch, "common_mode_suspect": suspect})
        row.setdefault("veto_primary_bad", 0); row.setdefault("veto_common_mode_suspect", 0); row.setdefault("independent_veto", 0)
        latent_hat = row["slope_before"] * stream["x_true"][t] + row["intercept_before"]
        row["latent_input_sq_error"] = (stream["y"][t] - latent_hat) ** 2
    return rows


def run_independent_persistence_on_stream(seed, label, tau, kappa3, lambda_anchor, stream):
    xp, ys = stream["x_primary"], stream["y"]
    model = initial_model(xp, ys); sq = []; streak = 0; rows = []
    pair = {"h_p_r1": [], "h_p_r2": [], "h_r1_r2": []}; abuf = []
    for t in range(INITIAL_FIT_END + 1, N_STEPS + 1):
        sb, ib = model.slope, model.intercept
        yh = model.predict(xp[t]); err = ys[t] - yh; se = err * err; sq.append(se)
        rmse = mean(sq[-ROLLING_WINDOW:]) if len(sq) >= ROLLING_WINDOW else None
        pv = {"h_p_r1": (xp[t]-stream["x_r1"][t])**2, "h_p_r2": (xp[t]-stream["x_r2"][t])**2,
              "h_r1_r2": (stream["x_r1"][t]-stream["x_r2"][t])**2}
        hv = {}
        for k,v in pv.items():
            pair[k].append(v); hv[k] = mean(pair[k][-ROLLING_WINDOW:]) if len(pair[k]) >= ROLLING_WINDOW else None
        pbad, r1bad, r2bad, state = classify_triad(hv["h_p_r1"], hv["h_p_r2"], hv["h_r1_r2"], kappa3)
        xm = median((xp[t], stream["x_r1"][t], stream["x_r2"][t])); xa = stream["z"][t]/BETA_ANCHOR
        abuf.append((xm-xa)**2); g = mean(abuf[-ROLLING_WINDOW:]) if len(abuf) >= ROLLING_WINDOW else None
        consistent = int(g is not None and all(hv[k] is not None and hv[k] <= kappa3 for k in hv))
        mismatch = int(g is not None and g > lambda_anchor); suspect = int(consistent and mismatch)
        if rmse is not None: streak = streak + 1 if rmse > tau else 0
        ready = streak >= PERSISTENCE_COUNT
        veto_p = int(ready and pbad); veto_c = int(ready and suspect); veto = int(veto_p or veto_c); adapt = int(ready and not veto)
        if ready: streak = 0
        if adapt: model = refit(xp, ys, t)
        latent_hat = sb * stream["x_true"][t] + ib
        rows.append({"seed": seed, "condition": label, "strategy": "independent_persistence", "t": t, "x": xp[t], "y": ys[t],
                     "y_hat": yh, "error": err, "sq_error": se, "rolling_mse": rmse, "tau": tau, "adapt": adapt,
                     "true_a": stream["a"][t], "slope_before": sb, "intercept_before": ib, "slope_after": model.slope,
                     "intercept_after": model.intercept, "x_true": stream["x_true"][t], "x_primary": xp[t],
                     "x_r1": stream["x_r1"][t], "x_r2": stream["x_r2"][t], "z": stream["z"][t], "x_med": xm, "x_a": xa,
                     "g_anchor": g, "lambda_anchor": lambda_anchor, "h_p_r1": hv["h_p_r1"], "h_p_r2": hv["h_p_r2"],
                     "h_r1_r2": hv["h_r1_r2"], "kappa3": kappa3, "primary_bad": pbad, "reference1_bad": r1bad,
                     "reference2_bad": r2bad, "triad_state": state, "triad_consistent": consistent, "anchor_mismatch": mismatch,
                     "common_mode_suspect": suspect, "veto_primary_bad": veto_p, "veto_common_mode_suspect": veto_c,
                     "independent_veto": veto, "latent_input_sq_error": (ys[t]-latent_hat)**2})
    return rows


def run_experiment_011_strategy(seed, family, magnitude, strategy, tau, kappa, kappa3, lambda_anchor):
    allowed = {"frozen", "continuous", "threshold", "persistence", "health_persistence", "triad_persistence", "independent_persistence"}
    if strategy not in allowed: raise ValueError(strategy)
    stream = generate_experiment_011_stream(seed, family, magnitude)
    label = f"experiment011_{family}_{magnitude:.2f}"
    if strategy == "independent_persistence":
        return run_independent_persistence_on_stream(seed, label, tau, kappa3, lambda_anchor, stream)
    if strategy == "triad_persistence":
        return _annotate(run_triad_persistence_on_stream(seed, label, tau, kappa3, stream), stream, kappa3, lambda_anchor)
    if strategy == "health_persistence":
        return _annotate(run_health_persistence_on_stream(seed, label, tau, kappa, stream), stream, kappa3, lambda_anchor)
    rows = run_strategy_on_stream(seed, label, strategy, tau, stream["x_primary"], stream["y"], stream["a"])
    return _annotate(rows, stream, kappa3, lambda_anchor)
