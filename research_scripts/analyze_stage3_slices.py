import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import json
import numpy as np
from annni.stage3 import OUT,CFG,dump,write_csv
from annni.stage3_diagnostics import feature_peaks
from annni.diagnostics import diagnose,folded_peaks

def main():
    observations=json.loads((OUT/'slices/observations.json').read_text())
    selected=json.loads((OUT/'slices/selection_frozen.json').read_text())['rows']
    peakrows=[];curves=[];crossings=[];qrows=[];status=[]
    for k in [0.,.3,.8]:
        for L in [4,6]:
            for p in [0,.01,.05]:
                group=sorted([r for r in observations if r['kappa']==k and r['layers']==L and r['p']==p],key=lambda r:r['h'])
                h=np.array([r['h'] for r in group])
                data=[np.load(ROOT/r['archive']) for r in group]
                sf=np.stack([d['structure_factor'] for d in data])
                order=sf[:,0] if k<.5 else sf[:,2]
                mx=np.array([r['mx'] for r in group])
                valid=np.array([not r['preparation_failed'] and not bool(r['branch_sensitive']) for r in group])
                switch=np.array([r['branch_switch'] for r in group]);checked=np.array([r['branch_checked'] for r in group])
                sensitive=[r['branch_sensitive'] for r in group]
                labels=[r['diagnostic'] for r in group]
                for i in range(len(group)):
                    if i and labels[i]!=labels[i-1]:
                        crossings.append(dict(kappa=k,L=L,p=p,h_low=float(h[i-1]),h_high=float(h[i]),
                            from_label=labels[i-1],to_label=labels[i],both_preparation_valid=bool(valid[i-1] and valid[i]),
                            branch_switch=bool(switch[i]),interpretation='control-resemblance transition only'))
                    if k==.8:
                        competitors=sf[i,:5].copy();competitors[2]=-np.inf
                        qrows.append(dict(L=L,p=p,h=float(h[i]),m_pi2=float(sf[i,2]),
                            strongest_other=float(competitors.max()),other_q_over_pi=float(competitors.argmax()/4),
                            competing_excess=float(competitors.max()-sf[i,2]),
                            near_peaks=folded_peaks(sf[i]),preparation_failed=group[i]['preparation_failed']))
                for feature,y,sign in [('order',order,-1),('mx',mx,1)]:
                    derivative,peaks=feature_peaks(h,y,valid,switch,checked,sensitive,CFG['diagnostics'],sign)
                    for peak in peaks:peakrows.append(dict(kappa=k,L=L,p=p,feature=feature,**peak))
                    resolved=[r for r in peaks if r['resolved']]
                    status.append(dict(kappa=k,L=L,p=p,feature=feature,preparation_valid_count=int(valid.sum()),
                        raw_peak_count=len(peaks),resolved_peak_count=len(resolved),
                        status='resolved' if resolved else 'not_resolved',
                        curve_range=float(np.ptp(y)),
                        reason_if_unresolved='' if resolved else 'See individual peaks; no feature satisfies all frozen amplitude, prominence, stability and branch checks'))
                    for i in range(len(h)):
                        curves.append(dict(kappa=k,L=L,p=p,feature=feature,h=float(h[i]),value=float(y[i]),
                            derivative=float(derivative[i]) if np.isfinite(derivative[i]) else None,
                            preparation_failed=group[i]['preparation_failed'],branch_switch=bool(switch[i]),
                            branch_checked=bool(checked[i]),branch_sensitive=sensitive[i]))
    shifts=[]
    for k in [0.,.3,.8]:
        for L in [4,6]:
            for feature in ['order','mx']:
                zero=[r for r in peakrows if r['kappa']==k and r['L']==L and r['p']==0 and r['feature']==feature and r['resolved']]
                for p in [.01,.05]:
                    noisy=[r for r in peakrows if r['kappa']==k and r['L']==L and r['p']==p and r['feature']==feature and r['resolved']]
                    matches=[]
                    for a in zero:
                        if not noisy:continue
                        b=min(noisy,key=lambda b:abs(b['h']-a['h']))
                        reverse=min(zero,key=lambda z:abs(z['h']-b['h']))
                        if reverse is a and abs(b['h']-a['h'])<=.2000001:matches.append((a,b))
                    if not matches:
                        shifts.append(dict(kappa=k,L=L,p=p,feature=feature,status='not_resolved',delta_h=None,
                            reason='No mutually matched resolved feature with valid preparation and checked branch neighborhood'))
                    for a,b in matches:
                        shifts.append(dict(kappa=k,L=L,p=p,feature=feature,status='candidate_match',
                            h0=a['h'],hp=b['h'],delta_h=b['h']-a['h'],
                            shift_support_low=b['interval_low']-a['interval_high'],
                            shift_support_high=b['interval_high']-a['interval_low'],
                            reason='Grid support only; needs complementary-indicator agreement'))
    for r in shifts:
        if r['status']!='candidate_match':continue
        other=[s for s in shifts if s['kappa']==r['kappa'] and s['L']==r['L'] and s['p']==r['p'] and s['feature']!=r['feature'] and s.get('delta_h') is not None]
        support_overlap=any(max(r['shift_support_low'],s['shift_support_low'])<=min(r['shift_support_high'],s['shift_support_high']) for s in other)
        r['complementary_indicator_agrees']=support_overlap
        r['status']='matched_diagnostic' if support_overlap else 'single_indicator_only'
        r['nonzero_shift_resolved']=support_overlap and (r['shift_support_low']>0 or r['shift_support_high']<0)
    dest=OUT/'slices/diagnostics'
    for name,rows in [('peaks',peakrows),('curves',curves),('status',status),('prototype_crossings',crossings),('wavevector_competition',qrows),('apparent_shifts',shifts)]:
        dump(dest/f'{name}.json',rows);write_csv(dest/f'{name}.csv',rows)
    coverage={str(L):dict(passed=sum(r['joint_pass'] for r in selected if r['layers']==L),total=120) for L in [4,6]}
    dump(OUT/'slices/coverage.json',coverage)
    print('Coverage',coverage)
    print('Resolved peaks',len([r for r in peakrows if r['resolved']]),'/',len(peakrows))
    print('Shift results',shifts)
if __name__=='__main__':main()
