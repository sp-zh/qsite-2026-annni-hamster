"""Refuse silent tensor-network backend/version changes during resume."""
import sys,json,platform,importlib.metadata
from pathlib import Path
R=Path(__file__).resolve().parents[1];r=json.loads((R/'results/stage5_v1/verification/tn_environment.json').read_text())
assert platform.python_version()==r['python'],('Frozen TN Python',r['python'],platform.python_version())
for package,version in r['versions'].items():assert importlib.metadata.version(package)==version,(package,version,importlib.metadata.version(package))
print('Tensor-network frozen environment matched')
