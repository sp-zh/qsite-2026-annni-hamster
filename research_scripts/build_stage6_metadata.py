"""Assemble provenance from actual indices; run after final analyses/verification."""
import sys,platform,importlib.metadata
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
def read(rel):
 p=OUT/rel
 return json.loads(p.read_text()) if p.exists() else None
files=[]
for folder in ['annni','scripts','tests','configs']:
 files += [p for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix in ['.py','.sh','.json'] and '__pycache__' not in p.parts]
code={str(p.relative_to(ROOT)):sha(p) for p in sorted(files)}
inputs={}
for rel in ['upstream/PROVENANCE.json','results/baseline/metadata.json','results/baseline/grid_n8.npz','results/baseline/slices_n8.npz','results/baseline/slices_n12.npz','results/baseline/slices_n16.npz','requirements.lock.txt','requirements-tn.lock.txt']:
 p=ROOT/rel
 if p.exists():inputs[rel]=dict(sha256=sha(p),bytes=p.stat().st_size)
progresses={p.stem:json.loads(p.read_text()) for p in sorted((OUT/'verification').glob('progress_*.json'))}
failures={str(p.relative_to(OUT)):json.loads(p.read_text()) for p in OUT.rglob('*failures.json')}
result=dict(run_id=PLAN['run_id'],generated_utc=datetime.now(timezone.utc).isoformat(),started_utc=PLAN['started_utc'],deadline=PLAN['deadline'],elapsed_wall_seconds=(datetime.now(timezone.utc)-datetime.fromisoformat(PLAN['started_utc'])).total_seconds(),environment=read('verification/environment.json'),current_python=sys.version,current_platform=platform.platform(),actual_versions={name:importlib.metadata.version(name) for name in ['numpy','scipy','pennylane','matplotlib','nbformat','nbclient']},code_sha256=code,baseline_inputs=inputs,all_protected_input_verification=read('verification/protected_inputs_verified.json'),scientific_payload_hash_verification=read('verification/artifact_hash_verification.json'),experiment_plan=PLAN,frozen_method=read('confirmation/method_frozen.json'),frozen_mitigation=read('end_to_end/mitigation_frozen.json'),stability_execution=read('confirmation/stability_execution_protocol.json'),resource_summary=read('verification/resource_summary.json'),sleep_resume=read('verification/system_sleep_resume.json'),progress=progresses,failures=failures,decision=read('decision.json'),model=dict(hamiltonian='-sum ZiZi+1 + kappa sum ZiZi+2 - h sum Xi',J1=1,main_bc='PBC',main_n=[8,12],large_n_bc='OBC',basis='wire0 most significant bit; array axes kappa,h',structure_factor='1/N² sumij exp(iq(i-j)) <ZiZj>, all q=2pi k/N including i=j background1/N',h_zero='Classical incoherent mixture preserved; no pure-state fidelity across h=0; main circuits at h>0',fidelity='Squared overlap with same-N ED state; sector gaps are distinguished from full-space cat splitting'),circuit=dict(primary='Energy-only physical/wall ADAPT; H6 frozen regional union selects one actual circuit',wall_encoding='y0=b0,yj=b(j-1) XOR bj; final wall parity XOR(y1..); even total walls',decode='Ordered CNOT(0,1),...,(N-2,N-1), charged and noisy',top4='Four bounded optimized proposals per growth step; full400-iteration fit, max160parameters',connectivity='Direct periodic NN and NNN only; no inherited20qubit routing graph',noise='After every literal CNOT on target only: Dp=(1-p)rho+p/3(XrhoX+YrhoY+ZrhoZ)',fold='Each CNOT repeated1/3/5, including reference/decode; all counted',SV='Signed (O+OP)/(1+P), no clipping; additional settings charged',selection='Energy/resource only; no ED target in deployed generation/selection; oracle fits isolated development diagnostics'),provenance_scope='Original Stage3–5/upstream remain read-only. Full coordinates and scientific configuration hashes key caches. All saved raw candidate/measurement records retain source keys and archive hashes. Historical reused, newly executed and implemented-not-run are distinguished in EVIDENCE_LEDGER.',timing_scope='Raw elapsed timings overlapping OS sleep are preserved and flagged, not retrospectively subtracted. Summed worker timings differ from wall-clock time. No QPU or paid cloud resource was used.')
result['document_runtime']=read('verification/document_runtime.json')
result['N12_density_actual_cost']=read('n12_transfer/density_actual_cost.json')
result['derived_analysis_corrections']={name:read('verification/'+name) for name in ['confirmation_prefix_race_correction.json','detector_boundary_denominator_fix.json','resource_coordinate_scope_v2.json','evidence_denominator_correction.json']}
dump(OUT/'metadata.json',result);print('metadata assembled with',len(code),'code/config hashes')
