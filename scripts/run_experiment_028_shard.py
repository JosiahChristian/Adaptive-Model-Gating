#!/usr/bin/env python3
import csv,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_028 import evaluate_both_paths
from run_experiment_028 import CELLS,SEEDS,AUDIT,write_csv
EXPECTED_ROWS=1000*2*5

def main():
 label=os.environ['EXPERIMENT_028_LABEL'];c=next(x for x in CELLS if x['label']==label);out=ROOT/'results'/'experiment_028_shards'/label;out.mkdir(parents=True,exist_ok=True);rows=[];audit=[]
 for seed in SEEDS:
  q=evaluate_both_paths(seed,c);rows.extend(q)
  if seed in AUDIT:audit.extend(q)
 if len(rows)!=EXPECTED_ROWS:raise ValueError((label,len(rows)))
 if len(audit)!=5*2*5:raise ValueError((label,len(audit)))
 write_csv(out/'posterior_rows.csv',rows);write_csv(out/'audit.csv',audit)
 (out/'metadata.json').write_text(json.dumps({'label':label,'rows':len(rows),'audit_rows':len(audit),'evaluation_seeds':[28000,28999]},indent=2)+'\n')
if __name__=='__main__':main()
