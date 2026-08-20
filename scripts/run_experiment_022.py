#!/usr/bin/env python3
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from adaptive_model_gating import BASELINE_A,paired_bootstrap_ci
from experiment_022 import CELLS,STRATEGIES,run_experiment_022_strategy
from experiment_021 import QUALIFICATION_AWARE_STRATEGY
from experiment_020 import EARLY_STRATEGY
from run_experiment_021 import calibrations

SEEDS=list(range(22000,22200));AUDIT=set(range(22000,22005));RESULTS=ROOT/'results'/'experiment_022'
TARGET019='targeted_replicated_selective_cumulative_provenance_quorum';TRIAD='triad_persistence';QA=QUALIFICATION_AWARE_STRATEGY;EARLY=EARLY_STRATEGY

def write_csv(p,rows):
 p.parent.mkdir(parents=True,exist_ok=True);fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with p.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def summary(rows,c):
 p=[r for r in rows if 401<=r['t']<=600];p20=[r for r in rows if 401<=r['t']<=420];r0=rows[0]
 target=BASELINE_A+float(c['magnitude']) if c['kind'] in ('gain','noise','timing','asym','mixed') or c['family'].startswith('drift') else BASELINE_A
 return {'seed':r0['seed'],'cell':c['label'],'kind':c['kind'],'family':c['family'],'magnitude':c['magnitude'],'strategy':r0['strategy'],'gain':r0.get('experiment022_gain',r0.get('probe_gain','')),'operational_loss_401_600':sum(r['sq_error'] for r in p),'adapt_401_420':int(any(r['adapt'] for r in p20)),'adapt_signature':','.join(str(r['t']) for r in rows if r.get('adapt')),'probe_energy':r0.get('probe_energy',0),'probe_stop_round':r0.get('probe_stop_round',0),'provenance_accepted':r0.get('provenance_accepted',0),'provenance_abstain':r0.get('provenance_abstain',0),'accepted_partition_correct':r0.get('accepted_partition_correct',''),'gate_signature':'|'.join(str(r0.get(f'gate_group_{x}','')) for x in 'abc'),'inherited_prequalified':r0.get('inherited_prequalified',0),'final_slope_error_abs':abs(rows[-1]['slope_after']-target)}

def ci(v):return list(paired_bootstrap_ci(v,seed=22022,reps=10000))
def rates(c,st):
 q=[r for r in c if r['strategy']==st];acc=[r for r in q if float(r['provenance_accepted'])==1];wrong=sum(1 for r in acc if float(r['accepted_partition_correct'])!=1)
 return {'coverage':len(acc)/200,'abstention':1-len(acc)/200,'accepted_n':len(acc),'correct_n':len(acc)-wrong,'precision':((len(acc)-wrong)/len(acc) if acc else None),'wrong_acceptance':wrong/200}
def mean_for(c,st,k):
 q=[float(r[k]) for r in c if r['strategy']==st];return sum(q)/len(q)
def paired(c,a,b,k):
 by={(int(float(r['seed'])),r['strategy']):r for r in c};return [float(by[(s,a)][k])-float(by[(s,b)][k]) for s in SEEDS]

def cell_report(summaries,cdef):
 c=[r for r in summaries if r['cell']==cdef['label']];qa=rates(c,QA);er=rates(c,EARLY);tr=rates(c,TARGET019);rr=rates(c,TRIAD)
 out={'cell':cdef,'rates':{QA:qa,EARLY:er,TARGET019:tr,TRIAD:rr},'mean_probe_energy':{st:mean_for(c,st,'probe_energy') for st in STRATEGIES},'adapt_401_420_rate':{st:mean_for(c,st,'adapt_401_420') for st in STRATEGIES},'mean_operational_loss_401_600':{st:mean_for(c,st,'operational_loss_401_600') for st in STRATEGIES},'mean_final_slope_error_abs':{st:mean_for(c,st,'final_slope_error_abs') for st in STRATEGIES}}
 d=paired(c,QA,EARLY,'operational_loss_401_600');out['qa_minus_early_loss']={'mean':sum(d)/200,'ci':ci(d)}
 by={(int(float(r['seed'])),r['strategy']):r for r in c};mismatch=0;pre=0
 for s in SEEDS:
  q=by[(s,QA)]
  if float(q['inherited_prequalified'])==1:
   pre+=1;b=by[(s,TARGET019)]
   exact=(int(float(q['probe_stop_round']))==int(float(b['probe_stop_round'])) and int(float(q['provenance_accepted']))==int(float(b['provenance_accepted'])) and q['gate_signature']==b['gate_signature'] and q['adapt_signature']==b['adapt_signature'] and float(q['operational_loss_401_600'])==float(b['operational_loss_401_600']) and float(q['probe_energy'])==float(b['probe_energy']))
   if not exact:mismatch+=1
 out['prequalification_rate']=pre/200;out['inherited_dispatch_mismatches']=mismatch
 return out

def evaluate_hypotheses(cells):
 h1=all(x['rates'][QA]['wrong_acceptance']==0 for x in cells)
 h2=True;h2_details=[]
 for x in cells:
  r=x['rates'][QA]
  if r['accepted_n']>=20:
   ok=r['precision'] is not None and r['precision']>=.99;h2=h2 and ok;h2_details.append((x['cell']['label'],ok,r['accepted_n'],r['precision']))
 h3=True;h3_details=[]
 for x in cells:
  c=x['cell'];g=c.get('gain',None)
  if c['kind'] in ('gain','noise','timing','asym') and g is not None and float(g)>=.35:
   q=x['rates'][QA]['coverage'];e=x['rates'][EARLY]['coverage'];ok=(q>=.90 if e>=.90 else q>=e-.03);h3=h3 and ok;h3_details.append((c['label'],ok,q,e))
 h4=True;h4_details=[]
 for x in cells:
  c=x['cell'];g=c.get('gain',None)
  if c['kind']=='gain' and g is not None and float(g)<=.20:
   q=x['rates'][QA];gap=x['adapt_401_420_rate'][QA]-x['adapt_401_420_rate'][TRIAD];ok=q['wrong_acceptance']==0 and gap<=.02;h4=h4 and ok;h4_details.append((c['label'],ok,gap,q['wrong_acceptance']))
 h5=True;h5_details=[]
 for x in cells:
  q=x['rates'][QA]['coverage'];e=x['rates'][EARLY]['coverage']
  if abs(q-e)<=.03+1e-12:
   gap=x['mean_probe_energy'][QA]-x['mean_probe_energy'][EARLY];ok=gap<=.01+1e-12;h5=h5 and ok;h5_details.append((x['cell']['label'],ok,gap))
 h6=all(x['inherited_dispatch_mismatches']==0 for x in cells)
 return {'H1_safety':h1,'H2_precision':h2,'H3_moderate_information_utility':h3,'H4_low_information_conservatism':h4,'H5_energy':h5,'H6_dispatch_integrity':h6,'H2_details':h2_details,'H3_details':h3_details,'H4_details':h4_details,'H5_details':h5_details}

def report_from(summaries):
 cells=[cell_report(summaries,c) for c in CELLS]
 return {'evaluation_seeds':[22000,22199],'bootstrap_seed':22022,'n_seeds_per_cell':200,'cell_count':len(CELLS),'strategies':list(STRATEGIES),'no_recalibration':True,'audit_seeds':sorted(AUDIT),'hypotheses':evaluate_hypotheses(cells),'cells':cells}

def main():
 vals=calibrations();summaries=[];audit=[]
 for c in CELLS:
  for seed in SEEDS:
   for st in STRATEGIES:
    rows=run_experiment_022_strategy(seed,c,st,vals);summaries.append(summary(rows,c))
    if seed in AUDIT:audit.extend(dict(r,cell=c['label'],kind=c['kind']) for r in rows)
 write_csv(RESULTS/'seed_summary.csv',summaries);write_csv(RESULTS/'audit_trace_seeds_22000_22004.csv',audit);rep=report_from(summaries);RESULTS.mkdir(parents=True,exist_ok=True);(RESULTS/'report.json').write_text(json.dumps(rep,indent=2)+'\n');print(json.dumps(rep['hypotheses'],indent=2))
if __name__=='__main__':main()
