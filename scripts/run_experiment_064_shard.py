#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import experiment_064 as exp64


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--panel',choices=tuple(exp64.SEED_RANGES),required=True)
    ap.add_argument('--out',required=True)
    args=ap.parse_args()
    panel=args.panel
    start,stop=exp64.SEED_RANGES[panel]
    expected=list(range(start,stop))
    if len(expected)!=3000 or len(set(expected))!=3000:
        raise AssertionError(('frozen_seed_range',panel,start,stop))
    if not exp64.provenance_integrity():
        raise AssertionError('operator_provenance_integrity')
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    rows_path=out/'rows.jsonl'
    n=0
    with rows_path.open('w',encoding='utf-8') as f:
        for seed in expected:
            rows=exp64.evaluate_draw(panel,seed,start)
            if tuple(rows)!=exp64.ARCHITECTURES:
                raise AssertionError(('architecture_order',panel,seed,tuple(rows)))
            common=None
            for architecture in exp64.ARCHITECTURES:
                r=rows[architecture]
                if r['panel']!=panel or int(r['seed'])!=seed or r['architecture']!=architecture:
                    raise AssertionError(('row_identity',panel,seed,architecture))
                cur=(r['discovery_candidate'],r['confirmation_candidate'],int(r['agreement']))
                if common is None: common=cur
                elif cur!=common: raise AssertionError(('paired_cube_mismatch',panel,seed))
                if int(r['agreement'])!=int(r['discovery_candidate']==r['confirmation_candidate']):
                    raise AssertionError(('agreement_reconstruction',panel,seed,architecture))
                if int(r['final_accept'])!=int(bool(r['underlying_accept']) and bool(r['agreement'])):
                    raise AssertionError(('veto_reconstruction',panel,seed,architecture))
                f.write(json.dumps(r,sort_keys=True,separators=(',',':'))+'\n')
                n+=1
    manifest={
        'experiment':64,'operative_spec_issue':exp64.OPERATIVE_SPEC_ISSUE,
        'provenance_closure_issue':exp64.PROVENANCE_CLOSURE_ISSUE,
        'implementation_closure_issue':exp64.IMPLEMENTATION_CLOSURE_ISSUE,
        'panel':panel,'seed_start':start,'seed_stop_exclusive':stop,
        'seed_count':len(expected),'architectures':list(exp64.ARCHITECTURES),
        'row_count':n,'shared_paired_vectors':True,'null_panel':True,
        'provenance_integrity':True,
    }
    if n!=3000*len(exp64.ARCHITECTURES):
        raise AssertionError(('row_count',panel,n))
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')

if __name__=='__main__':
    main()
