#!/usr/bin/env python3
import math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'scripts'))
import experiment_061 as exp61
import run_experiment_055 as base
from experiment_051 import CELLS

SEEDS=range(69000,70000)
AUDIT=set(range(69000,69005))
STRATEGIES=exp61.STRATEGIES
PRIMARY_STRATEGY=exp61.CONFIRMATION_AGREEMENT_STRATEGY
COMPARATOR_STRATEGY=exp61.SIGNED_RANK_30_STRATEGY
W_CUTOFF=exp61.W_CUTOFF
P345_NUMERATOR=exp61.P345_NUMERATOR
P345_DENOMINATOR=exp61.P345_DENOMINATOR
P344_NUMERATOR=exp61.P344_NUMERATOR
P344_DENOMINATOR=exp61.P344_DENOMINATOR
OPERATIVE_SPEC_ISSUE=226
Z=1.6448536269514722

calibration_values=base.calibration_values
write_csv=base.write_csv
exact_tail=base.exact_tail


def run_experiment_061_strategy(seed,c,strategy,vals):
    return exp61.run_experiment_061_strategy(seed,c,strategy,vals)


def summary(rows,c):
    out=base.summary(rows,c)
    r0=rows[0]
    if r0['strategy']==PRIMARY_STRATEGY:
        for k,v in r0.items():
            if str(k).startswith('rank55_') or str(k).startswith('rank61_'):
                out[k]=v
    return out


def wilson_upper(k,n):
    if n<=0:return 1.0
    p=k/n;den=1+Z*Z/n
    center=(p+Z*Z/(2*n))/den
    rad=Z*math.sqrt(p*(1-p)/n+Z*Z/(4*n*n))/den
    return min(1.0,center+rad)


def rates(q):
    accepted=[x for x in q if int(float(x['coverage']))]
    wrong=sum(int(float(x['wrong_accept'])) for x in q)
    correct=sum(int(float(x['correct'])) for x in accepted)
    return {
        'coverage':len(accepted)/len(q),
        'accepted_n':len(accepted),
        'wrong_n':wrong,
        'wrong_acceptance':wrong/len(q),
        'wrong_wilson_upper_95':wilson_upper(wrong,len(q)),
        'precision':correct/len(accepted) if accepted else None,
    }


def _argmax_scores(x,prefix):
    order=('H_ab','H_ac','H_bc')
    scores={h:float(x[prefix+h]) for h in order}
    return max(order,key=lambda h:(scores[h],-order.index(h)))


def integrity(x):
    if int(float(x.get('rank61_spec_issue',0) or 0))!=OPERATIVE_SPEC_ISSUE:return False
    if int(float(x.get('rank61_contrast_count',0) or 0))!=30:return False
    if int(float(x.get('rank61_w_cutoff',0) or 0))!=W_CUTOFF:return False
    if int(float(x.get('rank61_no_extra_observations',0) or 0))!=1:return False
    if int(float(x.get('rank61_candidate_reselected',1)))!=0:return False
    vals=[float(x[f'rank55_pair_response_r{r}_{k}']) for r in range(1,6) for k in range(1,7)]
    if len(vals)!=30 or any(v==0 for v in vals) or len(set(abs(v) for v in vals))!=30:return False
    w,ranks=exp61.signed_rank_statistic_30(vals)
    if w!=int(float(x.get('rank61_wplus',-1))):return False
    if w!=int(float(x.get('rank55_wplus',-1))):return False
    if any(int(float(x.get(f'rank55_rank_{i}',-1)))!=ranks[i-1] for i in range(1,31)):return False
    signed_pass=int(w>=W_CUTOFF)
    if int(float(x.get('rank61_signed_rank_pass',-1)))!=signed_pass:return False
    disc=str(x.get('rank61_candidate',''))
    conf=str(x.get('rank61_confirmation_candidate',''))
    if disc!=str(x.get('rank55_candidate','')):return False
    if disc!=_argmax_scores(x,'rank55_Q_'):return False
    if conf!=_argmax_scores(x,'rank61_Qconf_'):return False
    agreement=int(disc==conf)
    if int(float(x.get('rank61_confirmation_agreement',-1)))!=agreement:return False
    accepted=int(signed_pass and agreement)
    if int(float(x['coverage']))!=accepted:return False
    if abs(float(x.get('rank61_e_final',0))-(exp61.ACCEPT_E if accepted else 0.0))>1e-12:return False
    return True


def report_from(rows):
    if exact_tail(345)!=(P345_NUMERATOR,P345_DENOMINATOR):raise AssertionError('tail345')
    if exact_tail(344)!=(P344_NUMERATOR,P344_DENOMINATOR):raise AssertionError('tail344')
    if not(P345_NUMERATOR/P345_DENOMINATOR<.01<P344_NUMERATOR/P344_DENOMINATOR):raise AssertionError('exact_boundary')
    cells={};h5=True;h6=True;integrity_ok=True
    for c in CELLS:
        label=c['label'];sr=[r for r in rows if r['label']==label]
        by={(int(r['seed']),r['strategy']):r for r in sr}
        expected={(s,st) for s in SEEDS for st in STRATEGIES}
        if set(by)!=expected:raise AssertionError(('cell_summary_keys',label,len(by),len(expected)))
        primary=[by[(s,PRIMARY_STRATEGY)] for s in SEEDS]
        comparator=[by[(s,COMPARATOR_STRATEGY)] for s in SEEDS]
        if not all(integrity(x) for x in primary):integrity_ok=False
        pr=rates(primary);cr=rates(comparator)
        agreement=sum(int(float(x.get('rank61_confirmation_agreement',0) or 0)) for x in primary)/len(primary)
        ploss=sum(float(x['operational_loss_401_600']) for x in primary)/len(primary)
        closs=sum(float(x['operational_loss_401_600']) for x in comparator)/len(comparator)
        h5_cell=pr['wrong_wilson_upper_95']<=.01
        h6_cell=pr['accepted_n']>0 and pr['precision'] is not None and pr['precision']>=.99
        h5=h5 and h5_cell;h6=h6 and h6_cell
        cells[label]={
            'repaired':pr,
            'unchanged_comparator':cr,
            'H5_061_cell_pass':h5_cell,
            'H6_061_cell_pass':h6_cell,
            'discovery_confirmation_agreement_rate':agreement,
            'coverage_delta_vs_comparator':pr['coverage']-cr['coverage'],
            'operational_loss_401_600':ploss,
            'comparator_operational_loss_401_600':closs,
            'operational_loss_delta_vs_comparator':ploss-closs,
        }
    return {
        'experiment':61,
        'operative_spec_issue':OPERATIVE_SPEC_ISSUE,
        'evaluation_seeds':[69000,69999],
        'n_seeds_per_cell':1000,
        'cell_count':16,
        'audit_seeds':sorted(AUDIT),
        'strategies':list(STRATEGIES),
        'primary_strategy':PRIMARY_STRATEGY,
        'comparator_strategy':COMPARATOR_STRATEGY,
        'H5_061_pass':h5,
        'H6_061_pass':h6,
        'integrity_pass':integrity_ok,
        'interpretation_branch':('D' if not integrity_ok else ('C' if not h5 else ('A' if h6 else 'B'))),
        'contrast_count':30,
        'w_cutoff':W_CUTOFF,
        'exact_boundary':{
            'tail_345':[P345_NUMERATOR,P345_DENOMINATOR,P345_NUMERATOR/P345_DENOMINATOR],
            'tail_344':[P344_NUMERATOR,P344_DENOMINATOR,P344_NUMERATOR/P344_DENOMINATOR],
        },
        'e_threshold':base.E_THRESHOLD,
        'accept_e':exp61.ACCEPT_E,
        'repair_rule':'deploy iff unchanged W+>=345 passes for discovery-selected candidate and confirmation-only topology argmax agrees; agreement is veto-only',
        'utility_role':'descriptive only in Experiment 061',
        'no_extra_observations':True,
        'no_candidate_reselection':True,
        'no_tuning':True,
        'cells':cells,
    }
