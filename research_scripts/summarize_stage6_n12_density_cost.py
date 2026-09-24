"""Actual N12 density cost, separately from the earlier pilot extrapolation."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_io import measurement_rows
from annni.stage6_index_records import expand_measurement_record
points=measurement_rows((OUT/'end_to_end').glob('n12_*_index.json'))
records={}
for point in points:
    for entry in point['entries']:
        measurement=expand_measurement_record(entry['record'])
        for record in measurement['probability_records']:
            records[record['archive']]=record
rows=list(records.values())
assert len(points)==12 and len(rows)==72,(len(points),len(rows))
groups=[]
for p in [0,.01,.05]:
    subset=[r for r in rows if r['p']==p]
    groups.append(dict(p=p,unique_density_records=len(subset),
        summed_measured_seconds=sum(r['seconds'] for r in subset),
        max_trace_error=max(abs(r['trace_real']-1) for r in subset),
        max_hermiticity_error=max(r['hermiticity'] for r in subset),
        peak_process_rss_bytes=max(r['process_peak_rss_bytes'] for r in subset)))
dump(OUT/'n12_transfer/density_actual_cost.json',dict(coordinates=len(points),
    unique_density_records=len(rows),summed_measured_seconds=sum(r['seconds'] for r in rows),
    process_peak_rss_bytes=max(r['process_peak_rss_bytes'] for r in rows),groups=groups,
    records=[dict(archive=r['archive'],sha256=r['sha256'],p=r['p'],kappa=r['kappa'],h=r['h'],cnots=r['cnots'],seconds=r['seconds']) for r in rows],
    scope='Actual recorded density/probability wall timings, deduplicated by archive. Includes the pilot cache once. Not total pipeline wall time or a CPU-efficiency benchmark. Earlier density_batch_cost_estimate.json remains a labelled estimate. N12 positivity is supported by verified CPTP gates, not claimed full density eigenspectrum diagonalization.'))
print('N12 unique densities',len(rows),'actual summed seconds',sum(r['seconds'] for r in rows),'process peak bytes',max(r['process_peak_rss_bytes'] for r in rows))
