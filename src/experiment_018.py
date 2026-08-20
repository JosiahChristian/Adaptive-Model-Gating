from __future__ import annotations
from math import sqrt
from statistics import mean

from adaptive_model_gating import INITIAL_FIT_END,N_STEPS,PERSISTENCE_COUNT,ROLLING_WINDOW,empirical_quantile,initial_model,refit
from experiment_010 import classify_triad,rolling_pairwise_health
from experiment_013 import health
from experiment_016 import groups_from_edges,partition_matches
from experiment_017 import calibrate_cumulative_thresholds,generate_experiment_017_stream,infer_selective_cumulative
from experiment_017_dispatch import run_experiment_017_strategy

ROUND5_AMPLITUDE=0.200
ROUND5_BLOCKS={'a':range(261,266),'b':range(266,271),'c':range(271,276)}
ROUND5_CALIBRATION_SEEDS=range(3000,4000)
ALL_AMPLITUDES=(0.025,0.050,0.100,0.200,0.200)


def generate_experiment_018_stream(seed,family,magnitude,gain_override=None):
    s=generate_experiment_017_stream(seed,family,magnitude,gain_override=gain_override)
    gain=s['probe_gain'];groups={'a':'G1','b':'G1','c':'G2'}
    for target,ts in ROUND5_BLOCKS.items():
        for t in ts:
            for x in 'abc':
                if groups[x]==groups[target]:s[f'probe_obs_{x}'][t]+=gain*ROUND5_AMPLITUDE
    return s


def round5_response_matrix(stream):
    baseline={x:mean(stream[f'probe_obs_{x}'][t] for t in range(181,201)) for x in 'abc'}
    R={}
    for obs in 'abc':
        for target,ts in ROUND5_BLOCKS.items():
            R[(obs,target)]=mean(stream[f'probe_obs_{obs}'][t] for t in ts)-baseline[obs]
    return R


def cumulative5_statistics(stream):
    from experiment_016 import round_response_matrix
    Rs={r:round_response_matrix(stream,r) for r in range(1,5)};Rs[5]=round5_response_matrix(stream)
    denom=sqrt(sum(d*d for d in ALL_AMPLITUDES));C={}
    for i in 'abc':
        for j in 'abc':
            if i!=j:C[(i,j)]=sum(ALL_AMPLITUDES[k-1]*Rs[k][(i,j)] for k in range(1,6))/denom
    return C,Rs


def calibrate_round5_thresholds():
    vals=[]
    for seed in ROUND5_CALIBRATION_SEEDS:
        s=generate_experiment_018_stream(seed,'healthy',0.0,gain_override=0.0);C,_=cumulative5_statistics(s);vals.extend(C.values())
    return empirical_quantile(vals,0.99),empirical_quantile(vals,0.999)


def infer_round5(stream,mu5,nu5):
    C,Rs=cumulative5_statistics(stream);pairs=(('a','b'),('a','c'),('b','c'));Q={(i,j):min(C[(i,j)],C[(j,i)]) for i,j in pairs};edges=[(i,j) for i,j in pairs if Q[(i,j)]>mu5];groups=groups_from_edges(edges)
    sizes=sorted(sum(1 for x in 'abc' if groups[x]==g) for g in set(groups.values()));structural=int(len(edges)==1 and sizes==[1,2]);qualified=int(structural and Q[edges[0]]>nu5)
    return groups,C,Q,edges,structural,qualified,Rs


def infer_replicated_selective(stream,mu,nu,mu5,nu5):
    inferred,executed,stop,accepted,abstain,candidate=infer_selective_cumulative(stream,mu,nu)
    if accepted:return inferred,executed,stop,1,0,candidate,0,None
    r5=infer_round5(stream,mu5,nu5);executed=dict(executed);executed[5]=r5;candidate=r5[0]
    if r5[5]:return r5[0],executed,5,1,0,candidate,1,r5
    return None,executed,0,0,1,candidate,0,r5


def _annotation(stream,mu,nu,mu5,nu5,executed,accepted,stop,abstain,candidate,gate_groups,rescued):
    energy=sum(15*(ALL_AMPLITUDES[r-1]**2) for r in executed)
    out={'probe_gain':stream['probe_gain'],'probe_stop_round':stop,'probe_energy':energy,'probe_block_count':3*len(executed),'probe_max_amplitude':ALL_AMPLITUDES[(stop or max(executed))-1] if executed else 0.0,'provenance_accepted':accepted,'provenance_abstain':abstain,'accepted_partition_correct':partition_matches(gate_groups) if accepted else '','candidate_partition_correct':partition_matches(candidate) if candidate else '','round5_executed':int(5 in executed),'round5_rescued_acceptance':rescued,'round5_rescued_correct':partition_matches(gate_groups) if rescued else ''}
    for r in range(1,5):out[f'mu_probe_{r}']=mu[r-1];out[f'nu_probe_{r}']=nu[r-1]
    out['mu_probe_5']=mu5;out['nu_probe_5']=nu5
    if 5 in executed:
        groups,C,Q,edges,structural,qualified,Rs=executed[5];out['cumulative_r5_structural']=structural;out['cumulative_r5_qualified']=qualified;out['cumulative_r5_edges']=';'.join(''.join(x) for x in edges)
        for i,j in (('a','b'),('a','c'),('b','c')):out[f'cumulative_r5_Q_{i}{j}']=Q[(i,j)]
        for i in 'abc':
            for j in 'abc':
                if i!=j:out[f'cumulative_r5_C_{i}{j}']=C[(i,j)]
                out[f'probe_r5_R_{i}{j}']=Rs[5][(i,j)]
    for x in 'abc':out[f'gate_group_{x}']=gate_groups[x] if gate_groups else '';out[f'candidate_group_{x}']=candidate[x] if candidate else ''
    return out


def _run_group_gate(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,stream,ann,gate_groups):
    xp,ys=stream['x_primary'],stream['y'];model=initial_model(xp,ys);sq=[];streak=0;rows=[];h=health(stream);ph=rolling_pairwise_health(stream)
    for t in range(INITIAL_FIT_END+1,N_STEPS+1):
        sb,ib=model.slope,model.intercept;yh=model.predict(xp[t]);err=ys[t]-yh;se=err*err;sq.append(se);rm=mean(sq[-ROLLING_WINDOW:]) if len(sq)>=ROLLING_WINDOW else None
        m={x:int(h[x][t] is not None and h[x][t]>l) for x,l in [('a',la),('b',lb),('c',lc)]};dis={x:int(h[x][t] is not None and h[x][t]>l) for x,l in [('ab',lab),('ac',lac),('bc',lbc)]};consistent=int(all(ph[k][t] is not None and ph[k][t]<=k3 for k in ph));active={gate_groups[x] for x in 'abc' if m[x]};cross=int(any(gate_groups[i]!=gate_groups[j] and m[i] and m[j] and not dis[i+j] for i,j in (('a','b'),('a','c'),('b','c'))));pbad,_,_,_=classify_triad(ph['h_p_r1'][t],ph['h_p_r2'][t],ph['h_r1_r2'][t],k3);suspect=int(consistent and cross and len(active)>=2)
        if rm is not None:streak=streak+1 if rm>tau else 0
        ready=streak>=PERSISTENCE_COUNT;veto=int(ready and (pbad or suspect));adapt=int(ready and not veto)
        if ready:streak=0
        if adapt:model=refit(xp,ys,t)
        row={'seed':seed,'label':label,'t':t,'strategy':'replicated_selective_cumulative_provenance_quorum','y_hat':yh,'error':err,'sq_error':se,'rolling_mse':rm,'adapt':adapt,'slope_before':sb,'intercept_before':ib,'slope_after':model.slope,'intercept_after':model.intercept,'common_mode_suspect':suspect,'independent_veto':veto,'latent_input_sq_error':(ys[t]-(sb*stream['x_true'][t]+ib))**2,'raw_mismatch_votes':sum(m.values()),'provenance_mismatch_votes':len(active)}
        for key in ('x_true','x_primary','x_r1','x_r2','z','z_b','z_c','probe_obs_a','probe_obs_b','probe_obs_c','probe_noise_a','probe_noise_b','probe_noise_c'):row[key]=stream[key][t]
        row.update(ann);rows.append(row)
    return rows


def _fallback(seed,family,magnitude,tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5,stream,executed,candidate):
    rows=run_experiment_017_strategy(seed,family,magnitude,'triad_persistence',tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu);ann=_annotation(stream,mu,nu,mu5,nu5,executed,0,0,1,candidate,None,0)
    for row in rows:
        row['strategy']='replicated_selective_cumulative_provenance_quorum'
        t=row['t']
        for key in ('x_true','x_primary','x_r1','x_r2','z','z_b','z_c','probe_obs_a','probe_obs_b','probe_obs_c','probe_noise_a','probe_noise_b','probe_noise_c'):row[key]=stream[key][t]
        row.update(ann)
    return rows


def run_experiment_018_strategy(seed,family,magnitude,strategy,tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5):
    if strategy!='replicated_selective_cumulative_provenance_quorum':return run_experiment_017_strategy(seed,family,magnitude,strategy,tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu)
    stream=generate_experiment_018_stream(seed,family,magnitude);label=f'experiment018_{family}_{magnitude:.3f}';inferred,executed,stop,accepted,abstain,candidate,rescued,r5=infer_replicated_selective(stream,mu,nu,mu5,nu5)
    if abstain:return _fallback(seed,family,magnitude,tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5,stream,executed,candidate)
    ann=_annotation(stream,mu,nu,mu5,nu5,executed,accepted,stop,abstain,candidate,inferred,rescued);return _run_group_gate(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,stream,ann,inferred)
