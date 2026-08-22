#!/usr/bin/env python3
import math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'scripts'))
from experiment_039 import CELLS,STRATEGIES,RADIAL_C,LOG_RADIAL_NORM_2D,posterior_radial_huber,run_experiment_039_strategy,evaluate_radial_huber_posterior
from experiment_028 import covariance_terms
from run_experiment_021 import calibrations

def main():
    target=math.sqrt(-2.0*math.log(.05))
    if abs(RADIAL_C-target)>1e-15:
        raise AssertionError((RADIAL_C,target))
    expected=-math.log(2.0*math.pi*(1.0+math.exp(-.5*RADIAL_C*RADIAL_C)/(RADIAL_C*RADIAL_C)))
    if abs(LOG_RADIAL_NORM_2D-expected)>1e-15:
        raise AssertionError((LOG_RADIAL_NORM_2D,expected))
    p=posterior_radial_huber((0,0,0,0,0,0),*covariance_terms(.05,1))
    if abs(sum(p.values())-1)>1e-10 or any((not math.isfinite(x) or x<0 or x>1) for x in p.values()):
        raise AssertionError(p)
    vals=calibrations()
    seed=40999
    for idx in (0,1,4,8,12,15):
        c=CELLS[idx]
        pr=evaluate_radial_huber_posterior(seed,c)
        if len(pr)!=5:
            raise AssertionError((c['label'],len(pr)))
        for st in STRATEGIES:
            rows=run_experiment_039_strategy(seed,c,st,vals)
            if not rows or len(rows)!=900:
                raise AssertionError((c['label'],st,len(rows)))
    print('Experiment 039 smoke OK')
if __name__=='__main__':main()
