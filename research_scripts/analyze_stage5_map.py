import sys,json,csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_adapt import *
from annni.upgrade_detection import predict
old=list(csv.DictReader(open(ROOT/'results/stage4_upgrade_v1/matched_grid.csv')));old={(round(float(r['kappa']),6),round(float(r['h']),6),float(r['p'])):r for r in old if r['method']=='B3'};new=json.loads((OUT/'n8_maps/noise_index.json').read_text());rows=[];cfg=json.loads((ROOT/'results/stage4_upgrade_v1/detection/frozen.json').read_text())
for r in new:
 for nr in r['B5']:
  a=np.load(ROOT/nr['archive']);v=vector(dict(correlations=a['correlations'],structure_factor=a['structure_factor'],mx=float(a['mx'])));o=old[(round(r['kappa'],6),round(r['h'],6),nr['p'])];rows.append(dict(kappa=r['kappa'],h=r['h'],p=nr['p'],B0_error=float(o['epsilon_c_old']),B3_error=float(o['epsilon_c_new']),B5_error=nr['epsilon_c_total'],B0_pass=o['old_pass']=='True',B3_pass=o['new_pass']=='True',B5_pass=nr['prep_joint_pass'],B5_cnots=nr['cnots'],selection_unresolved=r['selection_unresolved'],**predict(v,cfg)))
summ=[]
for p in [0,.01,.05]:
 a=[r for r in rows if r['p']==p]
 for method in ['B0','B3','B5']:
  vals=np.array([r[method+'_error'] for r in a]);summ.append(dict(p=p,method=method,count=len(a),error_mean=float(vals.mean()),error_quantiles=np.quantile(vals,[0,.25,.5,.75,1]).tolist(),B5_paired_wins=int(sum(r['B5_error']<r[method+'_error'] for r in a)),common_pass_count=sum(r['B5_pass'] and r[method+'_pass'] for r in a),common_pass_B5_error_mean=float(np.mean([r['B5_error'] for r in a if r['B5_pass'] and r[method+'_pass']])),common_pass_baseline_error_mean=float(np.mean([r[method+'_error'] for r in a if r['B5_pass'] and r[method+'_pass']])),paired_error_difference_quantiles=np.quantile([r['B5_error']-r[method+'_error'] for r in a],[0,.25,.5,.75,1]).tolist()))
dump(OUT/'n8_maps/comparison.json',dict(rows=rows,summary=summ));print(summ)
