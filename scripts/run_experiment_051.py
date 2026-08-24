#!/usr/bin/env python3
import csv,json,math,os,random,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from adaptive_model_gating import BASELINE_A
from experiment_018 import ALL_AMPLITUDES
from experiment_028 import VECTOR,TOPOLOGY_DIRECTIONS
from experiment_029 import WRONG_COST,FALLBACK_COST,TRIAD
from experiment_046 import E_THRESHOLD,split_indices
from experiment_047 import AMP_DENOM,BLOCK_PRECISION,_apply_scale_free_precision,_dot
from experiment_049 import PAIR_SIGN_STRATEGY
from experiment_051 import SIGNED_RANK_STRATEGY,STRATEGIES,CELLS,OPERATIVE_SPEC_ISSUE,CONTRAST_COUNT,W_CUTOFF,P167_NUMERATOR,P167_DENOMINATOR,P167,P166_NUMERATOR,P166_DENOMINATOR,P166,ACCEPT_E,PRIMARY_PROBE_ENERGY,run_experiment_051_strategy,signed_rank_statistic
from run_experiment_021 import calibrations
SEEDS=range(51000,52000);AUDIT=set(range(51000,51005));Z=1.6448536269514722
EXP050_MEAN_COVERAGE=0.376125
EXP050_DISCOVERY={'contaminated_gaussian_g0.425_n1.00':0.956,'contaminated_gaussian_g0.425_n1.50':0.868,'contaminated_gaussian_g0.500_n1.00':0.971,'contaminated_gaussian_g0.500_n1.50':0.911,'gaussian_g0.425_n1.00':0.958,'gaussian_g0.425_n1.50':0.857,'gaussian_g0.500_n1.00':0.978,'gaussian_g0.500_n1.50':0.900,'laplace_g0.425_n1.00':0.956,'laplace_g0.425_n1.50':0.840,'laplace_g0.500_n1.00':0.980,'laplace_g0.500_n1.50':0.891,'student_t3_g0.425_n1.00':0.962,'student_t3_g0.425_n1.50':0.864,'student_t3_g0.500_n1.00':0.977,'student_t3_g0.500_n1.50':0.913}
STRESS={'M1':(5151000,'round-wise heteroskedastic symmetric scales 0.75,1.00,1.25,1.50,1.75'),'M2':(5152000,'direction-wise heteroskedastic symmetric forward:reverse 1:1.5'),'M3':(5153000,'AR(1) symmetric Gaussian rho=0.30'),'M4':(5154000,'90/10 asymmetric contaminated Gaussian shift +0.50')}

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
 out={'seed':int(r0['seed']),'label':c['label'],'noise_family':c['noise_family'],'gain':c['gain'],'noise_scale':c['noise_scale'],'strategy':r0['strategy'],'coverage':accepted,'correct':correct,'wrong_accept':int(accepted and not correct),'abstain':abstain,'deploy_hypothesis':str(r0.get('posterior_deploy_hypothesis','')),'operational_loss_401_600':sum(float(r['sq_error']) for r in post),'adapt_signature':','.join(str(r['t']) for r in rows if int(float(r.get('adapt',0) or 0))),'causal_violation_count':causal,'triad_veto_adapt_violations':sum(1 for r in rows if int(float(r.get('adapt',0) or 0)) and int(float(r.get('triad_primary_bad',0) or 0)))}
 if r0['strategy']==SIGNED_RANK_STRATEGY:
  for k in ('candidate','e_threshold','e_final','discovery_acceptance','candidate_reselected','spec_issue','amp_denom','contrast_count','w_cutoff','wplus','p167_numerator','p167_denominator','p167','p166_numerator','p166_denominator','p166','accept_e','zero_count','abs_tie_count','equal_budget_experiment049','uses_experiment050_replicate'):out['rank51_'+k]=r0.get('rank51_'+k,'')
  for pair in VECTOR:out['Y_'+''.join(pair)]=r0.get('rank51_Y_'+''.join(pair),'')
  for h in ('H_ab','H_ac','H_bc'):out['Q_'+h]=r0.get('rank51_Q_'+h,'')
  for rr in range(1,6):
   for k in ('baseline_discovery','baseline_confirmation'):out[f'{k}_r{rr}']=r0.get(f'rank51_{k}_r{rr}','')
   for tgt in 'abc':
    out[f'target_discovery_r{rr}_{tgt}']=r0.get(f'rank51_target_discovery_r{rr}_{tgt}','');out[f'target_confirmation_r{rr}_{tgt}']=r0.get(f'rank51_target_confirmation_r{rr}_{tgt}','');out[f'target_unused_r{rr}_{tgt}']=r0.get(f'rank51_target_unused_r{rr}_{tgt}','')
   out[f'e_r{rr}']=r0.get(f'rank51_e_r{rr}','')
   for pair in VECTOR:out[f'Ddisc_r{rr}_'+''.join(pair)]=r0.get(f'rank51_Ddisc_r{rr}_'+''.join(pair),'')
   for k in range(1,5):out[f'pair_response_r{rr}_{k}']=r0.get(f'rank51_pair_response_r{rr}_{k}','')
  for k in range(1,21):out[f'rank_{k}']=r0.get(f'rank51_rank_{k}','')
 if r0['strategy']==PAIR_SIGN_STRATEGY:out.update({'sign49_candidate':str(r0.get('sign49_candidate','')),'sign49_e_final':float(r0.get('sign49_e_final',0) or 0)})
 return out

def wilson_upper(k,n):
 p=k/n;den=1+Z*Z/n;center=(p+Z*Z/(2*n))/den;rad=Z*math.sqrt(p*(1-p)/n+Z*Z/(4*n*n))/den;return min(1.,center+rad)
def rates(q):
 acc=[x for x in q if int(float(x['coverage']))];wrong=sum(int(float(x['wrong_accept'])) for x in q);correct=sum(int(float(x['correct'])) for x in acc)
 return {'coverage':len(acc)/len(q),'accepted_n':len(acc),'wrong_n':wrong,'wrong_acceptance':wrong/len(q),'wrong_wilson_upper_95':wilson_upper(wrong,len(q)),'precision':correct/len(acc) if acc else None}
def avg(q,k):return sum(float(x[k]) for x in q)/len(q)

def integrity(x):
 if int(float(x.get('rank51_discovery_acceptance',1)))!=0 or int(float(x.get('rank51_candidate_reselected',1)))!=0:return False
 if int(float(x.get('rank51_spec_issue',0)))!=OPERATIVE_SPEC_ISSUE or float(x.get('rank51_e_threshold',0))!=E_THRESHOLD:return False
 if int(float(x.get('rank51_contrast_count',0)))!=CONTRAST_COUNT or int(float(x.get('rank51_w_cutoff',0)))!=W_CUTOFF:return False
 if int(float(x.get('rank51_p167_numerator',0)))!=P167_NUMERATOR or int(float(x.get('rank51_p167_denominator',0)))!=P167_DENOMINATOR:return False
 if int(float(x.get('rank51_p166_numerator',0)))!=P166_NUMERATOR or int(float(x.get('rank51_p166_denominator',0)))!=P166_DENOMINATOR:return False
 if abs(float(x.get('rank51_p167',0))-P167)>1e-15 or abs(float(x.get('rank51_p166',0))-P166)>1e-15 or abs(float(x.get('rank51_accept_e',0))-ACCEPT_E)>1e-12:return False
 vals=[]
 for r in range(1,6):
  vals.extend(float(x[f'pair_response_r{r}_{k}']) for k in range(1,5))
 if any(v==0 for v in vals) or len(set(abs(v) for v in vals))!=20:return False
 w,ranks=signed_rank_statistic(vals)
 if w!=int(float(x['rank51_wplus'])):return False
 if any(int(float(x[f'rank_{k}']))!=ranks[k-1] for k in range(1,21)):return False
 accepted=w>=W_CUTOFF
 if int(float(x['coverage']))!=accepted or abs(float(x['rank51_e_final'])-(ACCEPT_E if accepted else 0.0))>1e-12:return False
 y=[]
 for pair in VECTOR:
  val=sum(float(ALL_AMPLITUDES[r-1])*float(x[f'Ddisc_r{r}_'+''.join(pair)]) for r in range(1,6))/AMP_DENOM;y.append(val)
  if abs(val-float(x['Y_'+''.join(pair)]))>1e-12:return False
 py=_apply_scale_free_precision(y);scores={};order=('H_ab','H_ac','H_bc')
 for h,u in TOPOLOGY_DIRECTIONS.items():
  pu=_apply_scale_free_precision(u);num=max(0.0,_dot(u,py));scores[h]=(num*num)/_dot(u,pu)
  if abs(scores[h]-float(x['Q_'+h]))>1e-10:return False
 if max(order,key=lambda h:(scores[h],-order.index(h)))!=x.get('rank51_candidate'):return False
 return int(float(x.get('rank51_equal_budget_experiment049',0)))==1 and int(float(x.get('rank51_uses_experiment050_replicate',1)))==0

def _stress_values(kind,seed):
 rng=random.Random(seed)
 if kind=='M1':
  scales=(.75,1.,1.25,1.5,1.75);return [rng.gauss(0,scales[i//4]) for i in range(20)]
 if kind=='M2':return [rng.gauss(0,1.0 if (i%4)<2 else 1.5) for i in range(20)]
 if kind=='M3':
  rho=.30;x=rng.gauss(0,1);out=[x]
  for _ in range(19):x=rho*x+math.sqrt(1-rho*rho)*rng.gauss(0,1);out.append(x)
  return out
 if kind=='M4':return [rng.gauss(.5 if rng.random()<.10 else 0.0,1.0) for _ in range(20)]
 raise ValueError(kind)
def stress_panel():
 out={}
 for kind,(start,desc) in STRESS.items():
  wrong=0;ties=0;zeros=0
  for seed in range(start,start+1000):
   v=_stress_values(kind,seed);zeros+=sum(x==0 for x in v);ties+=20-len(set(abs(x) for x in v));w,_=signed_rank_statistic(v);wrong+=int(w>=W_CUTOFF)
  up=wilson_upper(wrong,1000);out[kind]={'seed_range':[start,start+999],'description':desc,'wrong_n':wrong,'wrong_acceptance':wrong/1000,'wrong_wilson_upper_95':up,'outside_demonstrated_1pct_robustness':up>.01,'zero_count':zeros,'absolute_tie_count':ties}
 return out

def report_from(rows):
 H={f'H{i}':True for i in range(1,17)};cells={};impc=[];impx=[];primary_zero=0;primary_ties=0
 if E_THRESHOLD!=100.0 or WRONG_COST!=100.0 or FALLBACK_COST!=1.0 or BLOCK_PRECISION!=((4.0/3.0,-2.0/3.0),(-2.0/3.0,4.0/3.0)):H['H16']=False
 if P167_NUMERATOR!=10084 or P167_DENOMINATOR!=1048576 or P166_NUMERATOR!=11264 or P166_DENOMINATOR!=1048576 or P167>.01 or P166<=.01 or W_CUTOFF!=167:H['H4']=False;H['H16']=False
 for r in range(1,6):
  target,(bd,bc)=split_indices(r)
  if len(set(bd)&set(bc)) or len(bc)!=2:H['H1']=False;H['H3']=False
  for td,tc in target.values():
   if len(set(td)&set(tc)) or len(tc)!=3:H['H1']=False;H['H3']=False
 for c in CELLS:
  sr=[r for r in rows if r['label']==c['label']];by={(int(r['seed']),r['strategy']):r for r in sr};qs={st:[by[(s,st)] for s in SEEDS] for st in STRATEGIES};rr={st:rates(qs[st]) for st in STRATEGIES};S=rr[SIGNED_RANK_STRATEGY];O=rr[PAIR_SIGN_STRATEGY]
  cand=[x for x in qs[SIGNED_RANK_STRATEGY] if x.get('rank51_candidate')=='H_ab'];disc=len(cand)/1000;cross=sum(int(float(x.get('rank51_wplus',0)))>=W_CUTOFF for x in cand)/len(cand) if cand else 0
  oldcand=[x for x in qs[PAIR_SIGN_STRATEGY] if x.get('sign49_candidate')=='H_ab'];oldcross=sum(float(x.get('sign49_e_final',0))>=E_THRESHOLD for x in oldcand)/len(oldcand) if oldcand else 0
  impc.append(S['coverage']-O['coverage']);impx.append(cross-oldcross)
  for x in qs[SIGNED_RANK_STRATEGY]:
   primary_zero+=int(float(x.get('rank51_zero_count',0) or 0));primary_ties+=int(float(x.get('rank51_abs_tie_count',0) or 0))
   if not integrity(x):H['H2']=False;H['H3']=False;H['H4']=False
  if S['wrong_wilson_upper_95']>.01:H['H5']=False
  if S['accepted_n'] and (S['precision'] or 0)<.99:H['H6']=False
  if float(c['noise_scale'])==1.0 and S['coverage']<(.70 if float(c['gain'])==.50 else .60):H['H7']=False
  if c['label']=='gaussian_g0.500_n1.50' and S['coverage']<.50:H['H8']=False
  if c['label']=='gaussian_g0.425_n1.50' and S['coverage']<.40:H['H8']=False
  if disc<(.90 if float(c['noise_scale'])==1.0 else .80) or disc<EXP050_DISCOVERY[c['label']]-.02:H['H9']=False
  if cross<=oldcross or S['coverage']<O['coverage']-.02:H['H10']=False
  losses={st:avg(qs[st],'operational_loss_401_600') for st in STRATEGIES}
  if losses[SIGNED_RANK_STRATEGY]>losses[TRIAD]+.20:H['H12']=False
  fb=0
  if sum(int(float(x['causal_violation_count'])) for x in qs[SIGNED_RANK_STRATEGY]) or sum(int(float(x['triad_veto_adapt_violations'])) for x in qs[SIGNED_RANK_STRATEGY]):H['H13']=False
  for s in SEEDS:
   a,t=by[(s,SIGNED_RANK_STRATEGY)],by[(s,TRIAD)]
   if int(float(a['abstain'])) and (a['adapt_signature']!=t['adapt_signature'] or abs(float(a['operational_loss_401_600'])-float(t['operational_loss_401_600']))>1e-12):fb+=1
  if fb:H['H13']=False
  cells[c['label']]={'cell':c,'rates':rr,'discovery_h_ab_rate':disc,'experiment050_discovery_h_ab_rate':EXP050_DISCOVERY[c['label']],'confirmation_cross_rate_given_h_ab':cross,'experiment049_cross_rate_given_h_ab':oldcross,'coverage_improvement_over_experiment049':S['coverage']-O['coverage'],'mean_operational_loss_401_600':losses,'fallback_exact_mismatches':fb}
 if sum(impc)/16<.10 or sum(impx)/16<=0:H['H10']=False
 mean_cov=sum(cells[k]['rates'][SIGNED_RANK_STRATEGY]['coverage'] for k in cells)/16
 if mean_cov<EXP050_MEAN_COVERAGE-.05:H['H11']=False
 if primary_zero or primary_ties:H['H14']=False
 stress=stress_panel();H['H15']=len(stress)==4 and all(v['zero_count']==0 and v['absolute_tie_count']==0 for v in stress.values())
 return {'evaluation_seeds':[51000,51999],'n_seeds_per_cell':1000,'cell_count':16,'strategies':STRATEGIES,'audit_seeds':sorted(AUDIT),'bootstrap_seed':51051,'bootstrap_resamples':10000,'hypotheses':H,'e_threshold':E_THRESHOLD,'wrong_action_cost':WRONG_COST,'fallback_cost':FALLBACK_COST,'contrast_count':CONTRAST_COUNT,'w_cutoff':W_CUTOFF,'p167_numerator':P167_NUMERATOR,'p167_denominator':P167_DENOMINATOR,'p167':P167,'p166_numerator':P166_NUMERATOR,'p166_denominator':P166_DENOMINATOR,'p166':P166,'accept_e':ACCEPT_E,'vector_order':VECTOR,'amplitudes':ALL_AMPLITUDES,'amplitude_normalization':AMP_DENOM,'covariance_blocks':'three scale-free [[1,1/2],[1/2,1]] blocks; analytic precision [[4/3,-2/3],[-2/3,4/3]]','discovery_rule':'Experiment-047 six-direction covariance-matched nonnegative-amplitude profile selector','confirmation_rule':'20 disjoint primary-stream pairwise contrasts; exact one-sided signed-rank W+>=167; terminal E=1/p167 on acceptance else 0','validity_assumptions':'independent identically distributed continuous symmetric confirmation contrasts','stress_panel':stress,'primary_zero_count':primary_zero,'primary_absolute_tie_count':primary_ties,'primary_probe_energy':PRIMARY_PROBE_ENERGY,'experiment050_reference_mean_coverage':EXP050_MEAN_COVERAGE,'mean_primary_coverage':mean_cov,'mean_coverage_improvement_over_experiment049':sum(impc)/16,'mean_cross_improvement_over_experiment049':sum(impx)/16,'context_rule':'Experiment-031 current-time causal context vote composed by Experiment-032','resource_accounting':'same primary-stream confirmation observations/probe exposure as Experiment 049; no Experiment 050 replicate; half Experiment 050 confirmation-stream measurement/probe exposure','full_five_round_latency':True,'no_tuning':True,'operative_spec_issue':OPERATIVE_SPEC_ISSUE,'code_commit':os.environ.get('GITHUB_SHA','unknown'),'cells':cells}
def calibration_values():return calibrations()
