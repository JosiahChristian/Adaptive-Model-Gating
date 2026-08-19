#!/usr/bin/env python3
import csv, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from adaptive_model_gating import BASELINE_A, EVENT_T, calibrate_tau, paired_bootstrap_ci
from experiment_008 import calibrate_kappa
from experiment_010 import calibrate_kappa3
from experiment_011 import calibrate_lambda_anchor, run_experiment_011_strategy
RESULTS=ROOT/"results"/"experiment_011"
STRATEGIES=["frozen","continuous","threshold","persistence","health_persistence","triad_persistence","independent_persistence"]
CELLS=[("healthy",0.0)]+[(f,m) for f in ("drift","common_mode","primary_fault","drift_anchor_fault") for m in (0.25,0.5,1.0)]
SEEDS=list(range(11000,11200)); AUDIT=set(range(11000,11005))

def write_csv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True); fields=[]
    for r in rows:
        for k in r:
            if k not in fields: fields.append(k)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

def ci(v,seed): return list(paired_bootstrap_ci(v,seed=seed,reps=10000))
def summary(rows,f,m):
    p200=[r for r in rows if 401<=r["t"]<=600]; pall=[r for r in rows if r["t"]>=401]; p20=[r for r in rows if 401<=r["t"]<=420]
    ats=[r["t"] for r in pall if r["adapt"]]; target=BASELINE_A+m if f in ("drift","drift_anchor_fault") else BASELINE_A
    return {"seed":rows[0]["seed"],"family":f,"magnitude":m,"strategy":rows[0]["strategy"],
      "operational_loss_401_600":sum(r["sq_error"] for r in p200),"operational_loss_401_1200":sum(r["sq_error"] for r in pall),
      "latent_input_loss_401_600":sum(r["latent_input_sq_error"] for r in p200),"latent_input_loss_401_1200":sum(r["latent_input_sq_error"] for r in pall),
      "adapt_401_420":int(any(r["adapt"] for r in p20)),"first_post_event_adaptation":ats[0] if ats else "","adaptation_delay":ats[0]-EVENT_T if ats else "",
      "adapt_count_401_600":sum(r["adapt"] for r in p200),"adapt_count_401_1200":sum(r["adapt"] for r in pall),
      "anchor_mismatch_fraction":sum(r["anchor_mismatch"] for r in pall)/len(pall),"common_mode_suspect_fraction":sum(r["common_mode_suspect"] for r in pall)/len(pall),
      "primary_bad_fraction":sum(r["primary_bad"] for r in pall)/len(pall),"veto_primary_bad_count":sum(r.get("veto_primary_bad",0) for r in pall),
      "veto_common_mode_suspect_count":sum(r.get("veto_common_mode_suspect",0) for r in pall),"independent_veto_count":sum(r.get("independent_veto",0) for r in pall),
      "final_slope":rows[-1]["slope_after"],"target_slope":target,"final_slope_error_abs":abs(rows[-1]["slope_after"]-target)}
def means(rows,k): return {s:sum(r[k] for r in rows if r["strategy"]==s)/len(SEEDS) for s in STRATEGIES}

def main():
    tau=calibrate_tau(); kappa=calibrate_kappa(); kappa3=calibrate_kappa3(); lam=calibrate_lambda_anchor(); summaries=[]; audit=[]
    for f,m in CELLS:
      for seed in SEEDS:
       for strategy in STRATEGIES:
        rows=run_experiment_011_strategy(seed,f,m,strategy,tau,kappa,kappa3,lam); summaries.append(summary(rows,f,m))
        if seed in AUDIT:
         audit.extend(dict(r,family=f,magnitude=m) for r in rows)
    write_csv(RESULTS/"seed_summary.csv",summaries); write_csv(RESULTS/"audit_trace_seeds_11000_11004.csv",audit)
    reports=[]
    for idx,(f,m) in enumerate(CELLS):
      c=[r for r in summaries if r["family"]==f and r["magnitude"]==m]; p={seed:{s:next(r for r in c if r["seed"]==seed and r["strategy"]==s) for s in STRATEGIES} for seed in SEEDS}; bs=20260819011+idx*1000
      rep={"family":f,"magnitude":m,"mean_operational_loss_401_600":means(c,"operational_loss_401_600"),"mean_final_slope_error_abs":means(c,"final_slope_error_abs"),
           "adapt_401_420_rate":means(c,"adapt_401_420"),"mean_anchor_mismatch_fraction":means(c,"anchor_mismatch_fraction"),"mean_common_mode_suspect_fraction":means(c,"common_mode_suspect_fraction"),
           "mean_independent_veto_count":means(c,"independent_veto_count")}
      if f in ("common_mode","primary_fault"):
       d=[p[s]["independent_persistence"]["final_slope_error_abs"]-p[s]["triad_persistence"]["final_slope_error_abs"] for s in SEEDS]; rep["independent_minus_triad_final_slope_error_mean_difference"]=sum(d)/len(d); rep["bootstrap_95_ci"]=ci(d,bs)
      if f in ("drift","drift_anchor_fault"):
       d=[p[s]["independent_persistence"]["operational_loss_401_600"]-p[s]["triad_persistence"]["operational_loss_401_600"] for s in SEEDS]; rep["independent_minus_triad_operational_loss_mean_difference"]=sum(d)/len(d); rep["bootstrap_95_ci"]=ci(d,bs)
       if f=="drift":
        rr=[d0/max(p[s]["triad_persistence"]["operational_loss_401_600"],1e-12) for s,d0 in zip(SEEDS,d)]; rep["mean_relative_excess_loss_R"]=sum(rr)/len(rr); rep["R_bootstrap_95_ci"]=ci(rr,bs+1); rep["non_destruction_upper_lt_0_10"]=rep["R_bootstrap_95_ci"][1]<0.10
      reports.append(rep)
    final={"tau":tau,"kappa":kappa,"kappa3":kappa3,"lambda_anchor":lam,"anchor_calibration_seeds":[600,799],"evaluation_seeds":[11000,11199],"n_seeds_per_cell":200,"cells":reports,"strategies":STRATEGIES,"audit_seeds":sorted(AUDIT)}
    RESULTS.mkdir(parents=True,exist_ok=True); (RESULTS/"report.json").write_text(json.dumps(final,indent=2)+"\n"); print(json.dumps(final,indent=2))
if __name__=="__main__": main()
