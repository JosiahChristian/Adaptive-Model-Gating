#!/usr/bin/env python3
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_034 import CELLS
from run_experiment_034 import report_from,calibration_values,write_csv

def main():
 base=ROOT/'results'/'experiment_034_shards';rows=[];audit_count=0
 for c in CELLS:
  p=base/c['label']/'summary.csv'
  with p.open(newline='',encoding='utf-8') as f:rows.extend(csv.DictReader(f))
  a=base/c['label']/'audit.jsonl'
  with a.open(encoding='utf-8') as f:
   for _ in f:audit_count+=1
 if len(rows)!=27000:raise AssertionError(f'summary rows {len(rows)}')
 if audit_count!=243000:raise AssertionError(f'audit rows {audit_count}')
 report=report_from(rows,calibration_values());report['summary_row_count']=len(rows);report['audit_row_count']=audit_count
 out=ROOT/'results'/'experiment_034';out.mkdir(parents=True,exist_ok=True)
 (out/'report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
 write_csv(out/'summary.csv',rows)
 # Stream-merge audit without loading it into memory.
 with (out/'audit.jsonl').open('w',encoding='utf-8') as dst:
  for c in CELLS:
   with (base/c['label']/'audit.jsonl').open(encoding='utf-8') as src:
    for line in src:dst.write(line)
 print(json.dumps({'summary_rows':len(rows),'audit_rows':audit_count,'hypotheses':report['hypotheses']},sort_keys=True))
if __name__=='__main__':main()
