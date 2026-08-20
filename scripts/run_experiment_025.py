#!/usr/bin/env python3
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from adaptive_model_gating import BASELINE_A
from experiment_021 import QUALIFICATION_AWARE_STRATEGY
from experiment_022 import TRIAD
from experiment_023 import NOISE_AWARE_STRATEGY
from experiment_024 import MARGIN_STRATEGY
from experiment_025 import CONDITIONAL_CONFIRMATION_STRATEGY,NOISE_TRIGGER,run_experiment_025_strategy
from run_experiment_021 import calibrations
from run_experiment_024 import CELLS

STRATEGIES=(CONDITIONAL_CONFIRMATION_STRATEGY,MARGIN_STRATEGY,NOISE_AWARE_STRATEGY,QUALIFICATION_AWARE_STRATEGY,TRIAD)
SEEDS=list(range(25000,25200));AUDIT=set(range(25000,25005));BOOTSTRAP_SEED=25025

def write_csv(p,rows):
 p.parent.mkdir(parents=True,exist_ok=True);fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with p.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def _gate_signature(r):
 vals=[str(r.get(f'gate_group_{x}','')) for x in 'abc']
 return '|'.join(vals)

def summary(rows,c):
 r0=rows[0];post=[r for r in rows if 401<=r['t']<=600];p20=[r for r in rows if 401<=r['t']<=420];target=BASELINE_A+float(c['magnitude']) if c['family'].startswith('drift') else BASELINE_A
 return {'seed':r0['seed'],'label':c['label'],'strategy':r0['strategy'],'coverage':float(r0.get('provenance_accepted',0)),'correct':float(r0.get('accepted_partition_correct',0) or 0),'abstain':float(r0.get('provenance_abstain',0)),'probe_energy':float(r0.get('probe_energy',0)),'adapt_401_420':int(any(r['adapt'] for r in p20)),'adapt_signature':','.join(str(r['t']) for r in rows if r.get('adapt')),'gate_signature':_gate_signature(r0),'operational_loss_401_600':sum(r['sq_error'] for r in post),'final_slope_error_abs':abs(rows[-1]['slope_after']-target),'noise_factor':float(r0.get('diagnostic_noise_factor',1.0)),'round6_executed':int(r0.get('round6_executed',0)),'high_noise_branch':int(r0.get('conditional_high_noise_branch',0))}

def rates(q):
 acc=[r for r in q if r['coverage']==1];correct=sum(r['correct'] for r in acc)
 return {'coverage':len(acc)/200,'abstention':1-len(acc)/200,'accepted_n':len(acc),'correct_n':int(correct),'precision':correct/len(acc) if acc else None,'wrong_acceptance':(len(acc)-correct)/200}
def mean(q,k):return sum(float(x[k]) for x in q)/len(q)

def report_from(rows):
 H={f'H{i}':True for i in range(1,10)};out=[]
 for c in CELLS:
  cr=[r for r in rows if r['label']==c['label']];by={st:[r for r in cr if r['strategy']==st] for st in STRATEGIES};rr={st:rates(by[st]) for st in STRATEGIES};p=rr[CONDITIONAL_CONFIRMATION_STRATEGY];m=rr[MARGIN_STRATEGY];n=rr[NOISE_AWARE_STRATEGY];old=rr[QUALIFICATION_AWARE_STRATEGY];ener={st:mean(by[st],'probe_energy') for st in STRATEGIES};adapt={st:mean(by[st],'adapt_401_420') for st in STRATEGIES}
  if p['wrong_acceptance']!=0:H['H1']=False
  if c.get('noise_scale',1)>=1.5 and p['accepted_n']>=20 and (p['precision'] is None or p['precision']<.99):H['H2']=False
  if c.get('gain')==.5 and c.get('noise_scale')==1.5 and (p['coverage']<.85 or p['wrong_acceptance']!=0):H['H3']=False
  if c.get('gain')==.5 and c.get('noise_scale')==1.5 and (p['coverage']-m['coverage']<.15 or p['coverage']-n['coverage']<.08 or p['wrong_acceptance']!=0):H['H4']=False
  # H5 exact nominal preservation on seeds actually routed to the low-noise branch.
  old_by={int(x['seed']):x for x in by[QUALIFICATION_AWARE_STRATEGY]};nominal_mismatch=0
  for x in by[CONDITIONAL_CONFIRMATION_STRATEGY]:
   if x['noise_factor']<=NOISE_TRIGGER:
    y=old_by[int(x['seed'])]
    if (x['coverage']!=y['coverage'] or x['gate_signature']!=y['gate_signature'] or x['adapt_signature']!=y['adapt_signature'] or x['operational_loss_401_600']!=y['operational_loss_401_600'] or x['probe_energy']!=y['probe_energy']):nominal_mismatch+=1
  if nominal_mismatch:H['H5']=False
  if c.get('gain') in (.425,.35) and c.get('noise_scale')==1.0 and (p['coverage']<old['coverage']-.03 or p['wrong_acceptance']!=0):H['H6']=False
  # H7: round 6 only in high noise, only after 024 would abstain; burden at original boundary <=1.35.
  margin_by={int(x['seed']):x for x in by[MARGIN_STRATEGY]};round6_violation=0
  for x in by[CONDITIONAL_CONFIRMATION_STRATEGY]:
   if x['round6_executed']:
    y=margin_by[int(x['seed'])]
    if x['noise_factor']<=NOISE_TRIGGER or y['abstain']!=1:round6_violation+=1
  if round6_violation:H['H7']=False
  if c.get('gain')==.5 and c.get('noise_scale')==1.5 and ener[CONDITIONAL_CONFIRMATION_STRATEGY]>1.35:H['H7']=False
  if c.get('gain')==.35 and c.get('noise_scale',1)>=1.5 and adapt[CONDITIONAL_CONFIRMATION_STRATEGY]>adapt[TRIAD]+.02:H['H8']=False
  tri_by={int(x['seed']):x for x in by[TRIAD]};fallback_mismatch=0
  for x in by[CONDITIONAL_CONFIRMATION_STRATEGY]:
   if x['abstain']==1:
    y=tri_by[int(x['seed'])]
    if x['adapt_signature']!=y['adapt_signature'] or x['operational_loss_401_600']!=y['operational_loss_401_600']:fallback_mismatch+=1
  if fallback_mismatch:H['H9']=False
  out.append({'cell':c,'rates':rr,'mean_probe_energy':ener,'adapt_401_420_rate':adapt,'nominal_exact_mismatches':nominal_mismatch,'round6_condition_violations':round6_violation,'fallback_exact_mismatches':fallback_mismatch,'round6_rate':mean(by[CONDITIONAL_CONFIRMATION_STRATEGY],'round6_executed'),'high_noise_branch_rate':mean(by[CONDITIONAL_CONFIRMATION_STRATEGY],'high_noise_branch'),'mean_noise_factor':mean(by[CONDITIONAL_CONFIRMATION_STRATEGY],'noise_factor')})
 return {'evaluation_seeds':[25000,25199],'bootstrap_seed':BOOTSTRAP_SEED,'n_seeds_per_cell':200,'cell_count':len(CELLS),'strategies':STRATEGIES,'no_recalibration':True,'audit_seeds':sorted(AUDIT),'noise_trigger':NOISE_TRIGGER,'hypotheses':H,'cells':out}
