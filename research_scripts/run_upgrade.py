#!/usr/bin/env python
import sys,json,time,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.upgrade_adapt import *
def compact(row):
 return {k:v for k,v in row.items() if k not in ['steps','checkpoints']}|dict(run_record=str(Path(row['archive']).with_suffix('.json')))
def progress(task,rows,start):
 dump(OUT/f'{task}/index.json',rows)
 dump(OUT/task/'progress.json',dict(last_kappa=rows[-1]['kappa'],last_h=rows[-1]['h'],completed=len(rows)))
 dump(OUT/'progress.json',dict(task=task,completed=len(rows),batch_seconds=time.perf_counter()-start,updated=datetime.now(timezone.utc).isoformat(),deadline=PLAN['deadline'],next_command=f'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python scripts/run_upgrade.py --task {task}'))
 print(task,len(rows),'seconds',round(time.perf_counter()-start,2),flush=True)
def main(task):
 start=time.perf_counter();rows=[]
 n=12 if task=='n12' else 8
 points=PLAN[{'development':'development','validation':'validation','heldout':'held_out','map':'final_map','n12':'slices'}[task]]
 for pi,(k,h) in enumerate(points):
  methods={};allmain=[];single=[];fixed=[]
  for seed in (PLAN['development_seeds'] if task=='development' else PLAN['map_seeds']):
   for ref in PLAN['refs']:
    r=adaptive(n,k,h,ref,seed,128,'cost',True,task);allmain.append(r)
    if task in ['development','heldout']:
     fixed.append(adaptive(n,k,h,ref,seed,128,'cost',True,task,fixed=True))
   if task in ['development','heldout']:
    single.append(adaptive(n,k,h,'plus',seed,128,'gradient',True,task))
  methods['B3']=select(allmain)
  if single:methods['B1']=select(single);methods['B2']=select(fixed)
  rows.append(dict(n=n,kappa=k,h=h,methods={m:compact(r) for m,r in methods.items()},candidates=[compact(r) for r in allmain+single+fixed]))
  if pi%5==0 or pi==len(points)-1:progress(task,rows,start)
 progress(task,rows,start)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--task',choices=['development','validation','heldout','map','n12'],required=True);a=p.parse_args();main(a.task)
