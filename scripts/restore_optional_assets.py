"""Restore optional lossless Release assets. No simulation or pickle loading."""
from pathlib import Path
import argparse,gzip,hashlib,json,shutil,tempfile
R=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--download-dir',type=Path,required=True);a=p.parse_args()
 for row in json.loads((R/'provenance/optional_assets.json').read_text()):
  src=a.download_dir/row['download_asset']
  if not src.exists():print('Not downloaded (optional):',src.name);continue
  assert sha(src)==row['download_sha256'],src.name
  dest=(R/row['path']).resolve();assert dest.is_relative_to(R)
  if dest.exists():assert sha(dest)==row['sha256'],row['path'];continue
  dest.parent.mkdir(parents=True,exist_ok=True)
  with tempfile.NamedTemporaryFile(dir=dest.parent,delete=False) as tmp:
   temp=Path(tmp.name)
   with gzip.open(src,'rb') as f:shutil.copyfileobj(f,tmp)
  assert sha(temp)==row['sha256'],row['path'];temp.replace(dest);print('Restored:',row['path'])
if __name__=='__main__':main()
