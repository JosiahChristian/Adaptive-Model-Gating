#!/usr/bin/env python3
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from run_experiment_027 import CELLS,SEEDS,report_from,write_csv
SRC=ROOT/'results'/'experiment_027_shards';OUT=ROOT/'results'/'experiment_027';EXPECTED_ROWS=15*1000*5;EXPECTED_AUDIT=15*5*5

def readcsv(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def num(r):
 for k,v in list(r.items()):
  if k in {'label','kind','family','top_hypothesis'}:continue
  try:r[k]=float(v)
  except:pass
 return r

def main():
 rows=[];aud=[]
 for c in CELLS:
  d=SRC/c['label'];rows.extend(num(r) for r in readcsv(d/'posterior_rows.csv'));aud.extend(num(r) for r in readcsv(d/'audit.csv'))
 if len(rows)!=EXPECTED_ROWS:raise ValueError(len(rows))
 if len(aud)!=EXPECTED_AUDIT:raise ValueError(len(aud))
 for c in CELLS:
  q=[r for r in rows if r['label']==c['label']]
  if len(q)!=5000 or {int(r['seed']) for r in q}!=set(SEEDS) or {int(r['stage']) for r in q}!={1,2,3,4,5}:raise ValueError(c['label'])
 OUT.mkdir(parents=True,exist_ok=True);write_csv(OUT/'posterior_rows.csv',rows);write_csv(OUT/'audit_seeds_27000_27004.csv',aud)
 rep=report_from(rows);(OUT/'report.json').write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps(rep['hypotheses'],indent=2))
if __name__=='__main__':main()
