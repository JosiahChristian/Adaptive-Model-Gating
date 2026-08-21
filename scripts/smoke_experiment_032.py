#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_029 import POSTERIOR_RISK_STRATEGY,ACCEPT_THRESHOLD
from experiment_032 import COMPOSED_STRATEGY,run_experiment_032_strategy
from run_experiment_032 import calibration_values,cell

assert abs(ACCEPT_THRESHOLD-.99)<1e-12
vals=calibration_values();seed=33999
cells=(
 cell('smoke_supported','noise','drift_ab_fault',.50,gain=.50,noise_scale=1.0),
 cell('smoke_common','control','common_mode',.50),
 cell('smoke_primary','control','primary_fault',.50),
 cell('smoke_healthy','control','healthy',0.0),
)
for c in cells:
 r29=run_experiment_032_strategy(seed,c,POSTERIOR_RISK_STRATEGY,vals);r32=run_experiment_032_strategy(seed,c,COMPOSED_STRATEGY,vals)
 assert len(r29)==900 and len(r32)==900
 a,b=r32[0],r29[0]
 for k in ('provenance_accepted','provenance_abstain','probe_stop_round','probe_energy','posterior_deploy_hypothesis'):
  assert a.get(k,'')==b.get(k,''),(c['label'],k,a.get(k),b.get(k))
 if a.get('posterior_at_deployment','')!='':assert abs(float(a['posterior_at_deployment'])-float(b['posterior_at_deployment']))<1e-12
 by={int(r['t']):r for r in r29}
 for r in r32:
  t=int(r['t']);old=by[t]
  if int(r.get('adapt',0))!=int(old.get('adapt',0)):assert int(r.get('context_vote_t',0))==1
  assert not (int(r.get('adapt',0)) and int(r.get('triad_primary_bad',0)))
  v=int(r.get('context_vote_t',0));assert v in (0,1)
print('experiment032 smoke passed')
