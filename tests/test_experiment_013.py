import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from experiment_013 import *
from experiment_011 import calibrate_lambda_anchor
from experiment_012 import calibrate_dual_anchor_thresholds
from adaptive_model_gating import calibrate_tau
from experiment_008 import calibrate_kappa
from experiment_010 import calibrate_kappa3
class Experiment013Tests(unittest.TestCase):
 def test_cells_and_streams_are_deterministic(self):
  for f in FAMILIES:
   a=generate_experiment_013_stream(13000,f,.5);b=generate_experiment_013_stream(13000,f,.5);self.assertEqual(a['z_c'],b['z_c'])
 def test_g1_fault_is_coherent_and_c_unaffected(self):
  h=generate_experiment_013_stream(13000,'drift',.5);g=generate_experiment_013_stream(13000,'drift_g1_common_fault',.5)
  t=EVENT_T;self.assertAlmostEqual(g['z'][t]-h['z'][t],g['z_b'][t]-h['z_b'][t]);self.assertEqual(g['z_c'][t],h['z_c'][t])
 def test_misdeclared_changes_metadata_not_physics(self):
  a=generate_experiment_013_stream(13000,'drift_g1_common_fault',.5);b=generate_experiment_013_stream(13000,'drift_misdeclared_g1_fault',.5);self.assertEqual(a['z'],b['z']);self.assertEqual(a['z_b'],b['z_b'])
 def test_c_calibration_is_healthy_only(self):
  vals=calibrate_anchor_c_thresholds();self.assertEqual(len(vals),3);self.assertTrue(all(v>0 for v in vals))
 def test_provenance_collapses_ab_vote(self):
  tau=calibrate_tau();k=calibrate_kappa();k3=calibrate_kappa3();la=calibrate_lambda_anchor();lb,lab=calibrate_dual_anchor_thresholds();lc,lac,lbc=calibrate_anchor_c_thresholds();rows=run_experiment_013_strategy(13000,'drift_g1_common_fault',1.0,'provenance_aware_quorum',tau,k,k3,la,lb,lc,lab,lac,lbc);self.assertTrue(any(r['raw_mismatch_votes']>=2 and r['provenance_mismatch_votes']==1 for r in rows))
if __name__=='__main__':unittest.main()
