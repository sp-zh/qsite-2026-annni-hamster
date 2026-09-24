import numpy as np
from annni.stage3_diagnostics import derivative_no_gaps,feature_peaks
from annni.stage3 import CFG

def test_no_gap_bridging_and_flat_unresolved():
    h=np.arange(40)*.05+.05;y=np.tanh((h-.7)*10)
    valid=np.ones(40,bool);valid[12:16]=False
    d=derivative_no_gaps(h,y,valid)
    assert np.isnan(d[12:16]).all()
    flags=np.zeros(40,bool)
    _,peaks=feature_peaks(h,1e-6*y,np.ones(40,bool),flags,flags,flags,CFG['diagnostics'])
    assert not any(r['resolved'] for r in peaks)

def test_branch_switch_suppresses_claim_not_raw_peak():
    h=np.arange(40)*.05+.05;y=np.tanh((h-.7)*10)
    valid=np.ones(40,bool);switch=np.zeros(40,bool);switch[13]=True
    checked=np.zeros(40,bool)
    _,peaks=feature_peaks(h,y,valid,switch,checked,checked,CFG['diagnostics'])
    assert any('unchecked_branch_switch' in r['reasons'] for r in peaks)
    assert any(abs(r['h']-.7)<.1 for r in peaks)
