#!/usr/bin/env python3
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from run_experiment_012 import CELLS,SEEDS,STRATEGIES,write_csv,report_from
SRC=ROOT/'results'/'experiment_012_shards';OUT=ROOT/'results'/'experiment_012'
def readcsv(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def num(r):
 for k,v in list(r.items()):
  if k in {'family','strategy'}:continue
  try:r[k]=float(v)
  except:pass
 return r
def main():
 summaries=[];audit=[];metas=[]
 for f,m in CELLS:
  label='healthy_0.00' if f=='healthy' else f'{f}_{m:.2f}';d=SRC/label;summaries += [num(r) for r in readcsv(d/'seed_summary.csv')];audit += [num(r) for r in readcsv(d/'audit.csv')];metas.append(json.loads((d/'metadata.json').read_text()))
 if len(summaries)!=19*8*200:raise ValueError(f'Expected 30400 summaries, got {len(summaries)}')
 for f,m in CELLS:
  c=[r for r in summaries if r['family']==f and float(r['magnitude'])==m]
  if len(c)!=8*200 or {int(r['seed']) for r in c}!=set(SEEDS) or {r['strategy'] for r in c}!=set(STRATEGIES):raise ValueError(f'Coverage mismatch {f} {m}')
 first=metas[0]
 for x in metas[1:]:
  for k in ('tau','kappa','kappa3','lambda_anchor_a','lambda_anchor_b','lambda_anchor_ab'):
   if x[k]!=first[k]:raise ValueError(f'Threshold mismatch {k}')
 write_csv(OUT/'seed_summary.csv',summaries);write_csv(OUT/'audit_trace_seeds_12000_12004.csv',audit);rep=report_from(summaries,first['tau'],first['kappa'],first['kappa3'],first['lambda_anchor_a'],first['lambda_anchor_b'],first['lambda_anchor_ab']);OUT.mkdir(parents=True,exist_ok=True);(OUT/'report.json').write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps(rep,indent=2))
if __name__=='__main__':main()
