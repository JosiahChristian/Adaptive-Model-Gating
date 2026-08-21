from __future__ import annotations

from statistics import mean

from adaptive_model_gating import INITIAL_FIT_END,N_STEPS,PERSISTENCE_COUNT,ROLLING_WINDOW,initial_model,refit
from experiment_010 import classify_triad,rolling_pairwise_health
from experiment_013 import health
from experiment_016 import partition_matches
from experiment_022 import generate_stress_stream
from experiment_027 import inject_symmetric_round5
from experiment_029 import (
    POSTERIOR_RISK_STRATEGY,TRIAD,_annotation,infer_posterior_risk,
    run_experiment_029_strategy,
)

COMPOSED_STRATEGY='causal_context_composed_posterior_risk_gate'


def _context_vote(h,ph,t,k3,la,lb,lc,lab,lac,lbc):
    mismatch={x:int(h[x][t] is not None and h[x][t]>thr) for x,thr in (('a',la),('b',lb),('c',lc))}
    disagree={x:int(h[x][t] is not None and h[x][t]>thr) for x,thr in (('ab',lab),('ac',lac),('bc',lbc))}
    triad_consistent=int(all(ph[k][t] is not None and ph[k][t]<=k3 for k in ph))
    broad=int(sum(mismatch.values())>=2)
    consensus=int(sum(disagree.values())==0)
    vote=int(triad_consistent and broad and consensus)
    return vote,mismatch,disagree,triad_consistent,broad,consensus


def _run_composed_gate(seed,label,tau,k3,la,lb,lc,lab,lac,lbc,stream,ann,gate_groups):
    xp,ys=stream['x_primary'],stream['y'];model=initial_model(xp,ys);sq=[];streak=0;rows=[]
    h=health(stream);ph=rolling_pairwise_health(stream)
    for t in range(INITIAL_FIT_END+1,N_STEPS+1):
        sb,ib=model.slope,model.intercept;yh=model.predict(xp[t]);err=ys[t]-yh;se=err*err;sq.append(se)
        rm=mean(sq[-ROLLING_WINDOW:]) if len(sq)>=ROLLING_WINDOW else None
        vote,mismatch,disagree,consistent,broad,consensus=_context_vote(h,ph,t,k3,la,lb,lc,lab,lac,lbc)
        active={gate_groups[x] for x in 'abc' if mismatch[x]}
        cross=int(any(gate_groups[i]!=gate_groups[j] and mismatch[i] and mismatch[j] and not disagree[i+j] for i,j in (('a','b'),('a','c'),('b','c'))))
        pbad,_,_,_=classify_triad(ph['h_p_r1'][t],ph['h_p_r2'][t],ph['h_r1_r2'][t],k3)
        suspect=int(consistent and cross and len(active)>=2)
        if rm is not None:streak=streak+1 if rm>tau else 0
        ready=streak>=PERSISTENCE_COUNT
        original_veto=int(ready and (pbad or suspect))
        effective_suspect=int(suspect and not vote)
        veto=int(ready and (pbad or effective_suspect))
        context_removed=int(ready and suspect and vote and not pbad)
        adapt=int(ready and not veto)
        if ready:streak=0
        if adapt:model=refit(xp,ys,t)
        row={'seed':seed,'label':label,'t':t,'strategy':COMPOSED_STRATEGY,'y_hat':yh,'error':err,'sq_error':se,'rolling_mse':rm,'adapt':adapt,
             'slope_before':sb,'intercept_before':ib,'slope_after':model.slope,'intercept_after':model.intercept,
             'common_mode_suspect':suspect,'independent_veto':veto,'triad_primary_bad':int(pbad),'provenance_suspect_original':suspect,
             'provenance_suspect_effective':effective_suspect,'experiment029_original_veto':original_veto,'context_removed_suspect_veto':context_removed,
             'context_vote_t':vote,'context_triad_consistent':consistent,'context_broad_anchor_mismatch':broad,'context_anchor_consensus':consensus,
             'latent_input_sq_error':(ys[t]-(sb*stream['x_true'][t]+ib))**2,'raw_mismatch_votes':sum(mismatch.values()),'provenance_mismatch_votes':len(active)}
        for key in ('x_true','x_primary','x_r1','x_r2','z','z_b','z_c','probe_obs_a','probe_obs_b','probe_obs_c','probe_noise_a','probe_noise_b','probe_noise_c'):
            row[key]=stream[key][t]
        for k,v in mismatch.items():row[f'context_m_{k}']=v
        for k,v in disagree.items():row[f'context_d_{k}']=v
        row.update(ann);rows.append(row)
    return rows


def run_experiment_032_strategy(seed,c,strategy,vals):
    if strategy==POSTERIOR_RISK_STRATEGY:
        return run_experiment_029_strategy(seed,c,strategy,vals)
    if strategy==TRIAD:
        return run_experiment_029_strategy(seed,c,strategy,vals)
    if strategy!=COMPOSED_STRATEGY:raise ValueError(strategy)

    stream=inject_symmetric_round5(generate_stress_stream(seed,c))
    groups,accepted,abstain,stop,path=infer_posterior_risk(stream)
    ann=_annotation(stream,groups,accepted,abstain,stop,path)
    tau,kappa,k3,la,lb,lc,lab,lac,lbc,lambdas,mu,nu,mu5,nu5,mu5t,nu5t,mu4e,nu4e=vals
    if abstain:
        rows=run_experiment_029_strategy(seed,c,POSTERIOR_RISK_STRATEGY,vals)
        for r in rows:
            r['strategy']=COMPOSED_STRATEGY
            r['context_vote_t']=0
            r['context_removed_suspect_veto']=0
            r['triad_primary_bad']=int(r.get('primary_bad',0) or 0)
    else:
        rows=_run_composed_gate(seed,f'experiment032_{c["label"]}',tau,k3,la,lb,lc,lab,lac,lbc,stream,ann,groups)
    for r in rows:
        r['experiment032_cell']=c['label'];r['experiment032_kind']=c['kind'];r['experiment032_gain']=c.get('gain',stream.get('probe_gain',''));r['experiment032_noise_scale']=c.get('noise_scale',1.0)
        r['experiment032_topology_correct']=partition_matches(groups) if accepted else ''
    return rows
