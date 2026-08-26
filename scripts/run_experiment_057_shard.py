#!/usr/bin/env python3
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from run_experiment_057 import CELLS,SEEDS,AUDIT,diagnostic_row,write_csv

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cell-index',type=int,required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
    c=CELLS[a.cell_index];out=Path(a.out);rows=[];audit=[]
    for seed in SEEDS:
        r=diagnostic_row(seed,c);rows.append(r)
        if seed in AUDIT:
            audit.append({'experiment057_cell':c['label'],'seed':seed,'selected':r['selected'],'selected_wplus':r['selected_wplus'],'reference_selected_match':r['reference_selected_match'],'reference_wplus_match':r['reference_wplus_match'],'spec_issue':r['spec_issue']})
    write_csv(out/'diagnostics.csv',rows)
    (out/'audit.jsonl').write_text('\n'.join(json.dumps(x,sort_keys=True) for x in audit)+'\n',encoding='utf-8')
    print(json.dumps({'cell':c['label'],'rows':len(rows),'audit_rows':len(audit)},indent=2))
if __name__=='__main__':main()
