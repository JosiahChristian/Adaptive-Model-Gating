#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from experiment_060 import *

assert OPERATIVE_SPEC_ISSUE == 221
assert CONTRAST_COUNT == 30
assert W_CUTOFF == 345
assert P345_NUMERATOR == 10555320 and P345_DENOMINATOR == 1073741824
assert P344_NUMERATOR == 11193679 and P344_DENOMINATOR == 1073741824
assert P345 < 0.01 < P344
assert ACCEPT_E >= 100

# Structural split contract only; no reserved Experiment 060 outcomes executed.
for r in range(1,6):
    target,(bd,bc)=split_indices_055(r)
    assert len(bd)==1 and len(bc)==3 and not (set(bd)&set(bc))
    assert len(set(bd+bc))==4
    for td,tc in target.values():
        assert len(td)==2 and len(tc)==3 and not (set(td)&set(tc))
        assert len(set(td+tc))==5
print('Experiment 060 prospective core smoke: PASS')
