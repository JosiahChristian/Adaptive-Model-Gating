#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
import experiment_062 as e
from experiment_051 import CELLS
from run_experiment_021 import calibrations


def exact_tail(cutoff):
    counts=[0]*466;counts[0]=1
    for rank in range(1,31):
        for s in range(465,rank-1,-1):
            counts[s]+=counts[s-rank]
    return sum(counts[cutoff:]),2**30

assert e.OPERATIVE_SPEC_ISSUE==235
assert e.CONTRAST_COUNT==30 and e.W_CUTOFF==345
assert exact_tail(345)==(e.P345_NUMERATOR,e.P345_DENOMINATOR)
assert exact_tail(344)==(e.P344_NUMERATOR,e.P344_DENOMINATOR)
assert e.P345<0.01<e.P344
for r in range(1,6):
    target,(bd,bc)=e.split_indices_055(r)
    assert len(bd)==1 and len(bc)==3 and not(set(bd)&set(bc))
    for td,tc in target.values():
        assert len(td)==2 and len(tc)==3 and not(set(td)&set(tc))

# Nonreserved implementation-only smoke. Reserved Experiment 062 seeds are 70000..70999.
c=CELLS[0];seed=620620
stream=e.generate_experiment_062_stream(seed,c)
groups,accepted,abstain,stop,path,mats,yd,sd,yc,sc=e.infer_confirmation_agreement_062(stream)
assert stop==5 and len(path)==5 and len(yd)==6 and len(yc)==6
last=path[-1]
assert last['agreement']==int(last['candidate']==last['confirmation_candidate'])
assert accepted==int(last['signed_rank_pass'] and last['agreement'])
assert len([x for row in path for x in row['pairwise_responses']])==30
rows=e.run_experiment_062_strategy(seed,c,e.CONFIRMATION_AGREEMENT_STRATEGY,calibrations())
assert rows and all(r['experiment062_cell']==c['label'] for r in rows)
r0=rows[0]
assert int(r0['rank62_spec_issue'])==235
assert int(r0['rank62_w_cutoff'])==345
assert int(r0['rank62_contrast_count'])==30
assert int(r0['rank62_candidate_reselected'])==0
assert int(r0['rank62_no_extra_observations'])==1
assert int(r0['experiment062_exact_replication_of_061'])==1
assert str(r0['rank62_candidate'])==str(r0['rank61_candidate'])
assert str(r0['rank62_confirmation_candidate'])==str(r0['rank61_confirmation_candidate'])
print('Experiment 062 prospective smoke passed')
