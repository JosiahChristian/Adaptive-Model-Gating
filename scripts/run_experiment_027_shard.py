#!/usr/bin/env python3
import csv,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_027 import evaluate_posterior_path
from run_experiment_027 import CELLS,SEEDS,AUDIT,write_csv
EXPECTED_ROWS=1000*5;EXPECTED_AUDIT=5*5

def main():
 label=os.environ['EXPERIMENT_027_LABEL'];c=next(x for x in CELLS if x['label']==label);out=ROOT/'results'/'experiment_027_shards'/label;out.mkdir(parents=True,exist_ok=True);rows=[];audit=[]
 for seed in SEEDS:
  q=evaluate_posterior_path(seed,c);rows.extend(q)
  if seed in AUDIT:audit.extend(q)
 if len(rows)!=EXPECTED_ROWS:raise ValueError(len(rows))
 if len(audit)!=EXPECTED_AUDIT:raise ValueError(len(audit))
 write_csv(out/'posterior_rows.csv',rows);write_csv(out/'audit.csv',audit)
 (out/'metadata.json').write_text(json.dumps({'label':label,'posterior_rows':len(rows),'audit_rows':len(audit),'evaluation_seeds':[27000,27999]},indent=2)+'\n')
if __name__=='__main__':main()
