from __future__ import annotations
from experiment_010 import run_triad_persistence_on_stream
from experiment_016 import groups_from_edges
from experiment_018 import ALL_AMPLITUDES
from experiment_046 import E_THRESHOLD,response_matrices
from experiment_047 import AMP_DENOM,HYP_EDGE,discovery_profile
from experiment_049 import CELLS,PAIR_SIGN_STRATEGY,STRATEGIES as EXP049_STRATEGIES,_pairwise_confirmation,generate_experiment_049_stream,run_experiment_049_strategy
from experiment_032 import _run_composed_gate

OPERATIVE_SPEC_ISSUE=145
REPLICATE_SEED_OFFSET=5000000
REPLICATED_SIGN_STRATEGY='covariance_matched_discovery_40sign_replicated_exact_binomial_context_composed_risk_gate'
STRATEGIES=(REPLICATED_SIGN_STRATEGY,)+EXP049_STRATEGIES
SIGN_COUNT=40
POSITIVE_CUTOFF=28
P28_NUMERATOR=9119901052
P28_DENOMINATOR=1099511627776
P28=P28_NUMERATOR/P28_DENOMINATOR
P27_NUMERATOR=21153123932
P27_DENOMINATOR=1099511627776
P27=P27_NUMERATOR/P27_DENOMINATOR
ACCEPT_E=1.0/P28
PRIMARY_PROBE_ENERGY=sum(15.0*(float(a)**2) for a in ALL_AMPLITUDES)
TOTAL_PROBE_ENERGY=2.0*PRIMARY_PROBE_ENERGY


def generate_experiment_050_streams(seed,c):
 return generate_experiment_049_stream(seed,c),generate_experiment_049_stream(seed+REPLICATE_SEED_OFFSET,c)

def infer_40sign_replicated_exact_binomial(primary,replicate):
 mats={r:response_matrices(primary,r) for r in range(1,6)};y,scores,candidate=discovery_profile(mats);edge=HYP_EDGE[candidate]
 path=[];positive=0;zero=0
 for r in range(1,6):
  p_primary=_pairwise_confirmation(primary,r,edge);p_replicate=_pairwise_confirmation(replicate,r,edge)
  primary_flat=tuple(x for pair in p_primary for x in pair);replicate_flat=tuple(x for pair in p_replicate for x in pair);flat=primary_flat+replicate_flat
  positive+=sum(int(x>0.0) for x in flat);zero+=sum(int(x==0.0) for x in flat)
  terminal=int(r==5);E=(ACCEPT_E if terminal and positive>=POSITIVE_CUTOFF else 0.0)
  path.append({'stage':r,'candidate':candidate,'e_value':E,'primary_pairwise_responses':primary_flat,'replicate_pairwise_responses':replicate_flat,'positive_sign_count':positive,'zero_sign_count':zero})
 final=path[-1]['e_value'];accepted=int(final>=E_THRESHOLD)
 return (groups_from_edges([edge]) if accepted else None),accepted,1-accepted,5,path,mats,y,scores

def _annotation(primary,seed,accepted,abstain,path,mats,y,scores):
 cand=path[0]['candidate'];final=path[-1]['e_value']
 out={'probe_gain':primary['probe_gain'],'probe_stop_round':5 if accepted else 0,'probe_energy':PRIMARY_PROBE_ENERGY,'probe_block_count':15,'probe_max_amplitude':float(max(ALL_AMPLITUDES)),
      'provenance_accepted':accepted,'provenance_abstain':abstain,'posterior_deploy_hypothesis':cand if accepted else '','posterior_at_deployment':'','posterior_implied_error_risk':'','posterior_expected_wrong_action_loss':'',
      'sign50_candidate':cand,'sign50_e_threshold':E_THRESHOLD,'sign50_e_final':final,'sign50_discovery_acceptance':0,'sign50_candidate_reselected':0,'sign50_spec_issue':OPERATIVE_SPEC_ISSUE,
      'sign50_rule':'Experiment-047 primary-stream covariance-matched discovery; primary plus independent confirmation replicate; 40 disjoint held-out pairwise signs; exact Bin(40,0.5) S>=28 terminal e-variable',
      'sign50_amp_denom':AMP_DENOM,'sign50_sign_count':SIGN_COUNT,'sign50_positive_cutoff':POSITIVE_CUTOFF,'sign50_p28_numerator':P28_NUMERATOR,'sign50_p28_denominator':P28_DENOMINATOR,'sign50_p28':P28,
      'sign50_p27_numerator':P27_NUMERATOR,'sign50_p27_denominator':P27_DENOMINATOR,'sign50_p27':P27,'sign50_accept_e':ACCEPT_E,'sign50_primary_seed':seed,'sign50_replicate_seed':seed+REPLICATE_SEED_OFFSET,
      'sign50_replicate_seed_offset':REPLICATE_SEED_OFFSET,'sign50_positive_sign_count':path[-1]['positive_sign_count'],'sign50_zero_sign_count':path[-1]['zero_sign_count'],
      'sign50_primary_probe_energy':PRIMARY_PROBE_ENERGY,'sign50_confirmation_replicate_probe_energy':PRIMARY_PROBE_ENERGY,'sign50_total_probe_energy':TOTAL_PROBE_ENERGY,'sign50_equal_budget_comparison':0}
 from experiment_028 import VECTOR
 from experiment_046 import split_indices
 for pair,val in zip(VECTOR,y):out['sign50_Y_'+''.join(pair)]=val
 for h,v in scores.items():out['sign50_Q_'+h]=v
 for r in range(1,6):
  target,(bd,bc)=split_indices(r);out[f'sign50_baseline_discovery_r{r}']=','.join(map(str,bd));out[f'sign50_baseline_confirmation_r{r}']=','.join(map(str,bc))
  for tgt,(td,tc) in target.items():
   out[f'sign50_target_discovery_r{r}_{tgt}']=','.join(map(str,td));out[f'sign50_target_confirmation_r{r}_{tgt}']=','.join(map(str,tc));out[f'sign50_target_unused_r{r}_{tgt}']=str(tc[2])
  D,_=mats[r]
  for i,j in (('a','b'),('a','c'),('b','c')):
   out[f'sign50_Ddisc_r{r}_{i}{j}']=D[(i,j)];out[f'sign50_Ddisc_r{r}_{j}{i}']=D[(j,i)]
  row=path[r-1];out[f'sign50_e_r{r}']=row['e_value'];out[f'sign50_positive_count_r{r}']=row['positive_sign_count'];out[f'sign50_zero_count_r{r}']=row['zero_sign_count']
  for k,x in enumerate(row['primary_pairwise_responses'],1):out[f'sign50_primary_pair_response_r{r}_{k}']=x
  for k,x in enumerate(row['replicate_pairwise_responses'],1):out[f'sign50_replicate_pair_response_r{r}_{k}']=x
 return out

def run_experiment_050_strategy(seed,c,strategy,vals):
 if strategy not in STRATEGIES:raise ValueError(strategy)
 if strategy!=REPLICATED_SIGN_STRATEGY:return run_experiment_049_strategy(seed,c,strategy,vals)
 primary,replicate=generate_experiment_050_streams(seed,c);groups,accepted,abstain,stop,path,mats,y,scores=infer_40sign_replicated_exact_binomial(primary,replicate);ann=_annotation(primary,seed,accepted,abstain,path,mats,y,scores);tau,kappa,k3,la,lb,lc,lab,lac,lbc,*_=vals
 if abstain:
  rows=run_triad_persistence_on_stream(seed,f'experiment050_{c["label"]}',tau,k3,primary)
  for r in rows:r['strategy']=REPLICATED_SIGN_STRATEGY;r.update(ann)
 else:
  rows=_run_composed_gate(seed,f'experiment050_{c["label"]}',tau,k3,la,lb,lc,lab,lac,lbc,primary,ann,groups)
  for r in rows:r['strategy']=REPLICATED_SIGN_STRATEGY
 for r in rows:
  r['experiment050_cell']=c['label'];r['experiment050_noise_family']=c['noise_family'];r['experiment050_no_tuning']=1
 return rows
