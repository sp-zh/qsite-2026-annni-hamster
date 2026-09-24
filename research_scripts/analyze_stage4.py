import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from annni.stage4 import *
from annni.stage4_diagnostics import derivative_peaks,coarsen_edges

def analyze():
    comparisons=read(OUT/'branch_audit/comparisons.json');old=read(OLD/'slices/diagnostics/peaks.json');new=[];curves=[]
    for k in [0.,.3,.8]:
        for L in [4,6]:
            for p in CFG['p']:
                rows=sorted([r for r in read(OUT/'branch_audit/slice_view.json') if r['kappa']==k and r['layers']==L and r['p']==p],key=lambda r:r['h']);h=np.array([r['h'] for r in rows]);valid=np.array([not r['preparation_failed'] for r in rows]);edge=np.ones(len(h)-1,bool)
                for i in range(len(h)-1):
                    comp=next((c for c in comparisons if c['kappa']==k and c['layers']==L and c['comparison_p']==p and c['left_h']==h[i] and c['right_h']==h[i+1]),None)
                    if comp:edge[i]=comp['actual_switch_pair_checked'] and not comp['actual_switch_pair_sensitive'] and comp['both_preparations_pass']
                for feature,sign in [('order',-1),('mx',1)]:
                    y=np.array([np.load(ROOT/r['archive'])['structure_factor'][0 if k<.5 else 2] if feature=='order' else r['mx'] for r in rows])
                    d,peaks=derivative_peaks(h,y,valid,edge,CFG['diagnostics'],sign)
                    for peak in peaks:
                        stable=True;supports=[peak['full_computation_support']]
                        for offset in [0,1]:
                            ids=np.arange(offset,len(h),2);_,coarse=derivative_peaks(h[ids],y[ids],valid[ids],coarsen_edges(ids,edge),CFG['diagnostics'],sign)
                            candidates=[c for c in coarse if c['resolved_under_protocol'] and abs(c['h']-peak['h'])<=.1+1e-12]
                            if not candidates:stable=False
                            else:supports.append(min(candidates,key=lambda c:abs(c['h']-peak['h']))['full_computation_support'])
                        peak.update(kappa=k,L=L,p=p,feature=feature,coarse_stable=stable,all_support_ranges=supports)
                        peak['resolved_under_protocol'] &= stable;new.append(peak)
                    curves.extend(dict(kappa=k,L=L,p=p,feature=feature,h=float(x),value=float(v),derivative=float(dv) if np.isfinite(dv) else None) for x,v,dv in zip(h,y,d))
    diff=[]
    for r in old:
        candidate=[c for c in new if c['kappa']==r['kappa'] and c['L']==r['L'] and c['p']==r['p'] and c['feature']==r['feature'] and abs(c['h']-r['h'])<1e-10]
        diff.append(dict(kappa=r['kappa'],L=r['L'],p=r['p'],feature=r['feature'],h=r['h'],old_resolved=r['resolved'],new_resolved=any(c['resolved_under_protocol'] for c in candidate),reason='Actual A/B pair at both ends; full derivative/prominence/coarse support; masked stitches can change peaks'))
    dump(OUT/'branch_audit/revised_peaks.json',new);dump(OUT/'branch_audit/revised_curves.json',curves);dump(OUT/'branch_audit/diagnostic_changes.json',diff);write_csv(OUT/'branch_audit/diagnostic_changes.csv',diff)
    observations=read(OUT/'local_refinement/observations.json');jump=read(OUT/'local_refinement/chain_jumps.json');peaks=[];curves=[];sensitivity=[]
    for w in CFG['windows']:
        for origin in [o for o in read(ROOT/'configs/stage4_local_amendment_v1.json')['origins'] if o['window']==w['id']]:
            direction,seed=origin['direction'],origin['seed']
            chain=f"{w['id']}/{direction}/seed{seed}"
            for p in CFG['p']:
                rows=sorted([r for r in observations if r['chain']==chain and r['p']==p],key=lambda r:r['h']);h=np.array([r['h'] for r in rows]);valid=np.array([not r['preparation_failed'] for r in rows]);edge=np.array([not any(j['chain']==chain and j['left_index']==rows[i]['grid_index'] and j['possible_optimizer_jump'] for j in jump) for i in range(len(rows)-1)])
                for feature,sign in [('order',-1),('mx',1)]:
                    y=np.array([np.load(ROOT/r['archive'])['structure_factor'][0 if w['kappa']<.5 else 2] if feature=='order' else r['mx'] for r in rows])
                    for stride in [4,2,1]:
                        ids=np.arange(0,len(h),stride);d,pp=derivative_peaks(h[ids],y[ids],valid[ids],coarsen_edges(ids,edge),CFG['diagnostics'],sign)
                        for r in pp:peaks.append(r|dict(window=w['id'],chain=chain,p=p,feature=feature,stride=stride))
                        curves.extend(dict(window=w['id'],chain=chain,p=p,feature=feature,stride=stride,h=float(x),value=float(v),derivative=float(dv) if np.isfinite(dv) else None) for x,v,dv in zip(h[ids],y[ids],d))
        for index in range(round(w['lo']*80),round(w['hi']*80)+1):
            for p in CFG['p']:
                pair=[r for r in observations if r['window']==w['id'] and r['grid_index']==index and r['p']==p];a,b=[np.load(ROOT/r['archive']) for r in pair]
                ec=float(np.max(abs(a['correlations']-b['correlations'])));es=float(np.max(abs(a['structure_factor']-b['structure_factor'])));em=abs(float(a['mx']-b['mx']))
                sensitivity.append(dict(window=w['id'],h=index/80,p=p,epsilon_c=ec,epsilon_sf=es,epsilon_mx=em,branch_sensitive=max(ec,es,em)>.02,both_preparations_pass=all(not r['preparation_failed'] for r in pair)))
    stability=[]
    for r in [r for r in peaks if r['stride']==1]:
        matches=[]
        for stride in [2,4]:
            c=[s for s in peaks if s['chain']==r['chain'] and s['p']==r['p'] and s['feature']==r['feature'] and s['stride']==stride and s['resolved_under_protocol']]
            m=min(c,key=lambda s:abs(s['h']-r['h'])) if c else None
            matches.append(m if m and abs(m['h']-r['h'])<=2*stride/80+1e-12 else None)
        stability.append(r|dict(coarse_matches=matches,last_two_position_difference=r['h']-matches[0]['h'] if matches[0] else None,stable_last_two=bool(r['resolved_under_protocol'] and matches[0]),stable_all_three=bool(r['resolved_under_protocol'] and all(matches))))
    shifts=[]
    for w in CFG['windows']:
        for chain in sorted(set(r['chain'] for r in observations if r['window']==w['id'])):
            for feature in ['order','mx']:
                zero=[r for r in stability if r['chain']==chain and r['feature']==feature and r['p']==0 and r['stable_all_three']]
                for p in [.01,.05]:
                    noisy=[r for r in stability if r['chain']==chain and r['feature']==feature and r['p']==p and r['stable_all_three']];matched=[]
                    for a in zero:
                        if not noisy:continue
                        b=min(noisy,key=lambda s:abs(s['h']-a['h']))
                        if min(zero,key=lambda s:abs(s['h']-b['h'])) is not a or abs(a['h']-b['h'])>.2:continue
                        matched.append(dict(window=w['id'],chain=chain,feature=feature,p=p,status='resolved_under_protocol',h0=a['h'],hp=b['h'],delta_h=b['h']-a['h'],range_low=b['position_support'][0]-a['position_support'][1],range_high=b['position_support'][1]-a['position_support'][0],grid_support_note='deterministic grid/protocol range, not confidence interval'))
                    shifts.extend(matched or [dict(window=w['id'],chain=chain,feature=feature,p=p,status='not_resolved_under_protocol',delta_h=None)])
    for r in shifts:
        if r['delta_h'] is None:continue
        others=[s for s in shifts if s['chain']==r['chain'] and s['p']==r['p'] and s['feature']!=r['feature'] and s['delta_h'] is not None]
        r['complementary_agreement']=any(max(r['range_low'],s['range_low'])<=min(r['range_high'],s['range_high']) for s in others)
        r['nonzero_supported_on_this_chain']=r['complementary_agreement'] and (r['range_low']>0 or r['range_high']<0)
    for name,data in [('peaks',peaks),('curves',curves),('stability',stability),('shifts',shifts),('branch_sensitivity',sensitivity)]:dump(OUT/f'local_refinement/{name}.json',data);write_csv(OUT/f'local_refinement/{name}.csv',data)
    print('A old/new resolved',sum(r['old_resolved'] for r in diff),sum(r['new_resolved'] for r in diff));print('Local shifts',shifts)
if __name__=='__main__':analyze()
