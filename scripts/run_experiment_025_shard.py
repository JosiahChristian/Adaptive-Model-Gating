#!/usr/bin/env python3
import csv,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from run_experiment_025 import CELLS,STRATEGIES,SEEDS,AUDIT,summary,write_csv,calibrations
from experiment_025 import run_experiment_025_strategy
EXPECTED_SUMMARIES=5*200;EXPECTED_AUDIT_ROWS=5*5*900

def main():
 label=os.environ['EXPERIMENT_025_LABEL'];c=next(x for x in CELLS if x['label']==label);out=ROOT/'results'/'experiment_025_shards'/label;out.mkdir(parents=True,exist_ok=True);tmp=out/'audit.jsonl.tmp';fields=[];audit_count=0;summaries=[];vals=calibrations()
 with tmp.open('w',encoding='utf-8') as f:
  for seed in SEEDS:
   for st in STRATEGIES:
    rows=run_experiment_025_strategy(seed,c,st,vals);summaries.append(summary(rows,c))
    if seed in AUDIT:
     for r in rows:
      row=dict(r,experiment025_label=label)
      for k in row:
       if k not in fields:fields.append(k)
      f.write(json.dumps(row,separators=(',',':'))+'\n');audit_count+=1
 if len(summaries)!=EXPECTED_SUMMARIES:raise ValueError(len(summaries))
 if audit_count!=EXPECTED_AUDIT_ROWS:raise ValueError(audit_count)
 write_csv(out/'seed_summary.csv',summaries)
 with (out/'audit.csv').open('w',newline='',encoding='utf-8') as dst,tmp.open(encoding='utf-8') as src:
  w=csv.DictWriter(dst,fieldnames=fields);w.writeheader()
  for line in src:w.writerow(json.loads(line))
 tmp.unlink();(out/'metadata.json').write_text(json.dumps({'label':label,'rows':len(summaries),'audit_rows':audit_count,'evaluation_seeds':[25000,25199]},indent=2)+'\n')
if __name__=='__main__':main()
