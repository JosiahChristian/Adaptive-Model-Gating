#!/usr/bin/env python3
import argparse,csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from run_experiment_057 import CELLS,SEEDS,AUDIT,report_from,write_csv,OPERATIVE_SPEC_ISSUE

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-root',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
    root=Path(a.input_root);out=Path(a.out);out.mkdir(parents=True,exist_ok=True);rows=[];audit=[]
    expected_audit={(c['label'],int(seed)) for c in CELLS for seed in AUDIT}
    for i,c in enumerate(CELLS):
        d=root/f'cell-{i:02d}';p=d/'diagnostics.csv';apath=d/'audit.jsonl'
        if not p.exists() or not apath.exists():raise FileNotFoundError((p,apath))
        with p.open(newline='',encoding='utf-8') as f:part=list(csv.DictReader(f))
        if len(part)!=len(SEEDS):raise AssertionError(('diagnostic_rows',i,len(part),len(SEEDS)))
        rows.extend(part)
        for line in apath.read_text(encoding='utf-8').splitlines():
            if line.strip():audit.append(json.loads(line))
    keys={(str(x['experiment057_cell']),int(x['seed'])) for x in audit}
    if keys!=expected_audit or len(audit)!=len(expected_audit):raise AssertionError(('audit_groups',len(keys),len(expected_audit),len(audit)))
    if any(int(x['spec_issue'])!=OPERATIVE_SPEC_ISSUE or int(x['reference_selected_match'])!=1 or int(x['reference_wplus_match'])!=1 for x in audit):raise AssertionError('audit integrity')
    write_csv(out/'diagnostics.csv',rows)
    (out/'audit.jsonl').write_text('\n'.join(json.dumps(x,sort_keys=True) for x in audit)+'\n',encoding='utf-8')
    report=report_from(rows);report['diagnostic_row_count']=len(rows);report['audit_row_count']=len(audit)
    (out/'report.json').write_text(json.dumps(report,indent=2,sort_keys=True),encoding='utf-8')
    print(json.dumps({'diagnostic_rows':len(rows),'audit_rows':len(audit),'D1':report['D1_integrity']},indent=2))
if __name__=='__main__':main()
