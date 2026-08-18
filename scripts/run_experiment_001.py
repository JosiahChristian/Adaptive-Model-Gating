#!/usr/bin/env python3
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adaptive_model_gating import calibrate_tau, run_strategy, summarize, paired_bootstrap_ci

RESULTS = ROOT / "results" / "experiment_001"
STRATEGIES = ["frozen", "continuous", "threshold", "persistence"]
CONDITIONS = ["stable", "transient", "persistent"]
SEEDS = range(1000, 1200)


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def main():
    tau = calibrate_tau()
    summaries = []
    trace_path = RESULTS / "trace.csv"
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    trace_file = trace_path.open("w", newline="", encoding="utf-8")
    trace_writer = None
    try:
        for condition in CONDITIONS:
            for seed in SEEDS:
                for strategy in STRATEGIES:
                    rows = run_strategy(seed, condition, strategy, tau)
                    if trace_writer is None:
                        trace_writer = csv.DictWriter(trace_file, fieldnames=rows[0].keys())
                        trace_writer.writeheader()
                    trace_writer.writerows(rows)
                    summaries.append(summarize(rows))
    finally:
        trace_file.close()

    write_csv(RESULTS / "seed_summary.csv", summaries)

    persistent = [r for r in summaries if r["condition"] == "persistent"]
    transient = [r for r in summaries if r["condition"] == "transient"]
    by_key = {(r["seed"], r["strategy"]): r for r in persistent}
    diff_g_b2 = [
        by_key[(seed, "persistence")]["persistent_horizon_loss"]
        - by_key[(seed, "threshold")]["persistent_horizon_loss"]
        for seed in SEEDS
    ]
    ci = paired_bootstrap_ci(diff_g_b2)

    report = {
        "tau": tau,
        "evaluation_seeds": [1000, 1199],
        "n_seeds_per_condition": 200,
        "persistent_mean_loss": {
            s: sum(r["persistent_horizon_loss"] for r in persistent if r["strategy"] == s) / 200
            for s in STRATEGIES
        },
        "transient_adaptation_rate": {
            s: sum(r["transient_adaptation"] for r in transient if r["strategy"] == s) / 200
            for s in STRATEGIES
        },
        "persistence_minus_threshold_persistent_loss_mean_difference": sum(diff_g_b2) / len(diff_g_b2),
        "persistence_minus_threshold_persistent_loss_bootstrap_95_ci": list(ci),
    }
    (RESULTS / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
