#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_029 import POSTERIOR_RISK_STRATEGY,TRIAD,ACCEPT_THRESHOLD
from experiment_032 import COMPOSED_STRATEGY
from experiment_033 import run_experiment_033_strategy
from run_experiment_033 import CELLS,calibration_values

assert abs(ACCEPT_THRESHOLD-.99)<1e-12
vals=calibration_values();seed=33999
labels=('gn_g0.475_n1.10','tn_m35_n1.50','an_0.75_1.25_n1.50','mixed_cm0.50_n1.25','common_mode_0.75')
for label in labels:
 c=next(x for x in CELLS if x['label']==label)
 r29=run_experiment_033_strategy(seed,c,POSTERIOR_RISK_STRATEGY,vals);r33=run_experiment_033_strategy(seed,c,COMPOSED_STRATEGY,vals);rt=run_experiment_033_strategy(seed,c,TRIAD,vals)
 assert len(r29)==900 and len(r33)==900 and len(rt)==900
 a,b=r33[0],r29[0]
 for k in ('provenance_accepted','provenance_abstain','probe_stop_round','probe_energy','posterior_deploy_hypothesis'):
  assert a.get(k,'')==b.get(k,''),(label,k,a.get(k),b.get(k))
 if a.get('posterior_at_deployment','')!='':assert abs(float(a['posterior_at_deployment'])-float(b['posterior_at_deployment']))<1e-12
 for r in r33:
  removed=int(r.get('context_removed_suspect_veto',0))
  if removed:
   assert int(r.get('context_vote_t',0))==1
   assert int(r.get('provenance_suspect_original',0))==1
   assert int(r.get('provenance_suspect_effective',1))==0
   assert int(r.get('triad_primary_bad',0))==0
   assert int(r.get('adapt',0))==1
  assert not (int(r.get('adapt',0)) and int(r.get('triad_primary_bad',0)))
print('experiment033 smoke passed')
