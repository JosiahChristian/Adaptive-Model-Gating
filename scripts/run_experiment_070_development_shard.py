#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
import experiment_070 as e70
from run_experiment_066_development_shard import _primary_one
EXECUTION_ISSUE=303

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cell-index',type=int,required=True);ap.add_argument('--chunk',type=int,required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
 if not e70.provenance_integrity():raise AssertionError('provenance_integrity')
 if not 0<=a.cell_index<len(e70.CELLS) or not 0<=a.chunk<80:raise ValueError('coordinate')
 start=e70.DEVELOPMENT_RANGE[0]+50*a.chunk;stop=start+50;c=e70.CELLS[a.cell_index]
 rows=[]
 for old in (_primary_one(s,c) for s in range(start,stop)):
  r=dict(old);r['experiment']=70;r['panel']='D070';r['c1_accept']=r.pop('m1_accept');r['c1_correct']=r.pop('m1_correct');r['c1_wrong_accept']=r.pop('m1_wrong_accept');r['c1_operational_loss_401_600']=r.pop('m1_operational_loss_401_600');r['c1_evidence_event']='five_replica_unanimity';r.pop('m1_e_value',None);rows.append(r)
 if len(rows)!=50 or [r['seed'] for r in rows]!=list(range(start,stop)):raise AssertionError('coverage')
 if any(r['cell']!=c['label'] or r['replica_discovery_used'] is not False for r in rows):raise AssertionError('identity')
 out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
 with (out/'rows.jsonl').open('w') as f:
  for r in rows:f.write(json.dumps(r,separators=(',',':'))+'\n')
 meta={'experiment':70,'role':'development_primary_shard','cell_index':a.cell_index,'cell':c['label'],'chunk':a.chunk,'start':start,'stop':stop,'n':50,'paired_c1_a0':True,'operative_spec_issue':301,'provenance_closure_issue':302,'execution_closure_issue':EXECUTION_ISSUE,'validation_touched':False,'no_tuning':True}
 (out/'meta.json').write_text(json.dumps(meta,indent=2,sort_keys=True)+'\n')
 print('Experiment 070 development coordinate preserved; scientific outcomes not summarized')
if __name__=='__main__':main()
