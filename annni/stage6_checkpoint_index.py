"""Monotone measurement-index checkpoints during cached batch replay."""
import json
from pathlib import Path
from .stage6_common import dump

def measurement_signature(row):
    return (row['n'],row['kappa'],row['h'],tuple(sorted(
        (e['method'],e['estimator'],e['record']['p'],e['record']['archive'],
         e['record']['sha256'],e['record'].get('metadata_sha256'))
        for e in row['entries'])))

def save_measurement_prefix(path, rows):
    """Never replace an already complete prefix with a shorter cached replay.

    Already saved scientific fingerprints must agree. A changed configuration
    needs a new index/run rather than silent replacement of prior results.
    """
    path=Path(path)
    if path.exists():
        old=json.loads(path.read_text())
        assert all(measurement_signature(a)==measurement_signature(b)
                   for a,b in zip(old,rows)), 'Existing measurement-index fingerprints differ'
        if len(rows)<len(old):
            return False
    dump(path,rows)
    return True
