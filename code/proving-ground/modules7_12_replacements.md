# Modules 7–12 — Clean-Slate Replacements

Clean-slate rebuild of the R Theory audit's Modules 7–12 (2026-09-24).
The original encodings of M8–M12 are INVALID (ledger §1); M7 as encoded is fine.
Each module below: (a) intent, (b) diagnosis, (c) corrected replacement,
(d) verification plan. Status labels per Kit's rule:
PROVED / CHECKED / ASSERTED / PROPOSED / INCOMPLETE / REFUTED.

Verified framework built on (cited, not re-derived):
- **C′(M) = −Σ_a(A_a²M + 2A_aMA_aᵀ + M(A_aᵀ)²)** — PROVED (independent, exact
  matrix-algebra expansion) to be the Casimir of the congruence action
  g·M = gMgᵀ on Sym²(128). (Ledger §1, B-4 addendum.)
- **Spectrum {0:1, 48:1820, 64:6435}** — PROVED analytic (B-6, CLOSED 2026-09-24;
  PROOFS_Casimir.md K-1..K-9). Sym²(128) = ℂs ⊕ F ⊕ V(2ω₈), dims 1+1820+6435.
- **Corrected Module 6** — guarded Σ-matrix (S_ii=0, antisymmetric extension);
  restricted generators A_ij = Π₊ΓᵢΓⱼ/2 Π₊, 120 of them, 128×128;
  so(16) relations on all 7140 pairs CHECKED numeric (max violation 0.0).
  Generators are anti-Hermitian (CHECKED) but NOT real antisymmetric
  (|A+Aᵀ| error 1.0, CHECKED) — this is what breaks the manuscript's M8 formula.
- **B-2 CLOSED** — Lagrange projectors for {0,48,64} idempotent, pairwise
  orthogonal, complete on C′ (CHECKED numeric, worst rel. residuals ~3e-16).
- **B-1 CLOSED** — the manuscript's M12 image claim is REFUTED on the corrected
  operator: trichotomy 896 zero + 140 pure-48 + 784 pure-64, 0 mixed (CHECKED).
- **B-5 CLOSED** — the 128 is real (Frobenius–Schur indicator +1); explicit real
  structure J and real basis exhibited; all 120 generators real antisymmetric
  (~1e-15); in that basis the manuscript's M8 formula R(M)=Σ_a[A_a,[A_a,M]]
  equals −C′(M) (CHECKED, worst rel. 5.4e-16).

Volume IV stays parked per instructions: no volume-iv* file was read or used.

---

## M7′ — Symmetric-square basis (original M7 as encoded: CHECKED, retained)

(a) **Intent.** Construct the computational basis of Sym²(128) — the 8256-dimensional
space of symmetric 128×128 matrices — as an explicit orthonormal basis in which the
Casimir operator can be assembled as a matrix. Pure infrastructure: without a basis,
Modules 8–11 cannot be stated computationally.

(b) **Diagnosis.** No failure. `BasisSize = 8256 = expected 8256` (CHECKED, ledger §1).
The encoding — pairs (a,b) with a≤b, 1/√2 normalization off-diagonal — is the standard
orthonormal basis under ⟨A,B⟩ = Tr(AB). All downstream failures were in M8's operator,
not M7's basis.

(c) **Corrected replacement (M7′).**
*Definition.* Let {e_a}_{a=1}^{128} be the standard basis of ℂ¹²⁸. For 1≤a≤b≤128:
E_{aa} = e_a e_aᵀ,   E_{ab} = (e_a e_bᵀ + e_b e_aᵀ)/√2 (a<b).
*Claim.* {E_{ab}} is an orthonormal basis of Sym²(ℂ¹²⁸) under the Frobenius inner
product; dim = 128·129/2 = 8256. **PROVED** (exact combinatorics for the count;
Tr(E_{ab}E_{cd}) = δ_{(a,b),(c,d)} by direct computation).
*Coordinate map.* For real symmetric M: coefficients c_{ab} = Tr(ME_{ab}), i.e.
c_{aa} = M_{aa}, c_{ab} = √2·M_{ab} (a<b). This is the manuscript's `assemble_row`
convention, now stated as a definition rather than code.

(d) **Verification plan.** The dimension and orthonormality are PROVED analytically —
no sampling needed (Kit's rule). The code convention is CHECKED implicitly by the
`verify_independent.py` §5 cross-check: the assembled C′ matches the literal operator
entry-by-entry (max deviation 3.7e-13), which exercises every basis vector. No new
computation required. Status of M7′: **PROVED** (math) / **CHECKED** (code convention).

---

## M8′ — Casimir action (original M8 as encoded: INVALID, replaced)

(a) **Intent.** Implement the Casimir operator of the so(16) representation on
Sym²(128) — the central operator whose eigenspace decomposition is the manuscript's
headline claim (the 1 ⊕ 1820 ⊕ 6435 split). This is the heart of the computation:
everything downstream (M9–M12) depends on getting this operator right.

(b) **Diagnosis.** The encoded formula R(M) = Σ_a[A_a,[A_a,M]] is ρ(A)² for the
infinitesimal action ρ(A)M = [A,M] — i.e., the Casimir of the **conjugation** action
g·M = gMg⁻¹. That identification is valid only when the generators are real
antisymmetric (Aᵀ = −A), because only then does the congruence action's infinitesimal
form ρ_cong(A)M = AM + MAᵀ coincide with [A,M]. The actual generators are complex
anti-Hermitian with |A + Aᵀ| error 1.0 (**CHECKED**) — not real antisymmetric. Hence
the encoded R computed the Casimir of the wrong action in a basis where the
identification fails, producing the garbage spectrum [−128,−120,−96,−64,−60,−56,−48,
−28,0] with zero multiplicity at 48 and 64 (ledger §1). Two independent errors:
wrong action/basis (category error) and, as B-5 shows, an overall sign.

(c) **Corrected replacement (M8′).**
*Primary definition.* C′(M) = −Σ_a (A_a²M + 2A_aMA_aᵀ + M(A_aᵀ)²).
*Claim 1.* C′ is the Casimir operator of the congruence action g·M = gMgᵀ on
Sym²(128). **PROVED (independent)**: the infinitesimal action is ρ(A)M = AM + MAᵀ,
and ρ(A)²M = A(AM+MAᵀ) + (AM+MAᵀ)Aᵀ = A²M + 2AMAᵀ + M(Aᵀ)² by exact matrix algebra
(ledger B-4 addendum).
*Claim 2 (B-5 rehabilitation).* In the exhibited real basis (Frobenius–Schur +1;
real structure J with J²=+1, [J,A_a]=0; 120 generators real antisymmetric to
~1e-15), the manuscript's encoded formula satisfies R_manuscript(M) = −C′(M).
**CHECKED (numeric)**: worst relative ‖R + C′‖/‖C′‖ = 5.4e-16 over 6 trials
(`b5_reality_check.py`, CLOSED 2026-09-23). So the manuscript's formula is
rehabilitated **up to the overall sign**, in the real basis. In the manuscript's
(complex) basis it remains the wrong operator.
*Claim 3.* C′ is central: [C′, ρ(A)] = 0 for all generators A. **STANDARD** (Casimir
of a representation commutes with the representation) + **CHECKED** numeric:
max |[C′,ρ]| ≈ 2.8–2.9e-14 on random symmetric matrices (`diag_casimir.py` §3).

(d) **Verification plan.** Claim 1's derivation is PROVED by exact expansion — no
computation needed. Claim 3's centrality: STANDARD Lie theory; the numeric tripwire
([C′,ρ] < 1e-12 on random symmetric M) is already run. Claim 2 is re-runnable via
`b5_reality_check.py` (already CLOSED/CONFIRMED; rerun only if the construction
changes). Status of M8′: **PROVED** (Claim 1) / **CHECKED** (Claims 2, 3).

---

## M9′ — Casimir matrix build (original M9 as encoded: INVALID, replaced)

(a) **Intent.** Assemble the Casimir operator as an explicit 8256×8256 real symmetric
matrix in the M7′ basis, so it can be diagonalized. Pure infrastructure — but it is
where the first corrected run failed subtly, so the assembly rule needs stating exactly.

(b) **Diagnosis.** The original M9 assembled the WRONG operator's matrix (inheriting
M8's wrong formula). The first CORRECTED run then failed differently: it double-counted
diagonal (p=q) basis inputs, yielding spectrum {0:1, 48:1820, 64:6307, 128:128} —
**INVALID** (ledger §1). Root cause: for p=q the basis matrix is E_{pp} (single, not
doubled), so each of the S₂, S₂ᵀ, and cross terms must be applied once. The patched
rerun (p=q handled singly) gave the correct spectrum.

(c) **Corrected replacement (M9′).**
*Definition.* Matrix elements C_{mn} = Tr(E_m · C′(E_n)) (Frobenius inner product),
m,n over the 8256 M7′ basis elements. Computationally: precompute S₂ = Σ_a A_a² once
(O(n²)); the −2Σ_a A_a E_n A_aᵀ cross term via batched einsum; diagonal inputs E_{pp}
applied singly (**PROVED** correct by the basis definition — E_{pp} occurs once).
*Claim.* The assembled C is real symmetric (symmetry err 0.0, **CHECKED**),
max|imag| = 0.0 (**CHECKED**), and matches the literal operator: max over random
symmetric M of |C·row(M) − row(C′(M))| = 3.7e-13 (**CHECKED**, `verify_independent.py`
§5, fresh implementation + entry-by-entry cross-check).

(d) **Verification plan.** Already run (`verify_independent.py` §§4–5, exit 0).
Tripwires for any rerun: symmetry err < 1e-12; max|imag| < 1e-12;
literal-operator cross-check < 1e-8 on ≥4 random symmetric matrices. Status of M9′:
**CHECKED** (assembly) / **PROVED** (p=q single-count rule).

---

## M10′ — Eigenvalues and multiplicities (original M10 as encoded: INVALID, replaced)

(a) **Intent.** Diagonalize the Casimir matrix and confirm the manuscript's headline:
the spectrum is exactly {0:1, 48:1820, 64:6435} — i.e., Sym²(128) = 1 ⊕ 1820 ⊕ 6435
as so(16)-modules. The central numerical claim of the whole 12-module computation.

(b) **Diagnosis.** The original M10 diagonalized the wrong operator, reporting
[−128,−120,−96,−64,−60,−56,−48,−28,0] with zero multiplicity at positive 48 and 64 —
**INVALID** (ledger §1). (No independent basis/assembly subtlety beyond M8/M9's
failures; the negative spectrum is the fingerprint of the sign error compounded with
the wrong-action error.)

(c) **Corrected replacement (M10′).**
*Claim.* eigvalsh of the corrected symmetric C gives exactly three distinct
eigenvalues {0, 48, 64} with multiplicities (1, 1820, 6435).
*Status.* **PROVED (analytic)** — B-6, CLOSED 2026-09-24 (`PROOFS_Casimir.md`
K-1..K-9): Sym²(128) = ℂs ⊕ F ⊕ V(2ω₈) with dims 1+1820+6435 (K-4, K-6, K-7, K-8);
C acts as 0/48/64 via Harish-Chandra proportionality with κ=1 pinned on S₊
(−ΣM_AB² = 30I) and D₈ arithmetic ω₈→30, ω₄→48, 2ω₈→64 (K-9); Weyl dimensions
independently re-derived in exact rational arithmetic (`b6_weyl_check.py`, exit 0).
The numeric diagonalization is now **corroboration**, not establishment (Kit's rule:
no sampling after proof).
*Numeric tripwires* (for the corroborating run — `casimir2b.log`,
`verify_independent.py` §6, both CHECKED): exactly 3 distinct rounded eigenvalues;
mults (1, 1820, 6435); eig min ≥ −1e-9, max ≤ 64+1e-9; polynomial identity
C(C−48I)(C−64I) = 0 on all 8256 basis vectors (also verified in tables `C.npz`
build).

(d) **Verification plan.** Analytic proof exists and is CLOSED — no new proof needed.
Numeric corroboration already run twice independently. Do not re-sample for
establishment; re-run only the tripwires if the operator is ever rebuilt. Status of
M10′: **PROVED** (spectrum) / **CHECKED** (numeric corroboration).

---

## M11′ — Projectors and verification (original M11 as encoded: INVALID, replaced)

(a) **Intent.** Build the three Lagrange projectors onto the Casimir eigenspaces and
verify they are idempotent, pairwise orthogonal, and complete — certifying the
decomposition 8256 = 1 ⊕ 1820 ⊕ 6435 as an operator identity, not just an eigenvalue
count.

(b) **Diagnosis.** The original M11 applied Lagrange polynomials to the WRONG spectrum,
reporting invalid ranks 36722/−82471/54005 (including a negative rank — impossible for
a projector) and failed idempotence (breakage log B-2). The formulas were never the
problem; the spectrum they were fed was.

(c) **Corrected replacement (M11′).**
On the corrected C′ with spectrum {0, 48, 64}:
p₀(x) = (x−48)(x−64)/3072,   p₄₈(x) = x(64−x)/768,   p₆₄(x) = x(x−48)/1024.
*Claim.* P_i = p_i(C′) are idempotent, pairwise orthogonal, complete
(P₀+P₄₈+P₆₄ = I), with ranks (tr P_i) = (1, 1820, 6435).
*Status.* **CLOSED** (B-2, 2026-09-22), **CHECKED** numeric: matrix-free application
via the batched-BLAS C′ to 10 random symmetric 128×128 matrices (5 real, 5 complex;
`b2_projector_check.py`) — worst relative (Frobenius) residuals: idempotence 3.6e-16,
pairwise orthogonality 3.3e-16, completeness 2.2e-16, all at machine precision.
*Analytic note.* Given the B-6 spectrum, idempotence/orthogonality/completeness of the
Lagrange projectors follow **PROVED** by polynomial algebra on the spectrum
(p_i(λ_j) = δ_ij); the numeric check confirms the operator application, not the
algebra.

(d) **Verification plan.** Already CLOSED. Caution for reruns (recorded in the
breakage log): `b2_projector_check.py`'s own aggregate `ALL RESIDUALS` verdict printed
`False` because the check accidentally included the ‖M‖ scale row (129.0, not a
residual) — the per-test rows are the real evidence and all pass. Any rerun must
exclude non-residual rows from the aggregate verdict. Status of M11′: **CHECKED**
(B-2) / **PROVED** (polynomial algebra given B-6).

---

## M12′ — Clifford 4-form embedding (original M12 as encoded: REFUTED, replaced)

(a) **Intent.** Exhibit the 1820-dimensional Casimir eigenspace CONCRETELY as the span
of the 1820 Clifford 4-forms Γ_{ijkl} projected to the chiral spinor space S₊ — i.e.,
show that the "1820" of the four-form construction coincides with the "1820" of the
Casimir spectrum. The manuscript's most geometric claim: the abstract irrep V(ω₄)
realized as explicit matrices.

(b) **Diagnosis.** The original M12 projected the 4-forms (PΓ_{ijkl}P†), symmetrized,
and tested membership in the 48-eigenspace of the WRONG Casimir — failed
(`ImageInP1820=false`, `max_sampleVerify=21.0`). Worse: on the CORRECTED operator the
claim itself is FALSE. B-1 CLOSED (2026-09-22) with a CHECKED trichotomy over the
1820 naive projected+symmetrized forms: **896 collapse to zero, 140 nonzero lie in the
48-eigenspace, 784 lie ENTIRELY in the 64-eigenspace, 0 mixed** (residuals exactly 0
vs exactly 16√128 ≈ 181.019; top-5 worst spot-checked: C′v = 64v to machine precision,
`b1_spotcheck.py`). The nonzero forms span only 924 dims. So the manuscript's image
claim is REFUTED on the corrected operator — not merely unproven, false.
*Root cause.* The naive symmetrization (M+Mᵀ)/2 is not so(16)-equivariant: transpose
does not commute with the complex representation (B-1 tripwire max|pr−prᵀ| = 2.0 over
the projected forms), so the projected forms need not — and do not — respect the
Casimir decomposition. [M12a per-quad classification: PENDING — fills in below.]

(c) **Corrected replacement (M12′) — THE B-MAPPED FOUR-FORM THEOREM.**
*Definitions.* Let B₊ be the invariant symmetric bilinear form on S₊ (exists by B-5,
Frobenius–Schur +1; R3b verifies: B₊ preserves S₊, B₊ symmetric involution, all to
fp 0.0). For each 4-combination I=(i,j,k,l) let G_I = Γ_{ijkl}|_{S₊} and define the
B-mapped form Φ_I = sym(B₊G_I) = (B₊G_I + (B₊G_I)ᵀ)/2, expressed in Sym²(128)
orthonormal coords.
*Claim (M12′).* All 1820 Φ_I lie in the 48-eigenspace of C′, and they span it
(rank 1820 = tr P₁₈₂₀).
*Status.* **PROVED (analytic)** — completed proof below; the R3b/M12b numerics are
now corroboration. Numeric record: `R3b_fourform_membership.py` (2026-09-19, EXIT:0,
384.8s): 0 vanishing forms; worst ‖Cv−48v‖/‖v‖ = 6.3e-15; worst ‖P₁₈₂₀v−v‖/‖v‖ = 0.0
(at %.3e print precision); rank 1820. Decisive structural contrast with the naive map:
max_I |B₊G_I − (B₊G_I)ᵀ| = 0.0 — the B-mapped forms are EXACTLY symmetric (now PROVED
by K-5(a)), zero symmetrization loss (vs tripwire 2.0 for the naive map). Re-verified
independently this rebuild — see M12b results below.
*Analytic proof* (**PROVED** 2026-09-25 — the computation already existed as
`PROOFS_Casimir.md` K-5/K-6, proved 2026-09-19 and verified line-by-line in the B-6
run (K-5(c) 2-fold cancellation and the K-6 intertwiner hand-checked); this run
reconciled it with the skeleton and closed the one gap, the ρ-twist). K-5(a):
(B₊G_I)ᵀ = B₊G_I exactly, so sym is a no-op (explains R3b's measured 0.0);
K-5(b): B₊G_I ≠ 0; K-5(c): [M_AB, γ_I] ∈ span{γ_J^{(4)}} with the 2-fold terms
cancelling — the infinitesimal Clifford equivariance; K-5(d): F := span{B₊G_I}
is a nonzero ρ-submodule of Sym²(S₊). K-6: Φ: Λ⁴(16) → F, e_I ↦ B₊G_I, is
(ρ∘φ)-equivariant for the automorphism φ = Ad_D, D = diag(σ) ∈ SO(16) (K-3);
Φ ≠ 0 and Λ⁴(16) ≅ V(ω₄) irreducible (ST) give ker Φ = 0 by Schur, dim F = 1820,
(F, ρ∘φ) ≅ V(ω₄). *Twist lemma* (this run, PROVED): {φ(M_AB)} is orthonormal for
the trace form (Ad preserves trace; K-9 normalization tr = −32δ), so the Casimir
element Σφ(M_AB)² = ΣM_AB² by basis-independence; hence −Σ(ρ∘φ)(M_AB)² = C′ as
operators, and C′|_F = 48·I_F (K-9 eigenvalue on V(ω₄)). Thus F ⊆ 48-eigenspace
of C′, and dim F = 1820 = tr P₁₈₂₀ forces F = the 48-eigenspace exactly. Every
Φ_I = sym(B₊G_I) = B₊G_I lies in F; the 1820 B-mapped four-forms lie in and span
the 48-eigenspace. Scope: CP with the same ST components as B-6.
*Also recorded (B-1, CHECKED):* the TRUE trichotomy for the naive map — 896 zero +
140 pure-48 + 784 pure-64, 0 mixed — replacing the manuscript's false image claim.

(d) **Verification plan.**
- R3b already ran (NC, EXIT:0, log `R3b_run.log`) — cite; outputs archived in
  `~/workspace/tables/` (`fourform_Bmapped.npy`, TABLES.md).
- Independent re-verification (this rebuild, M12b): reload `fourform_Bmapped.npy` +
  `C.npz` + `P1820.npz` from tables and recompute the three tripwires independently —
  done, PASS (see below).
- Naive-map classification (this rebuild, M12a): per-quad class (proj-zero / sym-zero
  / pure-48 / pure-64 / mixed) and slot-type correlation, with tripwires — done
  (see below).
- Analytic: Φ-equivariance computation — DONE (PROVED 2026-09-25; see (c)).

### M12a results (naive-map per-quad classification)
**Computed 2026-09-24** (`/tmp/m12a_fast.py`, exit 0, 282.7s), using the B-1
checkpoints (`b1_module12_forms.npy`, `b1_module12_resid_max.npy`) plus a fresh
streaming rebuild of pr = PΓ_{ijkl}P† per quad for the zero-split. **CHECKED**:

Class counts over the 1820 quads: **pure-64: 784, sym-zero: 896, pure-48: 140**,
mixed: 0 — exact ledger match (896/140/784).

Slot-type × class (slot-type = tensor-slot occupancy of the quad):
- (1,1,1,1), n=1120: pure-48: 140, sym-zero: 560, pure-64: 420
- (2,1,1), n=672: sym-zero: 336, pure-64: 336
- (2,2), n=28: pure-64: 28

Per-slot-set uniformity (finer run, exit 0, 277.9s) — **the rule is exact, not
statistical**: every one of the 70 four-slot sets contains exactly
{pure-48: 2, pure-64: 6, sym-zero: 8}; every one of the 168 (2,1,1) slot-sets
exactly {pure-64: 2, sym-zero: 2}; all 28 (2,2) quads pure-64.

Mechanism of the 896 "collapses" — **none** are projection-zero (pr itself never
vanishes; proj-zero count = 0). All 896 are **exactly antisymmetric**:
‖sym(pr)‖/‖pr‖ = 0.0 and ‖asym(pr)‖/‖pr‖ = 1.0 for every one of them. The
manuscript's transpose-symmetrization step annihilates them algebraically; it is
not that Γ_{ijkl} misses S₊, but that its S₊-projection is anti-symmetric under
transpose and hence invisible to (M+Mᵀ)/2.

Tripwires: max resid among pure-48 = 0.0; max |resid/max|v| − 16| among pure-64 =
0.0 (the 16√128·‖v‖_max fingerprint, exact); mixed count = 0. So "exactly which
4-forms land in the 48- vs 64-eigenspace" is answered: the 140 pure-48 naive forms
are precisely 2 per four-distinct-slot set; the 784 pure-64 are 6 per such set, 2
per (2,1,1) set, all of (2,2). The finer question — which 2 of the 16
index-choices per slot-set are the pure-48 ones — is answered by the choice-word
rule (finest run, exit 0, 173.2s). For type (1,1,1,1), encode each quad by its word
(0 = odd index/s1-type, 1 = even index/s2-type, in slot order). The class depends
**only on the word**, uniformly across all 70 slot-sets (each word attains its
class in all 70):
- **pure-48**: `0000` and `1111` — all four indices the same parity (all odd or
  all even). These are the only naive forms that survive into the 48-eigenspace.
- **sym-zero**: all 8 odd-parity words (0001, 0010, 0100, 0111, 1000, 1011, 1101,
  1110) — exactly antisymmetric, killed by symmetrization.
- **pure-64**: all 6 even-parity mixed words (0011, 0101, 0110, 1001, 1010, 1100).
In particular the 140 pure-48 naive forms are precisely the 2·70 = 140 quads with
four distinct tensor slots and uniform index parity. **CHECKED** (computed, not
guessed; tripwires all pass).
For slot-type (2,1,1) the rule is likewise word-uniform (exit 0, 109.3s): with the
pair slot fixed and the two single slots encoded as a word, `00` and `11`
(uniform parity) are sym-zero in all 168 slot-sets, `01` and `10` (mixed parity)
are pure-64 in all 168 slot-sets. Slot-type (2,2): all 28 pure-64. The full
1820-form classification is therefore an exact, slot-set-independent function of
(slot-type, parity word) — no mixed forms, no exceptions.

### M12b results (B-mapped re-verification)
**PASS** — independently re-verified 2026-09-24 (`/tmp/m12_bmapped_verify.py`, exit 0,
129.5s), loading `fourform_Bmapped.npy` + `C.npz` + `P1820.npz` fresh from
`~/workspace/tables/`:
- vanishing forms: 0 / 1820
- tripwire worst ‖Cv − 48v‖/‖v‖ = 0.0 (below %.1e print precision; R3b measured 6.3e-15)
- tripwire worst ‖P₁₈₂₀v − v‖/‖v‖ = 0.0
- tripwire rank of the 1820 vectors = 1820 (== tr P₁₈₂₀ = 1820.0)
- sanity: C Hermitian err 0.0
The R3b claim is confirmed by an independent reload-and-recompute: the 1820 B-mapped
four-forms lie in and span the Casimir 48-eigenspace. **CHECKED (numeric)**,
two independent runs in agreement.

---

## Ranking by confidence

1. **M8′ (Casimir action)** — Claim 1 PROVED by exact algebra; Claims 2–3 CHECKED.
   The single most load-bearing replacement, and the most certain.
2. **M10′ (spectrum)** — PROVED analytic (B-6). Nothing further needed.
3. **M11′ (projectors)** — B-2 CLOSED/CHECKED; polynomial algebra PROVED given B-6.
4. **M9′ (matrix build)** — assembly CHECKED (3.7e-13 cross-check); p=q rule PROVED.
5. **M7′ (basis)** — PROVED (combinatorics/orthonormality); code convention CHECKED.
6. **M12′ (B-mapped four-forms)** — PROVED analytic (K-5/K-6 + twist lemma,
   2026-09-25); R3b EXIT:0 and this rebuild's independent re-verification
   (rank exactly 1820, residuals ~1e-15, exact symmetry of the B-mapped forms)
   are corroboration.

## What the clean-slate rebuild could NOT recover

1. **The manuscript's reasoning for M12.** Wolfram.pdf is not on disk; the ledger +
   `run_modules.py` record only what the code did. Why the manuscript expected naive
   projection+symmetrization to land in the 48-eigenspace — and whether it intended
   something like the B-map all along — is unrecoverable from the record. We replaced
   the construction; we did not recover the reasoning. Stated plainly, not invented.
2. **M12′ analytic equivariance — RESOLVED 2026-09-25 (B-7).** The computation was
   already in `PROOFS_Casimir.md` K-5/K-6 (verified in the B-6 run); the twist lemma
   closed the remaining gap. M12′ membership + spanning PROVED analytic.
3. **M8's original sign/basis confusion, as the manuscript saw it.** We can diagnose
   the two independent errors (wrong action/basis + sign) from the B-4/B-5 record, but
   the manuscript's own derivation path is not in the record.
4. **Volume IV.** Parked per instructions; nothing from volume-iv* was used. Any
   downstream use of these replacements in the Volume IV audit will need its own
   scoping pass when Volume IV is unparked.
