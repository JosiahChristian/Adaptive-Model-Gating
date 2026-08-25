#!/usr/bin/env python3
import argparse,csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from run_experiment_053 import CELLS,STRATEGIES,SEEDS,AUDIT,report_from,write_csv

def validate_audit(paths):
 expected={(c['label'],int(seed),st) for c in CELLS for seed in AUDIT for st in STRATEGIES};groups={};count=0
 for path in paths:
  with path.open(encoding='utf-8') as f:
   for line in f:
    if not line.strip():continue
    r=json.loads(line);count+=1;label=str(r.get('experiment053_cell',''));seed=int(r['seed']);st=str(r['strategy']);key=(label,seed,st)
    if key not in expected:raise AssertionError(('unexpected_audit_group',key))
    t=int(r['t'])
    if t<1:raise AssertionError(('invalid_t',key,t))
    g=groups.setdefault(key,{'n':0,'seen':set(),'max':0});g['n']+=1
    if t in g['seen']:raise AssertionError(('duplicate_audit_t',key,t))
    g['seen'].add(t);g['max']=max(g['max'],t)
 if set(groups)!=expected:raise AssertionError(('audit_groups',len(groups),len(expected)))
 for key,g in groups.items():
  if g['n']!=g['max'] or len(g['seen'])!=g['max'] or min(g['seen'])!=1:raise AssertionError(('noncontiguous_audit_t',key,g['n'],g['max']))
 return count

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input-root',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();root=Path(a.input_root);out=Path(a.out);out.mkdir(parents=True,exist_ok=True);rows=[];audit_paths=[]
 for i,c in enumerate(CELLS):
  d=root/f'cell-{i:02d}';p=d/'summary.csv'
  if not p.exists():raise FileNotFoundError(p)
  with p.open(newline='',encoding='utf-8') as f:part=list(csv.DictReader(f))
  expected=len(SEEDS)*len(STRATEGIES)
  if len(part)!=expected:raise AssertionError((i,len(part),expected))
  rows.extend(part);apath=d/'audit.jsonl'
  if not apath.exists():raise FileNotFoundError(apath)
  audit_paths.append(apath)
 if len(rows)!=len(CELLS)*len(SEEDS)*len(STRATEGIES):raise AssertionError(('summary',len(rows)))
 audit_count=validate_audit(audit_paths);write_csv(out/'summary.csv',rows)
 with (out/'audit.jsonl').open('w',encoding='utf-8') as dst:
  for p in audit_paths:
   with p.open(encoding='utf-8') as src:
    for line in src:
     if line.strip():dst.write(line if line.endswith('\n') else line+'\n')
 report=report_from(rows);report['summary_row_count']=len(rows);report['audit_row_count']=audit_count;(out/'report.json').write_text(json.dumps(report,indent=2,sort_keys=True),encoding='utf-8')
 print(json.dumps({'summary_rows':len(rows),'audit_rows':audit_count,'hypotheses':report['hypotheses'],'mean_primary_coverage':report['mean_primary_coverage'],'stress_panel':report['stress_panel']},indent=2))
if __name__=='__main__':main()
