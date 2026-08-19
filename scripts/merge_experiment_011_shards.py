#!/usr/bin/env python3
import csv, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src")); sys.path.insert(0,str(ROOT/"scripts"))
from adaptive_model_gating import paired_bootstrap_ci
from run_experiment_011 import STRATEGIES,CELLS,SEEDS,write_csv,means
SRC=ROOT/"results"/"experiment_011_shards"; OUT=ROOT/"results"/"experiment_011"
def readcsv(p):
 with p.open(encoding="utf-8",newline="") as f:return list(csv.DictReader(f))
def num(r):
 for k,v in list(r.items()):
  if k in {"family","strategy","first_post_event_adaptation","adaptation_delay"}:continue
  try:r[k]=float(v)
  except:pass
 return r
def ci(v,s):return list(paired_bootstrap_ci(v,seed=s,reps=10000))
def main():
 summaries=[]; audit=[]; metas=[]
 for f,m in CELLS:
  label="healthy_0.00" if f=="healthy" else f"{f}_{m:.2f}"
  d=SRC/label; summaries += [num(r) for r in readcsv(d/"seed_summary.csv")]; audit += [num(r) for r in readcsv(d/"audit.csv")]; metas.append(json.loads((d/"metadata.json").read_text()))
 if len(summaries)!=13*7*200:raise ValueError(f"Expected 18200 summaries, got {len(summaries)}")
 if {int(r["seed"]) for r in summaries}!=set(SEEDS):raise ValueError("Evaluation seed coverage mismatch")
 write_csv(OUT/"seed_summary.csv",summaries); write_csv(OUT/"audit_trace_seeds_11000_11004.csv",audit)
 reports=[]
 for idx,(f,m) in enumerate(CELLS):
  c=[r for r in summaries if r["family"]==f and float(r["magnitude"])==m]; p={s:{st:next(r for r in c if int(r["seed"])==s and r["strategy"]==st) for st in STRATEGIES} for s in SEEDS}; bs=20260819011+idx*1000
  rep={"family":f,"magnitude":m,"mean_operational_loss_401_600":means(c,"operational_loss_401_600"),"mean_final_slope_error_abs":means(c,"final_slope_error_abs"),"adapt_401_420_rate":means(c,"adapt_401_420"),"mean_anchor_mismatch_fraction":means(c,"anchor_mismatch_fraction"),"mean_common_mode_suspect_fraction":means(c,"common_mode_suspect_fraction"),"mean_independent_veto_count":means(c,"independent_veto_count")}
  if f in ("common_mode","primary_fault"):
   d=[p[s]["independent_persistence"]["final_slope_error_abs"]-p[s]["triad_persistence"]["final_slope_error_abs"] for s in SEEDS];rep["independent_minus_triad_final_slope_error_mean_difference"]=sum(d)/len(d);rep["bootstrap_95_ci"]=ci(d,bs)
  if f in ("drift","drift_anchor_fault"):
   d=[p[s]["independent_persistence"]["operational_loss_401_600"]-p[s]["triad_persistence"]["operational_loss_401_600"] for s in SEEDS];rep["independent_minus_triad_operational_loss_mean_difference"]=sum(d)/len(d);rep["bootstrap_95_ci"]=ci(d,bs)
   if f=="drift":
    rr=[d0/max(p[s]["triad_persistence"]["operational_loss_401_600"],1e-12) for s,d0 in zip(SEEDS,d)];rep["mean_relative_excess_loss_R"]=sum(rr)/len(rr);rep["R_bootstrap_95_ci"]=ci(rr,bs+1);rep["non_destruction_upper_lt_0_10"]=rep["R_bootstrap_95_ci"][1]<0.10
  reports.append(rep)
 first=metas[0]
 for x in metas[1:]:
  for k in ("tau","kappa","kappa3","lambda_anchor"):
   if x[k]!=first[k]:raise ValueError(f"Threshold mismatch {k}")
 final={"tau":first["tau"],"kappa":first["kappa"],"kappa3":first["kappa3"],"lambda_anchor":first["lambda_anchor"],"anchor_calibration_seeds":[600,799],"evaluation_seeds":[11000,11199],"n_seeds_per_cell":200,"strategies":STRATEGIES,"cells":reports,"audit_seeds":[11000,11001,11002,11003,11004]}
 OUT.mkdir(parents=True,exist_ok=True);(OUT/"report.json").write_text(json.dumps(final,indent=2)+"\n");print(json.dumps(final,indent=2))
if __name__=="__main__":main()
