import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from adaptive_model_gating import calibrate_tau
from experiment_008 import calibrate_kappa
from experiment_010 import calibrate_kappa3
from experiment_011 import calibrate_lambda_anchor
from experiment_012 import calibrate_dual_anchor_thresholds
from experiment_013 import calibrate_anchor_c_thresholds
from experiment_016 import calibrate_lambda_probe_rounds
from experiment_017 import calibrate_cumulative_thresholds
from experiment_018 import (
 ALL_AMPLITUDES,ROUND5_AMPLITUDE,ROUND5_BLOCKS,calibrate_round5_thresholds,
 generate_experiment_018_stream,infer_replicated_selective,run_experiment_018_strategy,
)

class Experiment018Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.lambdas=calibrate_lambda_probe_rounds();cls.mu,cls.nu=calibrate_cumulative_thresholds();cls.mu5,cls.nu5=calibrate_round5_thresholds()

 def test_frozen_round5_schedule_and_amplitude(self):
  self.assertEqual(ROUND5_AMPLITUDE,0.2);self.assertEqual(ALL_AMPLITUDES,(0.025,0.05,0.1,0.2,0.2))
  vals=[t for ts in ROUND5_BLOCKS.values() for t in ts]
  self.assertEqual((min(vals),max(vals)),(261,275));self.assertEqual(len(vals),15)

 def test_round5_thresholds_positive_and_ordered(self):
  self.assertGreater(self.mu5,0);self.assertGreater(self.nu5,self.mu5)

 def test_round5_changes_only_diagnostic_observations(self):
  from experiment_017 import generate_experiment_017_stream
  a=generate_experiment_017_stream(4001,'drift_ab_gain050',0.5)
  b=generate_experiment_018_stream(4001,'drift_ab_gain050',0.5)
  for key in ('x_true','x_primary','x_r1','x_r2','y','z','z_b','z_c'):
   self.assertEqual(a[key],b[key])
  self.assertEqual(a['probe_gain'],b['probe_gain'])
  self.assertNotEqual(a['probe_obs_a'][261:276],b['probe_obs_a'][261:276])

 def test_standard_gain_stops_before_round5_on_non_evaluation_seed(self):
  s=generate_experiment_018_stream(4002,'drift_ab_fault',0.5)
  g,e,stop,acc,abst,cand,rescued,r5=infer_replicated_selective(s,self.mu,self.nu,self.mu5,self.nu5)
  self.assertEqual(acc,1);self.assertEqual(abst,0);self.assertLess(stop,5);self.assertNotIn(5,e);self.assertEqual(rescued,0)

 def test_round5_energy_ceiling(self):
  maximum=15*sum(d*d for d in ALL_AMPLITUDES)
  self.assertAlmostEqual(maximum,1.396875)
  self.assertAlmostEqual(15*ROUND5_AMPLITUDE**2,0.6)

 def test_all_strategy_compatibility_and_fallback_schema(self):
  tau=calibrate_tau();k=calibrate_kappa();k3=calibrate_kappa3();la=calibrate_lambda_anchor();lb,lab=calibrate_dual_anchor_thresholds();lc,lac,lbc=calibrate_anchor_c_thresholds()
  vals=(tau,k,k3,la,lb,lc,lab,lac,lbc,self.lambdas,self.mu,self.nu,self.mu5,self.nu5)
  strategies=('triad_persistence','selective_cumulative_provenance_quorum','replicated_selective_cumulative_provenance_quorum')
  for st in strategies:
   rows=run_experiment_018_strategy(4003,'drift_ab_gain0125',0.5,st,*vals)
   self.assertEqual(len(rows),900);self.assertIn('latent_input_sq_error',rows[-1]);self.assertIn('probe_energy',rows[-1])
  rep=run_experiment_018_strategy(4003,'drift_ab_gain0125',0.5,'replicated_selective_cumulative_provenance_quorum',*vals)
  tri=run_experiment_018_strategy(4003,'drift_ab_gain0125',0.5,'triad_persistence',*vals)
  if rep[0]['provenance_abstain']==1:
   for a,b in zip(rep,tri):
    self.assertEqual(a['adapt'],b['adapt']);self.assertEqual(a['sq_error'],b['sq_error']);self.assertEqual(a['slope_after'],b['slope_after'])
   self.assertEqual(rep[0]['round5_executed'],1)

if __name__=='__main__':unittest.main()
