#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_014 import run_experiment_014_strategy
from run_experiment_014 import STRATEGIES,SEEDS,AUDIT,calibrations,summary,write_csv
def main():
 f=os.environ['EXPERIMENT_014_FAMILY'];m=float(os.environ['EXPERIMENT_014_MAGNITUDE']);label=os.environ['EXPERIMENT_014_LABEL'];vals=calibrations();summaries=[];audit=[]
 for seed in SEEDS:
  for st in STRATEGIES:
   rows=run_experiment_014_strategy(seed,f,m,st,*vals);summaries.append(summary(rows,f,m))
   if seed in AUDIT:audit.extend(dict(r,family=f,magnitude=m) for r in rows)
 out=ROOT/'results'/'experiment_014_shards'/label;write_csv(out/'seed_summary.csv',summaries);write_csv(out/'audit.csv',audit)
 keys=('tau','kappa','kappa3','lambda_anchor_a','lambda_anchor_b','lambda_anchor_c','lambda_anchor_ab','lambda_anchor_ac','lambda_anchor_bc','lambda_dep');meta=dict(zip(keys,vals));meta.update({'family':f,'magnitude':m,'rho_sig':.35,'dependence_calibration_seeds':[1400,1599],'evaluation_seeds':[14000,14199],'rows':len(summaries)});(out/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
if __name__=='__main__':main()
