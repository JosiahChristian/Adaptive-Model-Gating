from __future__ import annotations

from copy import deepcopy

from adaptive_model_gating import EVENT_T
from experiment_010 import run_triad_persistence_on_stream
from experiment_011 import BETA_ANCHOR
from experiment_016 import ROUND_AMPLITUDES, ROUND_BLOCKS, SIGMA_PROBE
from experiment_018 import ALL_AMPLITUDES, ROUND5_BLOCKS, _run_group_gate as run_group_gate018
from experiment_022 import generate_stress_stream
from experiment_029 import POSTERIOR_RISK_STRATEGY, TRIAD, _annotation, infer_posterior_risk
from experiment_032 import COMPOSED_STRATEGY, _run_composed_gate

TOPOLOGIES=('H_ac','H_bc')
STRATEGIES=(COMPOSED_STRATEGY,POSTERIOR_RISK_STRATEGY,TRIAD)
PAIR={'H_ac':('a','c'),'H_bc':('b','c')}
GROUPS={
    'H_ac':{'a':'G1','c':'G1','b':'G2'},
    'H_bc':{'b':'G1','c':'G1','a':'G2'},
}


def cell(label,topology,kind,family,magnitude,**kw):
    if topology not in TOPOLOGIES: raise ValueError(topology)
    return {'label':label,'topology':topology,'kind':kind,'family':family,'magnitude':float(magnitude),**kw}


def frozen_cells():
    out=[]
    for h in TOPOLOGIES:
        tag=h[2:]
        out += [
            cell(f'{tag}_g0.500_n1.00',h,'noise','drift_ab_fault',.50,gain=.50,noise_scale=1.00),
            cell(f'{tag}_g0.500_n1.50',h,'noise','drift_ab_fault',.50,gain=.50,noise_scale=1.50),
            cell(f'{tag}_g0.425_n1.00',h,'noise','drift_ab_fault',.50,gain=.425,noise_scale=1.00),
            cell(f'{tag}_g0.400_n1.40',h,'noise','drift_ab_fault',.50,gain=.40,noise_scale=1.40),
            cell(f'{tag}_g0.350_n1.25',h,'noise','drift_ab_fault',.50,gain=.35,noise_scale=1.25),
            cell(f'{tag}_timing_p35_n1.50',h,'timing','drift_ab_fault',.50,gain=.50,noise_scale=1.50,timing_offset=35),
            cell(f'{tag}_healthy',h,'control','healthy',0.0),
            cell(f'{tag}_common_mode_0.50',h,'control','common_mode',.50),
            cell(f'{tag}_common_mode_1.00',h,'control','common_mode',1.00),
        ]
    if len(out)!=18: raise AssertionError(len(out))
    return tuple(out)

CELLS=frozen_cells()


def _base_cell(c):
    # Translate Experiment-034 cell metadata into the already-frozen stress generator.
    if c['kind']=='noise':
        return {'label':'base','kind':'noise','family':'drift_ab_fault','magnitude':c['magnitude'],'gain':c['gain'],'noise_scale':c['noise_scale']}
    if c['kind']=='timing':
        # Experiment 022 timing construction is followed by the explicit frozen noise transform here.
        return {'label':'base','kind':'timing','family':'drift_ab_fault','magnitude':c['magnitude'],'gain':c['gain'],'timing_offset':c['timing_offset']}
    return {'label':'base','kind':'control','family':c['family'],'magnitude':c['magnitude']}


def _apply_requested_noise(stream,scale):
    if float(scale)==1.0:return stream
    # Use Experiment-022 public construction logic through a synthetic noise cell, but preserve
    # any timing-specific fault geometry by scaling only stored diagnostic noise components here.
    from experiment_010 import SIGMA_REF
    from experiment_011 import SIGMA_ANCHOR
    from experiment_016 import SIGMA_PROBE
    s=deepcopy(stream);scale=float(scale)
    for t in range(1,len(s['x_true'])):
        xt=s['x_true'][t]
        # Preserve existing additive event corruption by extracting it relative to the old nominal model.
        r1_extra=s['x_r1'][t]-(xt+SIGMA_REF*s['r1_unit_noise'][t])
        r2_extra=s['x_r2'][t]-(xt+SIGMA_REF*s['r2_unit_noise'][t])
        s['x_r1'][t]=xt+SIGMA_REF*scale*s['r1_unit_noise'][t]+r1_extra
        s['x_r2'][t]=xt+SIGMA_REF*scale*s['r2_unit_noise'][t]+r2_extra
        for key,unit in (('z','anchor_unit_noise'),('z_b','anchor_b_unit_noise'),('z_c','anchor_c_unit_noise')):
            nominal=BETA_ANCHOR*xt+SIGMA_ANCHOR*s[unit][t]
            extra=s[key][t]-nominal
            s[key][t]=BETA_ANCHOR*xt+SIGMA_ANCHOR*scale*s[unit][t]+extra
        for x in 'abc':
            signal=s[f'probe_obs_{x}'][t]-SIGMA_PROBE*s[f'probe_noise_{x}'][t]
            s[f'probe_obs_{x}'][t]=signal+SIGMA_PROBE*scale*s[f'probe_noise_{x}'][t]
    return s


def _rebuild_probe_topology(s,topology):
    groups=GROUPS[topology];gain=float(s['probe_gain'])
    # Reconstruct from the exact stored unit-noise draws so no new randomness enters.
    for t in range(1,len(s['x_true'])):
        for x in 'abc': s[f'probe_obs_{x}'][t]=SIGMA_PROBE*s[f'probe_noise_{x}'][t]
    rounds=[(ROUND_AMPLITUDES[r-1],ROUND_BLOCKS[r]) for r in range(1,5)]
    rounds.append((ALL_AMPLITUDES[4],ROUND5_BLOCKS))
    for amp,blocks in rounds:
        for target,ts in blocks.items():
            for t in ts:
                for x in 'abc':
                    if groups[x]==groups[target]: s[f'probe_obs_{x}'][t]+=gain*float(amp)
    return s


def _move_aux_fault(s,c):
    if c['family']!='drift_ab_fault': return s
    onset=EVENT_T+int(c.get('timing_offset',0))
    pair=PAIR[c['topology']]
    m=float(c['magnitude'])
    for t in range(max(1,onset),len(s['x_true'])):
        q=BETA_ANCHOR*m*s['ab_fault_unit_noise'][t]
        # Remove inherited H_ab corruption, then apply the same seedwise draw to the true pair.
        s['z'][t]-=q;s['z_b'][t]-=q
        if 'a' in pair:s['z'][t]+=q
        if 'b' in pair:s['z_b'][t]+=q
        if 'c' in pair:s['z_c'][t]+=q
    return s


def generate_experiment_034_stream(seed,c):
    base=generate_stress_stream(seed,_base_cell(c))
    if c['kind']=='timing': base=_apply_requested_noise(base,c.get('noise_scale',1.0))
    s=_move_aux_fault(deepcopy(base),c)
    s=_rebuild_probe_topology(s,c['topology'])
    s['experiment034_topology']=c['topology']
    return s


def explicit_topology_correct(deploy_hypothesis,truth):
    return int(str(deploy_hypothesis)==str(truth))


def _triad(seed,c,stream,tau,k3):
    rows=run_triad_persistence_on_stream(seed,f'experiment034_{c["label"]}',tau,k3,stream)
    for r in rows:
        r['strategy']=TRIAD
        r['provenance_accepted']=0;r['provenance_abstain']=1;r['accepted_partition_correct']=''
        r['posterior_deploy_hypothesis']='';r['posterior_at_deployment']='';r['probe_stop_round']=0;r['probe_energy']=0.0
        r['context_vote_t']=0;r['context_removed_suspect_veto']=0;r['triad_primary_bad']=int(r.get('primary_bad',0) or 0)
    return rows


def run_experiment_034_strategy(seed,c,strategy,vals):
    if strategy not in STRATEGIES: raise ValueError(strategy)
    stream=generate_experiment_034_stream(seed,c)
    groups,accepted,abstain,stop,path=infer_posterior_risk(stream)
    ann=_annotation(stream,groups,accepted,abstain,stop,path)
    tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5,mu5t,nu5t,mu4e,nu4e=vals
    if strategy==TRIAD:
        rows=_triad(seed,c,stream,tau,k3)
    elif abstain:
        rows=_triad(seed,c,stream,tau,k3)
        for r in rows:r['strategy']=strategy;r.update(ann)
    elif strategy==POSTERIOR_RISK_STRATEGY:
        rows=run_group_gate018(seed,f'experiment034_{c["label"]}',tau,k3,la,lb,lc,lab,lac,lbc,stream,ann,groups)
        for r in rows:r['strategy']=POSTERIOR_RISK_STRATEGY
    else:
        rows=_run_composed_gate(seed,f'experiment034_{c["label"]}',tau,k3,la,lb,lc,lab,lac,lbc,stream,ann,groups)
    deploy=str(ann.get('posterior_deploy_hypothesis',''))
    explicit=explicit_topology_correct(deploy,c['topology']) if accepted else ''
    for r in rows:
        r['experiment034_cell']=c['label'];r['experiment034_topology_truth']=c['topology'];r['experiment034_explicit_topology_correct']=explicit
        r['experiment034_kind']=c['kind'];r['experiment034_gain']=c.get('gain',stream.get('probe_gain',''));r['experiment034_noise_scale']=c.get('noise_scale',1.0)
    return rows
