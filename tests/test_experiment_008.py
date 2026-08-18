import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adaptive_model_gating import BASELINE_A, EVENT_T, calibrate_tau
from experiment_008 import (
    SIGMA_REF,
    calibrate_kappa,
    generate_sensor_health_stream,
    rolling_health_values,
    run_experiment_008_strategy,
)


class SensorHealthAwareGatingTests(unittest.TestCase):
    def test_sensor_equations_and_physical_law(self):
        stream = generate_sensor_health_stream(81, sigma_x=0.5, transient_fault_duration=None)
        for t in range(1, len(stream["y"])):
            self.assertAlmostEqual(
                stream["y"][t],
                stream["a"][t] * stream["x_true"][t] + stream["physical_epsilon"][t],
            )
            self.assertAlmostEqual(
                stream["x_primary"][t],
                stream["x_true"][t] + stream["true_sigma_x"][t] * stream["primary_unit_noise"][t],
            )
            self.assertAlmostEqual(
                stream["x_ref"][t],
                stream["x_true"][t] + SIGMA_REF * stream["reference_unit_noise"][t],
            )
            self.assertEqual(stream["a"][t], BASELINE_A)

    def test_fault_transient_and_persistent_match_through_t420(self):
        transient = generate_sensor_health_stream(82, sigma_x=1.0, transient_fault_duration=20)
        persistent = generate_sensor_health_stream(82, sigma_x=1.0, transient_fault_duration=None)
        for key in transient:
            for t in range(1, EVENT_T + 20):
                self.assertEqual(transient[key][t], persistent[key][t])
        self.assertEqual(transient["true_sigma_x"][EVENT_T + 19], 1.0)
        self.assertEqual(transient["true_sigma_x"][EVENT_T + 20], 0.0)
        self.assertEqual(persistent["true_sigma_x"][EVENT_T + 20], 1.0)

    def test_drift_changes_physics_not_sensor_health(self):
        stable = generate_sensor_health_stream(83)
        drift = generate_sensor_health_stream(83, delta_a=0.5)
        self.assertEqual(stable["x_true"], drift["x_true"])
        self.assertEqual(stable["x_primary"], drift["x_primary"])
        self.assertEqual(stable["x_ref"], drift["x_ref"])
        self.assertEqual(stable["reference_unit_noise"], drift["reference_unit_noise"])
        for t in range(1, EVENT_T):
            self.assertEqual(stable["y"][t], drift["y"][t])
        self.assertEqual(drift["a"][EVENT_T], BASELINE_A + 0.5)

    def test_health_statistic_uses_only_primary_and_reference_sensors(self):
        stream = generate_sensor_health_stream(84, sigma_x=0.5, transient_fault_duration=None)
        original = rolling_health_values(stream["x_primary"], stream["x_ref"])
        stream["x_true"] = [999.0] * len(stream["x_true"])
        stream["a"] = [999.0] * len(stream["a"])
        altered = rolling_health_values(stream["x_primary"], stream["x_ref"])
        self.assertEqual(original, altered)

    def test_kappa_is_deterministic_and_positive(self):
        a = calibrate_kappa()
        b = calibrate_kappa()
        self.assertEqual(a, b)
        self.assertGreater(a, 0.0)

    def test_health_gate_vetoes_when_residual_ready_and_sensor_unhealthy(self):
        tau = calibrate_tau()
        kappa = calibrate_kappa()
        rows = run_experiment_008_strategy(
            85, "fault", 1.0, None, "health_persistence", tau, kappa
        )
        vetoes = [r for r in rows if r["health_veto"]]
        self.assertTrue(vetoes)
        self.assertTrue(all(r["sensor_unhealthy"] for r in vetoes))
        self.assertTrue(all(not r["adapt"] for r in vetoes))

    def test_invalid_combined_fault_and_drift_rejected(self):
        with self.assertRaises(ValueError):
            generate_sensor_health_stream(1, sigma_x=0.5, delta_a=0.5)


if __name__ == "__main__":
    unittest.main()
