#!/usr/bin/env python3
import csv,json,math,random,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_029 import TRIAD
from experiment_046 import E_THRESHOLD
from experiment_049 import PAIR_SIGN_STRATEGY
from experiment_051 import SIGNED_RANK_STRATEGY,CELLS
from experiment_054 import FAMILY_MIXTURE_STRATEGY
from experiment_055 import *
from run_experiment_021 import calibrations

SEEDS=range(55000,56000);AUDIT=set(range(55000,55005));Z=1.6448536269514722
STRESS={'M1':(5551000,'round-wise heteroskedastic symmetric scales 0.75,1.00,1.25,1.50,1.75'),'M2':(5552000,'direction-wise heteroskedastic symmetric forward:reverse 1:1.5'),'M3':(5553000,'AR(1) symmetric Gaussian rho=0.30'),'M4':(5554000,'90/10 asymmetric contaminated Gaussian shift +0.50')}
EXP053_MEAN_COVERAGE=0.2573125;EXP050_MEAN_COVERAGE=0.376125

def calibration_values():return calibrations()
def write_csv(p,rows):
 p.parent.mkdir(parents=True,exist_ok=True);fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with p.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def summary(rows,c):
 r0=rows[0];post=[r for r in rows if 401<=int(r['t'])<=600];acc=int(float(r0.get('provenance_accepted',0) or 0));ab=int(float(r0.get('provenance_abstain',0) or 0));correct=int(str(r0.get('posterior_deploy_hypothesis',''))=='H_ab') if acc else 0
 out={'seed':int(r0['seed']),'label':c['label'],'noise_family':c['noise_family'],'gain':c['gain'],'noise_scale':c['noise_scale'],'strategy':r0['strategy'],'coverage':acc,'correct':correct,'wrong_accept':int(acc and not correct),'abstain':ab,'operational_loss_401_600':sum(float(r['sq_error']) for r in post),'causal_violation_count':sum(int(float(r.get('context_removed_suspect_veto',0) or 0)) and not (int(float(r.get('context_vote_t',0) or 0))==1 and int(float(r.get('triad_primary_bad',0) or 0))==0) for r in rows),'triad_veto_adapt_violations':sum(1 for r in rows if int(float(r.get('adapt',0) or 0)) and int(float(r.get('triad_primary_bad',0) or 0)))}
 if r0['strategy']==SIGNED_RANK_30_STRATEGY:
  for k,v in r0.items():
   if str(k).startswith('rank55_'):out[k]=v
 if r0['strategy']==SIGNED_RANK_STRATEGY:
  for k in ('rank51_candidate','rank51_wplus','rank51_e_final'):out[k]=r0.get(k,'')
 if r0['strategy']==FAMILY_MIXTURE_STRATEGY:
  for k in ('mix54_candidate','mix54_bf','mix54_e_final'):out[k]=r0.get(k,'')
 if r0['strategy']==PAIR_SIGN_STRATEGY:
  out['sign49_candidate']=r0.get('sign49_candidate','');out['sign49_e_final']=r0.get('sign49_e_final','')
 return out
def wilson_upper(k,n):
 p=k/n;den=1+Z*Z/n;center=(p+Z*Z/(2*n))/den;rad=Z*math.sqrt(p*(1-p)/n+Z*Z/(4*n*n))/den;return min(1.,center+rad)
def rates(q):
 a=[x for x in q if int(float(x['coverage']))];w=sum(int(float(x['wrong_accept'])) for x in q);cor=sum(int(float(x['correct'])) for x in a);return {'coverage':len(a)/len(q),'accepted_n':len(a),'wrong_n':w,'wrong_acceptance':w/len(q),'wrong_wilson_upper_95':wilson_upper(w,len(q)),'precision':cor/len(a) if a else None}
def avg(q,k):return sum(float(x[k]) for x in q)/len(q)
def exact_tail(cutoff):
 counts=[0]*466;counts[0]=1
 for rank in range(1,31):
  for s in range(465,rank-1,-1):counts[s]+=counts[s-rank]
 return sum(counts[cutoff:]),2**30
def _stress_values(kind,seed):
 rng=random.Random(seed)
 if kind=='M1':
  s=(.75,1.,1.25,1.5,1.75);return [rng.gauss(0,s[i//6]) for i in range(30)]
 if kind=='M2':return [rng.gauss(0,1.0 if (i%6)<3 else 1.5) for i in range(30)]
 if kind=='M3':
  rho=.30;x=rng.gauss(0,1);o=[x]
  for _ in range(29):x=rho*x+math.sqrt(1-rho*rho)*rng.gauss(0,1);o.append(x)
  return o
 if kind=='M4':return [rng.gauss(.5 if rng.random()<.10 else 0,1) for _ in range(30)]
 raise ValueError(kind)
def stress_panel():
 out={}
 for k,(start,d) in STRESS.items():
  wrong=ties=zeros=0
  for seed in range(start,start+1000):
   v=_stress_values(k,seed);zeros+=sum(x==0 for x in v);ties+=30-len(set(abs(x) for x in v));w,_=signed_rank_statistic_30(v);wrong+=int(w>=W_CUTOFF)
  up=wilson_upper(wrong,1000);out[k]={'seed_range':[start,start+999],'description':d,'wrong_n':wrong,'wrong_acceptance':wrong/1000,'wrong_wilson_upper_95':up,'outside_demonstrated_1pct_robustness':up>.01,'zero_count':zeros,'absolute_tie_count':ties}
 return out
def _split_ok(x):
 for r in range(1,6):
  bd=str(x.get(f'rank55_baseline_discovery_r{r}','')).split(',');bc=str(x.get(f'rank55_baseline_confirmation_r{r}','')).split(',')
  if len(bd)!=1 or len(bc)!=3 or set(bd)&set(bc):return False
  used=set(bd+bc)
  if len(used)!=4:return False
  for tgt in 'abc':
   td=str(x.get(f'rank55_target_discovery_r{r}_{tgt}','')).split(',');tc=str(x.get(f'rank55_target_confirmation_r{r}_{tgt}','')).split(',')
   if len(td)!=2 or len(tc)!=3 or set(td)&set(tc) or len(set(td+tc))!=5:return False
 return True
def _rank_ok(x):
 vals=[float(x[f'rank55_pair_response_r{r}_{k}']) for r in range(1,6) for k in range(1,7)]
 if len(vals)!=30 or any(v==0 for v in vals) or len(set(abs(v) for v in vals))!=30:return False
 w,ranks=signed_rank_statistic_30(vals)
 if w!=int(float(x.get('rank55_wplus',-1))):return False
 if any(int(float(x.get(f'rank55_rank_{i}',-1)))!=ranks[i-1] for i in range(1,31)):return False
 accepted=w>=W_CUTOFF
 return int(float(x['coverage']))==int(accepted) and abs(float(x.get('rank55_e_final',0))-(ACCEPT_E if accepted else 0.0))<1e-12
def report_from(rows):
 H={f'H{i}':True for i in range(1,17)};cells={};cov=[];cross=[];cross53=[];disc_delta=[];conf_delta=[];zero=tie=0
 t345=exact_tail(345);t344=exact_tail(344)
 if t345!=(P345_NUMERATOR,P345_DENOMINATOR) or t344!=(P344_NUMERATOR,P344_DENOMINATOR) or P345>.01 or P344<=.01 or W_CUTOFF!=345 or ACCEPT_E<100:H['H4']=False
 for c in CELLS:
  sr=[r for r in rows if r['label']==c['label']];by={(int(r['seed']),r['strategy']):r for r in sr};qs={st:[by[(s,st)] for s in SEEDS] for st in STRATEGIES};rr={st:rates(qs[st]) for st in STRATEGIES};N=rr[SIGNED_RANK_30_STRATEGY];R=rr[SIGNED_RANK_STRATEGY];cov.append(N['coverage'])
  cand=[x for x in qs[SIGNED_RANK_30_STRATEGY] if x.get('rank55_candidate')=='H_ab'];cr=sum(int(float(x.get('rank55_wplus',0)))>=W_CUTOFF for x in cand)/len(cand) if cand else 0;cross.append(cr)
  rc=[x for x in qs[SIGNED_RANK_STRATEGY] if x.get('rank51_candidate')=='H_ab'];rcr=sum(float(x.get('rank51_e_final',0))>=E_THRESHOLD for x in rc)/len(rc) if rc else 0;cross53.append(rcr)
  disc=len(cand)/1000;disc53=len(rc)/1000;disc_delta.append(disc-disc53);conf_delta.append(cr-rcr)
  for x in qs[SIGNED_RANK_30_STRATEGY]:
   zero+=int(float(x.get('rank55_zero_count',0) or 0));tie+=int(float(x.get('rank55_abs_tie_count',0) or 0))
   if not _split_ok(x):H['H1']=False
   if int(float(x.get('rank55_contrast_count',0)))!=30 or int(float(x.get('rank55_spec_issue',0)))!=190:H['H2']=False;H['H16']=False
   if not _rank_ok(x):H['H3']=False
  if N['wrong_wilson_upper_95']>.01:H['H5']=False
  if N['accepted_n'] and (N['precision'] or 0)<.99:H['H6']=False
  if float(c['noise_scale'])==1 and N['coverage']<(.70 if float(c['gain'])==.5 else .60):H['H7']=False
  if c['label']=='gaussian_g0.500_n1.50' and N['coverage']<.50:H['H8']=False
  if c['label']=='gaussian_g0.425_n1.50' and N['coverage']<.40:H['H8']=False
  if disc<(.90 if float(c['noise_scale'])==1 else .80):H['H9']=False
  if N['coverage']<R['coverage']-.02:H['H10']=False
  losses={st:avg(qs[st],'operational_loss_401_600') for st in STRATEGIES}
  if losses[SIGNED_RANK_30_STRATEGY]>losses[TRIAD]+.20:H['H13']=False
  if sum(int(float(x['causal_violation_count']))+int(float(x['triad_veto_adapt_violations'])) for x in qs[SIGNED_RANK_30_STRATEGY]):H['H14']=False
  cells[c['label']]={'rank55':N,'signed_rank53':R,'discovery_hab':disc,'discovery_hab_53':disc53,'discovery_change':disc-disc53,'confirmation_crossing':cr,'confirmation_crossing_53':rcr,'confirmation_change':cr-rcr,'operational_loss':losses[SIGNED_RANK_30_STRATEGY],'triad_loss':losses[TRIAD]}
 mean_cov=sum(cov)/len(cov);mean_cross=sum(cross)/len(cross);mean_cross53=sum(cross53)/len(cross53)
 if mean_cov<.3073125 or mean_cross<=mean_cross53:H['H10']=False
 H['H11']=len(disc_delta)==16 and len(conf_delta)==16
 if mean_cov<.326125:H['H12']=False
 stress=stress_panel();H['H15']=all(set(v)>=set(('wrong_acceptance','wrong_wilson_upper_95','outside_demonstrated_1pct_robustness')) for v in stress.values())
 return {'experiment':55,'evaluation_seeds':[55000,55999],'n_seeds_per_cell':1000,'cell_count':16,'strategies':list(STRATEGIES),'audit_seeds':sorted(AUDIT),'bootstrap_seed':55055,'bootstrap_resamples':10000,'operative_spec_issue':190,'hypotheses':H,'all_hypotheses_pass':all(H.values()),'mean_primary_coverage':mean_cov,'experiment053_reference_mean_coverage':EXP053_MEAN_COVERAGE,'coverage_improvement_over_experiment053':mean_cov-EXP053_MEAN_COVERAGE,'experiment050_reference_mean_coverage':EXP050_MEAN_COVERAGE,'aggregate_confirmation_crossing':mean_cross,'experiment053_aggregate_confirmation_crossing':mean_cross53,'mean_discovery_change_vs_experiment053':sum(disc_delta)/len(disc_delta),'mean_confirmation_change_vs_experiment053':sum(conf_delta)/len(conf_delta),'primary_zero_count':zero,'primary_absolute_tie_count':tie,'stress_panel':stress,'exact_boundary':{'w_cutoff':W_CUTOFF,'tail_345':[t345[0],t345[1],t345[0]/t345[1]],'tail_344':[t344[0],t344[1],t344[0]/t344[1]]},'e_threshold':E_THRESHOLD,'accept_e':ACCEPT_E,'resource_accounting':'same total observations/probe exposure as Experiment 053; baseline allocation changed 2/2 to 1/3 and target remains 2/3; 30 disjoint confirmation contrasts','full_five_round_latency':True,'no_tuning':True,'cells':cells}
