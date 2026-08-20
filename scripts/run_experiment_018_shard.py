#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_018 import run_experiment_018_strategy
from run_experiment_018 import STRATEGIES,SEEDS,AUDIT,calibrations,summary,write_csv

def main():
 f=os.environ['EXPERIMENT_018_FAMILY'];m=float(os.environ['EXPERIMENT_018_MAGNITUDE']);label=os.environ['EXPERIMENT_018_LABEL'];vals=calibrations();summaries=[];audit=[]
 for seed in SEEDS:
  for st in STRATEGIES:
   rows=run_experiment_018_strategy(seed,f,m,st,*vals);summaries.append(summary(rows,f,m))
   if seed in AUDIT:audit.extend(dict(r,family=f,magnitude=m) for r in rows)
 out=ROOT/'results'/'experiment_018_shards'/label;write_csv(out/'seed_summary.csv',summaries);write_csv(out/'audit.csv',audit)
 tau,k,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5=vals
 meta={'family':f,'magnitude':m,'tau':tau,'kappa':k,'kappa3':k3,'lambda_anchor_a':la,'lambda_anchor_b':lb,'lambda_anchor_c':lc,'lambda_anchor_ab':lab,'lambda_anchor_ac':lac,'lambda_anchor_bc':lbc,'lambda_probe_rounds':list(lambdas),'mu_cumulative_rounds':list(mu),'nu_cumulative_rounds':list(nu),'mu_5':mu5,'nu_5':nu5,'evaluation_seeds':[18000,18199],'rows':len(summaries)}
 (out/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
if __name__=='__main__':main()
