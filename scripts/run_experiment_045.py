#!/usr/bin/env python3
import csv,json,math,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from adaptive_model_gating import BASELINE_A
from experiment_016 import SIGMA_PROBE
from experiment_029 import WRONG_COST,FALLBACK_COST,TRIAD
from experiment_032 import COMPOSED_STRATEGY
from experiment_036 import ROBUST_STRATEGY
from experiment_037 import MODEL_AVERAGED_STRATEGY
from experiment_039 import RADIAL_HUBER_STRATEGY
from experiment_040 import LOCAL_MIXTURE_STRATEGY
from experiment_041 import LOCAL_CAUCHY_STRATEGY
from experiment_042 import LOCAL_GAUSSIAN_GROSS_STRATEGY
from experiment_043 import REPLICATED_GAUSSIAN_STRATEGY
from experiment_044 import DIRECTIONAL_GAUSSIAN_STRATEGY
from experiment_045 import SYMMETRY_E_STRATEGY,E_THRESHOLD,BASELINE_SLICES,STRATEGIES,CELLS,bet_factor,run_experiment_045_strategy
from run_experiment_021 import calibrations
SEEDS=range(45000,46000);AUDIT=set(range(45000,45005));Z=1.6448536269514722
VULNERABLE_035={'contaminated_gaussian_g0.425_n1.00','contaminated_gaussian_g0.425_n1.50','contaminated_gaussian_g0.500_n1.00','contaminated_gaussian_g0.500_n1.50','student_t3_g0.425_n1.00','student_t3_g0.425_n1.50','student_t3_g0.500_n1.00','student_t3_g0.500_n1.50','laplace_g0.425_n1.50'}
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
 if r0['strategy']==SYMMETRY_E_STRATEGY:
  out.update({'symmetry_candidate':str(r0.get('symmetry_candidate','')),'symmetry_discovery_acceptance':int(float(r0.get('symmetry_discovery_acceptance',0) or 0)),'symmetry_candidate_reselected':int(float(r0.get('symmetry_candidate_reselected',0) or 0)),'symmetry_e_threshold':float(r0.get('symmetry_e_threshold',0) or 0),'symmetry_e_final':float(r0.get('symmetry_e_final',0) or 0),'symmetry_sigma_probe':float(r0.get('symmetry_sigma_probe',0) or 0),'symmetry_spec_issue':int(float(r0.get('symmetry_spec_issue',0) or 0))})
  for rr in range(1,6):
   out[f'e_r{rr}']=r0.get(f'symmetry_e_r{rr}','');out[f'cross_r{rr}']=r0.get(f'symmetry_cross_r{rr}','')
   out[f'baseline_start_r{rr}']=r0.get(f'symmetry_baseline_start_r{rr}','');out[f'baseline_stop_r{rr}']=r0.get(f'symmetry_baseline_stop_r{rr}','')
   if rr>=2:
    for d in ('forward','reverse'):
     out[f'factor_r{rr}_{d}']=r0.get(f'symmetry_factor_r{rr}_{d}','');out[f'response_r{rr}_{d}']=r0.get(f'symmetry_response_r{rr}_{d}','')
 return out
def wilson_upper(k,n):
 p=k/n;den=1+Z*Z/n;center=(p+Z*Z/(2*n))/den;rad=Z*math.sqrt(p*(1-p)/n+Z*Z/(4*n*n))/den;return min(1.,center+rad)
def rates(q):
 acc=[x for x in q if int(float(x['coverage']))];wrong=sum(int(float(x['wrong_accept'])) for x in q);correct=sum(int(float(x['correct'])) for x in acc)
 return {'coverage':len(acc)/len(q),'accepted_n':len(acc),'wrong_n':wrong,'wrong_acceptance':wrong/len(q),'wrong_wilson_upper_95':wilson_upper(wrong,len(q)),'precision':correct/len(acc) if acc else None}
def avg(q,k):return sum(float(x[k]) for x in q)/len(q)
def _f(x):return None if x in ('',None) else float(x)
def e_integrity(x):
 if int(float(x.get('symmetry_discovery_acceptance',1)))!=0 or int(float(x.get('symmetry_candidate_reselected',1)))!=0:return False
 if float(x.get('symmetry_e_threshold',0))!=E_THRESHOLD or float(x.get('symmetry_sigma_probe',0))!=SIGMA_PROBE:return False
 stop=int(float(x['stop_round']));vals=[]
 for r in range(1,6):
  v=_f(x.get(f'e_r{r}'));cross=_f(x.get(f'cross_r{r}'))
  if v is not None:
   if not math.isfinite(v) or v<0:return False
   vals.append((r,v,cross))
  if r>=2:
   for d in ('forward','reverse'):
    f=_f(x.get(f'factor_r{r}_{d}'));resp=_f(x.get(f'response_r{r}_{d}'))
    if f is None and resp is None:continue
    if f is None or resp is None or not math.isfinite(f) or f<0 or abs(f-bet_factor(resp))>1e-12:return False
 if int(float(x['coverage'])):
  if stop<2:return False
  ev=_f(x.get(f'e_r{stop}'))
  if ev is None or ev<E_THRESHOLD:return False
  for r,v,_ in vals:
   if r<stop and v>=E_THRESHOLD:return False
 else:
  if any(v>=E_THRESHOLD for _,v,_ in vals):return False
 return True
def report_from(rows):
 H={f'H{i}':True for i in range(1,14)};out={}
 expected_slices=[(181,184),(185,188),(189,192),(193,196),(197,200)]
 if [(BASELINE_SLICES[r].start,BASELINE_SLICES[r].stop-1) for r in range(1,6)]!=expected_slices:H['H11']=False
 if E_THRESHOLD!=100.0 or SIGMA_PROBE!=0.05 or WRONG_COST!=100.0 or FALLBACK_COST!=1.0:H['H13']=False
 for c in CELLS:
  sr=[r for r in rows if r['label']==c['label']];by={(int(r['seed']),r['strategy']):r for r in sr};qs={st:[by[(s,st)] for s in SEEDS] for st in STRATEGIES};rr={st:rates(qs[st]) for st in STRATEGIES};C=rr[SYMMETRY_E_STRATEGY];G=rr[COMPOSED_STRATEGY];D=rr[DIRECTIONAL_GAUSSIAN_STRATEGY]
  for x in qs[SYMMETRY_E_STRATEGY]:
   if not e_integrity(x):H['H1']=False;H['H12']=False
   for r,(bs,be) in enumerate(expected_slices,1):
    if int(float(x[f'baseline_start_r{r}']))!=bs or int(float(x[f'baseline_stop_r{r}']))!=be:H['H11']=False
  if C['wrong_wilson_upper_95']>.01:H['H2']=False
  if (C['precision'] or 0)<.99:H['H3']=False
  if float(c['noise_scale'])==1.0:
   req=.90 if float(c['gain'])==.50 else .85
   if C['coverage']<req:H['H4']=False
  if c['noise_family']=='gaussian':
   if c['label']=='gaussian_g0.500_n1.50' and C['coverage']<.90:H['H5']=False
   if c['label']=='gaussian_g0.425_n1.50' and C['coverage']<.80:H['H5']=False
   if float(c['noise_scale'])==1.0 and C['coverage']<G['coverage']-.05:H['H5']=False
   if C['wrong_wilson_upper_95']>.01 or (C['precision'] or 0)<.99:H['H5']=False
  if c['label'] in VULNERABLE_035 and (C['wrong_wilson_upper_95']>.01 or (C['precision'] or 0)<.99 or C['wrong_acceptance']>G['wrong_acceptance']):H['H6']=False
  if c['label'] in FAILED_044 and (C['wrong_wilson_upper_95']>.01 or C['wrong_acceptance']>D['wrong_acceptance']):H['H7']=False
  if C['coverage']<D['coverage']-.08:H['H8']=False
  losses={st:avg(qs[st],'operational_loss_401_600') for st in STRATEGIES}
  if losses[SYMMETRY_E_STRATEGY]>losses[TRIAD]+.20:H['H9']=False
  fb=0
  if sum(int(float(x['causal_violation_count'])) for x in qs[SYMMETRY_E_STRATEGY]) or sum(int(float(x['triad_veto_adapt_violations'])) for x in qs[SYMMETRY_E_STRATEGY]):H['H10']=False
  for s in SEEDS:
   a,t=by[(s,SYMMETRY_E_STRATEGY)],by[(s,TRIAD)]
   if int(float(a['abstain'])) and (a['adapt_signature']!=t['adapt_signature'] or abs(float(a['operational_loss_401_600'])-float(t['operational_loss_401_600']))>1e-12):fb+=1
  if fb:H['H10']=False
  out[c['label']]={'cell':c,'rates':rr,'mean_operational_loss_401_600':losses,'mean_probe_energy':{st:avg(qs[st],'probe_energy') for st in STRATEGIES},'fallback_exact_mismatches':fb}
 return {'evaluation_seeds':[45000,45999],'n_seeds_per_cell':1000,'cell_count':16,'strategies':STRATEGIES,'audit_seeds':sorted(AUDIT),'bootstrap_seed':45045,'bootstrap_resamples':10000,'hypotheses':H,'e_threshold':E_THRESHOLD,'wrong_action_cost':WRONG_COST,'fallback_cost':FALLBACK_COST,'sigma_probe':SIGMA_PROBE,'baseline_slices':expected_slices,'discovery_rule':'round 1 only; max S_ij=D1(i,j)+D1(j,i), lexical tie-break ab<ac<bc; no acceptance','confirmation_rule':'rounds 2..5 only; frozen candidate; m(x)=1+sgn(x)*tanh(|x|/0.05); cumulative E>=100','context_rule':'Experiment-031 current-time causal context vote composed by Experiment-032','symmetry_assumption':'candidate-null confirmation responses continuous and symmetric about zero; disjoint benchmark increments independent','vulnerable_experiment035_cells':sorted(VULNERABLE_035),'experiment044_failed_safety_cells':sorted(FAILED_044),'no_tuning':True,'operative_spec_issue':115,'code_commit':os.environ.get('GITHUB_SHA','unknown'),'cells':out}
def calibration_values():return calibrations()
