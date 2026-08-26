#!/usr/bin/env python3
import argparse,csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from run_experiment_060 import CELLS,STRATEGIES,SEEDS,AUDIT,SIGNED_RANK_30_STRATEGY,targeted_report

CHUNK_SIZE=500;CHUNK_COUNT=10

def validate_audit(paths):
    expected={(c['label'],int(seed),st) for c in CELLS for seed in AUDIT for st in STRATEGIES};groups={};row_count=0;reference_interval=None
    for p in paths:
        with p.open(encoding='utf-8') as f:
            for line in f:
                if not line.strip():continue
                r=json.loads(line);row_count+=1;key=(str(r.get('experiment060_cell','')),int(r['seed']),str(r['strategy']))
                if key not in expected:raise AssertionError(('unexpected_audit_group',key))
                groups.setdefault(key,[]).append(int(r['t']))
    if set(groups)!=expected:raise AssertionError(('audit_groups',len(groups),len(expected)))
    for key,ts in groups.items():
        if len(ts)!=len(set(ts)):raise AssertionError(('duplicate_audit_t',key))
        ordered=sorted(ts);interval=(ordered[0],ordered[-1],len(ordered))
        if ordered!=list(range(ordered[0],ordered[-1]+1)):raise AssertionError(('noncontiguous_audit_t',key,interval))
        if reference_interval is None:reference_interval=interval
        elif interval!=reference_interval:raise AssertionError(('audit_interval_mismatch',key,interval,reference_interval))
    return row_count,reference_interval

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-root',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();root=Path(a.input_root);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    audit_paths=[];cell_seed_coverage={};counts={c['label']:{'n':0,'accepted_n':0,'correct_n':0,'wrong_n':0} for c in CELLS};summary_out=out/'summary.csv';writer=None;dest=None;total_rows=0
    try:
        dest=summary_out.open('w',newline='',encoding='utf-8')
        for i,c in enumerate(CELLS):
            label=c['label'];seen=set()
            for chunk in range(CHUNK_COUNT):
                d=root/f'cell-{i:02d}-chunk-{chunk:02d}';p=d/'summary.csv';apath=d/'audit.jsonl';meta=d/'meta.json'
                if not p.exists() or not apath.exists() or not meta.exists():raise FileNotFoundError((p,apath,meta))
                m=json.loads(meta.read_text());start=64000+chunk*CHUNK_SIZE;stop=start+CHUNK_SIZE
                if (m.get('cell_index'),m.get('label'),m.get('seed_start'),m.get('seed_stop'))!=(i,label,start,stop):raise AssertionError(('meta',i,chunk,m))
                with p.open(newline='',encoding='utf-8') as f:
                    reader=csv.DictReader(f)
                    if writer is None:writer=csv.DictWriter(dest,fieldnames=reader.fieldnames);writer.writeheader()
                    elif reader.fieldnames!=writer.fieldnames:raise AssertionError(('summary_fields',i,chunk))
                    chunk_rows=0
                    for r in reader:
                        writer.writerow(r);total_rows+=1;chunk_rows+=1;seed=int(r['seed']);st=r['strategy'];seen.add((seed,st))
                        if st==SIGNED_RANK_30_STRATEGY:
                            x=counts[label];x['n']+=1;accepted=int(float(r['coverage']));correct=int(float(r['correct']));wrong=int(float(r['wrong_accept']))
                            x['accepted_n']+=accepted;x['correct_n']+=correct;x['wrong_n']+=wrong
                    if chunk_rows!=CHUNK_SIZE*len(STRATEGIES):raise AssertionError(('chunk_rows',i,chunk,chunk_rows))
                audit_paths.append(apath)
            expected={(seed,st) for seed in SEEDS for st in STRATEGIES}
            if seen!=expected:raise AssertionError(('cell_seed_coverage',label,len(seen),len(expected)))
            cell_seed_coverage[label]=len(seen)
    finally:
        if dest is not None:dest.close()
    expected_total=len(CELLS)*len(SEEDS)*len(STRATEGIES)
    if total_rows!=expected_total:raise AssertionError(('summary_total',total_rows,expected_total))
    audit_count,interval=validate_audit(audit_paths)
    with (out/'audit.jsonl').open('w',encoding='utf-8') as d:
        for p in audit_paths:
            with p.open(encoding='utf-8') as s:
                for line in s:
                    if line.strip():d.write(line if line.endswith('\n') else line+'\n')
    report=targeted_report(counts);report['summary_row_count']=total_rows;report['audit_row_count']=audit_count;report['audit_time_interval']=interval;report['cell_seed_coverage']=cell_seed_coverage
    (out/'report.json').write_text(json.dumps(report,indent=2,sort_keys=True),encoding='utf-8')
    print(json.dumps({'summary_rows':total_rows,'audit_rows':audit_count,'audit_interval':interval,'H6_060_pass':report['H6_060_pass'],'H5_crosscheck_pass':report['H5_crosscheck_pass']},indent=2))
if __name__=='__main__':main()
