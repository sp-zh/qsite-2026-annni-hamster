import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('OMP_NUM_THREADS','1');os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.mplconfig'))
os.environ.setdefault('JUPYTER_RUNTIME_DIR','/tmp/annni-stage3-jupyter');os.environ.setdefault('IPYTHONDIR','/tmp/annni-stage3-ipython')
import nbformat
from nbclient import NotebookClient
nb=nbformat.v4.new_notebook();md=nbformat.v4.new_markdown_cell;code=nbformat.v4.new_code_cell
nb.cells=[md('''# ANNNI Stage 3：受控深度与门噪声实验

**实测摘要：**固定L6的目标点延续3/3通过，独立冷启动4/6；三条切片获选状态120/120通过。A/B/C及条件正场网格的实际完成数见下方读取的decision。
没有互补指标共同支持的非零边界位移，不宣称四相分类。

## Context & Methods
N=8，周期边界，H=-ΣZZ+κΣZZ_NNN-hΣX。|+〉初态；每层NN ZZ、NNN ZZ、RX，角度均为2倍参数。每个实际CNOT后在target施加规定DepolarizingChannel；shots=None，完整256维密度矩阵。

### Key Assumptions
不删除零角度门，不做对称投影。结构因子含1/8自关联；h=0未纳入VQE，不填补缺失点。成功率区分独立冷启动和多链最低能量选择。'''),code('''from pathlib import Path
import sys,json,hashlib,numpy as np
from IPython.display import display,Markdown,Image
ROOT=Path.cwd();sys.path.insert(0,str(ROOT))
OUT=ROOT/'results/stage3_v1'
manifest=json.loads((OUT/'manifest.json').read_text())
for p,digest in manifest['fingerprint']['sources'].items():
    assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest,p
decision=json.loads((OUT/'decision.json').read_text())
print('Historical slice execution:', decision['slice_execution_status'])
print('Historical grid execution:', decision['grid_execution_status'])
print('Historical coverage:',decision['optimization_coverage'])'''),md('''## Data — 读取已保存的运行结果
以下图表读取历史扫描数据，不会重新进行全部优化。参数初值、全部失败及每个p的数据可从CSV/NPZ追溯。'''),code('''import csv
rows=list(csv.DictReader((OUT/'optimization/A_summary.csv').open()))
text='|组|h|通过/运行|δe中位数|F中位数|\\n|---|---|---|---|---|\\n'
for r in rows[:4]:
    text+=f"|{r['group']}|{r['h']}|{r['joint_pass']}/{r['runs']}|{float(r['median_delta_e']):.3g}|{float(r['median_fidelity']):.6f}|\\n"
display(Markdown(text))'''),md('## Results — 配对实验与完整切片'),code("display(Image(filename=str(OUT/'figures/matched_depth_noise.png'),width=1000))\ndisplay(Image(filename=str(OUT/'figures/slices_order.png'),width=1000))"),md('## Fresh validation — 本 notebook 现场重新计算'),code('''from annni.stage3 import dense_literal
from annni.circuits import HVAEngine,observe
from annni.noise import noisy_density,density_checks
rows=json.loads((OUT/'matched_noise/selection_frozen.json').read_text())['rows']
r=next(r for r in rows if r['layers']==2)
d=np.load(ROOT/r['archive']);theta=d['final_params']
psi=HVAEngine().state(theta);rho0=dense_literal(theta,0)
rho=dense_literal(theta,.01);qmlrho=noisy_density(theta,.01)
np.testing.assert_allclose(rho0,np.outer(psi,psi.conj()),atol=1e-11)
np.testing.assert_allclose(rho,qmlrho,atol=2e-11)
o=observe(rho);checks=density_checks(rho)
print('FRESH recomputation: L=2 at',r['kappa'],r['h'])
print('PennyLane full-matrix max error:',np.max(abs(rho-qmlrho)))
print('purity:',checks['purity'],'C(0):',o['correlations'][0])
print('No optimization or full scan was re-executed by this notebook.')'''),md('''## Interpretation & Limits
匹配队列揭示理想精度和逐门噪声暴露之间的权衡；更深不保证含噪总误差更小。
原始曲线与质量掩码可以用于下一阶段分析；not_resolved不是零位移，单指标位移不是已验证的相边界。

## Reproduce
根目录运行 `bash scripts/reproduce_stage3.sh` 可校验数据并重建报告和此notebook。
`--compute`只在原预算与指纹内续算。所有详细失败、资源、网格范围和下一轮配置见results/stage3_v1/REPORT.md。''')]
nb.metadata['kernelspec']={'display_name':'Python 3','language':'python','name':'python3'}
NotebookClient(nb,timeout=120,resources={'metadata':{'path':str(ROOT)}}).execute()
nbformat.write(nb,ROOT/'stage3.ipynb')
# Portable HTML preview without optional nbconvert or dependency changes.
import html,re

def render_md(text):
    parts=[]
    for line in text.splitlines():
        if line.startswith('|'):
            if set(line.replace('|','').replace('-','').replace(':','').strip())==set():continue
            parts.append('<div class="table-row">'+' | '.join(html.escape(c.strip()) for c in line.strip('|').split('|'))+'</div>')
            continue
        m=re.match(r'^(#{1,6}) (.*)',line)
        if m:parts.append(f'<h{len(m[1])}>'+html.escape(m[2])+f'</h{len(m[1])}>')
        elif line.strip():parts.append('<p>'+html.escape(line)+'</p>')
    return '\n'.join(parts)
parts=['<!doctype html><meta charset="utf-8"><title>ANNNI Stage 3</title><style>body{max-width:1100px;margin:40px auto;padding:24px;font:16px/1.6 system-ui}pre{background:#f2f4f6;padding:16px;overflow:auto}img{max-width:100%}.table-row{font:14px/1.8 monospace}</style>']
for c in nb.cells:
    if c.cell_type=='markdown':parts.append(render_md(c.source))
    else:
        parts.append('<details><summary>Executed Python cell '+str(c.execution_count)+'</summary><pre>'+html.escape(c.source)+'</pre></details>')
        for out in c.get('outputs',[]):
            if out.output_type=='stream':parts.append('<pre>'+html.escape(out.text)+'</pre>')
            elif 'image/png' in out.get('data',{}):parts.append('<img alt="Executed experiment figure" src="data:image/png;base64,'+out.data['image/png']+'">')
            elif 'text/markdown' in out.get('data',{}):parts.append(render_md(out.data['text/markdown']))
            elif 'text/plain' in out.get('data',{}):parts.append('<pre>'+html.escape(out.data['text/plain'])+'</pre>')
(ROOT/'results/stage3_v1/notebook.html').write_text('\n'.join(parts))
print('Executed stage3.ipynb; HTML preview generated with standard library (nbconvert unavailable).')
