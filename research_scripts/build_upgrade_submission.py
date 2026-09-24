"""Executed report notebook and editable narrative, generated from measured results."""
import sys,json,platform,hashlib,textwrap
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import nbformat
from nbclient import NotebookClient
from annni.upgrade_adapt import *
S=OUT/'submission';stats=json.loads((S/'statistics.json').read_text());held=stats['heldout'];grid=stats['map']['B3'];n12=stats['n12']['B3'];cost=stats['cost'];floatgrade=json.loads((OUT/'floating/evidence_grading.json').read_text()) if (OUT/'floating/evidence_grading.json').exists() else {'rows':[]}
summary=f'''# 多参考自适应电路的 ANNNI 相特征研究

本轮实际完成 N=8 开发、留出与 420 点描述性网格；旧 Stage 3 保持历史基线。B3 的留出制态通过率为 **{held['B3']['passed']}/{held['B3']['points']}**，完整网格为 **{grid['passed']}/{grid['points']}**，获选 CNOT 中位数 **{grid['median_cnots']:g}**；历史 B0 为 407/420、固定 192 CNOT。这些是获选制态验收覆盖，不是相分类准确率。

N=12 新电路完成 {n12['points']} 个正场点，{n12['passed']} 个通过；另有 {stats.get('n12_noise',{}).get('configs',0)} 个规定噪声配置的精确密度矩阵模拟。动力学完成 {stats['dynamics']['configs']} 个配置，缓解完成 15 坐标 × 2 噪声水平 × 2 shots 预算 × 32 次独立测量重复。

## 方法与公平比较

周期 ANNNI，J1=1，wire0 为最高位。三种显式参考态（plus、GHZ+、四平移反相猫态）在每个点都测试。局域 YZ/ZY 与有界 YXZ/ZXY 池按梯度/CNOT 排序，逐门添加并重优化。总上限128 CNOT 包含参考态。停止和选择只用能量、梯度与资源；ED 只做事后误差诊断。B3 在候选最低能量每自旋1e-4容差内选最小资源电路。开发三种随机种子；冻结后全图每参考态一种种子，独立初始化。

B1 是 plus 单参考最大梯度方案；B2 是三参考固定短修正；B3 为主方案；B4 仅在同一 B3 电路的等价方向编译中，用额外 p=.01 能量计算选择方向。B4 使用噪声信息，单独计成本。未用 held-out ED 误差过滤或选择候选。旧 B0 的参数和编译不变。辅助 ED-oracle 性能不得混入主算法。

每个实际 CNOT 后只给 target 加 (1-p)rho+p/3(XrhoX+YrhoY+ZrhoZ)，p=0,.01,.05。所有参考制备与折叠门计费；NN/NNN 环连接，不引入20-qubit路由限制。噪声参数冻结于无噪声能量优化结果。逐分量 prep+noise=total，误差范数不可直接相加。

## 实测收益与保留的失败

| p | 全域平均最大关联误差 B0 → B3 | B3 改善点数 | 共同合格区域平均误差 B0 → B3 |
|---|---|---|---|
| .01 | {stats['matched']['B3_p0.01_all']['c_error_mean_old']:.4f} → {stats['matched']['B3_p0.01_all']['c_error_mean_new']:.4f} | {stats['matched']['B3_p0.01_all']['c_improved']}/420 | {stats['matched']['B3_p0.01_common_pass']['c_error_mean_old']:.4f} → {stats['matched']['B3_p0.01_common_pass']['c_error_mean_new']:.4f} |
| .05 | {stats['matched']['B3_p0.05_all']['c_error_mean_old']:.4f} → {stats['matched']['B3_p0.05_all']['c_error_mean_new']:.4f} | {stats['matched']['B3_p0.05_all']['c_improved']}/420 | {stats['matched']['B3_p0.05_common_pass']['c_error_mean_old']:.4f} → {stats['matched']['B3_p0.05_common_pass']['c_error_mean_new']:.4f} |

共同合格区域为383点。无噪声全域平均关联误差反而从B0的.00193升到B3的.00470，合格点从407降到385，说明少门数带来含噪收益，也损失制态精度。描述性分层中，p=.01低场h≤.5的105点均改善（均值.5614→.2498），高场h≥1.2的189点中172点改善（.1071→.0695）。这些分层在计算后用于解释，不是训练或选择规则。

B4的全域平均关联误差为p=.01时.1414、p=.05时.3644，较B3只小幅改善，不能把主收益归因于编译。冻结held-out上，单plus最大梯度B1通过33/48；同一plus参考改为成本排序通过{stats['factor_ablation']['heldout']['single_plus_cost_pass']}/48；再用多参考B3通过42/48。固定短修正B2只有4/48。消融支持参考态和自适应都重要，但不是完整因子实验或普适因果证明。

原15代表点中，逐seed执行冻结选择后有13点至少2/3通过；(.8,.6)为0/3，(.8,.8)为1/3。新增低场竞争点(.45,.15)、(.5,.15)、(.55,.15)均0/3。所有失败坐标与各项误差在statistics.json，不能用选出的一个好seed替代稳定性。

近简并held-out点(.975,.15)是具体反例：资源选择选中31-CNOT GHZ候选，F≈.50001；32-CNOT反相候选F≈.99999。冻结能量容差不能保证正确平移对称纯态，保留为失败；没有事后改规则或投影。ED-oracle只存为辅助上界。

固定结构κ=.3、anchor h=.5的局部案例，D1全物理量变化、|dMx/dh|和D2均在h=.45达到局部峰，三个p一致，峰网格支持[.4,.5]，用于检验局部峰的四点制态支持[.3,.6]均通过。位移分辨区间[-.1,.1]是网格差区间，不是统计置信区间。其他切片存在指标与分支分歧，不能外推成统一边界移动。

100k总shots时，p=.01的平均分量MSE为raw .02158、ZNE .01184、SV .01473；p=.05为.13592、.12922、.13190。以本电路p0为目标，低噪声改善较明显，高噪声远未恢复。有限shots及两个窗口的峰位置重复抽样已保存。

动力学在全部28组参数/初态上，dt=.05/.1/.2的平均最大无噪声误差为.00112/.00452/.01844；p=.01总误差反而为.5022/.4018/.2974。更细步长增加CNOT，当前噪声下抵消了Trotter精度收益。留出h=.6,1.4的冻结时间均值与静态关联已单独比较；只有四个留出坐标，不据相关系数宣称分类能力。

## 诊断与科学限度

D1 使用完整 C(r)、全部离散 SF 和 Mx 的参考态相似性及变化率；旧三特征原型仅是对照。D2 用平方纯态/平方 Uhlmann 保真度；需要模拟器态访问，不是免费硬件测量。D3 的标准化、PCA、聚类与解析控制映射仅由无噪声开发数据确定，之后冻结。分类器没有坐标、p、参考态或门数输入。B3全图中D1拒绝/退化计数为p0的16/420、p=.01的130/420、p=.05的413/420；D3分别为0、15、384。D3较少拒绝不等于更准确。p=.05虽有较低物理量误差，依然无法可靠恢复全图主要相特征。

三个主要标签是 ferro-like、antiphase-like、paramagnetic-like；degraded/uncertain 不属于新的物理相。没有独立精确有限网格相标签，因此不报告虚假的分类准确率；报告覆盖、拒绝、方法一致性和解析控制行为。保留红色制态失败标记。文献曲线仅为外部近似参照。结构切换审计比较真实双方在同一坐标的候选，另有固定结构切片与步长比较。

MPS 使用 TeNPy1.1.1，独立Python3.12环境、OBC、Pauli归一化、conserve=None；N8/12 Hamiltonian逐矩阵元素验证，随后N32粗扫描与N64/96、chi64/128/256复核。关联波矢、幂律/指数模型、纠缠熵和截断收敛共同审查，证据等级见floating/evidence_grading.json。三个中心(κ,h)=(.6,.2)、(.8,.5)、(1,.7)达到本轮supported_in_tested_window证据等级：N64/96两窗口拟合c分别覆盖约.969–1.068、.990–1.114、1.093–1.145；q约1.260–1.265、1.356–1.358、1.419–1.425。χ128→256的最大关联变化低于1.5e-6，独立初态也一致。等级阈值是公开的计算后证据审查，不是预注册物理判据；有限OBC拟合仍不能提供精确连续浮相区间。两侧点多为candidate，κ=.6,h=.1为not_resolved。small_periodic_bridge.json比较N8/12的有限离散SF和门噪声，未把大N标签移植到小N含噪图。PT与KT/BKT边界区别保留，上游命名问题未修改原快照。

ZNE全CNOT局部折叠1/3/5，线性截距为主、二阶Richardson另存，结果不裁剪。SV使用 (O+OP)/(1+P)，P为全X；ZZ乘P的负号保留。SV共30测量设置，raw2设置，ZNE6设置；总shots相同，门加权成本另报。整比特串联合样本保留关联量协方差。缓解目标为本电路p0，ED制态偏差另存。

二阶 B/2-A-B/2 动力学从全0和0011两个固定初态出发；所有参数均使用两者。t=0..2，dt=.2/.1/.05，公共输出间隔.2。精确演化、Trotter误差和逐门噪声分开。有限时间quench特征不是平衡相边界或热力学动力学相变。

## 资源、失败与复现

本轮唯一 ADAPT 运行 {cost['unique_adaptive_runs']} 次，累计函数内实测时间 {cost['adaptive_seconds']:.1f} 秒；任务之间曾并行，因此累计时间不是墙钟。当前统计墙钟 {cost['wall_elapsed_seconds']/60:.1f} 分钟；12小时是上限，非要求跑满。N12 31CNOT密度试算峰值约1.84GiB，后续单独串行。新环境与原锁文件独立，所有旧输入哈希复核。

所有失败、优化器退出、逐步参数、门表、随机种子、分支、缓存来源与数据哈希保留。参见 all_optimization_runs.csv、seed_stability.csv、matched_grid.csv、verification/、各工作包 index.json。新增测试覆盖梯度/基底/参考态、密度/轨道/门噪声、SV相位与shots、平方保真度、Trotter阶数及结果加载。数值截断、有限shots、优化不稳定、MPS截断和网格间隔分别解释。

复现命令（项目根目录）：
```sh
bash scripts/reproduce_upgrade.sh --verify
bash scripts/reproduce_upgrade.sh --report-only
bash scripts/reproduce_upgrade.sh --resume
```
resume 保留原deadline并校验键，不静默重置预算。Notebook读取保存结果，并现场重新计算一个轻量制态/噪声一致性检查。首次导出PDF需要单独reportlab/pypdf运行时，不升级科学环境。
'''
(S/'technical_report.md').write_text(summary);(OUT/'REPORT.md').write_text(summary)
# Machine-readable status describes executed evidence rather than algorithm names.
status=dict(main='CONDITIONAL GO',main_limit='Region-qualified diagnostic comparison only. NO-GO for a reliable p=.05 full phase reconstruction: D1 rejects/degrades413/420. Retain preparation failures, near-degeneracy and structure sensitivity; no global validated phase boundaries.',n8_grid=grid,heldout=held,n12=n12,bonus={
 'floating':dict(status='executed_inconclusive',scope='N32 coarse; N64/96, chi64/128/256, two initializations at centers',evidence=floatgrade['rows'],missing='No universal thermodynamic boundary or transfer of labels to noisy small N'),
 'N12':dict(status='validated_evidence',scope=stats.get('n12_noise',{}),limitation='Circuit/noise implementation validated; preparation failures retained, not complete phase classification'),
 'multiple_detection':dict(status='validated_evidence',scope='D1 full observables, D2 noisy Uhlmann slices, D3 frozen PCA+clustering; Binder and shot comparison',limitation='Independent finite-grid classification error is undefined without reliable external labels'),
 'mitigation':dict(status='validated_evidence',scope='15 coordinates, p=.01/.05, raw/ZNE/SV, 10k/100k shots and 32 repeats',limitation='Partial observable restoration; high-noise saturation, no guaranteed boundary recovery'),
 'dynamics':dict(status='validated_evidence',scope=stats['dynamics'],limitation='Finite-time features only; no thermodynamic dynamical transition claim')},not_executed=['N128 MPS optional extension','N12 15x15 optional VQE grid','N12 quench optional extension','ZNE+SV optional combination','real hardware and paid resources'],disposition='New experiments except explicitly historical B0/ED inputs',elapsed_seconds=cost['wall_elapsed_seconds'])
if any(r['evidence_grade']=='supported_in_tested_window' for r in floatgrade['rows']):status['bonus']['floating']['status']='validated_evidence'
dump(OUT/'decision.json',status)
lines=['# Bonus execution status','']
for name,item in status['bonus'].items():lines += [f"## {name}: {item['status']}",'',json.dumps(item,ensure_ascii=False,indent=2),'']
(OUT/'BONUS_STATUS.md').write_text('\n'.join(lines))
# Compact editable English paper source; renderer lays out exactly 3 pages.
paper=f'''# Multi-reference adaptive preparation for noisy ANNNI diagnostics

## Abstract
We compare an energy-selected, resource-aware adaptive circuit with a historical six-layer HVA for the periodic eight-spin ANNNI model. Three explicitly prepared reference states and a local symmetry-preserving Pauli pool reduce the selected median CNOT count to {grid['median_cnots']:g}, compared with 192 in the HVA. The new method passes the unchanged preparation tolerances at {grid['passed']}/420 descriptive-grid points and {held['B3']['passed']}/48 predeclared held-out points. Coverage is state preparation acceptance, not phase-classification accuracy. We retain failures and distinguish noiseless preparation bias from gate-noise increments.

## Model and controlled comparison
H=-sum ZZ_NN+kappa sum ZZ_NNN-h sum X, with Pauli eigenvalues +/-1, periodic boundaries and h>0. We store all C(r), Mx and m_q squared including the 1/N self term. Every executed CNOT, including reference preparation and folds, is followed by target-only depolarization with p=0,.01,.05. NN/NNN connections are direct. All three p use the same optimized parameters. References are plus, GHZ+ and the coherent four-translation period-four cat. ADAPT appends local YZ/ZY or YXZ/ZXY rotations, reoptimizes energy and respects a total 128-CNOT budget. Selection uses energy and resource counts, never held-out ED errors. Three seeds per reference on development test stability; the frozen map protocol uses one seed per reference.

## Results and interpretation
B1 single-reference adaptation passes {held['B1']['passed']}/48 held-out points, B2 fixed short corrections {held['B2']['passed']}/48, and B3 multireference adaptation {held['B3']['passed']}/48. A plus-only cost-ranked ablation passes 39/48, separating ranking from the additional reference benefit. The short pilot alone does not generalize. Across all420 coordinates, mean maximum correlation error at p=.01 decreases from.2638 to.1432 (402 points improve); at p=.05 from.4454 to.3666 (418 improve). On383 jointly accepted points, the corresponding means are.2554 to.1357 and.4327 to.3532. Clean coverage nevertheless falls from407/420 to385/420. B4 chooses a noiseless-equivalent CNOT direction using paid p=.01 energy evaluations. Historical B0 remains unmodified. Full-domain and jointly qualified comparisons are tabulated separately. Quality masks and actual same-coordinate structure-switch audits prevent preparation failure and branch changes from silently becoming phase boundaries.

## Detection, mitigation and scale
D1 uses full physical observables and changes; D2 uses squared Uhlmann fidelity on noisy slices; D3 freezes development-only PCA and clustering. Their outputs express finite-size reference resemblance, with uncertain and degraded outcomes. Literature curves are external comparisons. No independent exact grid labels are assumed. Twelve-spin preparation covers {n12['points']} points ({n12['passed']} passing) and {stats.get('n12_noise',{}).get('configs',0)} exact-density noise configurations. Separate OBC TeNPy calculations examine N32/64/96 and bond dimensions64/128/256; three tested centers(.6,.2),(.8,.5),(1,.7) satisfy our transparent evidence-review criteria, with consistent raw/connected power-law fits, c near1 and converged q. Side controls remain less conclusive. These are finite-window numerical evidence, not precise boundaries or labels for small noisy states.

## Error mitigation and dynamics
ZNE folds every CNOT by factors1/3/5; a frozen linear intercept and separate quadratic estimator never use p0 or ED in the fit. Global-X symmetry verification includes signed OP terms and 30 measurement settings. Raw, ZNE and SV share total10k/100k circuit-shot budgets with32 independent joint-bitstring sampling repeats; gate-weighted costs are reported separately. The target is the same circuit's clean observables. At100k shots, mean component MSE is raw/ZNE/SV=.02158/.01184/.01473 at p=.01 and.13592/.12922/.13190 at p=.05. High-noise restoration remains incomplete. Independent second-order Trotter quenches use two fixed product states, dt=.2/.1/.05 and t<=2; exact evolution isolates discretization error from additional CNOT noise.

## Limitations and conclusion
Reduced inference gates come with adaptive search and measurement overhead. Competition-region failures, finite-size resolution, finite bond dimension, estimator variance and structure switches remain visible. The evidence supports conditional, region-qualified diagnostic comparisons, not a universal thermodynamic phase-boundary displacement, quantum advantage or forced floating-phase assignment. Sources, parameters, raw archives, tests, executed notebook and package manifest accompany the report.

## References
Tang et al., PRX Quantum2,020310 (2021), arXiv:1911.10205. Cea et al., arXiv:2402.11022. Beccaria et al., arXiv:cond-mat/0702676. Bonet-Monroig et al., PRA98,062339 (2018), arXiv:1807.10050. TeNPy1.1.1; PennyLane0.44.1; Mitiq official ZNE guide. Exact access versions and hashes: sources/.
'''
# Typographic spacing in the English deliverable, without changing values.
import re
paper=re.sub(r'(?<=[A-Za-z])(?=\d)', ' ', paper)
paper=paper.replace('from.', 'from .').replace('to.', 'to .').replace('and.', 'and .')
(S/'report.md').write_text(paper)
nb=nbformat.v4.new_notebook();cells=[nbformat.v4.new_markdown_cell('# ANNNI method upgrade: executed research report\n\n'+summary.split('## 方法')[0].split('\n',1)[1]+'\nThe figures below read saved experiment archives. A final cell performs a new lightweight consistency check.'),nbformat.v4.new_code_cell("from pathlib import Path\nimport json,sys,numpy as np\nROOT=next(p for p in [Path.cwd(),*Path.cwd().parents] if (p/'annni/upgrade_gates.py').exists())\nsys.path.insert(0,str(ROOT))\nOUT=ROOT/'results/stage4_upgrade_v1'\nstatistics=json.loads((OUT/'submission/statistics.json').read_text())\nprint({k:{m:{f:v for f,v in r.items() if f!='failures'} for m,r in statistics[k].items()} for k in ['heldout','map','n12']})")]
cells.append(nbformat.v4.new_markdown_cell('## Measured conclusions\n\n- Median inference CNOTs:192 →96, but clean acceptance407/420 →385/420.\n- At p=.01, mean maximum C error:.2638 →.1432, with402/420 points improving. At p=.05:.4454 →.3666.\n- D1 rejects/degrades413/420 at p=.05: lower error does not establish a recovered full phase map.\n- N12:40/60 preparations pass;12 representatives ×3p were actually simulated with exact density matrices.\n- Equal100k-shot MSE at p=.01:raw .02158,ZNE .01184,SV .01473. High-noise restoration remains limited.\n- Three large-OBC centers meet the recorded evidence-review criteria; no exact boundary or small-N label transfer.\n-252 quench configurations separate discretization error from gate noise. Conditional use retains preparation failures and branch sensitivity.'))
figures=[('Matched maps and preparation masks','matched_phase_maps'),('ED and ideal circuits','clean_ed_comparison'),('Gate cost and noise','pareto_noise'),('Reference choices and resources','resources_references'),('Preparation stability','calibration_stability'),('Full discrete structure factor','full_sf'),('Complementary detectors','detectors'),('Fixed-structure diagnostics','fixed_branch_diagnostics'),('Qualified local diagnostic case','qualified_local_case'),('Twelve-spin circuits','n12'),('Matched size comparison','size_comparison'),('Equal-shot mitigation','mitigation_equal_shots'),('OBC size and bond convergence','floating_convergence'),('Spatial and entanglement evidence','floating_correlations_entropy'),('Trotter/noise tradeoff','dynamics_tradeoff')]
for title,name in figures:
 if (S/'figures'/f'{name}.png').exists():
  cells.append(nbformat.v4.new_markdown_cell('## '+title+'\nSaved experiment results, not recomputed by this cell.'))
  cells.append(nbformat.v4.new_code_cell(f"from IPython.display import Image,display\ndisplay(Image(filename=str(OUT/'submission/figures/{name}.png')))"))
cells += [nbformat.v4.new_markdown_cell('## Fresh lightweight verification\nThis cell executes the explicit circuit again and checks p=0 density/pure equivalence. It does not rerun the full optimization campaign.'),nbformat.v4.new_code_cell("from annni.upgrade_gates import compile_circuit,evolve,density,observations,vector\npoint=json.loads((OUT/'development/index.json').read_text())[0]['methods']['B3']\ns=point['selected'];g=compile_circuit(8,point['ref'],s['words'],s['params'])\npsi=evolve(g,8);rho=density(g,8,0)\nnp.testing.assert_allclose(rho,np.outer(psi,psi.conj()),atol=1e-10)\nnp.testing.assert_allclose(psi,np.load(ROOT/point['archive'])['state'],atol=1e-10)\nnoisy=density(g,8,.01)\nprint('Freshly verified:',len(g),'gates; trace=',np.trace(noisy),'max noise-only observable change=',np.max(abs(vector(observations(noisy,8))-vector(observations(psi,8)))))"),nbformat.v4.new_markdown_cell('## Limits and continuation\n'+summary.split('## 资源、失败与复现')[1])]
nb.cells=cells;nb.metadata.kernelspec=dict(name='python3',display_name='Python 3',language='python');nbformat.write(nb,S/'submission.ipynb')
client=NotebookClient(nb,timeout=180,kernel_name='python3',resources={'metadata':{'path':str(ROOT)}});client.execute();nbformat.write(nb,S/'submission.ipynb')
# A lightweight portable HTML preview preserves actual cell outputs.
import html,base64
parts=['<html><meta charset="utf-8"><style>body{max-width:1100px;margin:auto;font:16px sans-serif;line-height:1.5}img{max-width:100%}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style>']
for c in nb.cells:
 if c.cell_type=='markdown':parts.append('<pre>'+html.escape(c.source)+'</pre>')
 else:
  parts.append('<details><summary>Executed Python</summary><pre>'+html.escape(c.source)+'</pre></details>')
  for o in c.get('outputs',[]):
   if 'image/png' in o.get('data',{}):parts.append('<img src="data:image/png;base64,'+o['data']['image/png']+'">')
   elif o.get('output_type')=='stream':parts.append('<pre>'+html.escape(o.get('text',''))+'</pre>')
parts.append('</html>');(S/'notebook_preview.html').write_text('\n'.join(parts))
dump(S/'notebook_execution.json',dict(code_cells=sum(c.cell_type=='code' for c in nb.cells),errors=sum(o.output_type=='error' for c in nb.cells if c.cell_type=='code' for o in c.outputs),executed_utc=datetime.now(timezone.utc).isoformat(),kernel_python=sys.executable,source='saved historical/new experiment outputs + one newly computed explicit-circuit check'))
print('Notebook executed and editable reports built')
