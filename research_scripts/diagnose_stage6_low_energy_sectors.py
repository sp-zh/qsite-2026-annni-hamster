"""Resolve parity/translation near-doublets without changing the target-state gate."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.upgrade_gates import geometry,diagonals,h_action
from annni.stage6_reference import record
from scipy.sparse import coo_matrix,diags
points=[(.525,.035),(.55,.05),(.55,.15),(.45,.15),(.8,.6)];dev=json.loads((OUT/'domain_wall_candidates/development_101_0_index.json').read_text());rows=[];n=8;ids,z,flips=geometry(n);size=1<<(n-1);reps=ids[:size];nn,nnn,_=diagonals(n);shift=((ids<<1)&((1<<n)-1))|(ids>>(n-1))
protocol=dict(points=points,parity_blocks=[1,-1],levels_per_block=8,diagnostic_energy_window_absolute=1e-4,meaning='Optional fixed absolute low-energy weight diagnostic only. Original F_ED>=.99 and joint thresholds remain unchanged. Compare energy splitting against residual and third-level separation; no phase boundary from minimum full-space gap.',timestamp=datetime.now(timezone.utc).isoformat())
dump(OUT/'failure_mechanisms/low_energy_sector_protocol.json',protocol)
for k,h in points:
 r=next(r for r in dev if r['kappa']==k and r['h']==h)['methods']['C3']['selected'];candidate=np.load(ROOT/r['archive'])['state'];reference=record(n,k,h);s0=np.load(ROOT/reference['archive'])['state'];blocks=[]
 for parity in [1,-1]:
  raw=np.concatenate([f[:size] for f in flips]);target=np.minimum(raw,((1<<n)-1)^raw);weights=np.where(raw>=size,parity,1);x=coo_matrix((weights,(target,np.tile(reps,n))),shape=(size,size)).toarray();matrix=np.diag((-nn+k*nnn)[:size])-h*x;energies,states=np.linalg.eigh(matrix);states=np.concatenate([states,parity*states[::-1]],axis=0)/np.sqrt(2);levels=[]
  for j in range(8):
   s=states[:,j];levels.append(dict(energy=float(energies[j]),delta_from_ED=float(energies[j]-reference['energy']),residual=float(np.linalg.norm(h_action(s,n,k,h)-energies[j]*s)),translation_real=float(np.vdot(s,s[shift]).real),translation_imag=float(np.vdot(s,s[shift]).imag),candidate_overlap=float(abs(np.vdot(s,candidate))**2),ED_overlap=float(abs(np.vdot(s,s0))**2)))
  blocks.append(dict(parity=parity,levels=levels,candidate_fixed_window_weight=float(np.sum(abs(states[:,energies<=reference['energy']+1e-4].conj().T@candidate)**2))))
  if parity==1:assert abs(energies[0]-reference['energy'])<1e-10 and abs(np.vdot(states[:,0],s0))**2>1-1e-9
 rows.append(dict(kappa=k,h=h,candidate_source=r['archive'],ED_source=reference['archive'],candidate_F_ED=float(abs(np.vdot(candidate,s0))**2),original_state_pass=bool(abs(np.vdot(candidate,s0))**2>=.99),blocks=blocks));dump(OUT/'failure_mechanisms/low_energy_sectors.json',rows)
 print(k,h,'gap+',blocks[0]['levels'][1]['delta_from_ED'],'weights',[x['candidate_overlap'] for x in blocks[0]['levels'][:3]],flush=True)
