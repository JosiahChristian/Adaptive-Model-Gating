#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import experiment_067 as e67

SHARD_N = 1000
SHARD_COUNT = 4
EXECUTION_CLOSURE_ISSUE = 282


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--panel', required=True)
    ap.add_argument('--shard-index', type=int, required=True)
    ap.add_argument('--out', required=True)
    a=ap.parse_args()
    if not e67.provenance_integrity():
        raise AssertionError('provenance_integrity')
    if a.panel not in e67.DEVELOPMENT_RANGES:
        raise ValueError('panel')
    if not 0 <= a.shard_index < SHARD_COUNT:
        raise ValueError('shard-index')
    panel_start,panel_stop=e67.DEVELOPMENT_RANGES[a.panel]
    if panel_stop-panel_start != SHARD_N*SHARD_COUNT:
        raise AssertionError('panel_partition')
    start=panel_start+SHARD_N*a.shard_index
    stop=start+SHARD_N
    rows=[e67.evaluate_diagnostic_draw(a.panel,seed,panel_start) for seed in range(start,stop)]
    if [int(r['seed']) for r in rows] != list(range(start,stop)):
        raise AssertionError('seed_coverage')
    for r in rows:
        if len(r['replicas']) != 5 or any(rep['discovery_used'] is not False for rep in r['replicas']):
            raise AssertionError('replica_identity')
        if [rep['replica_seed'] for rep in r['replicas']] != [e67.replica_seed(r['seed'],j) for j in range(1,6)]:
            raise AssertionError('replica_seed_mapping')
    out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    with (out/'rows.jsonl').open('w',encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row,separators=(',',':'))+'\n')
    meta={
        'experiment':67,'role':'zq_diagnostic_shard','panel':a.panel,
        'shard_index':a.shard_index,'seed_range':[start,stop-1],'n':len(rows),
        'replica_count':5,'operative_spec_issue':279,'provenance_closure_issue':280,
        'preflight_issue':281,'execution_closure_issue':EXECUTION_CLOSURE_ISSUE,
        'rq_seeds_touched':False,'experiment_066_validation_touched':False,'no_tuning':True
    }
    (out/'meta.json').write_text(json.dumps(meta,indent=2))
    print(f'preserved {a.panel} shard {a.shard_index}: {len(rows)} source draws; no diagnostic summaries printed')

if __name__=='__main__': main()
