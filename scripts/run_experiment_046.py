#!/usr/bin/env python3
import csv,json,math,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from adaptive_model_gating import BASELINE_A
from experiment_016 import SIGMA_PROBE
from experiment_029 import WRONG_COST,FALLBACK_COST,TRIAD
from experiment_032 import COMPOSED_STRATEGY
from experiment_044 import DIRECTIONAL_GAUSSIAN_STRATEGY
from experiment_045 import SYMMETRY_E_STRATEGY
from experiment_046 import WITHIN_SPLIT_E_STRATEGY,E_THRESHOLD,STRATEGIES,CELLS,split_indices,bet_factor,run_experiment_046_strategy
from run_experiment_021 import calibrations
SEEDS=range(46000,47000);AUDIT=set(range(46000,46005));Z=1.6448536269514722
FAILED_044={'contaminated_gaussian_g0.425_n1.00','contaminated_gaussian_g0.425_n1.50','contaminated_gaussian_g0.500_n1.50','student_t3_g0.425_n1.50','student_t3_g0.500_n1.50'}
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
 out={'seed':int(r0['seed']),'label':c['label'],'noise_family':c['noise_family'],'gain':c['gain'],'noise_scale':c['noise_scale'],'strategy':r0['strategy'],'coverage':accepted,'correct':correct,'wrong_accept':int(accepted and not correct),'abstain':abstain,'deploy_hypothesis':str(r0.get('posterior_deploy_hypothesis','')),'stop_round':int(float(r0.get('probe_stop_round',0) or 0)),'probe_energy':float(r0.get('probe_energy',0) or 0),'operational_loss_401_600':sum(float(r['sq_error']) for r in post),'final_slope_error_abs':abs(float(rows[-1]['slope_after'])-(BASELINE_A+0.50)),'adapt_signature':','.join(str(r['t']) for r in rows if int(float(r.get('adapt',0) or 0))),'causal_violation_count':causal,'triad_veto_adapt_violations':sum(1 for r in rows if int(float(r.get('adapt',0) or 0)) and int(float(r.get('triad_primary_bad',0) or 0)))}
 if r0['strategy']==WITHIN_SPLIT_E_STRATEGY:
  out.update({'within_candidate':str(r0.get('within_candidate','')),'within_e_threshold':float(r0.get('within_e_threshold',0) or 0),'within_e_final':float(r0.get('within_e_final',0) or 0),'within_sigma_probe':float(r0.get('within_sigma_probe',0) or 0),'within_discovery_acceptance':int(float(r0.get('within_discovery_acceptance',0) or 0)),'within_candidate_reselected':int(float(r0.get('within_candidate_reselected',0) or 0)),'within_spec_issue':int(float(r0.get('within_spec_issue',0) or 0))})
  for rr in range(1,6):
   for k in ('baseline_discovery','baseline_confirmation'):out[f'{k}_r{rr}']=r0.get(f'within_{k}_r{rr}','')
   for tgt in 'abc':
    out[f'target_discovery_r{rr}_{tgt}']=r0.get(f'within_target_discovery_r{rr}_{tgt}','');out[f'target_confirmation_r{rr}_{tgt}']=r0.get(f'within_target_confirmation_r{rr}_{tgt}','')
   out[f'e_r{rr}']=r0.get(f'within_e_r{rr}','')
   for d in ('forward','reverse'):
    out[f'factor_r{rr}_{d}']=r0.get(f'within_factor_r{rr}_{d}','');out[f'response_r{rr}_{d}']=r0.get(f'within_response_r{rr}_{d}','')
 return out
def wilson_upper(k,n):
 p=k/n;den=1+Z*Z/n;center=(p+Z*Z/(2*n))/den;rad=Z*math.sqrt(p*(1-p)/n+Z*Z/(4*n*n))/den;return min(1.,center+rad)
def rates(q):
 acc=[x for x in q if int(float(x['coverage']))];wrong=sum(int(float(x['wrong_accept'])) for x in q);correct=sum(int(float(x['correct'])) for x in acc)
 return {'coverage':len(acc)/len(q),'accepted_n':len(acc),'wrong_n':wrong,'wrong_acceptance':wrong/len(q),'wrong_wilson_upper_95':wilson_upper(wrong,len(q)),'precision':correct/len(acc) if acc else None}
def avg(q,k):return sum(float(x[k]) for x in q)/len(q)
def _f(x):return None if x in ('',None) else float(x)
def integrity(x):
 if int(float(x.get('within_discovery_acceptance',1)))!=0 or int(float(x.get('within_candidate_reselected',1)))!=0:return False
 if float(x.get('within_e_threshold',0))!=E_THRESHOLD or float(x.get('within_sigma_probe',0))!=SIGMA_PROBE:return False
 for r in range(1,6):
  ev=_f(x.get(f'e_r{r}'))
  if ev is None or not math.isfinite(ev) or ev<0:return False
  for d in ('forward','reverse'):
   f=_f(x.get(f'factor_r{r}_{d}'));resp=_f(x.get(f'response_r{r}_{d}'))
   if f is None or resp is None or not math.isfinite(f) or f<0 or abs(f-bet_factor(resp))>1e-12:return False
 if int(float(x['coverage']))!=(float(x['within_e_final'])>=E_THRESHOLD):return False
 return True
def report_from(rows):
 H={f'H{i}':True for i in range(1,15)};out={}
 if E_THRESHOLD!=100.0 or SIGMA_PROBE!=0.05 or WRONG_COST!=100.0 or FALLBACK_COST!=1.0:H['H14']=False
 for r in range(1,6):
  target,(bd,bc)=split_indices(r)
  if len(set(bd)&set(bc)) or any(len(set(td)&set(tc)) for td,tc in target.values()):H['H1']=False
 for c in CELLS:
  sr=[r for r in rows if r['label']==c['label']];by={(int(r['seed']),r['strategy']):r for r in sr};qs={st:[by[(s,st)] for s in SEEDS] for st in STRATEGIES};rr={st:rates(qs[st]) for st in STRATEGIES};C=rr[WITHIN_SPLIT_E_STRATEGY];W=rr[SYMMETRY_E_STRATEGY];G=rr[COMPOSED_STRATEGY];D=rr[DIRECTIONAL_GAUSSIAN_STRATEGY]
  cand=[x for x in qs[WITHIN_SPLIT_E_STRATEGY] if x.get('within_candidate')=='H_ab'];disc=len(cand)/1000;cross=sum(1 for x in cand if float(x.get('within_e_final',0))>=E_THRESHOLD)/len(cand) if cand else 0.0
  for x in qs[WITHIN_SPLIT_E_STRATEGY]:
   if not integrity(x):H['H2']=False
  if C['wrong_wilson_upper_95']>.01:H['H3']=False
  if C['accepted_n'] and (C['precision'] or 0)<.99:H['H4']=False
  if float(c['noise_scale'])==1.0:
   req=.90 if float(c['gain'])==.50 else .85
   if C['coverage']<req:H['H5']=False
  if c['noise_family']=='gaussian':
   if c['label']=='gaussian_g0.500_n1.50' and C['coverage']<.90:H['H6']=False
   if c['label']=='gaussian_g0.425_n1.50' and C['coverage']<.80:H['H6']=False
   if float(c['noise_scale'])==1.0 and C['coverage']<G['coverage']-.05:H['H6']=False
   if C['wrong_wilson_upper_95']>.01 or (C['accepted_n'] and (C['precision'] or 0)<.99):H['H6']=False
  if c['label'] in FAILED_044 and (C['wrong_wilson_upper_95']>.01 or C['wrong_acceptance']>D['wrong_acceptance']):H['H7']=False
  if float(c['noise_scale'])==1.0:
   improve=.50 if float(c['gain'])==.50 else .40
   if C['coverage']<W['coverage']+improve:H['H8']=False
  if C['coverage']<D['coverage']-.08:H['H9']=False
  losses={st:avg(qs[st],'operational_loss_401_600') for st in STRATEGIES}
  if losses[WITHIN_SPLIT_E_STRATEGY]>losses[TRIAD]+.20:H['H10']=False
  fb=0
  if sum(int(float(x['causal_violation_count'])) for x in qs[WITHIN_SPLIT_E_STRATEGY]) or sum(int(float(x['triad_veto_adapt_violations'])) for x in qs[WITHIN_SPLIT_E_STRATEGY]):H['H11']=False
  for s in SEEDS:
   a,t=by[(s,WITHIN_SPLIT_E_STRATEGY)],by[(s,TRIAD)]
   if int(float(a['abstain'])) and (a['adapt_signature']!=t['adapt_signature'] or abs(float(a['operational_loss_401_600'])-float(t['operational_loss_401_600']))>1e-12):fb+=1
  if fb:H['H11']=False
  if disc < (.90 if float(c['noise_scale'])==1.0 else .80):H['H12']=False
  if cross < (.90 if float(c['noise_scale'])==1.0 else (.75 if c['noise_family']=='gaussian' else 0.0)):H['H13']=False
  out[c['label']]={'cell':c,'rates':rr,'discovery_h_ab_rate':disc,'confirmation_cross_rate_given_h_ab':cross,'mean_operational_loss_401_600':losses,'fallback_exact_mismatches':fb}
 return {'evaluation_seeds':[46000,46999],'n_seeds_per_cell':1000,'cell_count':16,'strategies':STRATEGIES,'audit_seeds':sorted(AUDIT),'bootstrap_seed':46046,'bootstrap_resamples':10000,'hypotheses':H,'e_threshold':E_THRESHOLD,'wrong_action_cost':WRONG_COST,'fallback_cost':FALLBACK_COST,'sigma_probe':SIGMA_PROBE,'discovery_rule':'all five rounds; first 2/5 target and first 2/4 baseline; amplitude-weighted symmetric edge score; lexical tie-break','confirmation_rule':'all five rounds; held-out 3/5 target and last 2/4 baseline; frozen candidate; ten symmetry factors; terminal E>=100','context_rule':'Experiment-031 current-time causal context vote composed by Experiment-032','symmetry_assumption':'candidate-null held-out confirmation responses continuous and symmetric about zero; disjoint confirmation increments independent conditional on discovery','no_tuning':True,'operative_spec_issue':120,'code_commit':os.environ.get('GITHUB_SHA','unknown'),'cells':out}
def calibration_values():return calibrations()
