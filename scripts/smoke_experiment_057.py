#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from experiment_057 import (
    CONTRAST_COUNT, OPERATIVE_SPEC_ISSUE, round_block_randomization, split_contract
)

assert OPERATIVE_SPEC_ISSUE == 202
contract=split_contract()
assert len(contract)==5
vals=tuple(float(i+1) if i % 2 == 0 else -float(i+1) for i in range(CONTRAST_COUNT))
r=round_block_randomization(vals)
assert r['tail_denominator']==32
assert len(r['enumerated_wplus'])==32
assert abs(r['minimum_attainable_tail']-(1/32))<1e-15
print('experiment057 prospective diagnostic smoke: PASS')
