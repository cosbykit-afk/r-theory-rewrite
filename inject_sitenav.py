#!/usr/bin/env python3
"""Inject a site-wide navigation panel + Google site-search bar into every
page of the r-theory-rewrite site.

Idempotent: blocks are delimited by <!-- SITENAV-START --> / <!-- SITENAV-END -->
(CSS in <head>) and <!-- SITENAV-NAV-START --> / <!-- SITENAV-NAV-END -->
(nav right after <body>). Re-running replaces the blocks in place.

The Google search submits to google.com/search with a `site:` restriction
prepended via onsubmit JS (no CSE ID needed; degrades to plain Google search
with JS disabled). SITE_RESTRICTION is the one constant to change if the
published domain ever differs from the standard GitHub Pages URL.
"""

import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_RESTRICTION = "cosbykit-afk.github.io/r-theory-rewrite"

CSS_BLOCK = """<!-- SITENAV-START -->
<style>
.sitenav{font-family:Georgia,serif;font-size:.88em;background:#f4f4f0;border:1px solid #bbb;
 border-radius:4px;padding:8px 14px;margin:0 0 1.5em;display:flex;flex-wrap:wrap;
 align-items:center;gap:8px 16px;line-height:1.4}
.sitenav a{color:#0645ad;text-decoration:none;white-space:nowrap}
.sitenav a:hover{text-decoration:underline}
.sitenav .sitenav-brand{font-weight:bold;color:#1a1a1a}
.sitenav .sitenav-links{display:flex;flex-wrap:wrap;gap:8px 14px}
.sitenav-search{margin-left:auto;display:flex;gap:6px;align-items:center}
.sitenav-search input{font-family:Georgia,serif;font-size:.95em;padding:4px 8px;
 border:1px solid #999;border-radius:3px;width:170px;background:#fff;color:#1a1a1a}
.sitenav-search button{font-family:Georgia,serif;font-size:.95em;padding:4px 12px;
 border:1px solid #666;border-radius:3px;background:#eee;cursor:pointer;color:#1a1a1a}
</style>
<!-- SITENAV-END -->"""

NAV_TMPL = """<!-- SITENAV-NAV-START -->
<nav class="sitenav" aria-label="Site navigation">
<a class="sitenav-brand" href="{p}">R Theory — Rewrite</a>
<span class="sitenav-links">
<a href="{p}contents/">Contents</a><a href="{p}index/">Index</a><a href="{p}contents/#vol-0">Vol&nbsp;0</a><a href="{p}contents/#vol-1">Vol&nbsp;I</a><a href="{p}contents/#vol-2">Vol&nbsp;II</a><a href="{p}contents/#vol-3">Vol&nbsp;III</a><a href="{p}contents/#vol-4">Vol&nbsp;IV</a><a href="{p}tables/">Tables</a><a href="{p}research/">Research</a>
</span>
<form class="sitenav-search" action="https://www.google.com/search" method="get" target="_blank" role="search"
 onsubmit="if(!this.q.value.trim())return false;this.q.value='site:{site} '+this.q.value">
<input type="text" name="q" placeholder="Search this site&#8230;" aria-label="Search this site">
<button type="submit">Search</button>
</form>
</nav>
<!-- SITENAV-NAV-END -->"""


def replace_block(text, start, end, new):
    if start in text:
        pat = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
        return pat.sub(lambda _: new, text, count=1), True
    return text, False


def main():
    pages = []
    for dirpath, _, filenames in os.walk(ROOT):
        if ".git" in dirpath:
            continue
        if "index.html" in filenames:
            pages.append(os.path.join(dirpath, "index.html"))
    pages.sort()
    print(f"{len(pages)} pages")
    for page in pages:
        rel = os.path.relpath(page, ROOT)
        depth = rel.count(os.sep)  # book15/index.html -> 1
        prefix = "../" * depth
        with open(page) as fh:
            text = fh.read()

        # CSS into <head>
        text, had_css = replace_block(text, "<!-- SITENAV-START -->",
                                      "<!-- SITENAV-END -->", CSS_BLOCK)
        if not had_css:
            assert "</head>" in text, page
            text = text.replace("</head>", CSS_BLOCK + "\n</head>", 1)

        # nav right after <body>
        nav = NAV_TMPL.format(p=prefix, site=SITE_RESTRICTION)
        text, had_nav = replace_block(text, "<!-- SITENAV-NAV-START -->",
                                      "<!-- SITENAV-NAV-END -->", nav)
        if not had_nav:
            m = re.search(r"<body[^>]*>", text)
            assert m, page
            text = text[: m.end()] + "\n" + nav + text[m.end():]

        with open(page, "w") as fh:
            fh.write(text)
        print("injected", rel)


if __name__ == "__main__":
    main()
