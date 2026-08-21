#!/usr/bin/env python3
import csv,json,math,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_022 import generate_stress_stream
from experiment_031 import CONTEXT_THRESHOLD,context_summary
from run_experiment_021 import calibrations

SEEDS=range(31000,32000);AUDIT=set(range(31000,31005));Z=1.959963984540054

def cell(label,kind,family,magnitude,**kw):return {'label':label,'kind':kind,'family':family,'magnitude':float(magnitude),**kw}
CELLS=(
 cell('healthy','control','healthy',0.0),
 cell('drift_0.50','control','drift',0.50),
 cell('primary_fault_0.50','control','primary_fault',0.50),
 cell('common_mode_0.25','control','common_mode',0.25),
 cell('common_mode_0.50','control','common_mode',0.50),
 cell('common_mode_1.00','control','common_mode',1.00),
 cell('g0.500_n1.00','noise','drift_ab_fault',0.50,gain=0.50,noise_scale=1.00),
)

def inherited_thresholds():
    vals=calibrations();tau,kappa,k3,la,lb,lc,lab,lac,lbc=vals[:9]
    return {'tau':tau,'kappa':kappa,'k3':k3,'la':la,'lb':lb,'lc':lc,'lab':lab,'lac':lac,'lbc':lbc}

def evaluate_seed(seed,c,thr):
    s=generate_stress_stream(seed,c);summ,path=context_summary(s,thr['k3'],thr['la'],thr['lb'],thr['lc'],thr['lab'],thr['lac'],thr['lbc'])
    row={'seed':seed,'label':c['label'],'family':c['family'],'magnitude':c['magnitude'],'kind':c['kind'],**summ}
    if 'gain' in c:row['gain']=c['gain']
    if 'noise_scale' in c:row['noise_scale']=c['noise_scale']
    audit=[]
    if seed in AUDIT:
        for r in path:audit.append({'seed':seed,'label':c['label'],**r})
    return row,audit

def wilson(k,n,z=Z):
    if n<=0:return [None,None]
    p=k/n;den=1+z*z/n;center=(p+z*z/(2*n))/den;rad=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [max(0,center-rad),min(1,center+rad)]
def stats(q):
    n=len(q);calls=sum(int(r['common_mode_context']) for r in q);scores=sorted(float(r['context_score']) for r in q)
    return {'n':n,'mean_context_score':sum(scores)/n,'median_context_score':(scores[n//2-1]+scores[n//2])/2,'call_rate':calls/n,'call_rate_wilson_95':wilson(calls,n),
            'mean_broad_anchor_mismatch_fraction':sum(float(r['broad_anchor_mismatch_fraction']) for r in q)/n,
            'mean_anchor_consensus_fraction':sum(float(r['anchor_consensus_fraction']) for r in q)/n,
            'mean_triad_consistency_fraction':sum(float(r['triad_consistency_fraction']) for r in q)/n}
def report_from(rows,thr):
    by={c['label']:stats([r for r in rows if r['label']==c['label']]) for c in CELLS};H={f'H{i}':True for i in range(1,10)}
    for r in rows:
        if int(r['window_n'])!=20 or not (0<=float(r['context_score'])<=1) or int(r['common_mode_context'])!=int(float(r['context_score'])>=CONTEXT_THRESHOLD):H['H1']=False
    for lab in ('common_mode_0.50','common_mode_1.00'):
        if by[lab]['call_rate']<.90:H['H2']=False
    H['H3']=by['common_mode_0.25']['call_rate']>=.70
    H['H4']=by['g0.500_n1.00']['call_rate']<=.05
    H['H5']=by['drift_0.50']['call_rate']<=.05
    H['H6']=by['healthy']['call_rate']<=.05
    H['H7']=by['primary_fault_0.50']['call_rate']<=.10
    H['H8']=by['common_mode_0.50']['mean_context_score']>=by['g0.500_n1.00']['mean_context_score']+.50
    H['H9']=CONTEXT_THRESHOLD==.50
    return {'evaluation_seeds':[31000,31999],'n_seeds_per_cell':1000,'cell_count':7,'audit_seeds':sorted(AUDIT),'hypotheses':H,'context_threshold':CONTEXT_THRESHOLD,
            'context_statistic':'triad_consistent * 1[m_a+m_b+m_c>=2] * 1[d_ab+d_ac+d_bc==0], averaged over t=401..420','inherited_thresholds':thr,
            'family_labels_evaluator_only':True,'no_fitting':True,'code_commit':os.environ.get('GITHUB_SHA','unknown'),'cells':by}
def write_csv(p,rows):
    p.parent.mkdir(parents=True,exist_ok=True);fields=[]
    for r in rows:
        for k in r:
            if k not in fields:fields.append(k)
    with p.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
