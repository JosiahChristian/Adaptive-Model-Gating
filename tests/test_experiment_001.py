import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adaptive_model_gating import (
    EVENT_T,
    TRANSIENT_END_T,
    generate_stream,
    run_strategy,
    true_a,
)


class Experiment001Tests(unittest.TestCase):
    def test_transient_and_persistent_true_parameter_match_at_onset(self):
        for t in range(EVENT_T, TRANSIENT_END_T + 1):
            self.assertEqual(true_a("transient", t), true_a("persistent", t))

    def test_transient_reverts_and_persistent_does_not(self):
        self.assertEqual(true_a("transient", TRANSIENT_END_T + 1), 1.5)
        self.assertEqual(true_a("persistent", TRANSIENT_END_T + 1), 2.0)

    def test_same_seed_has_identical_matched_onset_observations(self):
        xt, yt, _ = generate_stream(1234, "transient")
        xp, yp, _ = generate_stream(1234, "persistent")
        for t in range(1, TRANSIENT_END_T + 1):
            self.assertEqual(xt[t], xp[t])
            self.assertEqual(yt[t], yp[t])

    def test_frozen_never_adapts(self):
        rows = run_strategy(1000, "persistent", "frozen", tau=1.0)
        self.assertFalse(any(r["adapt"] for r in rows))

    def test_adaptation_affects_next_prediction_not_current_prediction(self):
        rows = run_strategy(1000, "persistent", "continuous", tau=1.0)
        first = rows[0]
        self.assertEqual(first["adapt"], 1)
        # The scored prediction used the pre-decision parameters.
        expected = first["slope_before"] * first["x"] + first["intercept_before"]
        self.assertAlmostEqual(first["y_hat"], expected)

    def test_hidden_true_a_is_logging_only(self):
        # Changing tau changes gate behavior; true_a is not accepted as a gate input.
        low = run_strategy(1001, "persistent", "threshold", tau=0.0)
        high = run_strategy(1001, "persistent", "threshold", tau=10**9)
        self.assertGreater(sum(r["adapt"] for r in low), sum(r["adapt"] for r in high))


if __name__ == "__main__":
    unittest.main()
