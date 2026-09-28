Living document — update these diagrams when adding features.
# r-theory-rewrite — Architecture

Static documentation site repo for the R Theory rewrite series. Observed: README.md describes a book-by-book, intuition-first rewrite of the R Theory manuscript (Books 0–22 across Volumes 0–IV plus a Discrete Octant volume), published as static HTML pages with live Desmos graph embeds and PNG fallbacks, pre-computed math tables, numbered audit scripts, and Python build/injector tooling. No server, no CI, no package manager observed — the repo IS the site plus its audit tooling. Live site named in README: cosbykit-afk.github.io/r-theory-rewrite.

## 1. Context diagram (level 0)
```mermaid
flowchart
    E1["Kit researcher"]
    E2["Reader"]
    E3["Lampy forum"]
    E4["Desmos"]
    E5["Drive control docs"]
    E6["R Theory mirror repo"]
    SYS(["R Theory rewrite site"])
    E1 -->|"audit scripts and pages"| SYS
    E5 -->|"ledger state"| E1
    SYS -->|"published pages"| E2
    E2 -->|"comment posts"| E3
    E4 -->|"live graph embeds"| E2
    SYS -->|"synced research pages"| E6
```

## 2. Level-1 data flow diagram
```mermaid
flowchart
    E1["Kit researcher"]
    E2["Reader"]
    E3["Lampy forum"]
    E4["Desmos"]
    E5["Drive control docs"]
    E6["R Theory mirror repo"]
    P1("1.0 Audit math claims")
    P2("2.0 Generate figure fallbacks")
    P3("3.0 Build site pages")
    P4("4.0 Verify embeds and anchors")
    P5("5.0 Sync mirror pages")
    P6("6.0 Police scan polish")
    P7("7.0 Build PDF snapshots")
    D1[("D1 Book pages HTML")]
    D2[("D2 Audit ledgers")]
    D3[("D3 Figure PNGs")]
    D4[("D4 Precomputed tables")]
    D5[("D5 Scanner state")]
    D6[("D6 PDF snapshots")]
    E5 -->|"read only ledger state"| P1
    E1 -->|"audit scripts"| P1
    P1 -->|"scope labels"| D2
    P1 -->|"verified expressions"| P2
    P2 -->|"fallback PNGs"| D3
    D2 -->|"claim text"| P3
    D3 -->|"figure files"| P3
    D4 -->|"table values"| P3
    E1 -->|"injector scripts"| P3
    P3 -->|"built HTML"| D1
    D1 -->|"pages"| P4
    E4 -->|"live embeds"| P4
    P4 -->|"fixed pages"| D1
    D1 -->|"research pages"| P5
    P5 -->|"synced copies"| E6
    D1 -->|"book pages"| P6
    P6 -->|"polish fixes"| D1
    P6 -->|"pointer and log"| D5
    D1 -->|"volume pages"| P7
    P7 -->|"merged PDFs"| D6
    D1 -->|"served site"| E2
    E2 -->|"comment API calls"| E3
```

Process grounding: 1.0 = validation/bookN/verify_bookN.py, audit_N.py, LEDGER_*.md; 2.0 = make_graphs.py, gen_figs.py, gen_figures.py; 3.0 = inject_sitenav.py, inject_footer.py, inject_comments.py, inject_handoff.py, build_series_index.py, build_series_toc.py; 4.0 = test_embeds.py, verify_anchors.py; 6.0 = scanner/README.md police scanner plus pointer.json; 7.0 = pdf/build.py. 5.0 sync to R-Theory is INFERRED — the R-Theory repo description says it is synced from here but no sync script was observed in this repo's tree.

## 3. Entity–relationship diagram

No runtime data model observed — this is a static site repo. The ERD below models the document structure actually seen in the files.

```mermaid
erDiagram
    BOOK {
        string dirname PK
        string volume
        string title
    }
    SECTION {
        string anchor_id PK
        string heading
    }
    FIGURE {
        string embed_id PK
        string latex
        string fallback_png
        string caption
    }
    CLAIM {
        string claim_id PK
        string scope
        string wording
    }
    TABLE {
        string name PK
        string csv_path
    }
    LEDGER_ENTRY {
        string ledger_id PK
        string file_path
    }
    BOOK ||--o{ SECTION : contains
    SECTION ||--o{ FIGURE : shows
    SECTION ||--o{ CLAIM : states
    BOOK ||--o{ TABLE : cites
    LEDGER_ENTRY }o--|| CLAIM : grounds
```

Claim scope values observed in validation/README.md: CP, SC, NC, AX, MA, IC, ST, IN. Figure triplet (Desmos latex, fallback PNG, caption) observed in validation README embed-consistency tests. Comments are forum-backed via the injected block and live in the external Lampy forum, not in this repo.

## Grounding notes
- OBSERVED: README.md full text decoded from the API — series structure, live site URL, Desmos dependency, tables, validation, guide, manuscript snapshots, public domain license.
- OBSERVED: recursive tree listing of 366 paths — book0 through book22 directories, contents, index, tables, research, appendix, validation, scanner, pdf, vol4-audit, guide, e8, manuscript, title, vol0, vol4, sitemap.xml.
- OBSERVED: WORKFLOW.md — Drive-based control framework, read-only manuscript, scope labels, compute stack (NumPy, SymPy, Wolfram Engine, exact integer arithmetic).
- OBSERVED: validation/README.md — per-book audit scripts, what each verifies, assertion counts, honest error bounds.
- OBSERVED: docstrings of build_series_index.py, build_series_toc.py, inject_comments.py, inject_sitenav.py, verify_anchors.py, scanner/README.md, pdf/build.py.
- OBSERVED: no .github/workflows and no CNAME in the tree.
- INFERRED: the exact mechanism that syncs tables/research/appendix into the R-Theory mirror repo (no sync script seen in this tree; the mirror's repo description asserts it is synced from here).
- INFERRED: how the site is deployed to the live GitHub Pages URL named in the README (GitHub Pages itself was not observed, only the URL in the README text).
