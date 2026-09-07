#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math
from pathlib import Path
from scipy.stats import beta

CANDS=('H_ab','H_ac','H_bc')
PANELS={f'CQ{i}':(6800000+(i-1)*8000,6800000+i*8000) for i in range(1,7)}
STRIDE=10_000_000
ALPHA_FAMILY=0.05/6.0
TARGET=0.01

def cand_from_scores(scores):
    return max(CANDS,key=lambda c:(float(scores[c]),-CANDS.index(c)))

def tied(scores):
    vals=[float(scores[c]) for c in CANDS]; m=max(vals)
    return int(sum(int(v==m) for v in vals)>1)

def cp_upper(x,n):
    return 1.0 if x>=n else float(beta.ppf(1-ALPHA_FAMILY,x+1,n-x))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--input',required=True); ap.add_argument('--out',required=True); a=ap.parse_args()
    root=Path(a.input); out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    metas=list(root.rglob('meta.json')); seen={}; rows_by={}
    for mp in metas:
        m=json.loads(mp.read_text())
        if m.get('experiment')!=68 or m.get('role')!='calibration_shard': continue
        key=(m['panel'],int(m['shard_index']))
        if key in seen: raise AssertionError(f'duplicate_coordinate:{key}')
        if key[0] not in PANELS or key[1] not in range(16): raise AssertionError('coordinate')
        if m.get('operative_spec_issue')!=287 or m.get('provenance_closure_issue')!=288 or m.get('execution_closure_issue')!=289: raise AssertionError('provenance')
        start0=PANELS[key[0]][0]+500*key[1]; stop0=start0+500
        if int(m.get('start'))!=start0 or int(m.get('stop'))!=stop0 or int(m.get('n'))!=500: raise AssertionError('meta_range')
        if int(m.get('replica_count'))!=5 or int(m.get('replica_seed_stride'))!=STRIDE or m.get('no_tuning') is not True or m.get('reserved_confirmation_touched') is not False: raise AssertionError('meta_contract')
        rp=mp.parent/'rows.jsonl'; rows=[json.loads(x) for x in rp.read_text().splitlines() if x.strip()]
        if len(rows)!=500: raise AssertionError('shard_n')
        seen[key]=m; rows_by[key]=rows
    expected={(p,k) for p in PANELS for k in range(16)}
    if set(seen)!=expected: raise AssertionError(f'coordinate_set missing={sorted(expected-set(seen))} extra={sorted(set(seen)-expected)}')
    merged=[]; report={'experiment':68,'alpha_family':ALPHA_FAMILY,'target':TARGET,'panels':{},'C_068_pass':None,'xq_touched':False,'experiment_067_rq_touched':False,'experiment_066_validation_touched':False}
    for panel,(pstart,pstop) in PANELS.items():
        rows=[]
        for k in range(16): rows+=rows_by[(panel,k)]
        seeds=[int(r['seed']) for r in rows]
        if seeds!=list(range(pstart,pstop)): raise AssertionError(f'seed_coverage:{panel}')
        x=0
        for r in rows:
            seed=int(r['seed'])
            if r.get('panel')!=panel or r.get('source_candidate') not in CANDS: raise AssertionError('row_identity')
            expected_source=CANDS[(seed-pstart)%3]
            if r['source_candidate']!=expected_source: raise AssertionError('source_cycle')
            reps=r.get('replicas',[])
            if len(reps)!=5: raise AssertionError('replica_count')
            labels=[]
            for j,rep in enumerate(reps,1):
                if int(rep.get('replica_index'))!=j or int(rep.get('replica_seed'))!=seed+STRIDE*j or rep.get('discovery_used') is not False: raise AssertionError('replica_identity')
                scores=rep.get('confirmation_scores',{})
                if set(scores)!=set(CANDS): raise AssertionError('score_keys')
                cc=cand_from_scores(scores)
                if rep.get('confirmation_candidate')!=cc or int(rep.get('topology_tie_flag'))!=tied(scores): raise AssertionError('topology_reconstruction')
                labels.append(cc)
            wrong=int(all(c==r['source_candidate'] for c in labels))
            if int(r.get('unanimous_match_count'))!=sum(c==r['source_candidate'] for c in labels) or int(r.get('wrong_accept'))!=wrong: raise AssertionError('wrong_accept_reconstruction')
            if r.get('no_tuning') is not True or r.get('calibration_only') is not True: raise AssertionError('row_contract')
            x+=wrong
        u=cp_upper(x,8000)
        report['panels'][panel]={'n':8000,'wrong_accept_count':x,'wrong_accept_rate':x/8000.0,'clopper_pearson_upper':u,'pass':bool(u<=TARGET)}
        merged+=rows
    if len(merged)!=48000: raise AssertionError('total_n')
    report['C_068_pass']=all(v['pass'] for v in report['panels'].values())
    integrity={'integrity_pass':True,'coordinates':96,'source_rows':48000,'source_rows_per_panel':8000,'five_replicas_per_source':True,'candidate_order':list(CANDS),'replica_seed_stride':STRIDE,'operative_spec_issue':287,'provenance_closure_issue':288,'execution_closure_issue':289,'evidence_closure_issue':290,'xq_touched':False,'experiment_067_rq_touched':False,'experiment_066_validation_touched':False}
    (out/'integrity_report.json').write_text(json.dumps(integrity,indent=2,sort_keys=True)+'\n')
    (out/'calibration_report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    with (out/'merged_rows.jsonl').open('w') as f:
        for r in merged: f.write(json.dumps(r,separators=(',',':'))+'\n')
    print('Experiment 068 CQ reconstruction/integrity complete: 96 shards, 48000 source rows; calibration values intentionally not printed')

if __name__=='__main__': main()
