#!/usr/bin/env python3
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from run_experiment_060 import CELLS,STRATEGIES,SEEDS,AUDIT,summary,write_csv,calibration_values,run_experiment_060_strategy

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cell-index',type=int,required=True);ap.add_argument('--seed-start',type=int,required=True);ap.add_argument('--seed-stop',type=int,required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
    if not (64000<=a.seed_start<a.seed_stop<=69000) or (a.seed_stop-a.seed_start)!=500 or (a.seed_start-64000)%500:raise SystemExit(('invalid_seed_chunk',a.seed_start,a.seed_stop))
    c=CELLS[a.cell_index];out=Path(a.out);out.mkdir(parents=True,exist_ok=True);vals=calibration_values();summ=[]
    with (out/'audit.jsonl').open('w',encoding='utf-8') as af:
        for seed in range(a.seed_start,a.seed_stop):
            for st in STRATEGIES:
                rows=run_experiment_060_strategy(seed,c,st,vals);summ.append(summary(rows,c))
                if seed in AUDIT:
                    for r in rows:
                        record=dict(r);record['experiment060_cell']=c['label'];af.write(json.dumps(record,separators=(',',':'))+'\n')
    write_csv(out/'summary.csv',summ)
    (out/'meta.json').write_text(json.dumps({'cell_index':a.cell_index,'label':c['label'],'seed_start':a.seed_start,'seed_stop':a.seed_stop,'summary_rows':len(summ),'experiment':60},indent=2))
    if len(summ)!=(a.seed_stop-a.seed_start)*len(STRATEGIES):raise AssertionError(len(summ))
if __name__=='__main__':main()
