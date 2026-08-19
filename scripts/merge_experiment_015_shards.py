#!/usr/bin/env python3
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from run_experiment_015 import CELLS,SEEDS,STRATEGIES,write_csv,report_from
SRC=ROOT/'results'/'experiment_015_shards';OUT=ROOT/'results'/'experiment_015'
def readcsv(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def num(r):
 for k,v in list(r.items()):
  if k in {'family','strategy','inferred_group_a','inferred_group_b','inferred_group_c'}:continue
  try:r[k]=float(v)
  except:pass
 return r
def main():
 summaries=[];audit=[];metas=[]
 for f,m in CELLS:
  label='healthy_0.00' if f=='healthy' else f'{f}_{m:.2f}';d=SRC/label;summaries += [num(r) for r in readcsv(d/'seed_summary.csv')];audit += [num(r) for r in readcsv(d/'audit.csv')];metas.append(json.loads((d/'metadata.json').read_text()))
 if len(summaries)!=22*10*200:raise ValueError(f'Expected 44000 summaries, got {len(summaries)}')
 if len(audit)!=22*10*5*900:raise ValueError(f'Expected 990000 audit rows, got {len(audit)}')
 for f,m in CELLS:
  c=[r for r in summaries if r['family']==f and float(r['magnitude'])==m]
  if len(c)!=10*200 or {int(float(r['seed'])) for r in c}!=set(SEEDS) or {r['strategy'] for r in c}!=set(STRATEGIES):raise ValueError(f'Coverage mismatch {f} {m}')
 keys=('tau','kappa','kappa3','lambda_anchor_a','lambda_anchor_b','lambda_anchor_ab','lambda_anchor_c','lambda_anchor_ac','lambda_anchor_bc','lambda_probe');first=metas[0]
 for x in metas[1:]:
  for k in keys:
   if x[k]!=first[k]:raise ValueError(f'Threshold mismatch {k}')
 vals=tuple(first[k] for k in keys);write_csv(OUT/'seed_summary.csv',summaries);write_csv(OUT/'audit_trace_seeds_15000_15004.csv',audit);rep=report_from(summaries,*vals);OUT.mkdir(parents=True,exist_ok=True);(OUT/'report.json').write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps(rep,indent=2))
if __name__=='__main__':main()
