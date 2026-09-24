"""Small-PBC observable traces at supported large-OBC candidate centers; no label transfer."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.upgrade_adapt import *
from annni.upgrade_gates import *
grade=json.loads((OUT/'floating/evidence_grading.json').read_text());rows=[]
for g in grade['rows']:
 if g['evidence_grade']!='supported_in_tested_window':continue
 for n in [8,12]:
  state,e,source=reference(n,g['kappa'],g['h']);ob=observations(state,n);sf=ob['structure_factor'];folded=sf[:n//2+1];near=np.flatnonzero(folded>=.95*max(folded))
  r=dict(n=n,kappa=g['kappa'],h=g['h'],bc='PBC',ED_source=source,ed={key:value.tolist() if isinstance(value,np.ndarray) else value for key,value in ob.items()},near_peak_q=(2*np.pi*near/n).tolist(),peak_equivalence='q and 2pi-q identified; peaks within 5% of strongest retained',large_OBC_q=g['q'],discrete_spacing=2*np.pi/n,circuit_noise=[])
  source=OUT/('map' if n==8 else 'n12')/'noise_index.json'
  for point in json.loads(source.read_text()):
   if abs(point['kappa']-g['kappa'])<1e-10 and abs(point['h']-g['h'])<1e-10:
    records=point['methods']['B3'] if n==8 else point['noise']
    for entry in records:
     a=np.load(ROOT/entry['archive']);r['circuit_noise'].append(dict(p=entry['p'],prep_pass=entry['prep_joint_pass'],cnots=entry['cnots'],correlations=a['correlations'].tolist(),structure_factor=a['structure_factor'].tolist(),mx=float(a['mx']),epsilon_c_total=entry['epsilon_c_total']))
  rows.append(r)
dump(OUT/'floating/small_periodic_bridge.json',dict(rows=rows,claim='Large-OBC evidence is not a small-PBC phase label. Discrete small-system q cannot resolve the fitted large-N wavevectors; observables and their gate-noise attenuation are only finite-size traces. Missing circuit entries mean not executed, never ED substituted as circuit output.'))
print('Saved',len(rows),'small-periodic comparisons')
