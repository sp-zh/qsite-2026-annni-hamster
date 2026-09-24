import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('OMP_NUM_THREADS','1');os.environ.setdefault('MPLCONFIGDIR','.mplconfig')
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import csv,html,shutil,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from annni.stage4 import *

SUB=ROOT/'submission';FIG=SUB/'figures'
def table(rows,keys):return '|'+ '|'.join(keys)+'|\n|'+'|'.join(['---']*len(keys))+'|\n'+''.join('|'+ '|'.join(str(r.get(k,'')) for k in keys)+'|\n' for r in rows)
def build():
    SUB.mkdir(exist_ok=True);FIG.mkdir(exist_ok=True);plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    observations=read(OUT/'grid_v2/observations.json');selected=read(OUT/'grid_v2/selection_frozen.json')['rows'];reps=read(OUT/'grid_v2/replacement_map.json');cases=read(OUT/'branch_audit/regression_cases.json');pairs=read(OUT/'branch_audit/comparisons.json');local=read(OUT/'local_refinement/observations.json');shifts=read(OUT/'local_refinement/shifts.json');stability=read(OUT/'local_refinement/stability.json');sens=read(OUT/'local_refinement/branch_sensitivity.json')
    coverage=sum(r['joint_pass'] for r in selected);changed=sum(r['changed'] for r in reps);stats=dict(grid_pass=coverage,grid_total=420,repaired_gain=coverage-407,changed_parameters=changed,repair_attempts=len(read(OUT/'grid_repair/all_attempts.json')),switch_intervals=len(pairs)//3,interval_p_checks=len(pairs),actual_sensitive=sum(r['actual_switch_pair_sensitive'] for r in pairs),old_flags_changed=sum(r['opposite_direction_checked'] is True and r['opposite_direction_sensitive']!=r['actual_switch_pair_sensitive_at_right'] for r in pairs),local_optimizations=len(read(OUT/'local_refinement/optimization.json')),local_noise_configs=len(local),local_prep_pass=sum(r['joint_pass'] for r in read(OUT/'local_refinement/optimization.json')),local_nonzero_on_chain=sum(r.get('nonzero_supported_on_this_chain',False) for r in shifts),local_resolved_shift_pairs=sum(r['delta_h'] is not None for r in shifts),local_branch_sensitive=sum(r['branch_sensitive'] for r in sens))
    dump(SUB/'statistics.json',stats)
    # Keep the entry-point numbers derived from the same statistics as figures/report.
    import re
    entry=ROOT/'README.md'
    if entry.exists():
        text=entry.read_text()
        text=re.sub(r'fixed L6 grid preparation coverage .*?local noise configurations\.', f"fixed L6 grid preparation coverage {coverage}/420; {stats['switch_intervals']} actual switching intervals audited; {stats['repair_attempts']} repair attempts; {stats['local_optimizations']} local preparations and {stats['local_noise_configs']} local noise configurations.", text)
        entry.write_text(text)
    def save(name):plt.savefig(FIG/(name+'.png'),dpi=170,bbox_inches='tight');plt.close()
    grid={key:np.empty((21,20,3)) for key in ['m0','mpi2','mx','failed']}
    sf=np.empty((21,20,3,8))
    for r in observations:
        ix=(round(r['kappa']/.05),round(r['h']/.1)-1,CFG['p'].index(r['p']));d=np.load(ROOT/r['archive']);sf[ix]=d['structure_factor']
        for key,val in [('m0',d['structure_factor'][0]),('mpi2',d['structure_factor'][2]),('mx',r['mx']),('failed',r['preparation_failed'])]:grid[key][ix]=val
    np.savez_compressed(OUT/'grid_v2/arrays.npz',**grid,structure_factor=sf,kappa=np.arange(21)*.05,h=np.arange(1,21)*.1,p=CFG['p'])
    fig,axes=plt.subplots(3,3,figsize=(11,7),sharex=True,sharey=True,layout='constrained')
    for ir,(key,label,hi) in enumerate([('m0',r'$m_0^2$',1),('mpi2',r'$m_{\pi/2}^2$',.5),('mx',r'$M_x$',1)]):
        for ip,p in enumerate(CFG['p']):
            im=axes[ir,ip].pcolormesh(np.arange(1,21)*.1,np.arange(21)*.05,grid[key][:,:,ip],vmin=0,vmax=hi,shading='nearest');axes[ir,ip].set_title(f'{label}, p={p}');axes[ir,ip].set(xlabel='h',ylabel='kappa',xlim=(.1,2),ylim=(0,1))
        fig.colorbar(im,ax=axes[ir,:],shrink=.85)
    save('grid_main')
    for ip,p in enumerate(CFG['p']):
        fig,axes=plt.subplots(1,4,figsize=(14,3.5),layout='constrained')
        for a,(key,label,hi) in zip(axes,[('m0','m0 squared',1),('mpi2','m(pi/2) squared',.5),('mx','Mx',1),('failed','Preparation failure',1)]):
            im=a.pcolormesh(np.arange(1,21)*.1,np.arange(21)*.05,grid[key][:,:,ip],vmin=0,vmax=hi,shading='nearest');a.set(title=f'{label}; p={p}',xlabel='h',ylabel='kappa',xlim=(.1,2),ylim=(0,1));fig.colorbar(im,ax=a)
        save(f'grid_p{p}')
    fig,ax=plt.subplots(figsize=(6,4));im=ax.imshow(grid['failed'][:,:,0],origin='lower',extent=[.05,2.05,-.025,1.025],aspect='auto',vmin=0,vmax=1,cmap='Greys');ax.set(xlabel='h',ylabel='kappa',title=f'Noiseless preparation: {coverage}/420 pass; black = failure',xlim=(.1,2),ylim=(0,1));save('grid_quality')
    shutil.copy2(OLD/'figures/matched_depth_noise.png',FIG/'depth_noise.png')
    fig,axes=plt.subplots(1,2,figsize=(10,3.5))
    for i,label in enumerate(['case1','case2']):
        rr=[r for r in cases if r['case']==label]
        for j in [0,1]:axes[i].plot(CFG['p'],[r['endpoints'][j] if False else r['density_a' if j==0 else 'density_b']['mx'] for r in rr],'o-',label=f'Candidate {j+1}')
        axes[i].set(title=f'{label}: k=0.3, h={rr[0]["h"]}, L={rr[0]["candidates"][0]["layers"]}',xlabel='p',ylabel='Mx',ylim=(0,1));axes[i].legend()
    save('branch_cases')
    curves=read(OUT/'local_refinement/curves.json');colors=['#1665a7','#e48721','#7545a0']
    fig,axes=plt.subplots(2,3,figsize=(12,6),sharey='row',layout='constrained')
    for iw,w in enumerate(CFG['windows']):
        chains=sorted(set(r['chain'] for r in local if r['window']==w['id']))
        for fidx,feature in enumerate(['order','mx']):
            for ip,p in enumerate(CFG['p']):
                for ci,chain in enumerate(chains):
                    rr=sorted([r for r in curves if r['window']==w['id'] and r['chain']==chain and r['feature']==feature and r['p']==p and r['stride']==1],key=lambda r:r['h'])
                    axes[fidx,iw].plot([r['h'] for r in rr],[r['value'] for r in rr],ls=['-','--'][ci],color=colors[ip],label=f'p={p}, branch {ci+1}')
            axes[fidx,iw].set(title=f'{w["id"]}, k={w["kappa"]}',xlabel='h',ylabel=feature,ylim=(0,1))
    axes[0,0].legend(fontsize=7);save('local_curves')
    fig,axes=plt.subplots(3,3,figsize=(11,8),sharey=True,layout='constrained')
    for iw,w in enumerate(CFG['windows']):
        chain=sorted(set(r['chain'] for r in local if r['window']==w['id']))[0]
        for ip,p in enumerate(CFG['p']):
            rr=sorted([r for r in local if r['chain']==chain and r['p']==p],key=lambda r:r['h']);z=np.stack([np.load(ROOT/r['archive'])['structure_factor'] for r in rr]);im=axes[iw,ip].pcolormesh([r['h'] for r in rr],np.arange(8)/4,z.T,vmin=0,vmax=1,shading='nearest');axes[iw,ip].set(title=f'{w["id"]}, branch 1, p={p}',xlabel='h',ylabel='q / pi')
    fig.colorbar(im,ax=axes,label='m_q squared (fixed scale)');save('local_all_q')
    fig,axes=plt.subplots(1,3,figsize=(11,3),sharey=True,layout='constrained')
    for i,w in enumerate(CFG['windows']):
        for p,col in zip(CFG['p'],colors):
            rr=[r for r in sens if r['window']==w['id'] and r['p']==p];axes[i].plot([r['h'] for r in rr],[max(r['epsilon_c'],r['epsilon_sf'],r['epsilon_mx']) for r in rr],color=col,label=f'p={p}')
        axes[i].axhline(.02,c='gray',ls=':');axes[i].set(title=w['id'],xlabel='h',ylabel='Largest branch observable difference')
    axes[0].legend();save('local_branch_difference')
    # Machine-readable evidence, indexed to actual rows, rather than manually copied numbers.
    claims=[('C1',f'Grid-v2 selected preparation passes {coverage}/420','results/stage4_v1/grid_v2/selection_frozen.json','rows[*].joint_pass','N8 L6 k=0:.05:1 h=.1:.1:2','historical grid plus Stage4 repair','Energy-selected multi-chain coverage, not cold-start reliability',True),('C2',f'All {stats["switch_intervals"]} actual switching intervals checked','results/stage4_v1/branch_audit/comparisons.json','[*], both endpoints, comparison_p','Six Stage3 slices, L4/L6','Stage4 executed or exact physical-cache reuse','Sensitivity is pair-, endpoint- and p-specific',True),('C3',f'{stats["old_flags_changed"]} previous right-endpoint/p flags change','results/stage4_v1/branch_audit/old_new_flags.csv','rows with opposite_direction_checked=True','Original 11 positions times 3 p','Stage4 derived correction','Reliability correction, not a new physical discovery',True),('C4','Two high-fidelity ideal preparations yield different noisy Mx','results/stage4_v1/branch_audit/regression_cases.json','case2, p=.01; candidates and full_density','k=.3 h=.7 L6','Stage4 full density saved','Same gate count; different angles/protocols',True),('C5',f'Local nested-grid resolved shift pairs: {stats["local_resolved_shift_pairs"]}','results/stage4_v1/local_refinement/shifts.json','[*]','3 windows, 2 branches, 3 p, dh=.05/.025/.0125','Stage4','Finite-size protocol diagnostic; not thermodynamic boundary or CI',False),('C6','Ideal accuracy and noisy total error need not improve together','results/stage3_v1/matched_noise/summary.csv','all 15 point-depth rows','5 matched points, L2/4/6, 3 p','Historical Stage3 verified','No universal phase robustness ranking',True)]
    write_csv(SUB/'evidence_table.csv',[dict(zip(['claim_id','claim','evidence_file','array_or_row_index','configuration','provenance','limits','abstract_eligible'],r)) for r in claims])
    req=[('Implementation notebook','What You Submit, item 1','submission/submission.ipynb','candidate','Author/team placeholders need completion'),('Phase diagram images: clean (p=0), noisy (p=0.01), noisy (p=0.05)','What You Submit, item 2','submission/figures/grid_p*.png','partial scientific scope','Continuous diagnostics and control-resemblance views, no validated four-phase boundaries; excludes h=0'),('A 2–3 page writeup','What You Submit, item 3','submission/report.pdf','candidate','3 pages; scientific limitations explicit'),('A 5–7 minute presentation','What You Submit, item 4','submission/presentation.html + speaker_notes.md','candidate','Rehearsal and actual spoken duration not verified'),('at least 15×15','Judging Rubric Detail / Phase Diagram Accuracy','results/stage4_v1/grid_v2/arrays.npz','met','21x20 positive-field grid'),('System size (N=8 baseline, N≥12 impressive)','Technical Sophistication','configs/stage4_v1.json','baseline met','No larger-size VQE'),('Phase diagram accuracy (25%)','How You\'re Scored','submission/report.pdf','limited','No claim of full phase-boundary accuracy'),('Noise analysis depth (25%)','How You\'re Scored','branch_audit and local_refinement','evidence supplied','No forced shift or universal robustness ranking'),('Physical insight (20%)','How You\'re Scored','submission/report.md','evidence supplied','Finite-size and preparation dependence'),('Technical sophistication (15%); Presentation and clarity (15%)','How You\'re Scored','submission/','candidate','No predicted score or award guarantee')]
    write_csv(SUB/'requirements_checklist.csv',[dict(requirement=quote,source='upstream/Scientific Track/README.md#'+loc,artifact=artifact,status=status,gap=gap) for quote,loc,artifact,status,gap in req])
    case2=next(r for r in cases if r['case']=='case2' and r['p']==.01);fidelities=[r['fidelity'] for r in case2['candidates']];dMx=case2['comparison_metrics']['epsilon_mx']
    local_summary=table(shifts,['window','chain','feature','p','status','delta_h','range_low','range_high'])
    report=f'''# Preparation-Protocol Dependence of Noisy ANNNI Phase Diagnostics

Authors: [AUTHOR NAMES] · Team: [TEAM NAME] · Q-SITE 2026 Scientific Track submission candidate

## Abstract
We examine an eight-spin periodic ANNNI chain with an energy-optimized Hamiltonian variational ansatz and the prescribed target-only depolarizing channel after every CNOT. A fixed six-layer positive-field grid contains 420 points and three noise strengths. Bounded local repair raises the selected noiseless preparation coverage from 407 to {coverage}/420 without relaxing acceptance thresholds. We audit {stats['switch_intervals']} actual chain-switch intervals and separate their comparisons from opposite-direction controls. Two preparations with ideal fidelities {fidelities[0]:.8f} and {fidelities[1]:.8f} differ in transverse magnetization by {dMx:.5f} at p=0.01 despite identical CNOT counts. Nested local grids test whether finite-size diagnostics survive changes of resolution and preparation protocol. We do not identify a universal thermodynamic boundary displacement or establish quantum advantage.

## Model and controlled protocol
H = -sum_i Z_i Z_(i+1) + kappa sum_i Z_i Z_(i+2) - h sum_i X_i, N=8, periodic boundaries. The initial state is |+>^8. Each layer executes nearest-neighbor IsingZZ(2 gamma), next-nearest-neighbor IsingZZ(2 eta), then RX(2 beta). IsingZZ(2a)=exp(-ia ZZ); RX(2b)=exp(-ib X). Each ZZ block is compiled as CNOT-RZ-CNOT, with no zero-angle deletion or cancellation. L=6 has 192 CNOTs, 18 parameters and unitary depth 223. All ring edges are directly available; no routing constraint from the Computational Track is assumed.

After each CNOT only its target receives D_p(rho)=(1-p)rho+p/3(XrhoX+YrhoY+ZrhoZ), p=0,0.01,0.05. We simulate the full 256x256 density matrix without symmetry projection, shots=None. All three p values share the same frozen parameters. ED is a validation reference, never the preparation circuit or optimization target.

## Fixed-depth grid and calibration
The grid spans kappa=0:0.05:1 and h=0.1:0.1:2. Zero field is excluded, rather than filled with the ED mixed-state convention. Acceptance requires energy error per spin <=0.001, maximum C(r), structure-factor and Mx errors <=0.02, and squared state fidelity >=0.99. {coverage}/420 selected states pass after {stats['repair_attempts']} bounded repair attempts; {420-coverage} failures remain visible. Selection uses energy only, even when another higher-energy candidate passes. All eight discrete structure factors are saved with their 1/N self term. The control-resemblance classifier uses only [m0^2,2m(pi/2)^2,Mx], not all eight wavevectors.

![Fixed L6 continuous diagnostics, common scales across p](figures/grid_main.png)

These images are finite-size observable maps, not a validated four-phase classifier. The exact diagonalization baseline, VQE and the depolarizing model are established methods, not inventions of this project.

## Depth, noise and the corrected switching audit
The historical matched five-point experiment uses the same three cold-start seeds and budget at L=2,4,6, followed by energy-only selection. CNOT counts are 64,128,192. Deeper circuits improve ideal preparation but can worsen noisy total error. At (kappa,h)=(0,1.8), maximum structure-factor errors for p=0.01 are approximately 0.0297,0.0527,0.0937. Error vectors are stored separately as O(0)-O_ED and O(p)-O(0); their maximum norms cannot simply be added.

A previous diagnostic treated an opposite-direction comparison as evidence about a selected chain switch. This fails for same-direction, different-seed switches. We now compare A and B at both ends of every actual interval. {stats['old_flags_changed']} of the previously checked right-endpoint/p flags change; numerical propagation is unchanged. Unknown checks remain null, and no-switch intervals are not_applicable. Both preparations must pass before interpreting a difference as sensitivity between high-quality preparations.

![Same-parameter candidate comparison](figures/branch_cases.png)

The kappa=0.3,h=0.7,L6 case has an ideal Mx difference of {next(r for r in cases if r['case']=='case2' and r['p']==0)['comparison_metrics']['epsilon_mx']:.7f}, but p=0.01 increases it to {dMx:.5f}. The complete parameters, ideal states and six density matrices are archived. This demonstrates dependence on the implemented preparation protocol, not an intrinsic ranking of phase fragility.

## Local refinement and scientific limits
Three windows were frozen using N8 noiseless evidence: kappa=0,h=[.75,1.25]; kappa=.3,h=[.25,.65]; kappa=.8,h=[.35,.85]. Two independent archived endpoint chains are continued separately per window. The finest step is .0125; .025 and .05 grids are nested subsamples of exactly the same preparations, not independent repetitions. All three noise strengths are evaluated at every fine-grid state. {stats['local_prep_pass']}/{stats['local_optimizations']} local preparations pass.

![Fixed-branch local curves; solid and dashed denote separate chains](figures/local_curves.png)

The frozen protocol requires raw signal range >=.02 and derivative prominence >=.02, records every local and endpoint peak, and cuts derivatives at failed preparations or possible optimization jumps. Full stencil and coarse-grid supports are retained. There are {stats['local_resolved_shift_pairs']} matched branch/feature/noise pairs and {stats['local_nonzero_on_chain']} entries with complementary-indicator support excluding zero on an individual chain. These counts are not a universal boundary-shift claim: see the per-branch table and preparation-sensitivity records. We retain not_resolved values as missing, never zero. Signal loss under this protocol does not prove that every measurement loses all information. Resolution/protocol ranges are not statistical confidence intervals.

Finite N, incomplete preparation coverage, branch-dependent noisy circuits and a fixed ansatz limit interpretation. No floating phase is confirmed. We make no quantum-advantage claim. The new project contribution is a controlled computational comparison with traceable protocol sensitivity; the audit correction itself is reliability work. Author identities, final editorial review and a timed presentation rehearsal remain outstanding.

## References and reproducibility
[1] Q-SITE 2026 Quantum Coalition, Scientific Track handout, upstream snapshot 57f9a537d24c69328dedf915ad58d1d2bf505135 (README and PROVENANCE included).
[2] PennyLane, ANNNI Phase Detection demo, https://pennylane.ai/qml/demos/tutorial_annni (background linked by handout).
[3] PennyLane, A Noisy Heisenberg Model, https://pennylane.ai/challenges/heisenberg_model (noise resource linked by handout).

Run `bash scripts/reproduce_submission.sh` to verify archived results, rebuild this candidate and execute lightweight notebook checks. Full experimental continuation requires `--compute`. Exact sources, settings, inputs, archives and SHA256 manifests accompany the bundle.
'''
    (SUB/'report.md').write_text(report)
    (SUB/'local_diagnostic_details.md').write_text('# Per-branch local diagnostic results\n\n'+local_summary+'\nRanges are deterministic resolution/protocol ranges, not confidence intervals.\n')
    remaining=[dict(kappa=r['new']['kappa'],h=r['new']['h'],failed_metrics=r['failed_metrics'],other_candidate_pass=r['other_candidate_pass']) for r in reps if not r['selected_pass']]
    dump(OUT/'grid_repair/remaining_failures.json',remaining)
    decision=dict(branch_audit_status=dict(complete=True,actual_intervals=stats['switch_intervals'],interval_p_checks=len(pairs),changed_old_flags=stats['old_flags_changed']),grid_repair_status=dict(attempts=stats['repair_attempts'],before=407,after=coverage,total=420,remaining=remaining,changed_parameters=changed),local_refinement_status=dict(completed=True,states=stats['local_optimizations'],noise_configs=len(local),resolved_pairs=stats['local_resolved_shift_pairs'],individual_chain_nonzero_entries=stats['local_nonzero_on_chain']),scientific_claim_limits=['No universal thermodynamic boundary shift','Per-chain finite-size diagnostics only','No floating-phase confirmation or quantum advantage','Control prototypes use three features only'],submission_artifact_status='candidate; verify PDF, notebook execution, and bundle before final delivery',reproducibility_status='verification pending final bundle')
    dump(OUT/'decision.json',decision)
    code={str(p.relative_to(ROOT)):sha(p) for folder in ['annni','scripts','configs','tests'] for p in (ROOT/folder).glob('*') if p.is_file()}
    opts=[read(p) for p in (OUT/'optimization').glob('*.json')];dens=[read(p) for p in (OUT/'density').glob('*.json')]
    dump(OUT/'metadata.json',dict(created_utc=now(),statistics=stats,environment=dict(python=sys.version,platform=platform.platform(),versions=VERSIONS),physics_fingerprint=physical_fp(),selection_fingerprint=sha(OUT/'grid_v2/selection_frozen.json'),diagnostics_fingerprint=sha(ROOT/'annni/stage4_diagnostics.py'),code_hashes=code,config=CFG,local_source_amendment=read(ROOT/'configs/stage4_local_amendment_v1.json'),unique_new_optimizations=len(opts),unique_new_density=len(dens),optimization_seconds=sum(r['end_to_end_seconds'] for r in opts),density_seconds=sum(r['end_to_end_seconds'] for r in dens),budget=read(OUT/'session.json'),unexecuted=['large-size VQE','hardware','shot sampling','additional restarts beyond 78'],source_version_note='Stage3 sources retained unchanged; corrected analysis lives in new stage4 modules. README versioned with source_before copy.'))
    (OUT/'REPORT.md').write_text(f'''# Stage 4 执行总结

全部实际切换：{stats['switch_intervals']}区间、{len(pairs)}个区间-p检查；旧检查在同一右端点的{stats['old_flags_changed']}个标记改变。区间级敏感性另外汇总左右两端，不与单端点旧检查混淆。问题在比较对象及诊断支撑传播，未修改密度后端。

补救78次，覆盖407→{coverage}/420，获选参数改变{changed}点。三个p全部使用对应新参数；未改点显式复用。剩余失败：

{table(remaining,['kappa','h','failed_metrics','other_candidate_pass'])}

局部细化{stats['local_optimizations']}次优化、{len(local)}个噪声配置，制态通过{stats['local_prep_pass']}次。原预设部分端点不合格，在新局部计算之前保存来源修订；窗口、层数和阈值不变。嵌套子网格不是独立重复。

局部分支/特征配对{stats['local_resolved_shift_pairs']}个，单链互补指标支持非零的条目{stats['local_nonzero_on_chain']}个；完整逐链结果见submission/local_diagnostic_details.md。不能平均成唯一物理边界，not_resolved不填0。

英文报告、全网格图、逐门案例、已执行notebook与展示提纲见submission目录。官方要求逐项核对，未把连续特征图宣称为严格四相分类。仍需作者、队伍名、人工审稿与5–7分钟实际排练。

本轮新增优化{len(opts)}次，累计端到端{sum(r['end_to_end_seconds'] for r in opts):.1f}秒；新增密度计算{len(dens)}次，累计{sum(r['end_to_end_seconds'] for r in dens):.1f}秒。各调用保留executed/reused_stage3/cached_stage4状态；全新完整密度案例与重复缓存升级单独记账。

复现：`bash scripts/reproduce_submission.sh`；显式`--compute`才续算新实验，独立Stage4预算未重设Stage3时间。
''')
    print(stats)
if __name__=='__main__':build()
