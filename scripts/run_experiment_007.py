#!/usr/bin/env python3
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adaptive_model_gating import EVENT_T, calibrate_tau, paired_bootstrap_ci
from experiment_007 import run_input_sensor_corruption_strategy

RESULTS = ROOT / "results" / "experiment_007"
STRATEGIES = ["frozen", "continuous", "threshold", "persistence"]
SIGMAS = [0.25, 0.5, 1.0]
CELLS = [("transient", 20), ("persistent", None)]
SEEDS = list(range(7000, 7200))
AUDIT = set(range(7000, 7005))


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)


def ci(values, seed):
    return list(paired_bootstrap_ci(values, seed=seed, reps=10000))


def main():
    tau = calibrate_tau()
    summaries = []
    audit = []

    for sigma_x in SIGMAS:
        for event_class, duration in CELLS:
            for seed in SEEDS:
                for strategy in STRATEGIES:
                    rows = run_input_sensor_corruption_strategy(
                        seed, sigma_x, duration, strategy, tau
                    )
                    post200 = [r for r in rows if 401 <= r["t"] <= 600]
                    postall = [r for r in rows if r["t"] >= 401]
                    onset20 = [r for r in rows if 401 <= r["t"] <= 420]
                    adaptations = [r["t"] for r in postall if r["adapt"]]
                    final = rows[-1]
                    summaries.append({
                        "seed": seed,
                        "sigma_x": sigma_x,
                        "event_class": event_class,
                        "strategy": strategy,
                        "operational_loss_401_600": sum(r["sq_error"] for r in post200),
                        "operational_loss_401_1200": sum(r["sq_error"] for r in postall),
                        "latent_input_loss_401_600": sum(r["latent_input_sq_error"] for r in post200),
                        "latent_input_loss_401_1200": sum(r["latent_input_sq_error"] for r in postall),
                        "adapt_401_420": int(any(r["adapt"] for r in onset20)),
                        "first_post_event_adaptation": adaptations[0] if adaptations else "",
                        "adaptation_delay": adaptations[0] - EVENT_T if adaptations else "",
                        "adapt_count_401_600": sum(r["adapt"] for r in post200),
                        "adapt_count_401_1200": sum(r["adapt"] for r in postall),
                        "final_slope": final["slope_after"],
                        "final_intercept": final["intercept_after"],
                        "final_slope_error_abs": abs(final["slope_after"] - 1.5),
                    })
                    if seed in AUDIT:
                        for r in rows:
                            audit.append(dict(r, sigma_x=sigma_x, event_class=event_class))

    write_csv(RESULTS / "seed_summary.csv", summaries)
    write_csv(RESULTS / "audit_trace_seeds_7000_7004.csv", audit)

    cells = []
    for sigma_x in SIGMAS:
        for event_class, _duration in CELLS:
            c = [
                r for r in summaries
                if r["sigma_x"] == sigma_x and r["event_class"] == event_class
            ]
            operational_means = {
                s: sum(r["operational_loss_401_600"] for r in c if r["strategy"] == s) / len(SEEDS)
                for s in STRATEGIES
            }
            latent_means = {
                s: sum(r["latent_input_loss_401_600"] for r in c if r["strategy"] == s) / len(SEEDS)
                for s in STRATEGIES
            }
            adapt20_rates = {
                s: sum(r["adapt_401_420"] for r in c if r["strategy"] == s) / len(SEEDS)
                for s in STRATEGIES
            }
            burden_means = {
                s: sum(r["adapt_count_401_1200"] for r in c if r["strategy"] == s) / len(SEEDS)
                for s in STRATEGIES
            }
            slope_error_means = {
                s: sum(r["final_slope_error_abs"] for r in c if r["strategy"] == s) / len(SEEDS)
                for s in STRATEGIES
            }
            final_slope_means = {
                s: sum(r["final_slope"] for r in c if r["strategy"] == s) / len(SEEDS)
                for s in STRATEGIES
            }

            paired = {}
            for seed in SEEDS:
                p = next(r for r in c if r["seed"] == seed and r["strategy"] == "persistence")
                t = next(r for r in c if r["seed"] == seed and r["strategy"] == "threshold")
                paired[seed] = (p, t)

            cell_report = {
                "sigma_x": sigma_x,
                "event_class": event_class,
                "mean_operational_loss_401_600": operational_means,
                "mean_latent_input_loss_401_600": latent_means,
                "adapt_401_420_rate": adapt20_rates,
                "mean_adapt_count_401_1200": burden_means,
                "mean_final_slope": final_slope_means,
                "mean_final_slope_error_abs": slope_error_means,
            }
            base_seed = 2026081807 + int(sigma_x * 1000) + (
                0 if event_class == "transient" else 10000
            )
            if event_class == "transient":
                diffs = [
                    paired[s][0]["adapt_401_420"] - paired[s][1]["adapt_401_420"]
                    for s in SEEDS
                ]
                cell_report["primary_persistence_minus_threshold_adaptation_rate_difference"] = sum(diffs) / len(diffs)
                cell_report["primary_bootstrap_95_ci"] = ci(diffs, base_seed)
            else:
                operational_diffs = [
                    paired[s][0]["operational_loss_401_600"] - paired[s][1]["operational_loss_401_600"]
                    for s in SEEDS
                ]
                slope_error_diffs = [
                    paired[s][0]["final_slope_error_abs"] - paired[s][1]["final_slope_error_abs"]
                    for s in SEEDS
                ]
                burden_diffs = [
                    paired[s][0]["adapt_count_401_1200"] - paired[s][1]["adapt_count_401_1200"]
                    for s in SEEDS
                ]
                latent_diffs = [
                    paired[s][0]["latent_input_loss_401_600"] - paired[s][1]["latent_input_loss_401_600"]
                    for s in SEEDS
                ]
                cell_report["primary_persistence_minus_threshold_operational_loss_mean_difference"] = sum(operational_diffs) / len(operational_diffs)
                cell_report["primary_bootstrap_95_ci"] = ci(operational_diffs, base_seed)
                cell_report["persistence_minus_threshold_final_slope_error_mean_difference"] = sum(slope_error_diffs) / len(slope_error_diffs)
                cell_report["slope_error_bootstrap_95_ci"] = ci(slope_error_diffs, base_seed + 1)
                cell_report["persistence_minus_threshold_burden_mean_difference"] = sum(burden_diffs) / len(burden_diffs)
                cell_report["burden_bootstrap_95_ci"] = ci(burden_diffs, base_seed + 2)
                cell_report["persistence_minus_threshold_latent_input_loss_mean_difference"] = sum(latent_diffs) / len(latent_diffs)
                cell_report["latent_input_loss_bootstrap_95_ci"] = ci(latent_diffs, base_seed + 3)
            cells.append(cell_report)

    report = {
        "tau": tau,
        "evaluation_seeds": [7000, 7199],
        "n_seeds_per_cell": len(SEEDS),
        "sigma_x_values": SIGMAS,
        "event_classes": ["transient_20", "persistent"],
        "physical_response_law": "y = 1.5*x_true + epsilon; epsilon~N(0,0.5^2)",
        "observed_input_law": "x_obs = x_true + true_sigma_x*sensor_unit_noise",
        "cells": cells,
        "audit_seeds": sorted(AUDIT),
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
