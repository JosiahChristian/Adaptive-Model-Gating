#!/usr/bin/env python3
import argparse,json,shutil
from pathlib import Path
N=50; K=40; C=16; H=25; START=6612000; STOP=6614000
SPEC=269; PROV=270; EXEC=272; INGEST=275; AMEND=277
RECOVERY_AUTH={(c,k):(273,33531109410) for c in range(6) for k in range(K)}
RECOVERY_AUTH[(14,1)]=(276,33997473495)

def rows(p): return [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]
def common(m):
 assert int(m.get('experiment',-1))==66
 assert int(m.get('operative_spec_issue',-1))==SPEC
 assert int(m.get('provenance_closure_issue',-1))==PROV
 assert int(m.get('execution_closure_issue',-1))==EXEC
 assert m.get('validation_seeds_touched') in (False,0)
 assert m.get('no_tuning') in (True,1)
def main():
 a=argparse.ArgumentParser(); a.add_argument('--root',required=True); a.add_argument('--out',required=True); x=a.parse_args()
 src=Path(x.root); out=Path(x.out); shutil.rmtree(out,ignore_errors=True); out.mkdir(parents=True)
 dq={}; can={}; rec={}
 for mp in sorted(src.glob('**/meta.json')):
  rp=mp.with_name('rows.jsonl'); assert rp.exists(),f'missing_rows:{mp}'
  m=json.loads(mp.read_text()); role=m.get('role')
  if role not in ('development_robustness','development_primary_shard','development_primary_recovery_subshard'): continue
  common(m)
  if role=='development_robustness':
   p=str(m.get('panel')); assert p not in dq; dq[p]=(mp,m,rp)
  elif role=='development_primary_shard':
   key=(int(m.get('cell_index',-1)),int(m.get('chunk_index',-1))); assert 0<=key[0]<C and 0<=key[1]<K and key not in can; can[key]=(mp,m,rp)
  else:
   c,k,h=int(m.get('cell_index',-1)),int(m.get('chunk_index',-1)),int(m.get('half_index',-1)); assert h in (0,1)
   auth=RECOVERY_AUTH.get((c,k)); assert auth is not None,f'unauthorized_recovery:{c}:{k}'
   assert int(m.get('execution_recovery_issue',-1))==auth[0] and int(m.get('source_canonical_run',-1))==auth[1]
   key=(c,k,h); assert key not in rec; rec[key]=(mp,m,rp)
 assert sorted(dq)==['DQ1','DQ2','DQ3','DQ4','DQ5','DQ6']
 for p,(mp,m,rp) in dq.items():
  rr=rows(rp); assert len(rr)==2000
  d=out/f'DQ-{p}'; d.mkdir(); shutil.copy2(mp,d/'meta.json'); shutil.copy2(rp,d/'rows.jsonl')
 manifest={'experiment':66,'ingestion_closure_issue':INGEST,'ingestion_amendment_issue':AMEND,'dq_count':6,'dp':[]}
 cellseeds={c:[] for c in range(C)}
 for c in range(C):
  for k in range(K):
   key=(c,k); halves=[(c,k,h) in rec for h in (0,1)]; assert not (key in can and any(halves)),f'overlap:{key}'
   start=START+N*k; stop=start+N
   if key in can:
    mp,m,rp=can[key]; rr=rows(rp); source='canonical'; paths=[str(mp.parent)]
   else:
    assert halves==[True,True],f'missing:{key}:{halves}'; rr=[]; paths=[]; source='recovery_halves'
    for h in (0,1):
     mp,m,rp=rec[(c,k,h)]; r=rows(rp); hs=start+h*H; he=hs+H
     assert m.get('seed_range')==[hs,he-1] and int(m.get('n',-1))==H
     assert [int(z['seed']) for z in r]==list(range(hs,he)); rr+=r; paths.append(str(mp.parent))
    rr.sort(key=lambda z:int(z['seed']))
   seeds=[int(z['seed']) for z in rr]; assert len(rr)==N and seeds==list(range(start,stop)) and len(set(seeds))==N
   cellseeds[c]+=seeds; d=out/f'DP-cell-{c}-chunk-{k}'; d.mkdir()
   nm={'experiment':66,'role':'development_primary_shard','cell_index':c,'chunk_index':k,'seed_range':[start,stop-1],'n':N,'paired_m1_a0':True,'replica_count':5,'operative_spec_issue':SPEC,'provenance_closure_issue':PROV,'execution_closure_issue':EXEC,'validation_seeds_touched':False,'no_tuning':True,'normalized_under_ingestion_issue':INGEST,'normalized_under_amendment_issue':AMEND,'source_role':source}
   (d/'meta.json').write_text(json.dumps(nm,indent=2)); (d/'rows.jsonl').write_text(''.join(json.dumps(z,separators=(',',':'))+'\n' for z in rr))
   manifest['dp'].append({'cell_index':c,'chunk_index':k,'source_role':source,'source_paths':paths})
 assert len(manifest['dp'])==640
 for c,s in cellseeds.items(): assert s==list(range(START,STOP)) and len(set(s))==2000
 manifest.update(dp_coordinate_count=640,dp_paired_source_draws=32000,scientific_values_inspected=False,validation_seeds_touched=False,no_tuning=True)
 (out/'ingestion_manifest.json').write_text(json.dumps(manifest,indent=2))
 print('normalized 6 DQ artifacts and 640 DP coordinates; provenance/coverage only; no scientific values summarized')
if __name__=='__main__': main()
