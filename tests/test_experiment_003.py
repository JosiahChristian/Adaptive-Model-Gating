import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from adaptive_model_gating import generate_gradual_drift_stream,BASELINE_A,EVENT_T
class GradualTests(unittest.TestCase):
 def test_ramp_endpoints(self):
  _,_,a=generate_gradual_drift_stream(1,.5,20)
  self.assertEqual(a[EVENT_T-1],BASELINE_A)
  self.assertAlmostEqual(a[EVENT_T],BASELINE_A+.5/20)
  self.assertAlmostEqual(a[EVENT_T+19],2.0)
  self.assertAlmostEqual(a[EVENT_T+100],2.0)
 def test_same_seed_same_noise_before_change(self):
  x1,y1,_=generate_gradual_drift_stream(9,.25,20); x2,y2,_=generate_gradual_drift_stream(9,1.0,200)
  for t in range(1,EVENT_T): self.assertEqual((x1[t],y1[t]),(x2[t],y2[t]))
if __name__=='__main__': unittest.main()
