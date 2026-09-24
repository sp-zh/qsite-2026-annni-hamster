"""Exact joint probabilities with a reused all-X density representation.

Physical settings remain Z^N, X^N and X with two Y positions. Internally,
rho_X = H^N rho H^N. Replacing X measurement by Y uses W=RX(pi/2)H
on each of the two positions, since W H = RX(pi/2). This is a classical
change of representation, not additional executed measurement gates.
"""
import numpy as np
from .upgrade_gates import H,matrix,one_axis

def _probabilities(rho):
 p=rho.diagonal().real
 if p.min() < -1e-10:raise ArithmeticError('Negative probability beyond numerical tolerance')
 p=np.maximum(p,0)
 return p/p.sum()

def groups(rho):
 n=int(np.log2(len(rho)))
 if rho.shape!=(1<<n,1<<n):raise ValueError('Expected a square qubit density matrix')
 out={'Z'*n:_probabilities(rho)}
 rx=rho
 for i in range(n):
  rx=one_axis(rx,H,i,n)
  rx=one_axis(rx,H.conj(),i,n,n)
 out['X'*n]=_probabilities(rx)
 w=matrix(('RX',0,np.pi/2))@H
 for i in range(n-1):
  # Reuse the first changed site within this row of pairs as well.
  first=one_axis(rx,w,i,n);first=one_axis(first,w.conj(),i,n,n)
  for j in range(i+1,n):
   r=one_axis(first,w,j,n);r=one_axis(r,w.conj(),j,n,n)
   basis=['X']*n;basis[i]=basis[j]='Y'
   out[''.join(basis)]=_probabilities(r)
 return out
