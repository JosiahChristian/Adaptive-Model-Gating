#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from run_experiment_031 import CELLS,SEEDS,evaluate_seed,inherited_thresholds,write_csv

def main():
 label=os.environ['EXPERIMENT_031_LABEL'];c=next(x for x in CELLS if x['label']==label);thr=inherited_thresholds();rows=[];audit=[]
 for seed in SEEDS:
  r,a=evaluate_seed(seed,c,thr);rows.append(r);audit.extend(a)
 out=ROOT/'results'/'experiment_031_shards'/label;write_csv(out/'seed_summary.csv',rows);write_csv(out/'audit.csv',audit)
 (out/'metadata.json').write_text(json.dumps({'label':label,'rows':len(rows),'audit_rows':len(audit)},indent=2)+'\n')
 if len(rows)!=1000:raise ValueError(len(rows))
if __name__=='__main__':main()
