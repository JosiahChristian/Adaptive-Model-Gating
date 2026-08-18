#!/usr/bin/env python3
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adaptive_model_gating import BASELINE_A, EVENT_T, calibrate_tau, paired_bootstrap_ci
from experiment_008 import calibrate_kappa
from experiment_010 import calibrate_kappa3, run_experiment_010_strategy

RESULTS = ROOT / "results" / "experiment_010"
STRATEGIES = ["frozen", "continuous", "threshold", "persistence", "health_persistence", "triad_persistence"]
FAMILIES = ["primary_fault", "drift_reference_fault", "common_mode"]
MAGNITUDES = [0.25, 0.5, 1.0]
SEEDS = list(range(10000, 10200))
AUDIT = set(range(10000, 10005))


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
    target = BASELINE_A + magnitude if family == "drift_reference_fault" else BASELINE_A
    final_slope = rows[-1]["slope_after"]
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
        "adapt_count_401_600": sum(r["adapt"] for r in post200),
        "adapt_count_401_1200": sum(r["adapt"] for r in postall),
        "triad_veto_count_401_1200": sum(r.get("triad_veto", 0) for r in postall),
        "primary_bad_fraction_401_1200": sum(r["primary_bad"] for r in postall) / len(postall),
        "reference1_bad_fraction_401_1200": sum(r["reference1_bad"] for r in postall) / len(postall),
        "reference2_bad_fraction_401_1200": sum(r["reference2_bad"] for r in postall) / len(postall),
        "primary_bad_401_420": int(any(r["primary_bad"] for r in onset20)),
        "reference1_bad_401_420": int(any(r["reference1_bad"] for r in onset20)),
        "reference2_bad_401_420": int(any(r["reference2_bad"] for r in onset20)),
        "final_slope": final_slope,
        "target_slope": target,
        "final_slope_error_abs": abs(final_slope - target),
    }


def strategy_means(rows, field):
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
    kappa3 = calibrate_kappa3()
    summaries = []
    audit = []

    for family in FAMILIES:
        for magnitude in MAGNITUDES:
            for seed in SEEDS:
                for strategy in STRATEGIES:
                    rows = run_experiment_010_strategy(seed, family, magnitude, strategy, tau, kappa, kappa3)
                    summaries.append(summarize(rows, family, magnitude))
                    if seed in AUDIT:
                        for r in rows:
                            audit.append(dict(r, family=family, magnitude=magnitude))

    write_csv(RESULTS / "seed_summary.csv", summaries)
    write_csv(RESULTS / "audit_trace_seeds_10000_10004.csv", audit)

    cells = []
    cell_index = 0
    for family in FAMILIES:
        for magnitude in MAGNITUDES:
            c = [r for r in summaries if r["family"] == family and r["magnitude"] == magnitude]
            p = paired(c)
            base_seed = 2026081810 + cell_index * 1000
            cell_index += 1
            report = {
                "family": family,
                "magnitude": magnitude,
                "mean_operational_loss_401_600": strategy_means(c, "operational_loss_401_600"),
                "mean_latent_input_loss_401_600": strategy_means(c, "latent_input_loss_401_600"),
                "adapt_401_420_rate": strategy_means(c, "adapt_401_420"),
                "mean_adapt_count_401_1200": strategy_means(c, "adapt_count_401_1200"),
                "mean_triad_veto_count_401_1200": strategy_means(c, "triad_veto_count_401_1200"),
                "mean_primary_bad_fraction_401_1200": strategy_means(c, "primary_bad_fraction_401_1200"),
                "mean_reference1_bad_fraction_401_1200": strategy_means(c, "reference1_bad_fraction_401_1200"),
                "mean_reference2_bad_fraction_401_1200": strategy_means(c, "reference2_bad_fraction_401_1200"),
                "primary_bad_401_420_rate": strategy_means(c, "primary_bad_401_420"),
                "reference1_bad_401_420_rate": strategy_means(c, "reference1_bad_401_420"),
                "mean_final_slope": strategy_means(c, "final_slope"),
                "mean_final_slope_error_abs": strategy_means(c, "final_slope_error_abs"),
            }

            if family == "primary_fault":
                slope = [p[s]["triad_persistence"]["final_slope_error_abs"] - p[s]["health_persistence"]["final_slope_error_abs"] for s in SEEDS]
                burden = [p[s]["triad_persistence"]["adapt_count_401_1200"] - p[s]["persistence"]["adapt_count_401_1200"] for s in SEEDS]
                op = [p[s]["triad_persistence"]["operational_loss_401_600"] - p[s]["persistence"]["operational_loss_401_600"] for s in SEEDS]
                latent = [p[s]["triad_persistence"]["latent_input_loss_401_600"] - p[s]["persistence"]["latent_input_loss_401_600"] for s in SEEDS]
                report["primary_triad_minus_health_final_slope_error_mean_difference"] = sum(slope)/len(slope)
                report["primary_bootstrap_95_ci"] = ci(slope, base_seed)
                report["triad_minus_persistence_burden_mean_difference"] = sum(burden)/len(burden)
                report["burden_bootstrap_95_ci"] = ci(burden, base_seed+1)
                report["triad_minus_persistence_operational_loss_mean_difference"] = sum(op)/len(op)
                report["operational_loss_bootstrap_95_ci"] = ci(op, base_seed+2)
                report["triad_minus_persistence_latent_input_loss_mean_difference"] = sum(latent)/len(latent)
                report["latent_input_loss_bootstrap_95_ci"] = ci(latent, base_seed+3)

            elif family == "drift_reference_fault":
                loss = [p[s]["triad_persistence"]["operational_loss_401_600"] - p[s]["health_persistence"]["operational_loss_401_600"] for s in SEEDS]
                adapt = [p[s]["triad_persistence"]["adapt_401_420"] - p[s]["health_persistence"]["adapt_401_420"] for s in SEEDS]
                slope = [p[s]["triad_persistence"]["final_slope_error_abs"] - p[s]["health_persistence"]["final_slope_error_abs"] for s in SEEDS]
                delay = []
                for s in SEEDS:
                    td = p[s]["triad_persistence"]["adaptation_delay"]
                    pd = p[s]["persistence"]["adaptation_delay"]
                    if td != "" and pd != "":
                        delay.append(td-pd)
                report["primary_triad_minus_health_operational_loss_mean_difference"] = sum(loss)/len(loss)
                report["primary_bootstrap_95_ci"] = ci(loss, base_seed)
                report["triad_minus_health_adaptation_rate_difference_401_420"] = sum(adapt)/len(adapt)
                report["adaptation_rate_bootstrap_95_ci"] = ci(adapt, base_seed+1)
                report["triad_minus_health_final_slope_error_mean_difference"] = sum(slope)/len(slope)
                report["slope_error_bootstrap_95_ci"] = ci(slope, base_seed+2)
                if delay:
                    report["triad_minus_persistence_delay_among_both_adapting"] = sum(delay)/len(delay)
                    report["delay_bootstrap_95_ci"] = ci(delay, base_seed+3)
                    report["n_pairs_for_delay"] = len(delay)

            else:
                slope = [p[s]["triad_persistence"]["final_slope_error_abs"] - p[s]["persistence"]["final_slope_error_abs"] for s in SEEDS]
                op = [p[s]["triad_persistence"]["operational_loss_401_600"] - p[s]["persistence"]["operational_loss_401_600"] for s in SEEDS]
                report["primary_triad_minus_persistence_final_slope_error_mean_difference"] = sum(slope)/len(slope)
                report["primary_bootstrap_95_ci"] = ci(slope, base_seed)
                report["triad_minus_persistence_operational_loss_mean_difference"] = sum(op)/len(op)
                report["operational_loss_bootstrap_95_ci"] = ci(op, base_seed+1)
            cells.append(report)

    final = {
        "tau": tau,
        "kappa": kappa,
        "kappa3": kappa3,
        "triad_calibration_seeds": [200, 399],
        "evaluation_seeds": [10000, 10199],
        "n_seeds_per_cell": len(SEEDS),
        "sigma_ref": 0.05,
        "families": FAMILIES,
        "magnitudes": MAGNITUDES,
        "strategies": STRATEGIES,
        "cells": cells,
        "audit_seeds": sorted(AUDIT),
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "report.json").write_text(json.dumps(final, indent=2) + "\n")
    print(json.dumps(final, indent=2))


if __name__ == "__main__":
    main()
