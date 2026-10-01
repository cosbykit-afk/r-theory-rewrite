#!/usr/bin/env python3
"""Independent verification of the corrected R-Theory Casimir pipeline.

Fresh implementation written from the definitions (not a re-run of
run_modules.py / test_casimir2.py):
  1. gamma matrices rebuilt -> Clifford relations checked
  2. guarded so(16) generators (S_ii = 0, antisymmetric extension) ->
     commutation checked on ALL 120-generator pairs
  3. demonstrates the original Module 6 break: unguarded Sigma(i,i) = I/2
     fails exactly the 10 diagonal (i,j)=(k,l) cases with violation 1.0
  4. corrected Casimir C'(M) = -sum_a (A_a^2 M + 2 A_a M A_a^T + M (A_a^T)^2)
     assembled fresh, then cross-checked entry-by-entry against the literal
     operator definition on random symmetric matrices
  5. spectrum of the assembled matrix computed independently
"""
import numpy as np, time
from functools import reduce

T0 = time.time()
def tick(n): print(f"[{time.time()-T0:9.1f}s] {n}", flush=True)

# ---------- 1. gamma matrices ----------
s1 = np.array([[0, 1], [1, 0]], complex)
s2 = np.array([[0, -1j], [1j, 0]], complex)
s3 = np.array([[1, 0], [0, -1]], complex)
I2 = np.eye(2, dtype=complex)

def gamma(k):  # k = 1..16
    j = (k + 1) // 2
    p = s1 if (k % 2 == 1) else s2
    return reduce(np.kron,
                  [p if i == j else (s3 if i < j else I2) for i in range(1, 9)])

G = [gamma(k) for k in range(1, 17)]
I256 = np.eye(256, dtype=complex)
mx = 0.0
for i in range(16):
    for j in range(i, 16):
        r = G[i] @ G[j] + G[j] @ G[i] - (2.0 if i == j else 0.0) * I256
        mx = max(mx, float(np.max(np.abs(r))))
print("1) Clifford max violation:", mx)
assert mx < 1e-9, "Clifford failed"

g17 = reduce(np.dot, G)
PiM = (I256 - g17) / 2
w, V = np.linalg.eigh(PiM)
P = V[:, w < 1e-8].conj().T
assert P.shape == (128, 256)

def proj(M):
    return P @ M @ P.conj().T

gen = {}
for i in range(1, 17):
    for j in range(i + 1, 17):
        gen[(i, j)] = proj(G[i - 1] @ G[j - 1] / 2)

ah = max(float(np.max(np.abs(A + A.conj().T))) for A in gen.values())
print("   max |A + A^dagger| (anti-Hermitian check):", ah)
assert ah < 1e-9

def Sget(i, j):  # guarded: S_ii = 0, antisymmetric extension
    if i == j:
        return np.zeros((128, 128), complex)
    return gen[(i, j)] if i < j else -gen[(j, i)]

tick("setup done: Clifford OK, 120 guarded generators built")

# ---------- 2. so(16) on ALL pairs ----------
keys = list(gen.keys())
mx = 0.0
worst = None
for (i, j) in keys:
    A = gen[(i, j)]
    for (k, l) in keys:
        B = gen[(k, l)]
        rhs = ((1.0 if j == k else 0.0) * Sget(i, l)
               - (1.0 if i == k else 0.0) * Sget(j, l)
               - (1.0 if j == l else 0.0) * Sget(i, k)
               + (1.0 if i == l else 0.0) * Sget(j, k))
        v = float(np.max(np.abs(A @ B - B @ A - rhs)))
        if v > mx:
            mx, worst = v, ((i, j), (k, l))
print("2) so(16) all-pairs (7140) max violation:", mx, "worst:", worst)
assert mx < 1e-8, "so(16) failed"
tick("so(16) verified on all pairs")

# ---------- 3. exhibit the original Module 6 break ----------
# Unguarded WL definition: Sigma(i,i) = P (G_i G_i / 2) P^dagger = I_128 / 2.
I128o2 = np.eye(128, dtype=complex) / 2
def Sun(i, j):
    if i == j:
        return I128o2
    return gen[(i, j)] if i < j else -gen[(j, i)]

mxd = 0.0
for i in range(1, 5):
    for j in range(i + 1, 6):
        A = Sun(i, j)
        rhs = (Sun(i, j) - Sun(j, j) - Sun(j, j) + Sun(j, i))
        # = S_ij - I/2 - I/2 - S_ij = -I  (LHS [A,A] = 0)
        mxd = max(mxd, float(np.max(np.abs(A @ A - A @ A - rhs))))
print("3) original unguarded encoding: 10 diagonal cases max violation:", mxd,
      "(analytic expectation exactly 1.0)")
assert abs(mxd - 1.0) < 1e-9
tick("Module 6 break exhibited")

# ---------- 4. corrected Casimir, fresh assembly ----------
A3 = np.stack([gen[k] for k in keys])            # (120,128,128)
S2 = np.einsum('gij,gjk->ik', A3, A3)            # sum_a A_a^2
S2T = S2.T                                      # sum_a (A_a^T)^2
pairs = [(a, b) for a in range(128) for b in range(a, 128)]
n = len(pairs)
Pa = np.array([a for a, b in pairs])
Qa = np.array([b for a, b in pairs])
sv = np.where(Pa == Qa, 1.0, 1.0 / np.sqrt(2))

def row_of(R):
    r = np.empty(n)
    d = Pa == Qa
    r[d] = R[Pa[d], Qa[d]].real
    o = ~d
    r[o] = np.sqrt(2.0) * R[Pa[o], Qa[o]].real
    return r

C = np.zeros((n, n))
CH = 256
for c0 in range(0, n, CH):
    c1 = min(c0 + CH, n)
    Pc, Qc, sc = Pa[c0:c1], Qa[c0:c1], sv[c0:c1]
    K = c1 - c0
    W1 = np.einsum('gik,gjk->kij', A3[:, :, Pc], A3[:, :, Qc])
    W2 = np.einsum('gik,gjk->kij', A3[:, :, Qc], A3[:, :, Pc])
    for t in range(K):
        p, q, s = int(Pc[t]), int(Qc[t]), float(sc[t])
        R = np.zeros((128, 128), dtype=complex)
        if p == q:
            # basis matrix is E_pp (single, NOT doubled): each piece once
            R[:, p] += S2[:, p]
            R[p, :] += S2T[p, :]
            R += 2.0 * W1[t]
        else:
            R[:, q] += s * S2[:, p]
            R[:, p] += s * S2[:, q]
            R[q, :] += s * S2T[p, :]
            R[p, :] += s * S2T[q, :]
            R += 2.0 * s * (W1[t] + W2[t])
        R = -R
        C[c0 + t] = row_of((R + R.T) / 2)
    del W1, W2
    if (c0 // CH) % 4 == 0:
        tick(f"Casimir build {c1}/{n}")
print("4) C symmetry err:", float(np.max(np.abs(C - C.T))))
tick("Casimir matrix built")

# ---------- 5. cross-check vs literal operator definition ----------
def Cprime_def(M):
    out = -(S2 @ M + M @ S2T)
    for a in range(120):
        Aa = A3[a]
        out -= 2.0 * (Aa @ M @ Aa.T)
    return out

rng = np.random.default_rng(7)
mx = 0.0
mxi = 0.0
for trial in range(4):
    X = rng.standard_normal((128, 128))
    M = (X + X.T) / 2
    Lop = Cprime_def(M)
    mxi = max(mxi, float(np.max(np.abs(Lop.imag))))
    mx = max(mx, float(np.max(np.abs(C @ row_of(M) - row_of(Lop)))))
print("5) definition cross-check: max |C v - row(C'(M))| =", mx,
      " max|imag| of C'(M) =", mxi)
assert mx < 1e-8 and mxi < 1e-8
tick("assembly matches literal definition")

# ---------- 6. spectrum ----------
ev = np.linalg.eigvalsh((C + C.T) / 2)
er = np.round(ev, 2)
u, c = np.unique(er, return_counts=True)
spec = {float(k): int(v) for k, v in zip(u, c)}
print("6) spectrum:", spec)
m0, m48, m64 = (int(np.sum(er == 0.0)), int(np.sum(er == 48.0)),
                int(np.sum(er == 64.0)))
print("   mult0 =", m0, " mult48 =", m48, " mult64 =", m64)
ok = m0 == 1 and m48 == 1820 and m64 == 6435 and len(spec) == 3
print("SPECTRUM {0:1, 48:1820, 64:6435} CONFIRMED:", ok)
assert ok
tick("INDEPENDENT VERIFICATION COMPLETE")
