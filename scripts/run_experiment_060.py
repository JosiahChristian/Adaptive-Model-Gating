#!/usr/bin/env python3
import math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'scripts'))
import experiment_060 as exp60
import run_experiment_055 as base
from experiment_051 import CELLS

SEEDS=range(64000,69000)
AUDIT=set(range(64000,64005))
STRATEGIES=exp60.STRATEGIES
SIGNED_RANK_30_STRATEGY=exp60.SIGNED_RANK_30_STRATEGY
W_CUTOFF=exp60.W_CUTOFF
P345_NUMERATOR=exp60.P345_NUMERATOR
P345_DENOMINATOR=exp60.P345_DENOMINATOR
P344_NUMERATOR=exp60.P344_NUMERATOR
P344_DENOMINATOR=exp60.P344_DENOMINATOR
OPERATIVE_SPEC_ISSUE=221
CHUNK_SIZE=500
CHUNK_COUNT=10
Z=1.6448536269514722
calibration_values=base.calibration_values
write_csv=base.write_csv
summary=base.summary
exact_tail=base.exact_tail

def run_experiment_060_strategy(seed,c,strategy,vals):
    return exp60.run_experiment_060_strategy(seed,c,strategy,vals)

def wilson_upper(k,n):
    if n<=0:return 1.0
    p=k/n;den=1+Z*Z/n
    center=(p+Z*Z/(2*n))/den
    rad=Z*math.sqrt(p*(1-p)/n+Z*Z/(4*n*n))/den
    return min(1.0,center+rad)

def targeted_report(cell_counts):
    cells={};h6=True;h5=True
    for c in CELLS:
        label=c['label'];x=cell_counts[label]
        n=x['n'];accepted=x['accepted_n'];correct=x['correct_n'];wrong=x['wrong_n']
        if n!=5000:raise AssertionError(('primary_seed_count',label,n))
        precision=(correct/accepted) if accepted else None
        upper=wilson_upper(wrong,n)
        h6_cell=(accepted>0 and precision is not None and precision>=0.99)
        h5_cell=(upper<=0.01)
        h6=h6 and h6_cell;h5=h5 and h5_cell
        cells[label]={'n_seeds':n,'accepted_n':accepted,'correct_n':correct,'wrong_n':wrong,'precision':precision,'wrong_acceptance':wrong/n,'wrong_wilson_upper_95':upper,'H6_cell_pass':h6_cell,'H5_crosscheck_pass':h5_cell}
    return {'experiment':60,'operative_spec_issue':OPERATIVE_SPEC_ISSUE,'targeted_h6_precision_stability':True,'evaluation_seeds':[64000,68999],'n_seeds_per_cell':5000,'cell_count':16,'audit_seeds':[64000,64001,64002,64003,64004],'strategies':list(STRATEGIES),'primary_strategy':SIGNED_RANK_30_STRATEGY,'contrast_count':30,'w_cutoff':W_CUTOFF,'p345_numerator':P345_NUMERATOR,'p345_denominator':P345_DENOMINATOR,'p344_numerator':P344_NUMERATOR,'p344_denominator':P344_DENOMINATOR,'H6_060_pass':h6,'H5_crosscheck_pass':h5,'H6_060_rule':'PASS iff every cell with accepted seeds has empirical accepted precision >=0.99 over all 5,000 fresh seeds','cells':cells,'execution_chunk_size':CHUNK_SIZE,'execution_chunks_per_cell':CHUNK_COUNT,'no_tuning':True,'architecture':'unchanged Experiment 055/056/059 30-contrast architecture; targeted H6 replication only; no M1-M4 rerun'}
