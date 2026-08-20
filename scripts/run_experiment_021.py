#!/usr/bin/env python3
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from adaptive_model_gating import BASELINE_A,paired_bootstrap_ci
from experiment_020 import EARLY_STRATEGY
from experiment_021 import QUALIFICATION_AWARE_STRATEGY,run_experiment_021_strategy
from run_experiment_020 import STRATEGIES as S20,CELLS,calibrations as calibrations020

STRATEGIES=S20+[QUALIFICATION_AWARE_STRATEGY]
SEEDS=list(range(21000,21200));AUDIT=set(range(21000,21005));RESULTS=ROOT/'results'/'experiment_021'
TARGET019='targeted_replicated_selective_cumulative_provenance_quorum';TRI='triad_persistence'

def write_csv(p,rows):
 p.parent.mkdir(parents=True,exist_ok=True);fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with p.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def summary(rows,f,m):
 p=[r for r in rows if 401<=r['t']<=600];p20=[r for r in rows if 401<=r['t']<=420];r0=rows[0];target=BASELINE_A+m if f.startswith('drift') else BASELINE_A
 gate='|'.join(str(r0.get(f'gate_group_{x}','')) for x in 'abc')
 adapt_sig=','.join(str(r['t']) for r in rows if r.get('adapt'))
 return {'seed':r0['seed'],'family':f,'magnitude':m,'strategy':r0['strategy'],'operational_loss_401_600':sum(r['sq_error'] for r in p),'adapt_401_420':int(any(r['adapt'] for r in p20)),'adapt_signature':adapt_sig,'probe_energy':r0.get('probe_energy',0),'probe_stop_round':r0.get('probe_stop_round',0),'provenance_accepted':r0.get('provenance_accepted',0),'provenance_abstain':r0.get('provenance_abstain',0),'accepted_partition_correct':r0.get('accepted_partition_correct',''),'gate_signature':gate,'inherited_prequalified':r0.get('inherited_prequalified',0),'inherited_prequalification_round':r0.get('inherited_prequalification_round',0),'experiment020_dispatch_entry':r0.get('experiment020_dispatch_entry',0),'final_slope_error_abs':abs(rows[-1]['slope_after']-target)}

def ci(v):return list(paired_bootstrap_ci(v,seed=21021,reps=10000))
def mean_for(c,st,k):
 q=[float(r[k]) for r in c if r['strategy']==st];return sum(q)/len(q)
def paired(c,a,b,k):
 by={(int(float(r['seed'])),r['strategy']):r for r in c};return [float(by[(s,a)][k])-float(by[(s,b)][k]) for s in SEEDS]
def rates(c,st):
 q=[r for r in c if r['strategy']==st];acc=[r for r in q if float(r['provenance_accepted'])==1];wrong=sum(1 for r in acc if float(r['accepted_partition_correct'])!=1)
 return {'coverage':len(acc)/200,'abstention':1-len(acc)/200,'precision':sum(float(r['accepted_partition_correct']) for r in acc)/len(acc) if acc else None,'wrong_acceptance':wrong/200}

def report_from(summaries,*vals):
 qa=QUALIFICATION_AWARE_STRATEGY;early=EARLY_STRATEGY;cells=[]
 for f,m in CELLS:
  c=[r for r in summaries if r['family']==f and float(r['magnitude'])==m];qr=rates(c,qa);er=rates(c,early);tr=rates(c,TARGET019)
  r={'family':f,'magnitude':m,'qualification_aware_rates':qr,'experiment020_rates':er,'experiment019_rates':tr,'mean_probe_energy':{st:mean_for(c,st,'probe_energy') for st in (qa,early,TARGET019,TRI)},'adapt_401_420_rate':{st:mean_for(c,st,'adapt_401_420') for st in (qa,early,TARGET019,TRI)},'mean_operational_loss_401_600':{st:mean_for(c,st,'operational_loss_401_600') for st in (qa,early,TARGET019,TRI)},'mean_final_slope_error_abs':{st:mean_for(c,st,'final_slope_error_abs') for st in (qa,early,TARGET019,TRI)}}
  qrows=[x for x in c if x['strategy']==qa];pre=[x for x in qrows if float(x['inherited_prequalified'])==1];r['prequalification_rate']=len(pre)/200;r['experiment020_dispatch_rate']=sum(float(x['experiment020_dispatch_entry']) for x in qrows)/200
  d=paired(c,qa,early,'operational_loss_401_600');r['vs_experiment020']={'coverage_gap':qr['coverage']-er['coverage'],'loss_mean':sum(d)/200,'loss_ci':ci(d),'energy_gap':r['mean_probe_energy'][qa]-r['mean_probe_energy'][early],'adapt_gap':r['adapt_401_420_rate'][qa]-r['adapt_401_420_rate'][early]}
  by={(int(float(x['seed'])),x['strategy']):x for x in c};mismatches=0
  for x in pre:
   s=int(float(x['seed']));b=by[(s,TARGET019)]
   exact=(int(float(x['probe_stop_round']))==int(float(b['probe_stop_round'])) and int(float(x['provenance_accepted']))==int(float(b['provenance_accepted'])) and x['gate_signature']==b['gate_signature'] and x['adapt_signature']==b['adapt_signature'] and float(x['operational_loss_401_600'])==float(b['operational_loss_401_600']) and float(x['probe_energy'])==float(b['probe_energy']))
   mismatches+=0 if exact else 1
  r['inherited_prequalification_exact_mismatches']=mismatches
  if f in ('drift_ab_gain0375','drift_ab_gain025','drift_ab_gain0125'):
   dt=paired(c,qa,TRI,'operational_loss_401_600');r['attenuation_vs_triad']={'loss_mean':sum(dt)/200,'loss_ci':ci(dt),'adapt_gap':r['adapt_401_420_rate'][qa]-r['adapt_401_420_rate'][TRI]}
  if f=='drift':
   vv=[]
   for s in SEEDS:
    a=float(by[(s,qa)]['operational_loss_401_600']);b=float(by[(s,early)]['operational_loss_401_600']);vv.append((a-b)/max(abs(b),1e-12))
   r['drift_regression']={'relative_excess_mean':sum(vv)/200,'ci':ci(vv),'adapt_gap':r['adapt_401_420_rate'][qa]-r['adapt_401_420_rate'][early]}
  if f in ('common_mode','primary_fault'):
   df=paired(c,qa,early,'final_slope_error_abs');r['fault_regression']={'slope_error_diff_mean':sum(df)/200,'ci':ci(df)}
  cells.append(r)
 return {'evaluation_seeds':[21000,21199],'bootstrap_seed':21021,'n_seeds_per_cell':200,'strategies':STRATEGIES,'cells':cells,'audit_seeds':sorted(AUDIT),'no_new_calibration':True}

def calibrations():return calibrations020()
