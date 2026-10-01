#!/usr/bin/env python3
"""Diagnostics for the Casimir anomaly: verify the representation and centrality."""
import numpy as np, time
from functools import reduce

T0 = time.time()
def tick(name): print(f"[{time.time()-T0:9.1f}s] {name}", flush=True)

s1 = np.array([[0,1],[1,0]], complex); s2 = np.array([[0,-1j],[1j,0]], complex)
s3 = np.array([[1,0],[0,-1]], complex); I2 = np.eye(2, dtype=complex)
def gammaMat(k):
    j=(k+1)//2; pauli = s1 if k%2 else s2
    return reduce(np.kron, [pauli if i==j else (s3 if i<j else I2) for i in range(1,9)])
gammas = [gammaMat(k) for k in range(1,17)]
I256 = np.eye(256, dtype=complex)
g17 = reduce(np.dot, gammas)
PiPlus=(I256+g17)/2; PiMinus=(I256-g17)/2
wM, VM = np.linalg.eigh(PiMinus)
P = VM[:, wM < 1e-8].conj().T
def Sigma(i, j): return P @ (gammas[i-1] @ gammas[j-1] / 2) @ P.conj().T
tick("setup done")

# 1) S+ invariance under ALL Gamma_i Gamma_j
mx = 0.0
for i in range(1,17):
    for j in range(i+1,17):
        v = np.max(np.abs(PiMinus @ (gammas[i-1]@gammas[j-1]) @ PiPlus))
        mx = max(mx, v)
print("1) max ||PiMinus GiGj PiPlus|| over all i<j:", mx)
tick("invariance checked")

# 2) so(16) commutators for ALL generator pairs (skip diagonal artifact)
gens = {}
for i in range(1,17):
    for j in range(i+1,17):
        gens[(i,j)] = Sigma(i,j)
def Sget(i,j):
    if i==j: return np.eye(128, dtype=complex)/2   # unguarded WL definition
    if i<j: return gens[(i,j)]
    return -gens[(j,i)]
mx = 0.0; worst=None
keys = list(gens.keys())
for (i,j) in keys:
    A = gens[(i,j)]
    for (k,l) in keys:
        if (i,j)==(k,l): continue
        B = gens[(k,l)]
        rhs = ((1.0 if j==k else 0.0)*Sget(i,l) - (1.0 if i==k else 0.0)*Sget(j,l)
               - (1.0 if j==l else 0.0)*Sget(i,k) + (1.0 if i==l else 0.0)*Sget(j,k))
        v = np.max(np.abs(A@B - B@A - rhs))
        if v > mx: mx, worst = v, ((i,j),(k,l))
print("2) max commutator violation (all pairs, off-diagonal):", mx, "worst:", worst)
tick("commutators checked")

# 3) Centrality of C' (matrix-free) on random symmetric M
A3 = np.stack([gens[k] for k in keys])
AT3 = np.transpose(A3, (0,2,1))
S2 = np.einsum('gij,gjk->ik', A3, A3)
def Cp(M):
    # -sum_a (A_a^2 M + 2 A_a M A_a^T + M (A_a^T)^2)
    t1 = S2 @ M
    t3 = M @ S2.T
    t2 = np.einsum('gij,jk,gkl->il', A3, M, AT3)
    return -(t1 + 2*t2 + t3)
rng = np.random.default_rng(0)
for trial in range(3):
    X = rng.standard_normal((128,128)) + 1j*rng.standard_normal((128,128))
    M = (X + X.T)/2
    b = keys[rng.integers(len(keys))]
    Bm = gens[b]
    rhoM = Bm @ M + M @ Bm.T
    lhs = Cp(rhoM)
    rhs = Bm @ Cp(M) + Cp(M) @ Bm.T
    print(f"3) centrality trial {trial} (gen {b}): max|[C',rho]| =",
          np.max(np.abs(lhs-rhs)), " scale:", np.max(np.abs(lhs)))
tick("centrality checked")
