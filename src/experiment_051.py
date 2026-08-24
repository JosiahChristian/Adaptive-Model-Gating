from __future__ import annotations
from experiment_010 import run_triad_persistence_on_stream
from experiment_016 import groups_from_edges
from experiment_018 import ALL_AMPLITUDES
from experiment_028 import VECTOR
from experiment_032 import _run_composed_gate
from experiment_046 import E_THRESHOLD,split_indices,response_matrices
from experiment_047 import AMP_DENOM,HYP_EDGE,discovery_profile
from experiment_049 import CELLS,PAIR_SIGN_STRATEGY,STRATEGIES as EXP049_STRATEGIES,_pairwise_confirmation,generate_experiment_049_stream,run_experiment_049_strategy

OPERATIVE_SPEC_ISSUE=153
SIGNED_RANK_STRATEGY='covariance_matched_discovery_20contrast_exact_signed_rank_context_composed_risk_gate'
STRATEGIES=(SIGNED_RANK_STRATEGY,)+EXP049_STRATEGIES
CONTRAST_COUNT=20
W_CUTOFF=167
P167_NUMERATOR=10084
P167_DENOMINATOR=1048576
P167=P167_NUMERATOR/P167_DENOMINATOR
P166_NUMERATOR=11264
P166_DENOMINATOR=1048576
P166=P166_NUMERATOR/P166_DENOMINATOR
ACCEPT_E=1.0/P167
PRIMARY_PROBE_ENERGY=sum(15.0*(float(a)**2) for a in ALL_AMPLITUDES)


def generate_experiment_051_stream(seed,c):
 return generate_experiment_049_stream(seed,c)


def signed_rank_statistic(values):
 vals=tuple(float(x) for x in values)
 if len(vals)!=CONTRAST_COUNT:raise AssertionError(len(vals))
 if any(x==0.0 for x in vals):raise AssertionError('zero confirmation contrast')
 absvals=[abs(x) for x in vals]
 if len(set(absvals))!=CONTRAST_COUNT:raise AssertionError('tied absolute confirmation contrasts')
 order=sorted(range(CONTRAST_COUNT),key=lambda i:absvals[i])
 ranks=[0]*CONTRAST_COUNT
 for rank,i in enumerate(order,1):ranks[i]=rank
 wplus=sum(ranks[i] for i,x in enumerate(vals) if x>0.0)
 return wplus,tuple(ranks)


def infer_20contrast_exact_signed_rank(stream):
 mats={r:response_matrices(stream,r) for r in range(1,6)};y,scores,candidate=discovery_profile(mats);edge=HYP_EDGE[candidate]
 path=[];all_values=[]
 for r in range(1,6):
  pairs=_pairwise_confirmation(stream,r,edge);flat=tuple(x for pair in pairs for x in pair);all_values.extend(flat)
  E=0.0;wplus='';ranks=()
  if r==5:
   wplus,ranks=signed_rank_statistic(all_values);E=ACCEPT_E if wplus>=W_CUTOFF else 0.0
  path.append({'stage':r,'candidate':candidate,'e_value':E,'pairwise_responses':flat,'wplus':wplus,'ranks':ranks})
 final=path[-1]['e_value'];accepted=int(final>=E_THRESHOLD)
 return (groups_from_edges([edge]) if accepted else None),accepted,1-accepted,5,path,mats,y,scores


def _annotation(stream,accepted,abstain,path,mats,y,scores):
 cand=path[0]['candidate'];final=path[-1]['e_value'];wplus=path[-1]['wplus']
 out={'probe_gain':stream['probe_gain'],'probe_stop_round':5 if accepted else 0,'probe_energy':PRIMARY_PROBE_ENERGY,'probe_block_count':15,'probe_max_amplitude':float(max(ALL_AMPLITUDES)),
      'provenance_accepted':accepted,'provenance_abstain':abstain,'posterior_deploy_hypothesis':cand if accepted else '','posterior_at_deployment':'','posterior_implied_error_risk':'','posterior_expected_wrong_action_loss':'',
      'rank51_candidate':cand,'rank51_e_threshold':E_THRESHOLD,'rank51_e_final':final,'rank51_discovery_acceptance':0,'rank51_candidate_reselected':0,'rank51_spec_issue':OPERATIVE_SPEC_ISSUE,
      'rank51_rule':'Experiment-047 covariance-matched discovery; Experiment-049 20 disjoint primary-stream pairwise contrasts; exact one-sided Wilcoxon signed-rank W+>=167 terminal e-variable',
      'rank51_amp_denom':AMP_DENOM,'rank51_contrast_count':CONTRAST_COUNT,'rank51_w_cutoff':W_CUTOFF,'rank51_wplus':wplus,
      'rank51_p167_numerator':P167_NUMERATOR,'rank51_p167_denominator':P167_DENOMINATOR,'rank51_p167':P167,
      'rank51_p166_numerator':P166_NUMERATOR,'rank51_p166_denominator':P166_DENOMINATOR,'rank51_p166':P166,'rank51_accept_e':ACCEPT_E,
      'rank51_validity_model':'independent identically distributed continuous symmetric confirmation contrasts','rank51_equal_budget_experiment049':1,'rank51_uses_experiment050_replicate':0}
 for pair,val in zip(VECTOR,y):out['rank51_Y_'+''.join(pair)]=val
 for h,v in scores.items():out['rank51_Q_'+h]=v
 all_values=[]
 for r in range(1,6):
  target,(bd,bc)=split_indices(r);out[f'rank51_baseline_discovery_r{r}']=','.join(map(str,bd));out[f'rank51_baseline_confirmation_r{r}']=','.join(map(str,bc))
  for tgt,(td,tc) in target.items():
   out[f'rank51_target_discovery_r{r}_{tgt}']=','.join(map(str,td));out[f'rank51_target_confirmation_r{r}_{tgt}']=','.join(map(str,tc));out[f'rank51_target_unused_r{r}_{tgt}']=str(tc[2])
  D,_=mats[r]
  for i,j in (('a','b'),('a','c'),('b','c')):
   out[f'rank51_Ddisc_r{r}_{i}{j}']=D[(i,j)];out[f'rank51_Ddisc_r{r}_{j}{i}']=D[(j,i)]
  row=path[r-1];out[f'rank51_e_r{r}']=row['e_value']
  for k,x in enumerate(row['pairwise_responses'],1):out[f'rank51_pair_response_r{r}_{k}']=x;all_values.append(x)
 if path[-1]['ranks']:
  for k,rank in enumerate(path[-1]['ranks'],1):out[f'rank51_rank_{k}']=rank
 out['rank51_zero_count']=sum(int(x==0.0) for x in all_values);out['rank51_abs_tie_count']=CONTRAST_COUNT-len(set(abs(x) for x in all_values))
 return out


def run_experiment_051_strategy(seed,c,strategy,vals):
 if strategy not in STRATEGIES:raise ValueError(strategy)
 if strategy!=SIGNED_RANK_STRATEGY:return run_experiment_049_strategy(seed,c,strategy,vals)
 stream=generate_experiment_051_stream(seed,c);groups,accepted,abstain,stop,path,mats,y,scores=infer_20contrast_exact_signed_rank(stream);ann=_annotation(stream,accepted,abstain,path,mats,y,scores);tau,kappa,k3,la,lb,lc,lab,lac,lbc,*_=vals
 if abstain:
  rows=run_triad_persistence_on_stream(seed,f'experiment051_{c["label"]}',tau,k3,stream)
  for r in rows:r['strategy']=SIGNED_RANK_STRATEGY;r.update(ann)
 else:
  rows=_run_composed_gate(seed,f'experiment051_{c["label"]}',tau,k3,la,lb,lc,lab,lac,lbc,stream,ann,groups)
  for r in rows:r['strategy']=SIGNED_RANK_STRATEGY
 for r in rows:
  r['experiment051_cell']=c['label'];r['experiment051_noise_family']=c['noise_family'];r['experiment051_no_tuning']=1
 return rows
