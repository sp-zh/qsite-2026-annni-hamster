"""Exact Pauli Lie closure on the real wall register; no finite-depth guarantee."""
import sys,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annni.stage6_common import *
from annni.stage6_candidates import words_pool
rows=[]
for m in [3,4,7]:
 t=time.perf_counter();gens=[]
 for word in words_pool(m+1,'wall'):
  word=word[1:];x=sum((p in 'XY')<<j for j,p in enumerate(word));z=sum((p in 'ZY')<<j for j,p in enumerate(word));gens.append((x,z))
 seen=set(gens);queue=collections.deque(gens)
 while queue:
  x,z=queue.popleft()
  for a,b in gens:
   if ((x&b).bit_count()+(z&a).bit_count())%2:
    v=(x^a,z^b)
    if v not in seen:seen.add(v);queue.append(v)
 expected=(4**m-2**m)//2;assert len(seen)==expected and all((x&z).bit_count()%2==1 for x,z in seen)
 rows.append(dict(wall_register_qubits=m,physical_qubits=m+1,initial_generators=len(gens),lie_dimension=len(seen),real_SO_dimension=expected,seconds=time.perf_counter()-t))
dump(OUT/'verification/wall_pool_lie_closure.json',dict(rows=rows,meaning='Exact commutator closure spans all odd-Y Pauli generators, hence full real antisymmetric algebra for these finite registers. N8 has full real-state reachability in its global-flip-even wall representation with unrestricted depth. Does NOT prove reachability at64/96/128CNOT, successful greedy search, or N12 verification.',n12_full_closure='not_run'));print(rows)
