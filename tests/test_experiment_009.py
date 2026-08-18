import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adaptive_model_gating import BASELINE_A, EVENT_T
from experiment_008 import SIGMA_REF, calibrate_kappa
from experiment_009 import generate_experiment_009_stream


class Experiment009Tests(unittest.TestCase):
    def test_common_mode_corruption_cancels_from_disagreement(self):
        stream = generate_experiment_009_stream(91, "common_mode", 1.0)
        for t in range(EVENT_T, len(stream["x_true"])):
            expected = -SIGMA_REF * stream["reference_unit_noise"][t]
            actual = stream["x_primary"][t] - stream["x_ref"][t]
            self.assertAlmostEqual(actual, expected)
            self.assertAlmostEqual(stream["a"][t], BASELINE_A)

    def test_reference_fault_keeps_primary_sensor_exact(self):
        stream = generate_experiment_009_stream(92, "drift_reference_fault", 0.5)
        for t in range(1, len(stream["x_true"])):
            self.assertAlmostEqual(stream["x_primary"][t], stream["x_true"][t])
            expected_a = BASELINE_A + (0.5 if t >= EVENT_T else 0.0)
            self.assertAlmostEqual(stream["a"][t], expected_a)

    def test_reference_fault_equation(self):
        stream = generate_experiment_009_stream(93, "drift_reference_fault", 1.0)
        for t in range(1, len(stream["x_true"])):
            expected = (
                stream["x_true"][t]
                + SIGMA_REF * stream["reference_unit_noise"][t]
                + stream["true_sigma_ref_fault"][t] * stream["reference_fault_unit_noise"][t]
            )
            self.assertAlmostEqual(stream["x_ref"][t], expected)

    def test_same_seed_shares_latent_draws_across_families(self):
        a = generate_experiment_009_stream(94, "common_mode", 0.25)
        b = generate_experiment_009_stream(94, "drift_reference_fault", 1.0)
        self.assertEqual(a["x_true"], b["x_true"])
        self.assertEqual(a["physical_epsilon"], b["physical_epsilon"])
        self.assertEqual(a["primary_unit_noise"], b["primary_unit_noise"])
        self.assertEqual(a["reference_unit_noise"], b["reference_unit_noise"])
        self.assertEqual(a["reference_fault_unit_noise"], b["reference_fault_unit_noise"])

    def test_kappa_is_reused_from_experiment_008(self):
        self.assertGreater(calibrate_kappa(), 0.0)

    def test_invalid_parameters_rejected(self):
        with self.assertRaises(ValueError):
            generate_experiment_009_stream(1, "bad", 0.5)
        with self.assertRaises(ValueError):
            generate_experiment_009_stream(1, "common_mode", -0.1)


if __name__ == "__main__":
    unittest.main()
