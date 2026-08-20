from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
import importlib

from adaptive_model_gating import EVENT_T, N_STEPS
from experiment_010 import SIGMA_REF
from experiment_011 import BETA_ANCHOR, SIGMA_ANCHOR
from experiment_016 import SIGMA_PROBE
from experiment_017 import generate_experiment_017_stream as generate_base_stream
from experiment_021 import QUALIFICATION_AWARE_STRATEGY, run_experiment_021_strategy
from experiment_020 import EARLY_STRATEGY

TARGET019='targeted_replicated_selective_cumulative_provenance_quorum'
TRIAD='triad_persistence'
STRATEGIES=(QUALIFICATION_AWARE_STRATEGY,EARLY_STRATEGY,TARGET019,TRIAD)
MAGNITUDES=(0.25,0.50,1.00)
GAIN_STRESSES=(0.45,0.425,0.35,0.30,0.20,0.10)
NOISE_SCALES=(0.75,1.25,1.50)
TIMING_OFFSETS=(-20,20,50)
ASYM_SCALES=((1.0,0.5),(1.0,1.5),(0.5,1.5))


def cell(label,kind,family,magnitude,**params):
    return {'label':label,'kind':kind,'family':family,'magnitude':float(magnitude),**params}


def frozen_cells():
    out=[cell('healthy_0.00','control','healthy',0.0)]
    families=('drift','common_mode','primary_fault','drift_ab_fault','drift_ab_gain050','drift_ab_gain0375','drift_ab_gain025','drift_ab_gain0125','drift_all_aux_fault')
    for f in families:
        for m in MAGNITUDES:out.append(cell(f'{f}_{m:.2f}','control',f,m))
    for g in GAIN_STRESSES:
        for m in MAGNITUDES:out.append(cell(f'gain_{g:.3f}_{m:.2f}','gain','drift_ab_fault',m,gain=g))
    for scale in NOISE_SCALES:
        for m in MAGNITUDES:out.append(cell(f'noise_{scale:.2f}_{m:.2f}','noise','drift_ab_fault',m,gain=0.50,noise_scale=scale))
    for off in TIMING_OFFSETS:
        tag=f'm{abs(off)}' if off<0 else f'p{off}'
        for m in MAGNITUDES:out.append(cell(f'timing_{tag}_{m:.2f}','timing','drift_ab_fault',m,gain=0.50,timing_offset=off))
    for sa,sb in ASYM_SCALES:
        for m in MAGNITUDES:out.append(cell(f'asym_{sa:.2f}_{sb:.2f}_{m:.2f}','asym','drift_ab_fault',m,gain=0.50,scale_a=sa,scale_b=sb))
    for m in MAGNITUDES:out.append(cell(f'mixed_drift_common_{m:.2f}','mixed','drift',m,gain=1.0,common_magnitude=m))
    if len(out)!=76:raise AssertionError(f'expected 76 frozen cells, got {len(out)}')
    return tuple(out)

CELLS=frozen_cells()


def _base(seed,family,magnitude,gain=None):
    return generate_base_stream(seed,family,magnitude,gain_override=gain)


def _apply_noise_scale(s,magnitude,scale):
    # Reconstruct modeled noisy observations from inherited unit-noise draws while
    # preserving latent trajectory and the coherent A/B fault signal.
    for t in range(1,N_STEPS+1):
        xt=s['x_true'][t]
        s['x_r1'][t]=xt+SIGMA_REF*scale*s['r1_unit_noise'][t]
        s['x_r2'][t]=xt+SIGMA_REF*scale*s['r2_unit_noise'][t]
        qfault=BETA_ANCHOR*magnitude*s['ab_fault_unit_noise'][t] if t>=EVENT_T else 0.0
        s['z'][t]=BETA_ANCHOR*xt+SIGMA_ANCHOR*scale*s['anchor_unit_noise'][t]+qfault
        s['z_b'][t]=BETA_ANCHOR*xt+SIGMA_ANCHOR*scale*s['anchor_b_unit_noise'][t]+qfault
        s['z_c'][t]=BETA_ANCHOR*xt+SIGMA_ANCHOR*scale*s['anchor_c_unit_noise'][t]
        for x in 'abc':
            signal=s[f'probe_obs_{x}'][t]-SIGMA_PROBE*s[f'probe_noise_{x}'][t]
            s[f'probe_obs_{x}'][t]=signal+SIGMA_PROBE*scale*s[f'probe_noise_{x}'][t]
    return s


def _timing_stream(seed,magnitude,gain,offset):
    s=_base(seed,'drift',magnitude,gain)
    onset=EVENT_T+int(offset)
    for t in range(max(1,onset),N_STEPS+1):
        q=BETA_ANCHOR*magnitude*s['ab_fault_unit_noise'][t]
        s['z'][t]+=q;s['z_b'][t]+=q
    return s


def _asym_stream(seed,magnitude,gain,sa,sb):
    s=_base(seed,'drift',magnitude,gain)
    for t in range(EVENT_T,N_STEPS+1):
        q=BETA_ANCHOR*magnitude*s['ab_fault_unit_noise'][t]
        s['z'][t]+=float(sa)*q;s['z_b'][t]+=float(sb)*q
    return s


def _mixed_stream(seed,magnitude,gain,common_magnitude):
    s=_base(seed,'drift',magnitude,gain)
    cm=float(common_magnitude)
    for t in range(EVENT_T,N_STEPS+1):
        q=cm*s['common_unit_noise'][t]
        s['x_primary'][t]+=q;s['x_r1'][t]+=q;s['x_r2'][t]+=q
        if 'true_sigma_x' in s:s['true_sigma_x'][t]=cm
        if 'common_sigma' in s:s['common_sigma'][t]=cm
    return s


def generate_stress_stream(seed,c):
    kind=c['kind'];m=float(c['magnitude'])
    if kind=='control':return _base(seed,c['family'],m,None)
    if kind=='gain':return _base(seed,'drift_ab_fault',m,c['gain'])
    if kind=='noise':return _apply_noise_scale(_base(seed,'drift_ab_fault',m,c['gain']),m,c['noise_scale'])
    if kind=='timing':return _timing_stream(seed,m,c['gain'],c['timing_offset'])
    if kind=='asym':return _asym_stream(seed,m,c['gain'],c['scale_a'],c['scale_b'])
    if kind=='mixed':return _mixed_stream(seed,m,c['gain'],c['common_magnitude'])
    raise ValueError(kind)


@contextmanager
def bind_stressed_stream(stream):
    # Deep legacy dispatch paths regenerate streams in several modules. Bind every
    # relevant generator reference to one immutable per-seed stressed realization.
    targets=(
        ('experiment_016','generate_experiment_016_stream'),
        ('experiment_017','generate_experiment_016_stream'),
        ('experiment_017','generate_experiment_017_stream'),
        ('experiment_017_dispatch','generate_experiment_017_stream'),
        ('experiment_018','generate_experiment_017_stream'),
        ('experiment_019','generate_experiment_017_stream'),
        ('experiment_020','generate_experiment_017_stream'),
        ('experiment_021','generate_experiment_017_stream'),
    )
    old=[]
    def fixed(*args,**kwargs):return deepcopy(stream)
    try:
        for modname,name in targets:
            mod=importlib.import_module(modname);old.append((mod,name,getattr(mod,name)));setattr(mod,name,fixed)
        yield
    finally:
        for mod,name,value in reversed(old):setattr(mod,name,value)


def run_experiment_022_strategy(seed,c,strategy,vals):
    if strategy not in STRATEGIES:raise ValueError(strategy)
    stream=generate_stress_stream(seed,c)
    with bind_stressed_stream(stream):
        rows=run_experiment_021_strategy(seed,c['family'],float(c['magnitude']),strategy,*vals)
    for r in rows:
        r['experiment022_cell']=c['label'];r['experiment022_kind']=c['kind']
        r['experiment022_gain']=c.get('gain',stream.get('probe_gain',''))
        r['experiment022_noise_scale']=c.get('noise_scale',1.0)
        r['experiment022_timing_offset']=c.get('timing_offset',0)
        r['experiment022_asym_scale_a']=c.get('scale_a',1.0);r['experiment022_asym_scale_b']=c.get('scale_b',1.0)
        r['experiment022_common_magnitude']=c.get('common_magnitude',0.0)
    return rows
