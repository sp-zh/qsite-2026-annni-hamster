import numpy as np
from pathlib import Path
from annni.diagnostics import diagnose, folded_peaks, local_peaks, validate_dataset


def test_controls_distinguish_mixed_from_plus():
    for n in [8,12,16]:
        sf=np.zeros(n);sf[0]=1
        assert diagnose(sf,0)['label']=='ferro_like'
        sf=np.zeros(n);sf[n//4]=sf[3*n//4]=.5
        assert diagnose(sf,0)['label']=='antiphase_like'
        assert diagnose(np.ones(n)/n,1)['label']=='paramagnetic_like'
        assert diagnose(np.ones(n)/n,0)['label']=='degraded'


def test_equivalent_peaks_and_near_ties():
    sf=np.zeros(8);sf[2]=sf[6]=.3;sf[1]=sf[7]=.28
    peaks=folded_peaks(sf)
    assert {p['k'] for p in peaks}=={1,2}
    assert peaks[1]['partner_k']==6
    assert peaks[1]['value']==.3
    assert len(folded_peaks(np.ones(8)/8))==5


def test_all_local_peaks_and_endpoints_missingness():
    x=np.arange(8.)
    peaks=local_peaks(x,[np.nan,4,1,3,1,2,1,3])
    assert [p['index'] for p in peaks]==[1,3,5,7]
    assert peaks[0]['endpoint'] and peaks[-1]['endpoint']
    assert not peaks[1]['endpoint']


def test_baseline_hmid_nan_fft_contract():
    root=Path(__file__).resolve().parents[1]/'results/baseline'
    for path in root.glob('*.npz'):
        assert validate_dataset(dict(np.load(path)))
