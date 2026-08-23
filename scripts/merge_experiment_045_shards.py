#!/usr/bin/env python3
import argparse,csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_045 import CELLS
from run_experiment_045 import report_from,write_csv
def read_csv(p):
 with p.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input-root',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();root=Path(a.input_root);out=Path(a.out);out.mkdir(parents=True,exist_ok=True);summ=[];audit_count=0
 with (out/'audit.jsonl').open('w',encoding='utf-8') as dest:
  for i,c in enumerate(CELLS):
   d=root/f'cell-{i:02d}';summ.extend(read_csv(d/'summary.csv'))
   with (d/'audit.jsonl').open(encoding='utf-8') as src:
    for line in src:dest.write(line);audit_count+=1
 if len(summ)!=176000 or audit_count!=792000:raise AssertionError((len(summ),audit_count))
 write_csv(out/'summary.csv',summ);r=report_from(summ);r['summary_row_count']=len(summ);r['audit_row_count']=audit_count;(out/'report.json').write_text(json.dumps(r,indent=2,sort_keys=True));print(json.dumps({'hypotheses':r['hypotheses'],'summary_row_count':len(summ),'audit_row_count':audit_count},indent=2))
if __name__=='__main__':main()
