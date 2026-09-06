#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, 'src')
import experiment_068 as exp

EXECUTION_CLOSURE_ISSUE=289
SHARD_N=500
SHARD_COUNT=16


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--panel', required=True, choices=sorted(exp.CALIBRATION_RANGES))
    ap.add_argument('--shard-index', required=True, type=int)
    ap.add_argument('--out', required=True)
    a=ap.parse_args()
    if not 0 <= a.shard_index < SHARD_COUNT: raise ValueError('shard_index')
    pstart,pstop=exp.CALIBRATION_RANGES[a.panel]
    start=pstart+a.shard_index*SHARD_N; stop=start+SHARD_N
    if stop>pstop: raise AssertionError('range')
    out=Path(a.out); out.mkdir(parents=True, exist_ok=True)
    rows=[]
    for seed in range(start,stop):
        r=exp.evaluate_calibration_draw(a.panel,seed,pstart)
        rows.append(r)
    if len(rows)!=SHARD_N or [r['seed'] for r in rows] != list(range(start,stop)): raise AssertionError('coverage')
    with (out/'rows.jsonl').open('w') as f:
        for r in rows: f.write(json.dumps(r,separators=(',',':'))+'\n')
    meta={'experiment':68,'role':'calibration_shard','operative_spec_issue':287,'provenance_closure_issue':288,'execution_closure_issue':EXECUTION_CLOSURE_ISSUE,'panel':a.panel,'shard_index':a.shard_index,'start':start,'stop':stop,'n':SHARD_N,'replica_count':5,'replica_seed_stride':10_000_000,'no_tuning':True,'reserved_confirmation_touched':False}
    (out/'meta.json').write_text(json.dumps(meta,indent=2,sort_keys=True)+'\n')
    print(f'Experiment 068 {a.panel} shard {a.shard_index} complete: {SHARD_N} rows preserved; outcomes not summarized')

if __name__=='__main__': main()
