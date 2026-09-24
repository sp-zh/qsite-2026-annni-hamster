"""Execute notebook: historical data read + one fresh lightweight optimization."""
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.mplconfig'))
os.environ.setdefault('JUPYTER_RUNTIME_DIR','/tmp/quantum-jupyter-runtime')
os.environ.setdefault('IPYTHONDIR','/tmp/quantum-ipython')
import nbformat
from nbclient import NotebookClient
nb=nbformat.v4.new_notebook()
md=nbformat.v4.new_markdown_cell
code=nbformat.v4.new_code_cell
nb.cells=[
md("""# ANNNI Stage 2：VQE 校准、诊断与逐门噪声

**完整含噪全网格：NO-GO。** 本轮实际保存 195 次能量优化，14/15 点至少 2/3 轨迹达标；
(.3,.4) 仍不稳定。5 点 × 3 噪声水平全部执行，但深电路在 p=.05 接近混合态。

下文明确区分**读取的历史实验结果**与**本 notebook 新执行的一次轻量优化**。
完整运行日志、初始/最终参数和失败结果均保留；没有重新运行全 ED 基线。"""),
md("""## Context & Methods

N=8 周期 ANNNI；|+〉起态。每层按 NN IsingZZ(2γ)、NNN IsingZZ(2η)、RX(2β) 顺序。
所有 NN/NNN 逻辑边直接可用，无 SWAP；wire 0 为最高位。
能量优化采用解析伴随梯度，已与 PennyLane 自动微分及有限差分核对。

### Key Assumptions

shots=None；ED 只作验证，没有 StatePrep 主制态或输出投影。
结构因子保留 1/N 背景；χF 在 h_mid，h=0 的缺失纯态不填补。
L8 是独立种子各自 L6 轨迹的补救延续，不能称为三次全新随机重启。
验收门槛是工程配置，不是官方评分或热力学相图准确性保证。"""),
code("""from pathlib import Path
import sys, json, csv, hashlib
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, Markdown, Image
ROOT=Path.cwd()
assert (ROOT/'annni/circuits.py').exists(), '从项目根目录运行'
sys.path.insert(0,str(ROOT))
from annni.circuits import HVAEngine, qnode, observe
from annni.vqe import optimize, metrics
from annni.diagnostics import diagnose
OUT=ROOT/'results/calibration_v1'
manifest=json.loads((OUT/'run_manifest.json').read_text())
for path, expected in manifest['hashes'].items():
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected, path
cfg=manifest['configuration']
rows=[json.loads(p.read_text()) for p in sorted((OUT/'runs').glob('*.json'))]
summary=json.loads((OUT/'summary.json').read_text())
selected=json.loads((OUT/'selected.json').read_text())
plt.rcParams.update({'figure.figsize':(9,4), 'font.size':11, 'axes.spines.top':False, 'axes.spines.right':False})
print('Historical runs:',len(rows),'stable points:',len(selected),'/ 15')
print('All raw data and config/code hashes checked.')"""),
md("""## Data — 历史运行数据

参数初始化 seeds=11/23/37；L=1,2,4,6 各45次，L8仅5个预先触发补救点共15次。
同一点、同一深度按能量最小选择；每组全部指标的最好/中位数/最差值在 summary.csv。
下表是完整15点的联合验收通过数，不是优化器收敛数。"""),
code("""table='|κ|h|L1|L2|L4|L6|L8补救|\\n|---:|---:|---:|---:|---:|---:|---:|\\n'
for i,(k,h) in enumerate(cfg['points']):
    cells=[]
    for L in [1,2,4,6,8]:
        g=[s for s in summary if s['point']==i and s['layers']==L]
        cells.append(f"{g[0]['joint_pass_count']}/3" if g else '未运行')
    table+=f'|{k}|{h}|'+ '|'.join(cells)+'|\\n'
display(Markdown(table))"""),
md("""## Results — 精度与稳定性

同样的能量目标可能收敛到不同的局部结果；优化成功不等于通过物理验收。
图中 L8 样本仅含失败点的补救，不能与此前所有点的总体平均直接比较。"""),
code("""fig,axs=plt.subplots(1,2,figsize=(11,4),layout='constrained')
for ax,key,threshold in zip(axs,['delta_e','epsilon_c'],[.001,.02]):
    for seed,color in [(11,'#2864aa'),(23,'#bd7920'),(37,'#8860a4')]:
        group=[r for r in rows if r['seed']==seed]
        ax.scatter([r['layers']+{11:-.07,23:0,37:.07}[seed] for r in group],
                   [max(r[key],1e-12) for r in group],s=14,alpha=.6,color=color,label=f'seed {seed}')
    ax.axhline(threshold,color='black',ls='--')
    ax.set(yscale='log',xlabel='Layers L',ylabel=key,xticks=[1,2,4,6,8])
axs[0].legend(fontsize=8)
plt.show()"""),
code("""# Exact saved per-seed acceptance display. Plot source: scripts/report_calibration.py.
display(Image(filename=str(OUT/'seed_stability.png')))"""),
md("""### 完整结构因子

所有离散波矢都比较；同一纵轴，不将理想反相 π/2 峰重新归一到1。
完整15点图由 scripts/report_calibration.py 生成。"""),
code("""display(Image(filename=str(OUT/'structure_factor_comparison.png')))"""),
md("""### 新执行的轻量检查：重新优化一个代表点

下面**重新执行** (κ,h)=(.8,.2)、L=2、seed=11 的能量优化，并验证 PennyLane 高层门输出。
它没有重跑195次历史优化，也没有更新历史记录。"""),
code("""point=9; L=2; seed=11
init=np.random.default_rng(np.random.SeedSequence([seed,point,L])).uniform(-.5,.5,(L,3))
status,params,state,trace=optimize(init,.8,.2,cfg['options'])
historical=np.load(OUT/'runs/p09_L2_s11.npz')
historical_row=next(r for r in rows if r['run_id']=='p09_L2_s11')
metric,obs,ref=metrics(state,historical['ed_state'],historical_row['ed_energy'],.8,.2,cfg['thresholds'])
np.testing.assert_allclose(state,qnode()(params),atol=1e-11)
assert metric['joint_pass']
assert abs(metric['energy']-historical_row['energy'])<1e-9
print('FRESH notebook optimization:', {k:metric[k] for k in ['delta_e','fidelity','epsilon_c','joint_pass']})
print('FRESH elapsed seconds:',status['seconds'],'iterations:',status['nit'])
print('Historical reproduction energy difference:',metric['energy']-historical_row['energy'])"""),
md("""### 全波矢诊断 — 历史 ED

全 q 图使用原始 baseline NPZ，不重新求解。
N12/N16 出现竞争模式超过 π/2，N8 未出现；这种尺寸依赖不够证明 floating phase。
主峰近峰、所有局部变化率峰及其分辨率区间见 diagnostics_v1 CSV。"""),
code("""fig,axs=plt.subplots(1,3,figsize=(12,4),layout='constrained')
for ax,n in zip(axs,[8,12,16]):
    d=np.load(ROOT/f'results/baseline/slices_n{n}.npz')
    ki=np.flatnonzero(np.isclose(d['kappa'],.8))[0]
    im=ax.pcolormesh(2*np.arange(n)/n,d['h'],d['structure_factor'][ki],shading='nearest',vmin=0,vmax=.5,cmap='viridis')
    ax.set(title=f'N={n}, κ=.8',xlabel='q / π',ylabel='h')
fig.colorbar(im,ax=axs,label='m²(q)',shrink=.8)
plt.show()
mixed=diagnose(np.ones(8)/8,0)
plus=diagnose(np.ones(8)/8,1)
assert mixed['label']=='degraded' and plus['label']=='paramagnetic_like'
print('Controls:',mixed['label'],plus['label'])"""),
md("""### 逐门噪声 — 读取实际执行的15次密度矩阵结果

每次 CNOT 后对 target 加指定退极化通道，包括 ZZ 分解中的两个 CNOT。
各 p 使用同一组理想参数；下面的 ED overlap 定义为 〈ψ_ED|ρ|ψ_ED〉。
不同点的层数不同，所以不据此排名各相的内在脆弱性。"""),
code("""noise=list(csv.DictReader((ROOT/'results/noise_smoke_v1/observations.csv').open()))
fig,axs=plt.subplots(1,2,figsize=(11,4),layout='constrained')
colors=['#2864aa','#bd7920','#8860a4','#65885c','#b66489']
for point,color in zip([0,4,9,11,14],colors):
    group=[r for r in noise if int(r['point'])==point]
    label=f"κ={group[0]['kappa']},h={group[0]['h']},L={group[0]['layers']}"
    for ax,key in zip(axs,['ed_fidelity','purity']):
        ax.plot([float(r['p']) for r in group],[float(r[key]) for r in group],'o-',color=color,label=label)
        ax.set(xlabel='p per CNOT target',ylabel=key,ylim=(0,1.02))
axs[1].axhline(1/256,color='black',ls=':',lw=1)
axs[0].legend(fontsize=8)
plt.show()"""),
md("""## Takeaways

**完整21×21含噪扫描暂为 NO-GO。** 尚需解决 (.3,.4) 的稳定性与较深电路累积噪声。
已有14点的可用参数不丢弃，可供有限切片与资源改进对照。当前没有一个统一深度通过全部15点。
所有失败、迭代上限退出、结构因子/关联误差都保留；没有用事后子空间扩张掩盖低保真度。

诊断协议 v1 已冻结，输出 continuous features、finite-size peaks 和 uncertain/degraded。
本轮不声称确认 floating phase 或测出真实相边界移动。

复现命令、完整测试、配置与哈希见 results/calibration_v1/REPORT.md。
configs/next_stage_proposal.json 只是下一轮建议，尚未执行。""")]
nb.metadata['kernelspec']={'display_name':'Python 3 (locked .venv)','language':'python','name':'python3'}
nbformat.validate(nb)
NotebookClient(nb,timeout=120,kernel_name='python3',resources={'metadata':{'path':str(ROOT)}}).execute()
nbformat.write(nb,ROOT/'calibration.ipynb')
print('calibration.ipynb executed and saved')
