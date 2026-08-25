#!/usr/bin/env python3
from collections import Counter
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))

import experiment_055 as e


def exact_tail(n):
    dp=Counter({0:1})
    for r in range(1,n+1):
        nxt=dp.copy()
        for s,c in dp.items():
            nxt[s+r]+=c
        dp=nxt
    total=2**n
    tail={}
    running=0
    for w in range(n*(n+1)//2,-1,-1):
        running+=dp[w]
        tail[w]=running
    return tail,total


def main():
    assert e.OPERATIVE_SPEC_ISSUE==190
    assert e.CONTRAST_COUNT==30
    assert e.W_CUTOFF==345
    assert e.P345_NUMERATOR==10555320 and e.P345_DENOMINATOR==1073741824
    assert e.P344_NUMERATOR==11193679 and e.P344_DENOMINATOR==1073741824
    assert e.P345<=0.01<e.P344
    assert e.ACCEPT_E>=100.0
    tail,total=exact_tail(30)
    assert total==1073741824
    assert tail[345]==10555320
    assert tail[344]==11193679
    for r in range(1,6):
        target,(bd,bc)=e.split_indices_055(r)
        assert len(bd)==1 and len(bc)==3 and set(bd).isdisjoint(bc)
        for td,tc in target.values():
            assert len(td)==2 and len(tc)==3 and set(td).isdisjoint(tc)
    vals=tuple(float(i+1) if i%3 else -float(i+1) for i in range(30))
    w,ranks=e.signed_rank_statistic_30(vals)
    assert sorted(ranks)==list(range(1,31))
    assert w==sum(i+1 for i,x in enumerate(vals) if x>0)
    print('Experiment 055 prospective smoke passed; 30-contrast allocation and exact null cutoff verified.')

if __name__=='__main__':
    main()
