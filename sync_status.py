#!/usr/bin/env python3
"""Sync the R Theory site's research status tags with the research status ledger.

The research status ledger is ~/workspace/wolfram/theorem_ledger.md (the
Volume I audit's status record: PROVED / CHECKED / STANDARD / MANUSCRIPT /
INVALID / INCOMPLETE per claim).

This script keeps three things consistent:

1. status_registry.json -- the machine-readable mirror of the ledger. Proof
   sessions update the LEDGER (prose, human record); `sync_status.py refresh`
   re-parses its structured parts (markdown tables + status bullets) into the
   registry. Hand-curated entries (source "manual") are preserved across
   refreshes.
2. ledger/index.html -- the public "ledger website": the canonical status-key
   mapping every tag code site-wide, plus per-claim status tables generated
   from the registry. Every status tag on the site links here for its meaning.
3. The tags themselves -- `<span class="tag XX">` pills across the site are
   wrapped in links to the ledger key (`link` step), and spans carrying
   `data-claim="<id>"` get their code/label set from the registry
   (`sync-claims` step), so a status change in the ledger propagates to the
   page automatically.

Usage:
    python3 sync_status.py all            # refresh + render + link + sync-claims + check
    python3 sync_status.py refresh        # re-parse ledger -> registry only
    python3 sync_status.py render         # regenerate ledger/index.html only
    python3 sync_status.py link           # wrap tag pills in ledger-key links
    python3 sync_status.py sync-claims     # set data-claim spans from registry
    python3 sync_status.py check          # consistency report (no writes)

Idempotent: re-running `all` with no ledger/registry/page changes is a no-op.
"""

import json
import os
import re
import sys
import unicodedata
from datetime import datetime, timezone
from html import escape as htesc

ROOT = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.expanduser("~/workspace/wolfram/theorem_ledger.md")
REGISTRY = os.path.join(ROOT, "status_registry.json")
DERIV_REGISTRY = os.path.join(ROOT, "derivations_registry.json")
LEDGER_PAGE = os.path.join(ROOT, "ledger", "index.html")

# ---------------------------------------------------------------- canonical key
# Every tag code used anywhere on the site, with its canonical meaning and the
# ledger status it corresponds to. Aliases are historic per-book shorthands;
# the ledger page documents them so old pages keep working.
KEY = {
    "CP": {"label": "checked proof",
           "meaning": "Proof read and following from stated antecedents.",
           "ledger": "PROVED", "aliases": ["P"]},
    "SC": {"label": "completed symbolic check",
           "meaning": "Verified by an exact symbolic or integer-exact computation.",
           "ledger": "PROVED", "aliases": ["CS"]},
    "NC": {"label": "completed numerical check",
           "meaning": "Verified numerically to a stated tolerance; not a symbolic proof.",
           "ledger": "CHECKED", "aliases": ["N", "CN"]},
    "ST": {"label": "standard imported theorem",
           "meaning": "Independently established standard mathematics; the manuscript re-derives it.",
           "ledger": "STANDARD", "aliases": ["S", "SI"]},
    "MA": {"label": "manuscript assertion",
           "meaning": "Claim or proof exists only inside the manuscript; not yet independently checked.",
           "ledger": "MANUSCRIPT", "aliases": ["M"]},
    "AX": {"label": "assumption or axiom",
           "meaning": "Granted starting point: axiom, definition, or constitutional rule. Not proved.",
           "ledger": None, "aliases": ["A", "AA", "D"]},
    "IN": {"label": "incomplete or failed computation",
           "meaning": "Computation timed out, failed, or is still running.",
           "ledger": "INCOMPLETE", "aliases": ["IF"]},
    "IC": {"label": "incorrect result",
           "meaning": "The claim as stated fails; the ledger records how.",
           "ledger": "INVALID", "aliases": ["IR", "ER"]},
}
ALIAS_TO_CANON = {a: c for c, d in KEY.items() for a in d["aliases"]}

LEDGER_TO_SITE = {"PROVED": "CP", "CHECKED": "NC", "STANDARD": "ST",
                  "MANUSCRIPT": "MA", "INVALID": "IC", "INCOMPLETE": "IN"}
SYMBOLIC_HINTS = ("sympy", "symbolic", "exact", "by inspection", "by-inspection",
                  "rational arithmetic", "residual 0")

# ---------------------------------------------------------------- ledger parsing

BOOK_RE = re.compile(r"[Bb]ook (\d+)")
STATUS_RE = re.compile(r"\*\*(PROVED|CHECKED|STANDARD|MANUSCRIPT|INVALID|INCOMPLETE)\b([^*]*)\*\*")
# Sections whose content is recap / meta rather than claim verdicts: skip.
SKIP_SECTIONS = ("open / incomplete", "what the math has proven")


def _book_from_heading(text):
    m = BOOK_RE.search(text)
    if m:
        return int(m.group(1))
    if "olfram" in text or "odule" in text or "asimir" in text:
        return 6
    return None


def _clean(text):
    text = re.sub(r"[*_`~]", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"^[-–—:;,. ]+", "", text).strip()
    return text


def _site_code(status, basis):
    code = LEDGER_TO_SITE[status]
    b = basis.lower()
    if status in ("PROVED", "CHECKED") and any(h in b for h in SYMBOLIC_HINTS):
        # exact/symbolic verification -> symbolic check, unless it's an
        # analytic proof (which stays a checked proof)
        if "analytic proof" in b or "proof" in b and "proof read" in b:
            return "CP"
        return "SC" if status == "PROVED" else code
    return code


def parse_ledger(path=LEDGER):
    """Parse the ledger's markdown tables and status bullets into claim dicts."""
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    claims = []
    section = ""
    subsection = ""
    book = None
    skip = False
    counters = {}

    def book_now():
        return _book_from_heading(subsection) or _book_from_heading(section) or book

    i = 0
    while i < len(lines):
        line = lines[i]
        h2 = re.match(r"##\s+(.*)", line)
        h3 = re.match(r"###\s+(.*)", line)
        if h2:
            section, subsection = h2.group(1).strip(), ""
            skip = any(s in section.lower() for s in SKIP_SECTIONS)
            b = _book_from_heading(section)
            if b is not None:
                book = b
            i += 1
            continue
        if h3:
            subsection = h3.group(1).strip()
            i += 1
            continue
        if skip or not line.strip():
            i += 1
            continue
        # markdown table block
        if line.lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"\s*\|[\s:\-|]+\|\s*$", lines[i + 1]):
            header = [c.strip().lower() for c in line.strip().strip("|").split("|")]
            i += 2
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                row = dict(zip(header, cells))
                claim_txt, status_txt, basis_txt = "", "", ""
                if "identity" in row:
                    claim_txt, status_txt = row["identity"], row.get("status", "")
                    basis_txt = "max error " + row.get("max error", "?")
                elif "claim" in row:
                    claim_txt = row["claim"]
                    res = row.get("result", "")
                    if "✓" in res or "exact" in res.lower():
                        status_txt, basis_txt = "PROVED", res
                    else:
                        status_txt, basis_txt = "CHECKED", res
                if claim_txt and status_txt:
                    claims.append(_mk(book_now(), section, subsection,
                                             claim_txt, status_txt, basis_txt, counters, i))
                i += 1
            continue
        # status bullet
        m = STATUS_RE.search(line)
        if m and line.lstrip().startswith("-"):
            status = m.group(1)
            before = _clean(line[:m.start()])
            after = _clean((m.group(2) + " " + line[m.end():]))
            # skip bullets that are pure status recaps without a claim
            if len(before) >= 8:
                claims.append(_mk(book_now(), section, subsection,
                                         before, status, after, counters, i))
        i += 1
    return claims


STOPLIST = {"checked", "proved", "numeric", "completed", "exit", "addendum", "via"}
ROMAN = {"i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi",
         "xii", "xiii", "xiv", "xv"}


def _slug(text):
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    tokens = re.findall(r"[a-z0-9]+", ascii_text.lower())
    tokens = [t for t in tokens if t not in STOPLIST]
    # drop a leading section-number run like 3, vi, 2, xi, l or a date;
    # the run must start with an all-digit token
    if tokens and tokens[0].isdigit():
        while tokens and (tokens[0].isdigit() or tokens[0] in ROMAN
                          or (len(tokens[0]) == 1 and tokens[0] in "ivxlcdm")):
            tokens.pop(0)
    return "-".join(tokens[:4]) or "sec"


def _mk(book, section, subsection, claim, status, basis, counters, lineno):
    slug = _slug(subsection or section)
    # the "Book 4/5 spot-checks" table mixes books: the Iota-complex-structure
    # row belongs to Book 5
    if book == 4 and "ι" in claim:
        book = 5
    key = (book if book is not None else "x", slug)
    counters[key] = counters.get(key, 0) + 1
    cid = f"b{book}-{slug}-{counters[key]:03d}" if book is not None else f"x-{slug}-{counters[key]:03d}"
    claim = _clean(claim)
    if len(claim) > 220:
        claim = claim[:217] + "..."
    return {
        "id": cid,
        "book": book,
        "section": _clean(subsection or section),
        "claim": claim,
        "ledger_status": status,
        "site_code": _site_code(status, basis),
        "basis": _clean(basis)[:300],
        "source": f"theorem_ledger.md",
    }


# ---------------------------------------------------------------- registry

def load_registry():
    if os.path.exists(REGISTRY):
        with open(REGISTRY, encoding="utf-8") as fh:
            return json.load(fh)
    return {"meta": {}, "key": KEY, "claims": []}


def load_derivations():
    """Claim id -> appendix anchor mapping for the full-derivations appendix."""
    if os.path.exists(DERIV_REGISTRY):
        with open(DERIV_REGISTRY, encoding="utf-8") as fh:
            return json.load(fh)
    return {"meta": {}, "claims": {}, "results": {}}


def _deriv_link(cid, derivs):
    anchor = derivs.get("claims", {}).get(cid)
    if not anchor:
        return "&mdash;"
    return (f'<a href="../appendix-proofs/#{htesc(anchor)}"'
            f' title="Full derivation in Appendix P">derivation</a>')


def cmd_refresh():
    claims = parse_ledger()
    reg = load_registry()
    old = {c["id"]: c for c in reg.get("claims", []) if c.get("source") != "manual"}
    new_ids = set()
    added, changed = 0, 0
    merged = []
    for c in claims:
        new_ids.add(c["id"])
        if c["id"] in old:
            o = old[c["id"]]
            if (o.get("ledger_status") != c["ledger_status"] or o.get("claim") != c["claim"]
                    or o.get("site_code") != c["site_code"]):
                changed += 1
            merged.append(c)
        else:
            added += 1
            merged.append(c)
    removed = [cid for cid in old if cid not in new_ids]
    manual = [c for c in reg.get("claims", []) if c.get("source") == "manual"]
    old_meta = reg.get("meta", {}) or {}
    sources = ["~/workspace/wolfram/theorem_ledger.md"]
    note = ("Machine mirror of the ledger's structured verdicts (tables + status "
            "bullets). The prose ledger is the human record; entries with "
            "source 'manual' are hand-curated and preserved across refreshes. "
            "Proof sessions: update the LEDGER, then run sync_status.py all.")
    unchanged = (added == 0 and changed == 0 and not removed
                 and reg.get("key") == KEY
                 and old_meta.get("sources") == sources
                 and old_meta.get("note") == note)
    reg["meta"] = {
        # strict idempotence: a no-change refresh keeps the old timestamp so
        # the registry file (and everything downstream) is byte-identical
        "generated": (old_meta.get("generated")
                      if unchanged
                      else datetime.now(timezone.utc).isoformat(timespec="seconds")),
        "sources": sources,
        "note": note,
    }
    reg["key"] = KEY
    reg["claims"] = merged + manual
    with open(REGISTRY, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(f"registry: {len(merged)} ledger claims ({added} added, {changed} changed, "
          f"{len(removed)} removed) + {len(manual)} manual")
    for cid in removed:
        print(f"  removed (no longer in ledger): {cid}")
    return reg


# ---------------------------------------------------------------- ledger page render

TAG_CSS = """
.tag{display:inline-block;font-size:.68rem;font-weight:700;letter-spacing:.04em;
 text-transform:uppercase;border-radius:4px;padding:1px 7px;margin:0 2px;vertical-align:baseline;
 border:1px solid transparent;white-space:nowrap}
.tag.CP,.tag.SC{background:#e7f4ec;border-color:#9cc8ab;color:#1d5c33}
.tag.NC{background:#e8f0fb;border-color:#9db8e0;color:#1f3f7a}
.tag.ST{background:#f0eefb;border-color:#b7aee6;color:#46357e}
.tag.MA{background:#faf3e3;border-color:#ddc48f;color:#7a5a17}
.tag.AX{background:#f3f3f3;border-color:#c2c2c2;color:#4d4d4d}
.tag.IN{background:#fdeeee;border-color:#e5a3a3;color:#8f2b2b}
.tag.IC{background:#fbe4e4;border-color:#d97f7f;color:#7c1f1f}
a.taglink{text-decoration:none}
a.taglink:hover .tag{filter:brightness(.94)}
a.taglink:focus-visible{outline:3px solid #0e7c86;outline-offset:2px;border-radius:4px}
table.ledger{border-collapse:collapse;width:100%;margin:1em 0;font-size:.92rem}
table.ledger th,table.ledger td{border:1px solid #d5dfe0;padding:6px 9px;text-align:left;vertical-align:top}
table.ledger th{background:#eef4f4}
table.key td:first-child{white-space:nowrap}
"""

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Research status ledger — R Theory</title>
<!-- SITENAV-START -->
<!-- SITENAV-END -->
<style>
body{{font-family:Georgia,'Times New Roman',serif;max-width:860px;margin:0 auto;
 padding:0 24px;color:#1c2b2e;line-height:1.6}}
{TAG_CSS}
h1,h2,h3{{font-family:'Source Sans 3',system-ui,sans-serif;color:#0b3f45}}
.lede{{color:#41565a}}
.updated{{font-size:.85rem;color:#6b7f83}}
</style>
</head>
<body>
<!-- SITENAV-NAV-START -->
<!-- SITENAV-NAV-END -->
<h1>Research status ledger</h1>
<p class="lede">The single record of what the R Theory audit has established, per claim.
Every status tag on this site links here for its meaning, and tags carrying a
claim reference update from this ledger automatically. The human record is the
prose audit ledger (<code>theorem_ledger.md</code>); the original R Theory
manuscript (a Google Doc) stays read-only and is never edited by this process.
The tables below are the ledger's machine mirror, regenerated by
<code>sync_status.py</code>.</p>
<p class="lede"><b>Coverage.</b> The tables currently mirror the ledger's
structured verdicts for Books 2–6 (86 claims). Book 1's line-by-line source
audit and the Volume II audit (Books 7–13, in progress) are not yet in the
machine mirror — their verdicts join these tables as their ledgers land.</p>
<p class="lede"><b>Derivations.</b> Claim rows carrying a <i>derivation</i> link
point at the full written-out proof in
<a href="../appendix-proofs/">Appendix P — Full Derivations</a>. Verdicts that
are too thin for a derivation paragraph land on an explicitly labeled pointer
instead — never on invented mathematics.</p>
<p class="updated">Last synced: {updated}. {n_claims} claims across {n_books} books.</p>

<h2 id="key">Status key</h2>
<p>Each claim carries exactly one status. Historic per-book shorthands
(aliases) keep their meaning; the canonical codes are below.</p>
<table class="ledger key">
<tr><th>Code</th><th>Label</th><th>Meaning</th><th>Ledger status</th><th>Aliases</th></tr>
{key_rows}
</table>

<h2 id="claims">Claims by book</h2>
{book_sections}

<hr>
<!-- STATUSREG-START -->
<p class="updated">Registry: <code>status_registry.json</code> in the site repo.
Proof workflow: update the audit ledger, run <code>python3 sync_status.py all</code>,
rebuild <code>site-dist</code>, deploy.</p>
<!-- STATUSREG-END -->
<!-- COMMENTS-START -->
<!-- COMMENTS-END -->
<!-- FOOTER-START -->
<!-- FOOTER-END -->
</body>
</html>
"""


def _tag(code):
    canon = ALIAS_TO_CANON.get(code, code)
    info = KEY.get(canon, {"label": code})
    return f'<span class="tag {canon}">{info["label"]}</span>'


AUDIT_START = "<!-- AUDITSTATUS-START -->"
AUDIT_END = "<!-- AUDITSTATUS-END -->"


def _audit_block(book, claims, derivs=None):
    derivs = derivs or {}
    rows = []
    for c in claims:
        code = ALIAS_TO_CANON.get(c["site_code"], c["site_code"])
        label = KEY[code]["label"]
        rows.append(
            f"<tr id=\"audit-{c['id']}\" data-claim=\"{c['id']}\">"
            f"<td>{htesc(c['claim'])}</td>"
            f"<td><a class=\"taglink\" href=\"../ledger/#claim-{c['id']}\""
            f" title=\"{htesc(label)} — ledger claim {c['id']}\">"
            f"<span class=\"tag {code}\" data-claim=\"{c['id']}\">{label}</span></a></td>"
            f"<td>{htesc(c.get('basis', ''))}</td>"
            f"<td>{_deriv_link(c['id'], derivs)}</td></tr>")
    return f"""{AUDIT_START}
<h3>Independent audit verdicts</h3>
<p>Claim-by-claim results from the <a href="../ledger/">research status ledger</a>
(Volume I audit). Each status links directly to its claim row on the ledger.
This table is generated by <code>sync_status.py</code> from the ledger and updates
automatically as the audit advances.</p>
<table class="diag">
<tr><th>Claim</th><th>Status</th><th>Basis</th><th>Derivation</th></tr>
{chr(10).join(rows)}
</table>
{AUDIT_END}"""


def cmd_render(reg=None):
    reg = reg or load_registry()
    derivs = load_derivations()
    key_rows = []
    for code, d in KEY.items():
        ledger = d["ledger"] or "—"
        aliases = ", ".join(d["aliases"]) or "—"
        key_rows.append(
            f'<tr id="tag-{code}"><td><span class="tag {code}">{code}</span></td>'
            f"<td>{htesc(d['label'])}</td><td>{htesc(d['meaning'])}</td>"
            f"<td>{htesc(ledger)}</td><td>{htesc(aliases)}</td></tr>")
    by_book = {}
    for c in reg["claims"]:
        by_book.setdefault(c.get("book"), []).append(c)
    sections = []
    for b in sorted(by_book, key=lambda x: (x is None, x)):
        rows = []
        for c in by_book[b]:
            code = ALIAS_TO_CANON.get(c["site_code"], c["site_code"])
            rows.append(
                f"<tr id=\"claim-{c['id']}\"><td>{htesc(c['claim'])}</td>"
                f"<td><a class=\"taglink\" href=\"#tag-{code}\""
                f" title=\"Status key: {htesc(KEY[code]['label'])}\">{_tag(code)}</a></td>"
                f"<td>{htesc(c.get('basis', ''))}</td><td><code>{c['id']}</code>"
                f"<td>{_deriv_link(c['id'], derivs)}</td></tr>")
        title = f"Book {b}" if b is not None else "Unsorted"
        sections.append(
            f"<h3>{title}</h3>\n<table class=\"ledger\">\n"
            "<tr><th>Claim</th><th>Status</th><th>Basis</th><th>ID</th><th>Derivation</th></tr>\n"
            + "\n".join(rows) + "\n</table>")
    n_books = sum(1 for b in by_book if b is not None)
    html = PAGE_TEMPLATE.format(
        TAG_CSS=TAG_CSS, updated=reg["meta"].get("generated", "?"),
        n_claims=len(reg["claims"]), n_books=n_books,
        key_rows="\n".join(key_rows), book_sections="\n".join(sections))
    os.makedirs(os.path.dirname(LEDGER_PAGE), exist_ok=True)
    with open(LEDGER_PAGE, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"rendered {LEDGER_PAGE} ({len(reg['claims'])} claims)")

    # per-book audit tables, injected at the end of each Part III section
    n_audit = 0
    for b, claims in sorted(by_book.items()):
        if b is None:
            continue
        page = os.path.join(ROOT, f"book{b}", "index.html")
        if not os.path.exists(page):
            continue
        with open(page, encoding="utf-8") as fh:
            text = fh.read()
        block = _audit_block(b, claims, derivs)
        if AUDIT_START in text:
            text = re.sub(re.escape(AUDIT_START) + r".*?" + re.escape(AUDIT_END),
                          lambda _: block, text, flags=re.S, count=1)
        else:
            m = re.search(r'<h2 id="p4">', text)
            if not m:
                print(f"  WARNING: no Part IV heading on book{b}, audit table skipped")
                continue
            text = text[:m.start()] + block + "\n" + text[m.start():]
        with open(page, "w", encoding="utf-8") as fh:
            fh.write(text)
        n_audit += 1
    print(f"rendered audit tables on {n_audit} book pages")


# ---------------------------------------------------------------- tag linking + claim sync

TAG_RE = re.compile(r'<span class="tag ([A-Z]+)"((?: data-claim="[^"]*")?)>([^<]*)</span>')


def _rel_ledger(page):
    depth = os.path.relpath(page, ROOT).count(os.sep)
    return "../" * depth + "ledger/"


TAGLINK_CSS_BLOCK = """<!-- TAGLINK-CSS-START -->
<style>
a.taglink{text-decoration:none}
a.taglink:hover .tag{filter:brightness(.94)}
a.taglink:focus-visible{outline:3px solid #0e7c86;outline-offset:2px;border-radius:4px}
</style>
<!-- TAGLINK-CSS-END -->"""

# Regions cmd_link must not re-wrap: existing taglink anchors and the
# generated audit-status blocks (owned by cmd_render, already linked).
_SPLIT_RE = re.compile(
    r'(<a class="taglink".*?</a>|<!-- AUDITSTATUS-START -->.*?<!-- AUDITSTATUS-END -->)',
    flags=re.S)


def _wrap_tag(m, rel):
    code, extra, label = m.group(1), m.group(2), m.group(3)
    canon = ALIAS_TO_CANON.get(code, code)
    return (f'<a class="taglink" href="{rel}#tag-{canon}" '
            f'title="Status key: {KEY[canon]["label"]}">'
            f"<span class=\"tag {code}\"{extra}>{label}</span></a>")


def _refresh_anchor(anchor, rel):
    # Keep the wrapper's status-key destination in sync with the span it
    # wraps (e.g. after cmd_sync_claims changes a code). Claim-anchored
    # audit links (#claim-...) are stable and left alone.
    if "#tag-" not in anchor:
        return anchor
    m = re.search(r'<span class="tag ([A-Z]+)"', anchor)
    if not m:
        return anchor
    canon = ALIAS_TO_CANON.get(m.group(1), m.group(1))
    return re.sub(r'href="[^"]+"', f'href="{rel}#tag-{canon}"', anchor, count=1)


def cmd_link():
    n_pages = 0
    for dirpath, _, filenames in os.walk(ROOT):
        if ".git" in dirpath or "ledger" in dirpath.split(os.sep):
            continue
        if "index.html" not in filenames:
            continue
        page = os.path.join(dirpath, "index.html")
        with open(page, encoding="utf-8") as fh:
            text = fh.read()
        orig = text
        rel = _rel_ledger(page)

        if "<!-- TAGLINK-CSS-START -->" not in text:
            assert "</head>" in text, page
            text = text.replace("</head>", TAGLINK_CSS_BLOCK + "\n</head>", 1)

        parts, new_text = _SPLIT_RE.split(text), ""
        for part in parts:
            if part.startswith('<a class="taglink"'):
                new_text += _refresh_anchor(part, rel)
            elif part.startswith("<!-- AUDITSTATUS-START -->"):
                new_text += part  # owned by cmd_render
            else:
                new_text += TAG_RE.sub(lambda m: _wrap_tag(m, rel), part)
        if new_text != orig:
            with open(page, "w", encoding="utf-8") as fh:
                fh.write(new_text)
            n_pages += 1
    print(f"link: {n_pages} page(s) updated")


def cmd_sync_claims(reg=None):
    reg = reg or load_registry()
    by_id = {c["id"]: c for c in reg["claims"]}
    n_pages, missing = 0, []
    for dirpath, _, filenames in os.walk(ROOT):
        if ".git" in dirpath:
            continue
        if "index.html" not in filenames:
            continue
        page = os.path.join(dirpath, "index.html")
        with open(page, encoding="utf-8") as fh:
            text = fh.read()

        def fix(m):
            code, cid, label = m.group(1), m.group(2), m.group(3)
            c = by_id.get(cid)
            if not c:
                missing.append((page, cid))
                return m.group(0)
            want_code = c["site_code"]
            if code == want_code:
                return m.group(0)
            return m.group(0).replace(
                f'class="tag {code}" data-claim="{cid}">{label}',
                f'class="tag {want_code}" data-claim="{cid}">{KEY[want_code]["label"]}')

        new_text = re.sub(r'<span class="tag ([A-Z]+)" data-claim="([^"]*)">([^<]*)</span>',
                          fix, text)
        if new_text != text:
            with open(page, "w", encoding="utf-8") as fh:
                fh.write(new_text)
            n_pages += 1
    print(f"sync-claims: updated spans on {n_pages} pages")
    for page, cid in sorted(set(missing)):
        print(f"  WARNING: data-claim {cid} on {os.path.relpath(page, ROOT)} not in registry")


def cmd_check(reg=None):
    reg = reg or load_registry()
    by_id = {c["id"]: c for c in reg["claims"]}
    problems = []
    for dirpath, _, filenames in os.walk(ROOT):
        if ".git" in dirpath:
            continue
        if "index.html" not in filenames:
            continue
        page = os.path.join(dirpath, "index.html")
        with open(page, encoding="utf-8") as fh:
            text = fh.read()
        for code in set(re.findall(r'<span class="tag ([A-Z]+)"', text)):
            if code not in KEY and code not in ALIAS_TO_CANON:
                problems.append(f"{os.path.relpath(page, ROOT)}: unknown tag code {code}")
        for cid in set(re.findall(r'data-claim="([^"]*)"', text)):
            if cid not in by_id:
                problems.append(f"{os.path.relpath(page, ROOT)}: data-claim {cid} not in registry")
    if problems:
        print(f"check: {len(problems)} problem(s)")
        for p in problems:
            print("  " + p)
    else:
        print("check: clean")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd == "all":
        reg = cmd_refresh()
        cmd_render(reg)
        # the ledger page is regenerated by cmd_render, so (re)fill its
        # site chrome afterwards — same idempotent injectors as the deploy flow
        import inject_sitenav, inject_footer, inject_comments
        inject_sitenav.main()
        inject_footer.main()
        inject_comments.main()
        cmd_sync_claims(reg)
        cmd_link()
        cmd_check(reg)
    elif cmd == "refresh":
        cmd_refresh()
    elif cmd == "render":
        cmd_render()
    elif cmd == "link":
        cmd_link()
    elif cmd == "sync-claims":
        cmd_sync_claims()
    elif cmd == "check":
        cmd_check()
    else:
        sys.exit(f"unknown command: {cmd}")


if __name__ == "__main__":
    main()
