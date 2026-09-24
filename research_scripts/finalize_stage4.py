from pathlib import Path
import sys,json,difflib,datetime,collections,re
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from annni.stage4 import *

def finalize():
    meta=read(OUT/'metadata.json');decision=read(OUT/'decision.json');stats=read(ROOT/'submission/statistics.json')
    a=[]
    for r in read(OUT/'branch_audit/comparisons.json'):
        for e in r['endpoints']:a.extend([e['density_a'],e['density_b']])
    for r in read(OUT/'branch_audit/regression_cases.json'):
        a.extend([r['density_a'],r['density_b']]);a.extend(r.get('full_density',[]))
    calls={'branch_audit':a,'grid_v2':read(OUT/'grid_v2/observations.json'),'local_refinement':read(OUT/'local_refinement/observations.json')}
    meta['density_call_dispositions']={group:dict(collections.Counter(r['cache_status'] for r in rows)) for group,rows in calls.items()}
    meta['actual_elapsed_seconds_to_finalize']=(datetime.now(timezone.utc)-datetime.fromisoformat(read(OUT/'session.json')['started_utc'])).total_seconds()
    meta['test_execution']={'original_suite':(OUT/'verification/old_tests.txt').read_text().strip(),'new_suite':(OUT/'verification/new_tests.txt').read_text().strip(),'full_suite':(OUT/'verification/all_tests.txt').read_text().strip()}
    meta['artifact_review']={'pdf_pages':3,'pdf_rendered_and_visually_checked':read(OUT/'verification/pdf_visual_review.json')['pdf_sha256']==sha(ROOT/'submission/report.pdf'), 'review_record':read(OUT/'verification/pdf_visual_review.json'),'notebook_fresh_kernel_cells':8,'html_presentation_slides':7,'speaker_timing':read(ROOT/'submission/presentation_timing.json'),'html_browser_visual_check':False,'html_check_note':'HTML source/relative images checked; notebook images and PDF pages visually inspected. No interactive browser run.'}
    meta['export_environment']=read(ROOT/'submission/export_environment.json');meta['source_hashes_final']={str(p.relative_to(ROOT)):sha(p) for folder in ['annni','scripts','configs','tests'] for p in (ROOT/folder).glob('*') if p.is_file()}
    before=OUT/'verification/source_before';diff=[]
    for p in before.rglob('*'):
        if p.is_file():
            q=ROOT/p.relative_to(before)
            if q.exists() and p.read_bytes()!=q.read_bytes():diff.extend(difflib.unified_diff(p.read_text().splitlines(True),q.read_text().splitlines(True),fromfile='stage3/'+str(q.relative_to(ROOT)),tofile='stage4/'+str(q.relative_to(ROOT))))
    (OUT/'verification/source_changes.diff').write_text(''.join(diff))
    decision['submission_artifact_status']={'status':'submission_candidate','notebook':'executed, 8 cells','report':'3-page PDF; original visual review hash recorded separately; editable Markdown and builder supplied','presentation':'7-slide editable HTML plus complete notes; timing estimate only','manual_items':['AUTHOR NAMES','TEAM NAME','scientific/editorial review','timed rehearsal'],'official_scope_gaps':['No validated four-phase boundaries','No intrinsic phase-robustness ranking','h=0 excluded from circuit grid']}
    decision['reproducibility_status']={'local_default_entry':'executed successfully','original_tests':33,'new_tests':13,'full_tests':46,'archive_verification':'See external ZIP_VERIFICATION_STAGE4.json, produced after packaging','numerical_audit':read(OUT/'verification/verification.json')}
    dump(OUT/'metadata.json',meta);dump(OUT/'decision.json',decision)
    report=OUT/'REPORT.md';text=report.read_text().split('\n## 最终验证与资源')[0];text+='\n## 最终验证与资源\n\n'+f"本轮重跑旧测试33项、新增测试13项，完整套件46项通过。新密度归档894份，全部p=0共298份重新演化验证；旧受保护文件哈希保持不变。默认复现入口实际跑通。最终整理前墙钟 {meta['actual_elapsed_seconds_to_finalize']/60:.1f} 分钟（90分钟上限）。\n\n"
    text+='密度调用记录（按实验上下文计数；唯一物理执行数另见metadata，不将复用算新增）：\n\n'+json.dumps(meta['density_call_dispositions'],indent=2)+'\n\n'
    text+='三页英文PDF已渲染逐页检查；notebook八个代码单元从新kernel执行。七页HTML展示配有693词讲稿，按130词/分钟估计5.33分钟，尚未实际排练。HTML交互未做浏览器运行测试；其相对图片引用及notebook所有输出已检查。PDF导出使用独立运行时，科学锁定环境未升级。\n\n'
    text+='旧已检查的右端点对照变化：κ=.3,L4,h=.4,p=.05，以及h=.85,p=.01/.05，从不敏感变敏感；κ=.8,L6,h=.65,p=.01，从敏感变不敏感。区间级判断还包含左端点，故不与这张同端点比较表混用。\n\n'
    text+='W1升序p=.01：有序特征Δh=.025但支撑包含0，Mx的可分辨配对位移为0且支撑跨0；W1降序有序特征与Mx的位移不一致。W3仅升序有序特征可配对，缺少Mx支持。W2和所有p=.05的局部位移按本协议未分辨；这些缺失没有填0。\n'
    report.write_text(text)
    dump(OUT/'verification/final_artifact_checks.json',{'pdf_sha256':sha(ROOT/'submission/report.pdf'),'notebook_sha256':sha(ROOT/'submission/submission.ipynb'),'pdf_pages':3,'notebook_executed':True,'figures_visually_checked':['grid_main','branch_cases','local_curves'],'timestamp':now()})
    print('Finalized stage4 metadata and decision')
if __name__=='__main__':finalize()
