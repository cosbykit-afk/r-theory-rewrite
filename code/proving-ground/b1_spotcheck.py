#!/usr/bin/env python3
"""B-1 spot-check (independent): attribute the worst forms' eigenspace content.

For the top-K worst forms (by merged residuals), recompute C'(v) from scratch
and test whether D = C'(v) - 48v is explained by a pure 64-eigenspace
component, i.e. C'(v) = 64 v (residual ~0), or a mixture. Also cross-checks
the parallel workers' residual numbers via an independent recomputation.
"""
import numpy as np, sys
from functools import reduce

W = "/home/hatch/workspace/wolfram/"
s1 = np.array([[0, 1], [1, 0]], complex)
s2 = np.array([[0, -1j], [1j, 0]], complex)
s3 = np.array([[1, 0], [0, -1]], complex)
I2 = np.eye(2, dtype=complex)

def gammaMat(k):
    j = (k + 1) // 2
    p = s1 if (k % 2 == 1) else s2
    return reduce(np.kron,
                  [p if i == j else (s3 if i < j else I2) for i in range(1, 9)])

gammas = [gammaMat(k) for k in range(1, 17)]
I256 = np.eye(256, dtype=complex)
g17 = reduce(np.dot, gammas)
wM, VM = np.linalg.eigh((I256 - g17) / 2)
P = VM[:, wM < 1e-8].conj().T
assert P.shape == (128, 256)

A = [P @ (gammas[i] @ gammas[j] / 2) @ P.conj().T
     for i in range(16) for j in range(i + 1, 16)]
assert len(A) == 120
# rho(A)M = A M + M A^T ; C'(M) = -sum_a rho(A_a)(rho(A_a)(M))
def cprime(M):
    R = np.zeros(M.shape, dtype=complex)
    for Aa in A:
        R -= (Aa @ (Aa @ M + M @ Aa.T) + (Aa @ M + M @ Aa.T) @ Aa.T)
    return R.real

m = np.load(W + 'b1_module12_resid_max.npy')
f = np.load(W + 'b1_module12_resid_frob.npy')
assert np.all(m >= 0) and np.all(f >= 0), "merge incomplete"
from itertools import combinations
quads = list(combinations(range(1, 17), 4))
forms = np.load(W + 'b1_module12_forms.npy')

K = int(sys.argv[1]) if len(sys.argv) > 1 else 5
top = np.argsort(m)[-K:][::-1]
print("global max over all 1820 forms: entrywise =", float(m.max()),
      "frobenius =", float(f.max()))
for t in top:
    v = forms[t]
    Cv = cprime(v)
    r48 = np.linalg.norm((Cv - 48 * v).ravel())
    r64 = np.linalg.norm((Cv - 64 * v).ravel())
    r0 = np.linalg.norm(Cv.ravel())
    nv2 = float(np.vdot(v, v).real)
    print(f"idx={int(t)} quad={quads[t]} worker_fro={f[t]:.6f} "
          f"||v||^2={nv2:.6f} ||C'v-48v||_F={r48:.3e} "
          f"||C'v-64v||_F={r64:.3e} ||C'v||_F={r0:.3e}")
