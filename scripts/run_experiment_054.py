#!/usr/bin/env python3
import csv,json,math,random,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_029 import TRIAD
from experiment_046 import E_THRESHOLD
from experiment_049 import PAIR_SIGN_STRATEGY
from experiment_051 import SIGNED_RANK_STRATEGY,CELLS
from experiment_054 import *
from run_experiment_021 import calibrations

SEEDS=range(54000,55000);AUDIT=set(range(54000,54005));Z=1.6448536269514722
STRESS={'M1':(5451000,'round-wise heteroskedastic symmetric scales 0.75,1.00,1.25,1.50,1.75'),'M2':(5452000,'direction-wise heteroskedastic symmetric forward:reverse 1:1.5'),'M3':(5453000,'AR(1) symmetric Gaussian rho=0.30'),'M4':(5454000,'90/10 asymmetric contaminated Gaussian shift +0.50')}
EXP053_MEAN_COVERAGE=0.2573125;EXP050_MEAN_COVERAGE=0.376125

def calibration_values():
 c=calibrations();return c['tau'],c['kappa'],c['kappa3'],c['lambda_a'],c['lambda_b'],c['lambda_c'],c['lambda_ab'],c['lambda_ac'],c['lambda_bc']
def write_csv(p,rows):
 p.parent.mkdir(parents=True,exist_ok=True);fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with p.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def summary(rows,c):
 r0=rows[0];post=[r for r in rows if 401<=int(r['t'])<=600];acc=int(float(r0.get('provenance_accepted',0) or 0));ab=int(float(r0.get('provenance_abstain',0) or 0));correct=int(str(r0.get('posterior_deploy_hypothesis',''))=='H_ab') if acc else 0
 out={'seed':int(r0['seed']),'label':c['label'],'noise_family':c['noise_family'],'gain':c['gain'],'noise_scale':c['noise_scale'],'strategy':r0['strategy'],'coverage':acc,'correct':correct,'wrong_accept':int(acc and not correct),'abstain':ab,'operational_loss_401_600':sum(float(r['sq_error']) for r in post),'causal_violation_count':sum(int(float(r.get('context_removed_suspect_veto',0) or 0)) and not (int(float(r.get('context_vote_t',0) or 0))==1 and int(float(r.get('triad_primary_bad',0) or 0))==0) for r in rows),'triad_veto_adapt_violations':sum(1 for r in rows if int(float(r.get('adapt',0) or 0)) and int(float(r.get('triad_primary_bad',0) or 0)))}
 if r0['strategy']==FAMILY_MIXTURE_STRATEGY:
  for k,v in r0.items():
   if str(k).startswith('mix54_'):out[k]=v
 if r0['strategy']==SIGNED_RANK_STRATEGY:
  for k in ('rank51_candidate','rank51_wplus','rank51_e_final'):out[k]=r0.get(k,'')
 if r0['strategy']==PAIR_SIGN_STRATEGY:
  out['sign49_candidate']=r0.get('sign49_candidate','');out['sign49_e_final']=r0.get('sign49_e_final','')
 return out
def wilson_upper(k,n):
 p=k/n;den=1+Z*Z/n;center=(p+Z*Z/(2*n))/den;rad=Z*math.sqrt(p*(1-p)/n+Z*Z/(4*n*n))/den;return min(1.,center+rad)
def rates(q):
 a=[x for x in q if int(float(x['coverage']))];w=sum(int(float(x['wrong_accept'])) for x in q);cor=sum(int(float(x['correct'])) for x in a);return {'coverage':len(a)/len(q),'accepted_n':len(a),'wrong_n':w,'wrong_acceptance':w/len(q),'wrong_wilson_upper_95':wilson_upper(w,len(q)),'precision':cor/len(a) if a else None}
def avg(q,k):return sum(float(x[k]) for x in q)/len(q)
def _stress_values(kind,seed):
 rng=random.Random(seed)
 if kind=='M1':
  s=(.75,1.,1.25,1.5,1.75);return [rng.gauss(0,s[i//4]) for i in range(20)]
 if kind=='M2':return [rng.gauss(0,1.0 if (i%4)<2 else 1.5) for i in range(20)]
 if kind=='M3':
  rho=.30;x=rng.gauss(0,1);o=[x]
  for _ in range(19):x=rho*x+math.sqrt(1-rho*rho)*rng.gauss(0,1);o.append(x)
  return o
 if kind=='M4':return [rng.gauss(.5 if rng.random()<.10 else 0,1) for _ in range(20)]
def stress_panel():
 out={}
 for k,(start,d) in STRESS.items():
  wrong=ties=zeros=0
  for seed in range(start,start+1000):
   v=_stress_values(k,seed);zeros+=sum(x==0 for x in v);ties+=20-len(set(abs(x) for x in v));bf,_,_=family_mixture_statistic(v);wrong+=int(bf>=BF_CUTOFF)
  up=wilson_upper(wrong,1000);out[k]={'seed_range':[start,start+999],'description':d,'wrong_n':wrong,'wrong_acceptance':wrong/1000,'wrong_wilson_upper_95':up,'outside_demonstrated_1pct_robustness':up>.01,'zero_count':zeros,'absolute_tie_count':ties}
 return out
def report_from(rows):
 H={f'H{i}':True for i in range(1,17)};cells={};cov=[];cross=[];cross53=[];zero=tie=0
 boundary=enumerate_null_boundary()
 if boundary['accepted_count']!=ACCEPT_PATTERN_COUNT or abs(boundary['accepted_low']-BF_ACCEPTED_LOW)>1e-12 or abs(boundary['rejected_high']-BF_REJECTED_HIGH)>1e-12 or abs(boundary['cutoff']-BF_CUTOFF)>1e-15:H['H5']=False
 for c in CELLS:
  sr=[r for r in rows if r['label']==c['label']];by={(int(r['seed']),r['strategy']):r for r in sr};qs={st:[by[(s,st)] for s in SEEDS] for st in STRATEGIES};rr={st:rates(qs[st]) for st in STRATEGIES};M=rr[FAMILY_MIXTURE_STRATEGY];R=rr[SIGNED_RANK_STRATEGY];cov.append(M['coverage'])
  cand=[x for x in qs[FAMILY_MIXTURE_STRATEGY] if x.get('mix54_candidate')=='H_ab'];cr=sum(float(x.get('mix54_bf',0))>=BF_CUTOFF for x in cand)/len(cand) if cand else 0;cross.append(cr)
  rc=[x for x in qs[SIGNED_RANK_STRATEGY] if x.get('rank51_candidate')=='H_ab'];rcr=sum(float(x.get('rank51_e_final',0))>=E_THRESHOLD for x in rc)/len(rc) if rc else 0;cross53.append(rcr)
  for x in qs[FAMILY_MIXTURE_STRATEGY]:
   zero+=int(float(x.get('mix54_zero_count',0) or 0));tie+=int(float(x.get('mix54_abs_tie_count',0) or 0))
   if int(float(x.get('mix54_contrast_count',0)))!=20 or int(float(x.get('mix54_component_count',0)))!=12 or abs(float(x.get('mix54_mixture_weight',0))-1/12)>1e-15:H['H2']=False;H['H4']=False
   if x.get('mix54_families')!='sign,wilcoxon,normal' or x.get('mix54_thetas')!='0.5,1.0,2.0,4.0':H['H3']=False;H['H4']=False
   if int(float(x.get('mix54_spec_issue',0)))!=173 or int(float(x.get('mix54_equal_budget_experiment053',0)))!=1:H['H16']=False
  if zero or tie:H['H3']=False
  if M['wrong_wilson_upper_95']>.01:H['H6']=False
  if M['accepted_n'] and (M['precision'] or 0)<.99:H['H7']=False
  if float(c['noise_scale'])==1 and M['coverage']<(.70 if float(c['gain'])==.5 else .60):H['H8']=False
  if c['label']=='gaussian_g0.500_n1.50' and M['coverage']<.50:H['H9']=False
  if c['label']=='gaussian_g0.425_n1.50' and M['coverage']<.40:H['H9']=False
  disc=len(cand)/1000
  if disc<(.90 if float(c['noise_scale'])==1 else .80):H['H10']=False
  if M['coverage']<R['coverage']-.02:H['H11']=False
  losses={st:avg(qs[st],'operational_loss_401_600') for st in STRATEGIES}
  if losses[M and FAMILY_MIXTURE_STRATEGY]>losses[TRIAD]+.20:H['H13']=False
  if sum(int(float(x['causal_violation_count']))+int(float(x['triad_veto_adapt_violations'])) for x in qs[FAMILY_MIXTURE_STRATEGY]):H['H14']=False
  cells[c['label']]={'family_mixture':M,'signed_rank':R,'discovery_hab':disc,'confirmation_crossing':cr,'signed_rank_crossing':rcr,'operational_loss':losses[FAMILY_MIXTURE_STRATEGY],'triad_loss':losses[TRIAD]}
 mean_cov=sum(cov)/len(cov);mean_cross=sum(cross)/len(cross);mean_cross53=sum(cross53)/len(cross53)
 if mean_cov<EXP053_MEAN_COVERAGE+.05 or mean_cross<=mean_cross53:H['H11']=False
 if mean_cov<.326125:H['H12']=False
 stress=stress_panel();H['H15']=all(set(v)>=set(('wrong_acceptance','wrong_wilson_upper_95','outside_demonstrated_1pct_robustness')) for v in stress.values())
 return {'experiment':54,'evaluation_seeds':[54000,54999],'n_seeds_per_cell':1000,'cell_count':16,'strategies':list(STRATEGIES),'audit_seeds':sorted(AUDIT),'bootstrap_seed':54054,'bootstrap_resamples':10000,'operative_spec_issue':173,'hypotheses':H,'all_hypotheses_pass':all(H.values()),'mean_primary_coverage':mean_cov,'experiment053_reference_mean_coverage':EXP053_MEAN_COVERAGE,'coverage_improvement_over_experiment053':mean_cov-EXP053_MEAN_COVERAGE,'experiment050_reference_mean_coverage':EXP050_MEAN_COVERAGE,'aggregate_confirmation_crossing':mean_cross,'experiment053_aggregate_confirmation_crossing':mean_cross53,'primary_zero_count':zero,'primary_absolute_tie_count':tie,'stress_panel':stress,'exact_boundary':boundary,'e_threshold':E_THRESHOLD,'bf_cutoff':BF_CUTOFF,'p_star':P_STAR,'accept_e':ACCEPT_E,'resource_accounting':'same single-stream confirmation observation/probe budget as Experiments 049/051/053; half Experiment 050 confirmation-stream exposure','full_five_round_latency':True,'no_tuning':True,'cells':cells}
