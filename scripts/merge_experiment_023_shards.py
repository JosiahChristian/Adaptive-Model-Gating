#!/usr/bin/env python3
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from run_experiment_023 import CELLS,SEEDS,STRATEGIES,write_csv,report_from
SRC=ROOT/'results'/'experiment_023_shards';OUT=ROOT/'results'/'experiment_023'
EXPECTED_SUMMARIES=46*5*200
EXPECTED_AUDIT_ROWS=46*5*5*900

def readcsv(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def num(r):
 for k,v in list(r.items()):
  if k in {'label','kind','family','strategy','adapt_signature'}:continue
  try:r[k]=float(v)
  except:pass
 return r
def stream_audit(paths,out):
 fields=[]
 for p in paths:
  with p.open(encoding='utf-8',newline='') as f:
   rd=csv.DictReader(f)
   if rd.fieldnames is None:raise ValueError(f'Missing audit header {p}')
   for k in rd.fieldnames:
    if k not in fields:fields.append(k)
 out.parent.mkdir(parents=True,exist_ok=True);count=0
 with out.open('w',encoding='utf-8',newline='') as dst:
  w=csv.DictWriter(dst,fieldnames=fields);w.writeheader()
  for p in paths:
   shard=0
   with p.open(encoding='utf-8',newline='') as src:
    for row in csv.DictReader(src):w.writerow(row);count+=1;shard+=1
   if shard!=5*5*900:raise ValueError(f'Expected 22500 audit rows in {p}, got {shard}')
 return count

def main():
 summaries=[];audit=[]
 for c in CELLS:
  d=SRC/c['label'];summaries += [num(r) for r in readcsv(d/'seed_summary.csv')];audit.append(d/'audit.csv')
 if len(summaries)!=EXPECTED_SUMMARIES:raise ValueError(f'Expected {EXPECTED_SUMMARIES} summaries, got {len(summaries)}')
 for c in CELLS:
  q=[r for r in summaries if r['label']==c['label']]
  if len(q)!=5*200 or {int(r['seed']) for r in q}!=set(SEEDS) or {r['strategy'] for r in q}!=set(STRATEGIES):raise ValueError(f'Coverage mismatch {c["label"]}')
 OUT.mkdir(parents=True,exist_ok=True);write_csv(OUT/'seed_summary.csv',summaries)
 n=stream_audit(audit,OUT/'audit_trace_seeds_23000_23004.csv')
 if n!=EXPECTED_AUDIT_ROWS:raise ValueError(f'Expected {EXPECTED_AUDIT_ROWS} audit rows, got {n}')
 rep=report_from(summaries);(OUT/'report.json').write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps(rep,indent=2))
if __name__=='__main__':main()
