from __future__ import annotations
from math import sqrt
from statistics import mean

from adaptive_model_gating import INITIAL_FIT_END,N_STEPS,PERSISTENCE_COUNT,ROLLING_WINDOW,empirical_quantile,initial_model,refit
from experiment_010 import classify_triad,rolling_pairwise_health
from experiment_013 import health
from experiment_016 import (
    ROUND_AMPLITUDES,ROUND_BLOCKS,calibrate_lambda_probe_rounds,generate_experiment_016_stream,
    groups_from_edges,partition_matches,physical_groups,probe_energy,round_response_matrix,
    run_experiment_016_strategy,
)

CUMULATIVE_CALIBRATION_SEEDS=range(2000,3000)
GAIN_BY_FAMILY={
 'drift_ab_fault':1.0,'drift_ab_gain050':0.50,'drift_ab_gain0375':0.375,
 'drift_ab_gain025':0.25,'drift_ab_gain0125':0.125,
}
FAMILIES={'healthy','drift','common_mode','primary_fault','drift_ab_fault','drift_ab_gain050','drift_ab_gain0375','drift_ab_gain025','drift_ab_gain0125','drift_all_aux_fault'}
NEW_STRATEGIES={'cumulative_provenance_quorum','selective_cumulative_provenance_quorum'}


def generate_experiment_017_stream(seed,family,magnitude,gain_override=None):
    if family not in FAMILIES: raise ValueError(family)
    base={'drift_ab_gain0375':'drift_ab_fault','drift_ab_gain0125':'drift_ab_fault'}.get(family,family)
    gain=GAIN_BY_FAMILY.get(family,1.0) if gain_override is None else float(gain_override)
    return generate_experiment_016_stream(seed,base,magnitude,gain_override=gain)


def cumulative_statistics(stream,rnd):
    if rnd not in ROUND_BLOCKS: raise ValueError(rnd)
    denom=sqrt(sum(d*d for d in ROUND_AMPLITUDES[:rnd]))
    Rs={k:round_response_matrix(stream,k) for k in range(1,rnd+1)}
    C={}
    for i in 'abc':
        for j in 'abc':
            if i!=j:C[(i,j)]=sum(ROUND_AMPLITUDES[k-1]*Rs[k][(i,j)] for k in range(1,rnd+1))/denom
    return C,Rs


def calibrate_cumulative_thresholds():
    vals={r:[] for r in ROUND_BLOCKS}
    for seed in CUMULATIVE_CALIBRATION_SEEDS:
        s=generate_experiment_017_stream(seed,'healthy',0.0,gain_override=0.0)
        for r in ROUND_BLOCKS:
            C,_=cumulative_statistics(s,r);vals[r].extend(C.values())
    mu=tuple(empirical_quantile(vals[r],0.99) for r in sorted(vals))
    nu=tuple(empirical_quantile(vals[r],0.999) for r in sorted(vals))
    return mu,nu


def infer_cumulative_round(stream,mu,nu,rnd):
    C,Rs=cumulative_statistics(stream,rnd);pairs=(('a','b'),('a','c'),('b','c'))
    Q={(i,j):min(C[(i,j)],C[(j,i)]) for i,j in pairs}
    edges=[(i,j) for i,j in pairs if Q[(i,j)]>mu[rnd-1]]
    groups=groups_from_edges(edges)
    sizes=sorted(sum(1 for x in 'abc' if groups[x]==g) for g in set(groups.values()))
    structural=int(len(edges)==1 and sizes==[1,2])
    qualified=int(structural and Q[edges[0]]>nu[rnd-1])
    return groups,C,Q,edges,structural,qualified,Rs


def infer_selective_cumulative(stream,mu,nu):
    executed={};candidate=None
    for r in range(1,5):
        data=infer_cumulative_round(stream,mu,nu,r);executed[r]=data;candidate=data[0]
        if data[5]:return data[0],executed,r,1,0,candidate
    return None,executed,0,0,1,candidate


def infer_forced_cumulative(stream,mu,nu):
    executed={r:infer_cumulative_round(stream,mu,nu,r) for r in range(1,5)}
    g=executed[4][0]
    return g,executed,4,int(executed[4][4]),0,g


def _diagnostic_annotation(stream,mu,nu,executed,accepted,stop,abstain,candidate,gate_groups):
    energy=probe_energy(executed);out={
      'probe_gain':stream['probe_gain'],'probe_stop_round':stop,'probe_max_amplitude':ROUND_AMPLITUDES[(stop or 4)-1],
      'probe_block_count':3*len(executed),'probe_energy':energy,'provenance_accepted':accepted,'provenance_abstain':abstain,
      'accepted_partition_correct':partition_matches(gate_groups) if accepted else '',
      'candidate_partition_correct':partition_matches(candidate) if candidate else '',
    }
    for r in range(1,5):
        out[f'mu_probe_{r}']=mu[r-1];out[f'nu_probe_{r}']=nu[r-1]
        d=executed.get(r)
        if not d:continue
        groups,C,Q,edges,structural,qualified,Rs=d
        out[f'cumulative_r{r}_structural']=structural;out[f'cumulative_r{r}_qualified']=qualified
        out[f'cumulative_r{r}_edges']=';'.join(''.join(x) for x in edges)
        for i,j in (('a','b'),('a','c'),('b','c')):out[f'cumulative_r{r}_Q_{i}{j}']=Q[(i,j)]
        for i in 'abc':
            for j in 'abc':
                if i!=j:out[f'cumulative_r{r}_C_{i}{j}']=C[(i,j)]
                out[f'probe_r{r}_R_{i}{j}']=Rs[r][(i,j)]
    for x in 'abc':
        out[f'gate_group_{x}']=gate_groups[x] if gate_groups else ''
        out[f'candidate_group_{x}']=candidate[x] if candidate else ''
    return out


def _run_cumulative_gate(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,stream,mu,nu,selective):
    if selective:
        inferred,executed,stop,accepted,abstain,candidate=infer_selective_cumulative(stream,mu,nu)
        if abstain:
            rows=run_experiment_016_strategy(seed,label.split('_',1)[1].rsplit('_',1)[0] if False else 'healthy',0,'triad_persistence',tau,0,k3,la,lb,lc,lab,lac,lbc,calibrate_lambda_probe_rounds())
            # The caller replaces this fallback path below; retained only as an unreachable guard.
            raise AssertionError('selective fallback must be supplied by caller')
        gate_groups=inferred
    else:
        inferred,executed,stop,accepted,abstain,candidate=infer_forced_cumulative(stream,mu,nu);gate_groups=inferred
    xp,ys=stream['x_primary'],stream['y'];model=initial_model(xp,ys);sq=[];streak=0;rows=[];h=health(stream);ph=rolling_pairwise_health(stream)
    ann=_diagnostic_annotation(stream,mu,nu,executed,accepted,stop,abstain,candidate,gate_groups)
    for t in range(INITIAL_FIT_END+1,N_STEPS+1):
        sb,ib=model.slope,model.intercept;yh=model.predict(xp[t]);err=ys[t]-yh;se=err*err;sq.append(se);rm=mean(sq[-ROLLING_WINDOW:]) if len(sq)>=ROLLING_WINDOW else None
        m={x:int(h[x][t] is not None and h[x][t]>l) for x,l in [('a',la),('b',lb),('c',lc)]}
        dis={x:int(h[x][t] is not None and h[x][t]>l) for x,l in [('ab',lab),('ac',lac),('bc',lbc)]}
        consistent=int(all(ph[k][t] is not None and ph[k][t]<=k3 for k in ph));active={gate_groups[x] for x in 'abc' if m[x]}
        cross=int(any(gate_groups[i]!=gate_groups[j] and m[i] and m[j] and not dis[i+j] for i,j in (('a','b'),('a','c'),('b','c'))))
        pbad,_,_,_=classify_triad(ph['h_p_r1'][t],ph['h_p_r2'][t],ph['h_r1_r2'][t],k3);suspect=int(consistent and cross and len(active)>=2)
        if rm is not None:streak=streak+1 if rm>tau else 0
        ready=streak>=PERSISTENCE_COUNT;veto=int(ready and (pbad or suspect));adapt=int(ready and not veto)
        if ready:streak=0
        if adapt:model=refit(xp,ys,t)
        row={'seed':seed,'label':label,'t':t,'strategy':'selective_cumulative_provenance_quorum' if selective else 'cumulative_provenance_quorum','y_hat':yh,'error':err,'sq_error':se,'rolling_mse':rm,'adapt':adapt,'slope_before':sb,'intercept_before':ib,'slope_after':model.slope,'intercept_after':model.intercept,'common_mode_suspect':suspect,'independent_veto':veto,'latent_input_sq_error':(ys[t]-(sb*stream['x_true'][t]+ib))**2,'raw_mismatch_votes':sum(m.values()),'provenance_mismatch_votes':len(active)}
        row.update(ann);rows.append(row)
    return rows


def _fallback_rows(seed,family,magnitude,tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,stream,mu,nu,executed,candidate):
    rows=run_experiment_016_strategy(seed,{'drift_ab_gain0375':'drift_ab_fault','drift_ab_gain0125':'drift_ab_fault'}.get(family,family),magnitude,'triad_persistence',tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas)
    ann=_diagnostic_annotation(stream,mu,nu,executed,0,0,1,candidate,None)
    for row in rows:
        row['strategy']='selective_cumulative_provenance_quorum';row.update(ann)
    return rows


def run_experiment_017_strategy(seed,family,magnitude,strategy,tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu):
    stream=generate_experiment_017_stream(seed,family,magnitude);label=f'experiment017_{family}_{magnitude:.3f}'
    if strategy not in NEW_STRATEGIES:
        base_family={'drift_ab_gain0375':'drift_ab_fault','drift_ab_gain0125':'drift_ab_fault'}.get(family,family)
        return run_experiment_016_strategy(seed,base_family,magnitude,strategy,tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas)
    if strategy=='cumulative_provenance_quorum':return _run_cumulative_gate(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,stream,mu,nu,False)
    inferred,executed,stop,accepted,abstain,candidate=infer_selective_cumulative(stream,mu,nu)
    if abstain:return _fallback_rows(seed,family,magnitude,tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,stream,mu,nu,executed,candidate)
    return _run_cumulative_gate(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,stream,mu,nu,True)
