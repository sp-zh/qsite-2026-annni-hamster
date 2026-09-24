"""Opt-in original B3 energy optimization; never called by the notebook/release checks."""
import sys,argparse,json,datetime
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
p=argparse.ArgumentParser();p.add_argument('--compute',action='store_true',required=True);p.add_argument('--kappa',type=float,required=True);p.add_argument('--h',type=float,required=True);p.add_argument('--seed',type=int,default=11);p.add_argument('--budget',type=int,default=128);p.add_argument('--out',default='build/research');p.add_argument('--minutes',type=float,default=20);a=p.parse_args()
from annni import upgrade_adapt as engine
from annni.upgrade_gates import compile_circuit
root=Path(__file__).resolve().parents[1];out=(root/a.out).resolve();assert out.is_relative_to(root/'build')
engine.OUT=out;engine.OUT.mkdir(parents=True,exist_ok=True);engine.PLAN=dict(engine.PLAN);engine.PLAN['deadline']=(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(minutes=a.minutes)).isoformat();engine.dump(out/'run_config.json',dict(vars(a),scientific_plan=engine.PLAN,scope='opt-in original B3; new output, not archival results'))
runs=[engine.adaptive(8,a.kappa,a.h,ref,a.seed,budget=a.budget,group='explicit_release_recompute') for ref in ['plus','ghz','antiphase']];selected=engine.select(runs);s=selected['selected'];engine.dump(out/'selected.json',dict(selected=selected,gates=compile_circuit(8,selected['ref'],s['words'],s['params']),runs=runs));print(out/'selected.json')
