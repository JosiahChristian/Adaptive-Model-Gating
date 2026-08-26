#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'scripts'))

from experiment_051 import CELLS
import experiment_056 as exp56
from experiment_058 import (
    OPERATIVE_SPEC_ISSUE,SOURCE_SEED_START,SOURCE_SEED_STOP,REPLICA_SEED_OFFSET,
    RANDOMIZATION_SEED,RANDOMIZATION_RESAMPLES,BOOTSTRAP_SEED,BOOTSTRAP_RESAMPLES,
    independent_confirmation_readout,replica_seed,frozen_contract,
)


def main():
    # Synthetic/nonreserved smoke seed: never inspect reserved Experiment 058 outcomes.
    s=1234
    c=CELLS[0]
    rs=replica_seed(s)
    if rs != s + REPLICA_SEED_OFFSET:
        raise AssertionError((s,rs))
    source=exp56.generate_experiment_056_stream(s,c)
    replica=exp56.generate_experiment_056_stream(rs,c)
    d=independent_confirmation_readout(source,replica)
    if d['selected'] not in ('H_ab','H_ac','H_bc'):
        raise AssertionError(d['selected'])
    for side in ('source','replica'):
        for h in ('H_ab','H_ac','H_bc'):
            if len(d[f'{side}_vectors'][h]) != 30:
                raise AssertionError((side,h,len(d[f'{side}_vectors'][h])))
            if not (0 <= int(d[f'{side}_stats'][h]['wplus']) <= 465):
                raise AssertionError((side,h,d[f'{side}_stats'][h]['wplus']))
    contract=frozen_contract()
    assert contract['operative_spec_issue']==208==OPERATIVE_SPEC_ISSUE
    assert contract['source_seed_range']==(58000,62999)
    assert SOURCE_SEED_START==58000 and SOURCE_SEED_STOP==63000
    assert contract['replica_seed_offset']==10_000_000
    assert contract['w_cutoff_reference_only']==345
    assert RANDOMIZATION_SEED==58058 and RANDOMIZATION_RESAMPLES==100_000
    assert BOOTSTRAP_SEED==58059 and BOOTSTRAP_RESAMPLES==10_000
    print('Experiment 058 prospective smoke passed: independent replica reads confirmation only; frozen contract intact.')

if __name__=='__main__':
    main()
