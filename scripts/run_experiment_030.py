#!/usr/bin/env python3
import csv,json,math,os,random,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from adaptive_model_gating import BASELINE_A
from experiment_029 import POSTERIOR_RISK_STRATEGY,TRIAD,ACCEPT_THRESHOLD,run_experiment_029_strategy
from run_experiment_021 import calibrations

STRATEGIES=(POSTERIOR_RISK_STRATEGY,TRIAD)
SEEDS=range(30000,31000);AUDIT=set(range(30000,30005));BOOTSTRAP_SEED=30030;BOOTSTRAP_RESAMPLES=10000

def cell(label,kind,family,magnitude,**kw):return {'label':label,'kind':kind,'family':family,'magnitude':float(magnitude),**kw}
CELLS=(
 cell('healthy','control','healthy',0.0),
 cell('drift_0.50','control','drift',.50),
 cell('common_mode_0.25','control','common_mode',.25),
 cell('common_mode_0.50','control','common_mode',.50),
 cell('common_mode_1.00','control','common_mode',1.00),
 cell('g0.500_n1.00','noise','drift_ab_fault',.50,gain=.50,noise_scale=1.00),
 cell('g0.500_n1.50','noise','drift_ab_fault',.50,gain=.50,noise_scale=1.50),
)

def write_csv(path,rows):
 path.parent.mkdir(parents=True,exist_ok=True);fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with path.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def summary(rows,c):
 r0=rows[0];post=[r for r in rows if 401<=r['t']<=600];target=BASELINE_A+float(c['magnitude']) if c['family'].startswith('drift') else BASELINE_A
 accepted=int(float(r0.get('provenance_accepted',0) or 0));correct=int(float(r0.get('accepted_partition_correct',0) or 0))
 return {'seed':int(r0['seed']),'label':c['label'],'strategy':r0['strategy'],'coverage':accepted,'correct':correct,'abstain':int(float(r0.get('provenance_abstain',0) or 0)),
         'posterior_at_deployment':float(r0.get('posterior_at_deployment',0) or 0),'probe_energy':float(r0.get('probe_energy',0) or 0),
         'operational_loss_401_600':sum(float(r['sq_error']) for r in post),'final_slope_error_abs':abs(float(rows[-1]['slope_after'])-target),
         'adapt_signature':','.join(str(r['t']) for r in rows if r.get('adapt'))}

def _quantile(sorted_vals,q):
 if not sorted_vals:return None
 pos=(len(sorted_vals)-1)*q;lo=int(math.floor(pos));hi=int(math.ceil(pos))
 if lo==hi:return sorted_vals[lo]
 w=pos-lo;return sorted_vals[lo]*(1-w)+sorted_vals[hi]*w

def bootstrap_mean_ci(vals,seed):
 vals=list(map(float,vals));n=len(vals);rng=random.Random(seed);means=[]
 for _ in range(BOOTSTRAP_RESAMPLES):
  s=0.0
  for _ in range(n):s+=vals[rng.randrange(n)]
  means.append(s/n)
 means.sort();return [_quantile(means,.025),_quantile(means,.975)]

def paired_rows(rows,label):
 q=[r for r in rows if r['label']==label];by={(int(r['seed']),r['strategy']):r for r in q};out=[]
 for seed in SEEDS:
  a=by[(seed,POSTERIOR_RISK_STRATEGY)];b=by[(seed,TRIAD)]
  out.append({'seed':seed,'delta_loss':float(a['operational_loss_401_600'])-float(b['operational_loss_401_600']),
              'delta_slope':float(a['final_slope_error_abs'])-float(b['final_slope_error_abs'])})
 return out

def report_from(rows):
 H={f'H{i}':True for i in range(1,9)};out={}
 for ix,c in enumerate(CELLS):
  q=[r for r in rows if r['label']==c['label']];by={s:[r for r in q if r['strategy']==s] for s in STRATEGIES};p=by[POSTERIOR_RISK_STRATEGY];accepted=[r for r in p if int(r['coverage'])==1]
  coverage=len(accepted)/len(p);precision=(sum(float(r['correct']) for r in accepted)/len(accepted)) if accepted else None
  pairs=paired_rows(rows,c['label']);dl=[r['delta_loss'] for r in pairs];ds=[r['delta_slope'] for r in pairs]
  dl_ci=bootstrap_mean_ci(dl,BOOTSTRAP_SEED+100*ix+1);ds_ci=bootstrap_mean_ci(ds,BOOTSTRAP_SEED+100*ix+2)
  out[c['label']]={'cell':c,'coverage':coverage,'accepted_precision':precision,'mean_posterior_at_deployment':sum(float(r['posterior_at_deployment']) for r in accepted)/len(accepted) if accepted else None,
                   'mean_delta_loss':sum(dl)/len(dl),'median_delta_loss':_quantile(sorted(dl),.5),'delta_loss_bootstrap_95':dl_ci,
                   'mean_delta_slope':sum(ds)/len(ds),'median_delta_slope':_quantile(sorted(ds),.5),'delta_slope_bootstrap_95':ds_ci,
                   'mean_energy_029':sum(float(r['probe_energy']) for r in p)/len(p)}
 # H1 high topology-confidence condition.
 for label in ('common_mode_0.50','g0.500_n1.00'):
  x=out[label]
  if x['coverage']<.95 or x['accepted_precision'] is None or x['accepted_precision']<.99:H['H1']=False
 # H2 replicated common-mode predictive-loss penalty.
 x=out['common_mode_0.50']
 H['H2']=x['mean_delta_loss']>0 and x['delta_loss_bootstrap_95'][0]>0
 # H3 supported drift/fault non-regression.
 x=out['g0.500_n1.00']
 H['H3']=x['mean_delta_loss']<=.02 and x['delta_loss_bootstrap_95'][1]<=.05
 # H4 context-dependent interaction with paired seed-index bootstrap.
 cm=paired_rows(rows,'common_mode_0.50');df=paired_rows(rows,'g0.500_n1.00');diff=[cm[i]['delta_loss']-df[i]['delta_loss'] for i in range(len(cm))]
 interaction=sum(diff)/len(diff);interaction_ci=bootstrap_mean_ci(diff,BOOTSTRAP_SEED+999)
 H['H4']=interaction>=5.0 and interaction_ci[0]>0
 # H5 common-mode objective conflict.
 H['H5']=out['common_mode_0.50']['mean_delta_loss']>0 and out['common_mode_0.50']['mean_delta_slope']<0
 # H6 benign/control preservation.
 H['H6']=abs(out['healthy']['mean_delta_loss'])<=.02 and abs(out['drift_0.50']['mean_delta_loss'])<=.02
 # H7 fixed common-mode magnitude reporting.
 H['H7']=all(k in out for k in ('common_mode_0.25','common_mode_0.50','common_mode_1.00'))
 # H8 policy contamination guard is structural/provenance metadata.
 H['H8']=abs(ACCEPT_THRESHOLD-.99)<1e-12
 return {'evaluation_seeds':[30000,30999],'n_seeds_per_cell':1000,'cell_count':len(CELLS),'strategies':STRATEGIES,'audit_seeds':sorted(AUDIT),'bootstrap_seed':BOOTSTRAP_SEED,'bootstrap_resamples':BOOTSTRAP_RESAMPLES,
         'hypotheses':H,'accept_threshold':ACCEPT_THRESHOLD,'policy_modification':False,'family_labels_evaluator_only':True,'experiment029_inherited_unchanged':True,'code_commit':os.environ.get('GITHUB_SHA','unknown'),
         'interaction_mean_delta_loss_common_minus_driftfault':interaction,'interaction_bootstrap_95':interaction_ci,'cells':out}
