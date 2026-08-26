#!/usr/bin/env python3
import argparse,csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from run_experiment_059 import CELLS,STRATEGIES,SEEDS,AUDIT,report_from,write_csv

def validate_audit(paths):
 expected={(c['label'],int(seed),st) for c in CELLS for seed in AUDIT for st in STRATEGIES};groups={};row_count=0;reference_interval=None
 for p in paths:
  with p.open(encoding='utf-8') as f:
   for line in f:
    if not line.strip():continue
    r=json.loads(line);row_count+=1;key=(str(r.get('experiment059_cell','')),int(r['seed']),str(r['strategy']))
    if key not in expected:raise AssertionError(('unexpected_audit_group',key))
    t=int(r['t']);groups.setdefault(key,[]).append(t)
 if set(groups)!=expected:raise AssertionError(('audit_groups',len(groups),len(expected)))
 for key,ts in groups.items():
  if len(ts)!=len(set(ts)):raise AssertionError(('duplicate_audit_t',key))
  ordered=sorted(ts);interval=(ordered[0],ordered[-1],len(ordered))
  if ordered!=list(range(ordered[0],ordered[-1]+1)):raise AssertionError(('noncontiguous_audit_t',key,interval))
  if reference_interval is None:reference_interval=interval
  elif interval!=reference_interval:raise AssertionError(('audit_interval_mismatch',key,interval,reference_interval))
 return row_count,reference_interval

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input-root',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();root=Path(a.input_root);out=Path(a.out);out.mkdir(parents=True,exist_ok=True);rows=[];audit_paths=[]
 for i,c in enumerate(CELLS):
  d=root/f'cell-{i:02d}';p=d/'summary.csv';apath=d/'audit.jsonl'
  if not p.exists() or not apath.exists():raise FileNotFoundError((p,apath))
  with p.open(newline='',encoding='utf-8') as f:part=list(csv.DictReader(f))
  expected=len(SEEDS)*len(STRATEGIES)
  if len(part)!=expected:raise AssertionError((i,len(part),expected))
  rows.extend(part);audit_paths.append(apath)
 if len(rows)!=len(CELLS)*len(SEEDS)*len(STRATEGIES):raise AssertionError(('summary',len(rows)))
 audit_count,interval=validate_audit(audit_paths);write_csv(out/'summary.csv',rows)
 with (out/'audit.jsonl').open('w',encoding='utf-8') as dest:
  for p in audit_paths:
   with p.open(encoding='utf-8') as src:
    for line in src:
     if line.strip():dest.write(line if line.endswith('\n') else line+'\n')
 report=report_from(rows);report['summary_row_count']=len(rows);report['audit_row_count']=audit_count;report['audit_time_interval']=interval;(out/'report.json').write_text(json.dumps(report,indent=2,sort_keys=True),encoding='utf-8')
 print(json.dumps({'summary_rows':len(rows),'audit_rows':audit_count,'audit_interval':interval,'hypotheses':report['hypotheses'],'mean_primary_coverage':report['mean_primary_coverage']},indent=2))
if __name__=='__main__':main()
