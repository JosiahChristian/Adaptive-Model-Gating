#!/usr/bin/env python3
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adaptive_model_gating import (
    calibrate_tau,
    paired_bootstrap_ci,
    run_parameter_change_strategy,
    summarize_parameter_change,
)

RESULTS = ROOT / "results" / "experiment_002"
STRATEGIES = ["frozen", "continuous", "threshold", "persistence"]
MAGNITUDES = [0.10, 0.25, 0.50, 1.00]
DURATIONS = [5, 20, 50]
SEEDS = list(range(2000, 2200))
AUDIT_SEEDS = set(range(2000, 2005))


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def main():
    tau = calibrate_tau()
    summaries = []
    audit_rows = []

    cells = [(0.0, None)]
    cells += [(m, d) for m in MAGNITUDES for d in DURATIONS]
    cells += [(m, None) for m in MAGNITUDES]

    for delta_a, duration in cells:
        for seed in SEEDS:
            for strategy in STRATEGIES:
                rows = run_parameter_change_strategy(seed, delta_a, duration, strategy, tau)
                summary = summarize_parameter_change(rows, duration)
                summary["delta_a"] = delta_a
                summary["transient_duration"] = "" if duration is None else duration
                summaries.append(summary)
                if seed in AUDIT_SEEDS:
                    for row in rows:
                        row = dict(row)
                        row["delta_a"] = delta_a
                        row["transient_duration"] = "" if duration is None else duration
                        audit_rows.append(row)

    write_csv(RESULTS / "seed_summary.csv", summaries)
    write_csv(RESULTS / "audit_trace_seeds_2000_2004.csv", audit_rows)

    # Stable long-horizon false alarm summaries.
    stable = [r for r in summaries if float(r["delta_a"]) == 0.0]
    stable_summary = {}
    for strategy in STRATEGIES:
        rs = [r for r in stable if r["strategy"] == strategy]
        stable_summary[strategy] = {
            "adapt_rate_401_600": sum(int(r["adapt_401_600"]) for r in rs) / len(rs),
            "adapt_rate_401_1200": sum(int(r["adapt_401_1200"]) for r in rs) / len(rs),
            "mean_adapt_count_401_600": sum(int(r["adapt_count_401_600"]) for r in rs) / len(rs),
            "mean_adapt_count_401_1200": sum(int(r["adapt_count_401_1200"]) for r in rs) / len(rs),
        }

    # Full transient cell surface plus overall seed-level 12-cell G-B2 contrast.
    transient_cells = []
    seed_avg_diff = []
    for m in MAGNITUDES:
        for d in DURATIONS:
            cell = [r for r in summaries if float(r["delta_a"]) == m and str(r["transient_duration"]) == str(d)]
            rates = {}
            for strategy in STRATEGIES:
                rs = [r for r in cell if r["strategy"] == strategy]
                rates[strategy] = sum(int(r["adapt_during_true_event"]) for r in rs) / len(rs)
            transient_cells.append({"delta_a": m, "duration": d, "adaptation_rate": rates})

    for seed in SEEDS:
        diffs = []
        for m in MAGNITUDES:
            for d in DURATIONS:
                g = next(r for r in summaries if r["seed"] == seed and r["strategy"] == "persistence" and float(r["delta_a"]) == m and str(r["transient_duration"]) == str(d))
                b = next(r for r in summaries if r["seed"] == seed and r["strategy"] == "threshold" and float(r["delta_a"]) == m and str(r["transient_duration"]) == str(d))
                diffs.append(int(g["adapt_during_true_event"]) - int(b["adapt_during_true_event"]))
        seed_avg_diff.append(sum(diffs) / len(diffs))
    transient_ci = paired_bootstrap_ci(seed_avg_diff, seed=2026081802)

    # Persistent cell-specific loss surface.
    persistent_cells = []
    for m in MAGNITUDES:
        cell = [r for r in summaries if float(r["delta_a"]) == m and r["transient_duration"] == ""]
        means = {}
        for strategy in STRATEGIES:
            rs = [r for r in cell if r["strategy"] == strategy]
            means[strategy] = sum(float(r["loss_401_600"]) for r in rs) / len(rs)
        diffs = []
        for seed in SEEDS:
            g = next(r for r in cell if r["seed"] == seed and r["strategy"] == "persistence")
            b = next(r for r in cell if r["seed"] == seed and r["strategy"] == "threshold")
            diffs.append(float(g["loss_401_600"]) - float(b["loss_401_600"]))
        persistent_cells.append({
            "delta_a": m,
            "mean_loss": means,
            "persistence_minus_threshold_mean_difference": sum(diffs) / len(diffs),
            "persistence_minus_threshold_bootstrap_95_ci": list(paired_bootstrap_ci(diffs, seed=2026081803 + int(m * 100))),
        })

    report = {
        "tau": tau,
        "evaluation_seeds": [SEEDS[0], SEEDS[-1]],
        "n_seeds_per_cell": len(SEEDS),
        "stable": stable_summary,
        "transient_surface": transient_cells,
        "overall_transient_persistence_minus_threshold_mean_difference": sum(seed_avg_diff) / len(seed_avg_diff),
        "overall_transient_persistence_minus_threshold_bootstrap_95_ci": list(transient_ci),
        "persistent_surface": persistent_cells,
        "audit_seeds": sorted(AUDIT_SEEDS),
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
