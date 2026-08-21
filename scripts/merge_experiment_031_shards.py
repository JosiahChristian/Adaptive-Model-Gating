#!/usr/bin/env python3
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from run_experiment_031 import CELLS,SEEDS,inherited_thresholds,report_from,write_csv
SRC=ROOT/'results'/'experiment_031_shards';OUT=ROOT/'results'/'experiment_031'
def readcsv(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def num(r):
 for k,v in list(r.items()):
  if k in ('label','family','kind'):continue
  try:r[k]=float(v)
  except:pass
 return r
def main():
 rows=[];aud=[]
 for c in CELLS:
  q=[num(r) for r in readcsv(SRC/c['label']/'seed_summary.csv')]
  if len(q)!=1000 or {int(r['seed']) for r in q}!=set(SEEDS):raise ValueError(c['label'])
  rows+=q;aud+=readcsv(SRC/c['label']/'audit.csv')
 if len(rows)!=7000:raise ValueError(len(rows))
 if len(aud)!=700:raise ValueError(len(aud))
 OUT.mkdir(parents=True,exist_ok=True);write_csv(OUT/'seed_summary.csv',rows);write_csv(OUT/'audit_trace_seeds_31000_31004.csv',aud)
 rep=report_from(rows,inherited_thresholds());(OUT/'report.json').write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps(rep['hypotheses'],indent=2))
if __name__=='__main__':main()
