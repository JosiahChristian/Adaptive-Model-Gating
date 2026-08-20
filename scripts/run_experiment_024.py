#!/usr/bin/env python3
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from adaptive_model_gating import BASELINE_A
from experiment_020 import EARLY_STRATEGY
from experiment_021 import QUALIFICATION_AWARE_STRATEGY
from experiment_022 import TARGET019,TRIAD
from experiment_023 import NOISE_AWARE_STRATEGY
from experiment_024 import MARGIN_STRATEGY,run_experiment_024_strategy
from run_experiment_021 import calibrations

STRATEGIES=(MARGIN_STRATEGY,NOISE_AWARE_STRATEGY,QUALIFICATION_AWARE_STRATEGY,EARLY_STRATEGY,TRIAD)
SEEDS=list(range(24000,24200));AUDIT=set(range(24000,24005));MAGS=(.25,.5,1.0)
def _cell(label,kind,family,m,**kw):return {'label':label,'kind':kind,'family':family,'magnitude':float(m),**kw}
def cells():
 out=[]
 for g,scales in ((.50,(1.0,1.25,1.5,1.75,2.0)),(.425,(1.0,1.5,2.0)),(.35,(1.0,1.5,2.0))):
  for n in scales:
   for m in MAGS:out.append(_cell(f'g{g:.3f}_n{n:.2f}_{m:.2f}','noise','drift_ab_fault',m,gain=g,noise_scale=n))
 out.append(_cell('healthy_0.00','control','healthy',0.0))
 for f in ('drift','common_mode','primary_fault','drift_all_aux_fault'):
  for m in MAGS:out.append(_cell(f'{f}_{m:.2f}','control',f,m))
 if len(out)!=46:raise AssertionError(len(out))
 return tuple(out)
CELLS=cells()
def write_csv(p,rows):
 p.parent.mkdir(parents=True,exist_ok=True);fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with p.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def summary(rows,c):
 r0=rows[0];post=[r for r in rows if 401<=r['t']<=600];p20=[r for r in rows if 401<=r['t']<=420];target=BASELINE_A+float(c['magnitude']) if c['family'].startswith('drift') else BASELINE_A
 return {'seed':r0['seed'],'label':c['label'],'strategy':r0['strategy'],'coverage':float(r0.get('provenance_accepted',0)),'correct':float(r0.get('accepted_partition_correct',0) or 0),'abstain':float(r0.get('provenance_abstain',0)),'probe_energy':float(r0.get('probe_energy',0)),'adapt_401_420':int(any(r['adapt'] for r in p20)),'adapt_signature':','.join(str(r['t']) for r in rows if r.get('adapt')),'operational_loss_401_600':sum(r['sq_error'] for r in post),'final_slope_error_abs':abs(rows[-1]['slope_after']-target),'noise_sd_hat':float(r0.get('diagnostic_noise_sd_hat',0.05))}
def rates(q):
 acc=[r for r in q if r['coverage']==1];correct=sum(r['correct'] for r in acc)
 return {'coverage':len(acc)/200,'abstention':1-len(acc)/200,'accepted_n':len(acc),'correct_n':int(correct),'precision':correct/len(acc) if acc else None,'wrong_acceptance':(len(acc)-correct)/200}
def mean(q,k):return sum(float(x[k]) for x in q)/len(q)
def report_from(rows):
 H={f'H{i}':True for i in range(1,9)};out=[]
 for c in CELLS:
  cr=[r for r in rows if r['label']==c['label']];by={st:[r for r in cr if r['strategy']==st] for st in STRATEGIES};rr={st:rates(by[st]) for st in STRATEGIES};m=rr[MARGIN_STRATEGY];n=rr[NOISE_AWARE_STRATEGY];old=rr[QUALIFICATION_AWARE_STRATEGY];ener={st:mean(by[st],'probe_energy') for st in STRATEGIES};adapt={st:mean(by[st],'adapt_401_420') for st in STRATEGIES}
  if m['wrong_acceptance']!=0:H['H1']=False
  if c.get('noise_scale',1)>=1.5 and m['accepted_n']>=20 and (m['precision'] is None or m['precision']<.99):H['H2']=False
  if c.get('gain')==.5 and c.get('noise_scale')==1.5 and m['coverage']<.85:H['H3']=False
  if c.get('gain')==.5 and c.get('noise_scale')==1.5 and (m['coverage']-n['coverage']<.08 or m['wrong_acceptance']!=0):H['H4']=False
  if c.get('gain')==.5 and c.get('noise_scale')==1.0 and (m['coverage']<old['coverage']-.03 or (m['precision'] or 0)<.99 or ener[MARGIN_STRATEGY]>ener[QUALIFICATION_AWARE_STRATEGY]+.05):H['H5']=False
  if c.get('gain') in (.425,.35) and c.get('noise_scale')==1.0 and (m['coverage']<old['coverage']-.03 or m['wrong_acceptance']!=0):H['H6']=False
  if c.get('gain')==.35 and c.get('noise_scale',1)>=1.5 and adapt[MARGIN_STRATEGY]>adapt[TRIAD]+.02:H['H7']=False
  btri={int(x['seed']):x for x in by[TRIAD]};mismatch=0
  for x in by[MARGIN_STRATEGY]:
   if x['abstain']==1:
    y=btri[int(x['seed'])]
    if x['adapt_signature']!=y['adapt_signature'] or x['operational_loss_401_600']!=y['operational_loss_401_600']:mismatch+=1
  if mismatch:H['H8']=False
  out.append({'cell':c,'rates':rr,'mean_probe_energy':ener,'adapt_401_420_rate':adapt,'fallback_exact_mismatches':mismatch,'mean_noise_sd_hat':mean(by[MARGIN_STRATEGY],'noise_sd_hat')})
 return {'evaluation_seeds':[24000,24199],'n_seeds_per_cell':200,'cell_count':46,'strategies':STRATEGIES,'no_recalibration':True,'audit_seeds':sorted(AUDIT),'hypotheses':H,'cells':out}
