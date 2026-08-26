#!/usr/bin/env python3
import csv,json,math,random,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_051 import CELLS
import experiment_056 as exp56
from experiment_055 import infer_30contrast_exact_signed_rank,signed_rank_statistic_30,W_CUTOFF
from experiment_057 import EDGE_ORDER,split_contract
from experiment_058 import (
    OPERATIVE_SPEC_ISSUE,SOURCE_SEED_START,SOURCE_SEED_STOP,REPLICA_SEED_OFFSET,
    RANDOMIZATION_SEED,RANDOMIZATION_RESAMPLES,BOOTSTRAP_SEED,BOOTSTRAP_RESAMPLES,
    D5_RANDOMIZATION_RESAMPLES,D5_FIXED_EDGES,D5_METRICS,d5_randomization_seed,
    independent_confirmation_readout,replica_seed,frozen_contract,
)

SEEDS=range(SOURCE_SEED_START,SOURCE_SEED_STOP)
AUDIT=set(range(SOURCE_SEED_START,SOURCE_SEED_START+5))
STRESS={'M1':5851000,'M2':5852000,'M3':5853000,'M4':5854000}
Z=1.6448536269514722


def write_csv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True);fields=[]
    for r in rows:
        for k in r:
            if k not in fields:fields.append(k)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)


def wilson_upper(k,n):
    if not n:return None
    p=k/n;den=1+Z*Z/n;center=(p+Z*Z/(2*n))/den;rad=Z*math.sqrt(p*(1-p)/n+Z*Z/(4*n*n))/den
    return min(1.,center+rad)


def pearson(a,b):
    n=len(a)
    if n<2:return None
    ma=sum(a)/n;mb=sum(b)/n;xa=[x-ma for x in a];xb=[x-mb for x in b]
    da=sum(x*x for x in xa);db=sum(x*x for x in xb)
    if da<=0 or db<=0:return None
    return sum(x*y for x,y in zip(xa,xb))/math.sqrt(da*db)


def diagnostic_row(seed,c):
    rs=replica_seed(seed)
    source=exp56.generate_experiment_056_stream(seed,c)
    replica=exp56.generate_experiment_056_stream(rs,c)
    d=independent_confirmation_readout(source,replica)
    # D1: source path must exactly reproduce the unchanged 30-contrast source reference.
    _,_,_,_,path,_,_,_=infer_30contrast_exact_signed_rank(source)
    ref_selected=path[0]['candidate'];ref_wplus=int(path[-1]['wplus'])
    if d['selected']!=ref_selected or int(d['source_selected_wplus'])!=ref_wplus:
        raise AssertionError(('D1_reference_mismatch',seed,c['label'],d['selected'],ref_selected,d['source_selected_wplus'],ref_wplus))
    if rs!=seed+REPLICA_SEED_OFFSET or SOURCE_SEED_START<=rs<SOURCE_SEED_STOP:
        raise AssertionError(('D1_replica_mapping',seed,rs))
    row={'seed':int(seed),'replica_seed':int(rs),'cell':c['label'],'noise_family':c['noise_family'],'gain':c['gain'],'noise_scale':c['noise_scale'],'selected':d['selected'],'selected_correct':d['selected_correct'],'discovery_margin':d['discovery_margin'],'source_selected_wplus':d['source_selected_wplus'],'replica_selected_wplus':d['replica_selected_wplus'],'source_selected_accept':d['source_selected_accept'],'replica_selected_accept':d['replica_selected_accept'],'spec_issue':OPERATIVE_SPEC_ISSUE,'reference_selected_match':1,'reference_wplus_match':1,'replica_discovery_used_for_selection':0}
    for h in EDGE_ORDER:
        row[f'discovery_score_{h}']=d['discovery_scores'][h]
        for side in ('source','replica'):
            s=d[f'{side}_stats'][h]
            row[f'{side}_{h}_wplus']=s['wplus'];row[f'{side}_{h}_accept']=s['reference_accept'];row[f'{side}_{h}_sign_sum']=s['sign_sum'];row[f'{side}_{h}_mean']=s['mean']
    return row,d


def audit_record(seed,c,d):
    return {'experiment058_cell':c['label'],'source_seed':int(seed),'replica_seed':int(replica_seed(seed)),'spec_issue':OPERATIVE_SPEC_ISSUE,'selected':d['selected'],'replica_discovery_used_for_selection':0,'split_contract':split_contract(),'groups':{h:{'source_vector':list(d['source_vectors'][h]),'replica_vector':list(d['replica_vectors'][h]),'source_wplus':d['source_stats'][h]['wplus'],'replica_wplus':d['replica_stats'][h]['wplus']} for h in EDGE_ORDER}}


def _stress_values(kind,seed):
    rng=random.Random(seed)
    if kind=='M1':
        scales=(.75,1.,1.25,1.5,1.75);return [rng.gauss(0,scales[i//6]) for i in range(30)]
    if kind=='M2':return [rng.gauss(0,1.0 if (i%6)<3 else 1.5) for i in range(30)]
    if kind=='M3':
        rho=.30;x=rng.gauss(0,1);out=[x]
        for _ in range(29):x=rho*x+math.sqrt(1-rho*rho)*rng.gauss(0,1);out.append(x)
        return out
    if kind=='M4':return [rng.gauss(.5 if rng.random()<.10 else 0.0,1.0) for _ in range(30)]
    raise ValueError(kind)


def stress_panel():
    out={}
    for kind,start in STRESS.items():
        accept=0
        for seed in range(start,start+1000):
            w,_=signed_rank_statistic_30(_stress_values(kind,seed));accept+=int(w>=W_CUTOFF)
        out[kind]={'seed_range':[start,start+999],'reference_accept_n':accept,'reference_acceptance':accept/1000,'wilson_upper_95':wilson_upper(accept,1000)}
    return out


def _np():
    import numpy as np
    return np


def _paired_signflip_pvalue(diffs,seed,resamples,alternative='greater'):
    np=_np();d=np.asarray(diffs,dtype=float);d=d[np.isfinite(d)]
    if d.size==0:return None
    obs=float(d.mean());absd=np.abs(d);rng=np.random.default_rng(int(seed));extreme=0;done=0
    # Integer-valued paired differences admit an exact-equivalent grouped Rademacher MC.
    integer=bool(np.allclose(absd,np.rint(absd),rtol=0,atol=1e-12))
    if integer:
        vals,counts=np.unique(np.rint(absd).astype(int),return_counts=True);keep=vals>0;vals=vals[keep];counts=counts[keep]
        while done<resamples:
            b=min(4096,resamples-done)
            if vals.size:
                k=rng.binomial(counts,0.5,size=(b,len(counts)))
                sums=((2*k-counts)*vals).sum(axis=1)/d.size
            else:sums=np.zeros(b)
            extreme+=int(np.sum(sums>=obs-1e-15)) if alternative=='greater' else int(np.sum(np.abs(sums)>=abs(obs)-1e-15));done+=b
    else:
        while done<resamples:
            b=min(128,resamples-done);signs=rng.integers(0,2,size=(b,d.size),dtype=np.int8)*2-1;sums=(signs@d)/d.size
            extreme+=int(np.sum(sums>=obs-1e-15)) if alternative=='greater' else int(np.sum(np.abs(sums)>=abs(obs)-1e-15));done+=b
    return {'observed_mean_difference':obs,'pvalue':(extreme+1)/(resamples+1),'resamples':int(resamples),'seed':int(seed),'alternative':alternative}


def _corr_np(x,y):
    np=_np();x=np.asarray(x,dtype=float);y=np.asarray(y,dtype=float);xm=x-x.mean();ym=y-y.mean();den=np.sqrt((xm*xm).sum()*(ym*ym).sum());return float((xm*ym).sum()/den) if den>0 else float('nan')


def _bootstrap_coupling(q):
    np=_np();n=len(q)
    if n<3:return None
    m=np.asarray([float(r['discovery_margin']) for r in q]);pairs=[]
    for metric in ('wplus','sign_sum','mean'):
        s=np.asarray([float(r[f"source_{r['selected']}_{metric}"]) for r in q]);p=np.asarray([float(r[f"replica_{r['selected']}_{metric}"]) for r in q]);pairs.append((metric,s,p))
    point={metric:{'source':_corr_np(m,s),'replica':_corr_np(m,p)} for metric,s,p in pairs}
    for metric in point:point[metric]['source_minus_replica']=point[metric]['source']-point[metric]['replica']
    rng=np.random.default_rng(BOOTSTRAP_SEED);draws={metric:[] for metric,_,_ in pairs};done=0
    while done<BOOTSTRAP_RESAMPLES:
        b=min(16,BOOTSTRAP_RESAMPLES-done);idx=rng.integers(0,n,size=(b,n));xb=m[idx];xm=xb-xb.mean(axis=1,keepdims=True);xss=(xm*xm).sum(axis=1)
        for metric,s,p in pairs:
            sb=s[idx];pb=p[idx];sm=sb-sb.mean(axis=1,keepdims=True);pm=pb-pb.mean(axis=1,keepdims=True)
            cs=(xm*sm).sum(axis=1)/np.sqrt(xss*(sm*sm).sum(axis=1));cp=(xm*pm).sum(axis=1)/np.sqrt(xss*(pm*pm).sum(axis=1));draws[metric].extend((cs-cp).tolist())
        done+=b
    for metric in point:
        a=np.asarray(draws[metric]);point[metric]['bootstrap_95_interval']=[float(np.quantile(a,.025)),float(np.quantile(a,.975))];point[metric]['bootstrap_seed']=BOOTSTRAP_SEED;point[metric]['bootstrap_resamples']=BOOTSTRAP_RESAMPLES
    return point


def _median(values):
    s=sorted(float(x) for x in values);n=len(s)
    if not n:return None
    return s[n//2] if n%2 else .5*(s[n//2-1]+s[n//2])


def _d2(q,label):
    if not q:return {'label':label,'n':0}
    diffs=[float(r['source_selected_wplus'])-float(r['replica_selected_wplus']) for r in q]
    return {'label':label,'n':len(q),'paired_mean_wplus_difference':sum(diffs)/len(diffs),'paired_median_wplus_difference':_median(diffs),'fraction_source_gt_replica':sum(d>0 for d in diffs)/len(diffs),'one_sided_signflip':_paired_signflip_pvalue(diffs,RANDOMIZATION_SEED,RANDOMIZATION_RESAMPLES,'greater')}


def _d3(q):
    out={'n':len(q)}
    for side in ('source','replica'):
        k=sum(int(r[f'{side}_selected_accept']) for r in q);out[side]={'accept_n':k,'acceptance':k/len(q) if q else None,'wilson_upper_95':wilson_upper(k,len(q)) if q else None}
    return out


def _holm(items):
    m=len(items);order=sorted(range(m),key=lambda i:items[i]['raw_pvalue']);running=0.0
    for rank,i in enumerate(order):
        adj=min(1.0,(m-rank)*items[i]['raw_pvalue']);running=max(running,adj);items[i]['holm_pvalue']=running
    return items


def _d5_cell(q,cell_index):
    tests=[]
    for ei,h in enumerate(D5_FIXED_EDGES):
        for mi,metric in enumerate(D5_METRICS):
            field={'acceptance':'accept','wplus':'wplus','sign_sum':'sign_sum','confirmation_mean':'mean'}[metric]
            diffs=[float(r[f'source_{h}_{field}'])-float(r[f'replica_{h}_{field}']) for r in q]
            seed=d5_randomization_seed(cell_index,ei,mi);p=_paired_signflip_pvalue(diffs,seed,D5_RANDOMIZATION_RESAMPLES,'two-sided')
            tests.append({'edge':h,'metric':metric,'n':len(diffs),'paired_mean_difference':sum(diffs)/len(diffs),'paired_median_difference':_median(diffs),'raw_pvalue':p['pvalue'],'randomization_seed':seed,'randomization_resamples':D5_RANDOMIZATION_RESAMPLES})
    return _holm(tests)


def report_from(rows):
    expected=len(CELLS)*len(SEEDS)
    if len(rows)!=expected:raise AssertionError(('row_count',len(rows),expected))
    if any(int(r['spec_issue'])!=OPERATIVE_SPEC_ISSUE or int(r['reference_selected_match'])!=1 or int(r['reference_wplus_match'])!=1 or int(r['replica_discovery_used_for_selection'])!=0 for r in rows):raise AssertionError('D1 row integrity')
    wrong=[r for r in rows if not int(r['selected_correct'])]
    strata={'correct_H_ab':[r for r in rows if r['selected']=='H_ab'],'wrong_H_ac':[r for r in rows if r['selected']=='H_ac'],'wrong_H_bc':[r for r in rows if r['selected']=='H_bc'],'wrong_all':wrong}
    report={'experiment':58,'operative_spec_issue':OPERATIVE_SPEC_ISSUE,'diagnostic_only':True,'source_seed_range':[SOURCE_SEED_START,SOURCE_SEED_STOP-1],'replica_seed_offset':REPLICA_SEED_OFFSET,'w_cutoff_reference_only':W_CUTOFF,'frozen_contract':frozen_contract(),'D1_integrity':{'all_reference_selected_match':True,'all_reference_wplus_match':True,'all_replica_discovery_excluded':True,'all_replica_mappings_valid':all(int(r['replica_seed'])==int(r['seed'])+REPLICA_SEED_OFFSET for r in rows),'split_contract':split_contract()},'D2_matched_wrong_selection':_d2(wrong,'wrong_all'),'D3_wrong_selected_acceptance':{'global':_d3(wrong),'cells':{}},'D4_discovery_coupling':{},'D5_fixed_edge_law_parity':{},'D6_candidate_strata':{},'D7_stress_panel':stress_panel(),'no_tuning':True}
    for ci,c in enumerate(CELLS):
        q=[r for r in rows if r['cell']==c['label']];qw=[r for r in q if not int(r['selected_correct'])]
        report['D3_wrong_selected_acceptance']['cells'][c['label']]=_d3(qw)
        report['D5_fixed_edge_law_parity'][c['label']]=_d5_cell(q,ci)
    for name,q in strata.items():
        coupling=_bootstrap_coupling(q)
        report['D6_candidate_strata'][name]={'n':len(q),'D2':_d2(q,name),'D3':_d3(q),'D4':coupling}
        if name=='wrong_all':report['D4_discovery_coupling']['wrong_all']=coupling
    return report
