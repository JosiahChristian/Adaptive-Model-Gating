#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_029 import POSTERIOR_RISK_STRATEGY,TRIAD
from experiment_032 import COMPOSED_STRATEGY
from experiment_033 import run_experiment_033_strategy
from run_experiment_033 import CELLS,SEEDS,AUDIT,STRATEGIES,calibration_values,summary,write_csv

def main():
 label=os.environ['EXPERIMENT_033_LABEL'];c=next(x for x in CELLS if x['label']==label);vals=calibration_values();summaries=[]
 out=ROOT/'results'/'experiment_033_shards'/label;out.mkdir(parents=True,exist_ok=True);audit_path=out/'audit.jsonl'
 with audit_path.open('w',encoding='utf-8') as af:
  for seed in SEEDS:
   r29=run_experiment_033_strategy(seed,c,POSTERIOR_RISK_STRATEGY,vals)
   r33=run_experiment_033_strategy(seed,c,COMPOSED_STRATEGY,vals)
   rtri=run_experiment_033_strategy(seed,c,TRIAD,vals)
   summaries.extend((summary(r33,c,r29),summary(r29,c),summary(rtri,c)))
   if seed in AUDIT:
    for rows in (r33,r29,rtri):
     for r in rows:af.write(json.dumps(r,separators=(',',':'))+'\n')
 write_csv(out/'seed_summary.csv',summaries)
 (out/'metadata.json').write_text(json.dumps({'label':label,'summary_rows':len(summaries),'audit_seeds':sorted(AUDIT)},indent=2)+'\n')
 if len(summaries)!=1500:raise ValueError(len(summaries))
if __name__=='__main__':main()
