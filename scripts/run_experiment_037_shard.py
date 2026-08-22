#!/usr/bin/env python3
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_037 import CELLS,STRATEGIES,run_experiment_037_strategy,evaluate_model_averaged_posterior
from run_experiment_037 import SEEDS,AUDIT,summary,write_csv,calibration_values

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cell-index',type=int,required=True);ap.add_argument('--out',required=True);a=ap.parse_args();c=CELLS[a.cell_index];out=Path(a.out);out.mkdir(parents=True,exist_ok=True);vals=calibration_values();summ=[];post=[]
 with (out/'audit.jsonl').open('w',encoding='utf-8') as af:
  for seed in SEEDS:
   post.extend(evaluate_model_averaged_posterior(seed,c))
   for st in STRATEGIES:
    rows=run_experiment_037_strategy(seed,c,st,vals);summ.append(summary(rows,c))
    if seed in AUDIT:
     for r in rows:af.write(json.dumps(r,separators=(',',':'))+'\n')
 write_csv(out/'summary.csv',summ);write_csv(out/'posterior.csv',post)
 (out/'meta.json').write_text(json.dumps({'cell_index':a.cell_index,'label':c['label'],'summary_rows':len(summ),'posterior_rows':len(post)},indent=2))
 if len(summ)!=4000 or len(post)!=5000:raise AssertionError((len(summ),len(post)))
if __name__=='__main__':main()
