from __future__ import annotations
import math
from statistics import NormalDist
from experiment_010 import run_triad_persistence_on_stream
from experiment_016 import groups_from_edges
from experiment_018 import ALL_AMPLITUDES
from experiment_028 import VECTOR
from experiment_032 import _run_composed_gate
from experiment_046 import E_THRESHOLD,split_indices,response_matrices
from experiment_047 import AMP_DENOM,HYP_EDGE,discovery_profile
from experiment_049 import _pairwise_confirmation,generate_experiment_049_stream
import experiment_051 as exp51

OPERATIVE_SPEC_ISSUE=173
FAMILY_MIXTURE_STRATEGY='covariance_matched_discovery_20contrast_exact_rank_conditioned_family_mixture_context_composed_risk_gate'
STRATEGIES=(FAMILY_MIXTURE_STRATEGY,)+exp51.STRATEGIES
CONTRAST_COUNT=20
THETAS=(0.5,1.0,2.0,4.0)
FAMILIES=('sign','wilcoxon','normal')
COMPONENT_COUNT=12
MIXTURE_WEIGHT=1.0/12.0
NULL_PATTERN_COUNT=1<<20
ACCEPT_PATTERN_COUNT=10485
P_STAR=ACCEPT_PATTERN_COUNT/NULL_PATTERN_COUNT
BF_ACCEPTED_LOW=8.473780594324499
BF_REJECTED_HIGH=8.473517919478537
BF_CUTOFF=8.473649256901517
ACCEPT_E=1.0/P_STAR
PRIMARY_PROBE_ENERGY=sum(15.0*(float(a)**2) for a in ALL_AMPLITUDES)
_ND=NormalDist()
_q=tuple(_ND.inv_cdf(0.5+0.5*r/21.0) for r in range(1,21))
SCORE_MAPS={
 'sign':tuple(1.0 for _ in range(CONTRAST_COUNT)),
 'wilcoxon':tuple(r/20.0 for r in range(1,21)),
 'normal':tuple(v/_q[-1] for v in _q),
}

def _logistic(x):
 if x>=0:
  z=math.exp(-x);return 1.0/(1.0+z)
 z=math.exp(x);return z/(1.0+z)

def rank_signs(values):
 vals=tuple(float(x) for x in values)
 if len(vals)!=CONTRAST_COUNT:raise AssertionError(len(vals))
 if any(x==0.0 for x in vals):raise AssertionError('zero confirmation contrast')
 av=tuple(abs(x) for x in vals)
 if len(set(av))!=CONTRAST_COUNT:raise AssertionError('tied absolute confirmation contrasts')
 order=sorted(range(CONTRAST_COUNT),key=lambda i:av[i])
 ranks=[0]*CONTRAST_COUNT;signs_by_rank=[]
 for rank,i in enumerate(order,1):
  ranks[i]=rank;signs_by_rank.append(1 if vals[i]>0 else -1)
 return tuple(ranks),tuple(signs_by_rank)

def family_mixture_bf_from_signs(signs_by_rank):
 signs=tuple(int(s) for s in signs_by_rank)
 if len(signs)!=CONTRAST_COUNT or any(s not in (-1,1) for s in signs):raise AssertionError('invalid sign pattern')
 total=0.0
 for family in FAMILIES:
  scores=SCORE_MAPS[family]
  for theta in THETAS:
   logq=0.0
   for s,a in zip(signs,scores):
    p=_logistic(theta*a)
    logq+=math.log(p if s>0 else 1.0-p)
   total+=math.exp(logq)
 return NULL_PATTERN_COUNT*MIXTURE_WEIGHT*total

def family_mixture_statistic(values):
 ranks,signs=rank_signs(values);bf=family_mixture_bf_from_signs(signs)
 return bf,ranks,signs

def enumerate_null_boundary():
 # Exhaustive independent implementation of the prospectively frozen conditional null.
 # DFS accumulates rank-score sums without recursive product drift.
 maps=tuple(SCORE_MAPS[f] for f in FAMILIES)
 bases=[]
 for scores in maps:
  fb=[]
  for theta in THETAS:
   ps=tuple(_logistic(theta*a) for a in scores)
   fb.append((theta,sum(math.log1p(-p) for p in ps)))
  bases.append(tuple(fb))
 count=0;accepted_low=float('inf');rejected_high=float('-inf')
 def walk(r,s0,s1,s2):
  nonlocal count,accepted_low,rejected_high
  if r==CONTRAST_COUNT:
   sums=(s0,s1,s2);tot=0.0
   for j in range(3):
    for theta,logbase in bases[j]:tot+=math.exp(logbase+theta*sums[j])
   bf=NULL_PATTERN_COUNT*MIXTURE_WEIGHT*tot
   if bf>=BF_CUTOFF:
    count+=1
    if bf<accepted_low:accepted_low=bf
   elif bf>rejected_high:rejected_high=bf
   return
  walk(r+1,s0,s1,s2)
  walk(r+1,s0+maps[0][r],s1+maps[1][r],s2+maps[2][r])
 walk(0,0.0,0.0,0.0)
 return {'pattern_count':NULL_PATTERN_COUNT,'accepted_count':count,'accepted_low':accepted_low,'rejected_high':rejected_high,'cutoff':BF_CUTOFF,'p_star':P_STAR,'accept_e':ACCEPT_E}

def generate_experiment_054_stream(seed,c):return generate_experiment_049_stream(seed,c)

def infer_20contrast_family_mixture(stream):
 mats={r:response_matrices(stream,r) for r in range(1,6)};y,scores,candidate=discovery_profile(mats);edge=HYP_EDGE[candidate]
 path=[];all_values=[]
 for r in range(1,6):
  pairs=_pairwise_confirmation(stream,r,edge);flat=tuple(x for pair in pairs for x in pair);all_values.extend(flat)
  E=0.0;bf='';ranks=();signs=()
  if r==5:
   bf,ranks,signs=family_mixture_statistic(all_values);E=ACCEPT_E if bf>=BF_CUTOFF else 0.0
  path.append({'stage':r,'candidate':candidate,'e_value':E,'pairwise_responses':flat,'bf':bf,'ranks':ranks,'signs_by_rank':signs})
 final=path[-1]['e_value'];accepted=int(final>=E_THRESHOLD)
 return (groups_from_edges([edge]) if accepted else None),accepted,1-accepted,5,path,mats,y,scores

def _annotation(stream,accepted,abstain,path,mats,y,scores):
 cand=path[0]['candidate'];last=path[-1];final=last['e_value'];bf=last['bf']
 out={'probe_gain':stream['probe_gain'],'probe_stop_round':5 if accepted else 0,'probe_energy':PRIMARY_PROBE_ENERGY,'probe_block_count':15,'probe_max_amplitude':float(max(ALL_AMPLITUDES)),
      'provenance_accepted':accepted,'provenance_abstain':abstain,'posterior_deploy_hypothesis':cand if accepted else '','posterior_at_deployment':'','posterior_implied_error_risk':'','posterior_expected_wrong_action_loss':'',
      'mix54_candidate':cand,'mix54_e_threshold':E_THRESHOLD,'mix54_e_final':final,'mix54_discovery_acceptance':0,'mix54_candidate_reselected':0,'mix54_spec_issue':OPERATIVE_SPEC_ISSUE,
      'mix54_rule':'Experiment-047 covariance-matched discovery; Experiment-049 20 disjoint primary-stream pairwise contrasts; exact rank-conditioned 3-family x 4-theta sign-pattern mixture ordering with exhaustive <=1% conditional null rejection region',
      'mix54_amp_denom':AMP_DENOM,'mix54_contrast_count':CONTRAST_COUNT,'mix54_bf':bf,'mix54_bf_cutoff':BF_CUTOFF,'mix54_accept_pattern_count':ACCEPT_PATTERN_COUNT,'mix54_null_pattern_count':NULL_PATTERN_COUNT,'mix54_p_star':P_STAR,'mix54_accept_e':ACCEPT_E,
      'mix54_families':','.join(FAMILIES),'mix54_thetas':','.join(str(x) for x in THETAS),'mix54_component_count':COMPONENT_COUNT,'mix54_mixture_weight':MIXTURE_WEIGHT,
      'mix54_validity_model':'conditional on discovery and absolute magnitudes/ranks, 20 confirmation signs are independent fair Rademacher variables','mix54_equal_budget_experiment053':1,'mix54_uses_experiment050_replicate':0}
 for pair,val in zip(VECTOR,y):out['mix54_Y_'+''.join(pair)]=val
 for h,v in scores.items():out['mix54_Q_'+h]=v
 all_values=[]
 for r in range(1,6):
  target,(bd,bc)=split_indices(r);out[f'mix54_baseline_discovery_r{r}']=','.join(map(str,bd));out[f'mix54_baseline_confirmation_r{r}']=','.join(map(str,bc))
  for tgt,(td,tc) in target.items():
   out[f'mix54_target_discovery_r{r}_{tgt}']=','.join(map(str,td));out[f'mix54_target_confirmation_r{r}_{tgt}']=','.join(map(str,tc));out[f'mix54_target_unused_r{r}_{tgt}']=str(tc[2])
  D,_=mats[r]
  for i,j in (('a','b'),('a','c'),('b','c')):
   out[f'mix54_Ddisc_r{r}_{i}{j}']=D[(i,j)];out[f'mix54_Ddisc_r{r}_{j}{i}']=D[(j,i)]
  row=path[r-1];out[f'mix54_e_r{r}']=row['e_value']
  for k,x in enumerate(row['pairwise_responses'],1):out[f'mix54_pair_response_r{r}_{k}']=x;all_values.append(x)
 for k,rank in enumerate(last['ranks'],1):out[f'mix54_rank_{k}']=rank
 for k,s in enumerate(last['signs_by_rank'],1):out[f'mix54_sign_by_rank_{k}']=s
 out['mix54_zero_count']=sum(int(x==0.0) for x in all_values);out['mix54_abs_tie_count']=CONTRAST_COUNT-len(set(abs(x) for x in all_values))
 return out

def run_experiment_054_strategy(seed,c,strategy,vals):
 if strategy not in STRATEGIES:raise ValueError(strategy)
 if strategy!=FAMILY_MIXTURE_STRATEGY:return exp51.run_experiment_051_strategy(seed,c,strategy,vals)
 stream=generate_experiment_054_stream(seed,c);groups,accepted,abstain,stop,path,mats,y,scores=infer_20contrast_family_mixture(stream);ann=_annotation(stream,accepted,abstain,path,mats,y,scores);tau,kappa,k3,la,lb,lc,lab,lac,lbc,*_=vals
 if abstain:
  rows=run_triad_persistence_on_stream(seed,f'experiment054_{c["label"]}',tau,k3,stream)
  for row in rows:row['strategy']=FAMILY_MIXTURE_STRATEGY;row.update(ann)
 else:
  rows=_run_composed_gate(seed,f'experiment054_{c["label"]}',tau,k3,la,lb,lc,lab,lac,lbc,stream,ann,groups)
  for row in rows:row['strategy']=FAMILY_MIXTURE_STRATEGY
 for row in rows:
  row['experiment054_cell']=c['label'];row['experiment054_noise_family']=c['noise_family'];row['experiment054_no_tuning']=1
 return rows
