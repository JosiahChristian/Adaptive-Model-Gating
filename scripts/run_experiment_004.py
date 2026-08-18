#!/usr/bin/env python3
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adaptive_model_gating import EVENT_T, calibrate_tau, paired_bootstrap_ci
from experiment_004 import run_structural_mismatch_strategy

RESULTS = ROOT / "results" / "experiment_004"
STRATEGIES = ["frozen", "continuous", "threshold", "persistence"]
GAMMAS = [0.25, 0.5, 1.0]
CELLS = [("transient", 20), ("persistent", None)]
SEEDS = list(range(4000, 4200))
AUDIT = set(range(4000, 4005))

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

    for gamma in GAMMAS:
        for event_class, duration in CELLS:
            for seed in SEEDS:
                for strategy in STRATEGIES:
                    rows = run_structural_mismatch_strategy(seed, gamma, duration, strategy, tau)
                    post200 = [r for r in rows if 401 <= r["t"] <= 600]
                    postall = [r for r in rows if r["t"] >= 401]
                    onset20 = [r for r in rows if 401 <= r["t"] <= 420]
                    adaptations = [r["t"] for r in postall if r["adapt"]]
                    summaries.append({
                        "seed": seed,
                        "gamma": gamma,
                        "event_class": event_class,
                        "strategy": strategy,
                        "loss_401_600": sum(r["sq_error"] for r in post200),
                        "loss_401_1200": sum(r["sq_error"] for r in postall),
                        "adapt_401_420": int(any(r["adapt"] for r in onset20)),
                        "first_post_event_adaptation": adaptations[0] if adaptations else "",
                        "adaptation_delay": adaptations[0] - EVENT_T if adaptations else "",
                        "adapt_count_401_600": sum(r["adapt"] for r in post200),
                        "adapt_count_401_1200": sum(r["adapt"] for r in postall),
                    })
                    if seed in AUDIT:
                        for r in rows:
                            audit.append(dict(r, gamma=gamma, event_class=event_class))

    write_csv(RESULTS / "seed_summary.csv", summaries)
    write_csv(RESULTS / "audit_trace_seeds_4000_4004.csv", audit)

    cells = []
    for gamma in GAMMAS:
        for event_class, _duration in CELLS:
            c = [r for r in summaries if r["gamma"] == gamma and r["event_class"] == event_class]
            means_loss_200 = {
                s: sum(r["loss_401_600"] for r in c if r["strategy"] == s) / len(SEEDS)
                for s in STRATEGIES
            }
            means_loss_full = {
                s: sum(r["loss_401_1200"] for r in c if r["strategy"] == s) / len(SEEDS)
                for s in STRATEGIES
            }
            adapt20_rates = {
                s: sum(r["adapt_401_420"] for r in c if r["strategy"] == s) / len(SEEDS)
                for s in STRATEGIES
            }
            churn_means = {
                s: sum(r["adapt_count_401_1200"] for r in c if r["strategy"] == s) / len(SEEDS)
                for s in STRATEGIES
            }

            paired = {}
            for seed in SEEDS:
                p = next(r for r in c if r["seed"] == seed and r["strategy"] == "persistence")
                t = next(r for r in c if r["seed"] == seed and r["strategy"] == "threshold")
                paired[seed] = (p, t)

            cell_report = {
                "gamma": gamma,
                "event_class": event_class,
                "mean_loss_401_600": means_loss_200,
                "mean_loss_401_1200": means_loss_full,
                "adapt_401_420_rate": adapt20_rates,
                "mean_adapt_count_401_1200": churn_means,
            }
            base_seed = 2026081804 + int(gamma * 1000) + (0 if event_class == "transient" else 10000)
            if event_class == "transient":
                diffs = [paired[s][0]["adapt_401_420"] - paired[s][1]["adapt_401_420"] for s in SEEDS]
                cell_report["primary_persistence_minus_threshold_adaptation_rate_difference"] = sum(diffs) / len(diffs)
                cell_report["primary_bootstrap_95_ci"] = ci(diffs, base_seed)
            else:
                loss_diffs = [paired[s][0]["loss_401_600"] - paired[s][1]["loss_401_600"] for s in SEEDS]
                churn_diffs = [paired[s][0]["adapt_count_401_1200"] - paired[s][1]["adapt_count_401_1200"] for s in SEEDS]
                cell_report["primary_persistence_minus_threshold_loss_mean_difference"] = sum(loss_diffs) / len(loss_diffs)
                cell_report["primary_bootstrap_95_ci"] = ci(loss_diffs, base_seed)
                cell_report["persistence_minus_threshold_churn_mean_difference"] = sum(churn_diffs) / len(churn_diffs)
                cell_report["churn_bootstrap_95_ci"] = ci(churn_diffs, base_seed + 1)
            cells.append(cell_report)

    report = {
        "tau": tau,
        "evaluation_seeds": [4000, 4199],
        "n_seeds_per_cell": len(SEEDS),
        "gamma_values": GAMMAS,
        "event_classes": ["transient_20", "persistent"],
        "cells": cells,
        "audit_seeds": sorted(AUDIT),
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
