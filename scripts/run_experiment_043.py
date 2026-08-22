#!/usr/bin/env python3
import csv,json,math,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from adaptive_model_gating import BASELINE_A
from experiment_029 import ACCEPT_THRESHOLD,WRONG_COST,FALLBACK_COST,TRIAD
from experiment_032 import COMPOSED_STRATEGY
from experiment_036 import ROBUST_STRATEGY
from experiment_037 import MODEL_AVERAGED_STRATEGY
from experiment_039 import RADIAL_HUBER_STRATEGY
from experiment_040 import LOCAL_MIXTURE_STRATEGY
from experiment_041 import LOCAL_CAUCHY_STRATEGY
from experiment_042 import LOCAL_GAUSSIAN_GROSS_STRATEGY
from experiment_043 import REPLICATED_GAUSSIAN_STRATEGY,CONFIRMATIONS_REQUIRED,STRATEGIES,CELLS,run_experiment_043_strategy,evaluate_gaussian_posterior
from run_experiment_021 import calibrations
SEEDS=range(43000,44000);AUDIT=set(range(43000,43005));Z=1.6448536269514722
VULNERABLE_035={'contaminated_gaussian_g0.425_n1.00','contaminated_gaussian_g0.425_n1.50','contaminated_gaussian_g0.500_n1.00','contaminated_gaussian_g0.500_n1.50','student_t3_g0.425_n1.00','student_t3_g0.425_n1.50','student_t3_g0.500_n1.00','student_t3_g0.500_n1.50','laplace_g0.425_n1.50'}
HIGH_GAUSS={'gaussian_g0.500_n1.50','gaussian_g0.425_n1.50'}
def write_csv(p,rows):
 p.parent.mkdir(parents=True,exist_ok=True);fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with p.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def summary(rows,c):
 r0=rows[0];post=[r for r in rows if 401<=int(r['t'])<=600];accepted=int(float(r0.get('provenance_accepted',0) or 0));abstain=int(float(r0.get('provenance_abstain',0) or 0));correct=int(str(r0.get('posterior_deploy_hypothesis',''))=='H_ab') if accepted else 0;causal=0
 for r in rows:
  if int(float(r.get('context_removed_suspect_veto',0) or 0)):
   eff=r.get('provenance_suspect_effective',1);eff=int(float(eff)) if eff not in ('',None) else 1
   valid=(int(float(r.get('context_vote_t',0) or 0))==1 and int(float(r.get('provenance_suspect_original',0) or 0))==1 and eff==0 and int(float(r.get('triad_primary_bad',0) or 0))==0 and int(float(r.get('adapt',0) or 0))==1)
   if not valid:causal+=1
 out={'seed':int(r0['seed']),'label':c['label'],'noise_family':c['noise_family'],'gain':c['gain'],'noise_scale':c['noise_scale'],'strategy':r0['strategy'],'coverage':accepted,'correct':correct,'wrong_accept':int(accepted and not correct),'abstain':abstain,'deploy_hypothesis':str(r0.get('posterior_deploy_hypothesis','')),'posterior_at_deployment':float(r0.get('posterior_at_deployment',0) or 0),'stop_round':int(float(r0.get('probe_stop_round',0) or 0)),'probe_energy':float(r0.get('probe_energy',0) or 0),'operational_loss_401_600':sum(float(r['sq_error']) for r in post),'final_slope_error_abs':abs(float(rows[-1]['slope_after'])-(BASELINE_A+0.50)),'adapt_signature':','.join(str(r['t']) for r in rows if int(float(r.get('adapt',0) or 0))),'causal_violation_count':causal,'triad_veto_adapt_violations':sum(1 for r in rows if int(float(r.get('adapt',0) or 0)) and int(float(r.get('triad_primary_bad',0) or 0)))}
 if r0['strategy']==REPLICATED_GAUSSIAN_STRATEGY:
  out.update({'replication_confirmations_required':int(float(r0.get('replication_confirmations_required',0) or 0)),'replication_confirmed':int(float(r0.get('replication_confirmed',0) or 0)),'replication_resets_total':int(float(r0.get('replication_resets_total',0) or 0)),'replication_previous_candidate':str(r0.get('replication_previous_candidate','')),'replication_previous_posterior':float(r0.get('replication_previous_posterior',0) or 0),'replication_accept_candidate':str(r0.get('replication_accept_candidate','')),'replication_accept_posterior':float(r0.get('replication_accept_posterior',0) or 0)})
 return out
def wilson_upper(k,n):
 p=k/n;den=1+Z*Z/n;center=(p+Z*Z/(2*n))/den;rad=Z*math.sqrt(p*(1-p)/n+Z*Z/(4*n*n))/den;return min(1.,center+rad)
def rates(q):
 acc=[x for x in q if int(float(x['coverage']))];wrong=sum(int(float(x['wrong_accept'])) for x in q);correct=sum(int(float(x['correct'])) for x in acc)
 return {'coverage':len(acc)/len(q),'accepted_n':len(acc),'wrong_n':wrong,'wrong_acceptance':wrong/len(q),'wrong_wilson_upper_95':wilson_upper(wrong,len(q)),'precision':correct/len(acc) if acc else None}
def avg(q,k):return sum(float(x[k]) for x in q)/len(q)
def report_from(rows,posterior_rows):
 H={f'H{i}':True for i in range(1,13)};out={}
 for c in CELLS:
  sr=[r for r in rows if r['label']==c['label']];by={(int(r['seed']),r['strategy']):r for r in sr};qs={st:[by[(s,st)] for s in SEEDS] for st in STRATEGIES};rr={st:rates(qs[st]) for st in STRATEGIES}
  for r in posterior_rows:
   if r['label']!=c['label']:continue
   ps=[float(r['P_'+h]) for h in ('H_ab','H_ac','H_bc','H_null')]
   if any((not math.isfinite(p) or p<0 or p>1) for p in ps) or abs(sum(ps)-1)>1e-9:H['H1']=False
  C,G,T=rr[REPLICATED_GAUSSIAN_STRATEGY],rr[COMPOSED_STRATEGY],rr[ROBUST_STRATEGY]
  if C['wrong_wilson_upper_95']>.01:H['H2']=False
  if (C['precision'] or 0)<.99:H['H3']=False
  if float(c['noise_scale'])==1.0:
   req=.90 if float(c['gain'])==.50 else .85
   if C['coverage']<req:H['H4']=False
  losses={st:avg(qs[st],'operational_loss_401_600') for st in STRATEGIES}
  if c['noise_family']=='gaussian' and (C['coverage']<G['coverage']-.03 or losses[REPLICATED_GAUSSIAN_STRATEGY]>losses[COMPOSED_STRATEGY]+.05):H['H5']=False
  if c['label'] in VULNERABLE_035:
   if C['wrong_wilson_upper_95']>.01 or (C['precision'] or 0)<.99 or C['wrong_acceptance']>G['wrong_acceptance']:H['H6']=False
   base_wrong={int(x['seed']) for x in qs[COMPOSED_STRATEGY] if int(float(x['wrong_accept']))}
   if base_wrong:
    cand_wrong_on_base=sum(1 for x in qs[REPLICATED_GAUSSIAN_STRATEGY] if int(x['seed']) in base_wrong and int(float(x['wrong_accept'])))
    if cand_wrong_on_base>0.5*len(base_wrong) or C['coverage']<G['coverage']-.05:H['H7']=False
  if c['label']=='gaussian_g0.500_n1.50' and (C['coverage']<.90 or C['wrong_wilson_upper_95']>.01 or (C['precision'] or 0)<.99):H['H8']=False
  if c['label']=='gaussian_g0.425_n1.50' and (C['coverage']<.80 or C['wrong_wilson_upper_95']>.01 or (C['precision'] or 0)<.99):H['H8']=False
  if losses[REPLICATED_GAUSSIAN_STRATEGY]>losses[TRIAD]+.20:H['H9']=False
  fb=0
  if sum(int(float(x['causal_violation_count'])) for x in qs[REPLICATED_GAUSSIAN_STRATEGY]) or sum(int(float(x['triad_veto_adapt_violations'])) for x in qs[REPLICATED_GAUSSIAN_STRATEGY]):H['H10']=False
  for s in SEEDS:
   a,t=by[(s,REPLICATED_GAUSSIAN_STRATEGY)],by[(s,TRIAD)]
   if int(float(a['abstain'])) and (a['adapt_signature']!=t['adapt_signature'] or abs(float(a['operational_loss_401_600'])-float(t['operational_loss_401_600']))>1e-12):fb+=1
   if int(float(a['coverage'])):
    integrity=(int(float(a.get('replication_confirmations_required',0)))==2 and int(float(a.get('replication_confirmed',0)))==1 and int(float(a['stop_round']))>=2 and a.get('replication_previous_candidate','')==a.get('replication_accept_candidate','')==a.get('deploy_hypothesis','') and float(a.get('replication_previous_posterior',0))>=ACCEPT_THRESHOLD and float(a.get('replication_accept_posterior',0))>=ACCEPT_THRESHOLD)
    if not integrity:H['H11']=False
  if fb:H['H10']=False
  out[c['label']]={'cell':c,'rates':rr,'mean_operational_loss_401_600':losses,'mean_probe_energy':{st:avg(qs[st],'probe_energy') for st in STRATEGIES},'fallback_exact_mismatches':fb,'paired_single_crossing_wrong_n':sum(int(float(x['wrong_accept'])) for x in qs[COMPOSED_STRATEGY]),'paired_replicated_wrong_n':sum(int(float(x['wrong_accept'])) for x in qs[REPLICATED_GAUSSIAN_STRATEGY])}
 H['H12']=bool(CONFIRMATIONS_REQUIRED==2 and ACCEPT_THRESHOLD==.99 and WRONG_COST==100.0 and FALLBACK_COST==1.0)
 return {'evaluation_seeds':[43000,43999],'n_seeds_per_cell':1000,'cell_count':16,'strategies':STRATEGIES,'audit_seeds':sorted(AUDIT),'bootstrap_seed':43043,'bootstrap_resamples':10000,'hypotheses':H,'accept_threshold':ACCEPT_THRESHOLD,'wrong_action_cost':WRONG_COST,'fallback_cost':FALLBACK_COST,'confirmations_required':CONFIRMATIONS_REQUIRED,'confirmation_rule':'same non-null Gaussian posterior candidate >=0.99 on two consecutive diagnostic stages','reset_rule':'different candidate or posterior <0.99 resets confirmation','likelihood':'exact frozen Experiment-028/032 Gaussian directed-covariance posterior; unchanged','context_rule':'Experiment-031 current-time causal context vote composed by Experiment-032','vulnerable_experiment035_cells':sorted(VULNERABLE_035),'high_noise_gaussian_retention_cells':sorted(HIGH_GAUSS),'no_tuning':True,'code_commit':os.environ.get('GITHUB_SHA','unknown'),'cells':out}
def calibration_values():return calibrations()
