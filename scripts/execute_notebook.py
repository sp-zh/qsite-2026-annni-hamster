import sys,json,time,os,copy,re,base64,io
from pathlib import Path
import nbformat
from nbclient import NotebookClient
try:
 from nbconvert import HTMLExporter
except ImportError:
 HTMLExporter=None
R=Path(__file__).resolve().parents[1];out=R/'build/executed';out.mkdir(parents=True,exist_ok=True)
# A private kernelspec pins execution to this Python, rather than a user's default kernel.
k=out/'kernels/release-python';k.mkdir(parents=True,exist_ok=True);(k/'kernel.json').write_text(json.dumps(dict(argv=[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],display_name='Release Python',language='python')))
os.environ['JUPYTER_PATH']=str(out);os.environ['PYTHONPATH']='';os.environ['MPLCONFIGDIR']=str(R/'build/matplotlib');os.environ['XDG_CACHE_HOME']=str(R/'build/cache')
n=nbformat.read(R/'submission.ipynb',as_version=4);t=time.perf_counter();NotebookClient(n,timeout=240,kernel_name='release-python',resources={'metadata':{'path':str(R)}}).execute();nbformat.write(n,out/'submission.ipynb')
if HTMLExporter is not None:
 # Static formula images make the HTML readable without a remote MathJax runtime.
 import matplotlib.mathtext as mathtext
 offline=copy.deepcopy(n)
 def render_math(match):
  formula=match.group(0).strip('$').replace('\\frac p3','\\frac{p}{3}')
  buf=io.BytesIO();mathtext.math_to_image('$'+formula+'$',buf,format='png',dpi=150)
  encoded=base64.b64encode(buf.getvalue()).decode()
  return '<img alt="'+formula.replace('"','&quot;')+'" style="max-width:100%;vertical-align:middle" src="data:image/png;base64,'+encoded+'" />'
 for cell in offline.cells:
  if cell.cell_type=='markdown':cell.source=re.sub(r'\$\$[\s\S]*?\$\$|(?<!\$)\$[^$\n]+\$(?!\$)',render_math,cell.source)
 html,_=HTMLExporter().from_notebook_node(offline)
 html=re.sub(r'<script\b[^>]*>[\s\S]*?</script>','',html,flags=re.I)
 (out/'submission.html').write_text(html)
else:
 (out/'submission.html').unlink(missing_ok=True)
(out/'receipt.json').write_text(json.dumps(dict(status='PASS',html_export='PASS' if HTMLExporter is not None else 'SKIPPED_DEPENDENCY',seconds=time.perf_counter()-t,python=sys.version,code_cells=sum(c.cell_type=='code' for c in n.cells),errors=sum(o.get('output_type')=='error' for c in n.cells if c.cell_type=='code' for o in c.outputs)),indent=2));print((out/'receipt.json').read_text())
