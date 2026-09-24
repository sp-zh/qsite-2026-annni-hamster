import sys,json
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage5_adapt import ROOT,OUT,dump,sha
from annni.upgrade_detection import train,controls,predict
from annni.upgrade_gates import observations,vector
import numpy as np
path=ROOT/'results/stage4_upgrade_v1/n12/index.json';points=json.loads(path.read_text());vectors=[vector(observations(np.load(ROOT/r['methods']['B3']['archive'])['state'],12)) for r in points];cfg=train(vectors,12);cfg.update(training='All old 60 N12 B3 clean selected states, now development only. Same training algorithm and D1 thresholds as N8; separate frozen dimension-specific PCA. No Stage5 test/noise inputs.',input_sha=sha(path),created_utc=datetime.now(timezone.utc).isoformat());dump(OUT/'n12_scaling/detection_frozen.json',cfg);dump(OUT/'n12_scaling/detection_controls.json',[dict(control=name,**predict(v,cfg)) for name,v in zip(['ferro','anti','plus','mixed'],controls(12))])
