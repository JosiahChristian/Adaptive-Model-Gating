#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_060 import SIGNED_RANK_30_STRATEGY,W_CUTOFF,P345_NUMERATOR,P345_DENOMINATOR,P344_NUMERATOR,P344_DENOMINATOR
from run_experiment_060 import CELLS,STRATEGIES,SEEDS,AUDIT,CHUNK_SIZE,CHUNK_COUNT,calibration_values,exact_tail,run_experiment_060_strategy,summary
assert list(SEEDS)==list(range(64000,69000));assert AUDIT==set(range(64000,64005));assert CHUNK_SIZE==500 and CHUNK_COUNT==10
assert len(CELLS)==16 and SIGNED_RANK_30_STRATEGY in STRATEGIES and W_CUTOFF==345
assert exact_tail(345)==(P345_NUMERATOR,P345_DENOMINATOR);assert exact_tail(344)==(P344_NUMERATOR,P344_DENOMINATOR)
vals=calibration_values();assert isinstance(vals,tuple) and len(vals)>=9
c=CELLS[0];rows=run_experiment_060_strategy(63999,c,SIGNED_RANK_30_STRATEGY,vals);s=summary(rows,c)
assert int(float(s['rank55_contrast_count']))==30;assert int(float(s['rank55_spec_issue']))==221
for r in range(1,6):
 assert len(str(s[f'rank55_baseline_discovery_r{r}']).split(','))==1
 assert len(str(s[f'rank55_baseline_confirmation_r{r}']).split(','))==3
 for tgt in 'abc':
  assert len(str(s[f'rank55_target_discovery_r{r}_{tgt}']).split(','))==2
  assert len(str(s[f'rank55_target_confirmation_r{r}_{tgt}']).split(','))==3
print('Experiment 060 evaluator prospective smoke passed on nonreserved seed 63999')
