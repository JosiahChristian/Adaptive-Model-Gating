#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math,sys
from pathlib import Path
from scipy.stats import beta
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import experiment_061 as e61
import experiment_066 as e66
import experiment_069 as e69
from experiment_051 import CELLS

CANDS=tuple(e69.CANDIDATE_ORDER)
STRIDE=e69.REPLICA_SEED_STRIDE
ALPHA_FAMILY=e69.ALPHA_FAMILY
ERROR_TARGET=e69.ERROR_TARGET
PRECISION_TARGET=e69.PRECISION_TARGET
COVERAGE_TARGET=e69.COVERAGE_TARGET
Z=1.6448536269514722
EVIDENCE_ISSUE=299


def topology_candidate(scores):
    if set(scores)!=set(CANDS): raise AssertionError('topology_score_keys')
    return max(CANDS,key=lambda h:(float(scores[h]),-CANDS.index(h)))

def tie_flag(scores):
    vals=[float(scores[h]) for h in CANDS]; m=max(vals)
    return int(sum(int(v==m) for v in vals)>1)

def cp_upper(x,n):
    return 1.0 if x>=n else float(beta.ppf(1-ALPHA_FAMILY,x+1,n-x))

def wilson_upper(k,n):
    if n<=0:return 1.0
    p=k/n; den=1+Z*Z/n
    center=(p+Z*Z/(2*n))/den
    rad=Z*math.sqrt(p*(1-p)/n+Z*Z/(4*n*n))/den
    return min(1.0,center+rad)

def load_rows(p):
    return [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]

def check_replica(rep,seed,j):
    if int(rep['replica_index'])!=j or int(rep['replica_seed'])!=seed+STRIDE*j: raise AssertionError('replica_identity')
    if rep.get('discovery_used') not in (False,0): raise AssertionError('replica_discovery_leakage')
    scores=rep['confirmation_scores']; cc=topology_candidate(scores)
    if rep['confirmation_candidate']!=cc or int(rep['topology_tie_flag'])!=tie_flag(scores): raise AssertionError('replica_topology')
    return cc

def check_primary_row(r,cell):
    seed=int(r['seed']); reps=r['replicas']
    if len(reps)!=5: raise AssertionError('replica_count')
    labels=[check_replica(rep,seed,j) for j,rep in enumerate(reps,1)]
    d=e66.m1_from_candidates(r['discovery_candidate'],labels)
    if int(r['unanimous_match_count'])!=int(d['unanimous_match_count']) or int(r['c1_accept'])!=int(d['m1_accept']): raise AssertionError('c1_reconstruction')
    if r['topology_truth']!=cell['topology_truth'] or r['cell']!=cell['label'] or r.get('panel')!='P069': raise AssertionError('primary_identity')
    correct=int(r['discovery_candidate']==cell['topology_truth'])
    if int(r['candidate_correct'])!=correct: raise AssertionError('candidate_correct')
    c1=int(r['c1_accept'])
    if int(r['c1_correct'])!=int(c1 and correct) or int(r['c1_wrong_accept'])!=int(c1 and not correct): raise AssertionError('c1_correctness')
    contrasts=tuple(float(x) for x in r['a0_pairwise_confirmation'])
    wplus,ranks=e61.base.signed_rank_statistic_30(contrasts)
    if wplus!=int(r['a0_wplus']) or tuple(int(x) for x in ranks)!=tuple(int(x) for x in r['a0_ranks']): raise AssertionError('a0_rank')
    if int(r['a0_w_cutoff'])!=345: raise AssertionError('a0_cutoff')
    conf=topology_candidate(r['a0_confirmation_scores'])
    if conf!=r['a0_confirmation_candidate'] or tie_flag(r['a0_confirmation_scores'])!=int(r['a0_topology_tie_flag']): raise AssertionError('a0_topology')
    agree=int(conf==r['discovery_candidate']); a0=int(wplus>=345 and agree)
    if agree!=int(r['a0_topology_agreement']) or a0!=int(r['a0_accept']): raise AssertionError('a0_accept')
    if int(r['a0_correct'])!=int(a0 and correct) or int(r['a0_wrong_accept'])!=int(a0 and not correct): raise AssertionError('a0_correctness')
    fallback=float(r['fallback_operational_loss_401_600']); deploy=float(r['deploy_candidate_operational_loss_401_600'])
    if abs(float(r['c1_operational_loss_401_600'])-(deploy if c1 else fallback))>1e-12: raise AssertionError('c1_loss')
    if abs(float(r['a0_operational_loss_401_600'])-(deploy if a0 else fallback))>1e-12: raise AssertionError('a0_loss')
    if r.get('replica_discovery_used') not in (False,0): raise AssertionError('row_discovery_leakage')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--input',required=True); ap.add_argument('--out',required=True); a=ap.parse_args()
    root=Path(a.input); out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    if not e69.provenance_integrity(): raise AssertionError('provenance_integrity')
    xq_seen={}; primary_seen={}
    for mp in root.rglob('meta.json'):
        m=json.loads(mp.read_text()); rp=mp.parent/'rows.jsonl'
        if not rp.exists(): raise AssertionError(f'missing_rows:{mp}')
        rows=load_rows(rp)
        if m.get('experiment')!=69: continue
        if m.get('operative_spec_issue')!=292 or m.get('provenance_closure_issue')!=293 or m.get('execution_closure_issue')!=294 or m.get('no_tuning') is not True: raise AssertionError('meta_provenance')
        if m.get('experiment_067_rq_touched') is not False or m.get('experiment_066_validation_touched') is not False: raise AssertionError('reserved_touched')
        role=m.get('role')
        if role=='xq_shard':
            key=(m['panel'],int(m['shard']))
            if key in xq_seen: raise AssertionError(f'duplicate_xq:{key}')
            p0,p1=e69.XQ_RANGES[key[0]]; start=p0+500*key[1]; stop=start+500
            if int(m['start'])!=start or int(m['stop'])!=stop or int(m['n'])!=500 or len(rows)!=500: raise AssertionError('xq_meta')
            xq_seen[key]=rows
        elif role=='paired_primary_shard':
            key=(int(m['cell_index']),int(m['chunk']))
            if key in primary_seen: raise AssertionError(f'duplicate_primary:{key}')
            start=e69.PRIMARY_RANGE[0]+50*key[1]; stop=start+50
            if not 0<=key[0]<16 or not 0<=key[1]<80 or int(m['start'])!=start or int(m['stop'])!=stop or int(m['n'])!=50 or len(rows)!=50 or m.get('paired_c1_a0') is not True: raise AssertionError('primary_meta')
            primary_seen[key]=rows
    expected_xq={(f'XQ{i}',k) for i in range(1,7) for k in range(16)}
    expected_primary={(c,k) for c in range(16) for k in range(80)}
    if set(xq_seen)!=expected_xq: raise AssertionError(f'xq_coordinate_set missing={sorted(expected_xq-set(xq_seen))} extra={sorted(set(xq_seen)-expected_xq)}')
    if set(primary_seen)!=expected_primary: raise AssertionError(f'primary_coordinate_set missing={sorted(expected_primary-set(primary_seen))[:20]} extra={sorted(set(primary_seen)-expected_primary)[:20]}')

    xq_report={}; all_xq=[]
    for panel,(pstart,pstop) in e69.XQ_RANGES.items():
        rows=[]
        for k in range(16): rows+=xq_seen[(panel,k)]
        if [int(r['seed']) for r in rows]!=list(range(pstart,pstop)): raise AssertionError(f'xq_seed_coverage:{panel}')
        wrong=0
        for r in rows:
            seed=int(r['seed'])
            if r.get('panel')!=panel or r.get('source_candidate') not in CANDS: raise AssertionError('xq_row_identity')
            expected_source=CANDS[(seed-pstart)%3]
            if r['source_candidate']!=expected_source: raise AssertionError('xq_source_cycle')
            reps=r.get('replicas',[])
            if len(reps)!=5: raise AssertionError('xq_replica_count')
            labels=[check_replica(rep,seed,j) for j,rep in enumerate(reps,1)]
            w=int(all(c==r['source_candidate'] for c in labels))
            if int(r['unanimous_match_count'])!=sum(c==r['source_candidate'] for c in labels) or int(r['wrong_accept'])!=w: raise AssertionError('xq_wrong_accept_reconstruction')
            wrong+=w
        u=cp_upper(wrong,8000)
        xq_report[panel]={'n':8000,'wrong_accept_count':wrong,'wrong_accept_rate':wrong/8000.0,'clopper_pearson_upper':u,'pass':bool(u<=ERROR_TARGET)}
        all_xq+=rows

    cells_report={}; all_primary=[]
    for c,cell in enumerate(CELLS):
        rows=[]
        for k in range(80): rows+=primary_seen[(c,k)]
        if [int(r['seed']) for r in rows]!=list(range(*e69.PRIMARY_RANGE)) or len({int(r['seed']) for r in rows})!=4000: raise AssertionError(f'primary_seed_coverage:{c}')
        for r in rows: check_primary_row(r,cell)
        accepted=sum(int(r['c1_accept']) for r in rows); correct=sum(int(r['c1_correct']) for r in rows); wrong=sum(int(r['c1_wrong_accept']) for r in rows)
        precision=correct/accepted if accepted else None; upper=wilson_upper(wrong,len(rows))
        precision_pass=bool(accepted==0 or precision>=PRECISION_TARGET); wrong_pass=bool(upper<=ERROR_TARGET)
        cells_report[cell['label']]={'n':4000,'accepted_n':accepted,'correct_n':correct,'wrong_n':wrong,'precision':precision,'precision_pass':precision_pass,'wrong_acceptance':wrong/4000.0,'wrong_wilson_upper_95':upper,'wrong_pass':wrong_pass,'cell_pass':bool(precision_pass and wrong_pass),'a0_accepted_n':sum(int(r['a0_accept']) for r in rows)}
        all_primary+=rows
    if len(all_xq)!=48000 or len(all_primary)!=64000: raise AssertionError('row_totals')
    c1_accept=sum(int(r['c1_accept']) for r in all_primary); a0_accept=sum(int(r['a0_accept']) for r in all_primary)
    ratio=c1_accept/a0_accept if a0_accept else None; coverage_pass=bool(a0_accept>0 and ratio>=COVERAGE_TARGET)
    xq_pass=all(v['pass'] for v in xq_report.values()); cells_pass=all(v['cell_pass'] for v in cells_report.values())
    gate=bool(xq_pass and cells_pass and coverage_pass)
    integrity={'integrity_pass':True,'xq_coordinates':96,'primary_coordinates':1280,'xq_source_rows':48000,'primary_source_rows':64000,'five_replicas_per_source':True,'candidate_order':list(CANDS),'replica_seed_stride':STRIDE,'operative_spec_issue':292,'provenance_closure_issue':293,'execution_closure_issue':294,'evidence_closure_issue':EVIDENCE_ISSUE,'experiment_067_rq_touched':False,'experiment_066_validation_touched':False,'no_tuning':True}
    report={'experiment':69,'xq':{'alpha_family':ALPHA_FAMILY,'target':ERROR_TARGET,'panels':xq_report,'pass':xq_pass},'primary':{'precision_target':PRECISION_TARGET,'wrong_accept_target':ERROR_TARGET,'coverage_target':COVERAGE_TARGET,'C1_accept_count':c1_accept,'A0_accept_count':a0_accept,'coverage_ratio_C1_over_A0':ratio,'coverage_pass':coverage_pass,'cells':cells_report,'cells_pass':cells_pass},'G_069_pass':gate,'interpretation_branch':'PASS' if gate else 'FAIL','experiment_067_rq_touched':False,'experiment_066_validation_touched':False,'no_tuning':True}
    (out/'integrity_report.json').write_text(json.dumps(integrity,indent=2,sort_keys=True)+'\n')
    (out/'statistical_report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    with (out/'xq_rows.jsonl').open('w') as f:
        for r in all_xq:f.write(json.dumps(r,separators=(',',':'))+'\n')
    with (out/'primary_rows.jsonl').open('w') as f:
        for r in all_primary:f.write(json.dumps(r,separators=(',',':'))+'\n')
    print('Experiment 069 reconstruction/integrity complete: 96 XQ coordinates, 1280 primary coordinates, 112000 source rows; statistical values intentionally not printed')

if __name__=='__main__':main()
