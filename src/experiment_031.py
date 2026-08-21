from __future__ import annotations

from experiment_010 import rolling_pairwise_health
from experiment_013 import health

WINDOW=range(401,421)
CONTEXT_THRESHOLD=0.50


def context_path(stream,k3,la,lb,lc,lab,lac,lbc):
    h=health(stream);ph=rolling_pairwise_health(stream);rows=[]
    for t in WINDOW:
        mismatch={x:int(h[x][t] is not None and h[x][t]>thr) for x,thr in (('a',la),('b',lb),('c',lc))}
        disagree={x:int(h[x][t] is not None and h[x][t]>thr) for x,thr in (('ab',lab),('ac',lac),('bc',lbc))}
        triad_consistent=int(all(ph[k][t] is not None and ph[k][t]<=k3 for k in ph))
        broad=int(sum(mismatch.values())>=2)
        consensus=int(sum(disagree.values())==0)
        vote=int(triad_consistent and broad and consensus)
        rows.append({'t':t,'triad_consistent':triad_consistent,'broad_anchor_mismatch':broad,'anchor_consensus':consensus,'common_mode_context_vote':vote,
                     'm_a':mismatch['a'],'m_b':mismatch['b'],'m_c':mismatch['c'],'d_ab':disagree['ab'],'d_ac':disagree['ac'],'d_bc':disagree['bc']})
    return rows


def context_summary(stream,k3,la,lb,lc,lab,lac,lbc):
    rows=context_path(stream,k3,la,lb,lc,lab,lac,lbc)
    n=len(rows)
    if n!=20:raise AssertionError(n)
    score=sum(r['common_mode_context_vote'] for r in rows)/n
    call=int(score>=CONTEXT_THRESHOLD)
    return {'context_score':score,'common_mode_context':call,
            'broad_anchor_mismatch_fraction':sum(r['broad_anchor_mismatch'] for r in rows)/n,
            'anchor_consensus_fraction':sum(r['anchor_consensus'] for r in rows)/n,
            'triad_consistency_fraction':sum(r['triad_consistent'] for r in rows)/n,
            'window_n':n},rows
