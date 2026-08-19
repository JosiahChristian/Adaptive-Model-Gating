#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from adaptive_model_gating import calibrate_tau
from experiment_008 import calibrate_kappa
from experiment_010 import calibrate_kappa3
from experiment_011 import calibrate_lambda_anchor
from experiment_012 import calibrate_dual_anchor_thresholds
from experiment_013 import calibrate_anchor_c_thresholds,run_experiment_013_strategy
from run_experiment_013 import STRATEGIES,summary

def main():
 tau=calibrate_tau();k=calibrate_kappa();k3=calibrate_kappa3();la=calibrate_lambda_anchor();lb,lab=calibrate_dual_anchor_thresholds();lc,lac,lbc=calibrate_anchor_c_thresholds()
 # Non-evaluation seed: execution compatibility only, not scientific evidence.
 for strategy in STRATEGIES:
  rows=run_experiment_013_strategy(42,'healthy',0.0,strategy,tau,k,k3,la,lb,lc,lab,lac,lbc)
  if len(rows)!=900: raise ValueError(f'{strategy}: expected 900 rows, got {len(rows)}')
  s=summary(rows,'healthy',0.0)
  for key in ('operational_loss_401_600','latent_input_loss_401_600','final_slope_error_abs'):
   if key not in s: raise ValueError(f'{strategy}: missing summary field {key}')
 print('Experiment 013 execution smoke passed')
if __name__=='__main__':main()
