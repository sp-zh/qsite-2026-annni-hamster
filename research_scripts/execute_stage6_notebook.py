import sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from annni.stage6_common import *
path=OUT/'report/stage6_research.ipynb';book=nbformat.read(path,as_version=4);manager=KernelManager(kernel_name='python3');manager.kernel_spec.argv=[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'];start=time.perf_counter();client=NotebookClient(book,km=manager,timeout=180,resources={'metadata':{'path':str(ROOT)}})
client.execute();manager.shutdown_kernel(now=True);nbformat.validate(book);nbformat.write(book,path)
dump(OUT/'verification/notebook_execution.json',dict(executed_utc=datetime.now(timezone.utc).isoformat(),seconds=time.perf_counter()-start,python=sys.executable,archive=str(path.relative_to(ROOT)),sha256=sha(path),code_cells=sum(c.cell_type=='code' for c in book.cells),errors=[o for c in book.cells if c.cell_type=='code' for o in c.get('outputs',[]) if o.output_type=='error'],scope='Top-to-bottom locked-Python execution; historical saved results plus one current literal gate/state/energy check. No complete optimization rerun.'))
print('Executed',path)
