# Book23 feasibility investigation + "full derivations" appendix assessment

Investigated 2026-09-28 (Mon, ~15:35–15:50 PT) at Kit's request via the main agent.
Investigation only: no book23 created, no repo files modified, nothing pushed.

## Scope discipline

Only results with status PROVED or CHECKED count as book material.
ASSERTED / INCOMPLETE / OPEN items may appear only in an explicitly open
appendix or final chapter, never as chapters. Nothing below is rounded up.

## What book22 covered (content freeze: 2026-09-19)

book20–book22 (each `index.html` only) were created 2026-09-19; book22 is
"Canonical Spin–Geometry and the Primitive Symplectic Atlas — Volume 0".
Everything below is NEW since that freeze. (Book17–19 cleanup cycles and the
Book-3 second independent pass also closed 2026-09-19; counted as covered.)

## 1. New proved/checked results since book22

### A. The R3b theorem, analytic (B-6 + B-7) — PROVED, 2026-09-23/24/25
- **B-6 (2026-09-23/24):** the corrected Casimir spectrum promoted from
  CHECKED to **PROVED** analytic. `PROOFS_Casimir.md` K-1..K-9 hand-checked:
  D₈ arithmetic (ω₈→30, ω₄→48, 2ω₈→64), trace normalization
  tr(M_AB M_CD) = −32δ, κ=1 pinning, K-5(c) 2-fold cancellation, K-6
  intertwiner; Weyl dims 128/1820/6435 re-derived in exact rational
  arithmetic (`b6_weyl_check.py`, exit 0). Spectrum {0:1, 48:1820, 64:6435}
  is a theorem; numerics are now corroboration.
- **B-7 (2026-09-25):** M12′ analytic equivariance **PROVED** — twist
  lemma (Casimir basis-independence ⇒ −Σ(ρ∘φ)² = C′): all 1820 B-mapped
  four-forms lie in and span the 48-eigenspace exactly.
  Full proof artifacts: `~/workspace/icloud_pyto/rebuilt/PROOFS_Casimir.md`
  (6.8 KB), `PROOF_INDEX.md`, `~/workspace/wolfram/b6_weyl_check.py`,
  `~/workspace/wolfram/modules7_12_replacements.md` §M12′ (23 KB).

### B. Modules 7–12 clean-slate rebuild — PROVED/CHECKED, 2026-09-25
- M7′ Sym²(128) orthonormal basis (PROVED/CHECKED); M8′ corrected
  congruence-action Casimir C′ (PROVED); M9′ matrix assembly
  (PROVED rule / CHECKED implementation, 3.7e-13); M10′ analytic spectrum
  (PROVED); M11′ Lagrange projectors (PROVED algebra / CHECKED
  implementation); M12′ B-mapped embedding CHECKED twice independently
  (rank 1820, residuals ~1e-15, zero vanishing forms).
- **REFUTED:** the naive Module-12 image claim — 896 symmetrization-zero /
  140 pure-48 / 784 pure-64 / 0 mixed, exact per-quad classification
  (`m12a_classify.json`).
- The manuscript's original Modules 7–12 as encoded did NOT establish
  their claims; these are the replacements. Artifact:
  `~/workspace/wolfram/modules7_12_replacements.md`.

### C. The 1820 bilinear-odd campaign — 10 PROVED conditional theorems, 2026-09-26/27
All conditional throughout on the adopted g block form, the u-basis phase
convention, Π₀=P₂+P₆/Π₂=P₄+P₀, and MA1+MA2 (manuscript-literal v1:1730/1738).
1. **Conditional collapse (runs 12–15), PROVED:** Oprop ∈ 𝔟 := span{X̃_ab},
   dim_ℝ 𝔟 = 12, orthogonal basis {d_pq, o_pq} (norm² 188, Gram 188·I₁₂);
   f₀₂ = 47/182 exactly.
2. **Reality theorem (run 21), PROVED:** w₂ = w₆ for every real X ∈ 𝔟; no
   nonzero real mode-pure element; 6+6 lives only in 𝔟_ℂ.
3. **Cross-phase (run 24), PROVED:** o_{pq}⁽²⁾ = i·d_{pq}⁽²⁾; Q₂+Q₆ =
   188·I₁₂; per-pair block [[94,+94i],[−94i,94]].
4. **752 identity (omnibus Q1), PROVED:** ‖[X̃,M_ε]‖_F = 2‖X̃‖_F for every
   pure Π₀↔Π₂ flip; commutator Gram 752·I₁₂.
5. **M_ε commutant (run 22 + omnibus Q2), PROVED:** ker([·,M_ε]) = {0} on
   the pure Π₀↔Π₂ slot; full commutant M₈₁₆(ℂ)⊕M₁₀₀₄(ℂ); all four real
   transfer slots {0}. (Run 21's 6-dim kernel was a basis-mismatch bug,
   diagnosed and withdrawn.)
6. **m₀/m₂ decoupling (omnibus Q4), PROVED:** [M_e,M_ε] = i·[M_rest,K] for
   ALL real m₀,m₂ — masses absent from the commutator.
7. **Saw firewall FW-T12 (run 16), PROVED:** no real scalar g on an open
   quadrant satisfies S′ = g·X(S); saw complementation is algebraic and
   generates no transfer.
8. **W4 (C2a) discharged (run 19), PROVED:** deferred W4 skeleton
   substitution evaluates to exactly 0 on established witnesses.
9. **ε-survivor o-spectral-invisibility (run 17, corrected scope),
   PROVED:** the two DA-survivor positive-ε projectors are isospectral
   for real symmetric/Hermitian observables (earlier "every real
   operator" statement withdrawn — complex-Hermitian probes distinguish).
10. **Selection census (omnibus Q3), CHECKED (complete negative):** every
    established operator tabulated against 𝔟; none selects a vector or
    proper subspace of the real 12-dim space.
Full proof docs: `~/workspace/goals/r-theory-volume-i-audit/hidden_files/io_word_sweep/`
(~50 docs incl. `Q1_752_PROOF.md`, `CROSS_PHASE_PROOF.md`,
`F02_EXACT_PROOF.md`, `PAIRING_PROOF.md`, `B_REALITY_AND_COMMUTANT.md`,
`Q2_COMMUTANT_SLOTS.md`, `Q4_M0M2_IOWORDS.md`).

### D. Falsifications — 4 REFUTED, 2026-09-26/27
- **Run 25:** manuscript §19.4's N_1820 8-cycle (EBEOEBEO = 0 exactly,
  ‖·‖_F = 1.99e-61, 24/24 checks, robust under any letter↔projector
  bijection). Full 87,380-word cyclic classification: 85,866 exactly zero,
  32 nonzero classes, only sector-dimension/rest-spectrum content.
  N_1820 itself stays OPEN.
- **M_ε-commutant selection inside 𝔟** (the 12→6 reduction): REFUTED
  (run-21 basis bug withdrawn; kernel is {0}).
- **Mode-pure real Oprop construction:** REFUTED by the reality theorem.
- **W4 (C4)/Schur route to m₂⁻⁴:** REFUTED — full SO(16)-equivariance
  would force scalar M_e, contradicting m₀≠m₂; m₂⁻⁴ stays a manuscript
  convention.

### E. The 8-cycle dial theorems — PROVED, 2026-09-28
Exact block algebra (runs 30–31), conditional on established
witnesses/flip theorem/𝔟 content:
- **T1:** D₈ = ‖ZᵀZ‖²_F — blind to γ.
- **T3:** D_W = 2m₀m₂·C + m₀²·D₈ — sees γ (C := Tr(ZZᵀγZᵀZγᵀ) ≥ 0).
- **T4:** D_B = 2(m₀m₂)⁻¹·C + m₀⁻²·D₈ — sees γ.
- Cross-ratio exact identity: (D_W − m₀²D₈)/(D_B − m₀⁻²D₈) = (m₀m₂)²;
  bare (R=0): D_W·D_B = D₈² exactly; dressed: D_W·D_B ≥ D₈².
  Published as summaries in `research/calibration.html`; derivation notes
  in `io_word_sweep/EPSODD_8CYCLE_DIAL.md`, `DIAL_*.md`.

### F. The calibration program — PROVED inputs, OPEN predictions, 2026-09-28
- **CAL-P6, CONFIRMED by proof:** manuscript word
  Tr[E M_e E Oprop E M_e E Oprop] = 0 identically for every Oprop ∈ 𝔟
  (bare E), any M_e — exact support algebra. **PROVED.**
- CAL-P1..P5: **OPEN** predictions (dial consistency inequality,
  commutator-norm 752, mode-block 188, sector-dimension lock 368/556/896,
  ε-odd dial nonvanishing) — exact consequences of PROVED theorems,
  conditional on physical E_k/Oprop witnesses. Honest: not confirmed.
- Dimensionless inventory: 11 exact pure numbers (368/556/896, 816/1004,
  12, 188, 752, 2, 94, 47/182, 24/64/120) — PROVED/CHECKED.
- Anchors: SI-DIMLESS-01; CHIRAL-ANCHOR-01 (21 cm H I line, Kit: the SOLE
  numerical root); CHIRAL-ANCHOR-02 (sector occupancy, ASSERTED);
  AXIOM-ONE (ASSERTED, Kit's unit declaration).
- Open slots (for the physicist, by the Anti-Fabrication Rule):
  dial↔observable identifications, physical witnesses, bare-vs-dressed,
  ρ_E, ρ_V. All OPEN — Kit's call.
- Page: `research/calibration.html` (commits b92ea14, 6a104ae, 9a0ff3d,
  56de939, f0eb5eb, 3dd55d4).

### G. Two standalone theorems — PROVED
- **Book 2 L9 nonconstancy (2026-09-27), PROVED:** closed form
  urx²−uxp² = 4(s₁cos x − s₂sin x)/(sin²x cos²x) — no lambda; synced into
  book2. **PROVED.**
- **Kit's secant–cosecant identity (2026-09-21), PROVED:**
  4/sin(2x) = (A−1/B)+(B−1/A), A=tan x+|sec x|, B=cot x+|csc x|; no quadrant
  case split needed. Full proof + 500k-sample check (7.8e-07 worst).
  Artifact: `~/workspace/kit_theorems/secant-cosecant-identity/PROOF.md`.

### Front status checks
- **R Theory side chat (8bdadabe…):** quiet — newest message
  2026-09-25T06:56 PT; nothing new to harvest there. Recent results
  arrived via worker reports (breakage-follow-up log) and direct commits.
- **Breakage follow-up log:** B-1..B-7 all CLOSED; queue checks every ~6 h
  since 2026-09-24 report "no OPEN or IN PROGRESS items" — no new results
  there, consistent with the burst ending ~09-27/28.
- **status_registry.json:** 86 claims, Books 2–6 only; PROVED 49 /
  CHECKED 33 / STANDARD 2 / MANUSCRIPT 1 / INVALID 1. These are the
  Book-2/3/4/5/6 audit ledgers (created 2026-09-28 sync run) — no new
  claims added since; the *new* results above live in the research pages
  and workspace docs, not the registry.

## 2. Candidate book23 chapter outline

Working title (placeholder): **Book 23 — The 1820 Theorem and the
Calibration Program** (Volume IV / research front).

1. **The spectrum becomes a theorem** — B-6 analytic proof K-1..K-9;
   {0:1, 48:1820, 64:6435} as PROVED; Weyl dims re-derived in exact
   arithmetic. (Maps to §1A.)
2. **The 48-eigenspace is the four-form space** — M12′ twist lemma, B-7;
   Φ: Λ⁴(16) → F; the naive-map trichotomy refutation. (Maps to §1A, §1B.)
3. **Rebuilding the broken modules** — M7′–M11′ corrected replacements;
   the corrected Casimir C′; Lagrange projectors; why the original
   encodings failed. (Maps to §1B.)
4. **The twelve-dimensional candidate space** — conditional collapse,
   188-Gram, f₀₂=47/182; reality theorem; cross-phase 94/94. (Maps to
   §1C 1–3.)
5. **What the 1820 refuses** — the four falsifications: N_1820 8-cycle
   death (run 25), commutant-selection refuted, mode-pure Oprop refuted,
   the W4 (C4)→m₂⁻⁴ route refuted; W4 (C2a) skeleton = 0. (Maps to §1D,
   §1C 8.)
6. **The isolated hard core** — 752 identity; M_ε commutant; m₀/m₂
   decoupling; saw firewall; the complete negative selection census —
   what cannot select Oprop, and the two OPEN gates (physical selection,
   m₀/m₂). (Maps to §1C 4–7, 9–10.)
7. **The dial theorems** — D₈/D_W/D_B closed forms; bare-vs-dressed;
   cross-ratio; the dial ratios as the selecting observables. (Maps to
   §1E.)
8. **The calibration program** — anchors, Axiom One, the dimensionless
   inventory, CAL-P6 confirmed, CAL-P1..P5 as OPEN falsifiable
   predictions with explicit needs (witnesses, identifications). Scoped
   as "loaded instrument, no target yet." (Maps to §1F.)
9. **Two clean theorems** — Book-2 L9 analytic nonconstancy; the
   secant–cosecant identity. (Maps to §1G.)

Nine chapters is at the top of the 5–9 range; chapters 8–9 could merge,
or the two small theorems could move to an appendix (see §4).

## 3. Honest gaps — what must stay out or stay labeled

- **Physical Oprop / E_k witnesses: OPEN.** Every prediction and every
  conditional theorem depends on them; the book must say so on every
  affected page (it already does in research/).
- **N_1820: OPEN.** Its 8-cycle is dead, but N_1820 itself is unresolved.
- **m₀/m₂ selection: OPEN** (decoupling theorem proves commutators can't
  select them; dial identification is the path, unidentified).
- **S_F gate (C1): INCOMPLETE** (E_k, Oprop matrix, 128-dim gammas, C^t_2222
  / F_C8 absent).
- **The 29 GATEs (GATE-8..GATE-36)** and proving-ground gates (Λ²(16)↪1820
  branching, S_F) stay in research/, not in the book except as an
  explicitly open final appendix.
- **Axiom One / sector occupancy / m₀=2,m₂=5:** ASSERTED or reference —
  labeled, never chapters.
- CAL-P1..P5 are OPEN predictions: chapter 8 is a *prediction* chapter,
  not a result chapter. That is fine and honest as long as the boundary
  is drawn the way calibration.html already draws it.

## 4. The "full derivations" appendix (scope addition)

Kit's read of his word "decorations": a published appendix of complete
proofs/derivations behind the series' established results.

### (a) Which proved/checked results currently lack their full derivation
in the published books

Survey: the books publish verdicts, audit tables, and validation scripts;
the *written-out proofs* live in workspace docs. The gaps:

1. **Casimir K-1..K-9 + B-7 twist lemma** — PROVED; full proof text exists
   (`icloud_pyto/rebuilt/PROOFS_Casimir.md` + `PROOF_INDEX.md`, 12.5 KB).
   NOT in any published book page (book6 has no K-1..K-9 text).
2. **The 10 bilinear-odd campaign theorems** — PROVED/CHECKED; full or
   near-full proof notes exist (`io_word_sweep/*.md`: `Q1_752_PROOF.md`
   159 lines, `CROSS_PHASE_PROOF.md` 118, `F02_EXACT_PROOF.md` 132,
   `PAIRING_PROOF.md` 86, plus `B_REALITY_AND_COMMUTANT.md`,
   `Q2_COMMUTANT_SLOTS.md`, `Q4_M0M2_IOWORDS.md`, `SAW_LFORM_DERIVATION.md`,
   `SF_W4_CONDITIONALS.md`). Research pages carry bullets only.
3. **The dial theorems T1/T3/T4** — PROVED; summaries on calibration.html;
   block-algebra write-up exists in lab-note form
   (`EPSODD_8CYCLE_DIAL.md`, `DIAL_*.md`) but was NOT found as a single
   polished proof — needs one careful write-up pass.
4. **Secant–cosecant identity** — PROVED; complete self-contained proof
   exists (`kit_theorems/secant-cosecant-identity/PROOF.md`). NOT published
   in any book.
5. **Modules 7′–12′ derivations** — PROVED/CHECKED; written
   (`modules7_12_replacements.md`, 23 KB). Exists only in workspace.
6. **Books 2–6 audit claims** — 49 PROVED + 33 CHECKED in
   status_registry.json / theorem_ledger.md. Verdicts are "PROVED (exact
   by inspection / exact algebra)" with scripts, not written derivations.
   Largest gap by count; much is one-line mathematics (each would render
   as a short proof paragraph), but it is real editorial work, and the
   **Book 1 + Volume II claims are not yet in the machine mirror at all**
   (per the sync notes: Books 2–6 structured verdicts only).
7. **The refutations** (run-25 N_1820, commutant bug, mode-pure, W4 (C4)) —
   run-25's write-up exists (`N1820_CYCLE_PROBE.md` + results JSON);
   the others are documented in research/ bullets and ledger notes.
   Worth including as "negative derivations."

What needs nothing new: the **validation scripts** (verify_book19.py,
verify_book2_open.py, verify_book3_cocycle.py, b6_weyl_check.py, etc.)
are complete executable derivations for the CHECKED claims — an appendix
section can be a pointer table to scripts + run logs rather than prose.

### (b) Feasibility from existing artifacts

**Feasible: YES, from existing artifacts, with two write-up passes.**
- Ready to transcribe: (a)(1) Casimir proofs, (a)(4) secant–cosecant,
  (a)(5) modules 7′–12′ — proof text already publication-shaped.
- Near-ready: (a)(2) campaign theorems — lab-proof docs need light
  editing into appendix form (conditions stated up front, one doc per
  theorem, consistent notation).
- One write-up pass needed: (a)(3) dial T1/T3/T4 block algebra — compose
  from `EPSODD_8CYCLE_DIAL.md` / `DIAL_*.md` lab notes; all premises are
  proved, so this is editorial, not mathematical, work.
- Larger editorial lift: (a)(6) Books 2–6 audit claims — 82 claims need
  proof paragraphs; the ledger + scripts provide the skeleton. Volume II
  and Book 1 claims are not yet in the registry at all, so either the
  appendix stays scoped to Books 2–6 + the new campaign, or the registry
  coverage is extended first.
- Note the existing `appendix/index.html` is a *different* thing (the
  computational audit trail for the Casimir modules). Kit's appendix is a
  new volume-level appendix; recommend naming it accordingly (e.g.
  `appendix-proofs/`).

### (c) Candidate appendix structure

- **Appendix P-1. The Casimir spectrum proofs** — K-1..K-9, Weyl dims,
  B-7 twist lemma; scripts/logs cited as corroboration.
- **Appendix P-2. The 1820 conditional theorems** — collapse, reality,
  cross-phase, 752, commutant, decoupling, saw firewall, W4 (C2a),
  ε-invisibility; each with premises (MA1+MA2, conventions) stated once.
- **Appendix P-3. The dial theorems** — T1/T3/T4 with full block algebra
  (to be composed); CAL-P6 support-algebra proof.
- **Appendix P-4. The clean-slate modules** — M7′–M12′ derivations;
  naive-Module-12 refutation classification.
- **Appendix P-5. The refutations** — run-25 N_1820, commutant bug,
  mode-pure, W4 (C4): full negative derivations.
- **Appendix P-6. Standalone theorems** — secant–cosecant identity;
  Book-2 L9 analytic nonconstancy.
- **Appendix P-7. Audit-claim derivations (Books 2–6)** — condensed
  proof paragraphs for the 82 registry claims (largest lift; may ship
  first as a stub with the ledger link, expanded per book).
- **Appendix P-8. Reproducibility index** — script↔claim pointer table
  (validation scripts, run logs, checksums) for every CHECKED claim.
  This is the "executable derivation" half — cheap to build, high value.

## 5. Bottom-line verdict

**Enough for a full book: YES — and some.** The post-freeze burst
(2026-09-21..28) delivered ~30 PROVED/CHECKED items plus 4 substantive
REFUTED items, with full proof artifacts for nearly all of them. The
nine-chapter outline in §2 maps every chapter to concrete,
scope-labeled results; the falsifications chapter gives the book genuine
intellectual weight (run-25's 87,380-word classification is a result in
its own right). Two caveats keep it honest: (i) chapter 8 is a
*prediction* chapter (OPEN, conditional on witnesses — labeled as such);
(ii) the book's final section must be an explicitly open appendix of
the gates/witnesses/identifications that remain, never presented as
closed. The one thing a reader might expect and won't find: any physical
identification — the whole book is "the instrument, calibrated, awaiting
a target," which is itself a defensible thesis and should be the book's
stated scope on page one.

**The appendix: feasible, don't build yet.** No tipping proofs are
needed; the gating work is editorial (dial-theorem write-up, campaign
proofs light edit, audit-claim paragraphs). The two recommended
follow-ups before any build: (1) Kit's call on the appendix name/scope
(P-1..P-8, or P-1..P-6 without the audit-claims lift), and (2) a ruling
on whether Book-1/Volume-II claims join the appendix later (registry
coverage extension). Both are Kit calls, so this report stops here per
instructions.

Report written to: [book23_feasibility.md](sandbox://workspace/r-theory-rewrite/research/book23_feasibility.md)
