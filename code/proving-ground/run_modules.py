#!/usr/bin/env python3
"""Faithful NumPy/SciPy port of the 12 Wolfram modules from Wolfram.pdf.

Convention: WL 1-based indices in comments; 0-based in code.
Prints the same association outputs as the WL modules, plus timings.
Results are also saved to results.json.
"""
import numpy as np, time, json
from functools import reduce
from itertools import permutations, combinations

T0 = time.time()
def tick(name):
    print(f"[{time.time()-T0:9.1f}s] {name}", flush=True)

out = {}

# ---------------- Module 1: Pauli and Gamma Kernel ----------------
s1 = np.array([[0, 1], [1, 0]], dtype=complex)
s2 = np.array([[0, -1j], [1j, 0]], dtype=complex)
s3 = np.array([[1, 0], [0, -1]], dtype=complex)

def gammaMat(k):  # k = 1..16 (WL 1-based)
    # FIX for Module 1 bug in the document: slots *after* the Pauli position
    # must be IdentityMatrix[2], not s3, for {Gi,Gj} = 2*d_ij to hold.
    j = (k + 1) // 2                      # Ceiling[k/2]
    pauli = s1 if (k % 2 == 1) else s2    # If[OddQ[k], s1, s2]
    I2 = np.eye(2, dtype=complex)
    factors = [pauli if i == j else (s3 if i < j else I2) for i in range(1, 9)]
    return reduce(np.kron, factors)       # KroneckerProduct @@ factors

out["M1"] = {"s1": s1.shape, "s2": s2.shape, "s3": s3.shape}
tick("Module 1 done")

# ---------------- Module 2: Build 16 Gamma Matrices ----------------
gammas = [gammaMat(k) for k in range(1, 17)]
out["M2"] = {"NumGammas": len(gammas), "GammaDim": gammas[0].shape}
tick("Module 2 done")

# ---------------- Module 3: Clifford Algebra and Chirality Operator ----------------
I256 = np.eye(256, dtype=complex)
cliffordOK = True
for i in range(16):
    for j in range(16):
        lhs = gammas[i] @ gammas[j] + gammas[j] @ gammas[i] \
              - (2.0 if i == j else 0.0) * I256
        if np.max(np.abs(lhs)) >= 1e-10:
            cliffordOK = False
            print("  Clifford FAIL at", i + 1, j + 1, flush=True)

g17 = reduce(np.dot, gammas)  # Dot @@ gammas = g1.g2.....g16
hermitian_g17 = np.max(np.abs(g17 - g17.conj().T))
gamma17Sq = np.max(np.abs(g17 @ g17 - I256)) < 1e-10
gamma17Anti = np.max(np.abs(g17 @ gammas[0] + gammas[0] @ g17)) < 1e-10
out["M3"] = {"CliffordOK": bool(cliffordOK),
             "Gamma17Squared": bool(gamma17Sq),
             "Gamma17Anticommutes": bool(gamma17Anti),
             "g17_hermiticity_err": float(hermitian_g17)}
tick("Module 3 done")

# ---------------- Module 4: Chirality Projectors and Spinor Basis ----------------
PiPlus = (I256 + g17) / 2
PiMinus = (I256 - g17) / 2
wP, _ = np.linalg.eigh(PiPlus)
rankPiPlus = int(np.sum(wP > 0.5))
wM, VM = np.linalg.eigh(PiMinus)
rankPiMinus = int(np.sum(wM > 0.5))
P = VM[:, wM < 1e-8].conj().T   # orthonormal rows spanning ker(PiMinus); (128,256)
dimSplus = P.shape[0]
# sanity: P rows orthonormal, and P spans the +1 eigenspace of PiPlus
ortho_err = np.max(np.abs(P @ P.conj().T - np.eye(dimSplus)))

def projectToSplus(M):
    return P @ M @ P.conj().T

out["M4"] = {"RankPiPlus": rankPiPlus, "RankPiMinus": rankPiMinus,
             "DimSplus": int(dimSplus), "P_orthonormality_err": float(ortho_err)}
tick("Module 4 done")

# ---------------- Module 5: Charge Conjugation Matrix B ----------------
Bmat = reduce(np.dot, [gammas[2 * j] for j in range(8)])  # g1.g3.....g15
BmatInv = np.linalg.inv(Bmat)
chargeConjOK = True
for i in range(16):
    lhs = Bmat @ gammas[i] @ BmatInv + gammas[i].T
    if np.max(np.abs(lhs)) >= 1e-8:
        chargeConjOK = False
        print("  ChargeConj FAIL at", i + 1, flush=True)
BmatPlus = PiPlus @ Bmat @ PiPlus
out["M5"] = {"ChargeConjugationOK": bool(chargeConjOK), "BmatDim": Bmat.shape}
tick("Module 5 done")

# ---------------- Module 6: so(16) Generators and Commutation Sample ----------------
def Sigma(i, j):  # WL 1-based, unguarded (matches WL definition exactly)
    return projectToSplus(gammas[i - 1] @ gammas[j - 1] / 2)

commOK = True
antiOK = True
S_cache = {}
def Sget(i, j):
    if (i, j) not in S_cache:
        S_cache[(i, j)] = Sigma(i, j)
    return S_cache[(i, j)]

for i in range(1, 5):
    for j in range(i + 1, 6):
        Sij = Sget(i, j)
        if np.max(np.abs(Sij + Sij.T)) >= 1e-8:
            antiOK = False
        for k in range(1, 5):
            for l in range(k + 1, 6):
                lhs = (Sij @ Sget(k, l) - Sget(k, l) @ Sij
                       - ((1.0 if j == k else 0.0) * Sget(i, l)
                          - (1.0 if i == k else 0.0) * Sget(j, l)
                          - (1.0 if j == l else 0.0) * Sget(i, k)
                          + (1.0 if i == l else 0.0) * Sget(j, k)))
                if np.max(np.abs(lhs)) >= 1e-8:
                    commOK = False
out["M6"] = {"CommutationOK": bool(commOK), "SigmaAntisymmetric": bool(antiOK),
             "NumGenerators": 120}
tick("Module 6 done")

# ---------------- Module 7: Symmetric Square Basis Construction ----------------
pairs = [(a, b) for a in range(128) for b in range(a, 128)]  # WL order
nSym = len(pairs)
Pall = np.array([a for a, b in pairs])
Qall = np.array([b for a, b in pairs])
svals = np.where(Pall == Qall, 1.0, 1.0 / np.sqrt(2))
out["M7"] = {"BasisSize": nSym, "ExpectedSize": 8256,
             "Match": bool(nSym == 8256)}
tick("Module 7 done")

# ---------------- Module 8: Casimir Action Function ----------------
allGens = [Sigma(i, j) for i in range(1, 16) for j in range(i + 1, 17)]
assert len(allGens) == 120
A3 = np.stack(allGens)                      # (120,128,128), complex
S = np.einsum('gij,gjk->ik', A3, A3)        # sum_g A_g^2, done once
out["M8"] = {"NumGenerators": len(allGens), "CasimirActionDefined": True,
             "max_imag_allGens": float(np.max(np.abs(A3.imag))),
             "max_imag_S": float(np.max(np.abs(S.imag)))}
tick("Module 8 done")

def assemble_row(Rsym_re):
    """Coefficients of a real symmetric 128x128 matrix in the orthonormal
    symmetric basis: Tr(R.Q_m) = R[c,c] on diagonals, sqrt(2)*R[c,d] off-diag."""
    row = np.empty(nSym)
    dm = Pall == Qall
    row[dm] = Rsym_re[Pall[dm], Qall[dm]]
    od = ~dm
    row[od] = np.sqrt(2.0) * Rsym_re[Pall[od], Qall[od]]
    return row

# ---------------- Module 9: Casimir Matrix Build ----------------
# R = sum_g (A_g^2 M - 2 A_g M A_g + M A_g^2), M = s*(E_pq + E_qp).
# A_g^2 M + M A_g^2 via S = sum A_g^2 (O(n^2)); the -2 A M A term via einsum.
C = np.zeros((nSym, nSym))
max_imag_R = 0.0
CHUNK = 256
for c0 in range(0, nSym, CHUNK):
    c1 = min(c0 + CHUNK, nSym)
    Pc, Qc, sc = Pall[c0:c1], Qall[c0:c1], svals[c0:c1]
    K = c1 - c0
    E1 = np.einsum('gik,gkj->kij', A3[:, :, Pc], A3[:, Qc, :])
    E2 = np.einsum('gik,gkj->kij', A3[:, :, Qc], A3[:, Pc, :])
    U = E1 + E2
    del E1, E2
    for t in range(K):
        p, q, s = int(Pc[t]), int(Qc[t]), float(sc[t])
        R = np.zeros((128, 128), dtype=complex)
        R[:, q] += s * S[:, p]
        R[:, p] += s * S[:, q]
        R[p, :] += s * S[q, :]
        R[q, :] += s * S[p, :]
        R -= 2.0 * s * U[t]
        Rs = (R + R.T) / 2
        mi = np.max(np.abs(Rs.imag))
        if mi > max_imag_R:
            max_imag_R = mi
        C[c0 + t] = assemble_row(Rs.real)
    del U
    if (c0 // CHUNK) % 4 == 0:
        tick(f"Module 9 progress {c1}/{nSym}")
sym_err = np.max(np.abs(C - C.T))
out["M9"] = {"CasimirMatrixDim": C.shape,
             "max_imag_Rsym": float(max_imag_R),
             "C_symmetry_err": float(sym_err)}
tick("Module 9 done")

# ---------------- Module 10: Eigenvalues and Multiplicities ----------------
Csym = (C + C.T) / 2
del C
eigVals = np.linalg.eigvalsh(Csym)
eigRounded = np.round(eigVals, 2)
uniq = np.unique(eigRounded)
mult0 = int(np.sum(eigRounded == 0.0))
mult48 = int(np.sum(eigRounded == 48.0))
mult64 = int(np.sum(eigRounded == 64.0))
out["M10"] = {"DistinctEigenvalues": [float(v) for v in uniq],
              "Mult0": mult0, "Mult48": mult48, "Mult64": mult64,
              "eig_min": float(eigVals.min()), "eig_max": float(eigVals.max())}
tick("Module 10 done")

# ---------------- Module 11: Projectors and Verification ----------------
# C is real symmetric => diagonalizable; verify projector identities on the
# spectrum (equivalent to the WL matrix-polynomial checks).
def p1(x): return (x - 48.0) * (x - 64.0) / (48.0 * 64.0)
def p1820(x): return x * (64.0 - x) / 768.0
def p6435(x): return x * (x - 48.0) / 1024.0
lam = eigVals
rankP1 = int(round(np.sum(p1(lam))))
rankP1820 = int(round(np.sum(p1820(lam))))
rankP6435 = int(round(np.sum(p6435(lam))))
idem1820 = float(np.max(np.abs(p1820(lam) ** 2 - p1820(lam)))) < 1e-6
idem6435 = float(np.max(np.abs(p6435(lam) ** 2 - p6435(lam)))) < 1e-6
orthog = float(np.max(np.abs(p1820(lam) * p6435(lam)))) < 1e-6
complete = float(np.max(np.abs(p1(lam) + p1820(lam) + p6435(lam) - 1.0))) < 1e-6
out["M11"] = {"RankP1": rankP1, "RankP1820": rankP1820, "RankP6435": rankP6435,
              "P1820Idempotent": bool(idem1820), "P6435Idempotent": bool(idem6435),
              "Orthogonal": bool(orthog), "Complete": bool(complete)}
tick("Module 11 done")

# ---------------- Module 12: Clifford 4-Form Embedding and Image Check ----------------
def gamma4(i, j, k, l):  # WL 1-based; antisymmetrized product / 24
    total = np.zeros((256, 256), dtype=complex)
    for pr in permutations([i, j, k, l]):
        inv = sum(1 for a in range(4) for b in range(a + 1, 4) if pr[a] > pr[b])
        sgn = -1.0 if (inv % 2) else 1.0
        total += sgn * reduce(np.dot, [gammas[x - 1] for x in pr])
    return total / 24.0

def apply_P1820(vec):
    # P1820 = C(64I - C)/768 applied matrix-free
    return (Csym @ (64.0 * vec - Csym @ vec)) / 768.0

g4sample = projectToSplus(gamma4(1, 2, 3, 4))
gamma4Sym = np.max(np.abs(g4sample - g4sample.T)) < 1e-6
quadruples = list(combinations(range(1, 17), 4))
sampleVerify = []
for quad in quadruples[:10]:
    g4 = projectToSplus(gamma4(*quad))
    vec = assemble_row(((g4 + g4.T) / 2).real)
    sampleVerify.append(float(np.max(np.abs(apply_P1820(vec) - vec))))
imageOK = max(sampleVerify) < 1e-5
out["M12"] = {"Gamma4Symmetric": bool(gamma4Sym),
              "NumQuadruples": len(quadruples),
              "ImageInP1820": bool(imageOK),
              "max_sampleVerify": max(sampleVerify),
              "Lambda2ImageDim": 120, "Lambda4ImageDim": 1820}
tick("Module 12 done")

print(json.dumps(out, indent=1, default=str))
with open("/home/hatch/workspace/wolfram/results.json", "w") as f:
    json.dump(out, f, indent=1, default=str)
print("ALL MODULES DONE", flush=True)
