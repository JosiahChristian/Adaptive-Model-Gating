#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_054 import enumerate_null_boundary,ACCEPT_PATTERN_COUNT,BF_ACCEPTED_LOW,BF_REJECTED_HIGH,BF_CUTOFF,P_STAR,ACCEPT_E
from run_experiment_054 import SEEDS,AUDIT,STRESS,CELLS,STRATEGIES

def main():
 assert list(SEEDS)==list(range(54000,55000));assert AUDIT==set(range(54000,54005));assert len(CELLS)==16
 assert [STRESS[k][0] for k in ('M1','M2','M3','M4')]==[5451000,5452000,5453000,5454000]
 b=enumerate_null_boundary();assert b['accepted_count']==ACCEPT_PATTERN_COUNT==10485
 assert abs(b['accepted_low']-BF_ACCEPTED_LOW)<1e-12 and abs(b['rejected_high']-BF_REJECTED_HIGH)<1e-12
 assert abs(b['cutoff']-BF_CUTOFF)<1e-15 and abs(b['p_star']-P_STAR)<1e-15 and abs(b['accept_e']-ACCEPT_E)<1e-12
 assert len(STRATEGIES)>=4
 print('Experiment 054 evaluator preflight smoke passed')
if __name__=='__main__':main()
