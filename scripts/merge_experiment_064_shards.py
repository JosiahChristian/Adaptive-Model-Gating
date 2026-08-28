#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import experiment_064 as exp64

Z=1.6448536269514722


def wilson_upper(k,n):
    if n<=0:return 1.0
    p=k/n;den=1.0+Z*Z/n
    center=(p+Z*Z/(2*n))/den
    rad=Z*math.sqrt(p*(1-p)/n+Z*Z/(4*n*n))/den
    return min(1.0,center+rad)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input-root',required=True);ap.add_argument('--out',required=True)
    a=ap.parse_args();root=Path(a.input_root);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    if not exp64.provenance_integrity():raise AssertionError('operator_provenance_integrity')
    all_metrics={};integrity=True;manifests={};panel_dir=out/'panels';panel_dir.mkdir(exist_ok=True)
    for panel,(start,stop) in exp64.SEED_RANGES.items():
        src=root/panel
        manifest=json.loads((src/'manifest.json').read_text())
        manifests[panel]=manifest
        expected_manifest={'panel':panel,'seed_start':start,'seed_stop_exclusive':stop,'seed_count':3000,'row_count':12000}
        for k,v in expected_manifest.items():
            if manifest.get(k)!=v:integrity=False
        if manifest.get('architectures')!=list(exp64.ARCHITECTURES) or not manifest.get('shared_paired_vectors') or not manifest.get('provenance_integrity'):
            integrity=False
        rows=[json.loads(x) for x in (src/'rows.jsonl').read_text().splitlines() if x.strip()]
        by={(int(r['seed']),r['architecture']):r for r in rows}
        expected={(s,arch) for s in range(start,stop) for arch in exp64.ARCHITECTURES}
        if len(rows)!=len(expected) or set(by)!=expected:integrity=False
        for seed in range(start,stop):
            common=None
            for arch in exp64.ARCHITECTURES:
                r=by[(seed,arch)]
                if r.get('panel')!=panel:integrity=False
                cur=(r.get('discovery_candidate'),r.get('confirmation_candidate'),int(r.get('agreement',-1)))
                if common is None:common=cur
                elif cur!=common:integrity=False
                if int(r.get('agreement',-1))!=int(r.get('discovery_candidate')==r.get('confirmation_candidate')):integrity=False
                if int(r.get('final_accept',-1))!=int(bool(r.get('underlying_accept')) and bool(r.get('agreement'))):integrity=False
        for arch in exp64.ARCHITECTURES:
            q=[by[(s,arch)] for s in range(start,stop)]
            accepted=sum(int(r['final_accept']) for r in q)
            underlying=sum(int(r['underlying_accept']) for r in q)
            wrong=accepted
            precision=((accepted-wrong)/accepted) if accepted else None
            vetoed=underlying-accepted
            upper=wilson_upper(wrong,len(q))
            panel_pass=(upper<=0.01 and (accepted==0 or (precision is not None and precision>=0.99)))
            all_metrics.setdefault(arch,{})[panel]={
                'seed_range':[start,stop-1],'n':len(q),'accepted_n':accepted,'acceptance_rate':accepted/len(q),
                'wrong_n':wrong,'wrong_acceptance_rate':wrong/len(q),'precision':precision,
                'wrong_wilson_upper_95':upper,
                'topology_veto_rate_given_underlying_accept':vetoed/underlying if underlying else 0.0,
                'acceptance_delta_vs_no_veto':(accepted-underlying)/len(q),
                'underlying_accept_n':underlying,'F_064_panel_pass':panel_pass,
            }
        shutil.copy2(src/'rows.jsonl',panel_dir/f'{panel}-rows.jsonl')
        shutil.copy2(src/'manifest.json',panel_dir/f'{panel}-manifest.json')
    eligible=[]
    if integrity:
        for arch in exp64.ARCHITECTURES:
            if all(all_metrics[arch][p]['F_064_panel_pass'] for p in exp64.SEED_RANGES):eligible.append(arch)
    branch='D' if not integrity else ('A' if len(eligible)==0 else ('B' if len(eligible)==1 else 'C'))
    report={
        'experiment':64,'operative_spec_issue':exp64.OPERATIVE_SPEC_ISSUE,
        'provenance_closure_issue':exp64.PROVENANCE_CLOSURE_ISSUE,
        'implementation_closure_issue':exp64.IMPLEMENTATION_CLOSURE_ISSUE,
        'architectures':list(exp64.ARCHITECTURES),'panels':list(exp64.SEED_RANGES),
        'seed_ranges':{p:[a,b-1] for p,(a,b) in exp64.SEED_RANGES.items()},
        'n_per_panel':3000,'shared_paired_vectors_across_architectures':True,
        'null_panel_rule':'every final acceptance is a wrong acceptance',
        'wilson_upper_rule':'one-sided 95% Wilson upper bound, z=1.6448536269514722',
        'F_064_rule':'eligible iff every Q1-Q6 wrong-acceptance Wilson upper <=0.01 and, whenever accepted_n>0, empirical precision >=0.99',
        'F_064_eligible_architectures':eligible,'F_064_pass_count':len(eligible),
        'integrity_pass':integrity,'interpretation_branch':branch,
        'decision_branches':{'A':'no architecture eligible; no tuning; separately preregister a new structural robustness mechanism','B':'exactly one eligible; replication hypothesis only','C':'multiple eligible; carry all to separate replication or prospectively define non-outcome selection','D':'integrity/provenance failure; no scientific interpretation'},
        'metrics':all_metrics,'manifests':manifests,
        'no_tuning':True,'no_outcome_adaptive_rule':True,'no_candidate_reselection':True,
    }
    (out/'report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    if not integrity:raise AssertionError('experiment_064_integrity_failed')

if __name__=='__main__':main()
