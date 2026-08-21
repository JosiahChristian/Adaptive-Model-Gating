#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from adaptive_model_gating import EVENT_T
from experiment_011 import BETA_ANCHOR
from experiment_016 import ROUND_AMPLITUDES,ROUND_BLOCKS,SIGMA_PROBE
from experiment_034 import CELLS,STRATEGIES,GROUPS,PAIR,generate_experiment_034_stream,run_experiment_034_strategy
from run_experiment_034 import calibration_values

assert len(CELLS)==18
seed=33999
for topology in ('H_ac','H_bc'):
 c=next(x for x in CELLS if x['topology']==topology and x['label'].endswith('g0.500_n1.00'))
 s=generate_experiment_034_stream(seed,c);groups=GROUPS[topology];amp=ROUND_AMPLITUDES[0];gain=float(s['probe_gain'])
 # Exact signal after removing stored probe noise must follow the permuted grouping.
 for target,ts in ROUND_BLOCKS[1].items():
  t=next(iter(ts))
  for x in 'abc':
   signal=s[f'probe_obs_{x}'][t]-SIGMA_PROBE*s[f'probe_noise_{x}'][t]
   expected=gain*amp if groups[x]==groups[target] else 0.0
   assert abs(signal-expected)<1e-12,(topology,target,x,signal,expected)
 # At event onset, the inherited coherent draw must occupy exactly the topology pair.
 q=BETA_ANCHOR*.50*s['ab_fault_unit_noise'][EVENT_T]
 xt=s['x_true'][EVENT_T]
 # Remove nominal anchor component/noise to compare event extras pairwise.
 from experiment_011 import SIGMA_ANCHOR
 extras={
  'a':s['z'][EVENT_T]-(BETA_ANCHOR*xt+SIGMA_ANCHOR*s['anchor_unit_noise'][EVENT_T]),
  'b':s['z_b'][EVENT_T]-(BETA_ANCHOR*xt+SIGMA_ANCHOR*s['anchor_b_unit_noise'][EVENT_T]),
  'c':s['z_c'][EVENT_T]-(BETA_ANCHOR*xt+SIGMA_ANCHOR*s['anchor_c_unit_noise'][EVENT_T]),
 }
 for x in 'abc':assert abs(extras[x]-(q if x in PAIR[topology] else 0.0))<1e-10,(topology,x,extras[x],q)

vals=calibration_values()
representative=[
 next(x for x in CELLS if x['label']=='ac_g0.500_n1.00'),
 next(x for x in CELLS if x['label']=='bc_g0.500_n1.50'),
 next(x for x in CELLS if x['label']=='ac_timing_p35_n1.50'),
 next(x for x in CELLS if x['label']=='bc_common_mode_1.00'),
]
for c in representative:
 for st in STRATEGIES:
  rows=run_experiment_034_strategy(seed,c,st,vals)
  assert len(rows)==900,(c['label'],st,len(rows))
  assert all(r['experiment034_topology_truth']==c['topology'] for r in rows)
print('Experiment 034 structural smoke passed')
