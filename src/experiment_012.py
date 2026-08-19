from __future__ import annotations
from random import Random
from statistics import mean, median

from adaptive_model_gating import BASELINE_A, EVENT_T, INITIAL_FIT_END, N_STEPS, PERSISTENCE_COUNT, ROLLING_WINDOW, empirical_quantile, initial_model, refit, run_strategy_on_stream
from experiment_008 import run_health_persistence_on_stream
from experiment_010 import SIGMA_REF, classify_triad, rolling_pairwise_health, run_triad_persistence_on_stream
from experiment_011 import BETA_ANCHOR, SIGMA_ANCHOR, calibrate_lambda_anchor, run_independent_persistence_on_stream

CALIBRATION_SEEDS=range(800,1000)
FAMILIES={"healthy","drift","common_mode","primary_fault","drift_anchor_a_fault","drift_anchor_b_fault","drift_dual_anchor_fault"}


def generate_experiment_012_stream(seed,family,magnitude):
    if family not in FAMILIES: raise ValueError(family)
    if magnitude < 0: raise ValueError("magnitude must be nonnegative")
    rng=Random(seed)
    keys=("x_true","x_primary","x_r1","x_r2","z","z_b","y","a","physical_epsilon","r1_unit_noise","r2_unit_noise","anchor_unit_noise","anchor_b_unit_noise","common_unit_noise","primary_unit_noise","anchor_fault_unit_noise","anchor_b_fault_unit_noise","true_sigma_x","ref_fault_unit_noise","primary_fault_sigma","ref1_fault_sigma","common_sigma")
    s={k:[0.0]*(N_STEPS+1) for k in keys}; s["a"]=[BASELINE_A]*(N_STEPS+1)
    for t in range(1,N_STEPS+1):
        s["x_true"][t]=0.8*s["x_true"][t-1]+rng.gauss(0,0.5); s["physical_epsilon"][t]=rng.gauss(0,0.5)
        for k in ("r1_unit_noise","r2_unit_noise","anchor_unit_noise","anchor_b_unit_noise","common_unit_noise","primary_unit_noise","anchor_fault_unit_noise","anchor_b_fault_unit_noise"): s[k][t]=rng.gauss(0,1)
        xt=s["x_true"][t]; s["x_primary"][t]=xt; s["x_r1"][t]=xt+SIGMA_REF*s["r1_unit_noise"][t]; s["x_r2"][t]=xt+SIGMA_REF*s["r2_unit_noise"][t]
        s["z"][t]=BETA_ANCHOR*xt+SIGMA_ANCHOR*s["anchor_unit_noise"][t]; s["z_b"][t]=BETA_ANCHOR*xt+SIGMA_ANCHOR*s["anchor_b_unit_noise"][t]
        if t>=EVENT_T:
            if family=="drift": s["a"][t]=BASELINE_A+magnitude
            elif family=="common_mode":
                q=magnitude*s["common_unit_noise"][t]; s["x_primary"][t]+=q; s["x_r1"][t]+=q; s["x_r2"][t]+=q; s["true_sigma_x"][t]=magnitude; s["common_sigma"][t]=magnitude
            elif family=="primary_fault": s["x_primary"][t]+=magnitude*s["primary_unit_noise"][t]; s["true_sigma_x"][t]=magnitude; s["primary_fault_sigma"][t]=magnitude
            elif family in ("drift_anchor_a_fault","drift_anchor_b_fault","drift_dual_anchor_fault"):
                s["a"][t]=BASELINE_A+magnitude
                if family in ("drift_anchor_a_fault","drift_dual_anchor_fault"): s["z"][t]+=BETA_ANCHOR*magnitude*s["anchor_fault_unit_noise"][t]
                if family=="drift_anchor_b_fault": s["z_b"][t]+=BETA_ANCHOR*magnitude*s["anchor_b_fault_unit_noise"][t]
                elif family=="drift_dual_anchor_fault": s["z_b"][t]+=BETA_ANCHOR*magnitude*s["anchor_fault_unit_noise"][t]
        s["y"][t]=s["a"][t]*xt+s["physical_epsilon"][t]
    s["x_ref"]=s["x_r1"]; s["reference_unit_noise"]=s["r1_unit_noise"]
    return s


def rolling_dual_anchor_health(stream):
    xm=[0.0]*(N_STEPS+1); xa=[0.0]*(N_STEPS+1); xb=[0.0]*(N_STEPS+1); ga=[None]*(N_STEPS+1); gb=[None]*(N_STEPS+1); dab=[None]*(N_STEPS+1)
    ba=[]; bb=[]; bd=[]
    for t in range(1,N_STEPS+1):
        xm[t]=median((stream["x_primary"][t],stream["x_r1"][t],stream["x_r2"][t])); xa[t]=stream["z"][t]/BETA_ANCHOR; xb[t]=stream["z_b"][t]/BETA_ANCHOR
        ba.append((xm[t]-xa[t])**2); bb.append((xm[t]-xb[t])**2); bd.append((xa[t]-xb[t])**2)
        if len(ba)>=ROLLING_WINDOW: ga[t]=mean(ba[-ROLLING_WINDOW:]); gb[t]=mean(bb[-ROLLING_WINDOW:]); dab[t]=mean(bd[-ROLLING_WINDOW:])
    return xm,xa,xb,ga,gb,dab


def calibrate_dual_anchor_thresholds():
    vb=[]; vd=[]
    for seed in CALIBRATION_SEEDS:
        s=generate_experiment_012_stream(seed,"healthy",0.0); _,_,_,_,gb,dab=rolling_dual_anchor_health(s)
        vb.extend(gb[t] for t in range(101,301) if gb[t] is not None); vd.extend(dab[t] for t in range(101,301) if dab[t] is not None)
    return empirical_quantile(vb,0.99),empirical_quantile(vd,0.99)


def run_dual_independent_arbitration_on_stream(seed,label,tau,kappa3,lambda_a,lambda_b,lambda_ab,stream):
    xp,ys=stream["x_primary"],stream["y"]; model=initial_model(xp,ys); sq=[]; streak=0; rows=[]; pair={k:[] for k in ("h_p_r1","h_p_r2","h_r1_r2")}; ba=[]; bb=[]; bd=[]
    for t in range(INITIAL_FIT_END+1,N_STEPS+1):
        sb,ib=model.slope,model.intercept; yh=model.predict(xp[t]); err=ys[t]-yh; se=err*err; sq.append(se); rmse=mean(sq[-ROLLING_WINDOW:]) if len(sq)>=ROLLING_WINDOW else None
        pv={"h_p_r1":(xp[t]-stream["x_r1"][t])**2,"h_p_r2":(xp[t]-stream["x_r2"][t])**2,"h_r1_r2":(stream["x_r1"][t]-stream["x_r2"][t])**2}; hv={}
        for k,v in pv.items(): pair[k].append(v); hv[k]=mean(pair[k][-ROLLING_WINDOW:]) if len(pair[k])>=ROLLING_WINDOW else None
        pbad,r1bad,r2bad,state=classify_triad(hv["h_p_r1"],hv["h_p_r2"],hv["h_r1_r2"],kappa3)
        xm=median((xp[t],stream["x_r1"][t],stream["x_r2"][t])); xa=stream["z"][t]/BETA_ANCHOR; xb=stream["z_b"][t]/BETA_ANCHOR
        ba.append((xm-xa)**2); bb.append((xm-xb)**2); bd.append((xa-xb)**2); ga=mean(ba[-ROLLING_WINDOW:]) if len(ba)>=ROLLING_WINDOW else None; gb=mean(bb[-ROLLING_WINDOW:]) if len(bb)>=ROLLING_WINDOW else None; gd=mean(bd[-ROLLING_WINDOW:]) if len(bd)>=ROLLING_WINDOW else None
        ma=int(ga is not None and ga>lambda_a); mb=int(gb is not None and gb>lambda_b); dis=int(gd is not None and gd>lambda_ab); consistent=int(ga is not None and all(hv[k] is not None and hv[k]<=kappa3 for k in hv)); suspect=int(consistent and ma and mb and not dis)
        if rmse is not None: streak=streak+1 if rmse>tau else 0
        ready=streak>=PERSISTENCE_COUNT; veto_p=int(ready and pbad); veto_c=int(ready and suspect); veto=int(veto_p or veto_c); adapt=int(ready and not veto)
        if ready: streak=0
        if adapt: model=refit(xp,ys,t)
        latent_hat=sb*stream["x_true"][t]+ib
        rows.append({"seed":seed,"condition":label,"strategy":"dual_independent_arbitration","t":t,"x":xp[t],"y":ys[t],"y_hat":yh,"error":err,"sq_error":se,"rolling_mse":rmse,"tau":tau,"adapt":adapt,"true_a":stream["a"][t],"slope_before":sb,"intercept_before":ib,"slope_after":model.slope,"intercept_after":model.intercept,"x_true":stream["x_true"][t],"x_primary":xp[t],"x_r1":stream["x_r1"][t],"x_r2":stream["x_r2"][t],"z":stream["z"][t],"z_b":stream["z_b"][t],"x_med":xm,"x_a":xa,"x_b":xb,"g_anchor":ga,"g_anchor_b":gb,"g_anchor_ab":gd,"lambda_anchor":lambda_a,"lambda_anchor_b":lambda_b,"lambda_anchor_ab":lambda_ab,"h_p_r1":hv["h_p_r1"],"h_p_r2":hv["h_p_r2"],"h_r1_r2":hv["h_r1_r2"],"kappa3":kappa3,"primary_bad":pbad,"reference1_bad":r1bad,"reference2_bad":r2bad,"triad_state":state,"triad_consistent":consistent,"anchor_mismatch":ma,"anchor_b_mismatch":mb,"anchor_ab_disagreement":dis,"common_mode_suspect":suspect,"veto_primary_bad":veto_p,"veto_common_mode_suspect":veto_c,"independent_veto":veto,"latent_input_sq_error":(ys[t]-latent_hat)**2})
    return rows


def _annotate_dual(rows,stream,kappa3,lambda_a,lambda_b,lambda_ab):
    h=rolling_pairwise_health(stream); xm,xa,xb,ga,gb,gd=rolling_dual_anchor_health(stream)
    for row in rows:
        t=row["t"]; pbad,r1bad,r2bad,state=classify_triad(h["h_p_r1"][t],h["h_p_r2"][t],h["h_r1_r2"][t],kappa3); consistent=int(ga[t] is not None and all(h[k][t] is not None and h[k][t]<=kappa3 for k in h)); ma=int(ga[t] is not None and ga[t]>lambda_a); mb=int(gb[t] is not None and gb[t]>lambda_b); dis=int(gd[t] is not None and gd[t]>lambda_ab)
        row.update({"x_true":stream["x_true"][t],"x_primary":stream["x_primary"][t],"x_r1":stream["x_r1"][t],"x_r2":stream["x_r2"][t],"z":stream["z"][t],"z_b":stream["z_b"][t],"x_med":xm[t],"x_a":xa[t],"x_b":xb[t],"g_anchor":ga[t],"g_anchor_b":gb[t],"g_anchor_ab":gd[t],"lambda_anchor":lambda_a,"lambda_anchor_b":lambda_b,"lambda_anchor_ab":lambda_ab,"h_p_r1":h["h_p_r1"][t],"h_p_r2":h["h_p_r2"][t],"h_r1_r2":h["h_r1_r2"][t],"kappa3":kappa3,"primary_bad":pbad,"reference1_bad":r1bad,"reference2_bad":r2bad,"triad_state":state,"triad_consistent":consistent,"anchor_mismatch":ma,"anchor_b_mismatch":mb,"anchor_ab_disagreement":dis,"common_mode_suspect":int(consistent and ma and mb and not dis)})
        row.setdefault("veto_primary_bad",0); row.setdefault("veto_common_mode_suspect",0); row.setdefault("independent_veto",0); latent=row["slope_before"]*stream["x_true"][t]+row["intercept_before"]; row["latent_input_sq_error"]=(stream["y"][t]-latent)**2
    return rows


def run_experiment_012_strategy(seed,family,magnitude,strategy,tau,kappa,kappa3,lambda_a,lambda_b,lambda_ab):
    allowed={"frozen","continuous","threshold","persistence","health_persistence","triad_persistence","independent_persistence","dual_independent_arbitration"}
    if strategy not in allowed: raise ValueError(strategy)
    stream=generate_experiment_012_stream(seed,family,magnitude); label=f"experiment012_{family}_{magnitude:.2f}"
    if strategy=="dual_independent_arbitration": return run_dual_independent_arbitration_on_stream(seed,label,tau,kappa3,lambda_a,lambda_b,lambda_ab,stream)
    if strategy=="independent_persistence": return _annotate_dual(run_independent_persistence_on_stream(seed,label,tau,kappa3,lambda_a,stream),stream,kappa3,lambda_a,lambda_b,lambda_ab)
    if strategy=="triad_persistence": return _annotate_dual(run_triad_persistence_on_stream(seed,label,tau,kappa3,stream),stream,kappa3,lambda_a,lambda_b,lambda_ab)
    if strategy=="health_persistence": return _annotate_dual(run_health_persistence_on_stream(seed,label,tau,kappa,stream),stream,kappa3,lambda_a,lambda_b,lambda_ab)
    return _annotate_dual(run_strategy_on_stream(seed,label,strategy,tau,stream["x_primary"],stream["y"],stream["a"]),stream,kappa3,lambda_a,lambda_b,lambda_ab)
