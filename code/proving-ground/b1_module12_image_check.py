#!/usr/bin/env python3
"""B-1: Module 12 image check on the CORRECTED Casimir operator.

Original M12 (run_modules.py) failed on the wrong encoded Casimir:
ImageInP1820=false, max_sampleVerify=21.0. Here we rebuild the 1820
projectToSplus(gamma4(i,j,k,l)) exactly as in run_modules.py M12 and apply
the corrected C'(M) = -sum_a (A_a^2 M + 2 A_a M A_a^T + M (A_a^T)^2)
(matrix-free, batched over all 1820 forms), checking C'(v) = 48 v per form.

Accept (per breakage-followup-log.md B-1): max over 1820 forms of
|C'(v) - 48v| reported; CLOSED if < 1e-6 (CHECKED numeric), else
INCOMPLETE/INVALID with worst cases logged.

Read-only w.r.t. existing scripts: all construction logic replicated here
under a new name.
"""
import numpy as np, time, json
from functools import reduce
from itertools import permutations, combinations

T0 = time.time()
def tick(n): print(f"[{time.time()-T0:9.1f}s] {n}", flush=True)

# ---------- Modules 1-4 (fixed M1 convention, as in run_modules.py) ----------
s1 = np.array([[0, 1], [1, 0]], complex)
s2 = np.array([[0, -1j], [1j, 0]], complex)
s3 = np.array([[1, 0], [0, -1]], complex)
I2 = np.eye(2, dtype=complex)

def gammaMat(k):  # k = 1..16
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
assert P.shape == (128, 256), P.shape

def projectToSplus(M):
    return P @ M @ P.conj().T
tick("Modules 1-4 setup done")

# ---------- 120 so(16) generators (guarded) ----------
gen = {}
for i in range(1, 17):
    for j in range(i + 1, 17):
        gen[(i, j)] = projectToSplus(gammas[i - 1] @ gammas[j - 1] / 2)
keys = list(gen.keys())
assert len(keys) == 120
A3 = np.stack([gen[k] for k in keys])           # (120,128,128)
S2 = np.einsum('gij,gjk->ik', A3, A3)           # sum_a A_a^2
S2T = S2.T                                      # sum_a (A_a^T)^2
tick("120 generators + S2 built")

# ---------- 1820 projected gamma-4-forms (as run_modules.py M12) ----------
def gamma4_perm(i, j, k, l):  # literal run_modules.py formula (permutations/24)
    total = np.zeros((256, 256), dtype=complex)
    for pr in permutations([i, j, k, l]):
        inv = sum(1 for a in range(4) for b in range(a + 1, 4) if pr[a] > pr[b])
        sgn = -1.0 if (inv % 2) else 1.0
        total += sgn * reduce(np.dot, [gammas[x - 1] for x in pr])
    return total / 24.0

quads = list(combinations(range(1, 17), 4))
assert len(quads) == 1820

# checkpoint: reuse forms built by an earlier (killed) run if present
import os
forms_ckpt = "/home/hatch/workspace/wolfram/b1_module12_forms.npy"
trip_ckpt = "/home/hatch/workspace/wolfram/b1_module12_tripwires.json"
if os.path.exists(forms_ckpt):
    forms = np.load(forms_ckpt)
    assert forms.shape == (1820, 128, 128)
    with open(trip_ckpt) as f:
        twj = json.load(f)
    max_anti, max_imag = twj["tripwire_anti"], twj["tripwire_imag"]
    print("tripwire max |proj - proj^T| over 1820 forms:", max_anti)
    print("tripwire max |imag| of symmetrized forms:", max_imag)
    norms = np.linalg.norm(forms.reshape(1820, -1), axis=1)
    tick("1820 forms loaded from checkpoint")
else:
    # tripwire: permutation-sum == sorted product for distinct indices
    tw = 0.0
    for q in quads[:5]:
        i, j, k, l = q
        tw = max(tw, float(np.max(np.abs(
            gamma4_perm(i, j, k, l) - gammas[i-1] @ gammas[j-1] @ gammas[k-1] @ gammas[l-1]))))
    print("tripwire gamma4_perm == G_i G_j G_k G_l (first 5 quads):", tw)
    assert tw < 1e-9

    forms = np.empty((1820, 128, 128), dtype=float)
    max_anti = 0.0   # symmetrization tripwire
    max_imag = 0.0   # realness tripwire
    for t, (i, j, k, l) in enumerate(quads):
        g4 = gammas[i-1] @ gammas[j-1] @ gammas[k-1] @ gammas[l-1]
        pr = projectToSplus(g4)
        max_anti = max(max_anti, float(np.max(np.abs(pr - pr.T))))
        M = (pr + pr.T) / 2
        max_imag = max(max_imag, float(np.max(np.abs(M.imag))))
        forms[t] = M.real
        if (t + 1) % 455 == 0:
            tick(f"forms built {t+1}/1820")
    np.save(forms_ckpt, forms)
    with open(trip_ckpt, "w") as f:
        json.dump({"tripwire_anti": float(max_anti),
                   "tripwire_imag": float(max_imag)}, f)
    tick("1820 forms built + checkpoint saved")
print("tripwire max |proj - proj^T| over 1820 forms:", max_anti)
print("tripwire max |imag| of symmetrized forms:", max_imag)
norms = np.linalg.norm(forms.reshape(1820, -1), axis=1)
print("form norms: min =", float(norms.min()), "max =", float(norms.max()))
n_zero = int(np.sum(norms <= 1e-6))
n_nz = 1820 - n_zero
print(f"collapsed (zero) forms: {n_zero}; nonzero: {n_nz}")
# span of the nonzero symmetrized forms (CHECKED structural fact)
if n_nz:
    svn = np.linalg.svd(forms.reshape(1820, -1)[norms > 1e-6], compute_uv=False)
    span_rank = int(np.sum(svn > 1e-6))
    print("span rank of nonzero forms (tol 1e-6):", span_rank)
    print("singular values all equal (orthogonal set):",
          bool(np.allclose(svn, svn[0], rtol=1e-9)))
else:
    span_rank = 0

# ---------- corrected C' matrix-free, ONE batch over unfinished forms ----------
# (single large batch per generator maximizes BLAS efficiency; residuals
#  checkpointed so a killed run resumes only the unfinished forms)
resid_ckpt = "/home/hatch/workspace/wolfram/b1_module12_resid_max.npy"
frob_ckpt = "/home/hatch/workspace/wolfram/b1_module12_resid_frob.npy"
if os.path.exists(resid_ckpt):
    per_form_max = np.load(resid_ckpt)
    per_form_fro = np.load(frob_ckpt)
    tick(f"residual checkpoint found: {int(np.sum(per_form_max >= 0))}/1820 forms done")
else:
    per_form_max = np.full(1820, -1.0)
    per_form_fro = np.full(1820, -1.0)

todo = np.where(per_form_max < 0)[0]
tick(f"C' batch: {len(todo)} unfinished forms in one batch")
if len(todo):
    V = forms[todo]                               # (K,128,128) real
    R = -(S2 @ V + V @ S2T)
    for a in range(120):
        Aa = A3[a]
        W = Aa @ V                                # (K,128,128) complex
        R -= 2.0 * (W @ Aa.T)
        del W
        if (a + 1) % 30 == 0:
            tick(f"C' generators {a+1}/120")
    D = R.real - 48.0 * V
    per_form_max[todo] = np.max(np.abs(D), axis=(1, 2))
    per_form_fro[todo] = np.linalg.norm(D.reshape(len(todo), -1), axis=1)
    del R, V, D
    np.save(resid_ckpt, per_form_max)
    np.save(frob_ckpt, per_form_fro)
    tick("C' batch done + checkpoint saved")
assert np.all(per_form_max >= 0)
worst = int(np.argmax(per_form_max))
print("B-1 RESULT: max |C'(v)-48v| over 1820 forms (entrywise) =",
      float(per_form_max.max()))
print("            max |C'(v)-48v| over 1820 forms (Frobenius) =",
      float(per_form_fro.max()))
print("            worst form index:", worst, "quad:", quads[worst],
      "residual:", float(per_form_max[worst]))
print("            10 worst (idx, residual):",
      [(int(i), float(per_form_max[i]))
       for i in np.argsort(per_form_max)[-10:][::-1]])

# ---------- span check: do the 1820 forms span the 48-eigenspace? ----------
sv = np.linalg.svd(forms.reshape(1820, -1), compute_uv=False)
rank = int(np.sum(sv > 1e-6))
print("span check: singular values min/max =", float(sv.min()), float(sv.max()))
print("span check: rank of 1820 forms at tol 1e-6 =", rank)

res = {
    "max_residual_entrywise": float(per_form_max.max()),
    "max_residual_frobenius": float(per_form_fro.max()),
    "worst_quad": [int(x) for x in quads[worst]],
    "min_form_norm": float(norms.min()),
    "n_zero_forms": n_zero,
    "n_nonzero_forms": n_nz,
    "nonzero_span_rank": span_rank,
    "nonzero_norm_all_equal": bool(n_nz and np.allclose(norms[norms > 1e-6], norms[norms > 1e-6][0], rtol=1e-9)),
    "tripwire_anti": float(max_anti),
    "tripwire_imag": float(max_imag),
    "forms_rank": rank,
    "pass": bool(per_form_max.max() < 1e-6),
}
with open("/home/hatch/workspace/wolfram/b1_module12_result.json", "w") as f:
    json.dump(res, f, indent=1)
print("PASS (< 1e-6):", res["pass"])
print(json.dumps(res, indent=1))
tick("B-1 DONE")
