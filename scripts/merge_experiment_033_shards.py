#!/usr/bin/env python3
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from run_experiment_033 import CELLS,report_from,calibration_values,write_csv

def main():
 base=ROOT/'results'/'experiment_033_shards';rows=[]
 for c in CELLS:
  p=base/c['label']/'seed_summary.csv'
  if not p.exists():raise FileNotFoundError(p)
  with p.open(newline='',encoding='utf-8') as f:rows.extend(csv.DictReader(f))
 if len(rows)!=45000:raise ValueError(f'expected 45000 summaries, got {len(rows)}')
 out=ROOT/'results'/'experiment_033';out.mkdir(parents=True,exist_ok=True);write_csv(out/'seed_summary.csv',rows)
 audit_count=0
 with (out/'audit.jsonl').open('w',encoding='utf-8') as dst:
  for c in CELLS:
   p=base/c['label']/'audit.jsonl'
   if not p.exists():raise FileNotFoundError(p)
   with p.open(encoding='utf-8') as src:
    for line in src:
     if line.strip():dst.write(line);audit_count+=1
 if audit_count!=405000:raise ValueError(f'expected 405000 audit rows, got {audit_count}')
 report=report_from(rows,calibration_values());report['summary_row_count']=len(rows);report['audit_row_count']=audit_count
 (out/'report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'hypotheses':report['hypotheses'],'summary_rows':len(rows),'audit_rows':audit_count},indent=2))
if __name__=='__main__':main()
