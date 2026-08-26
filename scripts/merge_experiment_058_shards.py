#!/usr/bin/env python3
import argparse,csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_058 import OPERATIVE_SPEC_ISSUE,REPLICA_SEED_OFFSET,EDGE_ORDER,split_contract,SOURCE_SEED_START,SOURCE_SEED_STOP
from run_experiment_058 import CELLS,SEEDS,AUDIT,report_from,write_csv

CHUNK_SIZE=500
CHUNK_COUNT=(SOURCE_SEED_STOP-SOURCE_SEED_START)//CHUNK_SIZE

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-root',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
    root=Path(a.input_root);out=Path(a.out);out.mkdir(parents=True,exist_ok=True);rows=[];audit=[]
    expected_audit={(c['label'],int(seed)) for c in CELLS for seed in AUDIT}
    for i,c in enumerate(CELLS):
        dirs=sorted(root.glob(f'cell-{i:02d}-chunk-*'))
        if len(dirs)!=CHUNK_COUNT:raise AssertionError(('chunk_count',i,len(dirs),CHUNK_COUNT))
        cell_rows=[]
        for d in dirs:
            p=d/'diagnostics.csv';apath=d/'audit.jsonl'
            if not p.exists() or not apath.exists():raise FileNotFoundError((p,apath))
            with p.open(newline='',encoding='utf-8') as f:part=list(csv.DictReader(f))
            if len(part)!=CHUNK_SIZE:raise AssertionError(('chunk_rows',d.name,len(part),CHUNK_SIZE))
            if any(r['cell']!=c['label'] for r in part):raise AssertionError(('cell_label_mismatch',d.name))
            cell_rows.extend(part)
            for line in apath.read_text(encoding='utf-8').splitlines():
                if line.strip():audit.append(json.loads(line))
        seeds=[int(r['seed']) for r in cell_rows]
        if len(cell_rows)!=len(SEEDS) or len(set(seeds))!=len(SEEDS) or set(seeds)!=set(SEEDS):raise AssertionError(('cell_seed_coverage',i,len(cell_rows),len(set(seeds))))
        rows.extend(cell_rows)
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
    report=report_from(rows);report['diagnostic_row_count']=len(rows);report['audit_row_count']=len(audit);report['execution_chunk_size']=CHUNK_SIZE;report['execution_chunks_per_cell']=CHUNK_COUNT
    (out/'report.json').write_text(json.dumps(report,indent=2,sort_keys=True),encoding='utf-8')
    print(json.dumps({'diagnostic_rows':len(rows),'audit_rows':len(audit),'chunks_per_cell':CHUNK_COUNT,'D1':report['D1_integrity'],'D2':report['D2_matched_wrong_selection'],'D3_global':report['D3_wrong_selected_acceptance']['global']},indent=2))

if __name__=='__main__':main()
