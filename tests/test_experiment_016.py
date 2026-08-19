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
from experiment_016 import (
    ROUND_AMPLITUDES,ROUND_BLOCKS,SIGMA_PROBE,calibrate_lambda_probe_rounds,
    generate_experiment_016_stream,infer_round_groups,infer_sequential_groups,
    partition_matches,probe_energy,run_experiment_016_strategy,
)

class Experiment016Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.thresholds=calibrate_lambda_probe_rounds()

    def test_frozen_round_schedule(self):
        self.assertEqual(ROUND_AMPLITUDES,(0.025,0.05,0.1,0.2))
        expected={1:(201,215),2:(216,230),3:(231,245),4:(246,260)}
        for rnd,blocks in ROUND_BLOCKS.items():
            vals=[t for ts in blocks.values() for t in ts]
            self.assertEqual((min(vals),max(vals)),expected[rnd]);self.assertEqual(len(vals),15)

    def test_gain_construction(self):
        a=generate_experiment_016_stream(2001,'drift_ab_fault',0.5)
        b=generate_experiment_016_stream(2001,'drift_ab_gain050',0.5)
        c=generate_experiment_016_stream(2001,'drift_ab_gain025',0.5)
        self.assertEqual(a['probe_gain'],1.0);self.assertEqual(b['probe_gain'],0.5);self.assertEqual(c['probe_gain'],0.25)
        # Operational plant/sensing streams remain matched despite diagnostic gain changes.
        for key in ('x_true','x_primary','x_r1','x_r2','y','z','z_b','z_c'):
            self.assertEqual(a[key],b[key]);self.assertEqual(a[key],c[key])

    def test_probe_noise_is_pre_generated_and_fixed_scale(self):
        s=generate_experiment_016_stream(2002,'healthy',0.0,gain_override=0.0)
        for x in 'abc':
            for t in (1,181,205,260,1200):
                self.assertAlmostEqual(s[f'probe_obs_{x}'][t],SIGMA_PROBE*s[f'probe_noise_{x}'][t])

    def test_round_thresholds_positive(self):
        self.assertEqual(len(self.thresholds),4)
        self.assertTrue(all(x>0 for x in self.thresholds))

    def test_standard_gain_recovers_on_non_evaluation_seed(self):
        s=generate_experiment_016_stream(2003,'drift_ab_fault',0.5)
        groups,executed,stop,decisive=infer_sequential_groups(s,self.thresholds)
        self.assertTrue(partition_matches(groups))
        self.assertIn(stop,(2,3,4));self.assertEqual(decisive,1)
        self.assertEqual(set(executed),set(range(1,stop+1)))

    def test_early_stop_does_not_use_future_round(self):
        s=generate_experiment_016_stream(2004,'drift_ab_fault',0.5)
        g1,e1,stop1,d1=infer_sequential_groups(s,self.thresholds)
        if stop1<4:
            for blocks in (ROUND_BLOCKS[r] for r in range(stop1+1,5)):
                for ts in blocks.values():
                    for t in ts:
                        for x in 'abc':s[f'probe_obs_{x}'][t]+=1000000.0
            g2,e2,stop2,d2=infer_sequential_groups(s,self.thresholds)
            self.assertEqual(g1,g2);self.assertEqual(stop1,stop2);self.assertEqual(d1,d2);self.assertEqual(set(e1),set(e2))

    def test_energy_formula(self):
        self.assertAlmostEqual(probe_energy({1:None}),15*0.025**2)
        self.assertAlmostEqual(probe_energy({1:None,2:None,3:None}),15*(0.025**2+0.05**2+0.1**2))
        self.assertAlmostEqual(probe_energy({4:None}),15*0.2**2)

    def test_legacy_and_new_strategy_compatibility(self):
        tau=calibrate_tau();k=calibrate_kappa();k3=calibrate_kappa3();la=calibrate_lambda_anchor();lb,lab=calibrate_dual_anchor_thresholds();lc,lac,lbc=calibrate_anchor_c_thresholds()
        args=(2005,'drift_ab_fault',0.5)
        for st in ('frozen','health_persistence','triad_persistence','naive_three_anchor_quorum','oracle_provenance_quorum','max_probe_provenance_quorum','sequential_provenance_quorum'):
            rows=run_experiment_016_strategy(*args,st,tau,k,k3,la,lb,lc,lab,lac,lbc,self.thresholds)
            self.assertEqual(len(rows),900);self.assertIn('latent_input_sq_error',rows[-1]);self.assertIn('probe_energy',rows[-1])
            if st=='sequential_provenance_quorum':self.assertGreater(rows[-1]['probe_energy'],0)
            elif st=='max_probe_provenance_quorum':self.assertAlmostEqual(rows[-1]['probe_energy'],15*0.2**2)
            else:self.assertEqual(rows[-1]['probe_energy'],0)

if __name__=='__main__':unittest.main()
