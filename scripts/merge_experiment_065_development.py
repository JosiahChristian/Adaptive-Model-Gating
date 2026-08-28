#!/usr/bin/env python3
import argparse,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
import experiment_065 as e
from experiment_051 import CELLS
Z=1.6448536269514722

def wilson_upper(k,n):
    if n<=0:return 1.0
    p=k/n;den=1+Z*Z/n
    center=(p+Z*Z/(2*n))/den
    rad=Z*math.sqrt(p*(1-p)/n+Z*Z/(4*n*n))/den
    return min(1.0,center+rad)

def load_rows(p):
    return [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-root',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();root=Path(a.input_root);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    integrity=bool(e.provenance_integrity());dq={};raw_manifest=[]
    for panel,(start,stop) in e.DEVELOPMENT_ROBUSTNESS_RANGES.items():
        p=root/f'experiment-065-{panel}'/'rows.jsonl';rows=load_rows(p)
        expected=list(range(start,stop));seeds=[int(r['seed']) for r in rows]
        panel_integrity=(len(rows)==2000 and seeds==expected and len(set(seeds))==2000 and all(r.get('panel')==panel and r.get('q_family')==e.q_family(panel) for r in rows))
        integrity=integrity and panel_integrity
        accepted=sum(int(r['m0_accept']) for r in rows);wrong=accepted;upper=wilson_upper(wrong,len(rows));precision=(0.0 if accepted else None)
        panel_pass=bool(upper<=0.01 and (accepted==0 or precision>=0.99))
        dq[panel]={'seed_range':[start,stop-1],'n':len(rows),'accepted_n':accepted,'wrong_n':wrong,'wrong_acceptance':wrong/len(rows),'wrong_wilson_upper_95':upper,'precision':precision,'G_065_DQ_pass':panel_pass,'null_panel':True}
        raw_manifest.append(str(p))
    dp_rows=[]
    start,stop=e.DEVELOPMENT_PRIMARY_RANGE
    for i,c in enumerate(CELLS):
        p=root/f'experiment-065-DP-cell-{i}'/'rows.jsonl';rows=load_rows(p);seeds=[int(r['seed']) for r in rows]
        ok=(len(rows)==2000 and seeds==list(range(start,stop)) and len(set(seeds))==2000 and all(r.get('panel')=='DP' and r.get('cell')==c['label'] and int(r.get('shared_primary_stream',0))==1 for r in rows))
        integrity=integrity and ok;dp_rows.extend(rows);raw_manifest.append(str(p))
    expected_n=(stop-start)*len(CELLS);integrity=integrity and len(dp_rows)==expected_n
    m0=sum(int(r['m0_accept']) for r in dp_rows);a0=sum(int(r['a0_accept']) for r in dp_rows)
    subset_ok=all(not int(r['m0_accept']) or int(r['a0_accept']) for r in dp_rows);integrity=integrity and subset_ok
    ratio=(m0/a0 if a0 else None);coverage_pass=bool(a0>0 and ratio>=0.90)
    m0_loss=sum(float(r['m0_operational_loss_401_600']) for r in dp_rows)/len(dp_rows);a0_loss=sum(float(r['a0_operational_loss_401_600']) for r in dp_rows)/len(dp_rows)
    dq_pass=all(v['G_065_DQ_pass'] for v in dq.values())
    gate=bool(integrity and dq_pass and coverage_pass)
    report={'experiment':65,'phase':'development','operative_spec_issue':258,'provenance_closure_issue':259,'execution_closure_issue':261,'integrity_pass':bool(integrity),'development_robustness':dq,'DP':{'seed_range':[start,stop-1],'cell_count':len(CELLS),'paired_draws':len(dp_rows),'M0_accept_count':m0,'A0_accept_count':a0,'M0_coverage':m0/len(dp_rows),'A0_coverage':a0/len(dp_rows),'coverage_ratio_M0_over_A0':ratio,'coverage_ratio_gate_ge_0_90':coverage_pass,'subset_M0_of_A0':subset_ok,'mean_M0_operational_loss_401_600':m0_loss,'mean_A0_operational_loss_401_600':a0_loss,'mean_operational_loss_delta_M0_minus_A0':m0_loss-a0_loss,'operational_loss_role':'descriptive only; not a G-065 gate'},'G_065_pass':gate,'interpretation_branch':'PROCEED_TO_RESERVED_VALIDATION' if gate else 'STOP_NO_VALIDATION','validation_seeds_touched':False,'no_tuning':True,'raw_manifest':raw_manifest}
    (out/'development_report.json').write_text(json.dumps(report,indent=2))
    (out/'decision.txt').write_text(('PASS\n' if gate else 'FAIL\n'))
if __name__=='__main__':main()
