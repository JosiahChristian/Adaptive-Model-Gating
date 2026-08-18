from __future__ import annotations
from random import Random
from adaptive_model_gating import (
    BASELINE_A, EVENT_T, N_STEPS, run_strategy_on_stream,
)

TRANSIENT_MISMATCH_DURATION = 20

def generate_structural_mismatch_stream(seed, gamma, transient_duration=None):
    if gamma < 0:
        raise ValueError("gamma must be nonnegative")
    if transient_duration is not None and transient_duration <= 0:
        raise ValueError("transient_duration must be positive or None")
    rng = Random(seed)
    xs = [0.0] * (N_STEPS + 1)
    ys = [0.0] * (N_STEPS + 1)
    a_values = [BASELINE_A] * (N_STEPS + 1)
    gamma_values = [0.0] * (N_STEPS + 1)
    for t in range(1, N_STEPS + 1):
        xs[t] = 0.8 * xs[t-1] + rng.gauss(0, 0.5)
        active = t >= EVENT_T and (
            transient_duration is None or t < EVENT_T + transient_duration
        )
        gamma_values[t] = gamma if active else 0.0
        ys[t] = (
            BASELINE_A * xs[t]
            + gamma_values[t] * xs[t] * xs[t]
            + rng.gauss(0, 0.5)
        )
    return xs, ys, a_values, gamma_values

def run_structural_mismatch_strategy(seed, gamma, transient_duration, strategy, tau):
    xs, ys, a_values, gamma_values = generate_structural_mismatch_stream(
        seed, gamma, transient_duration
    )
    duration_label = "persistent" if transient_duration is None else f"transient_d_{transient_duration}"
    rows = run_strategy_on_stream(
        seed,
        f"structural_gamma_{gamma:.2f}_{duration_label}",
        strategy,
        tau,
        xs,
        ys,
        a_values,
    )
    for row in rows:
        row["true_gamma"] = gamma_values[row["t"]]
    return rows
