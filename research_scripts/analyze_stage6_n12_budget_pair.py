"""Same-coordinate 128/192 resource comparison; no candidate or selection change."""
import sys,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *

sources=[OUT/f'n12_transfer/{task}_paired_summary.json' for task in ['n12','n12_192']]
low,high=[json.loads(p.read_text())['rows'] for p in sources]
key=lambda r:(r['kappa'],r['h'],r['method'])
lookup={key(r):r for r in low}
assert len(lookup)==len(low)
rows=[]
for b in high:
    a=lookup[key(b)]
    assert a['region']==b['region'] and a['seed']==b['seed']
    rows.append(dict(kappa=b['kappa'],h=b['h'],method=b['method'],region=b['region'],seed=b['seed'],
        cap128={k:a[k] for k in ['joint_pass','observable_pass','state_pass','candidate_pool_exists','cnots','delta_e','fidelity','source']},
        cap192={k:b[k] for k in ['joint_pass','observable_pass','state_pass','candidate_pool_exists','cnots','delta_e','fidelity','source']},
        outcome='both_pass' if a['joint_pass'] and b['joint_pass'] else 'improved' if b['joint_pass'] else 'regressed' if a['joint_pass'] else 'both_fail'))
summary=[]
for method in sorted({r['method'] for r in rows}):
    for region in ['all',*sorted({r['region'] for r in rows})]:
        rr=[r for r in rows if r['method']==method and (region=='all' or r['region']==region)]
        summary.append(dict(method=method,region=region,coordinates=len(rr),outcomes=dict(collections.Counter(r['outcome'] for r in rr)),
            **{cap:dict(**{metric:sum(r[cap][metric] for r in rr) for metric in ['joint_pass','observable_pass','state_pass','candidate_pool_exists']},median_cnots=float(np.median([r[cap]['cnots'] for r in rr]))) for cap in ['cap128','cap192']}))
result=dict(rows=rows,summary=summary,sources=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in sources],
    scope='Twelve preselected exact coordinates, same seed and frozen generator rule. Separate runs at different search caps may grow differently; not continuation of identical gates and not proof of monotonic algorithmic improvement. Actual selected CNOTs differ from allowed caps. No additional optimization, truth-based selection or new measurement.')
dump(OUT/'n12_transfer/paired_budget_128_192.json',result)
print(json.dumps(summary,indent=2))
