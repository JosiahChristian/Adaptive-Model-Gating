#!/usr/bin/env python3
from __future__ import annotations
import argparse,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RUNNER=ROOT/'scripts'/'run_experiment_069_shard.py'
BLOCK_SIZE=10
AMENDMENT_ISSUE=296

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--cell-index',type=int,required=True)
    ap.add_argument('--block',type=int,required=True)
    ap.add_argument('--out',required=True)
    a=ap.parse_args()
    if not 0 <= a.cell_index < 16: raise ValueError('cell-index')
    if not 0 <= a.block < 8: raise ValueError('block')
    out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    first=a.block*BLOCK_SIZE
    for chunk in range(first,first+BLOCK_SIZE):
        dest=out/f'chunk-{chunk}'
        subprocess.run([sys.executable,str(RUNNER),'--mode','primary','--cell-index',str(a.cell_index),'--chunk',str(chunk),'--out',str(dest)],check=True)
        if not (dest/'rows.jsonl').exists() or not (dest/'meta.json').exists(): raise AssertionError('chunk_output')
    print(f'Experiment 069 packed primary block complete: cell={a.cell_index} block={a.block} chunks={first}-{first+BLOCK_SIZE-1}; outcomes not summarized')

if __name__=='__main__': main()
