import sys,json,argparse,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_adapt import *
from annni.stage5_selection import *
from annni.stage5_e2e import *
from annni.stage5_hva_baseline import baseline_arm
p=argparse.ArgumentParser();p.add_argument('--task',choices=['refined','full_sv','n12'],default='refined');args=p.parse_args();O=OUT/'end_to_end';rows=[];start=time.perf_counter();cfg=json.loads((OUT/'selector_frozen.json').read_text())['selector'];historical=json.loads((ROOT/'results/stage4_upgrade_v1/map/index.json').read_text());oldhva=json.loads((ROOT/'results/stage3_v1/grid/selection_frozen.json').read_text())['rows']
coords=json.loads((O/'grid_refinement_frozen.json').read_text())['coordinates'] if args.task=='refined' else PLAN['final_map'] if args.task=='full_sv' else PLAN['n12_mitigation_points']
# Uniform refinement; no extra anchor coordinates repeated.
for ii,(k,h) in enumerate(coords):
 n=12 if args.task=='n12' else 8;selectionfile=OUT/'selector_benchmark'/('n12_192' if n==12 else 'map')/f'n{n}_k{k:.6f}_h{h:.6f}.json'
 if not selectionfile.exists():selectionfile=OUT/'selector_benchmark/refined'/f'n{n}_k{k:.6f}_h{h:.6f}.json'
 selected=json.loads(selectionfile.read_text());arms={}
 for name,record in [('B3',selected['B3']),('B5',selected['B5'])]:
  a=np.load(ROOT/record['archive']);c=record['selected'];arms[name]=dict(n=n,kappa=k,h=h,state=a['state'],ed_vector=vector(observations(a['ed_state'],n)),gates=compile_circuit(n,record['ref'],c['words'],c['params']),joint_pass=record['joint_pass'])
 if args.task=='refined':arms['B0']=baseline_arm(k,h)
 entries=[]
 for noise in [0,.01,.05]:
  combos=[('B0','raw'),('B3','raw'),('B5','raw'),('B5','zne'),('B5','sv')] if args.task=='refined' else [('B5','sv')] if args.task=='full_sv' else [('B5','raw'),('B5','sv')]
  for name,method in combos:entries.append(dict(arm=name+'_'+method,record=measured(arms[name],noise,method)))
 rows.append(dict(n=n,kappa=k,h=h,entries=entries,B0_source=arms.get('B0',{}).get('source')));dump(O/(args.task+'_index.json'),rows);print(args.task,ii+1,len(coords),round(time.perf_counter()-start,2),flush=True)
