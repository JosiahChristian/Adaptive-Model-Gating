#!/usr/bin/env python3
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from run_experiment_058 import CELLS,SEEDS,AUDIT,diagnostic_row,audit_record,write_csv

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cell-index',type=int,required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
    c=CELLS[a.cell_index];out=Path(a.out);out.mkdir(parents=True,exist_ok=True);rows=[];audit=[]
    for seed in SEEDS:
        row,d=diagnostic_row(seed,c);rows.append(row)
        if seed in AUDIT:audit.append(audit_record(seed,c,d))
    write_csv(out/'diagnostics.csv',rows)
    (out/'audit.jsonl').write_text('\n'.join(json.dumps(x,sort_keys=True) for x in audit)+'\n',encoding='utf-8')
    print(json.dumps({'cell_index':a.cell_index,'cell':c['label'],'diagnostic_rows':len(rows),'audit_rows':len(audit)}))

if __name__=='__main__':main()
