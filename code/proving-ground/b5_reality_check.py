#!/usr/bin/env python3
"""B-5: Reality question — is the 128 (half-spin of so(16)) representation real?

Method (numerical, fresh implementation):
  1. Build the 120 guarded so(16) generators (same construction as
     verify_independent.py: gamma matrices -> chiral projection -> S_ij).
  2. Frobenius-Schur indicator via the invariant bilinear form:
     find null space of G = sum_a L_a^dagger L_a,  L_a(B) = A_a^T B + B A_a,
     matrix-free with scipy eigsh. Null dim 1 + symmetric null vector
     => indicator +1 (real); antisymmetric => -1; no null => 0.
  3. If real: build the antilinear real structure J (J^2=+1, [J,A_a]=0),
     extract an explicit real orthonormal basis Q (J-fixed), form
     U = Q^dagger, and exhibit tildeA_a = U A_a U^dagger real antisymmetric.
  4. Module-8 consequence: in the real basis check the manuscript's encoded
     formula R(M) = sum_a[A_a,[A_a,M]] against the corrected congruence
     Casimir C'(M) = -(S2 M + M S2^T) - 2 sum_a A_a M A_a^T on random real
     symmetric matrices.

Reference scripts (run_modules.py, verify_independent.py, diag_casimir.py)
are READ-ONLY sources; this file is new.
"""
import numpy as np, time, json
from functools import reduce
from scipy.sparse.linalg import LinearOperator, eigsh

T0 = time.time()
def tick(n): print(f"[{time.time()-T0:9.1f}s] {n}", flush=True)

N = 128

# ---------- 1. generators (guarded so(16), from definitions) ----------
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
assert mx < 1e-9

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
keys = list(gen.keys())
A = np.stack([gen[k] for k in keys])          # (120,128,128)
AT = A.transpose(0, 2, 1)                      # A_a^T (NOT dagger)
ah = float(np.max(np.abs(A + A.transpose(0, 2, 1).conj())))
print("   anti-Hermitian err:", ah)
assert ah < 1e-9
tick("120 guarded generators built")

# ---------- 2. Frobenius-Schur: null space of G = sum L_a^dagger L_a ----------
# L_a(B) = A_a^T B + B A_a ;  L_a^dagger(W) = conj(A_a)^T W + W conj(A_a)^T
#        = -(A_a^T W + W A_a^T)  (A anti-Hermitian => conj(A) = -A^T)
def Gmv(v):
    Vc = v.reshape(N, N)
    W = (np.einsum('aij,jk->aik', AT, Vc)
         + np.einsum('jk,akl->ajl', Vc, A))
    out = -(np.einsum('aij,ajk->ik', AT, W)
            + np.einsum('aij,ajk->ik', W, AT))
    return out.ravel()

Gop = LinearOperator((N * N, N * N), matvec=Gmv, dtype=complex)
rng = np.random.default_rng(12345)
v0 = rng.standard_normal(N * N) + 1j * rng.standard_normal(N * N)
vals, vecs = eigsh(Gop, k=4, which='SM', tol=1e-10, maxiter=2000, v0=v0)
order = np.argsort(vals)
vals, vecs = vals[order], vecs[:, order]
print("2) smallest eigenvalues of G:", vals)
tick("eigsh done")
nconv = 4
lam1, lam2 = float(vals[0]), float(vals[1])
gap = lam2 - lam1 if lam2 > lam1 else 0.0

B = vecs[:, 0].reshape(N, N)
nB = float(np.linalg.norm(B))
# direct null check: max_a ||A_a^T B + B A_a||_F / ||B||_F
LB = np.einsum('aij,jk->aik', AT, B) + np.einsum('ij,ajk->aik', B, A)
null_resid = float(np.max(np.linalg.norm(LB, axis=(1, 2))) / nB)
sym_meas = float(np.linalg.norm(B - B.T) / nB)     # ~0 => symmetric
askew_meas = float(np.linalg.norm(B + B.T) / nB)   # ~0 => antisymmetric
print(f"   null residual (rel): {null_resid:.3e}")
print(f"   symmetric meas ||B-B^T||/||B||: {sym_meas:.3e}")
print(f"   antisymmetric meas ||B+B^T||/||B||: {askew_meas:.3e}")

# Frobenius-Schur indicator determination
sv = np.linalg.svd(B, compute_uv=False)
condB = float(sv[0] / sv[-1])
print(f"   cond(B) = {condB:.3e} (nondegenerate iff finite & modest)")
if null_resid < 1e-6 and lam1 < 1e-8 * max(1.0, lam2):
    if sym_meas < 1e-6:
        indicator, verdict = +1, "REAL (symmetric invariant bilinear form)"
    elif askew_meas < 1e-6:
        indicator, verdict = -1, "QUATERNIONIC (skew invariant bilinear form)"
    else:
        indicator, verdict = 0, "UNEXPECTED: null vector neither sym nor skew"
else:
    indicator, verdict = 0, "COMPLEX (no invariant bilinear form)"
print("   Frobenius-Schur indicator:", indicator, "-", verdict)
tick("indicator determined")

result = {
    "G_eigenvalues_4": [float(v) for v in vals],
    "null_residual_rel": null_resid,
    "sym_measure": sym_meas, "askew_measure": askew_meas,
    "cond_B": condB,
    "frobenius_schur_indicator": indicator, "verdict": verdict,
}

if indicator != +1:
    with open("b5_reality_result.json", "w") as f:
        json.dump(result, f, indent=1)
    print("INDICATOR != +1: no real basis. B-5 CLOSED as ruled-out/INCOMPLETE.")
    tick("done")
    raise SystemExit(0)

# ---------- 3. real structure J and explicit real basis ----------
Bs = (B + B.T) / 2
Bs /= np.linalg.norm(Bs)
Bsc = Bs.conj()
BB = Bsc @ Bs
c1 = float(np.trace(BB).real) / N
c1_dev = float(np.linalg.norm(BB - c1 * np.eye(N)) / abs(c1 * N))
print(f"3) Bbar B = c1 I check: c1 = {c1:.6f}, rel deviation {c1_dev:.3e}")
assert c1_dev < 1e-6 and c1 > 0

def Jay(v):
    # antilinear, J^2 = I; accepts a vector (128,) or a batch (...,128)
    return (np.einsum('ij,...j->...i', Bsc, v.conj())) / np.sqrt(c1)

rng2 = np.random.default_rng(999)
# J^2 = I check
mxj = 0.0
for _ in range(5):
    v = rng2.standard_normal(N) + 1j * rng2.standard_normal(N)
    mxj = max(mxj, float(np.max(np.abs(Jay(Jay(v)) - v))))
print("   max |J^2 v - v|:", mxj)
assert mxj < 1e-8
# [J, A_a] = 0 check on random vectors
mxc = 0.0
for _ in range(3):
    v = rng2.standard_normal(N) + 1j * rng2.standard_normal(N)
    Jv = Jay(v)
    lhs = np.einsum('aij,j->ai', A, Jv)          # A_a (J v)
    rhs = Jay(np.einsum('aij,j->ai', A, v))      # J (A_a v)
    mxc = max(mxc, float(np.max(np.abs(lhs - rhs))))
print("   max_a,v |J A_a v - A_a J v|:", mxc)
assert mxc < 1e-8
tick("real structure J verified (J^2=I, commutes with all 120 generators)")

# real orthonormal basis: u_i = e_i + J e_i, w_i = i(e_i - J e_i), real QR
E = np.eye(N, dtype=complex)
JE = np.stack([Jay(E[:, i]) for i in range(N)], axis=1)
U_ = E + JE
W_ = 1j * (E - JE)
Wbig = np.concatenate([U_, W_], axis=1)          # (128,256), all J-fixed
Rbig = np.vstack([Wbig.real, Wbig.imag])         # (256,256) real
Qr, _ = np.linalg.qr(Rbig)
rank = int(np.sum(np.abs(np.diag(_)) > 1e-10)) if False else None
Q = Qr[:N, :N] + 1j * Qr[N:, :N]                  # (128,128) complex
# unitarity + J-fixed columns checks
uni_err = float(np.max(np.abs(Q.conj().T @ Q - np.eye(N))))
jfix = float(np.max(np.abs(
    np.stack([Jay(Q[:, i]) for i in range(N)], axis=1) - Q)))
print(f"   Q unitarity err: {uni_err:.3e}, J-fixed columns err: {jfix:.3e}")
assert uni_err < 1e-10 and jfix < 1e-8
U = Q.conj().T
At = np.einsum('ij,ajk,lk->ail', U, A, U.conj())  # tildeA_a = U A_a U^dagger
imag_err = float(np.max(np.abs(At.imag)))
antisym_err = float(np.max(np.abs(At + At.transpose(0, 2, 1))))
print(f"4) max_a |Im(tildeA_a)|: {imag_err:.3e}")
print(f"   max_a |tildeA_a + tildeA_a^T| (real antisymmetric): {antisym_err:.3e}")
assert imag_err < 1e-8 and antisym_err < 1e-8
np.save("b5_real_basis.npy", U)
tick("real basis exhibited; 120 generators real antisymmetric")

result.update({
    "c1": c1, "c1_I_deviation_rel": c1_dev,
    "J_squared_err": mxj, "J_commutator_err": mxc,
    "Q_unitarity_err": uni_err, "Q_Jfixed_err": jfix,
    "real_basis_imag_err": imag_err, "real_basis_antisym_err": antisym_err,
})

# ---------- 4. Module-8 consequence in the real basis ----------
# manuscript encoded formula: R(M) = sum_a [A_a,[A_a,M]]  (M9: A^2M - 2AMA + MA^2)
# corrected congruence Casimir: C'(M) = -(S2 M + M S2^T) - 2 sum_a A_a M A_a^T
# In the real basis (tildeA^T = -tildeA): C' = -sum_a[tildeA_a,[tildeA_a,.]]
# so the manuscript's formula as encoded equals -C' there (sign note).
S2t = np.einsum('aij,ajk->ik', At, At)
rng3 = np.random.default_rng(31337)
worst = 0.0
for trial in range(6):
    X = rng3.standard_normal((N, N))
    M = (X + X.T) / 2                            # real symmetric
    N1 = (np.einsum('aij,jk->aik', At, M)
          - np.einsum('jk,akl->ajl', M, At))     # [tildeA_a, M]
    R = (np.einsum('aij,ajk->aik', At, N1)
         - np.einsum('aij,ajk->aik', N1, At)).sum(axis=0)   # sum[A,[A,M]]
    Cp = (-(S2t @ M + M @ S2t.T)
          - 2.0 * np.einsum('aij,jk,alk->il', At, M, At))    # C'(M)
    rel = float(np.linalg.norm(R + Cp) / np.linalg.norm(Cp))
    worst = max(worst, rel)
print(f"5) Module-8 check: worst rel ||R_manuscript + C'||/||C'|| over 6 trials: {worst:.3e}")
assert worst < 1e-10
tick("Module-8 consequence verified")
result["module8_worst_rel_R_plus_Cp"] = worst
result["module8_consequence"] = (
    "In the exhibited real basis the manuscript's encoded Module 8/9 formula "
    "R(M)=sum_a[A_a,[A_a,M]] equals -C'(M) (sign-corrected); -R is the Casimir "
    "with the CHECKED spectrum {0:1, 48:1820, 64:6435}. Manuscript formula "
    "rehabilitable up to the overall sign.")

with open("b5_reality_result.json", "w") as f:
    json.dump(result, f, indent=1)
print("RESULT:", json.dumps(result, indent=1)[:400], "...")
tick("B-5 COMPLETE")
