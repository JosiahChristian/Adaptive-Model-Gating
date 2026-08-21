#!/usr/bin/env python3
from __future__ import annotations
import csv,json,math,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from adaptive_model_gating import BASELINE_A
from experiment_029 import POSTERIOR_RISK_STRATEGY,TRIAD,ACCEPT_THRESHOLD,WRONG_COST,FALLBACK_COST
from experiment_032 import COMPOSED_STRATEGY
from experiment_035 import CELLS,STRATEGIES,NOISE_FAMILIES,run_experiment_035_strategy,evaluate_experiment_035_posterior
from run_experiment_021 import calibrations

SEEDS=range(35000,36000);AUDIT=set(range(35000,35005));Z=1.6448536269514722

def write_csv(p,rows):
 p.parent.mkdir(parents=True,exist_ok=True);fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with p.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def summary(rows,c):
 r0=rows[0];post=[r for r in rows if 401<=int(r['t'])<=600];accepted=int(float(r0.get('provenance_accepted',0) or 0));abstain=int(float(r0.get('provenance_abstain',0) or 0));correct=int(str(r0.get('posterior_deploy_hypothesis',''))=='H_ab') if accepted else 0
 causal=0
 for r in rows:
  if int(float(r.get('context_removed_suspect_veto',0) or 0)):
   eff=r.get('provenance_suspect_effective',1);eff=int(float(eff)) if eff not in ('',None) else 1
   valid=(int(float(r.get('context_vote_t',0) or 0))==1 and int(float(r.get('provenance_suspect_original',0) or 0))==1 and eff==0 and int(float(r.get('triad_primary_bad',0) or 0))==0 and int(float(r.get('adapt',0) or 0))==1)
   if not valid:causal+=1
 return {'seed':int(r0['seed']),'label':c['label'],'noise_family':c['noise_family'],'gain':c['gain'],'noise_scale':c['noise_scale'],'strategy':r0['strategy'],
         'coverage':accepted,'correct':correct,'wrong_accept':int(accepted and not correct),'abstain':abstain,'deploy_hypothesis':str(r0.get('posterior_deploy_hypothesis','')),
         'posterior_at_deployment':float(r0.get('posterior_at_deployment',0) or 0),'stop_round':int(float(r0.get('probe_stop_round',0) or 0)),'probe_energy':float(r0.get('probe_energy',0) or 0),
         'operational_loss_401_600':sum(float(r['sq_error']) for r in post),'final_slope_error_abs':abs(float(rows[-1]['slope_after'])-(BASELINE_A+0.50)),
         'adapt_signature':','.join(str(r['t']) for r in rows if int(float(r.get('adapt',0) or 0))),'causal_violation_count':causal,
         'triad_veto_adapt_violations':sum(1 for r in rows if int(float(r.get('adapt',0) or 0)) and int(float(r.get('triad_primary_bad',0) or 0)))}

def wilson_upper(k,n):
 p=k/n;den=1+Z*Z/n;center=(p+Z*Z/(2*n))/den;rad=Z*math.sqrt(p*(1-p)/n+Z*Z/(4*n*n))/den;return min(1.,center+rad)
def rates(q):
 acc=[x for x in q if int(float(x['coverage']))];wrong=sum(int(float(x['wrong_accept'])) for x in q);correct=sum(int(float(x['correct'])) for x in acc)
 return {'coverage':len(acc)/len(q),'accepted_n':len(acc),'wrong_n':wrong,'wrong_acceptance':wrong/len(q),'wrong_wilson_upper_95':wilson_upper(wrong,len(q)),'precision':correct/len(acc) if acc else None}
def avg(q,k):return sum(float(x[k]) for x in q)/len(q)

def calibration_metrics(q):
 n=len(q);truth='H_ab';brier=0.;logloss=0.;correct=0;bins=[[] for _ in range(10)]
 for r in q:
  probs={h:float(r['P_'+h]) for h in ('H_ab','H_ac','H_bc','H_null')};brier+=sum((probs[h]-(1.0 if h==truth else 0.0))**2 for h in probs);p=max(probs[truth],1e-300);logloss-=math.log(p);ok=int(r['top_hypothesis']==truth);correct+=ok;conf=float(r['top_probability']);bins[min(9,int(conf*10))].append((conf,ok))
 ece=0.
 for b in bins:
  if b:ece+=(len(b)/n)*abs(sum(x for x,_ in b)/len(b)-sum(y for _,y in b)/len(b))
 return {'brier':brier/n,'log_loss':logloss/n,'top_accuracy':correct/n,'ece':ece,'mean_entropy':avg(q,'entropy')}

def report_from(summary_rows,posterior_rows):
 H={f'H{i}':True for i in range(1,11)};out={}
 for c in CELLS:
  sr=[r for r in summary_rows if r['label']==c['label']];by={(int(r['seed']),r['strategy']):r for r in sr};qs={st:[by[(s,st)] for s in SEEDS] for st in STRATEGIES};rr={st:rates(qs[st]) for st in STRATEGIES}
  pr=[r for r in posterior_rows if r['label']==c['label'] and int(float(r['stage']))==5];cm=calibration_metrics(pr)
  # H1 validity across all stages.
  for r in posterior_rows:
   if r['label']!=c['label']:continue
   ps=[float(r['P_'+h]) for h in ('H_ab','H_ac','H_bc','H_null')]
   if any((not math.isfinite(p) or p<0 or p>1) for p in ps) or abs(sum(ps)-1.0)>1e-9:H['H1']=False
  if rr[COMPOSED_STRATEGY]['wrong_wilson_upper_95']>.01:H['H2']=False
  if (rr[COMPOSED_STRATEGY]['precision'] or 0)<.99:H['H3']=False
  if float(c['noise_scale'])==1.0 and (cm['brier']>.12 or cm['ece']>.05):H['H4']=False
  if float(c['noise_scale'])==1.0:
   req=.90 if float(c['gain'])==.50 else .85
   if rr[COMPOSED_STRATEGY]['coverage']<req:H['H5']=False
  # H6 is characterization by construction.
  if avg(qs[COMPOSED_STRATEGY],'operational_loss_401_600')>avg(qs[POSTERIOR_RISK_STRATEGY],'operational_loss_401_600')+.05:H['H7']=False
  if sum(int(float(x['causal_violation_count'])) for x in qs[COMPOSED_STRATEGY]) or sum(int(float(x['triad_veto_adapt_violations'])) for x in qs[COMPOSED_STRATEGY]):H['H8']=False
  fb=0
  for s in SEEDS:
   a,t=by[(s,COMPOSED_STRATEGY)],by[(s,TRIAD)]
   if int(float(a['abstain'])) and (a['adapt_signature']!=t['adapt_signature'] or abs(float(a['operational_loss_401_600'])-float(t['operational_loss_401_600']))>1e-12):fb+=1
  if fb:H['H9']=False
  out[c['label']]={'cell':c,'rates':rr,'calibration_final_stage':cm,'mean_operational_loss_401_600':{st:avg(qs[st],'operational_loss_401_600') for st in STRATEGIES},'mean_probe_energy':{st:avg(qs[st],'probe_energy') for st in STRATEGIES},'fallback_exact_mismatches':fb}
 H['H10']=bool(ACCEPT_THRESHOLD==.99 and WRONG_COST==100.0 and FALLBACK_COST==1.0)
 return {'evaluation_seeds':[35000,35999],'n_seeds_per_cell':1000,'cell_count':12,'strategies':STRATEGIES,'audit_seeds':sorted(AUDIT),'bootstrap_seed':35035,'bootstrap_resamples':10000,
         'hypotheses':H,'accept_threshold':ACCEPT_THRESHOLD,'wrong_action_cost':WRONG_COST,'fallback_cost':FALLBACK_COST,'posterior_likelihood':'Experiment-028 Gaussian directed covariance unchanged',
         'noise_definitions':{'laplace':'unit variance Laplace','student_t3':'t(df=3)/sqrt(3)','contaminated_gaussian':'95% N(0,1)+5% N(0,25), divided by sqrt(2.2)'},'no_recalibration':True,'code_commit':os.environ.get('GITHUB_SHA','unknown'),'cells':out}

def calibration_values():return calibrations()
