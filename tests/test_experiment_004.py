import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adaptive_model_gating import BASELINE_A, EVENT_T
from experiment_004 import generate_structural_mismatch_stream

class StructuralMismatchTests(unittest.TestCase):
    def test_quadratic_term_exactly_matches_frozen_equation(self):
        gamma = 0.5
        x0, y0, a0, g0 = generate_structural_mismatch_stream(41, 0.0, None)
        x1, y1, a1, g1 = generate_structural_mismatch_stream(41, gamma, None)
        self.assertEqual(x0, x1)
        self.assertEqual(a0, a1)
        for t in range(1, EVENT_T):
            self.assertEqual(y0[t], y1[t])
            self.assertEqual(g1[t], 0.0)
        for t in range(EVENT_T, len(x1)):
            self.assertAlmostEqual(y1[t] - y0[t], gamma * x1[t] * x1[t])
            self.assertEqual(g1[t], gamma)
            self.assertEqual(a1[t], BASELINE_A)

    def test_transient_and_persistent_streams_match_through_t420(self):
        xt, yt, at, gt = generate_structural_mismatch_stream(52, 1.0, 20)
        xp, yp, ap, gp = generate_structural_mismatch_stream(52, 1.0, None)
        for t in range(1, EVENT_T + 20):
            self.assertEqual((xt[t], yt[t], at[t], gt[t]), (xp[t], yp[t], ap[t], gp[t]))
        self.assertEqual(gt[EVENT_T + 19], 1.0)
        self.assertEqual(gt[EVENT_T + 20], 0.0)
        self.assertEqual(gp[EVENT_T + 20], 1.0)

    def test_invalid_parameters_rejected(self):
        with self.assertRaises(ValueError):
            generate_structural_mismatch_stream(1, -0.1, None)
        with self.assertRaises(ValueError):
            generate_structural_mismatch_stream(1, 0.5, 0)

if __name__ == "__main__":
    unittest.main()
