#!/usr/bin/env python3
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adaptive_model_gating import BASELINE_A, EVENT_T, calibrate_tau, paired_bootstrap_ci
from experiment_008 import calibrate_kappa, run_experiment_008_strategy

RESULTS = ROOT / "results" / "experiment_008"
STRATEGIES = ["frozen", "continuous", "threshold", "persistence", "health_persistence"]
FAULT_SIGMAS = [0.25, 0.5, 1.0]
DRIFT_DELTAS = [0.25, 0.5, 1.0]
FAULT_CLASSES = [("transient_fault", 20), ("persistent_fault", None)]
SEEDS = list(range(8000, 8200))
AUDIT = set(range(8000, 8005))


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)


def ci(values, seed):
    return list(paired_bootstrap_ci(values, seed=seed, reps=10000))


def summarize_rows(rows, cell_type, magnitude, event_class):
    post200 = [r for r in rows if 401 <= r["t"] <= 600]
    postall = [r for r in rows if r["t"] >= 401]
    onset20 = [r for r in rows if 401 <= r["t"] <= 420]
    adaptations = [r["t"] for r in postall if r["adapt"]]
    health_flags = [r["t"] for r in postall if r["sensor_unhealthy"]]
    if cell_type == "fault":
        target_slope = BASELINE_A
    else:
        target_slope = BASELINE_A + magnitude
    final_slope = rows[-1]["slope_after"]
    return {
        "seed": rows[0]["seed"],
        "cell_type": cell_type,
        "magnitude": magnitude,
        "event_class": event_class,
        "strategy": rows[0]["strategy"],
        "operational_loss_401_600": sum(r["sq_error"] for r in post200),
        "operational_loss_401_1200": sum(r["sq_error"] for r in postall),
        "latent_input_loss_401_600": sum(r["latent_input_sq_error"] for r in post200),
        "latent_input_loss_401_1200": sum(r["latent_input_sq_error"] for r in postall),
        "adapt_401_420": int(any(r["adapt"] for r in onset20)),
        "first_post_event_adaptation": adaptations[0] if adaptations else "",
        "adaptation_delay": adaptations[0] - EVENT_T if adaptations else "",
        "adapt_count_401_600": sum(r["adapt"] for r in post200),
        "adapt_count_401_1200": sum(r["adapt"] for r in postall),
        "health_veto_count_401_1200": sum(r["health_veto"] for r in postall),
        "health_flag_401_420": int(any(r["sensor_unhealthy"] for r in onset20)),
        "first_post_event_health_flag": health_flags[0] if health_flags else "",
        "health_flag_delay": health_flags[0] - EVENT_T if health_flags else "",
        "health_flag_fraction_401_1200": sum(r["sensor_unhealthy"] for r in postall) / len(postall),
        "final_slope": final_slope,
        "final_slope_error_abs": abs(final_slope - target_slope),
        "target_slope": target_slope,
    }


def paired_map(cell_rows):
    out = {}
    for seed in SEEDS:
        out[seed] = {
            s: next(r for r in cell_rows if r["seed"] == seed and r["strategy"] == s)
            for s in STRATEGIES
        }
    return out


def strategy_means(cell_rows, field):
    return {
        s: sum(r[field] for r in cell_rows if r["strategy"] == s) / len(SEEDS)
        for s in STRATEGIES
    }


def main():
    tau = calibrate_tau()
    kappa = calibrate_kappa()
    summaries = []
    audit = []

    for sigma_x in FAULT_SIGMAS:
        for event_class, duration in FAULT_CLASSES:
            for seed in SEEDS:
                for strategy in STRATEGIES:
                    rows = run_experiment_008_strategy(
                        seed, "fault", sigma_x, duration, strategy, tau, kappa
                    )
                    summaries.append(summarize_rows(rows, "fault", sigma_x, event_class))
                    if seed in AUDIT:
                        for r in rows:
                            audit.append(dict(r, cell_type="fault", magnitude=sigma_x, event_class=event_class))

    for delta_a in DRIFT_DELTAS:
        for seed in SEEDS:
            for strategy in STRATEGIES:
                rows = run_experiment_008_strategy(
                    seed, "drift", delta_a, None, strategy, tau, kappa
                )
                summaries.append(summarize_rows(rows, "drift", delta_a, "persistent_drift"))
                if seed in AUDIT:
                    for r in rows:
                        audit.append(dict(r, cell_type="drift", magnitude=delta_a, event_class="persistent_drift"))

    write_csv(RESULTS / "seed_summary.csv", summaries)
    write_csv(RESULTS / "audit_trace_seeds_8000_8004.csv", audit)

    cells = []
    cell_specs = []
    for sigma_x in FAULT_SIGMAS:
        for event_class, duration in FAULT_CLASSES:
            cell_specs.append(("fault", sigma_x, event_class, duration))
    for delta_a in DRIFT_DELTAS:
        cell_specs.append(("drift", delta_a, "persistent_drift", None))

    for cell_index, (cell_type, magnitude, event_class, _duration) in enumerate(cell_specs):
        c = [
            r for r in summaries
            if r["cell_type"] == cell_type
            and r["magnitude"] == magnitude
            and r["event_class"] == event_class
        ]
        paired = paired_map(c)
        base_seed = 2026081808 + cell_index * 1000
        report = {
            "cell_type": cell_type,
            "magnitude": magnitude,
            "event_class": event_class,
            "mean_operational_loss_401_600": strategy_means(c, "operational_loss_401_600"),
            "mean_latent_input_loss_401_600": strategy_means(c, "latent_input_loss_401_600"),
            "adapt_401_420_rate": strategy_means(c, "adapt_401_420"),
            "mean_adapt_count_401_1200": strategy_means(c, "adapt_count_401_1200"),
            "mean_health_flag_fraction_401_1200": strategy_means(c, "health_flag_fraction_401_1200"),
            "health_flag_401_420_rate": strategy_means(c, "health_flag_401_420"),
            "mean_health_veto_count_401_1200": strategy_means(c, "health_veto_count_401_1200"),
            "mean_final_slope": strategy_means(c, "final_slope"),
            "mean_final_slope_error_abs": strategy_means(c, "final_slope_error_abs"),
        }

        if cell_type == "fault" and event_class == "transient_fault":
            diffs = [
                paired[s]["health_persistence"]["adapt_401_420"]
                - paired[s]["persistence"]["adapt_401_420"]
                for s in SEEDS
            ]
            report["primary_health_minus_persistence_adaptation_rate_difference"] = sum(diffs) / len(diffs)
            report["primary_bootstrap_95_ci"] = ci(diffs, base_seed)

        elif cell_type == "fault" and event_class == "persistent_fault":
            slope_diffs = [
                paired[s]["health_persistence"]["final_slope_error_abs"]
                - paired[s]["persistence"]["final_slope_error_abs"]
                for s in SEEDS
            ]
            operational_diffs = [
                paired[s]["health_persistence"]["operational_loss_401_600"]
                - paired[s]["persistence"]["operational_loss_401_600"]
                for s in SEEDS
            ]
            latent_diffs = [
                paired[s]["health_persistence"]["latent_input_loss_401_600"]
                - paired[s]["persistence"]["latent_input_loss_401_600"]
                for s in SEEDS
            ]
            burden_diffs = [
                paired[s]["health_persistence"]["adapt_count_401_1200"]
                - paired[s]["persistence"]["adapt_count_401_1200"]
                for s in SEEDS
            ]
            report["primary_health_minus_persistence_final_slope_error_mean_difference"] = sum(slope_diffs) / len(slope_diffs)
            report["primary_bootstrap_95_ci"] = ci(slope_diffs, base_seed)
            report["health_minus_persistence_operational_loss_mean_difference"] = sum(operational_diffs) / len(operational_diffs)
            report["operational_loss_bootstrap_95_ci"] = ci(operational_diffs, base_seed + 1)
            report["health_minus_persistence_latent_input_loss_mean_difference"] = sum(latent_diffs) / len(latent_diffs)
            report["latent_input_loss_bootstrap_95_ci"] = ci(latent_diffs, base_seed + 2)
            report["health_minus_persistence_burden_mean_difference"] = sum(burden_diffs) / len(burden_diffs)
            report["burden_bootstrap_95_ci"] = ci(burden_diffs, base_seed + 3)

        else:
            loss_diffs = [
                paired[s]["health_persistence"]["operational_loss_401_600"]
                - paired[s]["persistence"]["operational_loss_401_600"]
                for s in SEEDS
            ]
            adapt_diffs = [
                paired[s]["health_persistence"]["adapt_401_420"]
                - paired[s]["persistence"]["adapt_401_420"]
                for s in SEEDS
            ]
            delay_diffs = []
            for s in SEEDS:
                hp = paired[s]["health_persistence"]["adaptation_delay"]
                p = paired[s]["persistence"]["adaptation_delay"]
                if hp != "" and p != "":
                    delay_diffs.append(hp - p)
            report["primary_health_minus_persistence_operational_loss_mean_difference"] = sum(loss_diffs) / len(loss_diffs)
            report["primary_bootstrap_95_ci"] = ci(loss_diffs, base_seed)
            report["health_minus_persistence_adaptation_rate_difference_401_420"] = sum(adapt_diffs) / len(adapt_diffs)
            report["adaptation_rate_bootstrap_95_ci"] = ci(adapt_diffs, base_seed + 1)
            if delay_diffs:
                report["paired_adaptation_delay_difference_among_both_adapting"] = sum(delay_diffs) / len(delay_diffs)
                report["paired_adaptation_delay_bootstrap_95_ci"] = ci(delay_diffs, base_seed + 2)
                report["n_pairs_for_delay"] = len(delay_diffs)
        cells.append(report)

    final_report = {
        "tau": tau,
        "kappa": kappa,
        "health_calibration_seeds": [200, 399],
        "evaluation_seeds": [8000, 8199],
        "n_seeds_per_cell": len(SEEDS),
        "sigma_ref": 0.05,
        "fault_sigma_x_values": FAULT_SIGMAS,
        "drift_delta_a_values": DRIFT_DELTAS,
        "strategies": STRATEGIES,
        "cells": cells,
        "audit_seeds": sorted(AUDIT),
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "report.json").write_text(json.dumps(final_report, indent=2) + "\n")
    print(json.dumps(final_report, indent=2))


if __name__ == "__main__":
    main()
