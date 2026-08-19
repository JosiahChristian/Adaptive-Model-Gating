#!/usr/bin/env python3
"""Merge the nine execution shards of frozen Experiment 010 evidence."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHARDS = ROOT / "results" / "experiment_010_shards"
OUT = ROOT / "results" / "experiment_010"
FAMILIES = ["primary_fault", "drift_reference_fault", "common_mode"]
MAGNITUDES = [0.25, 0.5, 1.0]
STRATEGIES = ["frozen", "continuous", "threshold", "persistence", "health_persistence", "triad_persistence"]


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)


def main():
    reports = []
    summaries = []
    audit = []
    for family in FAMILIES:
        for magnitude in MAGNITUDES:
            label = f"{family}_{magnitude:.2f}"
            d = SHARDS / label
            report_path = d / "report.json"
            if not report_path.exists():
                raise FileNotFoundError(report_path)
            reports.append(json.loads(report_path.read_text()))
            summaries.extend(read_csv(d / "seed_summary.csv"))
            audit.extend(read_csv(d / "audit_trace.csv"))

    tau = reports[0]["tau"]
    kappa = reports[0]["kappa"]
    kappa3 = reports[0]["kappa3"]
    for r in reports[1:]:
        if r["tau"] != tau or r["kappa"] != kappa or r["kappa3"] != kappa3:
            raise ValueError("Calibration mismatch across Experiment 010 shards")

    expected_summary_rows = len(FAMILIES) * len(MAGNITUDES) * len(STRATEGIES) * 200
    if len(summaries) != expected_summary_rows:
        raise ValueError(f"Expected {expected_summary_rows} summary rows, got {len(summaries)}")

    # Preserve deterministic family/magnitude ordering from the original runner.
    cells = []
    for family in FAMILIES:
        for magnitude in MAGNITUDES:
            cells.append(next(r["cell"] for r in reports if r["family"] == family and r["magnitude"] == magnitude))

    OUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUT / "seed_summary.csv", summaries)
    write_csv(OUT / "audit_trace_seeds_10000_10004.csv", audit)
    final = {
        "tau": tau,
        "kappa": kappa,
        "kappa3": kappa3,
        "triad_calibration_seeds": [200, 399],
        "evaluation_seeds": [10000, 10199],
        "n_seeds_per_cell": 200,
        "sigma_ref": 0.05,
        "families": FAMILIES,
        "magnitudes": MAGNITUDES,
        "strategies": STRATEGIES,
        "cells": cells,
        "audit_seeds": [10000, 10001, 10002, 10003, 10004],
        "execution": "nine-cell sharded execution; scientific rules unchanged from frozen Experiment 010 specification",
    }
    (OUT / "report.json").write_text(json.dumps(final, indent=2) + "\n")
    print(json.dumps(final, indent=2))


if __name__ == "__main__":
    main()
