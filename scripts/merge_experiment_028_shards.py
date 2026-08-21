#!/usr/bin/env python3
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from run_experiment_028 import CELLS,MODELS,SEEDS,write_csv,report_from
SRC=ROOT/'results'/'experiment_028_shards';OUT=ROOT/'results'/'experiment_028';EXPECTED_ROWS=15*1000*2*5;EXPECTED_AUDIT=15*5*2*5

def readcsv(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def num(r):
 for k,v in list(r.items()):
  if k in {'label','kind','family','model','top_hypothesis'}:continue
  try:r[k]=float(v)
  except:pass
 return r

def main():
 rows=[];audit_paths=[]
 for c in CELLS:
  d=SRC/c['label'];q=[num(r) for r in readcsv(d/'posterior_rows.csv')];rows.extend(q);audit_paths.append(d/'audit.csv')
  if len(q)!=10000:raise ValueError((c['label'],len(q)))
  if {int(r['seed']) for r in q}!=set(SEEDS):raise ValueError((c['label'],'seeds'))
  if {r['model'] for r in q}!=set(MODELS):raise ValueError((c['label'],'models'))
 if len(rows)!=EXPECTED_ROWS:raise ValueError(len(rows))
 OUT.mkdir(parents=True,exist_ok=True);write_csv(OUT/'posterior_rows.csv',rows)
 fields=[]
 for p in audit_paths:
  with p.open(encoding='utf-8',newline='') as f:
   for k in csv.DictReader(f).fieldnames or []:
    if k not in fields:fields.append(k)
 count=0
 with (OUT/'audit_seeds_28000_28004.csv').open('w',newline='',encoding='utf-8') as dst:
  w=csv.DictWriter(dst,fieldnames=fields);w.writeheader()
  for p in audit_paths:
   with p.open(encoding='utf-8',newline='') as src:
    for row in csv.DictReader(src):w.writerow(row);count+=1
 if count!=EXPECTED_AUDIT:raise ValueError(count)
 rep=report_from(rows);(OUT/'report.json').write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps(rep['hypotheses'],indent=2))
if __name__=='__main__':main()
