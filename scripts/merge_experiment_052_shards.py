#!/usr/bin/env python3
import argparse,csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from run_experiment_052 import CELLS,STRATEGIES,SEEDS,AUDIT,report_from,write_csv

EXPECTED_AUDIT={(c['label'],int(seed),st) for c in CELLS for seed in AUDIT for st in STRATEGIES}

def merge_and_validate_audit(paths,outpath):
 groups={}
 count=0
 with outpath.open('w',encoding='utf-8') as dst:
  for path in paths:
   if not path.exists():raise FileNotFoundError(path)
   with path.open(encoding='utf-8') as src:
    for line in src:
     if not line.strip():continue
     r=json.loads(line)
     key=(str(r.get('experiment051_cell','')),int(r['seed']),str(r['strategy']))
     if key not in EXPECTED_AUDIT:raise AssertionError(('unexpected_audit_group',key))
     t=int(r['t'])
     if t<1:raise AssertionError(('invalid_t',key,t))
     mask,max_t,n=groups.get(key,(0,0,0));bit=1<<t
     if mask&bit:raise AssertionError(('duplicate_audit_t',key,t))
     groups[key]=(mask|bit,max(max_t,t),n+1)
     dst.write(line if line.endswith('\n') else line+'\n');count+=1
 if set(groups)!=EXPECTED_AUDIT:raise AssertionError(('audit_groups',len(groups),len(EXPECTED_AUDIT)))
 for key,(mask,max_t,n) in groups.items():
  expected_mask=(1<<(max_t+1))-2
  if n!=max_t or mask!=expected_mask:raise AssertionError(('noncontiguous_audit_t',key,n,max_t))
 return count

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input-root',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();root=Path(a.input_root);out=Path(a.out);out.mkdir(parents=True,exist_ok=True);rows=[];audit_paths=[]
 for i,c in enumerate(CELLS):
  d=root/f'cell-{i:02d}';p=d/'summary.csv'
  if not p.exists():raise FileNotFoundError(p)
  with p.open(newline='',encoding='utf-8') as f:part=list(csv.DictReader(f))
  expected=len(SEEDS)*len(STRATEGIES)
  if len(part)!=expected:raise AssertionError((i,len(part),expected))
  rows.extend(part);audit_paths.append(d/'audit.jsonl')
 if len(rows)!=len(CELLS)*len(SEEDS)*len(STRATEGIES):raise AssertionError(('summary',len(rows)))
 write_csv(out/'summary.csv',rows)
 audit_count=merge_and_validate_audit(audit_paths,out/'audit.jsonl')
 report=report_from(rows);report['summary_row_count']=len(rows);report['audit_row_count']=audit_count;(out/'report.json').write_text(json.dumps(report,indent=2,sort_keys=True),encoding='utf-8')
 print(json.dumps({'summary_rows':len(rows),'audit_rows':audit_count,'hypotheses':report['hypotheses'],'mean_primary_coverage':report['mean_primary_coverage'],'stress_panel':report['stress_panel']},indent=2))
if __name__=='__main__':main()
