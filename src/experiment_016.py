from __future__ import annotations
from random import Random
from statistics import mean

from adaptive_model_gating import (
    INITIAL_FIT_END, N_STEPS, PERSISTENCE_COUNT, ROLLING_WINDOW,
    empirical_quantile, initial_model, refit, run_strategy_on_stream,
)
from experiment_008 import run_health_persistence_on_stream
from experiment_010 import classify_triad, rolling_pairwise_health, run_triad_persistence_on_stream
from experiment_011 import run_independent_persistence_on_stream
from experiment_013 import health
from experiment_014 import generate_experiment_014_stream

SIGMA_PROBE = 0.05
ROUND_AMPLITUDES = (0.025, 0.050, 0.100, 0.200)
ROUND_BLOCKS = {
    1: {'a': range(201,206), 'b': range(206,211), 'c': range(211,216)},
    2: {'a': range(216,221), 'b': range(221,226), 'c': range(226,231)},
    3: {'a': range(231,236), 'b': range(236,241), 'c': range(241,246)},
    4: {'a': range(246,251), 'b': range(251,256), 'c': range(256,261)},
}
PROBE_CALIBRATION_SEEDS = range(1800, 2000)
FAMILIES = {
    'healthy','drift','common_mode','primary_fault','drift_ab_fault',
    'drift_ab_gain050','drift_ab_gain025','drift_all_aux_fault'
}


def physical_groups():
    return {'a':'G1','b':'G1','c':'G2'}


def probe_gain_for_family(family):
    if family == 'drift_ab_gain050': return 0.50
    if family == 'drift_ab_gain025': return 0.25
    return 1.00


def generate_experiment_016_stream(seed, family, magnitude, gain_override=None):
    if family not in FAMILIES:
        raise ValueError(family)
    if magnitude < 0:
        raise ValueError('magnitude must be nonnegative')
    base_family = {
        'drift_ab_gain050':'drift_ab_fault',
        'drift_ab_gain025':'drift_ab_fault',
    }.get(family, family)
    s = generate_experiment_014_stream(seed, base_family, magnitude, rho_override=0.0)
    gain = probe_gain_for_family(family) if gain_override is None else float(gain_override)
    rng = Random(seed + 16016000)
    for k in ('probe_noise_a','probe_noise_b','probe_noise_c','probe_obs_a','probe_obs_b','probe_obs_c'):
        s[k] = [0.0] * (N_STEPS + 1)
    for t in range(1, N_STEPS + 1):
        for x in 'abc':
            n = rng.gauss(0,1)
            s[f'probe_noise_{x}'][t] = n
            s[f'probe_obs_{x}'][t] = SIGMA_PROBE*n
    groups = physical_groups()
    for rnd, blocks in ROUND_BLOCKS.items():
        amp = ROUND_AMPLITUDES[rnd-1]
        for target, ts in blocks.items():
            for t in ts:
                for x in 'abc':
                    if groups[x] == groups[target]:
                        s[f'probe_obs_{x}'][t] += gain*amp
    s['probe_gain'] = gain
    return s


def round_response_matrix(stream, rnd):
    if rnd not in ROUND_BLOCKS:
        raise ValueError(rnd)
    baseline = {x:mean(stream[f'probe_obs_{x}'][t] for t in range(181,201)) for x in 'abc'}
    R = {}
    for obs in 'abc':
        for target, ts in ROUND_BLOCKS[rnd].items():
            R[(obs,target)] = mean(stream[f'probe_obs_{obs}'][t] for t in ts)-baseline[obs]
    return R


def calibrate_lambda_probe_rounds():
    vals={r:[] for r in ROUND_BLOCKS}
    for seed in PROBE_CALIBRATION_SEEDS:
        s=generate_experiment_016_stream(seed,'healthy',0.0,gain_override=0.0)
        for rnd in ROUND_BLOCKS:
            R=round_response_matrix(s,rnd)
            vals[rnd].extend(abs(R[(i,j)]) for i in 'abc' for j in 'abc')
    return tuple(empirical_quantile(vals[r],0.99) for r in sorted(vals))


def groups_from_edges(edges):
    nodes=('a','b','c');adj={n:set() for n in nodes}
    for u,v in edges:adj[u].add(v);adj[v].add(u)
    groups={};gid=0
    for n in nodes:
        if n in groups:continue
        gid+=1;stack=[n]
        while stack:
            u=stack.pop()
            if u in groups:continue
            groups[u]=f'G{gid}';stack.extend(adj[u]-groups.keys())
    return groups


def infer_round_groups(stream, thresholds, rnd):
    R=round_response_matrix(stream,rnd); lam=thresholds[rnd-1];edges=[]
    for i,j in (('a','b'),('a','c'),('b','c')):
        if R[(i,j)]>lam and R[(j,i)]>lam:edges.append((i,j))
    groups=groups_from_edges(edges)
    sizes=sorted([sum(1 for x in 'abc' if groups[x]==g) for g in set(groups.values())])
    decisive = int(len(edges)==1 and sizes==[1,2])
    return groups,R,edges,decisive


def infer_sequential_groups(stream, thresholds):
    executed={}
    for rnd in range(1,5):
        groups,R,edges,decisive=infer_round_groups(stream,thresholds,rnd)
        executed[rnd]=(groups,R,edges,decisive)
        if decisive or rnd==4:
            return groups,executed,rnd,decisive
    raise AssertionError('unreachable')


def infer_max_groups(stream, thresholds):
    groups,R,edges,decisive=infer_round_groups(stream,thresholds,4)
    return groups,{4:(groups,R,edges,decisive)},4,decisive


def partition_matches(inferred,target=None):
    target=target or physical_groups();nodes=('a','b','c')
    return int(all((inferred[x]==inferred[y])==(target[x]==target[y]) for i,x in enumerate(nodes) for y in nodes[i+1:]))


def probe_energy(executed_rounds):
    return sum(15*(ROUND_AMPLITUDES[r-1]**2) for r in executed_rounds)


def _diagnostics(stream, thresholds, mode):
    if mode=='sequential':
        groups,executed,stop,decisive=infer_sequential_groups(stream,thresholds)
    elif mode=='max':
        groups,executed,stop,decisive=infer_max_groups(stream,thresholds)
    else:
        groups=physical_groups();executed={};stop=0;decisive=1
    return groups,executed,stop,decisive


def _annotate(rows,stream,k3,la,lb,lc,lab,lac,lbc,thresholds,inferred,executed,stop_round,decisive,gate_groups=None,burden=False):
    h=health(stream);ph=rolling_pairwise_health(stream);gate_groups=gate_groups or inferred
    energy=probe_energy(executed) if burden else 0.0
    block_count=3*len(executed) if burden else 0
    max_amp=ROUND_AMPLITUDES[stop_round-1] if burden and stop_round else 0.0
    for row in rows:
        t=row['t'];m={x:int(h[x][t] is not None and h[x][t]>l) for x,l in [('a',la),('b',lb),('c',lc)]}
        dis={x:int(h[x][t] is not None and h[x][t]>l) for x,l in [('ab',lab),('ac',lac),('bc',lbc)]}
        consistent=int(all(ph[k][t] is not None and ph[k][t]<=k3 for k in ph))
        raw_cross=int((m['a'] and m['b'] and not dis['ab']) or (m['a'] and m['c'] and not dis['ac']) or (m['b'] and m['c'] and not dis['bc']))
        group_cross=int((gate_groups['a']!=gate_groups['b'] and m['a'] and m['b'] and not dis['ab']) or (gate_groups['a']!=gate_groups['c'] and m['a'] and m['c'] and not dis['ac']) or (gate_groups['b']!=gate_groups['c'] and m['b'] and m['c'] and not dis['bc']))
        active={gate_groups[x] for x in 'abc' if m[x]}
        extra={'anchor_mismatch':m['a'],'anchor_b_mismatch':m['b'],'anchor_c_mismatch':m['c'],'anchor_ab_disagreement':dis['ab'],'anchor_ac_disagreement':dis['ac'],'anchor_bc_disagreement':dis['bc'],'raw_mismatch_votes':sum(m.values()),'provenance_mismatch_votes':len(active),'triad_consistent':consistent,'raw_cross_consistent':raw_cross,'group_cross_consistent':group_cross,'inferred_group_a':inferred['a'],'inferred_group_b':inferred['b'],'inferred_group_c':inferred['c'],'gate_group_a':gate_groups['a'],'gate_group_b':gate_groups['b'],'gate_group_c':gate_groups['c'],'inferred_partition_correct':partition_matches(inferred),'probe_gain':stream['probe_gain'],'probe_stop_round':stop_round if burden else 0,'probe_decisive':decisive if burden else 0,'probe_max_amplitude':max_amp,'probe_block_count':block_count,'probe_energy':energy}
        for rnd,lam in enumerate(thresholds,1):extra[f'lambda_probe_{rnd}']=lam
        for rnd in range(1,5):
            data=executed.get(rnd)
            for i in 'abc':
                for j in 'abc':extra[f'probe_r{rnd}_R_{i}{j}']=data[1][(i,j)] if data else ''
        row.update(extra)
        for key in ('x_true','x_primary','x_r1','x_r2','z','z_b','z_c','probe_obs_a','probe_obs_b','probe_obs_c','probe_noise_a','probe_noise_b','probe_noise_c'):
            row.setdefault(key,stream[key][t])
        latent_hat=row['slope_before']*stream['x_true'][t]+row['intercept_before']
        row.setdefault('latent_input_sq_error',(stream['y'][t]-latent_hat)**2);row.setdefault('common_mode_suspect',0);row.setdefault('independent_veto',0)
    return rows


def _run_group_quorum(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,thresholds,stream,mode):
    if mode=='oracle':
        inferred,executed,stop,decisive=physical_groups(),{},0,1;groups=physical_groups();burden=False
    else:
        inferred,executed,stop,decisive=_diagnostics(stream,thresholds,mode);groups=inferred;burden=True
    xp,ys=stream['x_primary'],stream['y'];model=initial_model(xp,ys);sq=[];streak=0;rows=[]
    base=_annotate(run_strategy_on_stream(seed,label,'frozen',tau,xp,ys,stream['a']),stream,k3,la,lb,lc,lab,lac,lbc,thresholds,inferred,executed,stop,decisive,groups,burden);diag={r['t']:r for r in base};ph=rolling_pairwise_health(stream)
    strategy={'oracle':'oracle_provenance_quorum','max':'max_probe_provenance_quorum','sequential':'sequential_provenance_quorum'}[mode]
    for t in range(INITIAL_FIT_END+1,N_STEPS+1):
        sb,ib=model.slope,model.intercept;yh=model.predict(xp[t]);err=ys[t]-yh;se=err*err;sq.append(se);rm=mean(sq[-ROLLING_WINDOW:]) if len(sq)>=ROLLING_WINDOW else None;d=diag[t]
        pbad,_,_,_=classify_triad(ph['h_p_r1'][t],ph['h_p_r2'][t],ph['h_r1_r2'][t],k3)
        suspect=int(d['triad_consistent'] and d['group_cross_consistent'] and d['provenance_mismatch_votes']>=2)
        if rm is not None:streak=streak+1 if rm>tau else 0
        ready=streak>=PERSISTENCE_COUNT;veto=int(ready and (pbad or suspect));adapt=int(ready and not veto)
        if ready:streak=0
        if adapt:model=refit(xp,ys,t)
        row=dict(d);row.update({'strategy':strategy,'y_hat':yh,'error':err,'sq_error':se,'rolling_mse':rm,'adapt':adapt,'slope_before':sb,'intercept_before':ib,'slope_after':model.slope,'intercept_after':model.intercept,'common_mode_suspect':suspect,'independent_veto':veto,'latent_input_sq_error':(ys[t]-(sb*stream['x_true'][t]+ib))**2});rows.append(row)
    return rows


def _run_naive(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,thresholds,stream):
    inferred,executed,stop,decisive=_diagnostics(stream,thresholds,'sequential')
    xp,ys=stream['x_primary'],stream['y'];model=initial_model(xp,ys);sq=[];streak=0;rows=[]
    base=_annotate(run_strategy_on_stream(seed,label,'frozen',tau,xp,ys,stream['a']),stream,k3,la,lb,lc,lab,lac,lbc,thresholds,inferred,executed,stop,decisive,inferred,False);diag={r['t']:r for r in base};ph=rolling_pairwise_health(stream)
    for t in range(INITIAL_FIT_END+1,N_STEPS+1):
        sb,ib=model.slope,model.intercept;yh=model.predict(xp[t]);err=ys[t]-yh;se=err*err;sq.append(se);rm=mean(sq[-ROLLING_WINDOW:]) if len(sq)>=ROLLING_WINDOW else None;d=diag[t]
        pbad,_,_,_=classify_triad(ph['h_p_r1'][t],ph['h_p_r2'][t],ph['h_r1_r2'][t],k3);suspect=int(d['triad_consistent'] and d['raw_cross_consistent'] and d['raw_mismatch_votes']>=2)
        if rm is not None:streak=streak+1 if rm>tau else 0
        ready=streak>=PERSISTENCE_COUNT;veto=int(ready and (pbad or suspect));adapt=int(ready and not veto)
        if ready:streak=0
        if adapt:model=refit(xp,ys,t)
        row=dict(d);row.update({'strategy':'naive_three_anchor_quorum','y_hat':yh,'error':err,'sq_error':se,'rolling_mse':rm,'adapt':adapt,'slope_before':sb,'intercept_before':ib,'slope_after':model.slope,'intercept_after':model.intercept,'common_mode_suspect':suspect,'independent_veto':veto,'latent_input_sq_error':(ys[t]-(sb*stream['x_true'][t]+ib))**2});rows.append(row)
    return rows


def run_experiment_016_strategy(seed,family,magnitude,strategy,tau,kappa,k3,la,lb,lc,lab,lac,lbc,thresholds):
    allowed={'frozen','continuous','threshold','persistence','health_persistence','triad_persistence','independent_persistence','naive_three_anchor_quorum','oracle_provenance_quorum','max_probe_provenance_quorum','sequential_provenance_quorum'}
    if strategy not in allowed:raise ValueError(strategy)
    stream=generate_experiment_016_stream(seed,family,magnitude);label=f'experiment016_{family}_{magnitude:.2f}'
    if strategy=='sequential_provenance_quorum':return _run_group_quorum(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,thresholds,stream,'sequential')
    if strategy=='max_probe_provenance_quorum':return _run_group_quorum(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,thresholds,stream,'max')
    if strategy=='oracle_provenance_quorum':return _run_group_quorum(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,thresholds,stream,'oracle')
    if strategy=='naive_three_anchor_quorum':return _run_naive(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,thresholds,stream)
    inferred,executed,stop,decisive=_diagnostics(stream,thresholds,'sequential')
    if strategy=='independent_persistence':rows=run_independent_persistence_on_stream(seed,label,tau,k3,la,stream)
    elif strategy=='triad_persistence':rows=run_triad_persistence_on_stream(seed,label,tau,k3,stream)
    elif strategy=='health_persistence':rows=run_health_persistence_on_stream(seed,label,tau,kappa,stream)
    else:rows=run_strategy_on_stream(seed,label,strategy,tau,stream['x_primary'],stream['y'],stream['a'])
    return _annotate(rows,stream,k3,la,lb,lc,lab,lac,lbc,thresholds,inferred,executed,stop,decisive,inferred,False)
