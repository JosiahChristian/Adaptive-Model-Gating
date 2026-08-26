#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_051 import CELLS
import experiment_056 as exp56
from experiment_055 import infer_30contrast_exact_signed_rank,W_CUTOFF
from experiment_057 import diagnostic_readout,round_block_randomization,split_contract
from run_experiment_057 import SEEDS,AUDIT,STRESS,OPERATIVE_SPEC_ISSUE

def main():
    assert OPERATIVE_SPEC_ISSUE==202
    assert (SEEDS.start,SEEDS.stop-1)==(57000,57999)
    assert AUDIT==set(range(57000,57005))
    assert STRESS=={'M1':5751000,'M2':5752000,'M3':5753000,'M4':5754000}
    assert W_CUTOFF==345
    split_contract()
    # Synthetic/preflight-only seed outside the reserved Experiment 057 primary range.
    c=CELLS[0];stream=exp56.generate_experiment_056_stream(999,c);d=diagnostic_readout(stream)
    _,_,_,_,path,_,_,_=infer_30contrast_exact_signed_rank(stream)
    assert d['selected']==path[0]['candidate']
    assert int(d['selected_wplus'])==int(path[-1]['wplus'])
    assert set(d['edge_vectors'])=={'H_ab','H_ac','H_bc'}
    assert all(len(v)==30 for v in d['edge_vectors'].values())
    for v in d['edge_vectors'].values():
        b=round_block_randomization(v);assert b['tail_denominator']==32 and len(b['enumerated_wplus'])==32
    print('Experiment 057 evaluator prospective smoke passed; no reserved primary outcome accessed')
if __name__=='__main__':main()
