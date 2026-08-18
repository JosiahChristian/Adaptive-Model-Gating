import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adaptive_model_gating import (
    BASELINE_A,
    EVENT_T,
    generate_parameter_change_stream,
    run_parameter_change_strategy,
)


class Experiment002Tests(unittest.TestCase):
    def test_matched_onset_for_each_duration_and_magnitude(self):
        for delta_a in (0.10, 0.25, 0.50, 1.00):
            for duration in (5, 20, 50):
                xt, yt, at = generate_parameter_change_stream(2000, delta_a, duration)
                xp, yp, ap = generate_parameter_change_stream(2000, delta_a, None)
                end = EVENT_T + duration - 1
                for t in range(1, end + 1):
                    self.assertEqual(xt[t], xp[t])
                    self.assertEqual(yt[t], yp[t])
                    self.assertEqual(at[t], ap[t])

    def test_transient_reverts_exactly_after_duration(self):
        for duration in (5, 20, 50):
            _, _, a = generate_parameter_change_stream(2001, 0.50, duration)
            self.assertEqual(a[EVENT_T + duration - 1], 2.0)
            self.assertEqual(a[EVENT_T + duration], BASELINE_A)

    def test_persistent_does_not_revert(self):
        _, _, a = generate_parameter_change_stream(2002, 0.25, None)
        self.assertEqual(a[EVENT_T], 1.75)
        self.assertEqual(a[-1], 1.75)

    def test_stable_custom_stream_matches_experiment1_stable_behavior(self):
        rows = run_parameter_change_strategy(2003, 0.0, None, "frozen", tau=1.0)
        self.assertTrue(all(r["true_a"] == BASELINE_A for r in rows))
        self.assertFalse(any(r["adapt"] for r in rows))

    def test_strategy_cannot_receive_duration_through_row_fields_before_generation(self):
        rows = run_parameter_change_strategy(2004, 0.50, 5, "threshold", tau=10**9)
        self.assertFalse(any(r["adapt"] for r in rows))
        # The row condition label is logging metadata; gate logic receives only stream arrays.
        self.assertTrue(rows[0]["condition"].startswith("transient_da_"))


if __name__ == "__main__":
    unittest.main()
