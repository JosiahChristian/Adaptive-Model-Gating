import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adaptive_model_gating import BASELINE_A, EVENT_T
from experiment_006 import generate_measurement_corruption_stream


class MeasurementCorruptionTests(unittest.TestCase):
    def test_clean_system_is_unchanged(self):
        x, y, clean, a, sigma, eps, sensor = generate_measurement_corruption_stream(61, 1.0, None)
        for t in range(1, len(x)):
            self.assertEqual(a[t], BASELINE_A)
            self.assertAlmostEqual(clean[t], BASELINE_A * x[t] + eps[t])
            self.assertAlmostEqual(y[t], clean[t] + sigma[t] * sensor[t])

    def test_transient_and_persistent_match_through_t420(self):
        t_stream = generate_measurement_corruption_stream(62, 2.0, 20)
        p_stream = generate_measurement_corruption_stream(62, 2.0, None)
        for arrays_t, arrays_p in zip(t_stream, p_stream):
            for t in range(1, EVENT_T + 20):
                self.assertEqual(arrays_t[t], arrays_p[t])
        sigma_t = t_stream[4]
        sigma_p = p_stream[4]
        self.assertEqual(sigma_t[EVENT_T + 19], 2.0)
        self.assertEqual(sigma_t[EVENT_T + 20], 0.0)
        self.assertEqual(sigma_p[EVENT_T + 20], 2.0)

    def test_same_seed_shares_base_draws_across_magnitudes(self):
        a = generate_measurement_corruption_stream(63, 0.5, None)
        b = generate_measurement_corruption_stream(63, 2.0, None)
        self.assertEqual(a[0], b[0])  # x
        self.assertEqual(a[2], b[2])  # clean y
        self.assertEqual(a[5], b[5])  # baseline epsilon
        self.assertEqual(a[6], b[6])  # unit sensor noise

    def test_invalid_parameters_rejected(self):
        with self.assertRaises(ValueError):
            generate_measurement_corruption_stream(1, -0.1, None)
        with self.assertRaises(ValueError):
            generate_measurement_corruption_stream(1, 0.5, 0)


if __name__ == "__main__":
    unittest.main()
