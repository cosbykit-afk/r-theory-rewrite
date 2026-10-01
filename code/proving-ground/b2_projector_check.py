#!/usr/bin/env python3
"""B-2: Lagrange projector identities on the corrected Casimir C' (matrix-free).

Spectrum CHECKED numeric: {0:1, 48:1820, 64:6435} on Sym^2(128) (8256-dim).
Projectors:
  p0(M)  = (C'-48)(C'-64)M / 3072
  p48(M) = C'(64-C')M / 768
  p64(M) = C'(C'-48)M / 1024
Tests on >=8 random symmetric matrices M (real and complex):
  idempotence:  ||p_i(p_i(M)) - p_i(M)||
  orthogonality: ||p_i(p_j(M))||, i != j
  completeness:  ||p0+p48+p64 (M) - M||
Residuals reported as Frobenius norm relative to ||M|| (accept < 1e-6 relative).
"""
import numpy as np, time
from functools import reduce

T0 = time.time()
def tick(name): print(f"[{time.time()-T0:9.1f}s] {name}", flush=True)

# --- generator setup (same as diag_casimir.py, read-only reference) ---
s1 = np.array([[0,1],[1,0]], complex); s2 = np.array([[0,-1j],[1j,0]], complex)
s3 = np.array([[1,0],[0,-1]], complex); I2 = np.eye(2, dtype=complex)
def gammaMat(k):
    j=(k+1)//2; pauli = s1 if k%2 else s2
    return reduce(np.kron, [pauli if i==j else (s3 if i<j else I2) for i in range(1,9)])
gammas = [gammaMat(k) for k in range(1,17)]
I256 = np.eye(256, dtype=complex)
g17 = reduce(np.dot, gammas)
PiMinus=(I256-g17)/2
wM, VM = np.linalg.eigh(PiMinus)
P = VM[:, wM < 1e-8].conj().T
def Sigma(i, j): return P @ (gammas[i-1] @ gammas[j-1] / 2) @ P.conj().T
gens = {(i,j): Sigma(i,j) for i in range(1,17) for j in range(i+1,17)}
assert len(gens) == 120
A3 = np.stack([gens[k] for k in gens])
AT3 = np.transpose(A3, (0,2,1))
S2 = np.einsum('gij,gjk->ik', A3, A3)

def Cp(M):
    """C'(M) = -sum_a (A_a^2 M + 2 A_a M A_a^T + M (A_a^T)^2), matrix-free (batched BLAS)."""
    t1 = S2 @ M
    t3 = M @ S2.T
    t2 = ((A3 @ M) @ AT3).sum(axis=0)
    return -(t1 + 2*t2 + t3)

def p0(M):  return (Cp(Cp(M)) - 112*Cp(M) + 3072*M)/3072
def p48(M): return (64*Cp(M) - Cp(Cp(M)))/768
def p64(M): return (Cp(Cp(M)) - 48*Cp(M))/1024

tick("setup done")

rng = np.random.default_rng(20260922)
results = []
worst = {}
for t in range(10):
    X = rng.standard_normal((128,128)) + (1j*rng.standard_normal((128,128)) if t % 2 else 0)
    M = (X + X.T)/2
    nM = np.linalg.norm(M)
    q0, q48, q64 = p0(M), p48(M), p64(M)
    rows = {"trial": t, "complex": bool(t % 2), "||M||": nM}
    # idempotence
    for name, p, q in (("p0", p0, q0), ("p48", p48, q48), ("p64", p64, q64)):
        r = np.linalg.norm(p(q) - q)/nM
        rows[f"idem_{name}"] = r
    # orthogonality
    qs = {"p0": q0, "p48": q48, "p64": q64}
    names = list(qs)
    for i in range(3):
        for j in range(3):
            if i == j: continue
            ni, nj = names[i], names[j]
            r = np.linalg.norm(eval(f"{ni}(qs['{nj}'])"))/nM
            rows[f"orth_{ni}_{nj}"] = r
    # completeness
    rows["complete"] = np.linalg.norm(q0+q48+q64 - M)/nM
    results.append(rows)
    for k, v in rows.items():
        if isinstance(v, float):
            worst[k] = max(worst.get(k, 0.0), v)

print("\nWorst relative residuals over 10 trials:")
for k in sorted(worst):
    print(f"  {k:22s} {worst[k]:.3e}")
tick("done")

ok = all(v < 1e-6 for k, v in worst.items() if isinstance(v, float))
print("ALL RESIDUALS < 1e-6 (relative):", ok)
