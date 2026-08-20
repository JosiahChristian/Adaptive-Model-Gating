#!/usr/bin/env python3
import csv,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from experiment_019 import run_experiment_019_strategy
from run_experiment_019 import STRATEGIES,SEEDS,AUDIT,calibrations,summary,write_csv
EXPECTED_SUMMARIES=15*200
EXPECTED_AUDIT_ROWS=15*5*900

def main():
 f=os.environ['EXPERIMENT_019_FAMILY'];m=float(os.environ['EXPERIMENT_019_MAGNITUDE']);label=os.environ['EXPERIMENT_019_LABEL']
 out=ROOT/'results'/'experiment_019_shards'/label;out.mkdir(parents=True,exist_ok=True)
 tmp=out/'audit.jsonl.tmp';fields=[];audit_count=0;summaries=[];vals=calibrations()
 with tmp.open('w',encoding='utf-8') as audit_tmp:
  for seed in SEEDS:
   for st in STRATEGIES:
    rows=run_experiment_019_strategy(seed,f,m,st,*vals);summaries.append(summary(rows,f,m))
    if seed in AUDIT:
     for r in rows:
      row=dict(r,family=f,magnitude=m)
      for k in row:
       if k not in fields:fields.append(k)
      audit_tmp.write(json.dumps(row,separators=(',',':'))+'\n');audit_count+=1
 if len(summaries)!=EXPECTED_SUMMARIES:raise ValueError(f'Expected {EXPECTED_SUMMARIES} summaries, got {len(summaries)}')
 if audit_count!=EXPECTED_AUDIT_ROWS:raise ValueError(f'Expected {EXPECTED_AUDIT_ROWS} audit rows, got {audit_count}')
 write_csv(out/'seed_summary.csv',summaries)
 with (out/'audit.csv').open('w',newline='',encoding='utf-8') as dst,tmp.open(encoding='utf-8') as src:
  writer=csv.DictWriter(dst,fieldnames=fields);writer.writeheader()
  for line in src:writer.writerow(json.loads(line))
 tmp.unlink()
 tau,k,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5,mu5t,nu5t=vals
 meta={'family':f,'magnitude':m,'tau':tau,'kappa':k,'kappa3':k3,'lambda_anchor_a':la,'lambda_anchor_b':lb,'lambda_anchor_c':lc,'lambda_anchor_ab':lab,'lambda_anchor_ac':lac,'lambda_anchor_bc':lbc,'lambda_probe_rounds':list(lambdas),'mu_cumulative_rounds':list(mu),'nu_cumulative_rounds':list(nu),'mu_5':mu5,'nu_5':nu5,'mu_5_targeted':mu5t,'nu_5_targeted':nu5t,'evaluation_seeds':[19000,19199],'rows':len(summaries),'audit_rows':audit_count}
 (out/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
if __name__=='__main__':main()
