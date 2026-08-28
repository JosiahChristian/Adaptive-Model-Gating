#!/usr/bin/env python3
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
import experiment_065 as e
import experiment_064 as e64
import experiment_061 as e61
from experiment_051 import CELLS
from run_experiment_055 import calibration_values,summary


def _primary_one(seed,c):
    stream=e61.generate_experiment_061_stream(seed,c)
    groups,a0_accept,a0_abstain,_,path,mats,y_disc,scores_disc,y_conf,scores_conf=e61.infer_confirmation_agreement_061(stream)
    candidate=path[0]['candidate'];conf=path[0]['confirmation_candidate']
    vectors={};cube={}
    for h in e64.CANDIDATE_ORDER:
        edge=e64.EDGE_PAIRS[h][0]; vals=[]
        for r in range(1,6):
            pairs=e61.base.pairwise_confirmation_055(stream,r,edge)
            cube[(r,e64.EDGE_PAIRS[h][0])]=tuple(pairs[0])
            cube[(r,e64.EDGE_PAIRS[h][1])]=tuple(pairs[1])
            vals.extend(pairs[0]);vals.extend(pairs[1])
        vectors[h]=tuple(vals)
    if any(len(v)!=30 for v in vectors.values()) or len(cube)!=30: raise AssertionError('primary_cube_shape')
    m=e.m0_from_cube(candidate,vectors,cube)
    if m['confirmation_candidate']!=conf: raise AssertionError('confirmation_reconstruction')
    a0_expected=int(m['underlying_accept']['A0'] and m['topology_agreement'])
    if int(a0_accept)!=a0_expected: raise AssertionError('a0_reconstruction')
    if m['m0_accept'] and not a0_accept: raise AssertionError('m0_not_subset_a0')
    vals=calibration_values();tau,_,k3,la,lb,lc,lab,lac,lbc,*_=vals
    ann=e61._annotation_061(stream,a0_accept,a0_abstain,path,mats,y_disc,scores_disc,y_conf,scores_conf)
    if a0_abstain:
        a0_rows=e61.base.run_triad_persistence_on_stream(seed,f'experiment065_a0_{c["label"]}',tau,k3,stream)
        for row in a0_rows: row['strategy']=e61.CONFIRMATION_AGREEMENT_STRATEGY;row.update(ann)
    else:
        a0_rows=e61.base._run_composed_gate(seed,f'experiment065_a0_{c["label"]}',tau,k3,la,lb,lc,lab,lac,lbc,stream,ann,groups)
        for row in a0_rows: row['strategy']=e61.CONFIRMATION_AGREEMENT_STRATEGY
    a0s=summary(a0_rows,c)
    if int(a0s['coverage'])!=int(a0_accept): raise AssertionError('a0_summary_coverage')
    if m['m0_accept']:
        m0_loss=float(a0s['operational_loss_401_600'])
    else:
        m0_rows=e61.base.run_triad_persistence_on_stream(seed,f'experiment065_m0_{c["label"]}',tau,k3,stream)
        for row in m0_rows:
            row['strategy']='experiment065_m0_consensus_veto'
            row['provenance_accepted']=0;row['provenance_abstain']=1;row['posterior_deploy_hypothesis']=''
        m0_loss=float(summary(m0_rows,c)['operational_loss_401_600'])
    return {'panel':'DP','seed':seed,'cell':c['label'],'m0_accept':int(m['m0_accept']),'a0_accept':int(a0_accept),'topology_agreement':int(m['topology_agreement']),'underlying_accept':m['underlying_accept'],'m0_operational_loss_401_600':m0_loss,'a0_operational_loss_401_600':float(a0s['operational_loss_401_600']),'shared_primary_stream':1,'no_tuning':1}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--panel');ap.add_argument('--cell-index',type=int);ap.add_argument('--chunk-index',type=int);ap.add_argument('--out',required=True);a=ap.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    rows=[]
    if a.panel:
        if a.panel not in e.DEVELOPMENT_ROBUSTNESS_RANGES: raise ValueError(a.panel)
        start,stop=e.DEVELOPMENT_ROBUSTNESS_RANGES[a.panel]
        rows=[e.evaluate_robustness_draw(a.panel,seed,start) for seed in range(start,stop)]
        if [r['seed'] for r in rows]!=list(range(start,stop)) or len(rows)!=2000: raise AssertionError('dq_coverage')
        meta={'experiment':65,'role':'development_robustness','panel':a.panel,'seed_range':[start,stop-1],'n':len(rows),'shared_paired_vectors':True,'null_panel':True,'no_tuning':True}
    else:
        if a.cell_index is None or not 0<=a.cell_index<len(CELLS): raise ValueError('cell-index')
        if a.chunk_index is None or not 0<=a.chunk_index<4: raise ValueError('chunk-index')
        c=CELLS[a.cell_index];full_start,full_stop=e.DEVELOPMENT_PRIMARY_RANGE
        chunk_n=(full_stop-full_start)//4
        start=full_start+a.chunk_index*chunk_n;stop=start+chunk_n
        rows=[_primary_one(seed,c) for seed in range(start,stop)]
        if [r['seed'] for r in rows]!=list(range(start,stop)) or len(rows)!=chunk_n: raise AssertionError('dp_chunk_coverage')
        meta={'experiment':65,'role':'development_primary_chunk','cell_index':a.cell_index,'chunk_index':a.chunk_index,'cell':c['label'],'seed_range':[start,stop-1],'n':len(rows),'paired_m0_a0':True,'execution_repair_issue':263,'no_tuning':True}
    with (out/'rows.jsonl').open('w',encoding='utf-8') as f:
        for r in rows:f.write(json.dumps(r,separators=(',',':'))+'\n')
    (out/'meta.json').write_text(json.dumps(meta,indent=2))
if __name__=='__main__':main()
