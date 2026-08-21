#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_031 import CONTEXT_THRESHOLD,context_summary
from experiment_022 import generate_stress_stream
from run_experiment_031 import CELLS,inherited_thresholds

def main():
 if CONTEXT_THRESHOLD!=.50:raise AssertionError(CONTEXT_THRESHOLD)
 thr=inherited_thresholds();by={c['label']:c for c in CELLS}
 for label in ('healthy','common_mode_0.50','g0.500_n1.00'):
  s=generate_stress_stream(31999,by[label]);summ,path=context_summary(s,thr['k3'],thr['la'],thr['lb'],thr['lc'],thr['lab'],thr['lac'],thr['lbc'])
  if len(path)!=20 or summ['window_n']!=20:raise AssertionError((label,len(path)))
  if not 0<=summ['context_score']<=1:raise AssertionError((label,summ))
  if summ['common_mode_context']!=int(summ['context_score']>=.50):raise AssertionError((label,summ))
 print('Experiment 031 smoke passed.')
if __name__=='__main__':main()
