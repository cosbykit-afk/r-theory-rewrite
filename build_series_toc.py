#!/usr/bin/env python3
"""Series-wide table of contents for the R Theory rewrite site.

1. Adds id attributes to <h2> elements that lack them (appendix, guide,
   research, tables, title, vol0, vol4).
2. Adds a "Contents." link block (same style as book1) to the restructured
   pages that lack one (book0,7,8,10,11,12,20,21,22).
3. Generates contents/index.html: every volume, every book, every Part/section
   as an anchor link straight into its place in the book page.

Idempotent-ish: skips pages already processed (checks for existing ids /
existing <div class="toc">).
"""

import os
import re
import html

ROOT = os.path.dirname(os.path.abspath(__file__))

NEEDS_IDS = ["appendix", "guide", "research", "tables", "title", "vol0", "vol4"]
NEEDS_TOC = ["book0", "book7", "book8", "book10", "book11", "book12",
             "book20", "book21", "book22"]

TOC_CSS = (".toc{background:#f4f4f0;border:1px solid #ccc;border-radius:4px;"
           "padding:8px 14px;margin:1.2em 0}\n"
           ".toc a{color:#0645ad;text-decoration:none}\n"
           ".toc a:hover{text-decoration:underline}")


def clean_text(raw):
    t = re.sub(r"<[^>]+>", "", raw)
    t = html.unescape(re.sub(r"\s+", " ", t)).strip()
    return t


def slugify(text):
    s = text.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "section"


def h2_list(text):
    """[(id_or_None, clean_text), ...] in document order."""
    out = []
    for attrs, inner in re.findall(r"<h2([^>]*)>(.*?)</h2>", text, re.S):
        m = re.search(r'id="([^"]+)"', attrs)
        out.append((m.group(1) if m else None, clean_text(inner)))
    return out


def add_missing_h2_ids(text):
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
        return f"<h2{attrs} id=\"{cand}\">{inner}</h2>"

    return re.sub(r"<h2([^>]*)>(.*?)</h2>", repl, text, flags=re.S)


def short_label(h2text):
    """'Part I — See it first' -> 'I. See it first'; '§1 — ...' unchanged."""
    t = h2text
    if t.startswith("Part "):
        t = t[len("Part "):]
        t = t.replace(" — ", ". ", 1)
    return t


def add_contents_block(page_dir, text):
    if '<div class="toc">' in text:
        return text, False
    heads = [(i, t) for i, t in h2_list(text) if i]
    if not heads:
        raise RuntimeError(f"no headed sections in {page_dir}")
    items = " · ".join(
        f'<a href="#{i}">{html.escape(short_label(t))}</a>' for i, t in heads)
    block = (f'<div class="toc">\n<p><b>Contents.</b> {items}</p>\n</div>\n')
    # insert after the about box if present, else after the sub paragraph
    m = re.search(r'<div class="about">.*?</div>', text, re.S)
    if m:
        text = text[:m.end()] + "\n" + block + text[m.end():]
    else:
        m2 = re.search(r'<p class="sub">.*?</p>', text, re.S)
        assert m2, page_dir
        text = text[:m2.end()] + "\n" + block + text[m2.end():]
    # add .toc css if missing
    if ".toc{" not in text and ".toc " not in text:
        text = text.replace("</style>", TOC_CSS + "\n</style>", 1)
    return text, True


def page_title(text):
    m = re.search(r"<title>(.*?)</title>", text, re.S)
    return clean_text(m.group(1)) if m else "?"


def main():
    changed = []
    # 1. h2 ids
    for d in NEEDS_IDS:
        p = os.path.join(ROOT, d, "index.html")
        text = open(p, encoding="utf-8").read()
        new = add_missing_h2_ids(text)
        if new != text:
            open(p, "w", encoding="utf-8").write(new)
            changed.append(d + " (h2 ids)")
    # 2. Contents blocks
    for d in NEEDS_TOC:
        p = os.path.join(ROOT, d, "index.html")
        text = open(p, encoding="utf-8").read()
        new, did = add_contents_block(d, text)
        if did:
            open(p, "w", encoding="utf-8").write(new)
            changed.append(d + " (Contents block)")
    print("changed:", changed or "none")

    # 3. gather structure for the series TOC page
    def struct(d):
        text = open(os.path.join(ROOT, d, "index.html"), encoding="utf-8").read()
        return page_title(text), [(i, t) for i, t in h2_list(text) if i]

    volumes = [
        ("vol-0", "Volume 0 — Exact Witnesses at the Physics Boundary",
         ["vol0", "book20", "book21", "book22"]),
        ("vol-1", "Volume I — Books 0–6",
         ["book0", "book1", "book2", "book3", "book4", "book5", "book6"]),
        ("vol-2", "Volume II — Books 7–13",
         ["book7", "book8", "book9", "book10", "book11", "book12", "book13"]),
        ("vol-3", "Volume III — Books 14–16",
         ["book14", "book15", "book16"]),
        ("vol-4", "Volume IV — The Discrete Octant and the Computational Frontier",
         ["vol4", "book17", "book18", "book19"]),
    ]
    companions = ["tables", "appendix", "research", "guide", "title"]

    body = []
    body.append("<h1>Contents — the entire series</h1>")
    body.append(
        '<p class="sub">Every book and companion page, with each section as '
        "a hyperlink anchor straight to its place in the page. Click a "
        "section to land exactly there.</p>")
    for vid, vtitle, dirs in volumes:
        body.append(f'<h2 id="{vid}">{html.escape(vtitle)}</h2>')
        for d in dirs:
            title, heads = struct(d)
            body.append(
                f'<h3><a href="../{d}/">{html.escape(title)}</a></h3>')
            lis = "\n".join(
                f'  <li><a href="../{d}/#{i}">'
                f"{html.escape(short_label(t))}</a></li>"
                for i, t in heads)
            body.append(f"<ul>\n{lis}\n</ul>")
    body.append('<h2 id="companions">Companion pages</h2>')
    for d in companions:
        title, heads = struct(d)
        body.append(f'<h3><a href="../{d}/">{html.escape(title)}</a></h3>')
        lis = "\n".join(
            f'  <li><a href="../{d}/#{i}">{html.escape(t)}</a></li>'
            for i, t in heads)
        body.append(f"<ul>\n{lis}\n</ul>")
    inner = "\n".join(body)

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Contents — R Theory Rewrite Series</title>
<style>
  :root {{ --ink:#1a1a1a; --muted:#5a5a5a; --accent:#1b5faa; --paper:#fff; --wash:#f6f8fb; --line:#dfe5ec; }}
  body {{ font-family: -apple-system, "Segoe UI", Georgia, serif; color:var(--ink); background:var(--paper);
         max-width: 860px; margin:0 auto; padding: 24px 20px 80px; line-height:1.65; }}
  h1 {{ font-size:1.9em; line-height:1.25; margin-bottom:.2em; }}
  h2 {{ font-size:1.45em; margin-top:2.2em; border-bottom:2px solid var(--line); padding-bottom:.3em; }}
  h3 {{ font-size:1.1em; margin:1.4em 0 .3em; }}
  h3 a {{ color:var(--ink); text-decoration:none; }}
  h3 a:hover {{ text-decoration:underline; }}
  .sub {{ color:var(--muted); font-size:1.05em; margin-top:.4em; }}
  ul {{ margin:.4em 0 1em; padding-left:1.4em; }}
  li {{ margin:.25em 0; }}
  li a {{ color:var(--accent); text-decoration:none; }}
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
    os.makedirs(os.path.join(ROOT, "contents"), exist_ok=True)
    with open(os.path.join(ROOT, "contents", "index.html"), "w",
              encoding="utf-8") as fh:
        fh.write(page)
    print("wrote contents/index.html")


if __name__ == "__main__":
    main()
