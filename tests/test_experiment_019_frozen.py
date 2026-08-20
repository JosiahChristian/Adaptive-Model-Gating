import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from experiment_017 import calibrate_cumulative_thresholds,generate_experiment_017_stream,infer_selective_cumulative
from experiment_018 import calibrate_round5_thresholds
from experiment_019 import TARGETED_CALIBRATION_SEEDS,calibrate_targeted_thresholds,inject_targeted_round5,leading_edge,run_experiment_019_strategy

class TestExperiment019Frozen(unittest.TestCase):
 def test_seed_ranges_disjoint(self):
  self.assertEqual((min(TARGETED_CALIBRATION_SEEDS),max(TARGETED_CALIBRATION_SEEDS)),(4000,4999));self.assertTrue(set(TARGETED_CALIBRATION_SEEDS).isdisjoint(range(19000,19200)))
 def test_selector_unique_max(self):
  self.assertEqual(leading_edge({('a','b'):3,('a','c'):2,('b','c'):1}),('a','b'));self.assertIsNone(leading_edge({('a','b'):3,('a','c'):3,('b','c'):1}))
 def test_targeted_round_uses_only_two_blocks(self):
  s=generate_experiment_017_stream(19000,'drift_ab_gain050',1.0);t=inject_targeted_round5(s,('a','b'))
  changed=[i for i in range(261,276) if any(t[f'probe_obs_{x}'][i]!=s[f'probe_obs_{x}'][i] for x in 'abc')]
  self.assertEqual(changed,list(range(261,271)))
 def test_targeted_max_incremental_energy(self):
  self.assertAlmostEqual(2*5*(0.2**2),0.4);self.assertAlmostEqual(0.796875+0.4,1.196875)
 def test_calibration_returns_ordered_thresholds(self):
  mu,nu=calibrate_cumulative_thresholds();a,b=calibrate_targeted_thresholds(mu,nu);self.assertLessEqual(a,b)
 def test_abstention_falls_back_operationally(self):
  from adaptive_model_gating import calibrate_tau
  from experiment_008 import calibrate_kappa
  from experiment_010 import calibrate_kappa3
  from experiment_011 import calibrate_lambda_anchor
  from experiment_012 import calibrate_dual_anchor_thresholds
  from experiment_013 import calibrate_anchor_c_thresholds
  from experiment_016 import calibrate_lambda_probe_rounds
  tau=calibrate_tau();k=calibrate_kappa();k3=calibrate_kappa3();la=calibrate_lambda_anchor();lb,lab=calibrate_dual_anchor_thresholds();lc,lac,lbc=calibrate_anchor_c_thresholds();lambdas=calibrate_lambda_probe_rounds();mu,nu=calibrate_cumulative_thresholds();mu5,nu5=calibrate_round5_thresholds();mu5t,nu5t=calibrate_targeted_thresholds(mu,nu)
  a=run_experiment_019_strategy(19000,'drift_ab_gain0125',1.0,'targeted_replicated_selective_cumulative_provenance_quorum',tau,k,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5,mu5t,nu5t)
  b=run_experiment_019_strategy(19000,'drift_ab_gain0125',1.0,'triad_persistence',tau,k,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5,mu5t,nu5t)
  self.assertEqual([(r['adapt'],r['slope_after']) for r in a],[(r['adapt'],r['slope_after']) for r in b])

if __name__=='__main__':unittest.main()
