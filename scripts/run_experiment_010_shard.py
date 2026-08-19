#!/usr/bin/env python3
"""Execution-only shard wrapper for the frozen Experiment 010 runner.

This does not alter Experiment 010's scientific design. It evaluates exactly one
of the nine frozen cells using the same strategy functions, seeds, summaries,
paired contrasts, bootstrap seeds, and calibration routines as
scripts/run_experiment_010.py, allowing GitHub Actions to parallelize the
otherwise monolithic evaluation.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import run_experiment_010 as base
from adaptive_model_gating import BASELINE_A, calibrate_tau
from experiment_008 import calibrate_kappa
from experiment_010 import calibrate_kappa3, run_experiment_010_strategy


def cell_report(summaries, family, magnitude):
    c = [r for r in summaries if r["family"] == family and r["magnitude"] == magnitude]
    p = base.paired(c)
    cell_index = base.FAMILIES.index(family) * len(base.MAGNITUDES) + base.MAGNITUDES.index(magnitude)
    base_seed = 2026081810 + cell_index * 1000
    report = {
        "family": family,
        "magnitude": magnitude,
        "mean_operational_loss_401_600": base.strategy_means(c, "operational_loss_401_600"),
        "mean_latent_input_loss_401_600": base.strategy_means(c, "latent_input_loss_401_600"),
        "adapt_401_420_rate": base.strategy_means(c, "adapt_401_420"),
        "mean_adapt_count_401_1200": base.strategy_means(c, "adapt_count_401_1200"),
        "mean_triad_veto_count_401_1200": base.strategy_means(c, "triad_veto_count_401_1200"),
        "mean_primary_bad_fraction_401_1200": base.strategy_means(c, "primary_bad_fraction_401_1200"),
        "mean_reference1_bad_fraction_401_1200": base.strategy_means(c, "reference1_bad_fraction_401_1200"),
        "mean_reference2_bad_fraction_401_1200": base.strategy_means(c, "reference2_bad_fraction_401_1200"),
        "primary_bad_401_420_rate": base.strategy_means(c, "primary_bad_401_420"),
        "reference1_bad_401_420_rate": base.strategy_means(c, "reference1_bad_401_420"),
        "mean_final_slope": base.strategy_means(c, "final_slope"),
        "mean_final_slope_error_abs": base.strategy_means(c, "final_slope_error_abs"),
    }

    if family == "primary_fault":
        slope = [p[s]["triad_persistence"]["final_slope_error_abs"] - p[s]["health_persistence"]["final_slope_error_abs"] for s in base.SEEDS]
        burden = [p[s]["triad_persistence"]["adapt_count_401_1200"] - p[s]["persistence"]["adapt_count_401_1200"] for s in base.SEEDS]
        op = [p[s]["triad_persistence"]["operational_loss_401_600"] - p[s]["persistence"]["operational_loss_401_600"] for s in base.SEEDS]
        latent = [p[s]["triad_persistence"]["latent_input_loss_401_600"] - p[s]["persistence"]["latent_input_loss_401_600"] for s in base.SEEDS]
        report["primary_triad_minus_health_final_slope_error_mean_difference"] = sum(slope) / len(slope)
        report["primary_bootstrap_95_ci"] = base.ci(slope, base_seed)
        report["triad_minus_persistence_burden_mean_difference"] = sum(burden) / len(burden)
        report["burden_bootstrap_95_ci"] = base.ci(burden, base_seed + 1)
        report["triad_minus_persistence_operational_loss_mean_difference"] = sum(op) / len(op)
        report["operational_loss_bootstrap_95_ci"] = base.ci(op, base_seed + 2)
        report["triad_minus_persistence_latent_input_loss_mean_difference"] = sum(latent) / len(latent)
        report["latent_input_loss_bootstrap_95_ci"] = base.ci(latent, base_seed + 3)
    elif family == "drift_reference_fault":
        loss = [p[s]["triad_persistence"]["operational_loss_401_600"] - p[s]["health_persistence"]["operational_loss_401_600"] for s in base.SEEDS]
        adapt = [p[s]["triad_persistence"]["adapt_401_420"] - p[s]["health_persistence"]["adapt_401_420"] for s in base.SEEDS]
        slope = [p[s]["triad_persistence"]["final_slope_error_abs"] - p[s]["health_persistence"]["final_slope_error_abs"] for s in base.SEEDS]
        delay = []
        for s in base.SEEDS:
            td = p[s]["triad_persistence"]["adaptation_delay"]
            pd = p[s]["persistence"]["adaptation_delay"]
            if td != "" and pd != "":
                delay.append(td - pd)
        report["primary_triad_minus_health_operational_loss_mean_difference"] = sum(loss) / len(loss)
        report["primary_bootstrap_95_ci"] = base.ci(loss, base_seed)
        report["triad_minus_health_adaptation_rate_difference_401_420"] = sum(adapt) / len(adapt)
        report["adaptation_rate_bootstrap_95_ci"] = base.ci(adapt, base_seed + 1)
        report["triad_minus_health_final_slope_error_mean_difference"] = sum(slope) / len(slope)
        report["slope_error_bootstrap_95_ci"] = base.ci(slope, base_seed + 2)
        if delay:
            report["triad_minus_persistence_delay_among_both_adapting"] = sum(delay) / len(delay)
            report["delay_bootstrap_95_ci"] = base.ci(delay, base_seed + 3)
            report["n_pairs_for_delay"] = len(delay)
    else:
        slope = [p[s]["triad_persistence"]["final_slope_error_abs"] - p[s]["persistence"]["final_slope_error_abs"] for s in base.SEEDS]
        op = [p[s]["triad_persistence"]["operational_loss_401_600"] - p[s]["persistence"]["operational_loss_401_600"] for s in base.SEEDS]
        report["primary_triad_minus_persistence_final_slope_error_mean_difference"] = sum(slope) / len(slope)
        report["primary_bootstrap_95_ci"] = base.ci(slope, base_seed)
        report["triad_minus_persistence_operational_loss_mean_difference"] = sum(op) / len(op)
        report["operational_loss_bootstrap_95_ci"] = base.ci(op, base_seed + 1)
    return report


def main():
    family = os.environ["EXPERIMENT_010_FAMILY"]
    magnitude = float(os.environ["EXPERIMENT_010_MAGNITUDE"])
    if family not in base.FAMILIES or magnitude not in base.MAGNITUDES:
        raise ValueError((family, magnitude))

    tau = calibrate_tau()
    kappa = calibrate_kappa()
    kappa3 = calibrate_kappa3()
    summaries = []
    audit = []
    for seed in base.SEEDS:
        for strategy in base.STRATEGIES:
            rows = run_experiment_010_strategy(seed, family, magnitude, strategy, tau, kappa, kappa3)
            summaries.append(base.summarize(rows, family, magnitude))
            if seed in base.AUDIT:
                audit.extend(dict(r, family=family, magnitude=magnitude) for r in rows)

    label = f"{family}_{magnitude:.2f}"
    out = ROOT / "results" / "experiment_010_shards" / label
    base.write_csv(out / "seed_summary.csv", summaries)
    base.write_csv(out / "audit_trace.csv", audit)
    report = {
        "tau": tau,
        "kappa": kappa,
        "kappa3": kappa3,
        "triad_calibration_seeds": [200, 399],
        "evaluation_seeds": [10000, 10199],
        "n_seeds_per_cell": len(base.SEEDS),
        "sigma_ref": 0.05,
        "family": family,
        "magnitude": magnitude,
        "strategies": base.STRATEGIES,
        "cell": cell_report(summaries, family, magnitude),
        "audit_seeds": sorted(base.AUDIT),
    }
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
