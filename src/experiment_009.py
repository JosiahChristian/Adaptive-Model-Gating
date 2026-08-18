from __future__ import annotations
from random import Random

from adaptive_model_gating import BASELINE_A, EVENT_T, N_STEPS
from experiment_008 import SIGMA_REF, calibrate_kappa, run_health_persistence_on_stream, _annotate_rows
from adaptive_model_gating import run_strategy_on_stream


def generate_experiment_009_stream(seed, family, magnitude):
    if magnitude < 0:
        raise ValueError("magnitude must be nonnegative")
    if family not in {"common_mode", "drift_reference_fault"}:
        raise ValueError(family)

    rng = Random(seed)
    x_true = [0.0] * (N_STEPS + 1)
    x_primary = [0.0] * (N_STEPS + 1)
    x_ref = [0.0] * (N_STEPS + 1)
    ys = [0.0] * (N_STEPS + 1)
    a_values = [BASELINE_A] * (N_STEPS + 1)
    physical_eps = [0.0] * (N_STEPS + 1)
    common_unit = [0.0] * (N_STEPS + 1)
    reference_unit = [0.0] * (N_STEPS + 1)
    reference_fault_unit = [0.0] * (N_STEPS + 1)
    true_sigma_cm = [0.0] * (N_STEPS + 1)
    true_sigma_ref_fault = [0.0] * (N_STEPS + 1)

    for t in range(1, N_STEPS + 1):
        x_true[t] = 0.8 * x_true[t - 1] + rng.gauss(0, 0.5)
        physical_eps[t] = rng.gauss(0, 0.5)
        common_unit[t] = rng.gauss(0, 1.0)
        reference_unit[t] = rng.gauss(0, 1.0)
        reference_fault_unit[t] = rng.gauss(0, 1.0)
        active = t >= EVENT_T

        if family == "common_mode":
            true_sigma_cm[t] = magnitude if active else 0.0
            shared = true_sigma_cm[t] * common_unit[t]
            x_primary[t] = x_true[t] + shared
            x_ref[t] = x_true[t] + shared + SIGMA_REF * reference_unit[t]
            a_values[t] = BASELINE_A
        else:
            true_sigma_ref_fault[t] = magnitude if active else 0.0
            x_primary[t] = x_true[t]
            x_ref[t] = (
                x_true[t]
                + SIGMA_REF * reference_unit[t]
                + true_sigma_ref_fault[t] * reference_fault_unit[t]
            )
            a_values[t] = BASELINE_A + (magnitude if active else 0.0)

        ys[t] = a_values[t] * x_true[t] + physical_eps[t]

    return {
        "x_primary": x_primary,
        "x_ref": x_ref,
        "x_true": x_true,
        "y": ys,
        "a": a_values,
        "true_sigma_x": true_sigma_cm,
        "true_sigma_cm": true_sigma_cm,
        "true_sigma_ref_fault": true_sigma_ref_fault,
        "physical_epsilon": physical_eps,
        "primary_unit_noise": common_unit,
        "reference_unit_noise": reference_unit,
        "reference_fault_unit_noise": reference_fault_unit,
    }


def _extra_annotations(rows, stream, family, magnitude):
    for row in rows:
        t = row["t"]
        row["family"] = family
        row["magnitude"] = magnitude
        row["true_sigma_cm"] = stream["true_sigma_cm"][t]
        row["true_sigma_ref_fault"] = stream["true_sigma_ref_fault"][t]
        row["reference_fault_unit_noise"] = stream["reference_fault_unit_noise"][t]
        row["sensor_disagreement"] = stream["x_primary"][t] - stream["x_ref"][t]
    return rows


def run_experiment_009_strategy(seed, family, magnitude, strategy, tau, kappa=None):
    if strategy not in {"frozen", "continuous", "threshold", "persistence", "health_persistence"}:
        raise ValueError(strategy)
    if kappa is None:
        kappa = calibrate_kappa()

    stream = generate_experiment_009_stream(seed, family, magnitude)
    label = f"exp009_{family}_{magnitude:.2f}_persistent"

    if strategy == "health_persistence":
        rows = run_health_persistence_on_stream(seed, label, tau, kappa, stream)
    else:
        rows = run_strategy_on_stream(
            seed,
            label,
            strategy,
            tau,
            stream["x_primary"],
            stream["y"],
            stream["a"],
        )
        rows = _annotate_rows(rows, stream, kappa)

    return _extra_annotations(rows, stream, family, magnitude)
