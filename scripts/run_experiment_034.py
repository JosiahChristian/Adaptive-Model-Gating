#!/usr/bin/env python3
from __future__ import annotations
import csv,json,math,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from adaptive_model_gating import BASELINE_A,paired_bootstrap_ci
from experiment_029 import POSTERIOR_RISK_STRATEGY,TRIAD,ACCEPT_THRESHOLD,WRONG_COST,FALLBACK_COST
from experiment_032 import COMPOSED_STRATEGY
from experiment_034 import CELLS,STRATEGIES,run_experiment_034_strategy
from run_experiment_021 import calibrations

SEEDS=range(34000,34500);AUDIT=set(range(34000,34005));BOOTSTRAP_SEED=34034;Z=1.6448536269514722

def write_csv(p,rows):
 p.parent.mkdir(parents=True,exist_ok=True);fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with p.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def _num(row,key,default=0):
 v=row.get(key,default)
 if v is None or v=='': v=default
 return float(v)

def summary(rows,c,comparator_rows=None):
 r0=rows[0];post=[r for r in rows if 401<=int(r['t'])<=600]
 accepted=int(_num(r0,'provenance_accepted',0));abstain=int(_num(r0,'provenance_abstain',0));correct=int(_num(r0,'experiment034_explicit_topology_correct',0)) if accepted else 0
 target=BASELINE_A+float(c['magnitude']) if c['family']=='drift_ab_fault' else BASELINE_A
 causal=0
 for r in rows:
  if int(_num(r,'context_removed_suspect_veto',0)):
   valid=(int(_num(r,'context_vote_t',0))==1 and int(_num(r,'provenance_suspect_original',0))==1 and int(_num(r,'provenance_suspect_effective',1))==0 and int(_num(r,'triad_primary_bad',0))==0 and int(_num(r,'adapt',0))==1)
   if not valid:causal+=1
 changed=0
 if comparator_rows is not None:
  by={int(x['t']):x for x in comparator_rows};changed=sum(int(_num(r,'adapt',0))!=int(_num(by[int(r['t'])],'adapt',0)) for r in rows)
 return {'seed':int(r0['seed']),'label':c['label'],'topology_truth':c['topology'],'strategy':r0['strategy'],'coverage':accepted,'correct':correct,'wrong_accept':int(accepted and not correct),'abstain':abstain,
         'deploy_hypothesis':str(r0.get('posterior_deploy_hypothesis','')),'posterior_at_deployment':_num(r0,'posterior_at_deployment',0),'stop_round':int(_num(r0,'probe_stop_round',0)),'probe_energy':_num(r0,'probe_energy',0),
         'operational_loss_401_600':sum(float(r['sq_error']) for r in post),'final_slope_error_abs':abs(float(rows[-1]['slope_after'])-target),'adapt_signature':','.join(str(r['t']) for r in rows if int(_num(r,'adapt',0))),
         'context_vote_fraction_401_600':sum(int(_num(r,'context_vote_t',0)) for r in post)/len(post),'context_removed_count':sum(int(_num(r,'context_removed_suspect_veto',0)) for r in rows),
         'changed_adapt_count_vs_029':changed,'causal_violation_count':causal,'triad_veto_adapt_violations':sum(1 for r in rows if int(_num(r,'adapt',0)) and int(_num(r,'triad_primary_bad',0)))}

def wilson_upper(k,n):
 p=k/n;den=1+Z*Z/n;center=(p+Z*Z/(2*n))/den;rad=Z*math.sqrt(p*(1-p)/n+Z*Z/(4*n*n))/den;return min(1.,center+rad)
def rates(q):
 acc=[x for x in q if int(float(x['coverage']))];wrong=sum(int(float(x['wrong_accept'])) for x in q);correct=sum(int(float(x['correct'])) for x in acc)
 return {'coverage':len(acc)/len(q),'accepted_n':len(acc),'wrong_n':wrong,'wrong_acceptance':wrong/len(q),'wrong_wilson_upper_95':wilson_upper(wrong,len(q)),'precision':correct/len(acc) if acc else None}
def avg(q,k):return sum(float(x[k]) for x in q)/len(q)
def ci(v):return list(paired_bootstrap_ci(v,seed=BOOTSTRAP_SEED,reps=10000))
def paired(by,a,b,k):return [float(by[(s,a)][k])-float(by[(s,b)][k]) for s in SEEDS]

def report_from(rows,vals):
 H={f'H{i}':True for i in range(1,12)};out={};bycell={}
 for c in CELLS:
  cr=[r for r in rows if r['label']==c['label']];by={(int(r['seed']),r['strategy']):r for r in cr};qs={st:[by[(s,st)] for s in SEEDS] for st in STRATEGIES};rr={st:rates(qs[st]) for st in STRATEGIES};bycell[c['label']]=(c,by,qs,rr)
  for s in SEEDS:
   a,b=by[(s,COMPOSED_STRATEGY)],by[(s,POSTERIOR_RISK_STRATEGY)]
   if any(a[k]!=b[k] for k in ('coverage','abstain','stop_round','deploy_hypothesis')) or abs(float(a['posterior_at_deployment'])-float(b['posterior_at_deployment']))>1e-12 or abs(float(a['probe_energy'])-float(b['probe_energy']))>1e-12:H['H11']=False
  if rr[COMPOSED_STRATEGY]['wrong_wilson_upper_95']>.01:H['H1']=False
  lab=c['label']
  if lab.endswith('g0.500_n1.00') and (rr[COMPOSED_STRATEGY]['coverage']<.95 or (rr[COMPOSED_STRATEGY]['precision'] or 0)<.99):H['H2']=False
  if lab.endswith('g0.500_n1.50') and (rr[COMPOSED_STRATEGY]['coverage']<.80 or (rr[COMPOSED_STRATEGY]['precision'] or 0)<.99):H['H3']=False
  if lab.endswith('g0.425_n1.00') and (rr[COMPOSED_STRATEGY]['coverage']<.85 or (rr[COMPOSED_STRATEGY]['precision'] or 0)<.99):H['H3']=False
  if 'timing_p35_n1.50' in lab and (rr[COMPOSED_STRATEGY]['coverage']<.80 or (rr[COMPOSED_STRATEGY]['precision'] or 0)<.99):H['H4']=False
  if lab.endswith('_healthy') and (rr[COMPOSED_STRATEGY]['coverage']<.95 or (rr[COMPOSED_STRATEGY]['precision'] or 0)<.99):H['H5']=False
  losses={st:avg(qs[st],'operational_loss_401_600') for st in STRATEGIES};d32t=paired(by,COMPOSED_STRATEGY,TRIAD,'operational_loss_401_600');d29t=paired(by,POSTERIOR_RISK_STRATEGY,TRIAD,'operational_loss_401_600');ex32=sum(d32t)/500;ex29=sum(d29t)/500;red=((ex29-ex32)/ex29 if ex29>0 else None)
  if 'common_mode_0.50' in lab and (ex32>2.0 or (ex29>0 and (red is None or red<.80))):H['H6']=False
  if 'common_mode_1.00' in lab and (ex32>35.0 or (ex29>0 and (red is None or red<.80))):H['H6']=False
  if c['family']!='common_mode' and losses[COMPOSED_STRATEGY]>losses[POSTERIOR_RISK_STRATEGY]+.05:H['H8']=False
  if sum(int(float(x['causal_violation_count'])) for x in qs[COMPOSED_STRATEGY]) or sum(int(float(x['triad_veto_adapt_violations'])) for x in qs[COMPOSED_STRATEGY]):H['H9']=False
  fb=0
  for s in SEEDS:
   a,t=by[(s,COMPOSED_STRATEGY)],by[(s,TRIAD)]
   if int(float(a['abstain'])) and (a['adapt_signature']!=t['adapt_signature'] or abs(float(a['operational_loss_401_600'])-float(t['operational_loss_401_600']))>1e-12):fb+=1
  if fb:H['H10']=False
  out[lab]={'cell':c,'rates':rr,'mean_operational_loss_401_600':losses,'mean_final_slope_error_abs':{st:avg(qs[st],'final_slope_error_abs') for st in STRATEGIES},'mean_probe_energy':{st:avg(qs[st],'probe_energy') for st in STRATEGIES},'mean_context_vote_fraction_401_600':avg(qs[COMPOSED_STRATEGY],'context_vote_fraction_401_600'),'mean_context_removed_count':avg(qs[COMPOSED_STRATEGY],'context_removed_count'),'paired_loss_vs_triad_mean':ex32,'paired_loss_vs_triad_ci':ci(d32t),'experiment029_excess_vs_triad_mean':ex29,'fraction_excess_reduction_vs_029':red,'fallback_exact_mismatches':fb}
 for suffix in ('g0.500_n1.00','g0.500_n1.50','g0.425_n1.00','g0.400_n1.40','g0.350_n1.25','timing_p35_n1.50','healthy','common_mode_0.50','common_mode_1.00'):
  ca,ba,qa,ra=bycell['ac_'+suffix];cb,bb,qb,rb=bycell['bc_'+suffix]
  A=ra[COMPOSED_STRATEGY];B=rb[COMPOSED_STRATEGY]
  tol_loss=1.0 if 'common_mode' in suffix else .10
  if abs(A['coverage']-B['coverage'])>.05 or abs(A['wrong_acceptance']-B['wrong_acceptance'])>.005 or abs(avg(qa[COMPOSED_STRATEGY],'operational_loss_401_600')-avg(qb[COMPOSED_STRATEGY],'operational_loss_401_600'))>tol_loss:H['H7']=False
 H['H11']=bool(H['H11'] and ACCEPT_THRESHOLD==.99 and WRONG_COST==100.0 and FALLBACK_COST==1.0 and all(r.get('topology_truth') in ('H_ac','H_bc') for r in rows))
 return {'evaluation_seeds':[34000,34499],'n_seeds_per_cell':500,'cell_count':18,'strategies':STRATEGIES,'audit_seeds':sorted(AUDIT),'bootstrap_seed':BOOTSTRAP_SEED,'bootstrap_resamples':10000,'hypotheses':H,'accept_threshold':ACCEPT_THRESHOLD,'wrong_action_cost':WRONG_COST,'fallback_cost':FALLBACK_COST,'explicit_topology_truth':True,'no_recalibration':True,'code_commit':os.environ.get('GITHUB_SHA','unknown'),'cells':out}

def calibration_values():return calibrations()
