"""Adaptive-Model-Gating experimental implementation.

Uses only the Python standard library. Experiment-specific evaluation logic follows
prospectively committed specifications under research/.
"""
from __future__ import annotations
from dataclasses import dataclass
from random import Random
from statistics import mean
from typing import Iterable
N_STEPS=1200; EVENT_T=401; TRANSIENT_END_T=420; ROLLING_WINDOW=20; REFIT_WINDOW=100; INITIAL_FIT_START=101; INITIAL_FIT_END=300; PERSISTENCE_COUNT=3; BASELINE_A=1.5
@dataclass
class LinearModel:
    slope: float
    intercept: float
    def predict(self,x:float)->float: return self.slope*x+self.intercept

def ols_fit(xs,ys):
    if len(xs)!=len(ys) or len(xs)<2: raise ValueError("OLS requires equal-length x/y arrays with >=2 points")
    xb,yb=mean(xs),mean(ys); den=sum((x-xb)**2 for x in xs)
    if den==0: raise ValueError("Cannot fit OLS with zero x variance")
    slope=sum((x-xb)*(y-yb) for x,y in zip(xs,ys))/den
    return LinearModel(slope,yb-slope*xb)

def true_a(condition,t):
    if condition=="stable": return BASELINE_A
    if condition=="transient": return 2.0 if EVENT_T<=t<=TRANSIENT_END_T else BASELINE_A
    if condition=="persistent": return 2.0 if t>=EVENT_T else BASELINE_A
    raise ValueError(condition)

def _generate(seed,a_fn):
    rng=Random(seed); xs=[0.0]*(N_STEPS+1); ys=[0.0]*(N_STEPS+1); av=[BASELINE_A]*(N_STEPS+1)
    for t in range(1,N_STEPS+1):
        xs[t]=0.8*xs[t-1]+rng.gauss(0,0.5); av[t]=a_fn(t); ys[t]=av[t]*xs[t]+rng.gauss(0,0.5)
    return xs,ys,av

def generate_stream(seed,condition): return _generate(seed,lambda t:true_a(condition,t))
def generate_parameter_change_stream(seed,delta_a=0.0,transient_duration=None):
    if delta_a<0 or (transient_duration is not None and transient_duration<=0): raise ValueError("invalid change")
    def a(t):
        changed=delta_a>0 and t>=EVENT_T and (transient_duration is None or t<EVENT_T+transient_duration)
        return BASELINE_A+delta_a if changed else BASELINE_A
    return _generate(seed,a)
def generate_gradual_drift_stream(seed,delta_a,ramp_duration):
    if delta_a<=0 or ramp_duration<=0: raise ValueError("delta_a and ramp_duration must be positive")
    def a(t):
        if t<EVENT_T: return BASELINE_A
        j=t-EVENT_T+1
        return BASELINE_A+delta_a*(min(j,ramp_duration)/ramp_duration)
    return _generate(seed,a)
def initial_model(xs,ys): return ols_fit(xs[INITIAL_FIT_START:INITIAL_FIT_END+1],ys[INITIAL_FIT_START:INITIAL_FIT_END+1])
def refit(xs,ys,t): return ols_fit(xs[t-REFIT_WINDOW+1:t+1],ys[t-REFIT_WINDOW+1:t+1])
def run_strategy_on_stream(seed,condition_label,strategy,tau,xs,ys,a_values):
    model=initial_model(xs,ys); sq=[]; streak=0; rows=[]
    for t in range(INITIAL_FIT_END+1,N_STEPS+1):
        sb,ib=model.slope,model.intercept; yh=model.predict(xs[t]); err=ys[t]-yh; se=err*err; sq.append(se); rm=mean(sq[-ROLLING_WINDOW:]) if len(sq)>=ROLLING_WINDOW else None; adapt=False
        if strategy=="continuous": adapt=True
        elif strategy=="threshold" and rm is not None: adapt=rm>tau
        elif strategy=="persistence" and rm is not None:
            streak=streak+1 if rm>tau else 0; adapt=streak>=PERSISTENCE_COUNT
        elif strategy!="frozen": raise ValueError(strategy)
        if adapt:
            model=refit(xs,ys,t)
            if strategy=="persistence": streak=0
        rows.append({"seed":seed,"condition":condition_label,"strategy":strategy,"t":t,"x":xs[t],"y":ys[t],"y_hat":yh,"error":err,"sq_error":se,"rolling_mse":rm,"tau":tau,"adapt":int(adapt),"true_a":a_values[t],"slope_before":sb,"intercept_before":ib,"slope_after":model.slope,"intercept_after":model.intercept})
    return rows
def run_strategy(seed,condition,strategy,tau):
    x,y,a=generate_stream(seed,condition); return run_strategy_on_stream(seed,condition,strategy,tau,x,y,a)
def run_parameter_change_strategy(seed,delta_a,transient_duration,strategy,tau):
    x,y,a=generate_parameter_change_stream(seed,delta_a,transient_duration); label="stable" if delta_a==0 else (f"persistent_da_{delta_a:.2f}" if transient_duration is None else f"transient_da_{delta_a:.2f}_d_{transient_duration}"); return run_strategy_on_stream(seed,label,strategy,tau,x,y,a)
def run_gradual_drift_strategy(seed,delta_a,ramp_duration,strategy,tau):
    x,y,a=generate_gradual_drift_stream(seed,delta_a,ramp_duration); return run_strategy_on_stream(seed,f"gradual_da_{delta_a:.2f}_r_{ramp_duration}",strategy,tau,x,y,a)
def stable_calibration_values(seeds:Iterable[int]):
    vals=[]
    for seed in seeds:
        x,y,_=generate_stream(seed,"stable"); m=initial_model(x,y); sq=[]
        for t in range(INITIAL_FIT_END+1,N_STEPS+1):
            e=y[t]-m.predict(x[t]); sq.append(e*e)
            if len(sq)>=ROLLING_WINDOW: vals.append(mean(sq[-ROLLING_WINDOW:]))
    return vals
def empirical_quantile(values,q):
    if not values or not 0<=q<=1: raise ValueError("invalid quantile")
    o=sorted(values); return o[int(q*(len(o)-1))]
def calibrate_tau(): return empirical_quantile(stable_calibration_values(range(200)),0.99)
def summarize(rows):
    post=[r for r in rows if EVENT_T<=r["t"]<=600]; tw=[r for r in rows if EVENT_T<=r["t"]<=TRANSIENT_END_T]; aft=[r for r in rows if r["t"]>=EVENT_T]; ads=[r["t"] for r in aft if r["adapt"]]
    return {"seed":rows[0]["seed"],"condition":rows[0]["condition"],"strategy":rows[0]["strategy"],"persistent_horizon_loss":sum(r["sq_error"] for r in post),"transient_adaptation":int(any(r["adapt"] for r in tw)),"post_event_adaptation_count":sum(r["adapt"] for r in aft),"first_post_event_adaptation":ads[0] if ads else None,"adaptation_delay":ads[0]-EVENT_T if ads else None}
def summarize_parameter_change(rows,transient_duration):
    p200=[r for r in rows if EVENT_T<=r["t"]<=600]; full=[r for r in rows if r["t"]>=EVENT_T]; end=N_STEPS if transient_duration is None else EVENT_T+transient_duration-1; ev=[r for r in rows if EVENT_T<=r["t"]<=end]; ads=[r["t"] for r in full if r["adapt"]]
    return {"seed":rows[0]["seed"],"condition":rows[0]["condition"],"strategy":rows[0]["strategy"],"loss_401_600":sum(r["sq_error"] for r in p200),"adapt_during_true_event":int(any(r["adapt"] for r in ev)),"adapt_401_600":int(any(r["adapt"] for r in p200)),"adapt_401_1200":int(any(r["adapt"] for r in full)),"adapt_count_401_600":sum(r["adapt"] for r in p200),"adapt_count_401_1200":sum(r["adapt"] for r in full),"first_post_event_adaptation":ads[0] if ads else None,"adaptation_delay":ads[0]-EVENT_T if ads else None}
def paired_bootstrap_ci(differences,seed=8675309,reps=10000):
    rng=Random(seed); n=len(differences); est=[mean(differences[rng.randrange(n)] for _ in range(n)) for _ in range(reps)]; est.sort(); return est[int(.025*reps)],est[int(.975*reps)]
