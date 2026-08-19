#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from adaptive_model_gating import calibrate_tau
from experiment_008 import calibrate_kappa
from experiment_010 import calibrate_kappa3
from experiment_011 import calibrate_lambda_anchor
from experiment_012 import calibrate_dual_anchor_thresholds
from experiment_013 import calibrate_anchor_c_thresholds,run_experiment_013_strategy
from run_experiment_013 import STRATEGIES,SEEDS,AUDIT,summary,write_csv
def main():
 f=os.environ['EXPERIMENT_013_FAMILY'];m=float(os.environ['EXPERIMENT_013_MAGNITUDE']);label=os.environ['EXPERIMENT_013_LABEL'];tau=calibrate_tau();k=calibrate_kappa();k3=calibrate_kappa3();la=calibrate_lambda_anchor();lb,lab=calibrate_dual_anchor_thresholds();lc,lac,lbc=calibrate_anchor_c_thresholds();summaries=[];audit=[]
 for seed in SEEDS:
  for st in STRATEGIES:
   rows=run_experiment_013_strategy(seed,f,m,st,tau,k,k3,la,lb,lc,lab,lac,lbc);summaries.append(summary(rows,f,m))
   if seed in AUDIT:audit.extend(dict(r,family=f,magnitude=m) for r in rows)
 out=ROOT/'results'/'experiment_013_shards'/label;write_csv(out/'seed_summary.csv',summaries);write_csv(out/'audit.csv',audit);(out/'metadata.json').write_text(json.dumps({'family':f,'magnitude':m,'tau':tau,'kappa':k,'kappa3':k3,'lambda_anchor_a':la,'lambda_anchor_b':lb,'lambda_anchor_ab':lab,'lambda_anchor_c':lc,'lambda_anchor_ac':lac,'lambda_anchor_bc':lbc,'evaluation_seeds':[13000,13199],'rows':len(summaries)},indent=2)+'\n')
if __name__=='__main__':main()
