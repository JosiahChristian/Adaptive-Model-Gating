#!/usr/bin/env python3
import argparse,csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_058 import OPERATIVE_SPEC_ISSUE,REPLICA_SEED_OFFSET,EDGE_ORDER,split_contract
from run_experiment_058 import CELLS,SEEDS,AUDIT,report_from,write_csv

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-root',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
    root=Path(a.input_root);out=Path(a.out);out.mkdir(parents=True,exist_ok=True);rows=[];audit=[]
    expected_audit={(c['label'],int(seed)) for c in CELLS for seed in AUDIT}
    for i,c in enumerate(CELLS):
        d=root/f'cell-{i:02d}';p=d/'diagnostics.csv';apath=d/'audit.jsonl'
        if not p.exists() or not apath.exists():raise FileNotFoundError((p,apath))
        with p.open(newline='',encoding='utf-8') as f:part=list(csv.DictReader(f))
        if len(part)!=len(SEEDS):raise AssertionError(('diagnostic_rows',i,len(part),len(SEEDS)))
        if any(r['cell']!=c['label'] for r in part):raise AssertionError(('cell_label_mismatch',i))
        rows.extend(part)
        for line in apath.read_text(encoding='utf-8').splitlines():
            if line.strip():audit.append(json.loads(line))
    keys={(str(x['experiment058_cell']),int(x['source_seed'])) for x in audit}
    if keys!=expected_audit or len(audit)!=len(expected_audit):raise AssertionError(('audit_groups',len(keys),len(expected_audit),len(audit)))
    for x in audit:
        if int(x['spec_issue'])!=OPERATIVE_SPEC_ISSUE or int(x['replica_seed'])!=int(x['source_seed'])+REPLICA_SEED_OFFSET or int(x['replica_discovery_used_for_selection'])!=0:raise AssertionError(('audit_integrity',x.get('experiment058_cell'),x.get('source_seed')))
        if x['split_contract']!=split_contract():raise AssertionError(('split_contract',x['experiment058_cell'],x['source_seed']))
        if set(x['groups'])!=set(EDGE_ORDER):raise AssertionError(('edge_groups',x['experiment058_cell'],x['source_seed']))
        for h in EDGE_ORDER:
            g=x['groups'][h]
            if len(g['source_vector'])!=30 or len(g['replica_vector'])!=30:raise AssertionError(('vector_length',x['experiment058_cell'],x['source_seed'],h))
    write_csv(out/'diagnostics.csv',rows)
    (out/'audit.jsonl').write_text('\n'.join(json.dumps(x,sort_keys=True) for x in audit)+'\n',encoding='utf-8')
    report=report_from(rows);report['diagnostic_row_count']=len(rows);report['audit_row_count']=len(audit)
    (out/'report.json').write_text(json.dumps(report,indent=2,sort_keys=True),encoding='utf-8')
    print(json.dumps({'diagnostic_rows':len(rows),'audit_rows':len(audit),'D1':report['D1_integrity'],'D2':report['D2_matched_wrong_selection'],'D3_global':report['D3_wrong_selected_acceptance']['global']},indent=2))

if __name__=='__main__':main()
