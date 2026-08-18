#!/usr/bin/env python3
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adaptive_model_gating import BASELINE_A, EVENT_T, calibrate_tau, paired_bootstrap_ci
from experiment_008 import calibrate_kappa
from experiment_009 import run_experiment_009_strategy

RESULTS = ROOT / "results" / "experiment_009"
STRATEGIES = ["frozen", "continuous", "threshold", "persistence", "health_persistence"]
MAGNITUDES = [0.25, 0.5, 1.0]
FAMILIES = ["common_mode", "drift_reference_fault"]
SEEDS = list(range(9000, 9200))
AUDIT = set(range(9000, 9005))


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)


def ci(values, seed):
    return list(paired_bootstrap_ci(values, seed=seed, reps=10000))


def summarize(rows, family, magnitude):
    post200 = [r for r in rows if 401 <= r["t"] <= 600]
    postall = [r for r in rows if r["t"] >= 401]
    onset20 = [r for r in rows if 401 <= r["t"] <= 420]
    adaptations = [r["t"] for r in postall if r["adapt"]]
    target_slope = BASELINE_A if family == "common_mode" else BASELINE_A + magnitude
    final_slope = rows[-1]["slope_after"]
    health_flags = [r["t"] for r in postall if r["sensor_unhealthy"]]
    return {
        "seed": rows[0]["seed"],
        "family": family,
        "magnitude": magnitude,
        "strategy": rows[0]["strategy"],
        "operational_loss_401_600": sum(r["sq_error"] for r in post200),
        "operational_loss_401_1200": sum(r["sq_error"] for r in postall),
        "latent_input_loss_401_600": sum(r["latent_input_sq_error"] for r in post200),
        "latent_input_loss_401_1200": sum(r["latent_input_sq_error"] for r in postall),
        "adapt_401_420": int(any(r["adapt"] for r in onset20)),
        "first_post_event_adaptation": adaptations[0] if adaptations else "",
        "adaptation_delay": adaptations[0] - EVENT_T if adaptations else "",
        "adapt_count_401_1200": sum(r["adapt"] for r in postall),
        "health_flag_401_420": int(any(r["sensor_unhealthy"] for r in onset20)),
        "health_flag_fraction_401_1200": sum(r["sensor_unhealthy"] for r in postall) / len(postall),
        "first_post_event_health_flag": health_flags[0] if health_flags else "",
        "health_flag_delay": health_flags[0] - EVENT_T if health_flags else "",
        "health_veto_count_401_1200": sum(r["health_veto"] for r in postall),
        "final_slope": final_slope,
        "final_slope_error_abs": abs(final_slope - target_slope),
        "target_slope": target_slope,
    }


def means(rows, field):
    return {
        s: sum(r[field] for r in rows if r["strategy"] == s) / len(SEEDS)
        for s in STRATEGIES
    }


def paired(rows):
    return {
        seed: {
            s: next(r for r in rows if r["seed"] == seed and r["strategy"] == s)
            for s in STRATEGIES
        }
        for seed in SEEDS
    }


def main():
    tau = calibrate_tau()
    kappa = calibrate_kappa()
    summaries = []
    audit = []

    for family in FAMILIES:
        for magnitude in MAGNITUDES:
            for seed in SEEDS:
                for strategy in STRATEGIES:
                    rows = run_experiment_009_strategy(seed, family, magnitude, strategy, tau, kappa)
                    summaries.append(summarize(rows, family, magnitude))
                    if seed in AUDIT:
                        for r in rows:
                            audit.append(dict(r, family=family, magnitude=magnitude))

    write_csv(RESULTS / "seed_summary.csv", summaries)
    write_csv(RESULTS / "audit_trace_seeds_9000_9004.csv", audit)

    cells = []
    cell_index = 0
    for family in FAMILIES:
        for magnitude in MAGNITUDES:
            c = [r for r in summaries if r["family"] == family and r["magnitude"] == magnitude]
            p = paired(c)
            base_seed = 2026081809 + cell_index * 1000
            cell_index += 1
            report = {
                "family": family,
                "magnitude": magnitude,
                "mean_operational_loss_401_600": means(c, "operational_loss_401_600"),
                "mean_latent_input_loss_401_600": means(c, "latent_input_loss_401_600"),
                "adapt_401_420_rate": means(c, "adapt_401_420"),
                "mean_adapt_count_401_1200": means(c, "adapt_count_401_1200"),
                "mean_health_flag_fraction_401_1200": means(c, "health_flag_fraction_401_1200"),
                "health_flag_401_420_rate": means(c, "health_flag_401_420"),
                "mean_health_veto_count_401_1200": means(c, "health_veto_count_401_1200"),
                "mean_final_slope": means(c, "final_slope"),
                "mean_final_slope_error_abs": means(c, "final_slope_error_abs"),
            }

            if family == "common_mode":
                slope_diffs = [
                    p[s]["health_persistence"]["final_slope_error_abs"]
                    - p[s]["persistence"]["final_slope_error_abs"]
                    for s in SEEDS
                ]
                health_flag_diffs = [
                    p[s]["health_persistence"]["health_flag_fraction_401_1200"]
                    - p[s]["persistence"]["health_flag_fraction_401_1200"]
                    for s in SEEDS
                ]
                burden_diffs = [
                    p[s]["health_persistence"]["adapt_count_401_1200"]
                    - p[s]["persistence"]["adapt_count_401_1200"]
                    for s in SEEDS
                ]
                op_diffs = [
                    p[s]["health_persistence"]["operational_loss_401_600"]
                    - p[s]["persistence"]["operational_loss_401_600"]
                    for s in SEEDS
                ]
                latent_diffs = [
                    p[s]["health_persistence"]["latent_input_loss_401_600"]
                    - p[s]["persistence"]["latent_input_loss_401_600"]
                    for s in SEEDS
                ]
                report["primary_health_minus_persistence_final_slope_error_mean_difference"] = sum(slope_diffs) / len(slope_diffs)
                report["primary_bootstrap_95_ci"] = ci(slope_diffs, base_seed)
                report["health_minus_persistence_health_flag_fraction_difference"] = sum(health_flag_diffs) / len(health_flag_diffs)
                report["health_flag_fraction_bootstrap_95_ci"] = ci(health_flag_diffs, base_seed + 1)
                report["health_minus_persistence_burden_mean_difference"] = sum(burden_diffs) / len(burden_diffs)
                report["burden_bootstrap_95_ci"] = ci(burden_diffs, base_seed + 2)
                report["health_minus_persistence_operational_loss_mean_difference"] = sum(op_diffs) / len(op_diffs)
                report["operational_loss_bootstrap_95_ci"] = ci(op_diffs, base_seed + 3)
                report["health_minus_persistence_latent_input_loss_mean_difference"] = sum(latent_diffs) / len(latent_diffs)
                report["latent_input_loss_bootstrap_95_ci"] = ci(latent_diffs, base_seed + 4)
            else:
                loss_diffs = [
                    p[s]["health_persistence"]["operational_loss_401_600"]
                    - p[s]["persistence"]["operational_loss_401_600"]
                    for s in SEEDS
                ]
                adapt_diffs = [
                    p[s]["health_persistence"]["adapt_401_420"]
                    - p[s]["persistence"]["adapt_401_420"]
                    for s in SEEDS
                ]
                burden_diffs = [
                    p[s]["health_persistence"]["adapt_count_401_1200"]
                    - p[s]["persistence"]["adapt_count_401_1200"]
                    for s in SEEDS
                ]
                slope_diffs = [
                    p[s]["health_persistence"]["final_slope_error_abs"]
                    - p[s]["persistence"]["final_slope_error_abs"]
                    for s in SEEDS
                ]
                delay_diffs = []
                for s in SEEDS:
                    hp = p[s]["health_persistence"]["adaptation_delay"]
                    pp = p[s]["persistence"]["adaptation_delay"]
                    if hp != "" and pp != "":
                        delay_diffs.append(hp - pp)
                report["primary_health_minus_persistence_operational_loss_mean_difference"] = sum(loss_diffs) / len(loss_diffs)
                report["primary_bootstrap_95_ci"] = ci(loss_diffs, base_seed)
                report["health_minus_persistence_adaptation_rate_difference_401_420"] = sum(adapt_diffs) / len(adapt_diffs)
                report["adaptation_rate_bootstrap_95_ci"] = ci(adapt_diffs, base_seed + 1)
                report["health_minus_persistence_burden_mean_difference"] = sum(burden_diffs) / len(burden_diffs)
                report["burden_bootstrap_95_ci"] = ci(burden_diffs, base_seed + 2)
                report["health_minus_persistence_final_slope_error_mean_difference"] = sum(slope_diffs) / len(slope_diffs)
                report["slope_error_bootstrap_95_ci"] = ci(slope_diffs, base_seed + 3)
                if delay_diffs:
                    report["paired_adaptation_delay_difference_among_both_adapting"] = sum(delay_diffs) / len(delay_diffs)
                    report["paired_adaptation_delay_bootstrap_95_ci"] = ci(delay_diffs, base_seed + 4)
                    report["n_pairs_for_delay"] = len(delay_diffs)

            cells.append(report)

    final_report = {
        "tau": tau,
        "kappa": kappa,
        "health_calibration_seeds": [200, 399],
        "evaluation_seeds": [9000, 9199],
        "n_seeds_per_cell": len(SEEDS),
        "sigma_ref": 0.05,
        "families": FAMILIES,
        "magnitudes": MAGNITUDES,
        "strategies": STRATEGIES,
        "cells": cells,
        "audit_seeds": sorted(AUDIT),
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "report.json").write_text(json.dumps(final_report, indent=2) + "\n")
    print(json.dumps(final_report, indent=2))


if __name__ == "__main__":
    main()
