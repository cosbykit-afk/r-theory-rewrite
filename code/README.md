# code/ — the R Theory codebase, as published

The programs behind the results on this site, published so every claim that
rests on computation can be re-run from source. See
[Appendix Q](../appendix-q/) for the catalog: what each program does, what it
established, and how to reproduce the key checks.

## Layout

- `proving-ground/` — the Casimir / proving-ground computations (NumPy
  re-implementations and independent checks of the 12-module manuscript
  computation), exactly as run:
  - `run_modules.py` — faithful NumPy port of the 12 Wolfram modules
    (the original as-encoded computation, including its breakages)
  - `test_casimir2.py` — the corrected Casimir operator C′ test
  - `verify_independent.py` — from-definitions rebuild: Clifford relations
    on all 120 generators, so(16) commutation on all 7,140 pairs, full
    8,256-dim spectrum {0:1, 48:1820, 64:6435}
  - `diag_casimir.py` — diagnostics for the Casimir anomaly
  - `b1_cprime_worker.py`, `b1_module12_image_check.py`, `b1_spotcheck.py`
    — the B-1 module-12 image check on the corrected operator
  - `b2_projector_check.py` — B-2 Lagrange projector identities on C′
  - `b5_reality_check.py` — B-5: is the 128 half-spin representation real?
  - `b6_weyl_check.py` — B-6 support: exact rational-arithmetic check of
    the D8 Weyl dimensions and Casimir eigenvalues
  - `modules7_12_replacements.md` — replacement modules 7–12 notes
- `database/` — the R Theory database tooling:
  - `schema.sql` — the database contract
  - `rtheory.py` — CLI (init, import-status-registry, set-status,
    add-prose, link-prose, export-feeds, render-ledger)

## Already in this repo (not duplicated here)

- `validation/book*/` — per-book assertion scripts (`verify_bookN.py`,
  `make_graphs.py`, `test_embeds.py`)
- `*.py` at the repo root — site builders (`inject_sitenav.py`,
  `sync_status.py`, `build_series_toc.py`, `build_series_index.py`,
  `inject_comments.py`, `inject_footer.py`, `inject_handoff.py`,
  `verify_anchors.py`)

## Not published here

Raw data products (`.npy`/`.npz` arrays, run logs, pre-computed table
binaries) and machine-specific material (Wolfram Engine licensing,
Toetop-only deployment pieces) are not in this directory. The scripts are
the reproducible record; the data they consume or produce is described in
Appendix Q with its provenance.
