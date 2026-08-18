#!/usr/bin/env python3
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adaptive_model_gating import EVENT_T, calibrate_tau, paired_bootstrap_ci
from experiment_006 import run_measurement_corruption_strategy

RESULTS = ROOT / "results" / "experiment_006"
STRATEGIES = ["frozen", "continuous", "threshold", "persistence"]
SIGMAS = [0.5, 1.0, 2.0]
CELLS = [("transient", 20), ("persistent", None)]
SEEDS = list(range(6000, 6200))
AUDIT = set(range(6000, 6005))


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

    for sigma_c in SIGMAS:
        for event_class, duration in CELLS:
            for seed in SEEDS:
                for strategy in STRATEGIES:
                    rows = run_measurement_corruption_strategy(
                        seed, sigma_c, duration, strategy, tau
                    )
                    post200 = [r for r in rows if 401 <= r["t"] <= 600]
                    postall = [r for r in rows if r["t"] >= 401]
                    onset20 = [r for r in rows if 401 <= r["t"] <= 420]
                    adaptations = [r["t"] for r in postall if r["adapt"]]
                    summaries.append({
                        "seed": seed,
                        "sigma_c": sigma_c,
                        "event_class": event_class,
                        "strategy": strategy,
                        "observed_loss_401_600": sum(r["sq_error"] for r in post200),
                        "observed_loss_401_1200": sum(r["sq_error"] for r in postall),
                        "clean_loss_401_600": sum(r["clean_target_sq_error"] for r in post200),
                        "clean_loss_401_1200": sum(r["clean_target_sq_error"] for r in postall),
                        "adapt_401_420": int(any(r["adapt"] for r in onset20)),
                        "first_post_event_adaptation": adaptations[0] if adaptations else "",
                        "adaptation_delay": adaptations[0] - EVENT_T if adaptations else "",
                        "adapt_count_401_600": sum(r["adapt"] for r in post200),
                        "adapt_count_401_1200": sum(r["adapt"] for r in postall),
                    })
                    if seed in AUDIT:
                        for r in rows:
                            audit.append(dict(r, sigma_c=sigma_c, event_class=event_class))

    write_csv(RESULTS / "seed_summary.csv", summaries)
    write_csv(RESULTS / "audit_trace_seeds_6000_6004.csv", audit)

    cells = []
    for sigma_c in SIGMAS:
        for event_class, _duration in CELLS:
            c = [
                r for r in summaries
                if r["sigma_c"] == sigma_c and r["event_class"] == event_class
            ]
            observed_means = {
                s: sum(r["observed_loss_401_600"] for r in c if r["strategy"] == s) / len(SEEDS)
                for s in STRATEGIES
            }
            clean_means = {
                s: sum(r["clean_loss_401_600"] for r in c if r["strategy"] == s) / len(SEEDS)
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

            paired = {}
            for seed in SEEDS:
                p = next(r for r in c if r["seed"] == seed and r["strategy"] == "persistence")
                t = next(r for r in c if r["seed"] == seed and r["strategy"] == "threshold")
                paired[seed] = (p, t)

            cell_report = {
                "sigma_c": sigma_c,
                "event_class": event_class,
                "mean_observed_loss_401_600": observed_means,
                "mean_clean_loss_401_600": clean_means,
                "adapt_401_420_rate": adapt20_rates,
                "mean_adapt_count_401_1200": burden_means,
            }
            base_seed = 2026081806 + int(sigma_c * 1000) + (
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
                observed_diffs = [
                    paired[s][0]["observed_loss_401_600"] - paired[s][1]["observed_loss_401_600"]
                    for s in SEEDS
                ]
                clean_diffs = [
                    paired[s][0]["clean_loss_401_600"] - paired[s][1]["clean_loss_401_600"]
                    for s in SEEDS
                ]
                burden_diffs = [
                    paired[s][0]["adapt_count_401_1200"] - paired[s][1]["adapt_count_401_1200"]
                    for s in SEEDS
                ]
                cell_report["primary_persistence_minus_threshold_observed_loss_mean_difference"] = sum(observed_diffs) / len(observed_diffs)
                cell_report["primary_bootstrap_95_ci"] = ci(observed_diffs, base_seed)
                cell_report["persistence_minus_threshold_clean_loss_mean_difference"] = sum(clean_diffs) / len(clean_diffs)
                cell_report["clean_loss_bootstrap_95_ci"] = ci(clean_diffs, base_seed + 1)
                cell_report["persistence_minus_threshold_burden_mean_difference"] = sum(burden_diffs) / len(burden_diffs)
                cell_report["burden_bootstrap_95_ci"] = ci(burden_diffs, base_seed + 2)
            cells.append(cell_report)

    report = {
        "tau": tau,
        "evaluation_seeds": [6000, 6199],
        "n_seeds_per_cell": len(SEEDS),
        "sigma_c_values": SIGMAS,
        "event_classes": ["transient_20", "persistent"],
        "clean_response_law": "clean_y = 1.5*x + epsilon; epsilon~N(0,0.5^2)",
        "observed_response_law": "y = clean_y + true_sigma_c*sensor_unit_noise",
        "cells": cells,
        "audit_seeds": sorted(AUDIT),
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
