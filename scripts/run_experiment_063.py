#!/usr/bin/env python3
import math,random,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'scripts'))
import experiment_063 as exp63
import experiment_061 as exp61
import run_experiment_055 as base
from experiment_051 import CELLS

SEEDS=range(71000,72000)
AUDIT=set(range(71000,71005))
STRATEGIES=exp63.STRATEGIES
PRIMARY_STRATEGY=exp63.CONFIRMATION_AGREEMENT_STRATEGY
COMPARATOR_STRATEGY=exp63.SIGNED_RANK_30_STRATEGY
W_CUTOFF=exp63.W_CUTOFF
P345_NUMERATOR=exp63.P345_NUMERATOR
P345_DENOMINATOR=exp63.P345_DENOMINATOR
P344_NUMERATOR=exp63.P344_NUMERATOR
P344_DENOMINATOR=exp63.P344_DENOMINATOR
OPERATIVE_SPEC_ISSUE=241
IMPLEMENTATION_CLOSURE_ISSUE=243
BOOTSTRAP_SEED=63063
BOOTSTRAP_RESAMPLES=10000
ROBUSTNESS_SEED_RANGES=exp63.ROBUSTNESS_SEED_RANGES
STRESS_CANDIDATE_ORDER=('H_ab','H_ac','H_bc')
EDGE_PAIRS={
    'H_ab':(('a','b'),('b','a')),
    'H_ac':(('a','c'),('c','a')),
    'H_bc':(('b','c'),('c','b')),
}
T25_UNIT_IQR_DENOM=1.5700273659845985
Z=1.6448536269514722

calibration_values=base.calibration_values
write_csv=base.write_csv
exact_tail=base.exact_tail


def run_experiment_063_strategy(seed,c,strategy,vals):
    return exp63.run_experiment_063_strategy(seed,c,strategy,vals)


def summary(rows,c):
    out=base.summary(rows,c)
    r0=rows[0]
    if r0['strategy']==PRIMARY_STRATEGY:
        for k,v in r0.items():
            if str(k).startswith(('rank55_','rank61_','rank62_','rank63_')):
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
    if int(float(x.get('rank63_spec_issue',0) or 0))!=OPERATIVE_SPEC_ISSUE:return False
    if int(float(x.get('rank63_contrast_count',0) or 0))!=30:return False
    if int(float(x.get('rank63_w_cutoff',0) or 0))!=W_CUTOFF:return False
    if int(float(x.get('rank63_no_extra_observations',0) or 0))!=1:return False
    if int(float(x.get('rank63_candidate_reselected',1)))!=0:return False
    if int(float(x.get('experiment063_exact_repair_from_062',0) or 0))!=1:return False
    vals=[float(x[f'rank55_pair_response_r{r}_{k}']) for r in range(1,6) for k in range(1,7)]
    if len(vals)!=30 or any(v==0 for v in vals) or len(set(abs(v) for v in vals))!=30:return False
    w,ranks=exp63.signed_rank_statistic_30(vals)
    if w!=int(float(x.get('rank63_wplus',-1))):return False
    if w!=int(float(x.get('rank55_wplus',-1))):return False
    if any(int(float(x.get(f'rank55_rank_{i}',-1)))!=ranks[i-1] for i in range(1,31)):return False
    signed_pass=int(w>=W_CUTOFF)
    if int(float(x.get('rank63_signed_rank_pass',-1)))!=signed_pass:return False
    disc=str(x.get('rank63_candidate',''))
    conf=str(x.get('rank63_confirmation_candidate',''))
    if disc!=str(x.get('rank55_candidate','')):return False
    if disc!=_argmax_scores(x,'rank55_Q_'):return False
    if conf!=_argmax_scores(x,'rank61_Qconf_'):return False
    agreement=int(disc==conf)
    if int(float(x.get('rank63_confirmation_agreement',-1)))!=agreement:return False
    accepted=int(signed_pass and agreement)
    if int(float(x['coverage']))!=accepted:return False
    if abs(float(x.get('rank61_e_final',0))-(exp63.ACCEPT_E if accepted else 0.0))>1e-12:return False
    return True


def _bootstrap_interval(values,rng):
    vals=tuple(float(x) for x in values);n=len(vals)
    if n!=1000:raise AssertionError(('bootstrap_seed_count',n))
    means=[]
    for _ in range(BOOTSTRAP_RESAMPLES):
        means.append(sum(vals[rng.randrange(n)] for __ in range(n))/n)
    means.sort()
    lo=means[int(0.025*BOOTSTRAP_RESAMPLES)]
    hi=means[int(0.975*BOOTSTRAP_RESAMPLES)-1]
    return [sum(vals)/n,lo,hi]


def bootstrap_utility(by):
    cov=[];loss=[]
    for seed in SEEDS:
        cd=[];ld=[]
        for c in CELLS:
            label=c['label'];p=by[(label,seed,PRIMARY_STRATEGY)];q=by[(label,seed,COMPARATOR_STRATEGY)]
            cd.append(float(p['coverage'])-float(q['coverage']))
            ld.append(float(p['operational_loss_401_600'])-float(q['operational_loss_401_600']))
        cov.append(sum(cd)/len(cd));loss.append(sum(ld)/len(ld))
    rng=random.Random(BOOTSTRAP_SEED)
    coverage=_bootstrap_interval(cov,rng)
    operational_loss=_bootstrap_interval(loss,rng)
    return {
        'seed':BOOTSTRAP_SEED,'resamples':BOOTSTRAP_RESAMPLES,'resampling_unit':'primary seed with all 16 cells paired',
        'coverage_delta_mean_ci95':coverage,'operational_loss_delta_mean_ci95':operational_loss,
        'quantile_rule':'sorted bootstrap means; indices 250 and 9749 for 2.5% and 97.5%',
    }


def _student_t25(rng):
    z=rng.gauss(0.0,1.0);chi=rng.gammavariate(1.25,2.0)
    return (z/math.sqrt(chi/2.5))/T25_UNIT_IQR_DENOM


def _panel_vector(panel,rng):
    if panel=='R3':
        rho=.5;s=math.sqrt(1-rho*rho);x=rng.gauss(0,1);out=[x]
        for _ in range(29):
            x=rho*x+s*rng.gauss(0,1);out.append(x)
        return out
    out=[]
    scales=(.5,.75,1.0,1.5,2.0)
    for i in range(30):
        round_index=i//6;within=i%6
        if panel=='R1':x=rng.gauss(0,scales[round_index])
        elif panel=='R2':x=rng.gauss(0,1.0 if within<3 else 2.0)
        elif panel=='R4':x=rng.gauss(0,3.0 if rng.random()<.10 else 1.0)
        elif panel=='R5':x=rng.gauss(.75 if rng.random()<.10 else 0.0,1.0)
        elif panel=='R6':x=_student_t25(rng)
        else:raise ValueError(panel)
        out.append(x)
    return out


def _stress_cube(panel,seed,start):
    rng=random.Random(seed)
    while True:
        vectors={h:_panel_vector(panel,rng) for h in STRESS_CANDIDATE_ORDER}
        disc=STRESS_CANDIDATE_ORDER[(seed-start)%len(STRESS_CANDIDATE_ORDER)]
        vals=vectors[disc]
        if any(not math.isfinite(x) for v in vectors.values() for x in v):continue
        if any(x==0.0 for x in vals) or len(set(abs(x) for x in vals))!=30:continue
        cube={}
        for h,v in vectors.items():
            fwd,rev=EDGE_PAIRS[h]
            for r in range(1,6):
                b=(r-1)*6;cube[(r,fwd)]=tuple(v[b:b+3]);cube[(r,rev)]=tuple(v[b+3:b+6])
        if len(cube)!=30 or sum(len(v) for v in cube.values())!=90:raise AssertionError('stress_cube_shape')
        return disc,vectors,cube


def _stress_one(panel,seed,start):
    disc,vectors,cube=_stress_cube(panel,seed,start)
    mats={}
    for r in range(1,6):
        C={pair:sum(cube[(r,pair)])/3.0 for h in STRESS_CANDIDATE_ORDER for pair in EDGE_PAIRS[h]}
        mats[r]=({},C)
    _,_,conf=exp61.confirmation_profile_061(mats)
    vals=vectors[disc];w,_=exp63.signed_rank_statistic_30(vals)
    comparator=int(w>=W_CUTOFF);agreement=int(conf==disc);repaired=int(comparator and agreement)
    return {'seed':seed,'discovery_candidate':disc,'confirmation_candidate':conf,'wplus':w,'agreement':agreement,'comparator_accept':comparator,'repaired_accept':repaired}


def robustness_report():
    panels={};all_pass=True
    for panel,(start,stop) in ROBUSTNESS_SEED_RANGES.items():
        expected=list(range(start,stop))
        if len(expected)!=2000 or len(set(expected))!=2000:raise AssertionError(('robustness_seed_range',panel))
        rows=[_stress_one(panel,seed,start) for seed in expected]
        if [r['seed'] for r in rows]!=expected:raise AssertionError(('robustness_seed_coverage',panel))
        comp=sum(r['comparator_accept'] for r in rows);rep=sum(r['repaired_accept'] for r in rows);removed=comp-rep
        upper=wilson_upper(rep,len(rows));panel_pass=upper<=.01;all_pass=all_pass and panel_pass
        panels[panel]={
            'seed_range':[start,stop-1],'n':len(rows),'comparator_wrong_acceptance':comp/len(rows),
            'repaired_wrong_acceptance':rep/len(rows),'repaired_wrong_n':rep,'repaired_wrong_wilson_upper_95':upper,
            'veto_rate_given_comparator_accept':removed/comp if comp else 0.0,'acceptance_delta':(rep-comp)/len(rows),
            'R_063_panel_pass':panel_pass,
        }
    return all_pass,panels


def report_from(rows):
    if exact_tail(345)!=(P345_NUMERATOR,P345_DENOMINATOR):raise AssertionError('tail345')
    if exact_tail(344)!=(P344_NUMERATOR,P344_DENOMINATOR):raise AssertionError('tail344')
    if not(P345_NUMERATOR/P345_DENOMINATOR<.01<P344_NUMERATOR/P344_DENOMINATOR):raise AssertionError('exact_boundary')
    by={(r['label'],int(r['seed']),r['strategy']):r for r in rows}
    expected={(c['label'],s,st) for c in CELLS for s in SEEDS for st in STRATEGIES}
    if set(by)!=expected:raise AssertionError(('summary_keys',len(by),len(expected)))
    cells={};h5=True;h6=True;integrity_ok=True
    for c in CELLS:
        label=c['label'];primary=[by[(label,s,PRIMARY_STRATEGY)] for s in SEEDS];comparator=[by[(label,s,COMPARATOR_STRATEGY)] for s in SEEDS]
        if not all(integrity(x) for x in primary):integrity_ok=False
        pr=rates(primary);cr=rates(comparator)
        agreement=sum(int(float(x.get('rank63_confirmation_agreement',0) or 0)) for x in primary)/len(primary)
        ploss=sum(float(x['operational_loss_401_600']) for x in primary)/len(primary);closs=sum(float(x['operational_loss_401_600']) for x in comparator)/len(comparator)
        h5_cell=pr['wrong_wilson_upper_95']<=.01;h6_cell=pr['accepted_n']>0 and pr['precision'] is not None and pr['precision']>=.99
        h5=h5 and h5_cell;h6=h6 and h6_cell
        cells[label]={'repaired':pr,'unchanged_comparator':cr,'H5_063_cell_pass':h5_cell,'H6_063_cell_pass':h6_cell,'discovery_confirmation_agreement_rate':agreement,'coverage_delta_vs_comparator':pr['coverage']-cr['coverage'],'operational_loss_401_600':ploss,'comparator_operational_loss_401_600':closs,'operational_loss_delta_vs_comparator':ploss-closs}
    utility=bootstrap_utility(by)
    rpass,robustness=robustness_report()
    branch='D' if not integrity_ok else ('C' if not(h5 and h6) else ('A' if rpass else 'B'))
    return {
        'experiment':63,'operative_spec_issue':OPERATIVE_SPEC_ISSUE,'implementation_closure_issue':IMPLEMENTATION_CLOSURE_ISSUE,
        'evaluation_seeds':[71000,71999],'n_seeds_per_cell':1000,'cell_count':16,'audit_seeds':sorted(AUDIT),
        'strategies':list(STRATEGIES),'primary_strategy':PRIMARY_STRATEGY,'comparator_strategy':COMPARATOR_STRATEGY,
        'H5_063_pass':h5,'H6_063_pass':h6,'R_063_pass':rpass,'integrity_pass':integrity_ok,'interpretation_branch':branch,
        'contrast_count':30,'w_cutoff':W_CUTOFF,'exact_boundary':{'tail_345':[P345_NUMERATOR,P345_DENOMINATOR,P345_NUMERATOR/P345_DENOMINATOR],'tail_344':[P344_NUMERATOR,P344_DENOMINATOR,P344_NUMERATOR/P344_DENOMINATOR]},
        'e_threshold':base.E_THRESHOLD,'accept_e':exp63.ACCEPT_E,
        'repair_rule':'unchanged Experiment 061/062 repair: W+>=345 plus confirmation-topology agreement veto; no reselection',
        'utility_role':'descriptive/decision-support only; never used to tune Experiment 063','utility_bootstrap':utility,
        'robustness_role':'frozen confirmation-level misspecification diagnostics only; no threshold fitting','robustness_panels':robustness,
        'stress_candidate_cycle':list(STRESS_CANDIDATE_ORDER),'t25_unit_iqr_denom':T25_UNIT_IQR_DENOM,
        'no_extra_observations':True,'no_candidate_reselection':True,'no_tuning':True,'cells':cells,
    }
