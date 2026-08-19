import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from adaptive_model_gating import EVENT_T
from experiment_011 import calibrate_lambda_anchor
from experiment_012 import generate_experiment_012_stream, calibrate_dual_anchor_thresholds, run_experiment_012_strategy
from adaptive_model_gating import calibrate_tau
from experiment_008 import calibrate_kappa
from experiment_010 import calibrate_kappa3

class Experiment012Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tau=calibrate_tau(); cls.k=calibrate_kappa(); cls.k3=calibrate_kappa3(); cls.la=calibrate_lambda_anchor(); cls.lb,cls.lab=calibrate_dual_anchor_thresholds()
    def test_thresholds_positive_and_finite(self):
        self.assertGreater(self.lb,0); self.assertGreater(self.lab,0); self.assertGreater(self.la,0)
    def test_single_anchor_fault_is_source_specific(self):
        healthy=generate_experiment_012_stream(12000,"drift",0.5); a=generate_experiment_012_stream(12000,"drift_anchor_a_fault",0.5); b=generate_experiment_012_stream(12000,"drift_anchor_b_fault",0.5)
        t=EVENT_T
        self.assertEqual(a["z_b"][t],healthy["z_b"][t]); self.assertNotEqual(a["z"][t],healthy["z"][t]); self.assertEqual(b["z"][t],healthy["z"][t]); self.assertNotEqual(b["z_b"][t],healthy["z_b"][t])
    def test_dual_fault_is_coherent(self):
        s=generate_experiment_012_stream(12001,"drift_dual_anchor_fault",1.0); h=generate_experiment_012_stream(12001,"drift",1.0); t=EVENT_T
        self.assertAlmostEqual((s["z"][t]-h["z"][t]),(s["z_b"][t]-h["z_b"][t]))
    def test_all_strategies_share_stream_and_run(self):
        strategies=["frozen","continuous","threshold","persistence","health_persistence","triad_persistence","independent_persistence","dual_independent_arbitration"]
        first=None
        for strategy in strategies:
            rows=run_experiment_012_strategy(12000,"healthy",0.0,strategy,self.tau,self.k,self.k3,self.la,self.lb,self.lab)
            self.assertEqual(len(rows),900); sig=(rows[0]["x_true"],rows[0]["x_primary"],rows[0]["z"],rows[0]["z_b"])
            if first is None: first=sig
            self.assertEqual(sig,first)
    def test_dual_veto_requires_both_mismatch_and_anchor_agreement(self):
        rows=run_experiment_012_strategy(12002,"common_mode",1.0,"dual_independent_arbitration",self.tau,self.k,self.k3,self.la,self.lb,self.lab)
        for r in rows:
            if r["veto_common_mode_suspect"]:
                self.assertEqual(r["anchor_mismatch"],1); self.assertEqual(r["anchor_b_mismatch"],1); self.assertEqual(r["anchor_ab_disagreement"],0)

if __name__=="__main__": unittest.main()
