import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from adaptive_model_gating import calibrate_tau
from experiment_008 import calibrate_kappa
from experiment_010 import calibrate_kappa3
from experiment_011 import calibrate_lambda_anchor
from experiment_012 import calibrate_dual_anchor_thresholds
from experiment_013 import calibrate_anchor_c_thresholds
from experiment_015 import *

class Experiment015Tests(unittest.TestCase):
 def test_probe_blocks_do_not_change_operational_channels(self):
  a=generate_experiment_015_stream(1801,'healthy',0.0)
  b=generate_experiment_014_stream(1801,'healthy',0.0,rho_override=0.0)
  for k in ('x_true','x_primary','x_r1','x_r2','z','z_b','z_c','y','a'):
   self.assertEqual(a[k],b[k])
 def test_standard_probe_reciprocal_ab_response(self):
  s=generate_experiment_015_stream(1802,'healthy',0.0);R=probe_response_matrix(s)
  self.assertGreater(R[('a','b')],0.10);self.assertGreater(R[('b','a')],0.10)
  self.assertLess(abs(R[('c','a')]),0.10);self.assertLess(abs(R[('a','c')]),0.10)
 def test_probe_calibration_deterministic_positive(self):
  a=calibrate_lambda_probe();b=calibrate_lambda_probe();self.assertEqual(a,b);self.assertGreater(a,0)
 def test_standard_partition_recovery_on_smoke_seed(self):
  s=generate_experiment_015_stream(1803,'healthy',0.0);g,_=infer_probe_groups(s,calibrate_lambda_probe());self.assertEqual(partition_matches(g),1)
 def test_weak_probe_is_weaker(self):
  a=probe_response_matrix(generate_experiment_015_stream(1804,'drift_ab_fault',0.5));w=probe_response_matrix(generate_experiment_015_stream(1804,'drift_ab_weak_probe',0.5));self.assertLess(w[('a','b')],a[('a','b')])
 def test_cross_coupled_probe_affects_c(self):
  s=generate_experiment_015_stream(1805,'drift_ab_cross_coupled_probe',0.5);R=probe_response_matrix(s);self.assertGreater(R[('c','a')],0.10);self.assertGreater(R[('c','b')],0.10)
 def test_legacy_comparator_compatibility(self):
  s=generate_experiment_015_stream(1806,'healthy',0.0)
  for key in ('x_ref','reference_unit_noise','true_sigma_x','ref_fault_unit_noise','primary_fault_sigma','ref1_fault_sigma','common_sigma'):self.assertIn(key,s)
  tau=calibrate_tau();k=calibrate_kappa();k3=calibrate_kappa3();la=calibrate_lambda_anchor();lb,lab=calibrate_dual_anchor_thresholds();lc,lac,lbc=calibrate_anchor_c_thresholds();lp=calibrate_lambda_probe()
  for st in ('frozen','health_persistence','triad_persistence','interventional_provenance_quorum'):
   rows=run_experiment_015_strategy(1806,'healthy',0.0,st,tau,k,k3,la,lb,lc,lab,lac,lbc,lp);self.assertEqual(len(rows),900);self.assertTrue(all('latent_input_sq_error' in r for r in rows))

if __name__=='__main__':unittest.main()
