#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import experiment_070 as e70

assert e70.provenance_integrity()
assert len(e70.CELLS)==12
assert len({c['label'] for c in e70.CELLS})==12
assert e70.DEVELOPMENT_RANGE==(7_000_000,7_004_000)
assert e70.VALIDATION_RANGE==(7_004_000,7_008_000)
assert e70.DEVELOPMENT_RANGE[1] <= e70.VALIDATION_RANGE[0]
expected=set()
for nf in e70.NOISE_FAMILIES:
    expected |= {
        f'{nf}_g0.350_n1.50',
        f'{nf}_g0.425_n2.00',
        f'{nf}_g0.350_n2.00',
    }
assert {c['label'] for c in e70.CELLS}==expected
assert all(c['topology_truth']=='H_ab' for c in e70.CELLS)
# Nonreserved mechanical smoke only: no scientific source/replica seeds are generated.
print('Experiment 070 preflight PASS: provenance/cells/ranges/mechanics; no scientific outcomes generated')
