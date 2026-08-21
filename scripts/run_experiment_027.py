#!/usr/bin/env python3
import csv,json,math,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from experiment_027 import HYPOTHESES,BETA_SCALE,evaluate_posterior_path

SEEDS=range(27000,28000);AUDIT=set(range(27000,27005));TRUE='H_ab'

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
 if not truth:
  return {'n':len(rows),'mean_max_posterior':sum(float(r['top_probability']) for r in rows)/len(rows),'mean_entropy':sum(float(r['posterior_entropy']) for r in rows)/len(rows),'operational_truth_unresolved':True}
 n=len(rows);brier=sum(sum((float(r['P_'+h])-(1.0 if h==TRUE else 0.0))**2 for h in HYPOTHESES) for r in rows)/n;logloss=-sum(math.log(max(float(r['P_'+TRUE]),1e-300)) for r in rows)/n;acc=sum(r['top_hypothesis']==TRUE for r in rows)/n;ec,bins=ece(rows)
 return {'n':n,'brier':brier,'log_loss':logloss,'top_accuracy':acc,'ece':ec,'mean_p_true':sum(float(r['P_'+TRUE]) for r in rows)/n,'mean_p_null':sum(float(r['P_H_null']) for r in rows)/n,'mean_max_posterior':sum(float(r['top_probability']) for r in rows)/n,'mean_entropy':sum(float(r['posterior_entropy']) for r in rows)/n,'reliability':bins}

def report_from(rows):
 by={}
 for c in CELLS:
  cr=[r for r in rows if r['label']==c['label']];stages={}
  unresolved=bool(c.get('operational_truth_unresolved',False))
  for s in range(1,6):stages[str(s)]=metrics([r for r in cr if int(r['stage'])==s],truth=not unresolved)
  by[c['label']]={'cell':c,'stages':stages}
 H={f'H{i}':True for i in range(1,9)}
 for r in rows:
  ps=[float(r['P_'+h]) for h in HYPOTHESES]
  if any((not math.isfinite(p) or p<0) for p in ps) or abs(sum(ps)-1)>1e-10:H['H1']=False
 key=by['g0.500_n1.50']['stages']['5'];H['H2']=key['ece']<=.05 and key['brier']<=.12
 for label in ('g0.500_n1.25','g0.425_n1.00'):
  if by[label]['stages']['5']['ece']>.04:H['H3']=False
 for label in ('g0.500_n1.00','g0.500_n1.25','g0.500_n1.50','g0.500_n2.00'):
  if by[label]['stages']['5']['mean_p_true'] < by[label]['stages']['3']['mean_p_true']-.02:H['H4']=False
 H['H5']=by['g0.350_n2.00']['stages']['5']['mean_max_posterior'] <= by['g0.500_n1.00']['stages']['5']['mean_max_posterior']-.10
 for label in ('healthy','drift_0.50','common_mode_0.50','primary_fault_0.50'):
  m=by[label]['stages']['5']
  if m['top_accuracy']<.95 or m['mean_p_true']<.90:H['H6']=False
 aux=by['drift_all_aux_fault_0.50']['stages']['5'];H['H7']=bool(aux.get('operational_truth_unresolved')) and 'mean_entropy' in aux and 'mean_max_posterior' in aux
 H['H8']=BETA_SCALE==.20
 return {'evaluation_seeds':[27000,27999],'n_seeds_per_cell':1000,'cell_count':15,'audit_seeds':sorted(AUDIT),'hypotheses':H,'hypothesis_labels':HYPOTHESES,'truth_label_for_ordinary_cells':TRUE,'uniform_prior':[.25,.25,.25,.25],'beta_scale':BETA_SCALE,'analytic_variance_formula':'sigma_hat^2 * [1/5 + (A1^2/A2)/20]','no_probability_recalibration':True,'code_commit':os.environ.get('GITHUB_SHA','unknown'),'cells':by}
