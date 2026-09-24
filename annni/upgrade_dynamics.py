"""Second-order B/2-A-B/2, U=exp(-iHt), signed literal gates."""
import numpy as np
from .upgrade_gates import *
def trotter_gates(n,k,h,dt):
 g=[('RX',i,-h*dt) for i in range(n)]
 for d,c in [(1,-1),(2,k)]:
  for i in range(n):
   j=(i+d)%n;g += [('CNOT',i,j),('RZ',j,2*c*dt),('CNOT',i,j)]
 return g+[('RX',i,-h*dt) for i in range(n)]
