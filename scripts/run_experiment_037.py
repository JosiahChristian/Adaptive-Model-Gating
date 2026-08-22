#!/usr/bin/env python3
import csv,json,math,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from adaptive_model_gating import BASELINE_A
from experiment_029 import ACCEPT_THRESHOLD,WRONG_COST,FALLBACK_COST,TRIAD
from experiment_032 import COMPOSED_STRATEGY
from experiment_036 import ROBUST_STRATEGY,NU,BETA_MAX,BETA_STEP
from experiment_037 import MODEL_AVERAGED_STRATEGY,STRATEGIES,CELLS,MODEL_PRIOR,run_experiment_037_strategy,evaluate_model_averaged_posterior
from run_experiment_021 import calibrations
SEEDS=range(37000,38000);AUDIT=set(range(37000,37005));Z=1.6448536269514722
VULNERABLE_035={'contaminated_gaussian_g0.425_n1.00','contaminated_gaussian_g0.425_n1.50','contaminated_gaussian_g0.500_n1.00','contaminated_gaussian_g0.500_n1.50','student_t3_g0.425_n1.00','student_t3_g0.425_n1.50','student_t3_g0.500_n1.00','student_t3_g0.500_n1.50','laplace_g0.425_n1.50'}
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
 return {'seed':int(r0['seed']),'label':c['label'],'noise_family':c['noise_family'],'gain':c['gain'],'noise_scale':c['noise_scale'],'strategy':r0['strategy'],'coverage':accepted,'correct':correct,'wrong_accept':int(accepted and not correct),'abstain':abstain,'deploy_hypothesis':str(r0.get('posterior_deploy_hypothesis','')),'posterior_at_deployment':float(r0.get('posterior_at_deployment',0) or 0),'stop_round':int(float(r0.get('probe_stop_round',0) or 0)),'probe_energy':float(r0.get('probe_energy',0) or 0),'operational_loss_401_600':sum(float(r['sq_error']) for r in post),'final_slope_error_abs':abs(float(rows[-1]['slope_after'])-(BASELINE_A+0.50)),'adapt_signature':','.join(str(r['t']) for r in rows if int(float(r.get('adapt',0) or 0))),'causal_violation_count':causal,'triad_veto_adapt_violations':sum(1 for r in rows if int(float(r.get('adapt',0) or 0)) and int(float(r.get('triad_primary_bad',0) or 0)))}
def wilson_upper(k,n):
 p=k/n;den=1+Z*Z/n;center=(p+Z*Z/(2*n))/den;rad=Z*math.sqrt(p*(1-p)/n+Z*Z/(4*n*n))/den;return min(1.,center+rad)
def rates(q):
 acc=[x for x in q if int(float(x['coverage']))];wrong=sum(int(float(x['wrong_accept'])) for x in q);correct=sum(int(float(x['correct'])) for x in acc)
 return {'coverage':len(acc)/len(q),'accepted_n':len(acc),'wrong_n':wrong,'wrong_acceptance':wrong/len(q),'wrong_wilson_upper_95':wilson_upper(wrong,len(q)),'precision':correct/len(acc) if acc else None}
def avg(q,k):return sum(float(x[k]) for x in q)/len(q)
def report_from(rows,posterior_rows):
 H={f'H{i}':True for i in range(1,11)};out={}
 for c in CELLS:
  sr=[r for r in rows if r['label']==c['label']];by={(int(r['seed']),r['strategy']):r for r in sr};qs={st:[by[(s,st)] for s in SEEDS] for st in STRATEGIES};rr={st:rates(qs[st]) for st in STRATEGIES}
  for r in posterior_rows:
   if r['label']!=c['label']:continue
   ps=[float(r['P_'+h]) for h in ('H_ab','H_ac','H_bc','H_null')]
   if any((not math.isfinite(p) or p<0 or p>1) for p in ps) or abs(sum(ps)-1)>1e-9:H['H1']=False
  M,G,T=rr[MODEL_AVERAGED_STRATEGY],rr[COMPOSED_STRATEGY],rr[ROBUST_STRATEGY]
  if M['wrong_wilson_upper_95']>.01:H['H2']=False
  if (M['precision'] or 0)<.99:H['H3']=False
  if float(c['noise_scale'])==1.0:
   req=.90 if float(c['gain'])==.50 else .85
   if M['coverage']<req:H['H4']=False
  losses={st:avg(qs[st],'operational_loss_401_600') for st in STRATEGIES}
  if c['noise_family']=='gaussian' and (M['coverage']<G['coverage']-.03 or losses[MODEL_AVERAGED_STRATEGY]>losses[COMPOSED_STRATEGY]+.05):H['H5']=False
  if c['noise_family']!='gaussian' and c['label'] in VULNERABLE_035:
   if M['wrong_wilson_upper_95']>.01 or (M['precision'] or 0)<.99 or M['wrong_acceptance']>T['wrong_acceptance']+.003:H['H6']=False
  if c['noise_family']=='gaussian' and c['label'] in ('gaussian_g0.500_n1.50','gaussian_g0.425_n1.50') and M['coverage']<T['coverage']+.08:H['H7']=False
  if losses[MODEL_AVERAGED_STRATEGY]>losses[TRIAD]+.20:H['H8']=False
  fb=0
  if sum(int(float(x['causal_violation_count'])) for x in qs[MODEL_AVERAGED_STRATEGY]) or sum(int(float(x['triad_veto_adapt_violations'])) for x in qs[MODEL_AVERAGED_STRATEGY]):H['H9']=False
  for s in SEEDS:
   a,t=by[(s,MODEL_AVERAGED_STRATEGY)],by[(s,TRIAD)]
   if int(float(a['abstain'])) and (a['adapt_signature']!=t['adapt_signature'] or abs(float(a['operational_loss_401_600'])-float(t['operational_loss_401_600']))>1e-12):fb+=1
  if fb:H['H9']=False
  out[c['label']]={'cell':c,'rates':rr,'mean_operational_loss_401_600':losses,'mean_probe_energy':{st:avg(qs[st],'probe_energy') for st in STRATEGIES},'fallback_exact_mismatches':fb}
 H['H10']=bool(MODEL_PRIOR=={'gaussian':.5,'student_t3':.5} and NU==3.0 and BETA_STEP==.01 and BETA_MAX==1.20 and ACCEPT_THRESHOLD==.99 and WRONG_COST==100.0 and FALLBACK_COST==1.0)
 return {'evaluation_seeds':[37000,37999],'n_seeds_per_cell':1000,'cell_count':16,'strategies':STRATEGIES,'audit_seeds':sorted(AUDIT),'bootstrap_seed':37037,'bootstrap_resamples':10000,'hypotheses':H,'accept_threshold':ACCEPT_THRESHOLD,'wrong_action_cost':WRONG_COST,'fallback_cost':FALLBACK_COST,'model_prior':MODEL_PRIOR,'likelihoods':'proper normalized Gaussian covariance Sigma and Student-t3 scatter Sigma/3; equal-prior Bayesian model averaging','amplitude_prior':'HalfNormal inherited BETA_SCALE; trapezoid beta grid 0..1.20 step 0.01','vulnerable_experiment035_cells':sorted(VULNERABLE_035),'no_tuning':True,'code_commit':os.environ.get('GITHUB_SHA','unknown'),'cells':out}
def calibration_values():return calibrations()
