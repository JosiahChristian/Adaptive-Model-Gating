#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src')); sys.path.insert(0,str(ROOT/'scripts'))
import experiment_069 as e69
from experiment_051 import CELLS
from run_experiment_066_development_shard import _primary_one
EXECUTION_ISSUE=294

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--mode',choices=['xq','primary'],required=True); ap.add_argument('--panel'); ap.add_argument('--shard',type=int); ap.add_argument('--cell-index',type=int); ap.add_argument('--chunk',type=int); ap.add_argument('--out',required=True); a=ap.parse_args(); out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
 assert e69.provenance_integrity()
 if a.mode=='xq':
  if a.panel not in e69.XQ_RANGES or a.shard is None or not 0<=a.shard<16: raise ValueError('xq_args')
  p0,p1=e69.XQ_RANGES[a.panel]; start=p0+500*a.shard; stop=start+500
  rows=[e69.evaluate_xq_draw(a.panel,s) for s in range(start,stop)]
  assert len(rows)==500 and [r['seed'] for r in rows]==list(range(start,stop))
  meta={'experiment':69,'role':'xq_shard','panel':a.panel,'shard':a.shard,'start':start,'stop':stop,'n':500,'operative_spec_issue':292,'provenance_closure_issue':293,'execution_closure_issue':EXECUTION_ISSUE,'replica_count':5,'experiment_067_rq_touched':False,'experiment_066_validation_touched':False,'no_tuning':True}
 else:
  if a.cell_index is None or not 0<=a.cell_index<16 or a.chunk is None or not 0<=a.chunk<80: raise ValueError('primary_args')
  start=e69.PRIMARY_RANGE[0]+50*a.chunk; stop=start+50; c=CELLS[a.cell_index]
  old=[_primary_one(s,c) for s in range(start,stop)]; rows=[]
  for r in old:
   r=dict(r); r['panel']='P069'; r['c1_accept']=r.pop('m1_accept'); r['c1_correct']=r.pop('m1_correct'); r['c1_wrong_accept']=r.pop('m1_wrong_accept'); r['c1_operational_loss_401_600']=r.pop('m1_operational_loss_401_600'); r['c1_evidence_event']='five_replica_unanimity'; r.pop('m1_e_value',None); rows.append(r)
  assert len(rows)==50 and [r['seed'] for r in rows]==list(range(start,stop)) and all(r['cell']==c['label'] for r in rows)
  meta={'experiment':69,'role':'paired_primary_shard','cell_index':a.cell_index,'cell':c['label'],'chunk':a.chunk,'start':start,'stop':stop,'n':50,'paired_c1_a0':True,'operative_spec_issue':292,'provenance_closure_issue':293,'execution_closure_issue':EXECUTION_ISSUE,'replica_count':5,'experiment_067_rq_touched':False,'experiment_066_validation_touched':False,'no_tuning':True}
 with (out/'rows.jsonl').open('w') as f:
  for r in rows:f.write(json.dumps(r,separators=(',',':'))+'\n')
 (out/'meta.json').write_text(json.dumps(meta,indent=2,sort_keys=True)+'\n')
 print(f'Experiment 069 {a.mode} coordinate complete: {len(rows)} rows preserved; outcomes not summarized')
if __name__=='__main__':main()
