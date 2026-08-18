import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adaptive_model_gating import BASELINE_A, EVENT_T
from experiment_005 import generate_covariate_shift_stream


class CovariateShiftTests(unittest.TestCase):
    def test_shift_changes_x_but_not_conditional_response_law(self):
        mu = 1.0
        x0, y0, a0, m0, z0 = generate_covariate_shift_stream(61, 0.0, None)
        x1, y1, a1, m1, z1 = generate_covariate_shift_stream(61, mu, None)
        self.assertEqual(z0, z1)
        self.assertEqual(a0, a1)
        for t in range(1, EVENT_T):
            self.assertEqual((x0[t], y0[t], m1[t]), (x1[t], y1[t], 0.0))
        for t in range(EVENT_T, len(x1)):
            self.assertAlmostEqual(x1[t] - x0[t], mu)
            self.assertAlmostEqual(y1[t] - y0[t], BASELINE_A * mu)
            self.assertEqual(m1[t], mu)
            self.assertAlmostEqual(x1[t], z1[t] + mu)

    def test_transient_and_persistent_streams_match_through_t420(self):
        xt, yt, at, mt, zt = generate_covariate_shift_stream(72, 2.0, 20)
        xp, yp, ap, mp, zp = generate_covariate_shift_stream(72, 2.0, None)
        self.assertEqual(zt, zp)
        for t in range(1, EVENT_T + 20):
            self.assertEqual((xt[t], yt[t], at[t], mt[t]), (xp[t], yp[t], ap[t], mp[t]))
        self.assertEqual(mt[EVENT_T + 19], 2.0)
        self.assertEqual(mt[EVENT_T + 20], 0.0)
        self.assertEqual(mp[EVENT_T + 20], 2.0)

    def test_transient_reverts_exactly_without_latent_state_carryover(self):
        mu = 0.5
        xt, yt, at, mt, zt = generate_covariate_shift_stream(83, mu, 20)
        x0, y0, a0, m0, z0 = generate_covariate_shift_stream(83, 0.0, None)
        self.assertEqual(zt, z0)
        self.assertEqual(mt[EVENT_T + 20], 0.0)
        self.assertEqual(xt[EVENT_T + 20], x0[EVENT_T + 20])
        self.assertEqual(yt[EVENT_T + 20], y0[EVENT_T + 20])

    def test_invalid_parameters_rejected(self):
        with self.assertRaises(ValueError):
            generate_covariate_shift_stream(1, -0.1, None)
        with self.assertRaises(ValueError):
            generate_covariate_shift_stream(1, 0.5, 0)


if __name__ == "__main__":
    unittest.main()
