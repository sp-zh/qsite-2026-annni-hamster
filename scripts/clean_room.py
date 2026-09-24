"""Run inside an extracted package. No source-export or research computation."""
import os,sys,json,subprocess,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];os.chdir(R)
# Launcher must supply explicit historical root to deny, not a scientific data input.
forbid=os.environ.get('ANNNI_FORBID_HISTORY');assert forbid,'Set ANNNI_FORBID_HISTORY to original workspace root'
os.environ.pop('PYTHONPATH',None);os.environ.pop('PYTHONHOME',None)
os.environ['MPLCONFIGDIR']=str(R/'build/matplotlib');os.environ['XDG_CACHE_HOME']=str(R/'build/cache');os.environ['IPYTHONDIR']=str(R/'build/ipython');os.environ['OPENBLAS_NUM_THREADS']='1'
for name,subdir in [('JUPYTER_CONFIG_DIR','jupyter_config'),('JUPYTER_DATA_DIR','jupyter_data'),('JUPYTER_RUNTIME_DIR','jupyter_runtime')]:os.environ[name]=str(R/'build'/subdir)
keep=['PATH','LANG','LC_ALL','TMPDIR','ANNNI_FORBID_HISTORY','MPLCONFIGDIR','XDG_CACHE_HOME','IPYTHONDIR','OPENBLAS_NUM_THREADS','JUPYTER_CONFIG_DIR','JUPYTER_DATA_DIR','JUPYTER_RUNTIME_DIR']
child_env={k:os.environ[k] for k in keep if k in os.environ}
sys.path.insert(0,str(R/'scripts'));import release
out=R/'build/clean_receipt';out.mkdir(parents=True,exist_ok=True);start=time.perf_counter()
try:open(Path(forbid)/'README.md').read()
except PermissionError:blocked=True
else:raise AssertionError('Historical read barrier did not work')
commands=[['scripts/release.py','verify-data','--out','build/clean_receipt'],['scripts/release.py','verify-physics','--quick','--out','build/clean_receipt'],['scripts/release.py','verify-exact-replay','--out','build/clean_receipt'],['scripts/execute_notebook.py']]
import importlib.util
if importlib.util.find_spec('pennylane') is not None:commands[1].append('--sdk')
for i,cmd in enumerate(commands):
 with (out/f'command_{i}.log').open('w') as f:subprocess.run([sys.executable,*cmd],cwd=R,env=child_env,stdout=f,stderr=subprocess.STDOUT,check=True)
# Notebook writes only build; verify immutable manifest after full execution.
for rel,h in release.read('package_manifest.json')['files'].items():assert release.sha(release.path(rel))==h,rel
receipt=dict(status='PASS',environment=release.env(),history_read_probe='DENIED',allowed_external='Declared installed Python environment/system libraries only; no historical scientific inputs',PYTHONPATH='cleared',commands=commands,notebook=release.read('build/executed/receipt.json'),exact_rng_replay=release.read('build/clean_receipt/verify_exact_replay.json')['status'],manifest_unchanged=True,HTML_regenerated=(R/'build/executed/submission.html').exists(),seconds=time.perf_counter()-start)
release.dump(out/'clean_room_receipt.json',receipt);print(json.dumps(receipt,indent=2))
