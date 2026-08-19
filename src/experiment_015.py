from __future__ import annotations
from random import Random
from statistics import mean

from adaptive_model_gating import (
    EVENT_T, INITIAL_FIT_END, N_STEPS, PERSISTENCE_COUNT, ROLLING_WINDOW,
    empirical_quantile, initial_model, refit, run_strategy_on_stream,
)
from experiment_008 import run_health_persistence_on_stream
from experiment_010 import classify_triad, rolling_pairwise_health, run_triad_persistence_on_stream
from experiment_011 import run_independent_persistence_on_stream
from experiment_013 import health
from experiment_014 import generate_experiment_014_stream

DELTA_PROBE = 0.20
SIGMA_PROBE = 0.05
GAMMA_PROBE = 0.80
PROBE_CALIBRATION_SEEDS = range(1600, 1800)
FAMILIES = {
    'healthy','drift','common_mode','primary_fault','drift_ab_fault',
    'drift_ab_weak_probe','drift_ab_cross_coupled_probe','drift_all_aux_fault'
}


def _physical_groups():
    return {'a':'G1','b':'G1','c':'G2'}


def generate_experiment_015_stream(seed, family, magnitude, probe_amp_override=None):
    if family not in FAMILIES:
        raise ValueError(family)
    if magnitude < 0:
        raise ValueError('magnitude must be nonnegative')
    base_family = {
        'drift_ab_fault':'drift_ab_fault',
        'drift_ab_weak_probe':'drift_ab_fault',
        'drift_ab_cross_coupled_probe':'drift_ab_fault',
    }.get(family, family)
    s = generate_experiment_014_stream(seed, base_family, magnitude, rho_override=0.0)
    amp = DELTA_PROBE if probe_amp_override is None else float(probe_amp_override)
    if family == 'drift_ab_weak_probe' and probe_amp_override is None:
        amp = 0.025
    rng = Random(seed + 15015000)
    for k in ('probe_noise_a','probe_noise_b','probe_noise_c','probe_obs_a','probe_obs_b','probe_obs_c'):
        s[k] = [0.0] * (N_STEPS + 1)
    groups = _physical_groups()
    blocks = {'a':range(201,221),'b':range(221,241),'c':range(241,261)}
    for t in range(1, N_STEPS + 1):
        for x in 'abc':
            n = rng.gauss(0,1)
            s[f'probe_noise_{x}'][t] = n
            s[f'probe_obs_{x}'][t] = SIGMA_PROBE * n
    for target, ts in blocks.items():
        for t in ts:
            for x in 'abc':
                response = amp if groups[x] == groups[target] else 0.0
                if family == 'drift_ab_cross_coupled_probe' and target in ('a','b') and x == 'c':
                    response += GAMMA_PROBE * amp
                s[f'probe_obs_{x}'][t] += response
    s['probe_amplitude'] = amp
    s['probe_cross_coupled'] = int(family == 'drift_ab_cross_coupled_probe')
    return s


def probe_response_matrix(stream):
    baseline = {x:mean(stream[f'probe_obs_{x}'][t] for t in range(181,201)) for x in 'abc'}
    blocks = {'a':range(201,221),'b':range(221,241),'c':range(241,261)}
    R = {}
    for obs in 'abc':
        for target, ts in blocks.items():
            R[(obs,target)] = mean(stream[f'probe_obs_{obs}'][t] for t in ts) - baseline[obs]
    return R


def calibrate_lambda_probe():
    vals=[]
    for seed in PROBE_CALIBRATION_SEEDS:
        s=generate_experiment_015_stream(seed,'healthy',0.0,probe_amp_override=0.0)
        R=probe_response_matrix(s)
        vals.extend(abs(R[(i,j)]) for i in 'abc' for j in 'abc')
    return empirical_quantile(vals,0.99)


def infer_probe_groups(stream, lambda_probe):
    R=probe_response_matrix(stream); nodes=('a','b','c'); edges=[]
    for i,j in (('a','b'),('a','c'),('b','c')):
        if R[(i,j)] > lambda_probe and R[(j,i)] > lambda_probe:
            edges.append((i,j))
    adj={n:set() for n in nodes}
    for u,v in edges: adj[u].add(v); adj[v].add(u)
    groups={}; gid=0
    for n in nodes:
        if n in groups: continue
        gid += 1; stack=[n]
        while stack:
            u=stack.pop()
            if u in groups: continue
            groups[u]=f'G{gid}'; stack.extend(adj[u]-groups.keys())
    return groups,R


def partition_matches(inferred, target=None):
    target=target or _physical_groups(); nodes=('a','b','c')
    return int(all((inferred[x]==inferred[y]) == (target[x]==target[y]) for i,x in enumerate(nodes) for y in nodes[i+1:]))


def _annotate(rows,stream,k3,la,lb,lc,lab,lac,lbc,lambda_probe,inferred,R,gate_groups=None):
    h=health(stream); ph=rolling_pairwise_health(stream); gate_groups=gate_groups or inferred
    for r in rows:
        t=r['t']; m={x:int(h[x][t] is not None and h[x][t]>l) for x,l in [('a',la),('b',lb),('c',lc)]}
        dis={x:int(h[x][t] is not None and h[x][t]>l) for x,l in [('ab',lab),('ac',lac),('bc',lbc)]}
        consistent=int(all(ph[k][t] is not None and ph[k][t]<=k3 for k in ph))
        raw_cross=int((m['a'] and m['b'] and not dis['ab']) or (m['a'] and m['c'] and not dis['ac']) or (m['b'] and m['c'] and not dis['bc']))
        group_cross=int((gate_groups['a']!=gate_groups['b'] and m['a'] and m['b'] and not dis['ab']) or (gate_groups['a']!=gate_groups['c'] and m['a'] and m['c'] and not dis['ac']) or (gate_groups['b']!=gate_groups['c'] and m['b'] and m['c'] and not dis['bc']))
        active={gate_groups[x] for x in 'abc' if m[x]}
        extra={'anchor_mismatch':m['a'],'anchor_b_mismatch':m['b'],'anchor_c_mismatch':m['c'],'anchor_ab_disagreement':dis['ab'],'anchor_ac_disagreement':dis['ac'],'anchor_bc_disagreement':dis['bc'],'raw_mismatch_votes':sum(m.values()),'provenance_mismatch_votes':len(active),'triad_consistent':consistent,'raw_cross_consistent':raw_cross,'group_cross_consistent':group_cross,'lambda_probe':lambda_probe,'inferred_group_a':inferred['a'],'inferred_group_b':inferred['b'],'inferred_group_c':inferred['c'],'gate_group_a':gate_groups['a'],'gate_group_b':gate_groups['b'],'gate_group_c':gate_groups['c'],'probe_amplitude':stream['probe_amplitude'],'probe_cross_coupled':stream['probe_cross_coupled'],'inferred_partition_correct':partition_matches(inferred)}
        for i in 'abc':
            for j in 'abc': extra[f'probe_R_{i}{j}']=R[(i,j)]
        r.update(extra)
        for key in ('x_true','x_primary','x_r1','x_r2','z','z_b','z_c','probe_obs_a','probe_obs_b','probe_obs_c','probe_noise_a','probe_noise_b','probe_noise_c'):
            r.setdefault(key,stream[key][t])
        latent_hat=r['slope_before']*stream['x_true'][t]+r['intercept_before']
        r.setdefault('latent_input_sq_error',(stream['y'][t]-latent_hat)**2);r.setdefault('common_mode_suspect',0);r.setdefault('independent_veto',0)
    return rows


def _run_quorum(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,lambda_probe,stream,mode):
    inferred,R=infer_probe_groups(stream,lambda_probe); groups=_physical_groups() if mode=='oracle' else inferred
    xp,ys=stream['x_primary'],stream['y'];model=initial_model(xp,ys);sq=[];streak=0;rows=[]
    base=_annotate(run_strategy_on_stream(seed,label,'frozen',tau,xp,ys,stream['a']),stream,k3,la,lb,lc,lab,lac,lbc,lambda_probe,inferred,R,groups);diag={r['t']:r for r in base};ph=rolling_pairwise_health(stream)
    for t in range(INITIAL_FIT_END+1,N_STEPS+1):
        sb,ib=model.slope,model.intercept;yh=model.predict(xp[t]);err=ys[t]-yh;se=err*err;sq.append(se);rm=mean(sq[-ROLLING_WINDOW:]) if len(sq)>=ROLLING_WINDOW else None;d=diag[t]
        pbad,_,_,_=classify_triad(ph['h_p_r1'][t],ph['h_p_r2'][t],ph['h_r1_r2'][t],k3)
        suspect=int(d['triad_consistent'] and d['group_cross_consistent'] and d['provenance_mismatch_votes']>=2)
        if rm is not None: streak=streak+1 if rm>tau else 0
        ready=streak>=PERSISTENCE_COUNT;veto=int(ready and (pbad or suspect));adapt=int(ready and not veto)
        if ready: streak=0
        if adapt:model=refit(xp,ys,t)
        row=dict(d);row.update({'strategy':'oracle_provenance_quorum' if mode=='oracle' else 'interventional_provenance_quorum','y_hat':yh,'error':err,'sq_error':se,'rolling_mse':rm,'adapt':adapt,'slope_before':sb,'intercept_before':ib,'slope_after':model.slope,'intercept_after':model.intercept,'common_mode_suspect':suspect,'independent_veto':veto,'latent_input_sq_error':(ys[t]-(sb*stream['x_true'][t]+ib))**2});rows.append(row)
    return rows


def _run_naive(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,lambda_probe,stream):
    inferred,R=infer_probe_groups(stream,lambda_probe);xp,ys=stream['x_primary'],stream['y'];model=initial_model(xp,ys);sq=[];streak=0;rows=[]
    base=_annotate(run_strategy_on_stream(seed,label,'frozen',tau,xp,ys,stream['a']),stream,k3,la,lb,lc,lab,lac,lbc,lambda_probe,inferred,R,inferred);diag={r['t']:r for r in base};ph=rolling_pairwise_health(stream)
    for t in range(INITIAL_FIT_END+1,N_STEPS+1):
        sb,ib=model.slope,model.intercept;yh=model.predict(xp[t]);err=ys[t]-yh;se=err*err;sq.append(se);rm=mean(sq[-ROLLING_WINDOW:]) if len(sq)>=ROLLING_WINDOW else None;d=diag[t]
        pbad,_,_,_=classify_triad(ph['h_p_r1'][t],ph['h_p_r2'][t],ph['h_r1_r2'][t],k3);suspect=int(d['triad_consistent'] and d['raw_cross_consistent'] and d['raw_mismatch_votes']>=2)
        if rm is not None:streak=streak+1 if rm>tau else 0
        ready=streak>=PERSISTENCE_COUNT;veto=int(ready and (pbad or suspect));adapt=int(ready and not veto)
        if ready:streak=0
        if adapt:model=refit(xp,ys,t)
        row=dict(d);row.update({'strategy':'naive_three_anchor_quorum','y_hat':yh,'error':err,'sq_error':se,'rolling_mse':rm,'adapt':adapt,'slope_before':sb,'intercept_before':ib,'slope_after':model.slope,'intercept_after':model.intercept,'common_mode_suspect':suspect,'independent_veto':veto,'latent_input_sq_error':(ys[t]-(sb*stream['x_true'][t]+ib))**2});rows.append(row)
    return rows


def run_experiment_015_strategy(seed,family,magnitude,strategy,tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambda_probe):
    allowed={'frozen','continuous','threshold','persistence','health_persistence','triad_persistence','independent_persistence','naive_three_anchor_quorum','oracle_provenance_quorum','interventional_provenance_quorum'}
    if strategy not in allowed: raise ValueError(strategy)
    stream=generate_experiment_015_stream(seed,family,magnitude);label=f'experiment015_{family}_{magnitude:.2f}';inferred,R=infer_probe_groups(stream,lambda_probe)
    if strategy=='interventional_provenance_quorum':return _run_quorum(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,lambda_probe,stream,'interventional')
    if strategy=='oracle_provenance_quorum':return _run_quorum(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,lambda_probe,stream,'oracle')
    if strategy=='naive_three_anchor_quorum':return _run_naive(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,lambda_probe,stream)
    if strategy=='independent_persistence':rows=run_independent_persistence_on_stream(seed,label,tau,k3,la,stream)
    elif strategy=='triad_persistence':rows=run_triad_persistence_on_stream(seed,label,tau,k3,stream)
    elif strategy=='health_persistence':rows=run_health_persistence_on_stream(seed,label,tau,kappa,stream)
    else:rows=run_strategy_on_stream(seed,label,strategy,tau,stream['x_primary'],stream['y'],stream['a'])
    return _annotate(rows,stream,k3,la,lb,lc,lab,lac,lbc,lambda_probe,inferred,R,inferred)
