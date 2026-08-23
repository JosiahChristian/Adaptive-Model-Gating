#!/usr/bin/env python3
import argparse,csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_047 import CELLS
from run_experiment_047 import report_from,write_csv

def read_csv(path):
 with path.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input-root',required=True);ap.add_argument('--out',required=True);args=ap.parse_args()
 root=Path(args.input_root);out=Path(args.out);out.mkdir(parents=True,exist_ok=True);summ=[];audit_count=0
 with (out/'audit.jsonl').open('w',encoding='utf-8') as dest:
  for i,_ in enumerate(CELLS):
   d=root/f'cell-{i:02d}';summ.extend(read_csv(d/'summary.csv'))
   with (d/'audit.jsonl').open(encoding='utf-8') as src:
    for line in src:dest.write(line);audit_count+=1
 expected_summary=16*1000*10;expected_audit=16*5*10*600
 if len(summ)!=expected_summary or audit_count!=expected_audit:raise AssertionError((len(summ),audit_count,expected_summary,expected_audit))
 write_csv(out/'summary.csv',summ);report=report_from(summ);report['summary_row_count']=len(summ);report['audit_row_count']=audit_count
 (out/'report.json').write_text(json.dumps(report,indent=2,sort_keys=True))
 print(json.dumps({'hypotheses':report['hypotheses'],'summary_row_count':len(summ),'audit_row_count':audit_count},indent=2))

if __name__=='__main__':main()
