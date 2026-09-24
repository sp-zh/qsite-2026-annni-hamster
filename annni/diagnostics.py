"""Frozen operational diagnostics, not a thermodynamic phase classifier."""
import json
from pathlib import Path
import numpy as np
from scipy.signal import find_peaks

CONFIG = Path(__file__).resolve().parents[1] / 'configs/diagnostics_v1.json'


def load_config():
    return json.loads(CONFIG.read_text())


def diagnose(structure_factor, mx, config=None):
    """Use full q-vector and Mx; mixed-like/ambiguous states remain degraded/uncertain."""
    config = load_config() if config is None else config
    sf = np.asarray(structure_factor, dtype=float)
    n = len(sf)
    if sf.ndim != 1 or n % 4 or not np.all(np.isfinite(sf)) or not np.isfinite(mx):
        raise ValueError('Finite complete structure factor with N divisible by four required')
    feature = np.array([sf[0], 2*sf[n//4], float(mx)])
    labels = ['ferro_like', 'antiphase_like', 'paramagnetic_like', 'degraded']
    prototypes = np.array([[1,0,0], [0,1,0], [1/n,2/n,1], [1/n,2/n,0]])
    distance = np.linalg.norm(prototypes-feature, axis=1)
    ranking = np.argsort(distance, kind='stable')
    best = ranking[0]
    margin = float(distance[ranking[1]]-distance[best])
    accepted = distance[best] <= config['prototype_max_distance'] and margin >= config['prototype_min_margin']
    return dict(label=labels[best] if accepted else 'uncertain', nearest_control=labels[best],
                features=feature.tolist(), distances=dict(zip(labels, distance.tolist())),
                margin=margin, ferro_score=float((sf[0]-1/n)/(1-1/n)),
                antiphase_score=float((sf[n//4]-1/n)/(.5-1/n)), transverse_score=float(mx))


def folded_peaks(structure_factor, config=None):
    config = load_config() if config is None else config
    sf = np.asarray(structure_factor, dtype=float)
    n = len(sf)
    indices = np.arange(n//2+1)
    folded = (sf[indices]+sf[(-indices)%n])/2
    tolerance = max(config['near_peak_absolute_tolerance'], config['near_peak_relative_tolerance']*float(folded.max()))
    near = indices[folded >= folded.max()-tolerance]
    return [dict(k=int(k), partner_k=int((-k)%n), q_over_pi=float(2*k/n),
                 value=float(folded[k]), gap_from_max=float(folded.max()-folded[k]),
                 unique_global_max=bool(len(near)==1)) for k in near]


def local_peaks(x, y, support=None):
    """All strict/plateau local maxima and one-sided endpoint maxima; preserve NaNs."""
    x, y = np.asarray(x), np.asarray(y)
    finite = np.isfinite(y)
    rows = []
    # Work on each contiguous finite segment; never interpolate across missing values.
    starts = np.flatnonzero(finite & ~np.r_[False, finite[:-1]])
    ends = np.flatnonzero(finite & ~np.r_[finite[1:], False])
    for start, end in zip(starts, ends):
        segment = y[start:end+1]
        chosen = set((find_peaks(segment, plateau_size=True)[0]+start).tolist())
        if len(segment)==1 or segment[0]>segment[1]: chosen.add(int(start))
        if len(segment)>1 and segment[-1]>segment[-2]: chosen.add(int(end))
        for i in sorted(chosen):
            lo, hi = (x[max(start,i-1)], x[min(end,i+1)]) if support is None else support[i]
            rows.append(dict(index=int(i), coordinate=float(x[i]), value=float(y[i]),
                             interval_low=float(lo), interval_high=float(hi),
                             endpoint=bool(i in (start,end)),
                             step=float(np.median(np.diff(x))) if len(x)>1 else None))
    return rows


def validate_dataset(d):
    n = int(d['n']); shape=(len(d['kappa']),len(d['h']))
    assert d['structure_factor'].shape == (*shape,n)
    assert d['correlations'].shape == (*shape,n)
    assert d['chi_f'].shape == (shape[0],shape[1]-1)
    np.testing.assert_allclose(d['h_mid'],(d['h'][:-1]+d['h'][1:])/2)
    np.testing.assert_allclose(d['structure_factor'],np.fft.fft(d['correlations'],axis=-1).real/n,atol=1e-12)
    np.testing.assert_allclose(d['structure_factor'].sum(axis=-1),1,atol=1e-12)
    if d['h'][0]==0:
        assert np.all(np.isnan(d['chi_f'][:,0]))
        if 'states' in d: assert np.all(np.isnan(d['states'][:,0]))
    return True
