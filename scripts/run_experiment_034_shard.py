#!/usr/bin/env python3
import csv,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_029 import POSTERIOR_RISK_STRATEGY
from experiment_034 import CELLS,STRATEGIES,run_experiment_034_strategy
from run_experiment_034 import SEEDS,AUDIT,summary,calibration_values

def main():
 label=os.environ['EXPERIMENT_034_LABEL'];c=next(x for x in CELLS if x['label']==label);vals=calibration_values();out=ROOT/'results'/'experiment_034_shards'/label;out.mkdir(parents=True,exist_ok=True)
 summaries=[];audit=out/'audit.jsonl'
 with audit.open('w',encoding='utf-8') as af:
  for seed in SEEDS:
   per={}
   for st in STRATEGIES:per[st]=run_experiment_034_strategy(seed,c,st,vals)
   for st in STRATEGIES:
    summaries.append(summary(per[st],c,per[POSTERIOR_RISK_STRATEGY] if st!=POSTERIOR_RISK_STRATEGY else None))
    if seed in AUDIT:
     for r in per[st]:af.write(json.dumps(r,separators=(',',':'))+'\n')
 fields=[]
 for r in summaries:
  for k in r:
   if k not in fields:fields.append(k)
 with (out/'summary.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(summaries)
 if len(summaries)!=500*3:raise AssertionError(len(summaries))
 print(json.dumps({'label':label,'summary_rows':len(summaries),'audit_rows':5*3*900}))
if __name__=='__main__':main()
