#!/usr/bin/env python3
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_022 import CELLS,STRATEGIES
from run_experiment_022 import SEEDS,write_csv,report_from
SRC=ROOT/'results'/'experiment_022_shards';OUT=ROOT/'results'/'experiment_022'
EXPECTED_SUMMARIES=76*4*200;EXPECTED_AUDIT_ROWS=76*4*5*900

def readcsv(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def num(r):
 for k,v in list(r.items()):
  if k in {'cell','kind','family','strategy','adapt_signature','gate_signature'}:continue
  try:r[k]=float(v)
  except:pass
 return r
def stream_audit(paths,out):
 fields=[]
 for p in paths:
  with p.open(encoding='utf-8',newline='') as f:
   rd=csv.DictReader(f)
   if rd.fieldnames is None:raise ValueError(f'Missing audit header: {p}')
   for k in rd.fieldnames:
    if k not in fields:fields.append(k)
 out.parent.mkdir(parents=True,exist_ok=True);count=0
 with out.open('w',encoding='utf-8',newline='') as dst:
  w=csv.DictWriter(dst,fieldnames=fields);w.writeheader()
  for p in paths:
   shard=0
   with p.open(encoding='utf-8',newline='') as src:
    for row in csv.DictReader(src):w.writerow(row);count+=1;shard+=1
   if shard!=4*5*900:raise ValueError(f'Expected 18000 audit rows in {p}, got {shard}')
 return count

def main():
 summaries=[];audit_paths=[];metas=[]
 for c in CELLS:
  d=SRC/c['label'];summaries += [num(r) for r in readcsv(d/'seed_summary.csv')];audit_paths.append(d/'audit.csv');metas.append(json.loads((d/'metadata.json').read_text()))
 if len(summaries)!=EXPECTED_SUMMARIES:raise ValueError(f'Expected {EXPECTED_SUMMARIES} summaries, got {len(summaries)}')
 for c in CELLS:
  q=[r for r in summaries if r['cell']==c['label']]
  if len(q)!=4*200 or {int(float(r['seed'])) for r in q}!=set(SEEDS) or {r['strategy'] for r in q}!=set(STRATEGIES):raise ValueError(f'Coverage mismatch {c["label"]}')
 for m,c in zip(metas,CELLS):
  if m['cell']!=c or m['evaluation_seeds']!=[22000,22199] or not m['no_recalibration']:raise ValueError(f'Metadata mismatch {c["label"]}')
 OUT.mkdir(parents=True,exist_ok=True);write_csv(OUT/'seed_summary.csv',summaries)
 n=stream_audit(audit_paths,OUT/'audit_trace_seeds_22000_22004.csv')
 if n!=EXPECTED_AUDIT_ROWS:raise ValueError(f'Expected {EXPECTED_AUDIT_ROWS} audit rows, got {n}')
 rep=report_from(summaries);(OUT/'report.json').write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps(rep['hypotheses'],indent=2))
if __name__=='__main__':main()
