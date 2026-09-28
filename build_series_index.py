#!/usr/bin/env python3
"""Alphabetical index for the R Theory rewrite site.

1. Adds id attributes to <h3> elements that lack them (every content page).
2. Generates index-of-index: every h2/h3 heading across the series becomes an
   index entry, alphabetized, each linking straight to its anchor.
   Skips the site home page and the contents page (navigational, not content).
"""

import os
import re
import html

ROOT = os.path.dirname(os.path.abspath(__file__))
SKIP_DIRS = {"contents", "index"}  # navigational pages, not content
SKIP_FILES = {"index.html"}       # site home


def clean_text(raw):
    t = re.sub(r"<[^>]+>", "", raw)
    return html.unescape(re.sub(r"\s+", " ", t)).strip()


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "s"


def add_missing_h3_ids(text):
    seen = set(re.findall(r'id="([^"]+)"', text))

    def repl(m):
        attrs, inner = m.group(1), m.group(2)
        if 'id="' in attrs:
            return m.group(0)
        base = slugify(clean_text(inner))
        cand, n = base, 2
        while cand in seen:
            cand = f"{base}-{n}"
            n += 1
        seen.add(cand)
        return f"<h3{attrs} id=\"{cand}\">{inner}</h3>"

    return re.sub(r"<h3([^>]*)>(.*?)</h3>", repl, text, flags=re.S)


def short_label(d):
    if d.startswith("book"):
        return "Book " + d[4:]
    return {"vol0": "Volume 0", "vol4": "Volume IV", "tables": "Tables",
            "appendix": "Appendix", "research": "Research",
            "guide": "Guide", "title": "Title page"}.get(d, d)


def sort_key(term):
    k = term.lower()
    k = re.sub(r"^[^a-z]+", "", k)  # ignore leading §, digits, punctuation
    return k or term.lower()


# A section label like "§4.", "Figure 1", "Part I", "1.I", "6.3A" leads the
# heading; the keyword is the first content word after it. Rework the title
# so the keyword comes first and the label trails in parentheses:
#   "§4. A phase gradient carries no curvature" -> "Phase gradient carries no
#   curvature (§4)"
LABEL_RE = re.compile(
    r"^(§\s*[\w.]+|Figure \d+|Part [IVXLC]+|[\d][\w.]*?)\s*[—–:]\s*"
    r"|^(§\s*[\w.]+\.|[\d][\w.]*\.)\s+"
)
ARTICLE_RE = re.compile(r"^(a|an|the)\s+", re.IGNORECASE)


def keyword_title(term):
    m = LABEL_RE.match(term)
    label = m.group(1) if m else ""
    rest = term[m.end():] if m else term
    rest = ARTICLE_RE.sub("", rest).strip()
    if not rest:
        return term, sort_key(term)
    display = f"{rest} ({label})" if label else rest
    return display, sort_key(rest)


def main():
    entries = []  # (term, dir, anchor)
    pages = []
    for dirpath, _, fns in os.walk(ROOT):
        if ".git" in dirpath:
            continue
        if "index.html" not in fns:
            continue
        rel = os.path.relpath(os.path.join(dirpath, "index.html"), ROOT)
        d = os.path.dirname(rel)
        if d in SKIP_DIRS or (d == "" and "index.html" in SKIP_FILES):
            continue
        pages.append((d, rel))

    for d, rel in sorted(pages):
        p = os.path.join(ROOT, rel)
        text = open(p, encoding="utf-8").read()
        new = add_missing_h3_ids(text)
        if new != text:
            open(p, "w", encoding="utf-8").write(new)
            text = new
        for tag in ("h2", "h3"):
            for attrs, inner in re.findall(r"<%s([^>]*)>(.*?)</%s>"
                                           % (tag, tag), text, re.S):
                m = re.search(r'id="([^"]+)"', attrs)
                if not m:
                    continue
                term = clean_text(inner)
                if term:
                    display, key = keyword_title(term)
                    entries.append((key, display, d, m.group(1)))
    print(f"{len(entries)} entries from {len(pages)} pages")

    # group by letter
    groups = {}
    for key, display, d, a in entries:
        letter = key[0].upper() if key and key[0].isalpha() else "#"
        groups.setdefault(letter, []).append((key, display, d, a))
    for letter in groups:
        groups[letter].sort(key=lambda e: (e[0], e[2], e[3]))

    letters = sorted(groups)
    jump = " · ".join(f'<a href="#ix-{l.lower()}">{l}</a>' for l in letters)

    body = []
    body.append("<h1>Index</h1>")
    body.append('<p class="sub">Every section heading across the series, '
                "alphabetized. Click an entry to land exactly at that "
                "section.</p>")
    body.append(f'<p class="jump">{jump}</p>')
    for letter in letters:
        body.append(f'<h2 id="ix-{letter.lower()}">{letter}</h2>')
        body.append("<ul>")
        for _, display, d, a in groups[letter]:
            loc = (f'<a href="../{d}/#{a}">'
                   f"{html.escape(short_label(d))}</a>")
            body.append(f"  <li><b>{html.escape(display)}</b> — {loc}</li>")
        body.append("</ul>")
    inner = "\n".join(body)

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Index — R Theory Rewrite Series</title>
<style>
  :root {{ --ink:#1a1a1a; --muted:#5a5a5a; --accent:#1b5faa; --paper:#fff; --wash:#f6f8fb; --line:#dfe5ec; }}
  body {{ font-family: -apple-system, "Segoe UI", Georgia, serif; color:var(--ink); background:var(--paper);
         max-width: 860px; margin:0 auto; padding: 24px 20px 80px; line-height:1.65; }}
  h1 {{ font-size:1.9em; line-height:1.25; margin-bottom:.2em; }}
  h2 {{ font-size:1.45em; margin-top:2em; border-bottom:2px solid var(--line); padding-bottom:.3em; }}
  .sub {{ color:var(--muted); font-size:1.05em; margin-top:.4em; }}
  .jump {{ background:var(--wash); border:1px solid var(--line); border-radius:8px;
           padding:10px 14px; line-height:2; }}
  .jump a {{ color:var(--accent); text-decoration:none; margin:0 2px; }}
  ul {{ margin:.4em 0 1em; padding-left:1.2em; list-style:none; }}
  li {{ margin:.3em 0; padding-left:0; }}
  li b {{ font-weight:600; }}
  li a {{ color:var(--accent); text-decoration:none; white-space:nowrap; }}
  li a:hover {{ text-decoration:underline; }}
  footer {{ margin-top:3em; color:var(--muted); font-size:.88em; border-top:1px solid var(--line); padding-top:1em; }}
  footer a {{ color:var(--accent); text-decoration:none; }}
</style>
</head>
<body>
{inner}
<footer>
<p><a href="../">R Theory — A Visual Rewrite</a> &middot; by
<a href="https://orcid.org/0009-0003-5392-2359">Christopher (Kit) Michael Cosby</a></p>
</footer>
</body>
</html>
"""
    # the directory index/ holds index/index.html -- no clash with the
    # site home page (root index.html); the index page excludes itself.
    os.makedirs(os.path.join(ROOT, "index"), exist_ok=True)
    with open(os.path.join(ROOT, "index", "index.html"), "w",
              encoding="utf-8") as fh:
        fh.write(page)
    print("wrote index/index.html")


if __name__ == "__main__":
    main()
