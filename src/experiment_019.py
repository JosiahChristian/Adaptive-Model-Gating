from __future__ import annotations
from copy import deepcopy
from math import sqrt
from statistics import mean

from adaptive_model_gating import empirical_quantile
from experiment_016 import groups_from_edges,partition_matches
from experiment_017 import generate_experiment_017_stream,infer_selective_cumulative
from experiment_018 import ALL_AMPLITUDES,_annotation as annotation018,_fallback as fallback018,_run_group_gate as run_group_gate018,calibrate_round5_thresholds,run_experiment_018_strategy

TARGETED_CALIBRATION_SEEDS=range(4000,5000)
TARGETED_AMPLITUDE=0.200
TARGETED_BLOCKS=(range(261,266),range(266,271))
PAIRS=(('a','b'),('a','c'),('b','c'))


def leading_edge(q):
    vals=[(float(q[p]),p) for p in PAIRS]
    m=max(v for v,_ in vals);w=[p for v,p in vals if v==m]
    return w[0] if len(w)==1 else None


def inject_targeted_round5(stream,pair):
    s=deepcopy(stream)
    if pair is None:return s
    groups={'a':'G1','b':'G1','c':'G2'};gain=s['probe_gain']
    for target,ts in zip(pair,TARGETED_BLOCKS):
        for t in ts:
            for x in 'abc':
                if groups[x]==groups[target]:s[f'probe_obs_{x}'][t]+=gain*TARGETED_AMPLITUDE
    return s


def targeted_selected_score(stream,pair):
    if pair is None:raise ValueError('pair required')
    from experiment_016 import round_response_matrix
    baseline={x:mean(stream[f'probe_obs_{x}'][t] for t in range(181,201)) for x in 'abc'}
    R5={}
    for obs in 'abc':
        for target,ts in zip(pair,TARGETED_BLOCKS):R5[(obs,target)]=mean(stream[f'probe_obs_{obs}'][t] for t in ts)-baseline[obs]
    Rs={r:round_response_matrix(stream,r) for r in range(1,5)}
    denom=sqrt(sum(d*d for d in ALL_AMPLITUDES));i,j=pair
    def c(obs,target):return (sum(ALL_AMPLITUDES[k-1]*Rs[k][(obs,target)] for k in range(1,5))+TARGETED_AMPLITUDE*R5[(obs,target)])/denom
    cij,cji=c(i,j),c(j,i)
    return min(cij,cji),cij,cji,R5


def calibrate_targeted_thresholds(mu,nu):
    vals=[]
    for seed in TARGETED_CALIBRATION_SEEDS:
        base=generate_experiment_017_stream(seed,'healthy',0.0,gain_override=0.0)
        _,executed,_,accepted,_,_=infer_selective_cumulative(base,mu,nu)
        if accepted:continue
        pair=leading_edge(executed[4][2])
        if pair is None:continue
        s=inject_targeted_round5(base,pair);vals.append(targeted_selected_score(s,pair)[0])
    if not vals:raise RuntimeError('no targeted null calibration values')
    return empirical_quantile(vals,0.99),empirical_quantile(vals,0.999)


def infer_targeted(stream,mu,nu,mu5t,nu5t):
    inferred,executed,stop,accepted,abstain,candidate=infer_selective_cumulative(stream,mu,nu)
    if accepted:return inferred,executed,stop,1,0,candidate,None,0,None,stream
    q4=executed[4][2];pair=leading_edge(q4)
    if pair is None:return None,executed,0,0,1,candidate,None,0,None,stream
    s=inject_targeted_round5(stream,pair);score,cij,cji,r5=targeted_selected_score(s,pair)
    edges=[p for p in PAIRS if (score>mu5t if p==pair else q4[p]>mu[3])]
    groups=groups_from_edges(edges);sizes=sorted(sum(1 for x in 'abc' if groups[x]==g) for g in set(groups.values()))
    structural=int(len(edges)==1 and sizes==[1,2]);qualified=int(structural and pair in edges and score>nu5t)
    data={'pair':pair,'score':score,'c_ij':cij,'c_ji':cji,'r5':r5,'edges':edges,'groups':groups,'structural':structural,'qualified':qualified,'q4':q4}
    if qualified:return groups,executed,5,1,0,groups,pair,1,data,s
    return None,executed,0,0,1,groups,pair,0,data,s


def targeted_annotation(stream,mu,nu,mu5,nu5,mu5t,nu5t,executed,accepted,stop,abstain,candidate,gate_groups,pair,data):
    ann=annotation018(stream,mu,nu,mu5,nu5,executed,accepted,stop,abstain,candidate,gate_groups,0)
    round_count=len(executed);ann['probe_energy']=sum(15*(ALL_AMPLITUDES[r-1]**2) for r in executed)+(0.4 if pair is not None else 0.0)
    ann['probe_block_count']=3*round_count+(2 if pair is not None else 0);ann['targeted_round5_executed']=int(pair is not None);ann['targeted_selected_edge']=''.join(pair) if pair else '';ann['mu_probe_5_targeted']=mu5t;ann['nu_probe_5_targeted']=nu5t
    ann['targeted_selector_correct']=int(pair==('a','b')) if pair else ''
    if data:
        ann['targeted_r5_score']=data['score'];ann['targeted_r5_structural']=data['structural'];ann['targeted_r5_qualified']=data['qualified'];ann['targeted_r5_edges']=';'.join(''.join(x) for x in data['edges'])
        for p in PAIRS:ann[f'targeted_q4_{p[0]}{p[1]}']=data['q4'][p]
    return ann


def run_experiment_019_strategy(seed,family,magnitude,strategy,tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5,mu5t,nu5t):
    if strategy!='targeted_replicated_selective_cumulative_provenance_quorum':
        return run_experiment_018_strategy(seed,family,magnitude,strategy,tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5)
    base=generate_experiment_017_stream(seed,family,magnitude);label=f'experiment019_{family}_{magnitude:.3f}'
    inferred,executed,stop,accepted,abstain,candidate,pair,rescued,data,stream=infer_targeted(base,mu,nu,mu5t,nu5t)
    ann=targeted_annotation(stream,mu,nu,mu5,nu5,mu5t,nu5t,executed,accepted,stop,abstain,candidate,inferred,pair,data)
    if abstain:
        rows=fallback018(seed,family,magnitude,tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5,stream,executed,candidate)
        for r in rows:r['strategy']='targeted_replicated_selective_cumulative_provenance_quorum';r.update(ann)
        return rows
    rows=run_group_gate018(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,stream,ann,inferred)
    for r in rows:r['strategy']='targeted_replicated_selective_cumulative_provenance_quorum'
    return rows
