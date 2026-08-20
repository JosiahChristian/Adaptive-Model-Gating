#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_020 import EARLY_STRATEGY,run_experiment_020_strategy
from run_experiment_020 import calibrations

def main():
 vals=calibrations()
 for seed,f,m in ((20998,'drift_ab_fault',0.5),(20999,'drift_ab_gain050',0.5),(21000,'drift_ab_gain0125',0.5),(21001,'healthy',0.0)):
  rows=run_experiment_020_strategy(seed,f,m,EARLY_STRATEGY,*vals)
  if len(rows)!=900:raise RuntimeError(f'{f}: expected 900 rows, got {len(rows)}')
  r0=rows[0]
  if float(r0['probe_energy'])<0 or float(r0['probe_energy'])>1.196875+1e-12:raise RuntimeError(f'{f}: invalid energy {r0["probe_energy"]}')
  if int(r0['provenance_accepted'])+int(r0['provenance_abstain'])!=1:raise RuntimeError(f'{f}: invalid terminal provenance state')
 print('Experiment 020 smoke passed')
if __name__=='__main__':main()
