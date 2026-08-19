#!/usr/bin/env python3
import csv, json, os, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src")); sys.path.insert(0,str(ROOT/"scripts"))
from adaptive_model_gating import calibrate_tau
from experiment_008 import calibrate_kappa
from experiment_010 import calibrate_kappa3
from experiment_011 import calibrate_lambda_anchor, run_experiment_011_strategy
from run_experiment_011 import STRATEGIES, SEEDS, AUDIT, summary, write_csv

def main():
 f=os.environ["EXPERIMENT_011_FAMILY"]; m=float(os.environ["EXPERIMENT_011_MAGNITUDE"]); label=os.environ["EXPERIMENT_011_LABEL"]
 tau=calibrate_tau(); k=calibrate_kappa(); k3=calibrate_kappa3(); lam=calibrate_lambda_anchor(); summaries=[]; audit=[]
 for seed in SEEDS:
  for strategy in STRATEGIES:
   rows=run_experiment_011_strategy(seed,f,m,strategy,tau,k,k3,lam); summaries.append(summary(rows,f,m))
   if seed in AUDIT: audit.extend(dict(r,family=f,magnitude=m) for r in rows)
 out=ROOT/"results"/"experiment_011_shards"/label; write_csv(out/"seed_summary.csv",summaries); write_csv(out/"audit.csv",audit)
 (out/"metadata.json").write_text(json.dumps({"family":f,"magnitude":m,"tau":tau,"kappa":k,"kappa3":k3,"lambda_anchor":lam,"evaluation_seeds":[11000,11199],"rows":len(summaries)},indent=2)+"\n")
if __name__=="__main__": main()
