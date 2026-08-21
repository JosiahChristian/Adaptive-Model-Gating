#!/usr/bin/env python3
import csv,json,math,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from adaptive_model_gating import BASELINE_A,paired_bootstrap_ci
from experiment_029 import POSTERIOR_RISK_STRATEGY,TRIAD,ACCEPT_THRESHOLD,WRONG_COST,FALLBACK_COST
from experiment_032 import COMPOSED_STRATEGY,run_experiment_032_strategy
from run_experiment_021 import calibrations

STRATEGIES=(COMPOSED_STRATEGY,POSTERIOR_RISK_STRATEGY,TRIAD)
SEEDS=range(32000,33000);AUDIT=set(range(32000,32005));BOOTSTRAP_SEED=32032;Z=1.6448536269514722

def cell(label,kind,family,magnitude,**kw):return {'label':label,'kind':kind,'family':family,'magnitude':float(magnitude),**kw}
def cells():
 out=[]
 for g,scales in ((.50,(1.,1.25,1.5,2.)),(.425,(1.,1.5,2.)),(.35,(1.,1.5,2.))):
  for n in scales:out.append(cell(f'g{g:.3f}_n{n:.2f}','noise','drift_ab_fault',.50,gain=g,noise_scale=n))
 out += [cell('healthy','control','healthy',0.),cell('drift_0.50','control','drift',.50),cell('primary_fault_0.50','control','primary_fault',.50),
         cell('common_mode_0.25','control','common_mode',.25),cell('common_mode_0.50','control','common_mode',.50),cell('common_mode_1.00','control','common_mode',1.0),
         cell('drift_all_aux_fault_0.50','control','drift_all_aux_fault',.50,operational_truth_unresolved=True)]
 if len(out)!=17:raise AssertionError(len(out))
 return tuple(out)
CELLS=cells()

def write_csv(p,rows):
 p.parent.mkdir(parents=True,exist_ok=True);fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with p.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def summary(rows,c,comparator_rows=None):
 r0=rows[0];post=[r for r in rows if 401<=r['t']<=600];target=BASELINE_A+float(c['magnitude']) if c['family'].startswith('drift') else BASELINE_A
 accepted=int(float(r0.get('provenance_accepted',0)));correct=int(float(r0.get('accepted_partition_correct',0) or 0));abstain=int(float(r0.get('provenance_abstain',0)))
 context20=[r for r in rows if 401<=r['t']<=420];context200=post
 causal_violation=0;changed=0
 if comparator_rows is not None:
  by={int(r['t']):r for r in comparator_rows}
  for r in rows:
   t=int(r['t']);b=by[t]
   if int(r.get('adapt',0))!=int(b.get('adapt',0)):
    changed+=1
    if int(r.get('context_vote_t',0))!=1:causal_violation+=1
 return {'seed':int(r0['seed']),'label':c['label'],'strategy':r0['strategy'],'coverage':accepted,'correct':correct,'wrong_accept':int(accepted and not correct),'abstain':abstain,
         'stop_round':int(float(r0.get('probe_stop_round',0) or 0)),'probe_energy':float(r0.get('probe_energy',0)),'deploy_hypothesis':str(r0.get('posterior_deploy_hypothesis','')),
         'posterior_at_deployment':float(r0.get('posterior_at_deployment',0) or 0),'operational_loss_401_600':sum(float(r['sq_error']) for r in post),
         'final_slope_error_abs':abs(float(rows[-1]['slope_after'])-target),'adapt_signature':','.join(str(r['t']) for r in rows if r.get('adapt')),
         'context_vote_fraction_401_420':sum(int(r.get('context_vote_t',0)) for r in context20)/len(context20),
         'context_vote_fraction_401_600':sum(int(r.get('context_vote_t',0)) for r in context200)/len(context200),
         'context_removed_count':sum(int(r.get('context_removed_suspect_veto',0)) for r in rows),'changed_adapt_count_vs_029':changed,'causal_violation_count':causal_violation,
         'triad_veto_adapt_violations':sum(1 for r in rows if int(r.get('adapt',0)) and int(r.get('triad_primary_bad',0)))}

def wilson_upper(k,n):
 p=k/n;den=1+Z*Z/n;center=(p+Z*Z/(2*n))/den;rad=Z*math.sqrt(p*(1-p)/n+Z*Z/(4*n*n))/den;return min(1.,center+rad)
def rates(q):
 acc=[x for x in q if x['coverage']];wrong=sum(x['wrong_accept'] for x in q);correct=sum(x['correct'] for x in acc)
 return {'coverage':len(acc)/len(q),'accepted_n':len(acc),'wrong_n':wrong,'wrong_acceptance':wrong/len(q),'wrong_wilson_upper_95':wilson_upper(wrong,len(q)),'precision':correct/len(acc) if acc else None}
def avg(q,k):return sum(float(x[k]) for x in q)/len(q)
def ci(v):return list(paired_bootstrap_ci(v,seed=BOOTSTRAP_SEED,reps=10000))
def paired(by,a,b,k):return [float(by[(s,a)][k])-float(by[(s,b)][k]) for s in SEEDS]

def report_from(rows,vals):
 H={f'H{i}':True for i in range(1,12)};out={};frontier={c['label'] for c in CELLS if c['kind']=='noise'}
 for c in CELLS:
  cr=[r for r in rows if r['label']==c['label']];by={(int(r['seed']),r['strategy']):r for r in cr};qs={st:[by[(s,st)] for s in SEEDS] for st in STRATEGIES};rr={st:rates(qs[st]) for st in STRATEGIES}
  for s in SEEDS:
   a,b=by[(s,COMPOSED_STRATEGY)],by[(s,POSTERIOR_RISK_STRATEGY)]
   if any((a[k]!=b[k]) for k in ('coverage','abstain','stop_round','deploy_hypothesis')) or abs(a['posterior_at_deployment']-b['posterior_at_deployment'])>1e-12 or abs(a['probe_energy']-b['probe_energy'])>1e-12:H['H1']=False
  if c['label'] in frontier and rr[COMPOSED_STRATEGY]['wrong_wilson_upper_95']>.01:H['H2']=False
  if c['label']=='g0.500_n1.50' and (rr[COMPOSED_STRATEGY]['coverage']<.85 or (rr[COMPOSED_STRATEGY]['precision'] or 0)<.99):H['H3']=False
  if c['label']=='g0.500_n1.25' and rr[COMPOSED_STRATEGY]['coverage']<.90:H['H3']=False
  if c['label']=='g0.425_n1.00' and (rr[COMPOSED_STRATEGY]['coverage']<.85 or (rr[COMPOSED_STRATEGY]['precision'] or 0)<.99):H['H3']=False
  d32t=paired(by,COMPOSED_STRATEGY,TRIAD,'operational_loss_401_600');d29t=paired(by,POSTERIOR_RISK_STRATEGY,TRIAD,'operational_loss_401_600');d3229=paired(by,COMPOSED_STRATEGY,POSTERIOR_RISK_STRATEGY,'operational_loss_401_600')
  excess32=sum(d32t)/1000;excess29=sum(d29t)/1000;reduction=((excess29-excess32)/excess29 if excess29>0 else None)
  losses={st:avg(qs[st],'operational_loss_401_600') for st in STRATEGIES};slopes={st:avg(qs[st],'final_slope_error_abs') for st in STRATEGIES}
  if c['label']=='common_mode_0.50' and (excess32>2.0 or reduction is None or reduction<.80):H['H4']=False
  if c['label']=='common_mode_0.25' and excess32>.25:H['H5']=False
  if c['label']=='common_mode_1.00' and (excess32>35.0 or reduction is None or reduction<.80):H['H5']=False
  if c['label'] in ('g0.500_n1.00','g0.500_n1.25','g0.500_n1.50') and (losses[COMPOSED_STRATEGY]>losses[POSTERIOR_RISK_STRATEGY]+.02 or slopes[COMPOSED_STRATEGY]>slopes[POSTERIOR_RISK_STRATEGY]+.02):H['H6']=False
  if c['label'] in ('healthy','drift_0.50','primary_fault_0.50') and losses[COMPOSED_STRATEGY]>losses[TRIAD]+.02:H['H7']=False
  if sum(x['causal_violation_count'] for x in qs[COMPOSED_STRATEGY]):H['H8']=False
  if sum(x['triad_veto_adapt_violations'] for x in qs[COMPOSED_STRATEGY]):H['H9']=False
  fallback=0
  for s in SEEDS:
   a,t=by[(s,COMPOSED_STRATEGY)],by[(s,TRIAD)]
   if a['abstain'] and (a['adapt_signature']!=t['adapt_signature'] or a['operational_loss_401_600']!=t['operational_loss_401_600']):fallback+=1
  if fallback:H['H10']=False
  out[c['label']]={'cell':c,'rates':rr,'mean_probe_energy':{st:avg(qs[st],'probe_energy') for st in STRATEGIES},'mean_operational_loss_401_600':losses,'mean_final_slope_error_abs':slopes,
                   'mean_context_vote_fraction_401_420':avg(qs[COMPOSED_STRATEGY],'context_vote_fraction_401_420'),'mean_context_vote_fraction_401_600':avg(qs[COMPOSED_STRATEGY],'context_vote_fraction_401_600'),
                   'mean_context_removed_count':avg(qs[COMPOSED_STRATEGY],'context_removed_count'),'mean_changed_adapt_count_vs_029':avg(qs[COMPOSED_STRATEGY],'changed_adapt_count_vs_029'),
                   'paired_loss_vs_triad_mean':excess32,'paired_loss_vs_triad_ci':ci(d32t),'paired_loss_vs_029_mean':sum(d3229)/1000,'paired_loss_vs_029_ci':ci(d3229),
                   'experiment029_excess_vs_triad_mean':excess29,'fraction_excess_reduction_vs_029':reduction,'fallback_exact_mismatches':fallback}
  if c.get('operational_truth_unresolved'):out[c['label']]['operational_truth_unresolved']=True
 *_,k3,la,lb,lc,lab,lac,lbc=vals[:9]
 H['H11']=ACCEPT_THRESHOLD==.99 and WRONG_COST==100.0 and FALLBACK_COST==1.0
 return {'evaluation_seeds':[32000,32999],'n_seeds_per_cell':1000,'cell_count':17,'strategies':STRATEGIES,'audit_seeds':sorted(AUDIT),'bootstrap_seed':BOOTSTRAP_SEED,'bootstrap_resamples':10000,'hypotheses':H,
         'accept_threshold':ACCEPT_THRESHOLD,'wrong_action_cost':WRONG_COST,'fallback_cost':FALLBACK_COST,'context_vote_formula':'triad_consistent * 1[m_a+m_b+m_c>=2] * 1[d_ab+d_ac+d_bc==0] at current t only',
         'no_context_fitting':True,'code_commit':os.environ.get('GITHUB_SHA','unknown'),'cells':out}

def calibration_values():return calibrations()
