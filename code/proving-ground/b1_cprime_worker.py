#!/usr/bin/env python3
"""B-1 worker: apply corrected C' to a slice of forms.

Usage: b1_cprime_worker.py <idx_npy> <out_max_npy> <out_frob_npy>
Rebuilds gammas/projector/generators/A3/S2 (same construction as
b1_module12_image_check.py), loads forms, applies
C'(V) = -(S2 V + V S2T) - 2 sum_g A_g V A_g^T to forms[idx],
writes per-form entrywise-max and Frobenius residuals of C'(v)-48v.
"""
import numpy as np, time, sys
from functools import reduce

T0 = time.time()
def tick(n): print(f"[{time.time()-T0:9.1f}s] {n}", flush=True)

idx = np.load(sys.argv[1])
out_max_p, out_frob_p = sys.argv[2], sys.argv[3]
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
PiMinus = (I256 - g17) / 2
wM, VM = np.linalg.eigh(PiMinus)
P = VM[:, wM < 1e-8].conj().T
assert P.shape == (128, 256)

def projectToSplus(M):
    return P @ M @ P.conj().T

gen = {}
for i in range(1, 17):
    for j in range(i + 1, 17):
        gen[(i, j)] = projectToSplus(gammas[i - 1] @ gammas[j - 1] / 2)
keys = list(gen.keys())
A3 = np.stack([gen[k] for k in keys])
S2 = np.einsum('gij,gjk->ik', A3, A3)
S2T = S2.T
tick(f"setup done ({len(idx)} forms assigned)")

forms = np.load(W + "b1_module12_forms.npy")
V = forms[idx]
K = len(idx)
R = -(S2 @ V + V @ S2T)
for a in range(120):
    Aa = A3[a]
    Wm = Aa @ V
    R -= 2.0 * (Wm @ Aa.T)
    del Wm
    if (a + 1) % 30 == 0:
        tick(f"generators {a+1}/120")
D = R.real - 48.0 * V
rmax = np.max(np.abs(D), axis=(1, 2))
rfrob = np.linalg.norm(D.reshape(K, -1), axis=1)
np.save(out_max_p, rmax)
np.save(out_frob_p, rfrob)
tick(f"worker done: max residual = {float(rmax.max()):.3e}")
