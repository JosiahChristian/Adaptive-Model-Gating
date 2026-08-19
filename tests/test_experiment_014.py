import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from adaptive_model_gating import EVENT_T
from experiment_011 import BETA_ANCHOR,SIGMA_ANCHOR
from experiment_014 import *

class Experiment014Tests(unittest.TestCase):
 def test_signature_equations_and_absent_signature(self):
  s=generate_experiment_014_stream(1600,'healthy',0.0);a=generate_experiment_014_stream(1600,'drift_ab_absent_signature',.5)
  self.assertEqual(s['rho_sig'],RHO_SIG);self.assertEqual(a['rho_sig'],0.0)
  t=200;xt=s['x_true'][t];shared=RHO_SIG*s['dependence_unit_noise'][t]
  self.assertAlmostEqual(s['z'][t],BETA_ANCHOR*xt+SIGMA_ANCHOR*(s['anchor_unit_noise'][t]+shared))
  self.assertAlmostEqual(s['z_b'][t],BETA_ANCHOR*xt+SIGMA_ANCHOR*(s['anchor_b_unit_noise'][t]+shared))
  xt=a['x_true'][t];self.assertAlmostEqual(a['z'][t],BETA_ANCHOR*xt+SIGMA_ANCHOR*a['anchor_unit_noise'][t])

 def test_misleading_signature_changes_postevent_fault_pair_only(self):
  h=generate_experiment_014_stream(1601,'drift',.5);m=generate_experiment_014_stream(1601,'drift_bc_misleading_signature',.5);t=EVENT_T
  self.assertEqual(m['z'][t],h['z'][t]);self.assertAlmostEqual(m['z_b'][t]-h['z_b'][t],m['z_c'][t]-h['z_c'][t])

 def test_connected_component_partition_semantics(self):
  self.assertEqual(partition_matches({'a':'X','b':'X','c':'Y'},{'a':'G1','b':'G1','c':'G2'}),1)
  self.assertEqual(partition_matches({'a':'X','b':'Y','c':'Y'},{'a':'G1','b':'G1','c':'G2'}),0)
  self.assertEqual(oracle_groups('drift_bc_misleading_signature')['b'],oracle_groups('drift_bc_misleading_signature')['c'])

 def test_dependence_calibration_is_deterministic_and_positive(self):
  a=calibrate_lambda_dep();b=calibrate_lambda_dep();self.assertEqual(a,b);self.assertGreater(a,0)

 def test_legacy_compatibility_surface(self):
  s=generate_experiment_014_stream(1602,'healthy',0.0)
  for k in ('x_ref','reference_unit_noise','true_sigma_x','ref_fault_unit_noise','primary_fault_sigma','ref1_fault_sigma','common_sigma'):self.assertIn(k,s)

if __name__=='__main__':unittest.main()
