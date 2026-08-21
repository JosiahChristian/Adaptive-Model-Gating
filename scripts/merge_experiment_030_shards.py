#!/usr/bin/env python3
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from run_experiment_030 import CELLS,SEEDS,STRATEGIES,write_csv,report_from
SRC=ROOT/'results'/'experiment_030_shards';OUT=ROOT/'results'/'experiment_030';EXPECTED_SUMMARIES=7*2*1000;EXPECTED_AUDIT_ROWS=7*2*5*900

def readcsv(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def num(r):
 for k,v in list(r.items()):
  if k in {'label','strategy','adapt_signature'}:continue
  try:r[k]=float(v)
  except:pass
 return r

def main():
 summaries=[];paths=[]
 for c in CELLS:
  d=SRC/c['label'];summaries += [num(r) for r in readcsv(d/'seed_summary.csv')];paths.append(d/'audit.csv')
 if len(summaries)!=EXPECTED_SUMMARIES:raise ValueError(len(summaries))
 for c in CELLS:
  q=[r for r in summaries if r['label']==c['label']]
  if len(q)!=2000 or {int(r['seed']) for r in q}!=set(SEEDS) or {r['strategy'] for r in q}!=set(STRATEGIES):raise ValueError(c['label'])
 OUT.mkdir(parents=True,exist_ok=True);write_csv(OUT/'seed_summary.csv',summaries)
 fields=[]
 for p in paths:
  with p.open(encoding='utf-8',newline='') as f:
   for k in csv.DictReader(f).fieldnames or []:
    if k not in fields:fields.append(k)
 count=0
 with (OUT/'audit_trace_seeds_30000_30004.csv').open('w',newline='',encoding='utf-8') as dst:
  w=csv.DictWriter(dst,fieldnames=fields);w.writeheader()
  for p in paths:
   with p.open(encoding='utf-8',newline='') as src:
    for row in csv.DictReader(src):w.writerow(row);count+=1
 if count!=EXPECTED_AUDIT_ROWS:raise ValueError(count)
 rep=report_from(summaries);(OUT/'report.json').write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps(rep['hypotheses'],indent=2))
if __name__=='__main__':main()
