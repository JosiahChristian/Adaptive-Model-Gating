import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from adaptive_model_gating import calibrate_tau
from experiment_008 import calibrate_kappa
from experiment_010 import calibrate_kappa3
from experiment_011 import calibrate_lambda_anchor
from experiment_012 import calibrate_dual_anchor_thresholds
from experiment_013 import calibrate_anchor_c_thresholds
from experiment_016 import calibrate_lambda_probe_rounds,probe_energy
from experiment_017 import CUMULATIVE_CALIBRATION_SEEDS,calibrate_cumulative_thresholds,cumulative_statistics,generate_experiment_017_stream,infer_selective_cumulative
from experiment_017_dispatch import run_experiment_017_strategy

class Experiment017Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.lambdas=calibrate_lambda_probe_rounds();cls.mu,cls.nu=calibrate_cumulative_thresholds()
 def test_calibration_sets_are_frozen_and_disjoint(self):
  self.assertEqual((CUMULATIVE_CALIBRATION_SEEDS.start,CUMULATIVE_CALIBRATION_SEEDS.stop),(2000,3000));self.assertTrue(set(CUMULATIVE_CALIBRATION_SEEDS).isdisjoint(range(17000,17200)))
 def test_threshold_order(self):
  self.assertEqual(len(self.mu),4);self.assertEqual(len(self.nu),4);self.assertTrue(all(a>0 and b>=a for a,b in zip(self.mu,self.nu)))
 def test_gain_cells_preserve_operational_streams(self):
  streams=[generate_experiment_017_stream(3101,f,0.5) for f in ('drift_ab_fault','drift_ab_gain050','drift_ab_gain0375','drift_ab_gain025','drift_ab_gain0125')]
  self.assertEqual([s['probe_gain'] for s in streams],[1.0,.5,.375,.25,.125])
  for key in ('x_true','x_primary','x_r1','x_r2','y','z','z_b','z_c'):
   for s in streams[1:]:self.assertEqual(streams[0][key],s[key])
 def test_cumulative_statistic_uses_only_completed_rounds(self):
  s=generate_experiment_017_stream(3102,'drift_ab_fault',.5);c1,_=cumulative_statistics(s,1)
  for r in (2,3,4):
   for ts in [x for b in __import__('experiment_016').ROUND_BLOCKS[r].values() for x in b]:
    for x in 'abc':s[f'probe_obs_{x}'][ts]+=10000
  c2,_=cumulative_statistics(s,1);self.assertEqual(c1,c2)
 def test_selective_never_uses_future_round_after_accept(self):
  s=generate_experiment_017_stream(3103,'drift_ab_fault',.5);g,e,stop,accepted,abstain,c=infer_selective_cumulative(s,self.mu,self.nu)
  if accepted and stop<4:
   before=(g,stop,accepted,abstain,set(e))
   from experiment_016 import ROUND_BLOCKS
   for r in range(stop+1,5):
    for ts in ROUND_BLOCKS[r].values():
     for t in ts:
      for x in 'abc':s[f'probe_obs_{x}'][t]+=1e6
   g2,e2,stop2,a2,ab2,c2=infer_selective_cumulative(s,self.mu,self.nu);self.assertEqual(before,(g2,stop2,a2,ab2,set(e2)))
 def test_full_ladder_energy(self):
  self.assertAlmostEqual(probe_energy({1:None,2:None,3:None,4:None}),0.796875);self.assertAlmostEqual(probe_energy({4:None}),0.6)
 def test_new_strategies_and_gain_aware_comparators_run(self):
  tau=calibrate_tau();k=calibrate_kappa();k3=calibrate_kappa3();la=calibrate_lambda_anchor();lb,lab=calibrate_dual_anchor_thresholds();lc,lac,lbc=calibrate_anchor_c_thresholds();vals=(tau,k,k3,la,lb,lc,lab,lac,lbc,self.lambdas,self.mu,self.nu)
  for st in ('triad_persistence','sequential_provenance_quorum','cumulative_provenance_quorum','selective_cumulative_provenance_quorum'):
   rows=run_experiment_017_strategy(3104,'drift_ab_gain0375',.5,st,*vals);self.assertEqual(len(rows),900)
   if st!='triad_persistence':self.assertAlmostEqual(float(rows[-1]['probe_gain']),.375)
 def test_abstention_is_exact_triad_fallback_on_forced_high_confidence_threshold(self):
  tau=calibrate_tau();k=calibrate_kappa();k3=calibrate_kappa3();la=calibrate_lambda_anchor();lb,lab=calibrate_dual_anchor_thresholds();lc,lac,lbc=calibrate_anchor_c_thresholds();huge=(1e9,)*4
  sel=run_experiment_017_strategy(3105,'drift_ab_gain0125',.5,'selective_cumulative_provenance_quorum',tau,k,k3,la,lb,lc,lab,lac,lbc,self.lambdas,huge,huge)
  tri=run_experiment_017_strategy(3105,'drift_ab_gain0125',.5,'triad_persistence',tau,k,k3,la,lb,lc,lab,lac,lbc,self.lambdas,huge,huge)
  self.assertEqual([r['sq_error'] for r in sel],[r['sq_error'] for r in tri]);self.assertTrue(all(r['provenance_abstain']==1 for r in sel))

if __name__=='__main__':unittest.main()
