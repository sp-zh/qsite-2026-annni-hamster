"""Compact index copies; immutable full scientific metadata remains hash-linked.

Only redundant cache keys and CNOT-order lists are omitted from batch indices.
They remain in the original per-computation JSON, alongside the unchanged NPZ.
No simulator, estimator, random stream or cache identity is changed.
"""
from .stage6_common import ROOT,sha

def _link(record,omit):
    path=(ROOT/record['archive']).with_suffix('.json')
    result={k:v for k,v in record.items() if k not in omit}
    result.update(metadata_record=str(path.relative_to(ROOT)),metadata_sha256=sha(path),
                  index_representation='compact_copy_full_metadata_linked_v1')
    return result

def compact_measurement_record(record):
    result=_link(record,{'key'})
    result['probability_records']=[_link(r,{'key','cnot_order'}) for r in record['probability_records']]
    return result

def expand_measurement_record(record):
    """Verified access to all original keys/gates when a consumer needs them."""
    if 'metadata_record' not in record:
        return record
    import json
    path=ROOT/record['metadata_record']
    assert sha(path)==record['metadata_sha256'],('Metadata changed',str(path))
    original=json.loads(path.read_text())
    assert (original['archive'],original['sha256'])==(record['archive'],record['sha256'])
    return original
