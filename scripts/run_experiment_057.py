#!/usr/bin/env python3
import csv,json,math,random,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_051 import CELLS
import experiment_056 as exp56
from experiment_055 import infer_30contrast_exact_signed_rank,signed_rank_statistic_30,W_CUTOFF
from experiment_057 import EDGE_ORDER,diagnostic_readout,round_block_randomization,split_contract

SEEDS=range(57000,58000)
AUDIT=set(range(57000,57005))
STRESS={'M1':5751000,'M2':5752000,'M3':5753000,'M4':5754000}
OPERATIVE_SPEC_ISSUE=202
Z=1.6448536269514722

def write_csv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    fields=[]
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
    ma=sum(a)/n;mb=sum(b)/n
    xa=[x-ma for x in a];xb=[x-mb for x in b]
    da=sum(x*x for x in xa);db=sum(x*x for x in xb)
    if da<=0 or db<=0:return None
    return sum(x*y for x,y in zip(xa,xb))/math.sqrt(da*db)

def corr_matrix(vectors,sign=False):
    cols=list(zip(*vectors));out=[]
    for i in range(30):
        row=[]
        ai=[(1.0 if x>0 else -1.0) for x in cols[i]] if sign else [float(x) for x in cols[i]]
        for j in range(30):
            bj=[(1.0 if x>0 else -1.0) for x in cols[j]] if sign else [float(x) for x in cols[j]]
            r=pearson(ai,bj);row.append(0.0 if r is None else r)
        out.append(row)
    return out

def dependence_summary(R):
    within=[];cross=[];paired=[]
    for i in range(30):
        for j in range(i+1,30):
            (within if i//6==j//6 else cross).append(abs(R[i][j]))
    for r in range(5):
        # frozen slot layout: first three forward, next three reverse
        for k in range(3):paired.append(R[r*6+k][r*6+3+k])
    denom=sum(sum(row) for row in R)
    neff=(30.0*30.0/denom) if denom>0 else None
    return {'mean_abs_within_round_offdiag':sum(within)/len(within),'mean_abs_cross_round_offdiag':sum(cross)/len(cross),'mean_forward_reverse_paired_corr':sum(paired)/len(paired),'effective_sign_sample_size':neff}

def diagnostic_row(seed,c):
    stream=exp56.generate_experiment_056_stream(seed,c)
    d=diagnostic_readout(stream)
    _,_,_,_,path,_,_,_=infer_30contrast_exact_signed_rank(stream)
    ref_selected=path[0]['candidate'];ref_wplus=int(path[-1]['wplus'])
    if d['selected']!=ref_selected or int(d['selected_wplus'])!=ref_wplus:
        raise AssertionError(('D1_reference_mismatch',seed,c['label'],d['selected'],ref_selected,d['selected_wplus'],ref_wplus))
    row={'seed':seed,'cell':c['label'],'noise_family':c['noise_family'],'gain':c['gain'],'noise_scale':c['noise_scale'],'selected':d['selected'],'selected_correct':int(d['selected']=='H_ab'),'cyclic_control':d['cyclic_control'],'discovery_margin':d['discovery_margin'],'selected_wplus':d['selected_wplus'],'selected_reference_accept':d['selected_reference_accept'],'cyclic_reference_accept':d['cyclic_reference_accept'],'spec_issue':OPERATIVE_SPEC_ISSUE,'reference_selected_match':1,'reference_wplus_match':1}
    for h in EDGE_ORDER:
        vals=d['edge_vectors'][h];s=d['edge_stats'][h];blk=round_block_randomization(vals)
        row[f'{h}_wplus']=s['wplus'];row[f'{h}_accept']=s['reference_accept'];row[f'{h}_sign_sum']=s['sign_sum'];row[f'{h}_mean']=s['mean'];row[f'{h}_vector']=json.dumps(vals,separators=(',',':'));row[f'{h}_ranks']=json.dumps(s['ranks'],separators=(',',':'));row[f'{h}_block_tail']=blk['tail'];row[f'{h}_block_le_001']=int(blk['block_tail_le_0_01'])
        row[f'discovery_score_{h}']=d['discovery_scores'][h]
    return row

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
        wrong=0
        for seed in range(start,start+1000):
            w,_=signed_rank_statistic_30(_stress_values(kind,seed));wrong+=int(w>=W_CUTOFF)
        out[kind]={'seed_range':[start,start+999],'wrong_n':wrong,'wrong_acceptance':wrong/1000,'wrong_wilson_upper_95':wilson_upper(wrong,1000)}
    return out

def report_from(rows):
    if len(rows)!=len(CELLS)*1000:raise AssertionError(('row_count',len(rows)))
    report={'experiment':57,'operative_spec_issue':OPERATIVE_SPEC_ISSUE,'evaluation_seeds':[57000,57999],'audit_seeds':[57000,57001,57002,57003,57004],'diagnostic_only':True,'w_cutoff_reference_only':W_CUTOFF,'split_contract':split_contract(),'D1_integrity':{'all_reference_selected_match':all(int(r['reference_selected_match']) for r in rows),'all_reference_wplus_match':all(int(r['reference_wplus_match']) for r in rows)},'cells':{},'stress_panel':stress_panel(),'no_tuning':True}
    for c in CELLS:
        q=[r for r in rows if r['cell']==c['label']]
        wrong=[r for r in q if not int(r['selected_correct'])]
        wrongacc=sum(int(r['selected_reference_accept']) for r in wrong)
        cell={'n':len(q),'selected_correct_rate':sum(int(r['selected_correct']) for r in q)/len(q),'selected_wrong_acceptance':wrongacc/len(wrong) if wrong else None,'selected_wrong_wilson_upper_95':wilson_upper(wrongacc,len(wrong)) if wrong else None,'fixed_edges':{},'coupling':{},'slot_sign_means':{},'dependence':{}}
        margins=[float(r['discovery_margin']) for r in q]
        selw=[float(r['selected_wplus']) for r in q]
        selsign=[];selmean=[]
        for r in q:
            h=r['selected'];selsign.append(float(r[f'{h}_sign_sum']));selmean.append(float(r[f'{h}_mean']))
        cell['coupling']['selected']={'margin_vs_wplus':pearson(margins,selw),'margin_vs_sign_sum':pearson(margins,selsign),'margin_vs_mean':pearson(margins,selmean)}
        for h in EDGE_ORDER:
            acc=sum(int(r[f'{h}_accept']) for r in q)
            cell['fixed_edges'][h]={'acceptance':acc/len(q),'wilson_upper_95':wilson_upper(acc,len(q)),'mean_block_tail':sum(float(r[f'{h}_block_tail']) for r in q)/len(q),'fraction_reference_accept_block_le_001':sum(int(r[f'{h}_accept']) and int(r[f'{h}_block_le_001']) for r in q)/max(1,acc)}
            cell['coupling'][h]={'margin_vs_wplus':pearson(margins,[float(r[f'{h}_wplus']) for r in q]),'margin_vs_sign_sum':pearson(margins,[float(r[f'{h}_sign_sum']) for r in q]),'margin_vs_mean':pearson(margins,[float(r[f'{h}_mean']) for r in q])}
            vectors=[json.loads(r[f'{h}_vector']) for r in q];Rs=corr_matrix(vectors,True);Rr=corr_matrix(vectors,False)
            cell['dependence'][h]={'sign_correlation_matrix':Rs,'raw_correlation_matrix':Rr,'sign_summary':dependence_summary(Rs),'raw_summary':dependence_summary(Rr)}
        for stratum,name in ((True,'correct_candidate'),(False,'wrong_candidate')):
            qq=[r for r in q if bool(int(r['selected_correct']))==stratum]
            if not qq:cell['slot_sign_means'][name]=None;continue
            means=[]
            for i in range(30):
                vals=[]
                for r in qq:
                    v=json.loads(r[f"{r['selected']}_vector"])[i];vals.append(1.0 if v>0 else -1.0)
                means.append(sum(vals)/len(vals))
            cell['slot_sign_means'][name]=means
        report['cells'][c['label']]=cell
    return report
