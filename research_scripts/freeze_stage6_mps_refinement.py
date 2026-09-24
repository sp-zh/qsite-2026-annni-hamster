import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
O=OUT/'floating_boundary_scan';p=O/'refined_jobs.json'
if p.exists():raise SystemExit('Frozen refinement retained')
coarse=json.loads((O/'coarse_analysis.json').read_text());assert len(coarse)==15
hs=[.3,.325,.35,.4,.5,.525,.55,.6,.7]
jobs=[dict(n=n,k=.8,h=h,chi=chi,initial=initial) for h in hs for n,chi,initial in [(96,128,'plus'),(128,128,'plus'),(128,256,'plus'),(128,256,'antiphase')]]
dump(p,jobs);dump(O/'refinement_selection.json',dict(time=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),coarse_sha=sha(O/'coarse_analysis.json'),h=hs,reason='First locking/tail/response change .30-.35; upper broad crossover .50-.70 from tail decay and changing model extrapolation with increasing field. Include.40 middle control and.70 exponential/high-field control. .025 spacing in lower and first upper neighborhood. No c-nearest1 selection.',upper_boundary_not_assumed=.5,maximum_refined_points=9,followup_trigger='Contradictory bond/init/size evidence -> .0125 local windows orN160/192, not posthoc forced c=1',pair_sampling='Midpointswithin2sitesofcenter; both ends central half; r<=N/3'))
old=json.loads((ROOT/'results/stage5_v1/floating_validation/sweep_stopping_checks.json').read_text());bad=[r for r in old if not r['configured_stopping_tolerances_met']];dump(O/'old_unconverged_dependencies.json',dict(rows=bad,main_slice_related=[r for r in bad if r['kappa']==.8],policy='Related fields covered by fresh main-slice refinements or explicit continued checkpoint followup; other old failures remain historical and cannot certify main slice'))
print(len(jobs),'MPS refinement jobs frozen')
