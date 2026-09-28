#!/usr/bin/env python3
"""Assemble appendix-proofs/index.html from the transcribed fragments.

Validates that every required anchor id is present before writing.
Fails loudly on any missing id rather than shipping a broken page.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BUILD = os.path.join(ROOT, "research", "_build_p")
OUT = os.path.join(ROOT, "appendix-proofs", "index.html")

REQUIRED = {
    "frag-P-1.html": ["P-1"] + [f"P-1-k{i}" for i in range(1, 10)] + ["P-1-weyl", "P-1-twist"],
    "frag-P-2.html": ["P-2", "P-2-collapse", "P-2-reality", "P-2-crossphase",
                      "P-2-752", "P-2-commutant", "P-2-decoupling",
                      "P-2-sawfirewall", "P-2-w4c2a", "P-2-epsinvis", "P-2-census"],
    "frag-P-3.html": ["P-3", "P-3-t1", "P-3-t3", "P-3-t4", "P-3-crossratio", "P-3-calp6"],
    "frag-P-4.html": ["P-4", "P-4-context", "P-4-m7", "P-4-m8", "P-4-m9",
                      "P-4-m10", "P-4-m11", "P-4-m12", "P-4-naive12"],
    "frag-P-5.html": ["P-5", "P-5-run25", "P-5-commutant-bug", "P-5-modepure", "P-5-w4c4"],
    "frag-P-6.html": ["P-6", "P-6-secant", "P-6-l9"],
    "frag-P-8.html": ["P-8", "P-open"],
}

BOOK_TITLES = {2: "Book 2 — Canonical R-Operator Calculus",
               3: "Book 3 — Projective Phase, Orientation, and Lift Structure",
               4: "Book 4 — Geometric Rank, Coframes, and Connection",
               5: "Book 5 — Axiom Zero and the Decadic Carrier",
               6: "Book 6 — Local Symmetry and Carrier Mathematics"}

errors = []


def read(name):
    p = os.path.join(BUILD, name)
    if not os.path.exists(p):
        errors.append(f"MISSING FRAGMENT FILE: {name}")
        return ""
    return open(p, encoding="utf-8").read()


def check_ids(name, text):
    ids = set(re.findall(r'id="([^"]+)"', text))
    for want in REQUIRED[name]:
        if want not in ids:
            errors.append(f"{name}: missing required id #{want}")


parts = [read("head.html"), read("toc.html")]

for name in ["frag-P-1.html", "frag-P-2.html", "frag-P-3.html",
             "frag-P-4.html", "frag-P-5.html", "frag-P-6.html"]:
    text = read(name)
    if text:
        check_ids(name, text)
        parts.append(text)

# P-7: two fragments, wrapped with our own h2/h3 and split by book
p7_intro = """<h2 id="P-7">P-7. Audit-claim derivations (Books 2–6)</h2>
<div class="note"><b>How to read this section.</b> One condensed derivation
paragraph per audit claim in the <a href="../ledger/">research status
ledger</a> (86 claims, Books 2–6). The scope pill on each entry matches the
ledger exactly. Where the ledger's verdict is too thin for a real derivation,
the entry says so and points at the ledger row and the validation script
instead of inventing mathematics.</div>
"""
parts.append(p7_intro)

p7a = read("frag-P-7a.html")
p7b = read("frag-P-7b.html")
p7_ids = set(re.findall(r'id="([^"]+)"', p7a + p7b))
# every registry claim must have an anchor
import json
reg = json.load(open(os.path.join(ROOT, "status_registry.json")))
for c in reg["claims"]:
    if f"P-7-{c['id']}" not in p7_ids:
        errors.append(f"P-7: missing anchor for registry claim {c['id']}")


def split_by_book(*texts):
    """Parse h4 claim blocks, group by book, emit h3 headers in book order."""
    blocks = {}
    for text in texts:
        # split on h4 boundaries, keeping the header with its block
        parts = re.split(r'(?=<h4 id="P-7-b\d)', text)
        for part in parts:
            m = re.match(r'<h4 id="P-7-b(\d)-', part)
            if not m:
                continue
            blocks.setdefault(int(m.group(1)), []).append(part)
    out = []
    for book in sorted(blocks):
        out.append(f'<h3 id="P-7-b{book}">{BOOK_TITLES[book]}</h3>\n')
        out.extend(blocks[book])
    return "".join(out)


if p7a or p7b:
    parts.append(split_by_book(p7a, p7b))

p8 = read("frag-P-8.html")
if p8:
    check_ids("frag-P-8.html", p8)
    parts.append(p8)

parts.append("""<footer>
<p>Appendix P — Full Derivations. Part of the R Theory Rewrite Series.
Status labels follow the <a href="../ledger/#key">research status key</a>.
The manuscript (Google Doc) stays read-only; nothing here edits it.</p>
</footer>
<!-- COMMENTS-START -->
<!-- COMMENTS-END -->
<!-- FOOTER-START -->
<!-- FOOTER-END -->
</body>
</html>
""")

if errors:
    print("ASSEMBLY FAILED:")
    for e in errors:
        print("  " + e)
    sys.exit(1)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(parts))
print(f"assembled {OUT} ({sum(len(p) for p in parts)} bytes)")
