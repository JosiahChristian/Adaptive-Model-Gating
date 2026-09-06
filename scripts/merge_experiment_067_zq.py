#!/usr/bin/env python3
import argparse, json, math
from collections import Counter
from pathlib import Path

CANDS=('H_ab','H_ac','H_bc')
PANELS={f'ZQ{i}':(6700000+(i-1)*4000,6700000+i*4000) for i in range(1,7)}
STRIDE=10_000_000

def cand_from_scores(scores):
    return min(CANDS,key=lambda c:(float(scores[c]),CANDS.index(c)))

def tied(scores):
    vals=[float(scores[c]) for c in CANDS]
    m=min(vals)
    return sum(abs(v-m)<=1e-12 for v in vals)>1

def cramers_v(xs,ys):
    n=len(xs); table=[[0]*3 for _ in range(3)]
    for x,y in zip(xs,ys): table[CANDS.index(x)][CANDS.index(y)]+=1
    rs=[sum(r) for r in table]; cs=[sum(table[i][j] for i in range(3)) for j in range(3)]
    chi=0.0
    for i in range(3):
      for j in range(3):
        e=rs[i]*cs[j]/n
        if e: chi+=(table[i][j]-e)**2/e
    return math.sqrt(chi/(n*2))

def quantile(vals,q):
    a=sorted(vals); p=(len(a)-1)*q; lo=int(math.floor(p)); hi=int(math.ceil(p))
    return a[lo] if lo==hi else a[lo]+(a[hi]-a[lo])*(p-lo)

def stats(vals):
    n=len(vals); mean=sum(vals)/n; sd=math.sqrt(sum((x-mean)**2 for x in vals)/(n-1))
    return {'mean':mean,'sd':sd,'median':quantile(vals,.5),'q10':quantile(vals,.1),'q90':quantile(vals,.9)}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--input',required=True); ap.add_argument('--out',required=True); a=ap.parse_args()
    root=Path(a.input); out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    metas=list(root.rglob('meta.json')); seen={}; rows_by={}
    for mp in metas:
      m=json.loads(mp.read_text())
      if m.get('experiment')!=67 or m.get('role')!='zq_diagnostic_shard': continue
      key=(m['panel'],int(m['shard_index']))
      if key in seen: raise AssertionError(f'duplicate_coordinate:{key}')
      if key[0] not in PANELS or key[1] not in range(4): raise AssertionError('coordinate')
      if m.get('operative_spec_issue')!=279 or m.get('provenance_closure_issue')!=280 or m.get('preflight_issue')!=281 or m.get('execution_closure_issue')!=282: raise AssertionError('provenance')
      rp=mp.parent/'rows.jsonl'; rows=[json.loads(x) for x in rp.read_text().splitlines() if x.strip()]
      if len(rows)!=1000 or int(m.get('n'))!=1000: raise AssertionError('shard_n')
      seen[key]=m; rows_by[key]=rows
    expected={(p,k) for p in PANELS for k in range(4)}
    if set(seen)!=expected: raise AssertionError(f'coordinate_set:{sorted(expected-set(seen))}')
    report={'experiment':67,'integrity_pass':True,'source_rows':0,'panels':{},'rq_seeds_touched':False,'experiment_066_validation_touched':False}
    merged=[]
    for panel,(start,stop) in PANELS.items():
      rows=[]
      for k in range(4): rows+=rows_by[(panel,k)]
      seeds=[int(r['seed']) for r in rows]
      if seeds!=list(range(start,stop)): raise AssertionError(f'seed_coverage:{panel}')
      rep_labels=[[] for _ in range(5)]; tie_n=0; scorevals={c:[] for c in CANDS}; diffs={(CANDS[i],CANDS[j]):[] for i in range(3) for j in range(i+1,3)}
      source_pool=[[0]*3 for _ in range(3)]; source_match={c:[0,0] for c in CANDS}; unanim=0
      for r in rows:
        if r.get('panel')!=panel: raise AssertionError('panel_identity')
        if r.get('source_candidate') not in CANDS: raise AssertionError('source_candidate')
        reps=r.get('replicas',[])
        if len(reps)!=5: raise AssertionError('replica_count')
        labels=[]
        for j,rep in enumerate(reps,1):
          if int(rep.get('replica_index'))!=j or int(rep.get('replica_seed'))!=int(r['seed'])+STRIDE*j or rep.get('discovery_used') is not False: raise AssertionError('replica_identity')
          scores=rep.get('confirmation_scores',{})
          if set(scores)!=set(CANDS): raise AssertionError('score_keys')
          cc=cand_from_scores(scores)
          if rep.get('confirmation_candidate')!=cc or bool(rep.get('topology_tie_flag'))!=tied(scores): raise AssertionError('topology_reconstruction')
          labels.append(cc); rep_labels[j-1].append(cc); tie_n+=int(tied(scores))
          for c in CANDS: scorevals[c].append(float(scores[c]))
          for x,y in diffs: diffs[(x,y)].append(float(scores[x])-float(scores[y]))
          si=CANDS.index(r['source_candidate']); ri=CANDS.index(cc); source_pool[si][ri]+=1
          source_match[r['source_candidate']][1]+=1; source_match[r['source_candidate']][0]+=int(cc==r['source_candidate'])
        unanim+=int(all(x==r['source_candidate'] for x in labels))
      pooled=[x for col in rep_labels for x in col]; cnt=Counter(pooled); n=len(pooled); exp=n/3
      pearson=sum((cnt[c]-exp)**2/exp for c in CANDS)
      pair={}
      for i in range(5):
        for j in range(i+1,5):
          agree=sum(x==y for x,y in zip(rep_labels[i],rep_labels[j]))/len(rows)
          pair[f'{i+1}-{j+1}']={'agreement':agree,'excess_agreement':agree-1/3,'cramers_v':cramers_v(rep_labels[i],rep_labels[j])}
      report['panels'][panel]={
        'source_n':4000,'replica_label_counts':{c:cnt[c] for c in CANDS},'replica_label_proportions':{c:cnt[c]/n for c in CANDS},'pearson_uniform_df2':pearson,
        'pairwise_replica':pair,'five_way_external_unanimity_count':unanim,'five_way_external_unanimity_rate':unanim/4000,'analytic_reference_1_over_243':1/243,
        'source_x_replica_table':source_pool,'source_stratified_match_rate':{c:(source_match[c][0]/source_match[c][1] if source_match[c][1] else None) for c in CANDS},
        'replica_topology_tie_rate':tie_n/(4000*5),'score_summaries':{c:stats(scorevals[c]) for c in CANDS},
        'score_difference_summaries':{f'{x}-{y}':{'mean':stats(v)['mean'],'sd':stats(v)['sd']} for (x,y),v in diffs.items()}}
      report['source_rows']+=4000; merged+=rows
    if report['source_rows']!=24000: raise AssertionError('total_n')
    (out/'integrity_report.json').write_text(json.dumps({'integrity_pass':True,'coordinates':24,'source_rows':24000,'five_replicas_per_source':True,'rq_seeds_touched':False,'experiment_066_validation_touched':False,'schema_repair_issue':284},indent=2))
    (out/'diagnostic_report.json').write_text(json.dumps(report,indent=2))
    with (out/'merged_rows.jsonl').open('w') as f:
      for r in merged: f.write(json.dumps(r,separators=(',',':'))+'\n')
    print('Experiment 067 ZQ reconstruction/integrity complete: 24 shards, 24000 source rows; diagnostic values intentionally not printed')
if __name__=='__main__': main()
