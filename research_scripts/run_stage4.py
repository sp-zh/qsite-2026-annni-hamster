import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('OMP_NUM_THREADS','1')
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import numpy as np
from annni.stage4 import *

def audit_branches():
    selected=read(OLD/'slices/selection_frozen.json')['rows'];chains=read(OLD/'slices/optimization_rows.json');oldchecks=read(OLD/'slices/preparation_protocol_sensitivity.json')
    index={(branch_id(r),round(r['h']*80)):r for r in chains};intervals=[];results=[];cross=[]
    for k in [0.,.3,.8]:
        for L in [4,6]:
            rows=sorted([r for r in selected if r['kappa']==k and r['layers']==L],key=lambda r:r['h'])
            for i,(a,b) in enumerate(zip(rows,rows[1:])):
                A=branch_id(a);B=branch_id(b);base=dict(id=f'k{k}_L{L}_i{i}',kappa=k,layers=L,left_h=a['h'],right_h=b['h'],left_branch_id=A,right_branch_id=B)
                if A==B:intervals.append(base|dict(status='not_applicable',actual_switch_pair_checked=None,actual_switch_pair_sensitive=None));continue
                pair=[index.get((br,round(h*80))) for h in [a['h'],b['h']] for br in [A,B]]
                if any(r is None for r in pair):intervals.append(base|dict(status='missing_candidate',pair_complete=False,actual_switch_pair_checked=None,actual_switch_pair_sensitive=None));continue
                intervals.append(base|dict(status='complete',pair_complete=True,candidates=[r['archive'] for r in pair]))
                for p in CFG['p']:
                    comps=[compare(pair[j],pair[j+1],p) for j in [0,2]]
                    da=np.load(ROOT/comps[0]['density_a']['archive']);ar=np.load(ROOT/comps[1]['density_a']['archive']);br=np.load(ROOT/comps[1]['density_b']['archive'])
                    decomposition={}
                    for key in ['correlations','structure_factor','mx']:
                        total=br[key]-da[key];same=ar[key]-da[key];switch=br[key]-ar[key];np.testing.assert_allclose(total,same+switch,atol=1e-12)
                        decomposition[key]={'total':total.tolist(),'same_chain_change':same.tolist(),'switch_change_at_right':switch.tolist()}
                    result=base|dict(comparison_p=p,endpoints=comps,actual_switch_pair_checked=True,actual_switch_pair_sensitive=any(c['actual_switch_pair_sensitive'] for c in comps),both_preparations_pass=all(c['both_preparations_pass'] for c in comps),pair_complete=True,decomposition=decomposition)
                    prior=next((c for c in oldchecks if c['kappa']==k and c['layers']==L and c['h']==b['h'] and c['p']==p),None)
                    result.update(actual_switch_pair_sensitive_at_left=comps[0]['actual_switch_pair_sensitive'],actual_switch_pair_sensitive_at_right=comps[1]['actual_switch_pair_sensitive'])
                    result.update(opposite_direction_checked=True if prior else None,opposite_direction_sensitive=prior['branch_sensitive'] if prior else None)
                    results.append(result);dump(OUT/'branch_audit/pairs'/f"{base['id']}_p{p}.json",result)
                    cross.append({key:result[key] for key in ['id','kappa','layers','left_h','right_h','comparison_p','left_branch_id','right_branch_id','both_preparations_pass','actual_switch_pair_checked','actual_switch_pair_sensitive','opposite_direction_checked','opposite_direction_sensitive','actual_switch_pair_sensitive_at_left','actual_switch_pair_sensitive_at_right']})
            print('Actual switching pairs complete',k,L,flush=True)
    dump(OUT/'branch_audit/intervals.json',intervals);dump(OUT/'branch_audit/comparisons.json',results);write_csv(OUT/'branch_audit/old_new_flags.csv',cross)
    case=[]
    for label,L,h,names in [('case1',4,.85,['descending_s101','descending_s307']),('case2',6,.7,['ascending_s307','descending_s101'])]:
        chosen=[next(r for r in chains if r['kappa']==.3 and r['layers']==L and r['h']==h and r['group']=='C_'+name.split('_s')[0] and r['seed']==int(name.split('_s')[1])) for name in names]
        for p in CFG['p']:
            c=compare(*chosen,p);c.update(case=label,candidates=chosen)
            if label=='case2':
                c['full_density']=[noise(r,p,keep=True) for r in chosen]
                for j,r in enumerate(chosen):
                    np.savez_compressed(OUT/'branch_audit'/f'case2_candidate{j}.npz',params=params(r),ideal_state=HVAEngine().state(params(r)),ed_state=np.load(ROOT/r['archive'])['ed_state'])
            case.append(c)
    dump(OUT/'branch_audit/regression_cases.json',case)
    for L in [4,6]:dump(OUT/f'branch_audit/resources_L{L}.json',resources(8,L))
    # New contextual view: actual incoming/outgoing intervals, never inherit old checked.
    views=[]
    for r in read(OLD/'slices/observations.json'):
        adjacent=[c for c in results if c['kappa']==r['kappa'] and c['layers']==r['layers'] and c['comparison_p']==r['p'] and r['h'] in [c['left_h'],c['right_h']]]
        views.append(r|dict(opposite_direction_checked=r['branch_checked'] or None,opposite_direction_sensitive=r['branch_sensitive'] if r['branch_checked'] else None,actual_switch_pair_checked=all(c['actual_switch_pair_checked'] for c in adjacent) if adjacent else None,actual_switch_pair_sensitive=any(c['actual_switch_pair_sensitive'] for c in adjacent) if adjacent else None,actual_switch_context='checked' if adjacent else 'not_applicable',actual_pair_ids=[c['id'] for c in adjacent]))
    dump(OUT/'branch_audit/slice_view.json',views)
    print('A finished',sum(r['status']=='complete' for r in intervals),'switches',flush=True)

def repair_grid():
    selected=read(OLD/'grid/selection_frozen.json')['rows'];original_noise=read(OLD/'grid/observations.json');paths=read(OLD/'grid/optimization_rows.json')+read(OLD/'slices/optimization_rows.json');bad=[];allruns=[];replacements=[];newrows=[];faildetails=[]
    for r in selected:
        d=np.load(ROOT/r['archive']);met,o,ed=metrics(d['state'],d['ed_state'],float(d['ed_energy']),r['kappa'],r['h'],CFG['thresholds'])
        assert met['joint_pass']==r['joint_pass']
        if not met['joint_pass']:
            bad.append(r);faildetails.append(dict(kappa=r['kappa'],h=r['h'],**met,failed_metrics=fail_metrics(met),max_error_r=int(np.argmax(abs(o['correlations']-ed['correlations']))),correlations=o['correlations'].tolist(),ed_correlations=ed['correlations'].tolist(),original_source=r['archive']))
    assert len(bad)<=13,'Unexpected failure set; inspect before expanding budget'
    dump(OUT/'grid_repair/initial_failures.json',faildetails);write_csv(OUT/'grid_repair/initial_failures.csv',faildetails)
    for i,r in enumerate(bad):
        k,h=r['kappa'],r['h'];same=sorted([s for s in paths if s['kappa']==k and s['h']==h and s['layers']==6],key=lambda s:s['energy']);origins=[]
        for s in same:
            if not any(s['archive']==t['archive'] for t in origins):origins.append(s)
            if len(origins)==2:break
        nearby=sorted([s for s in selected if s['joint_pass'] and s['layers']==6],key=lambda s:((s['kappa']-k)**2+(s['h']-h)**2,s['energy']))[:2]
        initial=[(params(s),s['seed'],'parameter_resume',s['archive']) for s in origins]+[(params(s),s['seed'],'neighbor_initialization',s['archive']) for s in nearby]
        initial +=[(np.random.default_rng(np.random.SeedSequence([seed,round(k*1000),round(h*1000),6])).uniform(-.5,.5,(6,3)),seed,'independent_cold','uniform[-.5,.5]') for seed in [701,809]]
        assert len(initial)==6
        runs=[]
        for j,(theta,seed,method,source) in enumerate(initial):
            run=run_opt(f'B_point{i:02d}_attempt{j}',theta,k,h,seed,source);run['method']=method;run['old_iterations_in_source']=next((s['nit'] for s in same+nearby if s['archive']==source),0);runs.append(run);allruns.append(run)
        best=min([r]+runs,key=lambda x:x['energy']);changed=array_hash(params(best))!=array_hash(params(r));newrows.append(best)
        replacements.append(dict(kappa=k,h=h,old=r,new=best,changed=changed,selection='minimum energy including historical winner',other_candidate_pass=any(s['joint_pass'] for s in runs),selected_pass=best['joint_pass'],failed_metrics=fail_metrics(best)))
        print('B repair',k,h,'pass',best['joint_pass'],'failed',fail_metrics(best),flush=True)
    dump(OUT/'grid_repair/all_attempts.json',allruns);write_csv(OUT/'grid_repair/all_attempts.csv',allruns);dump(OUT/'grid_v2/replacement_map.json',replacements)
    updated=[next((s for s in newrows if s['kappa']==r['kappa'] and s['h']==r['h']),r) for r in selected]
    dump(OUT/'grid_v2/selection_frozen.json',dict(created_utc=now(),rows=updated,selection='energy only; frozen before updated noise'))
    results=[]
    for r in updated:
        rep=next((v for v in replacements if v['kappa']==r['kappa'] and v['h']==r['h']),None)
        for p in CFG['p']:
            if rep and rep['changed']:n=noise(r,p)
            else:
                n=next(s for s in original_noise if s['kappa']==r['kappa'] and s['h']==r['h'] and s['p']==p);assert sha(ROOT/n['archive'])==n['archive_sha256'];n=n|dict(cache_status='reused_stage3')
            near=any(v['changed'] and ((v['kappa']==r['kappa'] and abs(v['h']-r['h'])<=.10000001) or (v['h']==r['h'] and abs(v['kappa']-r['kappa'])<=.05000001)) for v in replacements)
            n=n|dict(preparation_failed=not r['joint_pass'],selection_archive=r['archive'],protocol_changed_neighborhood=near,actual_switch_pair_checked=None,actual_switch_pair_sensitive=None)
            if not near:
                old=next((v for v in read(OUT/'branch_audit/slice_view.json') if v['params_sha256']==n['params_sha256'] and v['kappa']==n['kappa'] and v['h']==n['h'] and v['p']==p),None)
                if old:n.update(actual_switch_pair_checked=old['actual_switch_pair_checked'],actual_switch_pair_sensitive=old['actual_switch_pair_sensitive'])
            results.append(n)
    dump(OUT/'grid_v2/observations.json',results);write_csv(OUT/'grid_v2/observations.csv',results)
    print('B complete pass',sum(r['joint_pass'] for r in updated),'/420',flush=True)

def local_windows():
    chains=read(OLD/'slices/optimization_rows.json');opts=[];noises=[];jumps=[]
    for w in CFG['windows']:
        start=round(w['lo']*80);stop=round(w['hi']*80)
        for origin in [o for o in read(ROOT/'configs/stage4_local_amendment_v1.json')['origins'] if o['window']==w['id']]:
            direction,seed=origin['direction'],origin['seed']
            indices=list(range(start,stop+1));indices=indices if direction=='ascending' else indices[::-1]
            source=next(r for r in chains if r['kappa']==w['kappa'] and r['layers']==6 and r['h']==indices[0]/80 and r['group']=='C_'+direction and r['seed']==seed)
            assert source['joint_pass'];theta=params(source);previous=None;rows=[]
            for index in indices:
                r=run_opt(f"C_{w['id']}_{direction}_seed{seed}_i{index}",theta,w['kappa'],index/80,seed,source['archive'],2000)
                r.update(window=w['id'],direction=direction,chain=f"{w['id']}/{direction}/seed{seed}",grid_index=index)
                state=np.load(ROOT/r['archive'])['state'];o=observe(state)
                if previous:
                    po=observe(previous[1]);inf=float(max(0,1-abs(np.vdot(previous[1],state))**2));delta=max(float(np.max(abs(o['correlations']-po['correlations']))),abs(o['mx']-po['mx']))
                    jumps.append(dict(window=w['id'],chain=r['chain'],left_index=min(index,previous[0]),right_index=max(index,previous[0]),infidelity=inf,observable_difference=delta,possible_optimizer_jump=inf>CFG['local']['chain_jump_infidelity'] or delta>CFG['local']['chain_jump_observable']))
                previous=(index,state);theta=params(r);source=r;rows.append(r);opts.append(r)
            dump(OUT/'local_refinement'/f"{w['id']}_{direction}_frozen.json",dict(created_utc=now(),rows=rows))
            for r in rows:
                for p in CFG['p']:noises.append(noise(r,p)|dict(window=r['window'],chain=r['chain'],grid_index=r['grid_index'],preparation_failed=not r['joint_pass'],selection_archive=r['archive']))
            dump(OUT/'local_refinement/optimization.json',opts);dump(OUT/'local_refinement/observations.json',noises);dump(OUT/'local_refinement/chain_jumps.json',jumps)
            print('C local',w['id'],direction,'passes',sum(r['joint_pass'] for r in rows),'/',len(rows),flush=True)
    write_csv(OUT/'local_refinement/optimization.csv',opts);write_csv(OUT/'local_refinement/observations.csv',noises)
    overlap=[]
    for w in CFG['windows']:
        for i in range(round(w['lo']*80),round(w['hi']*80)+1):
            pair=[r for r in opts if r['window']==w['id'] and r['grid_index']==i];a,b=[np.load(ROOT/r['archive'])['state'] for r in pair]
            overlap.append(dict(window=w['id'],grid_index=i,h=i/80,ideal_overlap=float(abs(np.vdot(a,b))**2),both_preparations_pass=all(r['joint_pass'] for r in pair),observable_difference=max(float(np.max(abs(observe(a)['correlations']-observe(b)['correlations']))),abs(observe(a)['mx']-observe(b)['mx']))))
    dump(OUT/'local_refinement/branch_overlap.json',overlap)
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--task',choices=['A','B','C','all'],default='all');a=p.parse_args()
    if a.task in ['A','all']:audit_branches()
    if a.task in ['B','all']:repair_grid()
    if a.task in ['C','all']:local_windows()
