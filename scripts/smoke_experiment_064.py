#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import experiment_064 as exp64

assert exp64.provenance_integrity()
# All smoke seeds are prospectively nonreserved and lie outside 6400000..6417999.
for i,panel in enumerate(exp64.SEED_RANGES):
    seed=6420000+i
    rows=exp64.evaluate_draw(panel,seed,start=6420000)
    assert set(rows)==set(exp64.ARCHITECTURES)
    candidates={r['discovery_candidate'] for r in rows.values()}
    conf={r['confirmation_candidate'] for r in rows.values()}
    assert len(candidates)==1 and len(conf)==1
    for architecture,row in rows.items():
        assert row['architecture']==architecture
        assert row['seed']==seed and row['panel']==panel
        assert row['final_accept']==int(row['underlying_accept'] and row['agreement'])
print('experiment064 nonreserved smoke PASS')
