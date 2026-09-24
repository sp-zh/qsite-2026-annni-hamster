"""Run deterministic ED scans, save raw data, and produce summary figures."""
import os
os.environ.setdefault("MPLCONFIGDIR", str(__import__('pathlib').Path(__file__).resolve().parents[1]/'.mplconfig'))
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import argparse
import csv
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import sys
import time
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from annni.model import Chain, fidelity_susceptibility

SCALARS=['energy_per_site','mx','c1','c2','m2_ferro','m2_antiphase','residual','classical_degeneracy']


def scan(n,kappas,fields,path,save_states=False):
    chain=Chain(n)
    data={key:np.empty((len(kappas),len(fields))) for key in SCALARS}
    data['correlations']=np.empty((len(kappas),len(fields),n))
    data['structure_factor']=np.empty_like(data['correlations'])
    data['chi_f']=np.empty((len(kappas),len(fields)-1))
    saved=[]
    for ki,kappa in enumerate(kappas):
        states=[]
        for hi,h in enumerate(fields):
            result=chain.ground_state(float(kappa),float(h))
            obs=chain.observables(result)
            for key in SCALARS+['correlations','structure_factor']:
                data[key][ki,hi]=obs[key]
            states.append(result.state)
        mid,chi=fidelity_susceptibility(states,fields)
        data['chi_f'][ki]=chi
        if save_states:
            saved.append(np.stack([np.full(chain.dim,np.nan) if s is None else s for s in states]))
        print(f'N={n}, kappa={kappa:.2f}: {len(fields)} points, max residual={data["residual"][ki].max():.2e}',flush=True)
    data.update(n=np.array(n),kappa=np.array(kappas),h=np.array(fields),h_mid=mid)
    if save_states:
        data['states']=np.stack(saved)
    np.savez_compressed(path,**data)
    with path.with_suffix('.csv').open('w') as handle:
        writer=csv.writer(handle)
        writer.writerow(['n','kappa','h']+SCALARS)
        for ki,k in enumerate(kappas):
            for hi,h in enumerate(fields):
                writer.writerow([n,k,h]+[data[key][ki,hi] for key in SCALARS])
    return data


def savefig(fig,path):
    fig.savefig(path.with_suffix('.png'),dpi=180,bbox_inches='tight')
    fig.savefig(path.with_suffix('.pdf'),bbox_inches='tight')
    plt.close(fig)


def plot_grid(data,out):
    fig,axs=plt.subplots(2,3,figsize=(12,7.3),layout='constrained')
    panels=[('m2_ferro',r'$m_0^2$',0,1,'viridis'),('m2_antiphase',r'$m_{\pi/2}^2$',0,.5,'viridis'),
            ('mx',r'$M_x$',0,1,'viridis'),('c1',r'$C(1)$',-1,1,'RdBu_r'),
            ('c2',r'$C(2)$',-1,1,'RdBu_r'),('chi_f',r'$\log_{10}(1+\chi_F)$',None,None,'magma')]
    for ax,(key,label,vmin,vmax,cmap) in zip(axs.flat,panels):
        values=data[key]
        y=data['h_mid'] if key=='chi_f' else data['h']
        if key=='chi_f': values=np.log10(1+values)
        artist=ax.pcolormesh(data['kappa'],y,values.T,shading='nearest',cmap=cmap,vmin=vmin,vmax=vmax,rasterized=True)
        fig.colorbar(artist,ax=ax,pad=.02)
        ax.set(xlabel=r'$\kappa$',ylabel=r'$h$',title=label,xlim=(0,1),ylim=(0,2))
    fig.suptitle('ANNNI exact-ground-state diagnostics | N=8, periodic | 21 x 21 grid',fontsize=15)
    fig.supxlabel('Observable maps, not four-phase classification. h=0: equal classical mixture; fidelity intervals touching h=0 excluded.',fontsize=9)
    savefig(fig,out/'ed_n8_maps')


def plot_slices(datasets,out):
    fig,axs=plt.subplots(3,3,figsize=(12,9),layout='constrained')
    colors={8:'#2563eb',12:'#d97706',16:'#128675'}
    for col,k in enumerate(datasets[0]['kappa']):
        order='m2_ferro' if k<.5 else 'm2_antiphase'
        for d in datasets:
            n=int(d['n']); color=colors[n]
            axs[0,col].plot(d['h'],d[order][col],label=f'N={n}',color=color)
            axs[1,col].plot(d['h'],d['mx'][col],color=color)
            axs[2,col].plot(d['h_mid'],d['chi_f'][col]/n,color=color)
        axs[0,col].set_title(rf'$\kappa={k:g}$')
        axs[0,col].set_ylabel(r'$m_0^2$' if k<.5 else r'$m_{\pi/2}^2$')
        axs[1,col].set_ylabel(r'$M_x$')
        axs[2,col].set_ylabel(r'$\chi_F / N$')
        axs[2,col].set_xlabel(r'$h$')
        axs[0,col].legend(frameon=False)
        if k==0:
            for row in range(3): axs[row,col].axvline(1,color='gray',ls='--',lw=1)
        for row in range(3):
            axs[row,col].set_xlim(0,2)
            axs[row,col].grid(alpha=.18)
    fig.suptitle('Finite-size comparison | periodic N=8, 12, 16 | field step 0.05',fontsize=15)
    fig.supxlabel('Dashed line: thermodynamic Ising h=1 only. Finite-size peaks are diagnostics, not confirmed phase boundaries.',fontsize=9)
    savefig(fig,out/'finite_size_slices')


def peak_rows(datasets):
    rows=[]
    for d in datasets:
        for ki,k in enumerate(d['kappa']):
            # Exclude zero-field mixed-state endpoint for derivative diagnostics.
            order='m2_ferro' if k<.5 else 'm2_antiphase'
            h=d['h'][1:]
            derivative=-np.gradient(d[order][ki,1:],h,edge_order=2)
            j=int(np.argmax(derivative))
            jf=int(np.nanargmax(d['chi_f'][ki]))
            rows.append(dict(n=int(d['n']),kappa=float(k),order_parameter=order,
                             derivative_peak_h=float(h[j]),
                             derivative_peak_at_endpoint=j in (0,len(h)-1),
                             fidelity_peak_h=float(d['h_mid'][jf]),
                             fidelity_peak_at_endpoint=jf in (1,len(d['h_mid'])-1),
                             field_step=float(h[1]-h[0])))
    return rows


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=ROOT/'results/baseline')
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    start=time.perf_counter()
    grid=scan(8,np.linspace(0,1,21),np.linspace(0,2,21),args.out/'grid_n8',True)
    plot_grid(grid,args.out)
    datasets=[scan(n,np.array([0.,.3,.8]),np.linspace(0,2,41),args.out/f'slices_n{n}') for n in [8,12,16]]
    plot_slices(datasets,args.out)
    rows=peak_rows(datasets)
    with (args.out/'diagnostic_peaks.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    comparison=[]
    for n in [6,8,10,12,16]:
        chain=Chain(n); r=chain.ground_state(.8,.2); obs=chain.observables(r)
        comparison.append(dict(n=n,kappa=.8,h=.2,c2=obs['c2'],energy_per_site=obs['energy_per_site'],residual=r.residual))
    metadata=dict(created_utc=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.perf_counter()-start,
                  python=sys.version,platform=platform.platform(),initial_vector='uniform positive, deterministic',tolerance=1e-11,
                  versions={p:importlib.metadata.version(p) for p in ['numpy','scipy','matplotlib','pennylane']},
                  upstream=json.loads((ROOT/'upstream/PROVENANCE.json').read_text()),
                  source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'annni/model.py',Path(__file__)]},
                  point_count=441+3*3*41+len(comparison),boundary_conditions='periodic',
                  solver='CSR, even spin-flip sector, uniform start, momentum-zero projection, eigsh k=1 SA; h=0 classical mixture',
                  max_residual=max(float(d['residual'].max()) for d in [grid]+datasets),
                  commensurability_check=comparison,
                  limitations=['No VQE or gate noise in this baseline.','No four-phase classification or floating-phase confirmation.',
                               'Peak positions are grid diagnostics, not uncertainty intervals or thermodynamic boundaries.',
                               'h=0 uses equal incoherent mixture; it need not equal the h->0+ state.'])
    (args.out/'metadata.json').write_text(json.dumps(metadata,indent=2))
    print(json.dumps(metadata,indent=2),flush=True)


if __name__=='__main__':
    main()
