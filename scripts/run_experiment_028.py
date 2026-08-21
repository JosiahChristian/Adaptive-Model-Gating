#!/usr/bin/env python3
import csv,json,math,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from experiment_027 import HYPOTHESES,BETA_SCALE
from experiment_028 import evaluate_both_paths

SEEDS=range(28000,29000);AUDIT=set(range(28000,28005));TRUE='H_ab'
MODELS=('directed_covariance','q_diagonal_experiment027')

def cell(label,kind,family,magnitude,**kw):return {'label':label,'kind':kind,'family':family,'magnitude':float(magnitude),**kw}
def cells():
 out=[]
 for g,scales in ((.50,(1.0,1.25,1.5,2.0)),(.425,(1.0,1.5,2.0)),(.35,(1.0,1.5,2.0))):
  for n in scales:out.append(cell(f'g{g:.3f}_n{n:.2f}','noise','drift_ab_fault',.50,gain=g,noise_scale=n))
 out += [cell('healthy','control','healthy',0.0),cell('drift_0.50','control','drift',.50),cell('common_mode_0.50','control','common_mode',.50),cell('primary_fault_0.50','control','primary_fault',.50),cell('drift_all_aux_fault_0.50','control','drift_all_aux_fault',.50,operational_truth_unresolved=True)]
 if len(out)!=15:raise AssertionError(len(out))
 return tuple(out)
CELLS=cells()

def write_csv(path,rows):
 path.parent.mkdir(parents=True,exist_ok=True);fields=[]
 for r in rows:
  for k in r:
   if k not in fields:fields.append(k)
 with path.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def ece(rows):
 bins=[];total=len(rows);v=0.0
 for b in range(10):
  lo=b/10;hi=(b+1)/10
  q=[r for r in rows if float(r['top_probability'])>=lo and (float(r['top_probability'])<hi if b<9 else float(r['top_probability'])<=hi)]
  if not q:bins.append({'bin':b,'count':0,'mean_confidence':None,'accuracy':None});continue
  conf=sum(float(r['top_probability']) for r in q)/len(q);acc=sum(r['top_hypothesis']==TRUE for r in q)/len(q);v+=len(q)/total*abs(conf-acc);bins.append({'bin':b,'count':len(q),'mean_confidence':conf,'accuracy':acc})
 return v,bins

def metrics(rows,truth=True):
 if not truth:return {'n':len(rows),'mean_max_posterior':sum(float(r['top_probability']) for r in rows)/len(rows),'mean_entropy':sum(float(r['posterior_entropy']) for r in rows)/len(rows),'operational_truth_unresolved':True}
 n=len(rows);brier=sum(sum((float(r['P_'+h])-(1.0 if h==TRUE else 0.0))**2 for h in HYPOTHESES) for r in rows)/n;ll=-sum(math.log(max(float(r['P_'+TRUE]),1e-300)) for r in rows)/n;acc=sum(r['top_hypothesis']==TRUE for r in rows)/n;ec,bins=ece(rows)
 return {'n':n,'brier':brier,'log_loss':ll,'top_accuracy':acc,'ece':ec,'mean_p_true':sum(float(r['P_'+TRUE]) for r in rows)/n,'mean_p_null':sum(float(r['P_H_null']) for r in rows)/n,'mean_max_posterior':sum(float(r['top_probability']) for r in rows)/n,'mean_entropy':sum(float(r['posterior_entropy']) for r in rows)/n,'reliability':bins}

def report_from(rows):
 by={}
 for c in CELLS:
  cm={}
  unresolved=bool(c.get('operational_truth_unresolved',False))
  for model in MODELS:
   mr=[r for r in rows if r['label']==c['label'] and r['model']==model];st={}
   for s in range(1,6):st[str(s)]=metrics([r for r in mr if int(r['stage'])==s],truth=not unresolved)
   cm[model]={'stages':st}
  by[c['label']]={'cell':c,'models':cm}
 new=lambda label:by[label]['models']['directed_covariance']['stages']['5']
 old=lambda label:by[label]['models']['q_diagonal_experiment027']['stages']['5']
 H={f'H{i}':True for i in range(1,10)}
 for r in rows:
  if r['model']!='directed_covariance':continue
  ps=[float(r['P_'+h]) for h in HYPOTHESES]
  if any((not math.isfinite(p) or p<0) for p in ps) or abs(sum(ps)-1)>1e-10:H['H1']=False
 k=new('g0.500_n1.50');H['H2']=k['ece']<=.05 and k['brier']<=.12
 for label in ('g0.500_n1.25','g0.425_n1.00'):
  if new(label)['ece']>.04:H['H3']=False
 nk,ok=new('g0.500_n1.50'),old('g0.500_n1.50');H['H4']=(ok['ece']-nk['ece']>=.02 and nk['brier']<=ok['brier']+.01)
 nom=new('g0.500_n1.00');H['H5']=nom['brier']<=.03 and nom['ece']<=.03 and nom['top_accuracy']>=.98
 for label in ('g0.500_n1.00','g0.500_n1.25','g0.500_n1.50','g0.500_n2.00'):
  s3=by[label]['models']['directed_covariance']['stages']['3'];s5=by[label]['models']['directed_covariance']['stages']['5']
  if s5['mean_p_true']<s3['mean_p_true']-.02:H['H6']=False
 H['H7']=new('g0.350_n2.00')['mean_max_posterior']<=new('g0.500_n1.00')['mean_max_posterior']-.10
 aux=by['drift_all_aux_fault_0.50']['models']['directed_covariance']['stages']['5'];H['H8']=bool(aux.get('operational_truth_unresolved')) and 'mean_entropy' in aux and 'mean_max_posterior' in aux
 H['H9']=BETA_SCALE==.20
 return {'evaluation_seeds':[28000,28999],'n_seeds_per_cell':1000,'cell_count':15,'audit_seeds':sorted(AUDIT),'models':MODELS,'hypotheses':H,'hypothesis_labels':HYPOTHESES,'truth_label_for_ordinary_cells':TRUE,'uniform_prior':[.25,.25,.25,.25],'beta_scale':BETA_SCALE,'analytic_covariance_variance':'sigma_hat^2 * [1/5 + S1^2/(20*S2)]','analytic_covariance_shared_baseline':'sigma_hat^2 * S1^2/(20*S2)','no_probability_recalibration':True,'code_commit':os.environ.get('GITHUB_SHA','unknown'),'cells':by}
