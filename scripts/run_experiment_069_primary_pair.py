#!/usr/bin/env python3
from __future__ import annotations
import argparse,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RUNNER=ROOT/'scripts'/'run_experiment_069_shard.py'
PAIR_SIZE=2
RECOVERY_ISSUE=297

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--cell-index',type=int,required=True)
    ap.add_argument('--pair',type=int,required=True)
    ap.add_argument('--out',required=True)
    a=ap.parse_args()
    if not 0 <= a.cell_index < 16: raise ValueError('cell-index')
    if not 0 <= a.pair < 40: raise ValueError('pair')
    out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    first=a.pair*PAIR_SIZE
    for chunk in (first,first+1):
        dest=out/f'chunk-{chunk}'
        subprocess.run([sys.executable,str(RUNNER),'--mode','primary','--cell-index',str(a.cell_index),'--chunk',str(chunk),'--out',str(dest)],check=True)
        if not (dest/'rows.jsonl').exists() or not (dest/'meta.json').exists(): raise AssertionError('chunk_output')
    print(f'Experiment 069 pair recovery complete: cell={a.cell_index} pair={a.pair} chunks={first}-{first+1}; outcomes not summarized')

if __name__=='__main__': main()
