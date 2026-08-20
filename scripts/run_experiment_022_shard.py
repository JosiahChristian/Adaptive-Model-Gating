#!/usr/bin/env python3
import csv,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_022 import CELLS,STRATEGIES,run_experiment_022_strategy
from run_experiment_022 import SEEDS,AUDIT,calibrations,summary,write_csv
EXPECTED_SUMMARIES=4*200;EXPECTED_AUDIT_ROWS=4*5*900

def main():
 label=os.environ['EXPERIMENT_022_LABEL'];matches=[c for c in CELLS if c['label']==label]
 if len(matches)!=1:raise ValueError(f'unknown/duplicate cell {label}')
 c=matches[0];out=ROOT/'results'/'experiment_022_shards'/label;out.mkdir(parents=True,exist_ok=True)
 tmp=out/'audit.jsonl.tmp';fields=[];audit_count=0;summaries=[];vals=calibrations()
 with tmp.open('w',encoding='utf-8') as audit_tmp:
  for seed in SEEDS:
   for st in STRATEGIES:
    rows=run_experiment_022_strategy(seed,c,st,vals);summaries.append(summary(rows,c))
    if seed in AUDIT:
     for r in rows:
      row=dict(r,cell=c['label'],kind=c['kind'])
      for k in row:
       if k not in fields:fields.append(k)
      audit_tmp.write(json.dumps(row,separators=(',',':'))+'\n');audit_count+=1
 if len(summaries)!=EXPECTED_SUMMARIES:raise ValueError(f'Expected {EXPECTED_SUMMARIES} summaries, got {len(summaries)}')
 if audit_count!=EXPECTED_AUDIT_ROWS:raise ValueError(f'Expected {EXPECTED_AUDIT_ROWS} audit rows, got {audit_count}')
 write_csv(out/'seed_summary.csv',summaries)
 with (out/'audit.csv').open('w',newline='',encoding='utf-8') as dst,tmp.open(encoding='utf-8') as src:
  w=csv.DictWriter(dst,fieldnames=fields);w.writeheader()
  for line in src:w.writerow(json.loads(line))
 tmp.unlink()
 (out/'metadata.json').write_text(json.dumps({'cell':c,'evaluation_seeds':[22000,22199],'strategies':list(STRATEGIES),'rows':len(summaries),'audit_rows':audit_count,'no_recalibration':True},indent=2)+'\n')
if __name__=='__main__':main()
