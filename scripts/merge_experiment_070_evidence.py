#!/usr/bin/env python3
"""Reconstruct frozen Experiment 070 development evidence before interpretation."""
from __future__ import annotations
import argparse,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import experiment_070 as e70
import experiment_066 as e66
import experiment_061 as e61

CANDS=tuple(e70.CANDIDATE_ORDER)
Z=1.6448536269514722
EVIDENCE_ISSUE=309

def candidate(scores):
    if set(scores)!=set(CANDS):raise AssertionError('candidate_keys')
    return max(CANDS,key=lambda h:(float(scores[h]),-CANDS.index(h)))

def tie(scores):
    vals=[float(scores[h]) for h in CANDS]
    return int(sum(v==max(vals) for v in vals)>1)

def wilson_upper(k,n):
    if n<=0:return 1.0
    p=k/n; den=1+Z*Z/n
    return min(1.0,(p+Z*Z/(2*n)+Z*math.sqrt(p*(1-p)/n+Z*Z/(4*n*n)))/den)

def check_row(r,c,seed):
    if int(r['seed'])!=seed or r.get('panel')!='D070' or r.get('experiment')!=70 or r['cell']!=c['label'] or r['topology_truth']!=c['topology_truth']:raise AssertionError('row_identity')
    if r.get('no_tuning') is not True or r.get('replica_discovery_used') is not False or r.get('source_discovery_stream_shared_with_a0') is not True:raise AssertionError('source_provenance')
    reps=r['replicas']
    if len(reps)!=5 or int(r['confirmation_replica_count'])!=5:raise AssertionError('replica_count')
    labels=[]
    for j,rep in enumerate(reps,1):
        if int(rep['replica_index'])!=j or int(rep['replica_seed'])!=seed+10_000_000*j or rep.get('discovery_used') is not False:raise AssertionError('replica_provenance')
        h=candidate(rep['confirmation_scores'])
        if h!=rep['confirmation_candidate'] or tie(rep['confirmation_scores'])!=int(rep['topology_tie_flag']):raise AssertionError('replica_candidate')
        labels.append(h)
    d=e66.m1_from_candidates(r['discovery_candidate'],labels)
    c1=int(d['m1_accept'])
    if int(r['unanimous_match_count'])!=int(d['unanimous_match_count']) or int(r['c1_accept'])!=c1:raise AssertionError('c1_reconstruction')
    correct=int(r['discovery_candidate']==c['topology_truth'])
    if int(r['candidate_correct'])!=correct or int(r['c1_correct'])!=int(c1 and correct) or int(r['c1_wrong_accept'])!=int(c1 and not correct):raise AssertionError('c1_correctness')
    contrasts=tuple(float(x) for x in r['a0_pairwise_confirmation'])
    wplus,ranks=e61.base.signed_rank_statistic_30(contrasts)
    if int(r['a0_wplus'])!=wplus or tuple(int(x) for x in r['a0_ranks'])!=tuple(int(x) for x in ranks) or int(r['a0_w_cutoff'])!=345:raise AssertionError('a0_rank')
    h=candidate(r['a0_confirmation_scores'])
    if h!=r['a0_confirmation_candidate'] or tie(r['a0_confirmation_scores'])!=int(r['a0_topology_tie_flag']):raise AssertionError('a0_candidate')
    agree=int(h==r['discovery_candidate']); a0=int(wplus>=345 and agree)
    if int(r['a0_topology_agreement'])!=agree or int(r['a0_accept'])!=a0 or int(r['a0_correct'])!=int(a0 and correct) or int(r['a0_wrong_accept'])!=int(a0 and not correct):raise AssertionError('a0_reconstruction')
    fallback=float(r['fallback_operational_loss_401_600']); deploy=float(r['deploy_candidate_operational_loss_401_600'])
    if abs(float(r['c1_operational_loss_401_600'])-(deploy if c1 else fallback))>1e-12 or abs(float(r['a0_operational_loss_401_600'])-(deploy if a0 else fallback))>1e-12:raise AssertionError('paired_loss')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
    if not e70.provenance_integrity() or len(e70.CELLS)!=12:raise AssertionError('frozen_provenance')
    root=Path(a.input);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    seen={}
    metas=list(root.rglob('meta.json'))
    for mp in metas:
        m=json.loads(mp.read_text()); rp=mp.parent/'rows.jsonl'
        if not rp.is_file():raise AssertionError('missing_rows')
        if m.get('experiment')!=70 or m.get('role')!='development_primary_shard' or m.get('operative_spec_issue')!=301 or m.get('provenance_closure_issue')!=302 or m.get('execution_closure_issue')!=303 or m.get('validation_touched') is not False or m.get('no_tuning') is not True or m.get('paired_c1_a0') is not True:raise AssertionError('meta_provenance')
        ci=int(m['cell_index']);chunk=int(m['chunk'])
        if not 0<=ci<12 or not 0<=chunk<80:raise AssertionError('coordinate_bounds')
        key=(ci,chunk)
        if key in seen:raise AssertionError('duplicate_coordinate')
        start=e70.DEVELOPMENT_RANGE[0]+50*chunk
        if m['cell']!=e70.CELLS[ci]['label'] or int(m['start'])!=start or int(m['stop'])!=start+50 or int(m['n'])!=50:raise AssertionError('meta_identity')
        rows=[json.loads(line) for line in rp.read_text().splitlines() if line.strip()]
        if len(rows)!=50 or [int(r['seed']) for r in rows]!=list(range(start,start+50)):raise AssertionError('seed_coverage')
        seen[key]=rows
    expected={(ci,k) for ci in range(12) for k in range(80)}
    if set(seen)!=expected or len(metas)!=960:raise AssertionError('coordinate_set')
    cell_reports={}; all_rows=[]
    for ci,c in enumerate(e70.CELLS):
        rows=[]
        for k in range(80):rows.extend(seen[(ci,k)])
        if len(rows)!=4000 or [int(r['seed']) for r in rows]!=list(range(*e70.DEVELOPMENT_RANGE)):raise AssertionError('cell_seed_coverage')
        for r in rows:check_row(r,c,int(r['seed']))
        accepted=sum(int(r['c1_accept']) for r in rows);correct=sum(int(r['c1_correct']) for r in rows);wrong=sum(int(r['c1_wrong_accept']) for r in rows)
        precision=correct/accepted if accepted else None;upper=wilson_upper(wrong,4000)
        precision_pass=bool(accepted>0 and precision>=e70.PRECISION_TARGET)
        wrong_pass=bool(upper<=e70.WRONG_ACCEPT_WILSON_TARGET)
        cell_reports[c['label']]={'n':4000,'accepted_n':accepted,'correct_n':correct,'wrong_n':wrong,'precision':precision,'precision_pass':precision_pass,'wrong_acceptance':wrong/4000,'wrong_wilson_upper_95':upper,'wrong_pass':wrong_pass,'cell_pass':bool(precision_pass and wrong_pass),'a0_accepted_n':sum(int(r['a0_accept']) for r in rows)}
        all_rows.extend(rows)
    if len(all_rows)!=48000:raise AssertionError('total_rows')
    c1=sum(int(r['c1_accept']) for r in all_rows);a0=sum(int(r['a0_accept']) for r in all_rows)
    ratio=c1/a0 if a0 else None;coverage_pass=bool(a0>0 and ratio>=e70.COVERAGE_TARGET)
    cells_pass=all(x['cell_pass'] for x in cell_reports.values());gate=bool(cells_pass and coverage_pass)
    integrity={'integrity_pass':True,'original_coordinates':960,'source_rows':48000,'cells':12,'chunks_per_cell':80,'rows_per_chunk':50,'five_replicas_per_source':True,'candidate_order':list(CANDS),'replica_seed_stride':e70.REPLICA_SEED_STRIDE,'operative_spec_issue':301,'provenance_closure_issue':302,'execution_closure_issue':303,'evidence_closure_issue':EVIDENCE_ISSUE,'validation_touched':False,'no_tuning':True}
    report={'experiment':70,'role':'development','precision_target':e70.PRECISION_TARGET,'wrong_accept_target':e70.WRONG_ACCEPT_WILSON_TARGET,'coverage_target':e70.COVERAGE_TARGET,'C1_accept_count':c1,'A0_accept_count':a0,'coverage_ratio_C1_over_A0':ratio,'coverage_pass':coverage_pass,'cells':cell_reports,'cells_pass':cells_pass,'G_070_development_pass':gate,'interpretation_branch':'VALIDATION_AUTHORIZED' if gate else 'STOP_NO_VALIDATION','validation_touched':False,'no_tuning':True}
    (out/'integrity_report.json').write_text(json.dumps(integrity,indent=2,sort_keys=True)+'\n')
    (out/'statistical_report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    with (out/'development_rows.jsonl').open('w') as h:
        for r in all_rows:h.write(json.dumps(r,separators=(',',':'))+'\n')
    print('Experiment 070 exact 960-coordinate / 48000-row reconstruction complete; statistical outcomes not printed')
if __name__=='__main__':main()
