from __future__ import annotations
from random import Random
from statistics import mean, median
from math import sqrt

from adaptive_model_gating import (
    BASELINE_A, EVENT_T, INITIAL_FIT_END, N_STEPS, PERSISTENCE_COUNT,
    ROLLING_WINDOW, empirical_quantile, initial_model, refit, run_strategy_on_stream,
)
from experiment_008 import run_health_persistence_on_stream
from experiment_010 import SIGMA_REF, classify_triad, rolling_pairwise_health, run_triad_persistence_on_stream
from experiment_011 import BETA_ANCHOR, SIGMA_ANCHOR, run_independent_persistence_on_stream
from experiment_013 import health

RHO_SIG = 0.35
DEPENDENCE_CALIBRATION_SEEDS = range(1400, 1600)
FAMILIES = {
    'healthy','drift','common_mode','primary_fault','drift_ab_fault',
    'drift_ab_absent_signature','drift_bc_misleading_signature','drift_all_aux_fault'
}


def generate_experiment_014_stream(seed, family, magnitude, rho_override=None):
    if family not in FAMILIES:
        raise ValueError(family)
    if magnitude < 0:
        raise ValueError('magnitude must be nonnegative')
    rho = (0.0 if family == 'drift_ab_absent_signature' else RHO_SIG) if rho_override is None else float(rho_override)
    rng = Random(seed)
    keys = (
        'x_true','x_primary','x_r1','x_r2','z','z_b','z_c','y','a','physical_epsilon',
        'r1_unit_noise','r2_unit_noise','anchor_unit_noise','anchor_b_unit_noise','anchor_c_unit_noise',
        'dependence_unit_noise','common_unit_noise','primary_unit_noise','ab_fault_unit_noise','bc_fault_unit_noise',
        'true_sigma_x','ref_fault_unit_noise','primary_fault_sigma','ref1_fault_sigma','common_sigma'
    )
    random_keys = (
        'physical_epsilon','r1_unit_noise','r2_unit_noise','anchor_unit_noise','anchor_b_unit_noise',
        'anchor_c_unit_noise','dependence_unit_noise','common_unit_noise','primary_unit_noise',
        'ab_fault_unit_noise','bc_fault_unit_noise'
    )
    s = {k:[0.0]*(N_STEPS+1) for k in keys}; s['a']=[BASELINE_A]*(N_STEPS+1)
    for t in range(1,N_STEPS+1):
        s['x_true'][t] = 0.8*s['x_true'][t-1] + rng.gauss(0,0.5)
        for k in random_keys:
            s[k][t] = rng.gauss(0,0.5) if k == 'physical_epsilon' else rng.gauss(0,1)
        xt=s['x_true'][t]
        s['x_primary'][t]=xt
        s['x_r1'][t]=xt+SIGMA_REF*s['r1_unit_noise'][t]
        s['x_r2'][t]=xt+SIGMA_REF*s['r2_unit_noise'][t]
        shared = rho*s['dependence_unit_noise'][t]
        s['z'][t]=BETA_ANCHOR*xt+SIGMA_ANCHOR*(s['anchor_unit_noise'][t]+shared)
        s['z_b'][t]=BETA_ANCHOR*xt+SIGMA_ANCHOR*(s['anchor_b_unit_noise'][t]+shared)
        s['z_c'][t]=BETA_ANCHOR*xt+SIGMA_ANCHOR*s['anchor_c_unit_noise'][t]
        if t >= EVENT_T:
            if family == 'drift':
                s['a'][t]=BASELINE_A+magnitude
            elif family == 'common_mode':
                q=magnitude*s['common_unit_noise'][t]
                s['x_primary'][t]+=q; s['x_r1'][t]+=q; s['x_r2'][t]+=q
                s['true_sigma_x'][t]=magnitude; s['common_sigma'][t]=magnitude
            elif family == 'primary_fault':
                s['x_primary'][t]+=magnitude*s['primary_unit_noise'][t]
                s['true_sigma_x'][t]=magnitude; s['primary_fault_sigma'][t]=magnitude
            elif family in ('drift_ab_fault','drift_ab_absent_signature'):
                s['a'][t]=BASELINE_A+magnitude
                q=BETA_ANCHOR*magnitude*s['ab_fault_unit_noise'][t]
                s['z'][t]+=q; s['z_b'][t]+=q
            elif family == 'drift_bc_misleading_signature':
                s['a'][t]=BASELINE_A+magnitude
                q=BETA_ANCHOR*magnitude*s['bc_fault_unit_noise'][t]
                s['z_b'][t]+=q; s['z_c'][t]+=q
            elif family == 'drift_all_aux_fault':
                s['a'][t]=BASELINE_A+magnitude
                q=BETA_ANCHOR*magnitude*s['ab_fault_unit_noise'][t]
                s['z'][t]+=q; s['z_b'][t]+=q; s['z_c'][t]+=q
        s['y'][t]=s['a'][t]*xt+s['physical_epsilon'][t]
    s['x_ref']=s['x_r1']; s['reference_unit_noise']=s['r1_unit_noise']; s['rho_sig']=rho
    return s


def _pearson(xs, ys):
    xb=mean(xs); yb=mean(ys)
    dx=[x-xb for x in xs]; dy=[y-yb for y in ys]
    den=sqrt(sum(x*x for x in dx)*sum(y*y for y in dy))
    return 0.0 if den == 0 else sum(x*y for x,y in zip(dx,dy))/den


def preevent_correlations(stream):
    ra=[]; rb=[]; rc=[]
    for t in range(101,301):
        xm=median((stream['x_primary'][t],stream['x_r1'][t],stream['x_r2'][t]))
        ra.append(stream['z'][t]/BETA_ANCHOR-xm)
        rb.append(stream['z_b'][t]/BETA_ANCHOR-xm)
        rc.append(stream['z_c'][t]/BETA_ANCHOR-xm)
    return _pearson(ra,rb),_pearson(ra,rc),_pearson(rb,rc)


def calibrate_lambda_dep():
    vals=[]
    for seed in DEPENDENCE_CALIBRATION_SEEDS:
        c=preevent_correlations(generate_experiment_014_stream(seed,'healthy',0.0,rho_override=0.0))
        vals.extend(abs(x) for x in c)
    return empirical_quantile(vals,0.99)


def infer_groups(stream, lambda_dep):
    corr=preevent_correlations(stream)
    nodes=('a','b','c'); edges=[]
    for pair,val in zip((('a','b'),('a','c'),('b','c')),corr):
        if abs(val) > lambda_dep: edges.append(pair)
    adj={n:set() for n in nodes}
    for u,v in edges: adj[u].add(v); adj[v].add(u)
    groups={}; gid=0
    for n in nodes:
        if n in groups: continue
        gid+=1; stack=[n]
        while stack:
            u=stack.pop()
            if u in groups: continue
            groups[u]=f'G{gid}'; stack.extend(adj[u]-groups.keys())
    return groups,corr


def oracle_groups(family):
    if family == 'drift_bc_misleading_signature': return {'a':'G1','b':'G2','c':'G2'}
    if family == 'drift_all_aux_fault': return {'a':'G1','b':'G1','c':'G1'}
    return {'a':'G1','b':'G1','c':'G2'}


def partition_matches(inferred, target):
    nodes=('a','b','c')
    return int(all((inferred[x]==inferred[y]) == (target[x]==target[y]) for i,x in enumerate(nodes) for y in nodes[i+1:]))


def _annotate(rows,stream,k3,la,lb,lc,lab,lac,lbc,lambda_dep,inferred,corr,gate_groups=None):
    h=health(stream); ph=rolling_pairwise_health(stream); gate_groups=gate_groups or inferred
    target=oracle_groups(rows[0].get('experiment014_family','healthy')) if rows else {'a':'G1','b':'G1','c':'G2'}
    for r in rows:
        t=r['t']; m={x:int(h[x][t] is not None and h[x][t]>l) for x,l in [('a',la),('b',lb),('c',lc)]}
        dis={x:int(h[x][t] is not None and h[x][t]>l) for x,l in [('ab',lab),('ac',lac),('bc',lbc)]}
        consistent=int(all(ph[k][t] is not None and ph[k][t]<=k3 for k in ph))
        raw_cross=int((m['a'] and m['b'] and not dis['ab']) or (m['a'] and m['c'] and not dis['ac']) or (m['b'] and m['c'] and not dis['bc']))
        group_cross=int((gate_groups['a']!=gate_groups['b'] and m['a'] and m['b'] and not dis['ab']) or (gate_groups['a']!=gate_groups['c'] and m['a'] and m['c'] and not dis['ac']) or (gate_groups['b']!=gate_groups['c'] and m['b'] and m['c'] and not dis['bc']))
        active={gate_groups[x] for x in 'abc' if m[x]}
        r.update({'z_c':stream['z_c'][t],'anchor_mismatch':m['a'],'anchor_b_mismatch':m['b'],'anchor_c_mismatch':m['c'],'anchor_ab_disagreement':dis['ab'],'anchor_ac_disagreement':dis['ac'],'anchor_bc_disagreement':dis['bc'],'raw_mismatch_votes':sum(m.values()),'inferred_group_mismatch_votes':len(active),'triad_consistent':consistent,'raw_cross_consistent':raw_cross,'group_cross_consistent':group_cross,'corr_ab':corr[0],'corr_ac':corr[1],'corr_bc':corr[2],'lambda_dep':lambda_dep,'inferred_group_a':inferred['a'],'inferred_group_b':inferred['b'],'inferred_group_c':inferred['c'],'gate_group_a':gate_groups['a'],'gate_group_b':gate_groups['b'],'gate_group_c':gate_groups['c']})
        for key in ('x_true','x_primary','x_r1','x_r2','z','z_b','physical_epsilon','r1_unit_noise','r2_unit_noise','anchor_unit_noise','anchor_b_unit_noise','anchor_c_unit_noise','dependence_unit_noise','common_unit_noise','primary_unit_noise','ab_fault_unit_noise','bc_fault_unit_noise'):
            r.setdefault(key,stream[key][t])
        latent_hat=r['slope_before']*stream['x_true'][t]+r['intercept_before']; r.setdefault('latent_input_sq_error',(stream['y'][t]-latent_hat)**2); r.setdefault('common_mode_suspect',0); r.setdefault('independent_veto',0)
    return rows


def run_group_quorum(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,lambda_dep,stream,family,mode):
    inferred,corr=infer_groups(stream,lambda_dep); groups=oracle_groups(family) if mode=='oracle' else inferred
    xp,ys=stream['x_primary'],stream['y']; model=initial_model(xp,ys); sq=[]; streak=0; rows=[]
    base=run_strategy_on_stream(seed,label,'frozen',tau,xp,ys,stream['a'])
    for r in base: r['experiment014_family']=family
    base=_annotate(base,stream,k3,la,lb,lc,lab,lac,lbc,lambda_dep,inferred,corr,groups); diag={r['t']:r for r in base}; ph=rolling_pairwise_health(stream)
    for t in range(INITIAL_FIT_END+1,N_STEPS+1):
        sb,ib=model.slope,model.intercept; yh=model.predict(xp[t]); err=ys[t]-yh; se=err*err; sq.append(se); rm=mean(sq[-ROLLING_WINDOW:]) if len(sq)>=ROLLING_WINDOW else None; d=diag[t]
        pbad,_,_,_=classify_triad(ph['h_p_r1'][t],ph['h_p_r2'][t],ph['h_r1_r2'][t],k3)
        suspect=int(d['triad_consistent'] and d['group_cross_consistent'] and d['inferred_group_mismatch_votes']>=2)
        if rm is not None: streak=streak+1 if rm>tau else 0
        ready=streak>=PERSISTENCE_COUNT; veto=int(ready and (pbad or suspect)); adapt=int(ready and not veto)
        if ready: streak=0
        if adapt: model=refit(xp,ys,t)
        row=dict(d); row.update({'strategy':'oracle_provenance_quorum' if mode=='oracle' else 'learned_provenance_quorum','y_hat':yh,'error':err,'sq_error':se,'rolling_mse':rm,'adapt':adapt,'slope_before':sb,'intercept_before':ib,'slope_after':model.slope,'intercept_after':model.intercept,'common_mode_suspect':suspect,'independent_veto':veto,'latent_input_sq_error':(ys[t]-(sb*stream['x_true'][t]+ib))**2}); rows.append(row)
    return rows


def run_naive_quorum(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,lambda_dep,stream,family):
    inferred,corr=infer_groups(stream,lambda_dep); xp,ys=stream['x_primary'],stream['y']; model=initial_model(xp,ys); sq=[]; streak=0; rows=[]
    base=run_strategy_on_stream(seed,label,'frozen',tau,xp,ys,stream['a'])
    for r in base:r['experiment014_family']=family
    base=_annotate(base,stream,k3,la,lb,lc,lab,lac,lbc,lambda_dep,inferred,corr,inferred);diag={r['t']:r for r in base};ph=rolling_pairwise_health(stream)
    for t in range(INITIAL_FIT_END+1,N_STEPS+1):
        sb,ib=model.slope,model.intercept;yh=model.predict(xp[t]);err=ys[t]-yh;se=err*err;sq.append(se);rm=mean(sq[-ROLLING_WINDOW:]) if len(sq)>=ROLLING_WINDOW else None;d=diag[t]
        pbad,_,_,_=classify_triad(ph['h_p_r1'][t],ph['h_p_r2'][t],ph['h_r1_r2'][t],k3);suspect=int(d['triad_consistent'] and d['raw_cross_consistent'] and d['raw_mismatch_votes']>=2)
        if rm is not None:streak=streak+1 if rm>tau else 0
        ready=streak>=PERSISTENCE_COUNT;veto=int(ready and (pbad or suspect));adapt=int(ready and not veto)
        if ready:streak=0
        if adapt:model=refit(xp,ys,t)
        row=dict(d);row.update({'strategy':'naive_three_anchor_quorum','y_hat':yh,'error':err,'sq_error':se,'rolling_mse':rm,'adapt':adapt,'slope_before':sb,'intercept_before':ib,'slope_after':model.slope,'intercept_after':model.intercept,'common_mode_suspect':suspect,'independent_veto':veto,'latent_input_sq_error':(ys[t]-(sb*stream['x_true'][t]+ib))**2});rows.append(row)
    return rows


def run_experiment_014_strategy(seed,family,magnitude,strategy,tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambda_dep):
    allowed={'frozen','continuous','threshold','persistence','health_persistence','triad_persistence','independent_persistence','naive_three_anchor_quorum','oracle_provenance_quorum','learned_provenance_quorum'}
    if strategy not in allowed:raise ValueError(strategy)
    stream=generate_experiment_014_stream(seed,family,magnitude);label=f'experiment014_{family}_{magnitude:.2f}';inferred,corr=infer_groups(stream,lambda_dep)
    if strategy=='learned_provenance_quorum':return run_group_quorum(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,lambda_dep,stream,family,'learned')
    if strategy=='oracle_provenance_quorum':return run_group_quorum(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,lambda_dep,stream,family,'oracle')
    if strategy=='naive_three_anchor_quorum':return run_naive_quorum(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,lambda_dep,stream,family)
    if strategy=='independent_persistence':rows=run_independent_persistence_on_stream(seed,label,tau,k3,la,stream)
    elif strategy=='triad_persistence':rows=run_triad_persistence_on_stream(seed,label,tau,k3,stream)
    elif strategy=='health_persistence':rows=run_health_persistence_on_stream(seed,label,tau,kappa,stream)
    else:rows=run_strategy_on_stream(seed,label,strategy,tau,stream['x_primary'],stream['y'],stream['a'])
    for r in rows:r['experiment014_family']=family
    rows=_annotate(rows,stream,k3,la,lb,lc,lab,lac,lbc,lambda_dep,inferred,corr,inferred)
    target=oracle_groups(family); match=partition_matches(inferred,target)
    for r in rows:r['inferred_partition_correct']=match
    return rows
