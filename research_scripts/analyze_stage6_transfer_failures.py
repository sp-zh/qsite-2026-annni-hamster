"""Post-evaluation N12 attribution; no new selector or candidate optimization."""
import sys, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *

outputs=[]
for task in ['n12','n12_192','n12_window']:
    path=OUT/f'n12_transfer/{task}_paired_summary.json'
    if not path.exists():
        continue
    source=json.loads(path.read_text())
    rows=[]
    for r in source['rows']:
        if r['joint_pass']:
            mechanism='selected_joint_pass'
        elif r['candidate_pool_exists']:
            mechanism='qualified_saved_candidate_not_selected'
        else:
            mechanism='no_qualified_saved_candidate_within_run_budget'
        rows.append(dict(**r, mechanism=mechanism,
            observable_accurate_state_inaccurate=r['observable_pass'] and not r['state_pass'],
            parity_even_translation_broken=(abs(r['parity_real']-1)<1e-6 and abs(r['translation_real'])<.05),
            interpretation=('Near-half fidelity and small translation expectation can be consistent with one translation branch; no projection, enlarged target subspace or changed acceptance is applied.'
                if r['observable_pass'] and .45<r['fidelity']<.55 and abs(r['translation_real'])<.05 else
                'Budget-limited empirical evidence. Missing a good saved candidate does not prove mathematical inexpressibility.')))
    groups=[]
    for method in sorted({r['method'] for r in rows}):
        for region in ['all',*sorted({r['region'] for r in rows})]:
            rr=[r for r in rows if r['method']==method and (region=='all' or r['region']==region)]
            groups.append(dict(method=method,region=region,coordinates=len(rr),
                mechanisms=dict(collections.Counter(r['mechanism'] for r in rr)),
                observable_accurate_state_inaccurate=sum(r['observable_accurate_state_inaccurate'] for r in rr),
                parity_even_translation_broken=sum(r['parity_even_translation_broken'] for r in rr)))
    dump(OUT/f'n12_transfer/{task}_failure_mechanisms.json',dict(source=str(path.relative_to(ROOT)),source_sha256=sha(path),rows=rows,summary=groups,
        scope='Frozen N8-to-N12 transfer, post-evaluation attribution only. Candidate existence includes saved intermediate checkpoints; an ED oracle can identify them but is not used for deployed selection. No model, thresholds, pool or initialization rules were retuned using these results.'))
    outputs.append((task,len(rows)))
print(outputs)
