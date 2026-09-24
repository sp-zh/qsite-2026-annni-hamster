"""Build a data-backed report and execute the baseline reader notebook."""
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.mplconfig'))
os.environ.setdefault('JUPYTER_RUNTIME_DIR','/tmp/quantum-jupyter-runtime')
os.environ.setdefault('IPYTHONDIR','/tmp/quantum-ipython')
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
import csv
import json
import nbformat
from nbclient import NotebookClient

out=ROOT/'results/baseline'
metadata=json.loads((out/'metadata.json').read_text())
peaks=list(csv.DictReader((out/'diagnostic_peaks.csv').open()))
table='| N | κ | 序参量负导数峰 h | 保真度峰 h |\n|---:|---:|---:|---:|\n'
for row in peaks:
    table+=f"| {row['n']} | {float(row['kappa']):.1f} | {float(row['derivative_peak_h']):.3f} | {float(row['fidelity_peak_h']):.3f} |\n"
comparison='| N | C(2) |\n|---:|---:|\n'
for row in metadata['commensurability_check']:
    comparison+=f"| {row['n']} | {row['c2']:.9f} |\n"
report=f"""# 无噪声基线实验结果

本次完成了 **815 次参数点计算**（包含不同扫描间的重复点）：
N=8 的 21×21 全网格、N=8/12/16 的三条 41 点切片，以及五个尺寸相容性对照点。
运行时间约 {metadata['elapsed_seconds']:.2f} 秒（不含环境安装、测试和 notebook 执行）。
上游版本为 {metadata['upstream']['commit']}，没有修改上游代码。

## 数值可信度

全部扫描的最大本征残差为 **{metadata['max_residual']:.3e}**。
13 项自动化测试通过，覆盖上游 PennyLane Hamiltonian 的逐元素比较、
小尺寸密集本征分解、有限周期 Ising 链的解析基态能量、经典铁磁与反相极限、
结构因子背景与和规则、低场平移对称性和保真度约定。

仅有小残差不足以排除近简并态混合。第一轮随机初始向量使 N=16 低场保真度出现伪尖峰；
最终实现使用均匀正初始向量，并投影到零动量，再重新计算能量与残差。
已重新生成本目录全部扫描数据和图表。

## 首轮发现

1. **Ising 极限自洽。** κ=0 时，序参量导数峰随 N 从 8 增加到 12/16，
   由网格上的 h=0.95 移至 h=1.00；保真度峰由 0.925 移至 0.975，
   与热力学极限 h=1 的位置相容。这里没有对峰位置做连续拟合。
2. **反相区对尺寸更敏感。** κ=0.8 的导数峰由 N=8 的 0.60 变为 N=16 的 0.45。
   这表明不能用单个小尺寸峰位置作为最终相边界；本轮没有做热力学外推或确认 floating phase。
3. **周期相容性对照复现。** 固定 (κ,h)=(0.8,0.2) 时：

{comparison}

N=8、12、16 的 C(2) 接近 −1；N=6、10 因周期环不能无缺陷容纳四周期图案而差异明显。
因此主要尺寸比较使用 4 的倍数。

## 有限尺寸诊断峰

{table}

切片步长为 0.05。保真度定义在相邻 h 的**中点**，所以表中的 0.425、0.975 等值
不表示精确到了 0.001。导数计算排除 h=0 的混合态端点。
此表仅列全切片上的最大峰；没有把一个峰强行对应到两条反相/floating/顺磁边界。
下一阶段需局部加密并比较多个诊断量，不能把这里的网格峰位置当成已验证的四相分类。

## 图表

![N=8 诊断图](ed_n8_maps.png)

![有限尺寸切片](finite_size_slices.png)

## 解释边界及下一步

- h=0 使用所有经典最低能量构型的等权非相干混合；特别在 κ=0.5，不声称它等于 h→0+ 极限。
- 结构因子包含 1/N 自关联背景；不能用严格大于零作为有序相判据。
- 本轮只有 ED。没有完成 VQE、p=0.01/0.05 的门噪声实验、ZNE 或最终比赛报告。
- 下一步先在代表点校准参数化制态电路，同时检查能量、结构因子与保真度；
  达标后固定参数比较三个噪声水平，以分离制态误差和门噪声误差。

原始数据见本目录的 CSV/NPZ；环境版本、模型约定、代码 SHA256 和上游来源见 metadata.json。
"""
(out/'REPORT.md').write_text(report)

nb=nbformat.v4.new_notebook()
md=nbformat.v4.new_markdown_cell
code=nbformat.v4.new_code_cell
nb.cells=[
md("""# ANNNI：无噪声精确解基线

读取已保存的 21×21 主网格与 N=8/12/16 切片，并重新求解一个代表点。
这是含噪电路实验的校准参考，尚不是完整的比赛 submission。
完整实验实现位于 annni/model.py 和 scripts/run_baseline.py。"""),
code("""from pathlib import Path
import csv, json, sys, hashlib
import numpy as np
from IPython.display import display, Image, Markdown
ROOT = Path.cwd()
assert (ROOT / 'annni/model.py').exists(), '请从项目根目录运行 notebook'
sys.path.insert(0, str(ROOT))
from annni.model import Chain
OUT = ROOT / 'results/baseline'
metadata = json.loads((OUT / 'metadata.json').read_text())
for path, expected in metadata['source_sha256'].items():
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, f'源码已改变，请重跑扫描: {path}'
print('Python:', sys.version.split()[0])
print('上游 commit:', metadata['upstream']['commit'])
print('计算点次:', metadata['point_count'])
print('最大残差:', metadata['max_residual'])"""),
md(r"""## 模型与对称性

周期边界，最近邻耦合为 1：
$$H=-\sum_i Z_iZ_{i+1}+\kappa\sum_i Z_iZ_{i+2}-h\sum_iX_i.$$

h>0 在全局翻转偶扇区求解，并保持零动量；h=0 采用简并经典基态的等权混合。
后者没有唯一纯态，所以不用于相邻点保真度。"""),
code("""chain = Chain(8)
result = chain.ground_state(kappa=0.8, h=0.2)
obs = chain.observables(result)
for key in ['energy_per_site', 'mx', 'c1', 'c2', 'm2_ferro', 'm2_antiphase', 'residual']:
    print(f'{key}: {obs[key]:.12g}')
assert abs(obs['energy_per_site'] - (-obs['c1'] + 0.8*obs['c2'] - 0.2*obs['mx'])) < 1e-10"""),
md("""## N=8 全网格

数组维度为 [κ,h,...]；结构因子包含 1/N 背景。
这些图显示可观测量，不预先赋予四种相标签。"""),
code("""grid = np.load(OUT / 'grid_n8.npz')
assert grid['energy_per_site'].shape == (21,21)
assert np.isnan(grid['states'][:,0]).all()
assert np.isnan(grid['chi_f'][:,0]).all()
np.testing.assert_allclose(grid['structure_factor'].sum(axis=-1), 1, atol=1e-10)
display(Image(filename=str(OUT / 'ed_n8_maps.png')))"""),
md(r"""## 尺寸切片与诊断峰

保真度指标采用 $-\log F/\Delta h^2$，$F=|\langle\psi(h)|\psi(h+\Delta h)\rangle|^2$。
峰值位于区间中点；步长 0.05 不支持千分之一精度的边界声明。"""),
code("""display(Image(filename=str(OUT / 'finite_size_slices.png')))
rows = list(csv.DictReader((OUT / 'diagnostic_peaks.csv').open()))
table = '| N | κ | 导数峰 h | 保真度峰 h |\\n|---:|---:|---:|---:|\\n'
for row in rows:
    table += f"| {row['n']} | {float(row['kappa']):.1f} | {float(row['derivative_peak_h']):.3f} | {float(row['fidelity_peak_h']):.3f} |\\n"
display(Markdown(table))"""),
md("""## 复算全部实验

在项目根目录使用 .venv/bin/python 执行 scripts/run_baseline.py，再执行 scripts/build_notebook.py。
设置 OPENBLAS_NUM_THREADS=1 和 OMP_NUM_THREADS=1，避免小矩阵计算的线程开销。

下一步：代表点 VQE 制态校准，再固定参数施加 CNOT 后目标位退极化噪声。
本 notebook 没有把 ED 图充当含噪电路图，也不确认 floating phase。""")]
nb.metadata['kernelspec']={'display_name':'Python 3 (annni .venv)','language':'python','name':'python3'}
nbformat.validate(nb)
NotebookClient(nb,timeout=120,kernel_name='python3',resources={'metadata':{'path':str(ROOT)}}).execute()
nbformat.write(nb,ROOT/'baseline.ipynb')
print('Created REPORT.md and executed baseline.ipynb')
