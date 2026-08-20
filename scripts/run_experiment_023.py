#!/usr/bin/env python3
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from adaptive_model_gating import BASELINE_A,paired_bootstrap_ci
from experiment_020 import EARLY_STRATEGY
from experiment_021 import QUALIFICATION_AWARE_STRATEGY
from experiment_022 import TARGET019,TRIAD
from experiment_023 import NOISE_AWARE_STRATEGY,run_experiment_023_strategy
from run_experiment_021 import calibrations

STRATEGIES=(NOISE_AWARE_STRATEGY,QUALIFICATION_AWARE_STRATEGY,EARLY_STRATEGY,TARGET019,TRIAD)
SEEDS=list(range(23000,23200));AUDIT=set(range(23000,23005));BOOTSTRAP_SEED=23023
MAGS=(.25,.5,1.0)

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
 return {'seed':r0['seed'],'label':c['label'],'kind':c['kind'],'family':c['family'],'magnitude':c['magnitude'],'gain':c.get('gain',r0.get('probe_gain',1.0)),'noise_scale':c.get('noise_scale',1.0),'strategy':r0['strategy'],'coverage':float(r0.get('provenance_accepted',0)),'correct':float(r0.get('accepted_partition_correct',0) or 0),'abstain':float(r0.get('provenance_abstain',0)),'probe_energy':float(r0.get('probe_energy',0)),'adapt_401_420':int(any(r['adapt'] for r in p20)),'operational_loss_401_600':sum(r['sq_error'] for r in post),'final_slope_error_abs':abs(rows[-1]['slope_after']-target),'noise_factor':float(r0.get('diagnostic_noise_factor',1.0)),'noise_sd_hat':float(r0.get('diagnostic_noise_sd_hat',0.05))}

def rates(q):
 acc=[r for r in q if r['coverage']==1];correct=sum(r['correct'] for r in acc)
 return {'coverage':len(acc)/200,'abstention':1-len(acc)/200,'accepted_n':len(acc),'correct_n':int(correct),'precision':correct/len(acc) if acc else None,'wrong_acceptance':(len(acc)-correct)/200}
def mean(q,k):return sum(float(x[k]) for x in q)/len(q)
def ci(v):return list(paired_bootstrap_ci(v,seed=BOOTSTRAP_SEED,reps=10000))

def report_from(rows):
 cells_out=[];H1=True;H2=True;H3=True;H4=True;H5=True;H6=True
 for c in CELLS:
  cr=[r for r in rows if r['label']==c['label']];by={st:[r for r in cr if r['strategy']==st] for st in STRATEGIES};rr={st:rates(by[st]) for st in STRATEGIES};qa=rr[NOISE_AWARE_STRATEGY];old=rr[QUALIFICATION_AWARE_STRATEGY]
  energies={st:mean(by[st],'probe_energy') for st in STRATEGIES};adapts={st:mean(by[st],'adapt_401_420') for st in STRATEGIES}
  if qa['wrong_acceptance']!=0:H1=False
  if float(c.get('noise_scale',1.0))>=1.5 and qa['accepted_n']>=20 and (qa['precision'] is None or qa['precision']<.99):H2=False
  if c.get('gain')==.5 and c.get('noise_scale')==1.5 and qa['coverage']<.85:H3=False
  if c.get('gain')==.5 and c.get('noise_scale')==1.0:
   if qa['coverage']<old['coverage']-.03 or (qa['precision'] or 0)<.99 or energies[NOISE_AWARE_STRATEGY]>energies[QUALIFICATION_AWARE_STRATEGY]+.05:H4=False
  if c.get('gain') in (.425,.35) and c.get('noise_scale')==1.0:
   if qa['coverage']<old['coverage']-.03 or qa['wrong_acceptance']!=0:H5=False
  if c.get('gain',1)>0 and c.get('gain',1)<=.35 and c.get('noise_scale',1)>=1.5 and adapts[NOISE_AWARE_STRATEGY]>adapts[TRIAD]+.02:H6=False
  cells_out.append({'cell':c,'rates':rr,'mean_probe_energy':energies,'adapt_401_420_rate':adapts,'mean_noise_factor':mean(by[NOISE_AWARE_STRATEGY],'noise_factor'),'noise_factor_min':min(r['noise_factor'] for r in by[NOISE_AWARE_STRATEGY]),'noise_factor_max':max(r['noise_factor'] for r in by[NOISE_AWARE_STRATEGY])})
 return {'evaluation_seeds':[23000,23199],'bootstrap_seed':BOOTSTRAP_SEED,'n_seeds_per_cell':200,'cell_count':len(CELLS),'strategies':STRATEGIES,'no_recalibration':True,'audit_seeds':sorted(AUDIT),'hypotheses':{'H1_restored_safety':H1,'H2_high_noise_precision':H2,'H3_high_noise_coverage':H3,'H4_nominal_nonregression':H4,'H5_moderate_gain_preservation':H5,'H6_low_information_conservatism':H6,'H7_mechanism_validity':'structural'},'cells':cells_out}
