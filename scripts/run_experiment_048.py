#!/usr/bin/env python3
import csv,json,math,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from adaptive_model_gating import BASELINE_A
from experiment_018 import ALL_AMPLITUDES
from experiment_028 import VECTOR,TOPOLOGY_DIRECTIONS
from experiment_029 import WRONG_COST,FALLBACK_COST,TRIAD
from experiment_044 import DIRECTIONAL_GAUSSIAN_STRATEGY
from experiment_046 import E_THRESHOLD,split_indices
from experiment_047 import COV_MATCHED_E_STRATEGY,AMP_DENOM,BLOCK_PRECISION,_apply_scale_free_precision,_dot
from experiment_048 import SIGN_E_STRATEGY,STRATEGIES,CELLS,OPERATIVE_SPEC_ISSUE,EXACT_ALL_POSITIVE_TAIL,EXACT_GE9_TAIL,sign_factor,run_experiment_048_strategy
from run_experiment_021 import calibrations
SEEDS=range(48000,49000);AUDIT=set(range(48000,48005));Z=1.6448536269514722
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
 if r0['strategy']==SIGN_E_STRATEGY:
  out.update({'sign48_candidate':str(r0.get('sign48_candidate','')),'sign48_e_threshold':float(r0.get('sign48_e_threshold',0) or 0),'sign48_e_final':float(r0.get('sign48_e_final',0) or 0),'sign48_discovery_acceptance':int(float(r0.get('sign48_discovery_acceptance',0) or 0)),'sign48_candidate_reselected':int(float(r0.get('sign48_candidate_reselected',0) or 0)),'sign48_spec_issue':int(float(r0.get('sign48_spec_issue',0) or 0)),'sign48_amp_denom':float(r0.get('sign48_amp_denom',0) or 0),'sign48_positive_sign_count':int(float(r0.get('sign48_positive_sign_count',0) or 0))})
  for pair in VECTOR:out['Y_'+''.join(pair)]=r0.get('sign48_Y_'+''.join(pair),'')
  for h in ('H_ab','H_ac','H_bc'):out['Q_'+h]=r0.get('sign48_Q_'+h,'')
  for rr in range(1,6):
   for k in ('baseline_discovery','baseline_confirmation'):out[f'{k}_r{rr}']=r0.get(f'sign48_{k}_r{rr}','')
   for tgt in 'abc':
    out[f'target_discovery_r{rr}_{tgt}']=r0.get(f'sign48_target_discovery_r{rr}_{tgt}','');out[f'target_confirmation_r{rr}_{tgt}']=r0.get(f'sign48_target_confirmation_r{rr}_{tgt}','')
   out[f'e_r{rr}']=r0.get(f'sign48_e_r{rr}','')
   for pair in VECTOR:out[f'Ddisc_r{rr}_'+''.join(pair)]=r0.get(f'sign48_Ddisc_r{rr}_'+''.join(pair),'')
   for d in ('forward','reverse'):
    out[f'factor_r{rr}_{d}']=r0.get(f'sign48_factor_r{rr}_{d}','');out[f'response_r{rr}_{d}']=r0.get(f'sign48_response_r{rr}_{d}','')
 if r0['strategy']==COV_MATCHED_E_STRATEGY:
  out.update({'cov47_candidate':str(r0.get('cov47_candidate','')),'cov47_e_final':float(r0.get('cov47_e_final',0) or 0)})
 return out

def wilson_upper(k,n):
 p=k/n;den=1+Z*Z/n;center=(p+Z*Z/(2*n))/den;rad=Z*math.sqrt(p*(1-p)/n+Z*Z/(4*n*n))/den;return min(1.,center+rad)
def rates(q):
 acc=[x for x in q if int(float(x['coverage']))];wrong=sum(int(float(x['wrong_accept'])) for x in q);correct=sum(int(float(x['correct'])) for x in acc)
 return {'coverage':len(acc)/len(q),'accepted_n':len(acc),'wrong_n':wrong,'wrong_acceptance':wrong/len(q),'wrong_wilson_upper_95':wilson_upper(wrong,len(q)),'precision':correct/len(acc) if acc else None}
def avg(q,k):return sum(float(x[k]) for x in q)/len(q)
def _f(x):return None if x in ('',None) else float(x)

def integrity(x):
 if int(float(x.get('sign48_discovery_acceptance',1)))!=0 or int(float(x.get('sign48_candidate_reselected',1)))!=0:return False
 if int(float(x.get('sign48_spec_issue',0)))!=OPERATIVE_SPEC_ISSUE or float(x.get('sign48_e_threshold',0))!=E_THRESHOLD:return False
 if abs(float(x.get('sign48_amp_denom',0))-AMP_DENOM)>1e-12:return False
 y=[]
 for pair in VECTOR:
  val=sum(float(ALL_AMPLITUDES[r-1])*float(x[f'Ddisc_r{r}_'+''.join(pair)]) for r in range(1,6))/AMP_DENOM;y.append(val)
  if abs(val-float(x['Y_'+''.join(pair)]))>1e-12:return False
 py=_apply_scale_free_precision(y);scores={};order=('H_ab','H_ac','H_bc')
 for h,u in TOPOLOGY_DIRECTIONS.items():
  pu=_apply_scale_free_precision(u);num=max(0.0,_dot(u,py));den=_dot(u,pu);scores[h]=(num*num)/den
  if abs(scores[h]-float(x['Q_'+h]))>1e-10:return False
 cand=max(order,key=lambda h:(scores[h],-order.index(h)))
 if cand!=x.get('sign48_candidate'):return False
 prev=1.0;positive=0
 for r in range(1,6):
  ev=_f(x.get(f'e_r{r}'))
  if ev is None or not math.isfinite(ev) or ev<0:return False
  fs=[]
  for d in ('forward','reverse'):
   f=_f(x.get(f'factor_r{r}_{d}'));resp=_f(x.get(f'response_r{r}_{d}'))
   if f is None or resp is None or f not in (0.0,1.0,2.0) or abs(f-sign_factor(resp))>1e-12:return False
   positive+=int(resp>0.0);fs.append(f)
  prev*=fs[0]*fs[1]
  if abs(prev-ev)>1e-12:return False
 if positive!=int(float(x.get('sign48_positive_sign_count',-1))):return False
 if int(float(x['coverage']))!=(float(x['sign48_e_final'])>=E_THRESHOLD):return False
 if positive==10 and float(x['sign48_e_final'])!=1024.0:return False
 if positive<10 and float(x['sign48_e_final'])!=0.0:return False
 return True

def report_from(rows):
 H={f'H{i}':True for i in range(1,16)};out={};cross_improvements=[];coverage_improvements=[]
 if E_THRESHOLD!=100.0 or WRONG_COST!=100.0 or FALLBACK_COST!=1.0 or BLOCK_PRECISION!=((4.0/3.0,-2.0/3.0),(-2.0/3.0,4.0/3.0)):H['H15']=False
 if EXACT_ALL_POSITIVE_TAIL!=1/1024 or EXACT_GE9_TAIL!=11/1024:H['H15']=False
 for r in range(1,6):
  target,(bd,bc)=split_indices(r)
  if len(set(bd)&set(bc)) or any(len(set(td)&set(tc)) for td,tc in target.values()):H['H1']=False
 for c in CELLS:
  sr=[r for r in rows if r['label']==c['label']];by={(int(r['seed']),r['strategy']):r for r in sr};qs={st:[by[(s,st)] for s in SEEDS] for st in STRATEGIES};rr={st:rates(qs[st]) for st in STRATEGIES};S=rr[SIGN_E_STRATEGY];O=rr[COV_MATCHED_E_STRATEGY];D=rr[DIRECTIONAL_GAUSSIAN_STRATEGY]
  cand=[x for x in qs[SIGN_E_STRATEGY] if x.get('sign48_candidate')=='H_ab'];disc=len(cand)/1000;cross=sum(1 for x in cand if float(x.get('sign48_e_final',0))>=E_THRESHOLD)/len(cand) if cand else 0.0
  oldcand=[x for x in qs[COV_MATCHED_E_STRATEGY] if x.get('cov47_candidate')=='H_ab'];disc47=len(oldcand)/1000;cross47=sum(1 for x in oldcand if float(x.get('cov47_e_final',0))>=E_THRESHOLD)/len(oldcand) if oldcand else 0.0
  cross_improvements.append(cross-cross47);coverage_improvements.append(S['coverage']-O['coverage'])
  for x in qs[SIGN_E_STRATEGY]:
   if not integrity(x):H['H2']=False;H['H3']=False
  if S['wrong_wilson_upper_95']>.01:H['H4']=False
  if S['accepted_n'] and (S['precision'] or 0)<.99:H['H5']=False
  if float(c['noise_scale'])==1.0:
   req=.90 if float(c['gain'])==.50 else .85
   if S['coverage']<req:H['H6']=False
  if c['label']=='gaussian_g0.500_n1.50' and S['coverage']<.90:H['H7']=False
  if c['label']=='gaussian_g0.425_n1.50' and S['coverage']<.80:H['H7']=False
  if c['label'] in FAILED_044 and (S['wrong_wilson_upper_95']>.01 or S['wrong_acceptance']>D['wrong_acceptance']):H['H8']=False
  if disc < (.90 if float(c['noise_scale'])==1.0 else .80):H['H9']=False
  if disc < disc47-.02:H['H10']=False
  if cross < (.90 if float(c['noise_scale'])==1.0 else (.75 if c['noise_family']=='gaussian' else 0.0)):H['H11']=False
  if cross<cross47-.01 or S['coverage']<O['coverage']-.01:H['H12']=False
  losses={st:avg(qs[st],'operational_loss_401_600') for st in STRATEGIES}
  if losses[SIGN_E_STRATEGY]>losses[TRIAD]+.20:H['H13']=False
  fb=0
  if sum(int(float(x['causal_violation_count'])) for x in qs[SIGN_E_STRATEGY]) or sum(int(float(x['triad_veto_adapt_violations'])) for x in qs[SIGN_E_STRATEGY]):H['H14']=False
  for s in SEEDS:
   a,t=by[(s,SIGN_E_STRATEGY)],by[(s,TRIAD)]
   if int(float(a['abstain'])) and (a['adapt_signature']!=t['adapt_signature'] or abs(float(a['operational_loss_401_600'])-float(t['operational_loss_401_600']))>1e-12):fb+=1
  if fb:H['H14']=False
  out[c['label']]={'cell':c,'rates':rr,'discovery_h_ab_rate':disc,'experiment047_discovery_h_ab_rate':disc47,'confirmation_cross_rate_given_h_ab':cross,'experiment047_confirmation_cross_rate_given_h_ab':cross47,'cross_rate_improvement_over_experiment047':cross-cross47,'coverage_improvement_over_experiment047':S['coverage']-O['coverage'],'mean_operational_loss_401_600':losses,'fallback_exact_mismatches':fb}
 if sum(cross_improvements)/len(cross_improvements)<=0 or sum(coverage_improvements)/len(coverage_improvements)<=0:H['H12']=False
 return {'evaluation_seeds':[48000,48999],'n_seeds_per_cell':1000,'cell_count':16,'strategies':STRATEGIES,'audit_seeds':sorted(AUDIT),'bootstrap_seed':48048,'bootstrap_resamples':10000,'hypotheses':H,'e_threshold':E_THRESHOLD,'wrong_action_cost':WRONG_COST,'fallback_cost':FALLBACK_COST,'exact_all_positive_tail':EXACT_ALL_POSITIVE_TAIL,'exact_ge9_tail':EXACT_GE9_TAIL,'vector_order':VECTOR,'amplitudes':ALL_AMPLITUDES,'amplitude_normalization':AMP_DENOM,'covariance_blocks':'three scale-free [[1,1/2],[1/2,1]] blocks; analytic precision [[4/3,-2/3],[-2/3,4/3]]','discovery_rule':'Experiment-047 six-direction covariance-matched nonnegative-amplitude profile selector','confirmation_rule':'ten held-out sign factors: 2 positive, 0 negative, 1 exact zero; terminal E>=100; continuous case accepts iff 10/10 positive','context_rule':'Experiment-031 current-time causal context vote composed by Experiment-032','symmetry_assumption':'candidate-null held-out confirmation responses conditionally continuous and symmetric about zero; confirmation disjoint from discovery','full_five_round_latency':True,'no_tuning':True,'operative_spec_issue':OPERATIVE_SPEC_ISSUE,'code_commit':os.environ.get('GITHUB_SHA','unknown'),'mean_cross_rate_improvement_over_experiment047':sum(cross_improvements)/len(cross_improvements),'mean_coverage_improvement_over_experiment047':sum(coverage_improvements)/len(coverage_improvements),'cells':out}
def calibration_values():return calibrations()
