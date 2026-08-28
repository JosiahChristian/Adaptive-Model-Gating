from __future__ import annotations
import math
import random

import experiment_047 as exp47
import experiment_048 as exp48
import experiment_049 as exp49
import experiment_061 as exp61
import experiment_063 as exp63
from experiment_046 import E_THRESHOLD, bet_factor

OPERATIVE_SPEC_ISSUE = 250
PROVENANCE_CLOSURE_ISSUE = 251
IMPLEMENTATION_CLOSURE_ISSUE = 252
ARCHITECTURES = ('A0','A1','A2','A3')
CANDIDATE_ORDER = ('H_ab','H_ac','H_bc')
EDGE_PAIRS = {
    'H_ab': (('a','b'),('b','a')),
    'H_ac': (('a','c'),('c','a')),
    'H_bc': (('b','c'),('c','b')),
}
SEED_RANGES = {
    'Q1': (6400000,6403000),
    'Q2': (6403000,6406000),
    'Q3': (6406000,6409000),
    'Q4': (6409000,6412000),
    'Q5': (6412000,6415000),
    'Q6': (6415000,6418000),
}
Q1_ROUND_SCALES = (0.40,0.70,1.00,1.60,2.20)
Q2_FORWARD_SD = 1.0
Q2_REVERSE_SD = 2.5
Q3_RHO = 0.65
Q4_CONTAMINATION = 0.15
Q4_CONTAMINATION_SD = 3.0
Q5_CONTAMINATION = 0.10
Q5_SHIFT = 1.00
Q6_DF = 2.2
Q6_UNIT_IQR_DENOM = 1.6039801884225622
W_CUTOFF = exp63.W_CUTOFF


def _student_t22(rng):
    z = rng.gauss(0.0,1.0)
    chi = rng.gammavariate(Q6_DF/2.0,2.0)
    return (z/math.sqrt(chi/Q6_DF))/Q6_UNIT_IQR_DENOM


def _panel_vector(panel,rng):
    if panel == 'Q3':
        rho=Q3_RHO; scale=math.sqrt(1-rho*rho); x=rng.gauss(0,1); out=[x]
        for _ in range(29):
            x=rho*x+scale*rng.gauss(0,1); out.append(x)
        return out
    out=[]
    for i in range(30):
        r=i//6; within=i%6
        if panel == 'Q1': x=rng.gauss(0,Q1_ROUND_SCALES[r])
        elif panel == 'Q2': x=rng.gauss(0,Q2_FORWARD_SD if within<3 else Q2_REVERSE_SD)
        elif panel == 'Q4': x=rng.gauss(0,Q4_CONTAMINATION_SD if rng.random()<Q4_CONTAMINATION else 1.0)
        elif panel == 'Q5': x=rng.gauss(Q5_SHIFT if rng.random()<Q5_CONTAMINATION else 0.0,1.0)
        elif panel == 'Q6': x=_student_t22(rng)
        else: raise ValueError(panel)
        out.append(x)
    return out


def stress_cube(panel,seed,start):
    rng=random.Random(seed)
    while True:
        vectors={h:_panel_vector(panel,rng) for h in CANDIDATE_ORDER}
        candidate=CANDIDATE_ORDER[(seed-start)%len(CANDIDATE_ORDER)]
        vals=vectors[candidate]
        if any(not math.isfinite(x) for v in vectors.values() for x in v): continue
        if any(x==0.0 for x in vals) or len(set(abs(x) for x in vals))!=30: continue
        cube={}
        for h,v in vectors.items():
            fwd,rev=EDGE_PAIRS[h]
            for r in range(1,6):
                b=(r-1)*6
                cube[(r,fwd)]=tuple(v[b:b+3])
                cube[(r,rev)]=tuple(v[b+3:b+6])
        if len(cube)!=30 or sum(len(v) for v in cube.values())!=90: raise AssertionError('cube_shape')
        return candidate,vectors,cube


def confirmation_candidate(cube):
    mats={}
    for r in range(1,6):
        C={pair:sum(cube[(r,pair)])/3.0 for h in CANDIDATE_ORDER for pair in EDGE_PAIRS[h]}
        mats[r]=({},C)
    _,_,candidate=exp61.confirmation_profile_061(mats)
    return candidate


def _underlying_accept(architecture,candidate,vectors,cube):
    edge=EDGE_PAIRS[candidate]
    if architecture == 'A0':
        w,_=exp63.signed_rank_statistic_30(vectors[candidate])
        return int(w>=W_CUTOFF), {'wplus':w}
    if architecture == 'A1':
        signs=[]
        for r in range(1,6):
            signs.extend(cube[(r,edge[0])][:2]); signs.extend(cube[(r,edge[1])][:2])
        if len(signs)!=exp49.SIGN_COUNT: raise AssertionError('A1_sign_count')
        positive=sum(int(x>0.0) for x in signs)
        return int(positive>=exp49.POSITIVE_CUTOFF), {'positive_sign_count':positive}
    if architecture == 'A2':
        E=1.0
        for r in range(1,6):
            for pair in edge:
                E*=exp48.sign_factor(sum(cube[(r,pair)])/3.0)
        return int(E>=E_THRESHOLD), {'e_final':E}
    if architecture == 'A3':
        E=1.0
        for r in range(1,6):
            for pair in edge:
                E*=bet_factor(sum(cube[(r,pair)])/3.0)
        return int(E>=E_THRESHOLD), {'e_final':E}
    raise ValueError(architecture)


def evaluate_draw(panel,seed,start=None):
    if start is None: start=SEED_RANGES[panel][0]
    candidate,vectors,cube=stress_cube(panel,seed,start)
    conf=confirmation_candidate(cube)
    agreement=int(candidate==conf)
    rows={}
    for architecture in ARCHITECTURES:
        underlying,detail=_underlying_accept(architecture,candidate,vectors,cube)
        final=int(underlying and agreement)
        rows[architecture]={
            'panel':panel,'seed':seed,'architecture':architecture,
            'discovery_candidate':candidate,'confirmation_candidate':conf,
            'agreement':agreement,'underlying_accept':underlying,'final_accept':final,
            **detail,
        }
    return rows


def provenance_integrity():
    return all((
        exp49.SIGN_COUNT==20,
        exp49.POSITIVE_CUTOFF==16,
        exp49.P16_NUMERATOR==6196,
        exp49.P16_DENOMINATOR==1048576,
        abs(exp49.ACCEPT_E-(1.0/(6196/1048576)))<1e-12,
        exp48.sign_factor(1.0)==2.0,
        exp48.sign_factor(-1.0)==0.0,
        exp48.sign_factor(0.0)==1.0,
        E_THRESHOLD==100.0,
        W_CUTOFF==345,
    ))
