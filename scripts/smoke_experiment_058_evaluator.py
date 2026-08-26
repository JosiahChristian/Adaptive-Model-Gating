#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_051 import CELLS
from experiment_058 import frozen_contract,D5_RANDOMIZATION_RESAMPLES,d5_randomization_seed
from run_experiment_058 import diagnostic_row,audit_record,_paired_signflip_pvalue


def main():
    # Nonreserved synthetic seed only; this smoke never executes 58000..62999.
    seed=4321;c=CELLS[0];row,d=diagnostic_row(seed,c);a=audit_record(seed,c,d)
    assert row['seed']==seed and row['replica_seed']==seed+10_000_000
    assert row['reference_selected_match']==1 and row['reference_wplus_match']==1
    assert row['replica_discovery_used_for_selection']==0
    assert len(a['groups'])==3 and all(len(g['source_vector'])==30 and len(g['replica_vector'])==30 for g in a['groups'].values())
    p=_paired_signflip_pvalue([1,-2,3,-4,5],58058,1000,'greater')
    assert 0.0 < p['pvalue'] <= 1.0
    contract=frozen_contract()
    assert contract['source_seed_range']==(58000,62999)
    assert contract['replica_seed_offset']==10_000_000
    assert contract['randomization_resamples']==100_000
    assert contract['bootstrap_resamples']==10_000
    assert contract['d5_randomization_resamples']==D5_RANDOMIZATION_RESAMPLES==2_000
    assert d5_randomization_seed(0,0,0)==58058
    assert d5_randomization_seed(15,1,3)==73071
    print('Experiment 058 evaluator smoke passed on nonreserved synthetic data; frozen source/replica and D5 contracts intact.')

if __name__=='__main__':main()
