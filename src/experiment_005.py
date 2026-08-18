from __future__ import annotations
from random import Random
from adaptive_model_gating import BASELINE_A, EVENT_T, N_STEPS, run_strategy_on_stream

TRANSIENT_SHIFT_DURATION = 20


def generate_covariate_shift_stream(seed, mu, transient_duration=None):
    if mu < 0:
        raise ValueError("mu must be nonnegative")
    if transient_duration is not None and transient_duration <= 0:
        raise ValueError("transient_duration must be positive or None")

    rng = Random(seed)
    zs = [0.0] * (N_STEPS + 1)
    xs = [0.0] * (N_STEPS + 1)
    ys = [0.0] * (N_STEPS + 1)
    a_values = [BASELINE_A] * (N_STEPS + 1)
    mu_values = [0.0] * (N_STEPS + 1)

    for t in range(1, N_STEPS + 1):
        zs[t] = 0.8 * zs[t - 1] + rng.gauss(0, 0.5)
        active = t >= EVENT_T and (
            transient_duration is None or t < EVENT_T + transient_duration
        )
        mu_values[t] = mu if active else 0.0
        xs[t] = zs[t] + mu_values[t]
        ys[t] = BASELINE_A * xs[t] + rng.gauss(0, 0.5)

    return xs, ys, a_values, mu_values, zs


def run_covariate_shift_strategy(seed, mu, transient_duration, strategy, tau):
    xs, ys, a_values, mu_values, zs = generate_covariate_shift_stream(
        seed, mu, transient_duration
    )
    duration_label = (
        "persistent" if transient_duration is None else f"transient_d_{transient_duration}"
    )
    rows = run_strategy_on_stream(
        seed,
        f"covariate_mu_{mu:.2f}_{duration_label}",
        strategy,
        tau,
        xs,
        ys,
        a_values,
    )
    for row in rows:
        t = row["t"]
        row["true_mu"] = mu_values[t]
        row["latent_z"] = zs[t]
    return rows
