"""Retained D2 squared-Uhlmann susceptibility: explicit full-simulator-state access."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_arms import load
from annni.stage6_noise import physical
from annni.upgrade_detection import uhlmann_squared
from annni.stage6_diagnostics import peaks_and_primary
from annni.stage6_reference import record
f=json.loads((OUT/'confirmation/method_frozen.json').read_text());windows=json.loads((OUT/'reference_atlas/window_reference.json').read_text());rows=[]
for window in windows:
 if window['kappa'] not in [.45,.55,.8]:continue
 k=window['kappa'];h=np.array(window['h']);ed=[np.load(ROOT/record(8,k,float(x))['archive'])['state'] for x in h];ef=np.array([abs(np.vdot(a,b))**2 for a,b in zip(ed[:-1],ed[1:])]);echi=-np.log(np.clip(ef,1e-300,1))/np.diff(h)**2;reference=peaks_and_primary(h,echi)
 for method in ['B3',f['physical_method']]:
  arms=[load(k,float(x),method,task='windows') for x in h]
  for p in [0,.01,.05]:
   guard();rs=[physical(a,p,keep=True)[1] for a in arms];matrices=[np.load(ROOT/r['archive'])['rho'] for r in rs];overlap=np.array([uhlmann_squared(a,b) for a,b in zip(matrices[:-1],matrices[1:])]);chi=-np.log(np.maximum(overlap,1e-300))/np.diff(h)**2;peak=peaks_and_primary(h,chi);r=peak['primary'];ref=reference['primary'];structure_changes=[a['gates']!=b['gates'] for a,b in zip(arms[:-1],arms[1:])];topology=lambda arm:[tuple(g if g[0]=='CNOT' else g[:2]) for g in arm['gates']];topology_changes=[topology(a)!=topology(b) for a,b in zip(arms[:-1],arms[1:])];rows.append(dict(n=8,kappa=k,method=method,p=p,h=h,h_mid=(h[:-1]+h[1:])/2,fidelity_squared=overlap,chi=chi,ED_chi=echi,peak=peak,ED_peak=reference,position_error=float(r['coordinate']-ref['coordinate']) if r and ref else None,source_records=rs,structure_or_parameter_changes=structure_changes,gate_topology_changes=topology_changes,measurement_resource='Full density matrices and eigen/SVD computations; NOT included in local10k/100k-shot classification budget',quality_policy='Unmasked raw curves retained, actual selected-reference branch comparisons saved separately; no opposite-direction proxy'))
   dump(OUT/'end_to_end/D2_full_state_windows.json',rows);print('D2',k,method,p,flush=True)
import subprocess
subprocess.run([sys.executable,'scripts/plot_stage6_d2_windows.py'],check=True,cwd=ROOT)
