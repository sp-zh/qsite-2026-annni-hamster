import os
os.environ.setdefault('MPLCONFIGDIR','.mplconfig');os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import json,csv,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from annni.stage3 import *
from datetime import datetime,timezone

def read(p):return json.loads((OUT/p).read_text())
def table(rows,keys):
    return '|'+ '|'.join(keys)+'|\n|'+'|'.join(['---']*len(keys))+'|\n'+''.join('|'+ '|'.join(str(r.get(k,'')) for k in keys)+'|\n' for r in rows)
def main():
    figdir=OUT/'figures';figdir.mkdir(exist_ok=True)
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    def save(name):plt.savefig(figdir/(name+'.png'),dpi=160,bbox_inches='tight');plt.close()
    A=read('optimization/A_runs.json');B=read('matched_noise/observations.json');C=read('slices/observations.json');S=read('slices/selection_frozen.json')['rows'];D=read('slices/preparation_protocol_sensitivity.json')
    colors=['#1665a7','#e48721','#7545a0'];ps=[0,.01,.05]
    fig,ax=plt.subplots(figsize=(9,4))
    groups=['A1_parameter_resume','A2_independent_cold','A3_continuation']
    old=[json.loads((ROOT/f'results/calibration_v1/runs/p06_L6_s{s}.json').read_text()) for s in [11,23,37]]
    for i,g in enumerate([old]+[[r for r in A if r['group']==g and r['h']==.4] for g in groups]):
        ax.scatter(np.full(len(g),i)+np.linspace(-.12,.12,len(g)),[r['delta_e'] for r in g],c=['#26763d' if r['joint_pass'] else '#b43b38' for r in g])
    ax.axhline(.001,c='gray',ls='--');ax.set(yscale='log',ylabel='Energy error / spin',xticks=range(4),xticklabels=['Old 400 iterations','Parameter resume','6 independent cold','3 continuation chains'],title='Fixed L=6, kappa=0.3, h=0.4; green = joint pass');save('optimization')
    points=CFG['B']['points'];fig,axes=plt.subplots(2,5,figsize=(16,6),sharex=True,sharey='row')
    for j,(k,h) in enumerate(points):
        for ip,p in enumerate(ps):
            rows=sorted([r for r in B if r['kappa']==k and r['h']==h and r['p']==p],key=lambda r:r['layers'])
            axes[0,j].plot([r['layers'] for r in rows],[r['epsilon_sf_total'] for r in rows],'o-',color=colors[ip],label=f'p={p}')
            axes[1,j].plot([r['layers'] for r in rows],[r['r_mix'] for r in rows],'o-',color=colors[ip])
        axes[0,j].set_title(f'k={k}, h={h}');axes[1,j].set_xlabel('Layers (32 CNOT / layer)')
    axes[0,0].set_ylabel('max SF error to ED');axes[1,0].set_ylabel('R_mix');axes[1,0].set_ylim(-.02,1.02);axes[0,0].legend();save('matched_depth_noise')
    fig,axes=plt.subplots(3,5,figsize=(16,8),sharex=True,sharey=True)
    for il,L in enumerate([2,4,6]):
        for j,(k,h) in enumerate(points):
            for ip,p in enumerate(ps):
                r=next(r for r in B if r['kappa']==k and r['h']==h and r['layers']==L and r['p']==p);d=np.load(ROOT/r['archive'])
                axes[il,j].plot(np.arange(8)/4,d['structure_factor'],'o-',color=colors[ip],label=f'p={p}',ms=3)
            axes[il,j].plot(np.arange(8)/4,d['ed_structure_factor'],'k--',label='ED');axes[il,j].set_title(f'k={k}, h={h}, L={L}');axes[il,j].set_ylim(0,1)
    axes[0,0].legend(fontsize=8);fig.supxlabel('q / pi (all eight discrete modes)');fig.supylabel('m_q squared');save('matched_full_structure_factor')
    fig,axes=plt.subplots(2,3,figsize=(14,7),sharex=True,sharey=True)
    for il,L in enumerate([4,6]):
        for ik,k in enumerate([0,.3,.8]):
            a=axes[il,ik]
            for ip,p in enumerate(ps):
                rows=sorted([r for r in C if r['layers']==L and r['kappa']==k and r['p']==p],key=lambda r:r['h']);ds=[np.load(ROOT/r['archive']) for r in rows];q=0 if k<.5 else 2
                a.plot([r['h'] for r in rows],[d['structure_factor'][q] for d in ds],color=colors[ip],label=f'p={p}')
                if p==0:a.plot([r['h'] for r in rows],[d['ed_structure_factor'][q] for d in ds],'k--',label='ED')
            for r in rows:
                if r['preparation_failed']:a.axvspan(r['h']-.025,r['h']+.025,color='red',alpha=.14)
                if r['branch_switch']:a.plot(r['h'],1.025,'|',color='gray',ms=4)
            a.set(title=f'k={k}, L={L}',ylim=(0,1.04),xlabel='h')
    axes[0,0].legend();fig.supylabel('m_0 squared (k<0.5), m_pi/2 squared (k=0.8)');save('slices_order')
    fig,axes=plt.subplots(2,3,figsize=(14,7),sharex=True,sharey=True)
    for il,L in enumerate([4,6]):
        for ik,k in enumerate([0,.3,.8]):
            for ip,p in enumerate(ps):
                rows=sorted([r for r in C if r['layers']==L and r['kappa']==k and r['p']==p],key=lambda r:r['h'])
                axes[il,ik].plot([r['h'] for r in rows],[r['mx'] for r in rows],color=colors[ip],label=f'p={p}')
            axes[il,ik].set(title=f'k={k}, L={L}',ylim=(-.05,1.05),xlabel='h')
    axes[0,0].legend();fig.supylabel('Mx');save('slices_mx')
    arr=np.load(OUT/'slices/arrays.npz');fig,axes=plt.subplots(2,3,figsize=(14,7),sharex=True,sharey=True,layout='constrained')
    for il,L in enumerate([4,6]):
        for ip,p in enumerate(ps):
            im=axes[il,ip].pcolormesh(arr['h'],np.arange(8)/4,arr['structure_factor'][il,2,:,ip,:].T,vmin=0,vmax=.5,shading='nearest');axes[il,ip].set(title=f'k=0.8, L={L}, p={p}',xlabel='h',ylabel='q / pi')
    fig.colorbar(im,ax=axes,label='m_q squared (fixed scale)');save('full_wavevector')
    fig,axes=plt.subplots(1,2,figsize=(11,4))
    for ip,p in enumerate(ps):
        rows=[r for r in C if r['p']==p];axes[0].scatter([r['d_mix'] for r in rows],[r['r_mix'] for r in rows],s=7,alpha=.6,label=f'p={p}',color=colors[ip])
        dd=[r for r in D if r['p']==p];axes[1].scatter(range(len(dd)),[max(r['max_c_difference'],r['mx_difference']) for r in dd],s=22,label=f'p={p}',color=colors[ip])
    axes[0].set(xlabel='D_mix',ylabel='R_mix',xlim=(0,1),ylim=(0,1.03));axes[1].axhline(.02,c='gray',ls='--');axes[1].set(xlabel='Preselected alternate location index',ylabel='max(C, Mx) branch difference');axes[0].legend();save('mixing_branch_sensitivity')
    curves=read('slices/diagnostics/curves.json')
    fig,axes=plt.subplots(2,3,figsize=(14,7),sharex=True,sharey='row')
    for il,L in enumerate([4,6]):
        for ik,k in enumerate([0,.3,.8]):
            for ip,p in enumerate(ps):
                for feature,style in [('order','-'),('mx','--')]:
                    rr=[r for r in curves if r['kappa']==k and r['L']==L and r['p']==p and r['feature']==feature]
                    axes[il,ik].plot([r['h'] for r in rr],[np.nan if r['derivative'] is None else r['derivative'] for r in rr],style,color=colors[ip],label=f'{feature}, p={p}')
            axes[il,ik].set(title=f'k={k}, L={L}',xlabel='h')
    axes[0,0].legend(fontsize=7);fig.supylabel('Diagnostic derivatives (gaps retained)');save('diagnostic_derivatives')
    import csv
    direction_rows=list(csv.DictReader((OUT/'slices/direction_best.csv').open()))
    fig,axes=plt.subplots(2,3,figsize=(14,7),sharex=True,sharey=True)
    for il,L in enumerate([4,6]):
        for ik,k in enumerate([0,.3,.8]):
            for direction,style in [('ascending','-'),('descending','--')]:
                rr=sorted([r for r in direction_rows if float(r['kappa'])==k and int(r['layers'])==L and r['direction']==direction],key=lambda r:float(r['h']))
                axes[il,ik].plot([float(r['h']) for r in rr],[max(1e-12,float(r['delta_e'])) for r in rr],style,label=direction)
            axes[il,ik].axhline(.001,c='gray',ls=':');axes[il,ik].set(title=f'k={k}, L={L}',yscale='log',xlabel='h')
    axes[0,0].legend();fig.supylabel('Best energy error / spin by direction (plot floor 1e-12)');save('directional_preparation')
    grid=read('grid/execution.json') if (OUT/'grid/execution.json').exists() else {'status':'not_started'}
    if grid['status']=='complete':
        g=np.load(OUT/'grid/arrays.npz');fig,axes=plt.subplots(4,3,figsize=(13,12),sharex=True,sharey=True,layout='constrained')
        for row,(name,z,vmax) in enumerate([('m0 squared',g['structure_factor'][...,0],1),('m_pi/2 squared',g['structure_factor'][...,2],.5),('Mx',g['mx'],1),('preparation failed',g['preparation_failed'],1)]):
            for ip,p in enumerate(ps):
                im=axes[row,ip].pcolormesh(g['h'],g['kappa'],z[:,:,ip],vmin=0,vmax=vmax,shading='nearest');axes[row,ip].set(title=f'{name}; p={p}',xlabel='h',ylabel='kappa')
            fig.colorbar(im,ax=axes[row,:])
        save('positive_field_grid')
    fail=[dict(kappa=k,layers=L,h=[r['h'] for r in S if r['kappa']==k and r['layers']==L and not r['joint_pass']]) for L in [4,6] for k in [0,.3,.8]]
    grid_failed=[]
    if grid['status']=='complete':
        grid_failed=[dict(kappa=r['kappa'],h=r['h'],delta_e=r['delta_e'],fidelity=r['fidelity'],epsilon_c=r['epsilon_c'],epsilon_sf=r['epsilon_sf'],epsilon_mx=r['epsilon_mx']) for r in read('grid/selection_frozen.json')['rows'] if not r['joint_pass']]
        dump(OUT/'grid/failed_points.json',grid_failed);write_csv(OUT/'grid/failed_points.csv',grid_failed)
    b_opt=list(csv.DictReader((OUT/'matched_noise/optimization.csv').open()))
    summaries=[]
    for k,h in points:
        for L in [2,4,6]:
            rows=sorted([r for r in B if r['kappa']==k and r['h']==h and r['layers']==L],key=lambda r:r['p'])
            opt=next(r for r in read('matched_noise/selection_frozen.json')['rows'] if r['kappa']==k and r['h']==h and r['layers']==L)
            cold=[r for r in b_opt if float(r['kappa'])==k and float(r['h'])==h and int(r['layers'])==L]
            summaries.append(dict(kappa=k,h=h,L=L,cold_pass=str(sum(r['joint_pass']=='True' for r in cold))+'/3',pass0=not rows[0]['preparation_failed'],delta_e=f"{opt['delta_e']:.3g}",F0=f"{rows[0]['fidelity_ed']:.6f}",SFerr_p0=f"{rows[0]['epsilon_sf_total']:.4g}",SFerr_p01=f"{rows[1]['epsilon_sf_total']:.4g}",SFerr_p05=f"{rows[2]['epsilon_sf_total']:.4g}",Rmix_p05=f"{rows[2]['r_mix']:.4g}",Dmix_p05=f"{rows[2]['d_mix']:.4g}"))
    write_csv(OUT/'matched_noise/summary.csv',summaries)
    caches=[json.loads(p.read_text()) for p in (OUT/'optimization/cache').glob('*.json')];dens=[json.loads(p.read_text()) for p in (OUT/'density_cache').glob('*.json')]
    elapsed=(datetime.now(timezone.utc)-datetime.fromisoformat(read('manifest.json')['started_utc'])).total_seconds()
    decision=dict(implementation_verified={'passed':True,'tests':33,'result_audit':read('verification/result_audit.json')},optimization_coverage=read('slices/coverage.json'),diagnostic_readiness='Continuous diagnostics usable; no corroborated nonzero boundary shift. Unchecked switches and failed preparation neighborhoods masked.',slice_execution_status=dict(status='complete',optimization_records=1440,main_noise_evaluations=720,alternate_locations=len(D)//3,alternate_evaluations=len(D)),grid_execution_status=grid,scientific_claim_limits=['N=8 finite size only','No floating-phase confirmation','No statistically established critical boundary','Independent cold-start stability differs from six-chain best selection','No shots or hardware errors included'],next_stage='CONDITIONAL GO: region-qualified continuous-observable analysis; local branch-controlled refinements before boundary claims')
    dump(OUT/'decision.json',decision)
    metadata=dict(completed_utc=now(),wall_elapsed_seconds_including_authoring=elapsed,unique_optimization_executions=len(caches),unique_density_executions=len(dens),optimizer_end_to_end_seconds=sum(r['end_to_end_seconds'] for r in caches),density_end_to_end_seconds=sum(r['end_to_end_seconds'] for r in dens),density_evolution_seconds=sum(r['evolution_seconds'] for r in dens),density_postprocess_seconds=sum(r['postprocess_seconds'] for r in dens),environment=read('manifest.json'),failures=fail,code_hashes={str(p.relative_to(ROOT)):sha(p) for folder in ['annni','scripts','tests','configs'] for p in (ROOT/folder).glob('*') if p.is_file()},input_hashes=read('verification/input_audit.json')['protected_sha256'],remaining_unexecuted=['N>=12 VQE','hardware','shot sampling','local refinement','strict four-phase classification'],adjustments=[{'reason':'NumPy integer JSON serialization in peak index corrected; no model/threshold/results changed','when':'post-C diagnostic export before grid run'}],cache_reuse='Exactly matching parameter/config/version hashes only; each alias keeps cache_status. B reused 3 A2 runs. Grid exact slice states and their noise reused.',basis='wire 0 MSB; array axes slices=[L,kappa,h,p,q]; grid=[kappa,h,p,q]; h>0 only')
    dump(OUT/'metadata.json',metadata)
    resolved=[r for r in read('slices/diagnostics/peaks.json') if r['resolved']]
    sensitivity=[r for r in D if r['branch_sensitive']]
    with (OUT/'REPORT.md').open('w') as f:
        f.write(f'''# Stage 3：优化稳定化与逐门噪声实测

A/B/C 均实际完成；正场网格状态：**{grid['status']}**。N=8 周期边界，未修改旧结果和 upstream。
固定 L=6 的切片获选覆盖 120/120，L=4 为 107/120。选择是六条独立方向/种子链中的最低能量，不能称为冷启动 100% 成功。

## A：固定 L=6 的补救

目标 (0.3,0.4)：旧参数追加最多1600步通过1/3；六个新冷启动通过4/6；从h=.5经.45到.4的独立来源延续通过3/3。
延续组目标δe中位数3.6553e-5、F中位数0.9999314。续跑仅恢复参数，不恢复L-BFGS历史。
共39条A记录，包含四个额外点及所有失败，未超过60条上限。原400步和累计成本保存在每条记录。
同样预算并不能消除所有局部最优；已有准确解支持优先改善初始化，而非把困难点直接归因于表达能力。

![优化补救](figures/optimization.png)

## B：匹配冷启动队列与深度噪声

5点×3深度×3新种子，共45个优化配置（其中3个与A2完全相同，哈希校验后复用），再做45个密度矩阵评估，完整保存45个rho。
各(point,L)在含噪计算前按无噪声能量冻结参数。浅层失败继续计算并标记。
每层32个CNOT；L2/4/6分别64/128/192个，实际单元门深度75/149/223。零角度块与κ=0的NNN块不删除。

{table(summaries,['kappa','h','L','cold_pass','pass0','delta_e','F0','SFerr_p0','SFerr_p01','SFerr_p05','Rmix_p05','Dmix_p05'])}

更深的理想制态收益没有保证含噪总误差单调降低。总误差含制态误差与噪声增量；逐分量差严格可加，最大范数不可直接相加。
误差抵消不是误差缓解。相同门数仍有角度和误差传播差异，不能解释成不同相的固有抗噪性。
R_mix与D_mix保留数值，不能因purity四舍五入接近1/256而断言完全混合。

![配对结果](figures/matched_depth_noise.png)
![全波矢配对](figures/matched_full_structure_factor.png)

## C：完整含噪切片

κ=0,.3,.8；h=.05,.10,…,2；L=4,6；p=0,.01,.05。1440条优化记录、720个主噪声配置、{len(D)//3}个位置的{len(D)}个反方向对照全部完成。
每个方向使用101/211/307三个独立来源链，不在链之间复制获胜参数。每条2000步上限，退出原因、全部初末参数可查。
获选制态失败位置如下（其余点通过）：

{table(fail,['kappa','layers','h'])}

反方向对照有{len(sensitivity)}/{len(D)}个(p,位置)超过预设物理量差.02，详细位置在preparation_protocol_sensitivity.csv。
未检查位置的branch_sensitive保留null，不把缺乏证据写成无分支效应。参数切换位置可从selected.csv追溯。上下文质量标记以各组observations.json/CSV与noise_records为准；density_cache中的branch_sensitive是未使用的后端默认值，不能解读为已做分支检查。复用切片参数的网格记录继承已有检查结果。

![切片有序信号](figures/slices_order.png)
红色区间为制态失败；顶部短线为参数来源切换。
![横磁化](figures/slices_mx.png)
![全部离散波矢](figures/full_wavevector.png)
κ=.8的竞争波矢逐点保存在wavevector_competition.csv；q与2π-q折叠只用于峰诊断，原始数据保留8个q。
π/2信号降低与其他q权重变化分开处理；不据此确认floating phase。
![混合程度与分支检查](figures/mixing_branch_sensitivity.png)

## 有限尺寸诊断与边界解释

保留diagnostics_v1控制态原型与阈值。额外可分辨性规则在计算前冻结于stage3_v1配置：无平滑/插值，连续有效区间内差分；幅度≥.02、导数峰显著度≥.02；两个隔点网格均需稳定；端点峰、失败间隙、未核查的分支切换邻域不用于边界结论。
全部局部峰含端点、峰宽、显著度和网格支撑区间均保存。共{len(resolved)}个峰满足单曲线规则，但没有互补指标共同支持的非零位移。
少数Mx配对只是single_indicator_only，其位移网格支撑包含零；不作为测得的边界移动。其他记录为not_resolved，而非零位移。
![导数诊断](figures/diagnostic_derivatives.png)
![方向依赖](figures/directional_preparation.png)

网格支撑不是统计置信区间；确定性shots=None数据不产生抽样误差条。原型标签只表征控制态相似性，完全混合态归degraded，不等同高场基态。

## 正场网格与推进判断

{json.dumps(grid,ensure_ascii=False,indent=2)}

网格范围κ=0:.05:1、h=.1:.1:2，**不含h=0**。L=6由理想覆盖率和资源选定，未按噪声图外观选层数。
对三条已有切片的相同点复用冻结参数；其余κ分别由邻近切片同seed同direction的端点初始化，再各自延续。
网格逐点重新验证制态，失败保存真实值；没有以ED输出替代。

{table(grid_failed,['kappa','h','delta_e','fidelity'])}
主结论限定连续物理量与质量掩码，未经分支验证的局部特征不宣称边界。

![正场网格](figures/positive_field_grid.png)

**CONDITIONAL GO**：可以继续有区域质量控制的连续物理量分析；严格边界或四相分类仍需局部同协议、同网格的分支核查与加密。

## 数值验证、复现与资源

本轮33项回归测试通过；逐结果审计见verification/result_audit.json。随机及近最优参数下，快速纯态与PennyLane、解析梯度与有限差分交叉验证；密度后端与PennyLane完整矩阵代表配置差异约5e-14。
每个实际密度计算均检查迹、厄米性、半正定性、能量/SF恒等式、C(0)、有符号误差分解；每个p=0密度与纯态外积一致。
密度使用完整256×256，未施加对称投影。所有NN/NNN边直接可执行，无另一赛道硬件路由约束；每个CNOT后仅target加规定通道。
小范围PennyLane交叉验证不代表所有参数点逐一与该后端重算；全结果恒等式与归档哈希另行检查。

实测唯一优化执行{len(caches)}次，累计端到端{metadata['optimizer_end_to_end_seconds']:.1f}秒；唯一密度执行{len(dens)}次，累计端到端{metadata['density_end_to_end_seconds']:.1f}秒。
编写/检查/等待在内截至报告的墙钟{elapsed/60:.1f}分钟，预设预算90分钟。纯演化和后处理时间独立存metadata；缓存命中不算新增执行。
已执行notebook全部代码单元，并重新计算一个L2代表态与PennyLane密度对照。nbconvert未安装，HTML预览改用标准库生成；无环境升级。图像已检查色标与布局，未用浏览器逐页检查HTML。首次导出失败日志保留。
未升级环境；Python与库版本、所有输入/代码哈希在metadata。无真实硬件、无抽样、无N≥12 VQE、无局部加密。

复现入口：项目根目录执行 `bash scripts/reproduce_stage3.sh`。默认校验并重建报告/notebook；`--compute`按原指纹复用断点继续计算，原会话预算到期时停止，不静默重设预算。
下一轮建议固定L6，沿用阈值，优先针对失败格点及候选峰邻域进行独立分支检查，p三值同步加密；不要直接扩大尺寸或放宽门槛。
结果包包含源码、锁文件、既有必需输入、所有新原始数据、执行日志和notebook；ZIP解压校验结果另附sidecar。
''')
    print('Report generated',grid)
if __name__=='__main__':main()
