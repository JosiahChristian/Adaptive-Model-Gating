#!/usr/bin/env python3
"""Execution-only packaging of two unchanged 50-seed validation coordinates."""
from __future__ import annotations
import argparse,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SHARD=ROOT/'scripts'/'run_experiment_070_validation_shard.py'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cell-index',type=int,required=True);ap.add_argument('--pair',type=int,required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
    if not 0<=a.cell_index<12 or not 0<=a.pair<40:raise ValueError('pair_coordinate')
    out=Path(a.out)
    for chunk in (2*a.pair,2*a.pair+1):
        target=out/f'chunk-{chunk:02d}'
        subprocess.run([sys.executable,str(SHARD),'--cell-index',str(a.cell_index),'--chunk',str(chunk),'--out',str(target)],check=True)
        if not (target/'rows.jsonl').is_file() or not (target/'meta.json').is_file():raise AssertionError('missing_chunk_evidence')
    print('Experiment 070 validation pair packaging complete; outcomes not summarized')
if __name__=='__main__':main()
