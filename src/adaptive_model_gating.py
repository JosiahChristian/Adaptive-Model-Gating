"""Adaptive-Model-Gating experimental implementation.

Uses only the Python standard library. Experiment-specific evaluation logic follows
prospectively committed specifications under research/.
"""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from statistics import mean
from typing import Iterable

N_STEPS = 1200
EVENT_T = 401
TRANSIENT_END_T = 420
ROLLING_WINDOW = 20
REFIT_WINDOW = 100
INITIAL_FIT_START = 101
INITIAL_FIT_END = 300
PERSISTENCE_COUNT = 3
BASELINE_A = 1.5


@dataclass
class LinearModel:
    slope: float
    intercept: float

    def predict(self, x: float) -> float:
        return self.slope * x + self.intercept


def ols_fit(xs: list[float], ys: list[float]) -> LinearModel:
    if len(xs) != len(ys) or len(xs) < 2:
        raise ValueError("OLS requires equal-length x/y arrays with >=2 points")
    xbar, ybar = mean(xs), mean(ys)
    denom = sum((x - xbar) ** 2 for x in xs)
    if denom == 0:
        raise ValueError("Cannot fit OLS with zero x variance")
    slope = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys)) / denom
    return LinearModel(slope, ybar - slope * xbar)


def true_a(condition: str, t: int) -> float:
    """Experiment 001 generating parameter."""
    if condition == "stable":
        return BASELINE_A
    if condition == "transient":
        return 2.0 if EVENT_T <= t <= TRANSIENT_END_T else BASELINE_A
    if condition == "persistent":
        return 2.0 if t >= EVENT_T else BASELINE_A
    raise ValueError(f"unknown condition: {condition}")


def generate_stream(seed: int, condition: str) -> tuple[list[float], list[float], list[float]]:
    """Generate an Experiment 001 stream."""
    rng = Random(seed)
    xs = [0.0] * (N_STEPS + 1)
    ys = [0.0] * (N_STEPS + 1)
    a_values = [BASELINE_A] * (N_STEPS + 1)
    for t in range(1, N_STEPS + 1):
        eta = rng.gauss(0.0, 0.5)
        eps = rng.gauss(0.0, 0.5)
        xs[t] = 0.8 * xs[t - 1] + eta
        a_values[t] = true_a(condition, t)
        ys[t] = a_values[t] * xs[t] + eps
    return xs, ys, a_values


def generate_parameter_change_stream(
    seed: int,
    delta_a: float = 0.0,
    transient_duration: int | None = None,
) -> tuple[list[float], list[float], list[float]]:
    """Generate an Experiment 002 stream.

    transient_duration=None means persistent change. delta_a=0 produces stable.
    Random draws depend only on seed/time, so matched conditions share identical
    x/noise realizations and are numerically identical while their a_t values match.
    """
    if delta_a < 0:
        raise ValueError("delta_a must be nonnegative")
    if transient_duration is not None and transient_duration <= 0:
        raise ValueError("transient_duration must be positive or None")
    rng = Random(seed)
    xs = [0.0] * (N_STEPS + 1)
    ys = [0.0] * (N_STEPS + 1)
    a_values = [BASELINE_A] * (N_STEPS + 1)
    for t in range(1, N_STEPS + 1):
        eta = rng.gauss(0.0, 0.5)
        eps = rng.gauss(0.0, 0.5)
        xs[t] = 0.8 * xs[t - 1] + eta
        changed = False
        if delta_a > 0 and t >= EVENT_T:
            if transient_duration is None:
                changed = True
            else:
                changed = t < EVENT_T + transient_duration
        a_values[t] = BASELINE_A + delta_a if changed else BASELINE_A
        ys[t] = a_values[t] * xs[t] + eps
    return xs, ys, a_values


def initial_model(xs: list[float], ys: list[float]) -> LinearModel:
    return ols_fit(
        xs[INITIAL_FIT_START : INITIAL_FIT_END + 1],
        ys[INITIAL_FIT_START : INITIAL_FIT_END + 1],
    )


def refit(xs: list[float], ys: list[float], t: int) -> LinearModel:
    start = t - REFIT_WINDOW + 1
    return ols_fit(xs[start : t + 1], ys[start : t + 1])


def run_strategy_on_stream(
    seed: int,
    condition_label: str,
    strategy: str,
    tau: float,
    xs: list[float],
    ys: list[float],
    a_values: list[float],
) -> list[dict]:
    model = initial_model(xs, ys)
    squared_errors: list[float] = []
    exceedance_streak = 0
    rows: list[dict] = []

    for t in range(INITIAL_FIT_END + 1, N_STEPS + 1):
        slope_before = model.slope
        intercept_before = model.intercept
        y_hat = model.predict(xs[t])
        error = ys[t] - y_hat
        sq_error = error * error
        squared_errors.append(sq_error)
        rolling_mse = None
        if len(squared_errors) >= ROLLING_WINDOW:
            rolling_mse = mean(squared_errors[-ROLLING_WINDOW:])

        adapt = False
        if strategy == "continuous":
            adapt = True
        elif strategy == "threshold" and rolling_mse is not None:
            adapt = rolling_mse > tau
        elif strategy == "persistence" and rolling_mse is not None:
            if rolling_mse > tau:
                exceedance_streak += 1
            else:
                exceedance_streak = 0
            adapt = exceedance_streak >= PERSISTENCE_COUNT
        elif strategy != "frozen":
            if strategy not in {"continuous", "threshold", "persistence"}:
                raise ValueError(f"unknown strategy: {strategy}")

        if adapt:
            model = refit(xs, ys, t)
            if strategy == "persistence":
                exceedance_streak = 0

        rows.append(
            {
                "seed": seed,
                "condition": condition_label,
                "strategy": strategy,
                "t": t,
                "x": xs[t],
                "y": ys[t],
                "y_hat": y_hat,
                "error": error,
                "sq_error": sq_error,
                "rolling_mse": rolling_mse,
                "tau": tau,
                "adapt": int(adapt),
                "true_a": a_values[t],  # evaluator-only; never read by gate logic
                "slope_before": slope_before,
                "intercept_before": intercept_before,
                "slope_after": model.slope,
                "intercept_after": model.intercept,
            }
        )
    return rows


def run_strategy(seed: int, condition: str, strategy: str, tau: float) -> list[dict]:
    xs, ys, a_values = generate_stream(seed, condition)
    return run_strategy_on_stream(seed, condition, strategy, tau, xs, ys, a_values)


def run_parameter_change_strategy(
    seed: int,
    delta_a: float,
    transient_duration: int | None,
    strategy: str,
    tau: float,
) -> list[dict]:
    xs, ys, a_values = generate_parameter_change_stream(seed, delta_a, transient_duration)
    if delta_a == 0:
        label = "stable"
    elif transient_duration is None:
        label = f"persistent_da_{delta_a:.2f}"
    else:
        label = f"transient_da_{delta_a:.2f}_d_{transient_duration}"
    return run_strategy_on_stream(seed, label, strategy, tau, xs, ys, a_values)


def stable_calibration_values(seeds: Iterable[int]) -> list[float]:
    values: list[float] = []
    for seed in seeds:
        xs, ys, _ = generate_stream(seed, "stable")
        model = initial_model(xs, ys)
        sq_errors: list[float] = []
        for t in range(INITIAL_FIT_END + 1, N_STEPS + 1):
            err = ys[t] - model.predict(xs[t])
            sq_errors.append(err * err)
            if len(sq_errors) >= ROLLING_WINDOW:
                values.append(mean(sq_errors[-ROLLING_WINDOW:]))
    return values


def empirical_quantile(values: list[float], q: float) -> float:
    if not values or not 0 <= q <= 1:
        raise ValueError("nonempty values and q in [0,1] required")
    ordered = sorted(values)
    idx = int(q * (len(ordered) - 1))
    return ordered[idx]


def calibrate_tau() -> float:
    return empirical_quantile(stable_calibration_values(range(0, 200)), 0.99)


def summarize(rows: list[dict]) -> dict:
    post = [r for r in rows if EVENT_T <= r["t"] <= 600]
    transient_window = [r for r in rows if EVENT_T <= r["t"] <= TRANSIENT_END_T]
    event_and_after = [r for r in rows if r["t"] >= EVENT_T]
    adaptations = [r["t"] for r in event_and_after if r["adapt"]]
    return {
        "seed": rows[0]["seed"],
        "condition": rows[0]["condition"],
        "strategy": rows[0]["strategy"],
        "persistent_horizon_loss": sum(r["sq_error"] for r in post),
        "transient_adaptation": int(any(r["adapt"] for r in transient_window)),
        "post_event_adaptation_count": sum(r["adapt"] for r in event_and_after),
        "first_post_event_adaptation": adaptations[0] if adaptations else None,
        "adaptation_delay": (adaptations[0] - EVENT_T) if adaptations else None,
    }


def summarize_parameter_change(rows: list[dict], transient_duration: int | None) -> dict:
    post_200 = [r for r in rows if EVENT_T <= r["t"] <= 600]
    post_full = [r for r in rows if EVENT_T <= r["t"] <= N_STEPS]
    if transient_duration is None:
        true_event = [r for r in rows if r["t"] >= EVENT_T]
    else:
        event_end = EVENT_T + transient_duration - 1
        true_event = [r for r in rows if EVENT_T <= r["t"] <= event_end]
    adaptations = [r["t"] for r in post_full if r["adapt"]]
    return {
        "seed": rows[0]["seed"],
        "condition": rows[0]["condition"],
        "strategy": rows[0]["strategy"],
        "loss_401_600": sum(r["sq_error"] for r in post_200),
        "adapt_during_true_event": int(any(r["adapt"] for r in true_event)),
        "adapt_401_600": int(any(r["adapt"] for r in post_200)),
        "adapt_401_1200": int(any(r["adapt"] for r in post_full)),
        "adapt_count_401_600": sum(r["adapt"] for r in post_200),
        "adapt_count_401_1200": sum(r["adapt"] for r in post_full),
        "first_post_event_adaptation": adaptations[0] if adaptations else None,
        "adaptation_delay": (adaptations[0] - EVENT_T) if adaptations else None,
    }


def paired_bootstrap_ci(differences: list[float], seed: int = 8675309, reps: int = 10000) -> tuple[float, float]:
    rng = Random(seed)
    n = len(differences)
    estimates = []
    for _ in range(reps):
        estimates.append(mean(differences[rng.randrange(n)] for _ in range(n)))
    estimates.sort()
    return estimates[int(0.025 * reps)], estimates[int(0.975 * reps)]
