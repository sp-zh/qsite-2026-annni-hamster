import sys,argparse,csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_reference import *
from scipy.signal import find_peaks
parser=argparse.ArgumentParser();parser.add_argument('--sizes',nargs='+',type=int,default=[8,12,16]);args=parser.parse_args()
for n in args.sizes:
 rows=[];index={};ks=PLAN['atlas']['kappa_n8'] if n==8 else PLAN['atlas']['kappa_large']
 for k in ks:
  hs=sorted(set([round(float(h),6) for h in np.arange(.05,2.001,.05 if n==8 else .1)]+(PLAN['atlas']['low_h'] if .4<=k<=.6 else [])))
  curve=[record(n,k,h) for h in hs]
  if n==8:
   resp=abs(np.gradient([r['mx'] for r in curve],hs));peaks=find_peaks(resp)[0];top=sorted(peaks,key=lambda i:resp[i],reverse=True)[:2]
   extra=sorted(set(round(float(h),6) for i in top for h in np.arange(max(.01,hs[i]-.05),min(2,hs[i]+.050001),.0125))-set(hs))
   curve+= [record(n,k,h) for h in extra];curve=sorted(curve,key=lambda r:r['h'])
  index[str(k)]=curve;rows+=curve;dump(OUT/f'reference_atlas/slices_n{n}.json',index);progress('atlas',len(rows),f'.venv/bin/python scripts/run_stage6_atlas.py --sizes {n}',n=n,kappa=k)
 if n==8:
  low=[record(8,k,h) for k in PLAN['atlas']['low_kappa'] for h in PLAN['atlas']['low_h']];dump(OUT/'reference_atlas/low_field.json',low)
 print('atlas complete',n,len(rows),flush=True)
