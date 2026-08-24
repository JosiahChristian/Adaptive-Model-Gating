#!/usr/bin/env python3
import argparse,csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_051 import CELLS,STRATEGIES
from run_experiment_051 import SEEDS,AUDIT,report_from,write_csv

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input-root',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();root=Path(a.input_root);out=Path(a.out);out.mkdir(parents=True,exist_ok=True);rows=[];audit=[]
 for i,c in enumerate(CELLS):
  d=root/f'cell-{i:02d}';p=d/'summary.csv'
  if not p.exists():raise FileNotFoundError(p)
  with p.open(newline='',encoding='utf-8') as f:part=list(csv.DictReader(f))
  expected=len(SEEDS)*len(STRATEGIES)
  if len(part)!=expected:raise AssertionError((i,len(part),expected))
  rows.extend(part)
  apath=d/'audit.jsonl'
  if not apath.exists():raise FileNotFoundError(apath)
  audit.extend(x for x in apath.read_text(encoding='utf-8').splitlines() if x.strip())
 expected_summary=len(CELLS)*len(SEEDS)*len(STRATEGIES);expected_audit=len(CELLS)*len(AUDIT)*len(STRATEGIES)*600
 if len(rows)!=expected_summary:raise AssertionError(('summary',len(rows),expected_summary))
 if len(audit)!=expected_audit:raise AssertionError(('audit',len(audit),expected_audit))
 write_csv(out/'summary.csv',rows);(out/'audit.jsonl').write_text('\n'.join(audit)+'\n',encoding='utf-8');report=report_from(rows);report['summary_row_count']=len(rows);report['audit_row_count']=len(audit);(out/'report.json').write_text(json.dumps(report,indent=2,sort_keys=True),encoding='utf-8')
 print(json.dumps({'summary_rows':len(rows),'audit_rows':len(audit),'hypotheses':report['hypotheses'],'mean_primary_coverage':report['mean_primary_coverage'],'stress_panel':report['stress_panel']},indent=2))
if __name__=='__main__':main()
