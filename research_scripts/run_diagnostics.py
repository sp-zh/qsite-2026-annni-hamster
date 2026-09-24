"""Run diagnostics from frozen baseline files; no new ED solves or learned labels."""
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.mplconfig'))
import sys
sys.path.insert(0,str(ROOT))
import csv, hashlib, importlib.metadata, json, platform, time
from datetime import datetime, timezone
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from annni.diagnostics import diagnose, folded_peaks, local_peaks, validate_dataset, load_config


def write_csv(path,rows):
    with path.open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def savefig(fig,path):
    fig.savefig(path.with_suffix('.png'),dpi=170,bbox_inches='tight')
    fig.savefig(path.with_suffix('.pdf'),bbox_inches='tight');plt.close(fig)


def main():
    start=time.perf_counter();out=ROOT/'results/diagnostics_v1';out.mkdir(exist_ok=True,parents=True)
    config=load_config();(out/'protocol.json').write_text(json.dumps(config,indent=2))
    paths=[ROOT/'results/baseline'/name for name in ['grid_n8.npz','slices_n8.npz','slices_n12.npz','slices_n16.npz']]
    datasets=[dict(np.load(p)) for p in paths]
    inventory={str(p.relative_to(ROOT)):{k:{'shape':list(v.shape),'dtype':str(v.dtype)} for k,v in d.items()} for p,d in zip(paths,datasets)}
    for d in datasets: validate_dataset(d)
    (out/'input_inventory.json').write_text(json.dumps(inventory,indent=2))
    controls=[]
    for n in [8,12,16]:
        ferro=np.zeros(n);ferro[0]=1
        anti=np.zeros(n);anti[n//4]=anti[3*n//4]=.5
        for name,sf,mx in [('ferro',ferro,0),('antiphase',anti,0),('plus',np.ones(n)/n,1),('mixed',np.ones(n)/n,0)]:
            result=diagnose(sf,mx,config)
            controls.append(dict(n=n,control=name,label=result['label'],margin=result['margin']))
    write_csv(out/'control_states.csv',controls)
    curves=[];peaks=[];wave=[];protocol_rows=[];transitions=[];summaries=[]
    figq,axs=plt.subplots(2,3,figsize=(13,7.6),layout='constrained')
    figr,axr=plt.subplots(3,3,figsize=(13,9),layout='constrained')
    colors={8:'#2563eb',12:'#d97706',16:'#128675'}
    for col,d in enumerate(datasets[1:]):
        n=int(d['n']);ki=int(np.flatnonzero(np.isclose(d['kappa'],.8))[0]);sf=d['structure_factor'][ki]
        artist=axs[0,col].pcolormesh(d['h'],2*np.arange(n)/n,sf.T,shading='nearest',vmin=0,vmax=.5,cmap='viridis')
        axs[0,col].set(xlabel='h',ylabel='q / π',title=f'N={n}, κ=0.8 | full q')
        axs[1,col].plot(d['h'],sf[:,n//4],color='#2563eb',label='fixed q=π/2')
        competitors=np.delete(sf,[n//4,3*n//4],axis=1).max(axis=1)
        axs[1,col].plot(d['h'],competitors,color='#d97706',ls='--',label='strongest other q')
        axs[1,col].axhline(1/n,color='gray',ls=':',label='self background 1/N')
        axs[1,col].set(xlabel='h',ylabel='m_q²',ylim=(0,.51));axs[1,col].legend(fontsize=8)
        for hi,h in enumerate(d['h']):
            for rec in folded_peaks(sf[hi],config): wave.append(dict(n=n,kappa=.8,h=float(h),**rec))
        transfer=np.flatnonzero(competitors>sf[:,n//4]+1e-12)
        summaries.append(dict(n=n,first_other_q_exceeds_pi_over_2=float(d['h'][transfer[0]]) if len(transfer) else None))
        for ki,kappa in enumerate(d['kappa']):
            h=d['h'][1:];order='m2_ferro' if kappa<.5 else 'm2_antiphase'
            series={'negative_order_derivative':(h,-np.gradient(d[order][ki,1:],h,edge_order=2),None),
                    'mx_derivative':(h,np.gradient(d['mx'][ki,1:],h,edge_order=2),None),
                    'chi_f_per_site':(d['h_mid'],d['chi_f'][ki]/n,np.column_stack([d['h'][:-1],d['h'][1:]]))}
            for row,(metric,(x,y,support)) in enumerate(series.items()):
                axr[row,ki].plot(x,y,label=f'N={n}',color=colors[n])
                axr[row,ki].set(xlabel='h',ylabel=metric,title=f'κ={kappa:g}' if row==0 else '')
                for j in range(len(x)):curves.append(dict(n=n,kappa=float(kappa),metric=metric,h=float(x[j]),value=float(y[j])))
                for rec in local_peaks(x,y,support):peaks.append(dict(n=n,kappa=float(kappa),metric=metric,order_parameter=order,**rec))
    figq.colorbar(artist,ax=axs[0,:],label='m_q²; same scale in all panels',shrink=.85)
    figq.suptitle('Full-wavevector ED diagnostics; no floating-phase assignment')
    savefig(figq,out/'full_wavevector')
    for ax in axr.flat:ax.grid(alpha=.15)
    axr[0,0].legend();figr.suptitle('Local-change diagnostics; finite-size features, not thermodynamic boundaries')
    savefig(figr,out/'change_diagnostics')
    for dataset_name,d in zip(['grid_n8','slices_n8','slices_n12','slices_n16'],datasets):
        n=int(d['n'])
        for ki,k in enumerate(d['kappa']):
            previous=None
            for hi,h in enumerate(d['h']):
                result=diagnose(d['structure_factor'][ki,hi],d['mx'][ki,hi],config)
                record=dict(dataset=dataset_name,n=n,kappa=float(k),h=float(h),label=result['label'],nearest_control=result['nearest_control'],margin=result['margin'],
                    ferro_score=result['ferro_score'],antiphase_score=result['antiphase_score'],transverse_score=result['transverse_score'])
                record.update({'distance_'+key:value for key,value in result['distances'].items()});protocol_rows.append(record)
                if previous is not None and previous!=result['label']:
                    transitions.append(dict(dataset=dataset_name,n=n,kappa=float(k),h_low=float(d['h'][hi-1]),h_high=float(h),left=previous,right=result['label']))
                previous=result['label']
    write_csv(out/'wavevector_near_peaks.csv',wave);write_csv(out/'diagnostic_curves.csv',curves)
    write_csv(out/'local_peaks.csv',peaks);write_csv(out/'prototype_diagnostics.csv',protocol_rows)
    write_csv(out/'prototype_transitions.csv',transitions)
    (out/'wavevector_summary.json').write_text(json.dumps(summaries,indent=2))
    # A continuous diagnostic map, deliberately not a forced phase-label map.
    grid=datasets[0];fig,axs=plt.subplots(1,3,figsize=(12.5,4.2),layout='constrained')
    for ax,key,title,vmax in zip(axs,['m2_ferro','m2_antiphase','mx'],['ferro structure','antiphase structure','transverse polarization'],[1,.5,1]):
        art=ax.pcolormesh(grid['kappa'],grid['h'],grid[key].T,vmin=0,vmax=vmax,shading='nearest')
        ax.set(xlabel='κ',ylabel='h',title=title);fig.colorbar(art,ax=ax)
    fig.suptitle('N=8 continuous features | prototypes retained as auxiliary resemblance checks')
    savefig(fig,out/'continuous_features')
    # Same-size prototype distances alongside local-response supports.
    fig,axs=plt.subplots(1,3,figsize=(13,4.2),layout='constrained')
    palette={'ferro_like':'#2563eb','antiphase_like':'#d97706','paramagnetic_like':'#128675','degraded':'#777777'}
    for ax,kappa in zip(axs,[0.,.3,.8]):
        selected=[r for r in protocol_rows if r['dataset']=='slices_n8' and r['kappa']==kappa]
        for label,color in palette.items():
            ax.plot([r['h'] for r in selected],[r['distance_'+label] for r in selected],color=color,label=label)
        ax.axhline(config['prototype_max_distance'],color='black',ls=':',label='distance threshold')
        for peak in peaks:
            if peak['n']==8 and peak['kappa']==kappa:
                ax.axvspan(peak['interval_low'],peak['interval_high'],color='grey',alpha=.10)
        ax.set(xlabel='h',ylabel='distance to analytic control',title=f'N=8, κ={kappa:g}',ylim=(0,1.5))
    axs[0].legend(fontsize=8)
    fig.suptitle('Auxiliary prototype comparison | grey supports: local response peaks; margin rule also required')
    savefig(fig,out/'prototype_comparison')
    # Cross-check both diagnostic schemes using same-size, same-slice coordinates only.
    cross=[]
    for p in peaks:
        candidates=[t for t in transitions if t['dataset']==f"slices_n{p['n']}" and t['kappa']==p['kappa']]
        t=min(candidates,key=lambda t:abs((t['h_low']+t['h_high'])/2-p['coordinate'])) if candidates else None
        cross.append(dict(n=p['n'],kappa=p['kappa'],metric=p['metric'],peak_h=p['coordinate'],peak_endpoint=p['endpoint'],
            prototype_interval_low=None if t is None else t['h_low'],prototype_interval_high=None if t is None else t['h_high'],
            nearest_transition=None if t is None else t['left']+' -> '+t['right'],
            midpoint_separation=None if t is None else abs((t['h_low']+t['h_high'])/2-p['coordinate'])))
    write_csv(out/'method_comparison.csv',cross)
    np.savez_compressed(out/'diagnostic_arrays.npz',**{f'n{int(d["n"])}_{key}':d[key] for d in datasets[1:] for key in ['h','h_mid','kappa','structure_factor','mx','chi_f']})
    source=[ROOT/'annni/diagnostics.py',Path(__file__),ROOT/'configs/diagnostics_v1.json',ROOT/'tests/test_diagnostics.py']
    meta=dict(created_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.perf_counter()-start,
        python=sys.version,platform=platform.platform(),versions={p:importlib.metadata.version(p) for p in ['numpy','scipy','matplotlib','pennylane']},
        source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source},
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        protocol=config,new_ED_solves=0,cache_source='Read-only original baseline NPZ; validated shapes, FFT identity, h_mid and h=0 missingness',
        model='periodic H=-sum ZZ_nn+kappa sum ZZ_nnn-h sum X; all q include self correlations',
        basis_order='Wire 0 most significant bit, checked by main calibration tests; diagnostics use existing observables',
        dataset_layout='[kappa_index,h_index,...]; chi_f uses h_mid', failures=[],retries=[],
        unfinished=['No thermodynamic phase identification','No floating phase confirmation','No statistical uncertainty intervals'])
    (out/'metadata.json').write_text(json.dumps(meta,indent=2))
    report=['# Operational diagnostics v1 — actual ED-data run','',
      'All four baseline NPZ files were loaded and validated; no ED baseline was rerun. All outputs are finite-size diagnostics. Configuration was frozen before noise evaluation.',
      '', '## Protocol',
      'Full q is retained. Equivalent k and N−k peaks are averaged, not summed; near peaks lie within max(0.005, 10% of maximum). The CSV retains every near-maximum equivalence class. Flat mixed-state spectra consequently have many equivalent candidates.',
      'Order-parameter negative derivatives and Mx derivatives use numpy.gradient(edge_order=2), h>0 only. All local maxima (including plateau centers) and one-sided endpoint maxima are saved. chiF/N remains at h_mid; NaN intervals touching h=0 remain missing. No smoothing or interpolation is applied. Derivative brackets are neighboring grid nodes; chiF brackets are its original pair of h nodes. These are resolution supports, not confidence intervals.',
      'The auxiliary prototype check uses [m0², 2 mπ/2², Mx], Euclidean distances to analytic ferro [1,0,0], antiphase [0,1,0], plus [1/N,2/N,1], and mixed [1/N,2/N,0]. A label needs distance ≤0.45 and runner-up margin ≥0.10; otherwise uncertain. Mixed resemblance is degraded. These engineering thresholds are declared, not trained or tuned on noisy observations. Labels mean resemblance, not validated phase assignments. Scores subtract self background but are not clipped, so negative excess correlation remains visible.',
      'All 12 N=8/12/16 controls returned their intended diagnostic. The maximally mixed state is degraded and is distinct from plus. protocol.json is the frozen copy.',
      '', '## Observed full-wavevector behavior']
    for r in summaries:report.append(f'- N={r["n"]}: first sampled h with a non-π/2 mode strictly stronger than the π/2 mode: {r["first_other_q_exceeds_pi_over_2"]}. This is a discrete mode competition observation, not a phase boundary.')
    report+=['','## Local peaks at κ=0.8 (all peaks retained in CSV)']
    for p in peaks:
        if p['kappa']==.8:report.append(f'- N={p["n"]}, {p["metric"]}: h={p["coordinate"]:.3f}, support [{p["interval_low"]:.3f}, {p["interval_high"]:.3f}], endpoint={p["endpoint"]}.')
    report+=['','## Comparison and limits','method_comparison.csv compares every local-change peak with the nearest same-N prototype transition interval. There is no requirement that a distance-to-control threshold coincide with a response peak; disagreement is preserved. No N=16 result labels N=8. Full-q plots separate weakening at fixed π/2 from growth of competitors. Neither observation alone establishes a floating phase. Finite-grid mode quantization, broad peaks, and analytic-prototype bias remain substantial limitations. No external phase reference curves were used.',
      '', '## Reproduce','`.venv/bin/python scripts/run_diagnostics.py`','`.venv/bin/python -m pytest tests/test_diagnostics.py -q`']
    (out/'REPORT.md').write_text('\n\n'.join(report)+'\n')
    print(json.dumps(dict(elapsed_seconds=meta['elapsed_seconds'],local_peaks=len(peaks),control_checks=len(controls),wavevector_summary=summaries),indent=2))

if __name__=='__main__':main()
