#!/usr/bin/env python3
import csv,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_021 import QUALIFICATION_AWARE_STRATEGY
from experiment_023 import NOISE_AWARE_STRATEGY
from experiment_024 import MARGIN_STRATEGY
from experiment_025 import CONDITIONAL_CONFIRMATION_STRATEGY,run_experiment_025_strategy
from experiment_022 import TRIAD
from run_experiment_021 import calibrations
from run_experiment_024 import CELLS as ALL_CELLS

STRATEGIES=(QUALIFICATION_AWARE_STRATEGY,NOISE_AWARE_STRATEGY,MARGIN_STRATEGY,CONDITIONAL_CONFIRMATION_STRATEGY,TRIAD)
SEEDS=list(range(26000,27000));AUDIT=set(range(26000,26005));N=len(SEEDS)
LABELS=('healthy_0.00','drift_0.50','g0.500_n1.00_0.50','g0.500_n1.25_0.50','g0.500_n1.50_0.50','g0.425_n1.00_0.50','g0.425_n1.50_0.50','g0.350_n1.00_0.50','g0.350_n1.50_0.50','g0.350_n2.00_0.50')
_by={c['label']:c for c in ALL_CELLS};CELLS=tuple(_by[x] for x in LABELS)
if len(CELLS)!=10:raise AssertionError(len(CELLS))

def write_csv(p,rows):
 p.parent.mkdir(parents=True,exist_ok=True);fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with p.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def summary(rows,c):
 r0=rows[0];post=[r for r in rows if 401<=r['t']<=600];p20=[r for r in rows if 401<=r['t']<=420]
 return {'seed':int(r0['seed']),'label':c['label'],'strategy':r0['strategy'],'coverage':float(r0.get('provenance_accepted',0)),'correct':float(r0.get('accepted_partition_correct',0) or 0),'abstain':float(r0.get('provenance_abstain',0)),'probe_energy':float(r0.get('probe_energy',0)),'adapt_401_420':int(any(r.get('adapt') for r in p20)),'operational_loss_401_600':sum(float(r['sq_error']) for r in post)}

def wilson_two_sided(k,n,z=1.959963984540054):
 if n<=0:return [None,None]
 p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
 return [max(0,c-h),min(1,c+h)]

def wilson_upper(k,n,z=1.6448536269514722):
 if n<=0:return None
 p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
 return min(1,c+h)

def stats(q):
 acc=[r for r in q if float(r['coverage'])==1.0];wrong=sum(1 for r in acc if float(r['correct'])!=1.0);correct=len(acc)-wrong
 cov=len(acc)/N
 return {'coverage':cov,'coverage_wilson_95':wilson_two_sided(len(acc),N),'abstention':1-cov,'accepted_n':len(acc),'correct_n':correct,'wrong_n':wrong,'precision':correct/len(acc) if acc else None,'wrong_acceptance':wrong/N,'wrong_acceptance_wilson_upper_95':wilson_upper(wrong,N),'mean_probe_energy':sum(float(r['probe_energy']) for r in q)/N,'adapt_401_420_rate':sum(float(r['adapt_401_420']) for r in q)/N,'mean_operational_loss_401_600':sum(float(r['operational_loss_401_600']) for r in q)/N}

def report_from(rows):
 out=[]
 for c in CELLS:
  cr=[r for r in rows if r['label']==c['label']];entry={'cell':c,'strategies':{}}
  for st in STRATEGIES:
   q=[r for r in cr if r['strategy']==st];s=stats(q);gain=c.get('gain');moderate=gain is not None and float(gain)>=.425
   s['safety_supported']=bool(s['wrong_acceptance_wilson_upper_95']<=.01)
   s['utility_supported']=bool(moderate and s['coverage']>=.85) if gain is not None else None
   s['jointly_supported']=bool(s['safety_supported'] and s['utility_supported']) if moderate else None
   entry['strategies'][st]=s
  out.append(entry)
 return {'evaluation_seeds':[26000,26999],'n_seeds_per_cell':N,'cell_count':len(CELLS),'strategies':list(STRATEGIES),'no_recalibration':True,'audit_seeds':sorted(AUDIT),'interpretation_rule':'estimation study; no policy modification or post-hoc winner selection','cells':out}
