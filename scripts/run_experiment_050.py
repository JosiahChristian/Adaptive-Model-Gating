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
from experiment_047 import AMP_DENOM,BLOCK_PRECISION,_apply_scale_free_precision,_dot
from experiment_049 import PAIR_SIGN_STRATEGY
from experiment_050 import REPLICATED_SIGN_STRATEGY,STRATEGIES,CELLS,OPERATIVE_SPEC_ISSUE,REPLICATE_SEED_OFFSET,SIGN_COUNT,POSITIVE_CUTOFF,P28_NUMERATOR,P28_DENOMINATOR,P28,P27_NUMERATOR,P27_DENOMINATOR,P27,ACCEPT_E,PRIMARY_PROBE_ENERGY,TOTAL_PROBE_ENERGY,run_experiment_050_strategy
from run_experiment_021 import calibrations
SEEDS=range(50000,51000);AUDIT=set(range(50000,50005));Z=1.6448536269514722
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
 if r0['strategy']==REPLICATED_SIGN_STRATEGY:
  for k in ('candidate','e_threshold','e_final','discovery_acceptance','candidate_reselected','spec_issue','amp_denom','sign_count','positive_cutoff','p28_numerator','p28_denominator','p28','p27_numerator','p27_denominator','p27','accept_e','primary_seed','replicate_seed','replicate_seed_offset','positive_sign_count','zero_sign_count','primary_probe_energy','confirmation_replicate_probe_energy','total_probe_energy','equal_budget_comparison'):out['sign50_'+k]=r0.get('sign50_'+k,'')
  for pair in VECTOR:out['Y_'+''.join(pair)]=r0.get('sign50_Y_'+''.join(pair),'')
  for h in ('H_ab','H_ac','H_bc'):out['Q_'+h]=r0.get('sign50_Q_'+h,'')
  for rr in range(1,6):
   for k in ('baseline_discovery','baseline_confirmation'):out[f'{k}_r{rr}']=r0.get(f'sign50_{k}_r{rr}','')
   for tgt in 'abc':
    out[f'target_discovery_r{rr}_{tgt}']=r0.get(f'sign50_target_discovery_r{rr}_{tgt}','');out[f'target_confirmation_r{rr}_{tgt}']=r0.get(f'sign50_target_confirmation_r{rr}_{tgt}','');out[f'target_unused_r{rr}_{tgt}']=r0.get(f'sign50_target_unused_r{rr}_{tgt}','')
   out[f'e_r{rr}']=r0.get(f'sign50_e_r{rr}','');out[f'positive_count_r{rr}']=r0.get(f'sign50_positive_count_r{rr}','');out[f'zero_count_r{rr}']=r0.get(f'sign50_zero_count_r{rr}','')
   for pair in VECTOR:out[f'Ddisc_r{rr}_'+''.join(pair)]=r0.get(f'sign50_Ddisc_r{rr}_'+''.join(pair),'')
   for k in range(1,5):out[f'primary_pair_response_r{rr}_{k}']=r0.get(f'sign50_primary_pair_response_r{rr}_{k}','');out[f'replicate_pair_response_r{rr}_{k}']=r0.get(f'sign50_replicate_pair_response_r{rr}_{k}','')
 if r0['strategy']==PAIR_SIGN_STRATEGY:out.update({'sign49_candidate':str(r0.get('sign49_candidate','')),'sign49_e_final':float(r0.get('sign49_e_final',0) or 0)})
 return out

def wilson_upper(k,n):
 p=k/n;den=1+Z*Z/n;center=(p+Z*Z/(2*n))/den;rad=Z*math.sqrt(p*(1-p)/n+Z*Z/(4*n*n))/den;return min(1.,center+rad)
def rates(q):
 acc=[x for x in q if int(float(x['coverage']))];wrong=sum(int(float(x['wrong_accept'])) for x in q);correct=sum(int(float(x['correct'])) for x in acc)
 return {'coverage':len(acc)/len(q),'accepted_n':len(acc),'wrong_n':wrong,'wrong_acceptance':wrong/len(q),'wrong_wilson_upper_95':wilson_upper(wrong,len(q)),'precision':correct/len(acc) if acc else None}
def avg(q,k):return sum(float(x[k]) for x in q)/len(q)

def integrity(x):
 if int(float(x.get('sign50_discovery_acceptance',1)))!=0 or int(float(x.get('sign50_candidate_reselected',1)))!=0:return False
 if int(float(x.get('sign50_spec_issue',0)))!=OPERATIVE_SPEC_ISSUE or float(x.get('sign50_e_threshold',0))!=E_THRESHOLD:return False
 if int(float(x.get('sign50_sign_count',0)))!=SIGN_COUNT or int(float(x.get('sign50_positive_cutoff',0)))!=POSITIVE_CUTOFF:return False
 if int(float(x.get('sign50_p28_numerator',0)))!=P28_NUMERATOR or int(float(x.get('sign50_p28_denominator',0)))!=P28_DENOMINATOR:return False
 if int(float(x.get('sign50_p27_numerator',0)))!=P27_NUMERATOR or int(float(x.get('sign50_p27_denominator',0)))!=P27_DENOMINATOR:return False
 if abs(float(x.get('sign50_p28',0))-P28)>1e-15 or abs(float(x.get('sign50_p27',0))-P27)>1e-15 or abs(float(x.get('sign50_accept_e',0))-ACCEPT_E)>1e-12:return False
 seed=int(x['seed'])
 if int(float(x.get('sign50_primary_seed',-1)))!=seed or int(float(x.get('sign50_replicate_seed',-1)))!=seed+REPLICATE_SEED_OFFSET or int(float(x.get('sign50_replicate_seed_offset',-1)))!=REPLICATE_SEED_OFFSET:return False
 y=[]
 for pair in VECTOR:
  val=sum(float(ALL_AMPLITUDES[r-1])*float(x[f'Ddisc_r{r}_'+''.join(pair)]) for r in range(1,6))/AMP_DENOM;y.append(val)
  if abs(val-float(x['Y_'+''.join(pair)]))>1e-12:return False
 py=_apply_scale_free_precision(y);scores={};order=('H_ab','H_ac','H_bc')
 for h,u in TOPOLOGY_DIRECTIONS.items():
  pu=_apply_scale_free_precision(u);num=max(0.0,_dot(u,py));scores[h]=(num*num)/_dot(u,pu)
  if abs(scores[h]-float(x['Q_'+h]))>1e-10:return False
 if max(order,key=lambda h:(scores[h],-order.index(h)))!=x.get('sign50_candidate'):return False
 positive=0;zero=0
 for r in range(1,6):
  vals=[float(x[f'primary_pair_response_r{r}_{k}']) for k in range(1,5)]+[float(x[f'replicate_pair_response_r{r}_{k}']) for k in range(1,5)];positive+=sum(v>0 for v in vals);zero+=sum(v==0 for v in vals)
  expected=ACCEPT_E if r==5 and positive>=POSITIVE_CUTOFF else 0.0
  if abs(float(x[f'e_r{r}'])-expected)>1e-12:return False
 if positive!=int(float(x.get('sign50_positive_sign_count',-1))) or zero!=int(float(x.get('sign50_zero_sign_count',-1))):return False
 accepted=positive>=POSITIVE_CUTOFF
 if int(float(x['coverage']))!=accepted or abs(float(x['sign50_e_final'])-(ACCEPT_E if accepted else 0.0))>1e-12:return False
 if abs(float(x.get('sign50_primary_probe_energy',0))-PRIMARY_PROBE_ENERGY)>1e-12 or abs(float(x.get('sign50_confirmation_replicate_probe_energy',0))-PRIMARY_PROBE_ENERGY)>1e-12 or abs(float(x.get('sign50_total_probe_energy',0))-TOTAL_PROBE_ENERGY)>1e-12 or int(float(x.get('sign50_equal_budget_comparison',1)))!=0:return False
 return True

def report_from(rows):
 H={f'H{i}':True for i in range(1,17)};out={};cross_improvements=[];coverage_improvements=[]
 if E_THRESHOLD!=100.0 or WRONG_COST!=100.0 or FALLBACK_COST!=1.0 or BLOCK_PRECISION!=((4.0/3.0,-2.0/3.0),(-2.0/3.0,4.0/3.0)):H['H16']=False
 if SIGN_COUNT!=40 or POSITIVE_CUTOFF!=28 or P28_NUMERATOR!=9119901052 or P28_DENOMINATOR!=1099511627776 or P28>.01 or P27<=.01:H['H16']=False
 for r in range(1,6):
  target,(bd,bc)=split_indices(r)
  if len(set(bd)&set(bc)) or len(bc)!=2:H['H1']=False;H['H3']=False
  for td,tc in target.values():
   if len(set(td)&set(tc)) or len(tc)!=3:H['H1']=False;H['H3']=False
 for c in CELLS:
  sr=[r for r in rows if r['label']==c['label']];by={(int(r['seed']),r['strategy']):r for r in sr};qs={st:[by[(s,st)] for s in SEEDS] for st in STRATEGIES};rr={st:rates(qs[st]) for st in STRATEGIES};S=rr[REPLICATED_SIGN_STRATEGY];O=rr[PAIR_SIGN_STRATEGY];D=rr[DIRECTIONAL_GAUSSIAN_STRATEGY]
  cand=[x for x in qs[REPLICATED_SIGN_STRATEGY] if x.get('sign50_candidate')=='H_ab'];disc=len(cand)/1000;cross=sum(1 for x in cand if float(x.get('sign50_e_final',0))>=E_THRESHOLD)/len(cand) if cand else 0.0
  oldcand=[x for x in qs[PAIR_SIGN_STRATEGY] if x.get('sign49_candidate')=='H_ab'];disc49=len(oldcand)/1000;cross49=sum(1 for x in oldcand if float(x.get('sign49_e_final',0))>=E_THRESHOLD)/len(oldcand) if oldcand else 0.0
  cross_improvements.append(cross-cross49);coverage_improvements.append(S['coverage']-O['coverage'])
  for x in qs[REPLICATED_SIGN_STRATEGY]:
   if not integrity(x):H['H2']=False;H['H3']=False;H['H4']=False;H['H13']=False
  if S['wrong_wilson_upper_95']>.01:H['H5']=False
  if S['accepted_n'] and (S['precision'] or 0)<.99:H['H6']=False
  if float(c['noise_scale'])==1.0:
   req=.70 if float(c['gain'])==.50 else .60
   if S['coverage']<req:H['H7']=False
  if c['label']=='gaussian_g0.500_n1.50' and S['coverage']<.50:H['H8']=False
  if c['label']=='gaussian_g0.425_n1.50' and S['coverage']<.40:H['H8']=False
  if c['label'] in FAILED_044 and (S['wrong_wilson_upper_95']>.01 or S['wrong_acceptance']>D['wrong_acceptance']):H['H9']=False
  if disc < (.90 if float(c['noise_scale'])==1.0 else .80) or disc<disc49-.02:H['H10']=False
  if cross<=cross49:H['H11']=False
  if S['coverage']<O['coverage']-.01:H['H12']=False
  losses={st:avg(qs[st],'operational_loss_401_600') for st in STRATEGIES}
  if losses[REPLICATED_SIGN_STRATEGY]>losses[TRIAD]+.20:H['H14']=False
  fb=0
  if sum(int(float(x['causal_violation_count'])) for x in qs[REPLICATED_SIGN_STRATEGY]) or sum(int(float(x['triad_veto_adapt_violations'])) for x in qs[REPLICATED_SIGN_STRATEGY]):H['H15']=False
  for s in SEEDS:
   a,t=by[(s,REPLICATED_SIGN_STRATEGY)],by[(s,TRIAD)]
   if int(float(a['abstain'])) and (a['adapt_signature']!=t['adapt_signature'] or abs(float(a['operational_loss_401_600'])-float(t['operational_loss_401_600']))>1e-12):fb+=1
  if fb:H['H15']=False
  out[c['label']]={'cell':c,'rates':rr,'discovery_h_ab_rate':disc,'experiment049_discovery_h_ab_rate':disc49,'confirmation_cross_rate_given_h_ab':cross,'experiment049_confirmation_cross_rate_given_h_ab':cross49,'cross_rate_improvement_over_experiment049':cross-cross49,'coverage_improvement_over_experiment049':S['coverage']-O['coverage'],'mean_operational_loss_401_600':losses,'fallback_exact_mismatches':fb}
 if sum(cross_improvements)/len(cross_improvements)<.25:H['H11']=False
 if sum(coverage_improvements)/len(coverage_improvements)<.20:H['H12']=False
 return {'evaluation_seeds':[50000,50999],'replicate_seed_offset':REPLICATE_SEED_OFFSET,'replicate_evaluation_seeds':[5050000,5050999],'n_seeds_per_cell':1000,'cell_count':16,'strategies':STRATEGIES,'audit_seeds':sorted(AUDIT),'audit_replicate_seeds':[s+REPLICATE_SEED_OFFSET for s in sorted(AUDIT)],'bootstrap_seed':50050,'bootstrap_resamples':10000,'hypotheses':H,'e_threshold':E_THRESHOLD,'wrong_action_cost':WRONG_COST,'fallback_cost':FALLBACK_COST,'sign_count':SIGN_COUNT,'positive_cutoff':POSITIVE_CUTOFF,'p28_numerator':P28_NUMERATOR,'p28_denominator':P28_DENOMINATOR,'p28':P28,'p27_numerator':P27_NUMERATOR,'p27_denominator':P27_DENOMINATOR,'p27':P27,'accept_e':ACCEPT_E,'vector_order':VECTOR,'amplitudes':ALL_AMPLITUDES,'amplitude_normalization':AMP_DENOM,'covariance_blocks':'three scale-free [[1,1/2],[1/2,1]] blocks; analytic precision [[4/3,-2/3],[-2/3,4/3]]','discovery_rule':'Experiment-047 primary-stream six-direction covariance-matched nonnegative-amplitude profile selector','confirmation_rule':'primary plus independent confirmation replicate; 40 disjoint held-out pairwise signs; exact Bin(40,0.5) S>=28; terminal E=1/p28 on acceptance else 0','context_rule':'Experiment-031 current-time causal context vote composed by Experiment-032 on primary stream only','symmetry_assumption':'candidate-null disjoint pairwise confirmation contrasts conditionally continuous and symmetric about zero; replicate independent by fixed seed offset','primary_probe_energy':PRIMARY_PROBE_ENERGY,'confirmation_replicate_probe_energy':PRIMARY_PROBE_ENERGY,'total_probe_energy':TOTAL_PROBE_ENERGY,'equal_budget_comparison':False,'full_five_round_latency':True,'no_tuning':True,'operative_spec_issue':OPERATIVE_SPEC_ISSUE,'code_commit':os.environ.get('GITHUB_SHA','unknown'),'mean_cross_rate_improvement_over_experiment049':sum(cross_improvements)/len(cross_improvements),'mean_coverage_improvement_over_experiment049':sum(coverage_improvements)/len(coverage_improvements),'cells':out}
def calibration_values():return calibrations()
