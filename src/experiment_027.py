from __future__ import annotations

from copy import deepcopy
from math import erf, exp, isfinite, log, pi, sqrt

from experiment_016 import ROUND_AMPLITUDES
from experiment_017 import cumulative_statistics
from experiment_018 import ALL_AMPLITUDES, ROUND5_AMPLITUDE, ROUND5_BLOCKS, cumulative5_statistics
from experiment_023 import diagnostic_noise_factor
from experiment_022 import generate_stress_stream

HYPOTHESES=('H_ab','H_ac','H_bc','H_null')
PAIRS=(('a','b'),('a','c'),('b','c'))
BETA_SCALE=0.20
LOG2PI=log(2.0*pi)


def inject_symmetric_round5(stream):
    s=deepcopy(stream);groups={'a':'G1','b':'G1','c':'G2'};gain=float(s['probe_gain'])
    for target,ts in ROUND5_BLOCKS.items():
        for t in ts:
            for x in 'abc':
                if groups[x]==groups[target]:
                    s[f'probe_obs_{x}'][t]+=gain*ROUND5_AMPLITUDE
    return s


def q_stage(stream,stage):
    if stage in (1,2,3,4):
        C,_=cumulative_statistics(stream,stage)
    elif stage==5:
        C,_=cumulative5_statistics(stream)
    else:
        raise ValueError(stage)
    return {(i,j):min(float(C[(i,j)]),float(C[(j,i)])) for i,j in PAIRS}


def sigma_c(sigma_hat,stage):
    amps=ROUND_AMPLITUDES[:stage] if stage<=4 else ALL_AMPLITUDES
    a1=sum(float(x) for x in amps);a2=sum(float(x)*float(x) for x in amps)
    coeff=(1.0/5.0)+((a1*a1/a2)/20.0)
    return max(float(sigma_hat)*sqrt(coeff),1e-12)


def _log_normal(x,sd):
    z=float(x)/float(sd)
    return -log(float(sd))-0.5*LOG2PI-0.5*z*z


def _normal_cdf(x):
    return 0.5*(1.0+erf(float(x)/sqrt(2.0)))


def _log_signal_marginal(x,sd):
    # X = beta + epsilon, beta~HalfNormal(BETA_SCALE), epsilon~N(0,sd^2).
    omega=sqrt(sd*sd+BETA_SCALE*BETA_SCALE)
    alpha=BETA_SCALE/sd
    z=float(x)/omega
    cdf=max(_normal_cdf(alpha*z),1e-300)
    return log(2.0)-log(omega)-0.5*LOG2PI-0.5*z*z+log(cdf)


def posterior_from_q(q,sd):
    xs={p:float(q[p]) for p in PAIRS};logs={}
    for candidate in PAIRS:
        lp=log(0.25)
        for p in PAIRS:
            lp += _log_signal_marginal(xs[p],sd) if p==candidate else _log_normal(xs[p],sd)
        logs['H_'+''.join(candidate)]=lp
    logs['H_null']=log(0.25)+sum(_log_normal(xs[p],sd) for p in PAIRS)
    m=max(logs.values());weights={h:exp(v-m) for h,v in logs.items()};z=sum(weights.values())
    post={h:weights[h]/z for h in HYPOTHESES}
    if not all(isfinite(v) and v>=0.0 for v in post.values()):raise FloatingPointError(post)
    if abs(sum(post.values())-1.0)>1e-10:raise FloatingPointError(sum(post.values()))
    return post,logs


def evaluate_posterior_path(seed,cell):
    stream=inject_symmetric_round5(generate_stress_stream(seed,cell));_,sigma_hat=diagnostic_noise_factor(stream)
    out=[]
    for stage in range(1,6):
        q=q_stage(stream,stage);sd=sigma_c(sigma_hat,stage);post,logs=posterior_from_q(q,sd)
        top=max(HYPOTHESES,key=lambda h:post[h])
        row={'seed':int(seed),'label':cell['label'],'kind':cell['kind'],'family':cell['family'],'magnitude':float(cell['magnitude']),
             'gain':float(cell.get('gain',stream.get('probe_gain',1.0))),'noise_scale':float(cell.get('noise_scale',1.0)),
             'stage':stage,'sigma_hat':float(sigma_hat),'sigma_c':float(sd),'beta_scale':BETA_SCALE,'top_hypothesis':top,'top_probability':float(post[top]),
             'posterior_entropy':-sum(p*log(max(p,1e-300)) for p in post.values())}
        for p in PAIRS:row['Q_'+''.join(p)]=float(q[p])
        for h in HYPOTHESES:row['P_'+h]=float(post[h]);row['logml_'+h]=float(logs[h])
        out.append(row)
    return out
