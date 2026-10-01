#!/usr/bin/env python3
"""Corrected Casimir test.

The document's Module 8 formula  M -> sum_a [A_a,[A_a,M]]  is the Casimir
action only for REAL antisymmetric generators (its Module 6 antiCheck).
The actual Sigma matrices are anti-Hermitian (complex), for which the
correct positive-definite Casimir on Sym^2(128) (congruence action
M -> g M g^T) is:

    C'(M) = - sum_a ( A_a^2 M + 2 A_a M A_a^T + M (A_a^T)^2 )

This script builds C' and checks for eigenvalues {0:1, 48:1820, 64:6435}.
"""
import numpy as np, time, json
from functools import reduce

T0 = time.time()
def tick(name): print(f"[{time.time()-T0:9.1f}s] {name}", flush=True)

# ---- Modules 1-8 (Module 1 with the s3->I fix) ----
s1 = np.array([[0,1],[1,0]], complex); s2 = np.array([[0,-1j],[1j,0]], complex)
s3 = np.array([[1,0],[0,-1]], complex); I2 = np.eye(2, dtype=complex)
def gammaMat(k):
    j=(k+1)//2; pauli = s1 if k%2 else s2
    return reduce(np.kron, [pauli if i==j else (s3 if i<j else I2) for i in range(1,9)])
gammas = [gammaMat(k) for k in range(1,17)]
I256 = np.eye(256, dtype=complex)
g17 = reduce(np.dot, gammas)
PiMinus = (I256 - g17)/2
wM, VM = np.linalg.eigh(PiMinus)
P = VM[:, wM < 1e-8].conj().T
def projectToSplus(M): return P @ M @ P.conj().T
def Sigma(i, j): return projectToSplus(gammas[i-1] @ gammas[j-1] / 2)
allGens = [Sigma(i, j) for i in range(1,16) for j in range(i+1,17)]
A3 = np.stack(allGens)                      # (120,128,128)
S2 = np.einsum('gij,gjk->ik', A3, A3)        # sum_a A_a^2
S2T = S2.T                                  # sum_a (A_a^T)^2
tick("setup done (M1-M8)")

pairs = [(a,b) for a in range(128) for b in range(a,128)]
nSym = len(pairs)
Pall = np.array([a for a,b in pairs]); Qall = np.array([b for a,b in pairs])
svals = np.where(Pall == Qall, 1.0, 1.0/np.sqrt(2))

def assemble_row(Rsym_re):
    row = np.empty(nSym)
    dm = Pall == Qall
    row[dm] = Rsym_re[Pall[dm], Qall[dm]]
    od = ~dm
    row[od] = np.sqrt(2.0) * Rsym_re[Pall[od], Qall[od]]
    return row

# ---- Corrected Casimir matrix ----
C = np.zeros((nSym, nSym))
max_imag = 0.0
CHUNK = 256
for c0 in range(0, nSym, CHUNK):
    c1 = min(c0 + CHUNK, nSym)
    Pc, Qc, sc = Pall[c0:c1], Qall[c0:c1], svals[c0:c1]
    K = c1 - c0
    # V[k,i,j] = sum_a (A_a[i,p] A_a[j,q] + A_a[i,q] A_a[j,p])
    V1 = np.einsum('gik,gjk->kij', A3[:, :, Pc], A3[:, :, Qc])
    V2 = np.einsum('gik,gjk->kij', A3[:, :, Qc], A3[:, :, Pc])
    for t in range(K):
        p, q, s = int(Pc[t]), int(Qc[t]), float(sc[t])
        R = np.zeros((128,128), dtype=complex)
        if p == q:
            # M = E_pp: single-term basis vector, add each piece ONCE
            R[:, p] += s * S2[:, p]      # (sum A^2) M
            R[p, :] += s * S2T[p, :]    # M (sum (A^T)^2)
            R += 2.0 * s * V1[t]        # 2 sum A M A^T (V1==V2 here)
        else:
            R[:, q] += s * S2[:, p]     # (sum A^2) M
            R[:, p] += s * S2[:, q]
            R[p, :] += s * S2T[q, :]    # M (sum (A^T)^2)
            R[q, :] += s * S2T[p, :]
            R += 2.0 * s * (V1[t] + V2[t])  # 2 sum A M A^T
        R = -R
        Rs = (R + R.T)/2
        mi = np.max(np.abs(Rs.imag))
        if mi > max_imag: max_imag = mi
        C[c0+t] = assemble_row(Rs.real)
    del V1, V2
    if (c0 // CHUNK) % 4 == 0: tick(f"build {c1}/{nSym}")
tick("Casimir matrix built")
print("max|imag| =", max_imag, " C symmetry err =", np.max(np.abs(C - C.T)))

eig = np.linalg.eigvalsh((C + C.T)/2)
er = np.round(eig, 2)
uniq, counts = np.unique(er, return_counts=True)
print("distinct eigenvalues:", dict(zip(uniq.tolist(), counts.tolist())))
print("mult0 =", int(np.sum(er == 0.0)), " mult48 =", int(np.sum(er == 48.0)),
      " mult64 =", int(np.sum(er == 64.0)))
print("eig min/max:", eig.min(), eig.max())
