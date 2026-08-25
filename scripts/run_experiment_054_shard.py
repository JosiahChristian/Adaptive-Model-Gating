#!/usr/bin/env python3
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from run_experiment_054 import CELLS,STRATEGIES,SEEDS,AUDIT,summary,write_csv,calibration_values,run_experiment_054_strategy

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cell-index',type=int,required=True);ap.add_argument('--out',required=True);a=ap.parse_args();c=CELLS[a.cell_index];out=Path(a.out);out.mkdir(parents=True,exist_ok=True);vals=calibration_values();summ=[]
 with (out/'audit.jsonl').open('w',encoding='utf-8') as af:
  for seed in SEEDS:
   for st in STRATEGIES:
    rows=run_experiment_054_strategy(seed,c,st,vals);summ.append(summary(rows,c))
    if seed in AUDIT:
     for r in rows:
      record=dict(r);record['experiment054_cell']=c['label'];af.write(json.dumps(record,separators=(',',':'))+'\n')
 write_csv(out/'summary.csv',summ);(out/'meta.json').write_text(json.dumps({'cell_index':a.cell_index,'label':c['label'],'summary_rows':len(summ),'experiment':54},indent=2))
 if len(summ)!=len(SEEDS)*len(STRATEGIES):raise AssertionError(len(summ))
if __name__=='__main__':main()
