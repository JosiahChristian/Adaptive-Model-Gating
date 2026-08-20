#!/usr/bin/env python3
import csv,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_021 import run_experiment_021_strategy
from run_experiment_021 import STRATEGIES,SEEDS,AUDIT,calibrations,summary,write_csv
EXPECTED_SUMMARIES=17*200
EXPECTED_AUDIT_ROWS=17*5*900

def main():
 f=os.environ['EXPERIMENT_021_FAMILY'];m=float(os.environ['EXPERIMENT_021_MAGNITUDE']);label=os.environ['EXPERIMENT_021_LABEL']
 out=ROOT/'results'/'experiment_021_shards'/label;out.mkdir(parents=True,exist_ok=True)
 tmp=out/'audit.jsonl.tmp';fields=[];audit_count=0;summaries=[];vals=calibrations()
 with tmp.open('w',encoding='utf-8') as audit_tmp:
  for seed in SEEDS:
   for st in STRATEGIES:
    rows=run_experiment_021_strategy(seed,f,m,st,*vals);summaries.append(summary(rows,f,m))
    if seed in AUDIT:
     for r in rows:
      row=dict(r,family=f,magnitude=m)
      for k in row:
       if k not in fields:fields.append(k)
      audit_tmp.write(json.dumps(row,separators=(',',':'))+'\n');audit_count+=1
 if len(summaries)!=EXPECTED_SUMMARIES:raise ValueError(f'Expected {EXPECTED_SUMMARIES} summaries, got {len(summaries)}')
 if audit_count!=EXPECTED_AUDIT_ROWS:raise ValueError(f'Expected {EXPECTED_AUDIT_ROWS} audit rows, got {audit_count}')
 write_csv(out/'seed_summary.csv',summaries)
 with (out/'audit.csv').open('w',newline='',encoding='utf-8') as dst,tmp.open(encoding='utf-8') as src:
  writer=csv.DictWriter(dst,fieldnames=fields);writer.writeheader()
  for line in src:writer.writerow(json.loads(line))
 tmp.unlink()
 *v19,mu4e,nu4e=vals
 meta={'family':f,'magnitude':m,'mu_4_early':mu4e,'nu_4_early':nu4e,'early_calibration_seeds':[5000,5999],'evaluation_seeds':[21000,21199],'rows':len(summaries),'audit_rows':audit_count,'strategy_count':len(STRATEGIES)}
 (out/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
if __name__=='__main__':main()
