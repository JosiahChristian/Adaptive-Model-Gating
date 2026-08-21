#!/usr/bin/env python3
import csv,json,math,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from adaptive_model_gating import BASELINE_A
from experiment_029 import POSTERIOR_RISK_STRATEGY,QUALIFICATION_AWARE_STRATEGY,TRIAD,ACCEPT_THRESHOLD,WRONG_COST,FALLBACK_COST,run_experiment_029_strategy
from run_experiment_021 import calibrations

STRATEGIES=(POSTERIOR_RISK_STRATEGY,QUALIFICATION_AWARE_STRATEGY,TRIAD)
SEEDS=range(29000,30000);AUDIT=set(range(29000,29005));Z_ONE_SIDED_95=1.6448536269514722

def cell(label,kind,family,magnitude,**kw):return {'label':label,'kind':kind,'family':family,'magnitude':float(magnitude),**kw}
def cells():
 out=[]
 for g,scales in ((.50,(1.0,1.25,1.5,2.0)),(.425,(1.0,1.5,2.0)),(.35,(1.0,1.5,2.0))):
  for n in scales:out.append(cell(f'g{g:.3f}_n{n:.2f}','noise','drift_ab_fault',.50,gain=g,noise_scale=n))
 out += [cell('healthy','control','healthy',0.0),cell('drift_0.50','control','drift',.50),cell('common_mode_0.50','control','common_mode',.50),cell('primary_fault_0.50','control','primary_fault',.50),cell('drift_all_aux_fault_0.50','control','drift_all_aux_fault',.50,operational_truth_unresolved=True)]
 if len(out)!=15:raise AssertionError(len(out))
 return tuple(out)
CELLS=cells()

def write_csv(path,rows):
 path.parent.mkdir(parents=True,exist_ok=True);fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with path.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def summary(rows,c):
 r0=rows[0];post=[r for r in rows if 401<=r['t']<=600];p20=[r for r in rows if 401<=r['t']<=420];target=BASELINE_A+float(c['magnitude']) if c['family'].startswith('drift') else BASELINE_A
 accepted=int(float(r0.get('provenance_accepted',0)));abstain=int(float(r0.get('provenance_abstain',0)));stop=int(float(r0.get('probe_stop_round',0) or 0));correct=int(float(r0.get('accepted_partition_correct',0) or 0))
 violation=0
 if r0['strategy']==POSTERIOR_RISK_STRATEGY:
  ps=[float(r0.get(f'posterior_r{i}_candidate_p',0)) for i in range(1,6)]
  quals=[i+1 for i,p in enumerate(ps) if p>=ACCEPT_THRESHOLD]
  expected=quals[0] if quals else 0
  if accepted and (stop!=expected or expected==0):violation=1
  if abstain and expected!=0:violation=1
  if accepted and float(r0.get('posterior_at_deployment',0))<ACCEPT_THRESHOLD:violation=1
 return {'seed':int(r0['seed']),'label':c['label'],'strategy':r0['strategy'],'coverage':accepted,'correct':correct,'wrong_accept':int(accepted and not correct),'abstain':abstain,'stop_round':stop,
         'probe_energy':float(r0.get('probe_energy',0)),'adapt_401_420':int(any(r.get('adapt') for r in p20)),'adapt_signature':','.join(str(r['t']) for r in rows if r.get('adapt')),
         'operational_loss_401_600':sum(float(r['sq_error']) for r in post),'final_slope_error_abs':abs(float(rows[-1]['slope_after'])-target),'policy_violation':violation,
         'posterior_at_deployment':float(r0.get('posterior_at_deployment',0) or 0),'posterior_implied_error_risk':float(r0.get('posterior_implied_error_risk',0) or 0)}

def wilson_upper(k,n,z=Z_ONE_SIDED_95):
 if n<=0:return None
 p=k/n;den=1+z*z/n;center=(p+z*z/(2*n))/den;rad=z*math.sqrt((p*(1-p)/n)+(z*z/(4*n*n)))/den
 return min(1.0,center+rad)
def rates(q):
 acc=[x for x in q if x['coverage']==1];wrong=sum(x['wrong_accept'] for x in q);correct=sum(x['correct'] for x in acc)
 return {'coverage':len(acc)/len(q),'accepted_n':len(acc),'correct_n':correct,'wrong_n':wrong,'wrong_acceptance':wrong/len(q),'wrong_wilson_upper_95':wilson_upper(wrong,len(q)),'precision':correct/len(acc) if acc else None,'abstention':1-len(acc)/len(q)}
def mean(q,k):return sum(float(x[k]) for x in q)/len(q)

def report_from(rows):
 H={f'H{i}':True for i in range(1,11)};out={}
 frontier=set(c['label'] for c in CELLS if c['kind']=='noise')
 for c in CELLS:
  cr=[r for r in rows if r['label']==c['label']];by={s:[r for r in cr if r['strategy']==s] for s in STRATEGIES};rr={s:rates(by[s]) for s in STRATEGIES};pr=rr[POSTERIOR_RISK_STRATEGY];tri=rr[TRIAD]
  if any(x['policy_violation'] for x in by[POSTERIOR_RISK_STRATEGY]):H['H1']=False
  if c['label'] in frontier and pr['wrong_wilson_upper_95']>.01:H['H2']=False
  if c['label']=='g0.500_n1.50' and (pr['coverage']<.85 or (pr['precision'] or 0)<.99):H['H3']=False
  if c['label']=='g0.500_n1.25' and (pr['coverage']<.90 or (pr['precision'] or 0)<.99):H['H4']=False
  if c['label']=='g0.425_n1.00' and (pr['coverage']<.85 or (pr['precision'] or 0)<.99):H['H4']=False
  if c['label']=='g0.350_n2.00' and pr['wrong_wilson_upper_95']>.01:H['H5']=False
  energies={s:mean(by[s],'probe_energy') for s in STRATEGIES};losses={s:mean(by[s],'operational_loss_401_600') for s in STRATEGIES};slopes={s:mean(by[s],'final_slope_error_abs') for s in STRATEGIES}
  if c['label']=='g0.500_n1.00' and energies[POSTERIOR_RISK_STRATEGY]>.80:H['H6']=False
  if c['label']=='g0.500_n1.50' and energies[POSTERIOR_RISK_STRATEGY]>1.20:H['H6']=False
  if c['label'] in ('g0.500_n1.00','g0.500_n1.25','g0.500_n1.50') and (losses[POSTERIOR_RISK_STRATEGY]>losses[TRIAD]+.02 or slopes[POSTERIOR_RISK_STRATEGY]>slopes[TRIAD]+.02):H['H7']=False
  tri_by={int(x['seed']):x for x in by[TRIAD]};fallback=0
  for x in by[POSTERIOR_RISK_STRATEGY]:
   if x['abstain']:
    y=tri_by[int(x['seed'])]
    if x['adapt_signature']!=y['adapt_signature'] or x['operational_loss_401_600']!=y['operational_loss_401_600']:fallback+=1
  if fallback:H['H8']=False
  if c['kind']=='control' and c['label']!='drift_all_aux_fault_0.50' and (losses[POSTERIOR_RISK_STRATEGY]>losses[TRIAD]+.02 or slopes[POSTERIOR_RISK_STRATEGY]>slopes[TRIAD]+.02):H['H9']=False
  out[c['label']]={'cell':c,'rates':rr,'mean_probe_energy':energies,'mean_operational_loss_401_600':losses,'mean_final_slope_error_abs':slopes,'fallback_exact_mismatches':fallback,
                   'stop_round_distribution':{str(i):sum(1 for x in by[POSTERIOR_RISK_STRATEGY] if int(x['stop_round'])==i) for i in range(0,6)},
                   'mean_posterior_at_deployment':mean([x for x in by[POSTERIOR_RISK_STRATEGY] if x['coverage']],'posterior_at_deployment') if pr['accepted_n'] else None}
 # H5 relative conservatism clause.
 if out['g0.350_n2.00']['rates'][POSTERIOR_RISK_STRATEGY]['coverage'] > out['g0.500_n1.00']['rates'][POSTERIOR_RISK_STRATEGY]['coverage']-.10:H['H5']=False
 H['H10']=abs(ACCEPT_THRESHOLD-.99)<1e-12 and WRONG_COST==100.0 and FALLBACK_COST==1.0
 return {'evaluation_seeds':[29000,29999],'n_seeds_per_cell':1000,'cell_count':15,'strategies':STRATEGIES,'audit_seeds':sorted(AUDIT),'hypotheses':H,'wrong_action_cost':WRONG_COST,'fallback_cost':FALLBACK_COST,'accept_threshold':ACCEPT_THRESHOLD,
         'posterior_model':'Experiment-028 directed covariance; frozen without recalibration','code_commit':os.environ.get('GITHUB_SHA','unknown'),'cells':out}
