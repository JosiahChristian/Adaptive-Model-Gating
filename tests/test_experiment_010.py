import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adaptive_model_gating import BASELINE_A, EVENT_T
from experiment_010 import (
    SIGMA_REF,
    calibrate_kappa3,
    classify_triad,
    generate_triad_stream,
    run_experiment_010_strategy,
)
from experiment_008 import calibrate_kappa
from adaptive_model_gating import calibrate_tau


class Experiment010Tests(unittest.TestCase):
    def test_primary_fault_equations(self):
        s = generate_triad_stream(10001, "primary_fault", 0.5)
        for t in range(1, len(s["x_true"])):
            self.assertAlmostEqual(s["y"][t], s["a"][t] * s["x_true"][t] + s["physical_epsilon"][t])
            self.assertEqual(s["a"][t], BASELINE_A)
            expected_p = s["x_true"][t]
            if t >= EVENT_T:
                expected_p += 0.5 * s["primary_unit_noise"][t]
            self.assertAlmostEqual(s["x_primary"][t], expected_p)
            self.assertAlmostEqual(s["x_r1"][t], s["x_true"][t] + SIGMA_REF * s["r1_unit_noise"][t])
            self.assertAlmostEqual(s["x_r2"][t], s["x_true"][t] + SIGMA_REF * s["r2_unit_noise"][t])

    def test_drift_reference_fault_equations(self):
        s = generate_triad_stream(10002, "drift_reference_fault", 1.0)
        self.assertEqual(s["a"][EVENT_T - 1], BASELINE_A)
        self.assertEqual(s["a"][EVENT_T], BASELINE_A + 1.0)
        for t in range(EVENT_T, len(s["x_true"])):
            self.assertEqual(s["x_primary"][t], s["x_true"][t])
            self.assertAlmostEqual(
                s["x_r1"][t],
                s["x_true"][t] + SIGMA_REF * s["r1_unit_noise"][t] + 1.0 * s["ref_fault_unit_noise"][t],
            )
            self.assertAlmostEqual(s["x_r2"][t], s["x_true"][t] + SIGMA_REF * s["r2_unit_noise"][t])

    def test_common_mode_reuses_same_corruption(self):
        s = generate_triad_stream(10003, "common_mode", 0.5)
        for t in range(EVENT_T, len(s["x_true"])):
            shared = 0.5 * s["common_unit_noise"][t]
            self.assertAlmostEqual(s["x_primary"][t] - s["x_true"][t], shared)
            self.assertAlmostEqual(s["x_r1"][t] - s["x_true"][t] - SIGMA_REF * s["r1_unit_noise"][t], shared)
            self.assertAlmostEqual(s["x_r2"][t] - s["x_true"][t] - SIGMA_REF * s["r2_unit_noise"][t], shared)

    def test_classifier_single_channel_logic(self):
        k = 1.0
        self.assertEqual(classify_triad(2.0, 2.0, 0.5, k)[:3], (1, 0, 0))
        self.assertEqual(classify_triad(2.0, 0.5, 2.0, k)[:3], (0, 1, 0))
        self.assertEqual(classify_triad(0.5, 2.0, 2.0, k)[:3], (0, 0, 1))
        self.assertEqual(classify_triad(2.0, 2.0, 2.0, k)[:3], (0, 0, 0))

    def test_learner_uses_primary_only(self):
        tau = calibrate_tau()
        kappa = calibrate_kappa()
        kappa3 = calibrate_kappa3()
        rows = run_experiment_010_strategy(10004, "primary_fault", 0.5, "triad_persistence", tau, kappa, kappa3)
        for r in rows:
            self.assertEqual(r["x"], r["x_primary"])

    def test_invalid_family_rejected(self):
        with self.assertRaises(ValueError):
            generate_triad_stream(1, "bad", 0.5)


if __name__ == "__main__":
    unittest.main()
