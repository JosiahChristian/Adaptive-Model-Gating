import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adaptive_model_gating import BASELINE_A, EVENT_T
from experiment_007 import generate_input_sensor_corruption_stream


class InputSensorCorruptionTests(unittest.TestCase):
    def test_physical_system_is_unchanged(self):
        x_obs, y, x_true, a, sigma, eps, sensor = generate_input_sensor_corruption_stream(71, 0.5, None)
        for t in range(1, len(x_obs)):
            self.assertEqual(a[t], BASELINE_A)
            self.assertAlmostEqual(y[t], BASELINE_A * x_true[t] + eps[t])
            self.assertAlmostEqual(x_obs[t], x_true[t] + sigma[t] * sensor[t])

    def test_transient_and_persistent_match_through_t420(self):
        transient = generate_input_sensor_corruption_stream(72, 1.0, 20)
        persistent = generate_input_sensor_corruption_stream(72, 1.0, None)
        for arrays_t, arrays_p in zip(transient, persistent):
            for t in range(1, EVENT_T + 20):
                self.assertEqual(arrays_t[t], arrays_p[t])
        sigma_t = transient[4]
        sigma_p = persistent[4]
        self.assertEqual(sigma_t[EVENT_T + 19], 1.0)
        self.assertEqual(sigma_t[EVENT_T + 20], 0.0)
        self.assertEqual(sigma_p[EVENT_T + 20], 1.0)

    def test_same_seed_shares_physical_and_sensor_draws_across_magnitudes(self):
        a = generate_input_sensor_corruption_stream(73, 0.25, None)
        b = generate_input_sensor_corruption_stream(73, 1.0, None)
        self.assertEqual(a[2], b[2])  # latent physical x
        self.assertEqual(a[1], b[1])  # physical y
        self.assertEqual(a[5], b[5])  # physical epsilon
        self.assertEqual(a[6], b[6])  # unit sensor noise

    def test_pre_event_observed_input_equals_latent_input(self):
        x_obs, _, x_true, _, sigma, _, _ = generate_input_sensor_corruption_stream(74, 1.0, None)
        for t in range(1, EVENT_T):
            self.assertEqual(sigma[t], 0.0)
            self.assertEqual(x_obs[t], x_true[t])

    def test_invalid_parameters_rejected(self):
        with self.assertRaises(ValueError):
            generate_input_sensor_corruption_stream(1, -0.1, None)
        with self.assertRaises(ValueError):
            generate_input_sensor_corruption_stream(1, 0.5, 0)


if __name__ == "__main__":
    unittest.main()
