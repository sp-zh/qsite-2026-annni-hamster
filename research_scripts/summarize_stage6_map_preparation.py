"""Selected-state map counts from actual analyzed circuits; no new optimization."""
import sys,argparse,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
p=argparse.ArgumentParser();p.add_argument('--task',choices=['map','low_map'],default='map');a=p.parse_args()
source=OUT/f'n8_maps/{a.task}_analysis.json';points=json.loads(source.read_text())
rows=[];paired=[]
for r in points:
    methods={}
    for e in r['entries']:methods[e['method']]=e['preparation_quality']
    tol=16*np.finfo(float).eps
    regions=[]
    if .4-tol<=r['kappa']<=.6+tol and .01-tol<=r['h']<=.35+tol:regions.append('low_field')
    if .6-tol<=r['kappa']<=1+tol and .2-tol<=r['h']<=.7+tol:regions.append('antiphase_transition_band')
    for method,q in methods.items():rows.append(dict(kappa=r['kappa'],h=r['h'],regions=regions,method=method,**q))
    b,h=methods['B3'],methods['H6']
    paired.append(dict(kappa=r['kappa'],h=r['h'],regions=regions,outcome='both_pass' if b['joint_pass'] and h['joint_pass'] else 'H6_only_pass' if h['joint_pass'] else 'B3_only_pass' if b['joint_pass'] else 'both_fail'))
summary=[]
for region in ['all','low_field','antiphase_transition_band']:
    for method in ['B3','H6']:
        rr=[r for r in rows if r['method']==method and (region=='all' or region in r['regions'])]
        summary.append(dict(region=region,method=method,coordinates=len(rr),**{key:sum(r[key] for r in rr) for key in ['observable_pass','state_pass','joint_pass']}))
dump(OUT/f'n8_maps/{a.task}_selected_preparation_summary.json',dict(rows=rows,summary=summary,paired=paired,
    paired_counts=dict(collections.Counter(r['outcome'] for r in paired)),source=str(source.relative_to(ROOT)),source_sha256=sha(source),
    scope='Descriptive selected-state counts, not confirmation or independent phase labels. Rectangular regions may overlap; their counts must not be summed. Region point counts are not cell-intersection area weights; use the separate area summary. Machine-epsilon endpoint tolerance only. Main-map B3 circuits are historical reused; fresh Stage6 noise is distinguished in source indices. Candidate existence is not inferred from selected-state accuracy.'))
print(a.task,[(r['method'],r['joint_pass'],r['coordinates']) for r in summary if r['region']=='all'])
