import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from adaptive_model_gating import BASELINE_A, EVENT_T, calibrate_tau
from experiment_008 import calibrate_kappa
from experiment_010 import SIGMA_REF, calibrate_kappa3
from experiment_011 import BETA_ANCHOR, SIGMA_ANCHOR, calibrate_lambda_anchor, generate_experiment_011_stream, run_experiment_011_strategy

class Experiment011Tests(unittest.TestCase):
    def test_common_mode_leaves_anchor_independent(self):
        s=generate_experiment_011_stream(11000,"common_mode",0.5)
        for t in range(EVENT_T, len(s["x_true"])):
            shared=0.5*s["common_unit_noise"][t]
            self.assertAlmostEqual(s["x_primary"][t]-s["x_true"][t], shared)
            self.assertAlmostEqual(s["x_r1"][t]-s["x_true"][t]-SIGMA_REF*s["r1_unit_noise"][t], shared)
            self.assertAlmostEqual(s["x_r2"][t]-s["x_true"][t]-SIGMA_REF*s["r2_unit_noise"][t], shared)
            self.assertAlmostEqual(s["z"][t], BETA_ANCHOR*s["x_true"][t]+SIGMA_ANCHOR*s["anchor_unit_noise"][t])

    def test_drift_does_not_change_anchor_law(self):
        s=generate_experiment_011_stream(11001,"drift",1.0)
        self.assertEqual(s["a"][EVENT_T], BASELINE_A+1.0)
        for t in range(EVENT_T, len(s["x_true"])):
            self.assertEqual(s["x_primary"][t], s["x_true"][t])
            self.assertAlmostEqual(s["z"][t], BETA_ANCHOR*s["x_true"][t]+SIGMA_ANCHOR*s["anchor_unit_noise"][t])

    def test_anchor_fault_equation(self):
        s=generate_experiment_011_stream(11002,"drift_anchor_fault",0.5)
        for t in range(EVENT_T, len(s["x_true"])):
            expected=BETA_ANCHOR*s["x_true"][t]+SIGMA_ANCHOR*s["anchor_unit_noise"][t]+BETA_ANCHOR*0.5*s["anchor_fault_unit_noise"][t]
            self.assertAlmostEqual(s["z"][t], expected)
            self.assertEqual(s["a"][t], BASELINE_A+0.5)

    def test_primary_fault_preserves_references_and_anchor(self):
        s=generate_experiment_011_stream(11003,"primary_fault",1.0)
        for t in range(EVENT_T, len(s["x_true"])):
            self.assertAlmostEqual(s["x_primary"][t],s["x_true"][t]+s["primary_unit_noise"][t])
            self.assertAlmostEqual(s["x_r1"][t],s["x_true"][t]+SIGMA_REF*s["r1_unit_noise"][t])
            self.assertAlmostEqual(s["x_r2"][t],s["x_true"][t]+SIGMA_REF*s["r2_unit_noise"][t])

    def test_independent_strategy_uses_primary_only(self):
        rows=run_experiment_011_strategy(11004,"common_mode",0.5,"independent_persistence",calibrate_tau(),calibrate_kappa(),calibrate_kappa3(),calibrate_lambda_anchor())
        for r in rows: self.assertEqual(r["x"],r["x_primary"])

    def test_calibration_is_deterministic_positive(self):
        a=calibrate_lambda_anchor(); b=calibrate_lambda_anchor()
        self.assertEqual(a,b); self.assertGreater(a,0)

    def test_invalid_family(self):
        with self.assertRaises(ValueError): generate_experiment_011_stream(1,"bad",0.5)

if __name__ == "__main__": unittest.main()
