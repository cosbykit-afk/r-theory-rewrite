#!/usr/bin/env python3
"""Inject the wireframe navigation panel site-wide.

Replaces the old .sitenav bar with the Navigation Panel Wireframe design
(artifact slug: navigation-panel-wireframe):
  - flat deep-teal (#092d32) top bar: "R Theory" wordmark (Libre Baskerville),
    native <select> dropdown (Contents, Volume 0-IV, Index), Google
    site-restricted search, "Large text" pill switch (role=switch,
    localStorage-persisted across pages)
  - breadcrumb strip below the bar (volume button / book / position pill)
  - mobile stacked layout at <=600px; 3px teal focus rings; toast announcements

Idempotent: blocks are delimited by <!-- SITENAV-START --> / <!-- SITENAV-END -->
(head: fonts + CSS + large-text init) and <!-- SITENAV-NAV-START --> /
<!-- SITENAV-NAV-END --> (bar + crumbs + behavior JS right after <body>).
Re-running replaces the blocks in place.

Dropdown destinations are real URLs (the prototype's toast previews are not
carried over). Volumes without a landing page point at the volume's anchor
on the Contents page, matching the previous nav's approach.
Tables/Research are no longer in the top bar per the wireframe; both remain
linked from the Contents page.
Dark mode: the site has no dark-mode theme, so only the light design is
implemented; the bar itself is #092d32 in both modes per the wireframe spec.
"""

import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_RESTRICTION = "cosbykit-afk.github.io/r-theory-rewrite"

VOLUMES = [
    ("Volume 0", [20, 21, 22], "vol0/"),
    ("Volume I", [0, 1, 2, 3, 4, 5, 6], "contents/#vol-1"),
    ("Volume II", [7, 8, 9, 10, 11, 12, 13], "contents/#vol-2"),
    ("Volume III", [14, 15, 16], "contents/#vol-3"),
    ("Volume IV", [17, 18, 19], "vol4/"),
]
BOOK_VOLUME = {}
for _name, _books, _dest in VOLUMES:
    for _b in _books:
        BOOK_VOLUME[_b] = (_name, _books, _dest)

LABELS = {
    "appendix": "Appendix",
    "contents": "Contents",
    "guide": "Guide",
    "index": "Index",
    "research": "Research",
    "sitemap": "Site map",
    "tables": "Tables",
    "title": "Title page",
    "vol0": "Volume 0",
    "vol4": "Volume IV",
}

CSS_BLOCK = """<!-- SITENAV-START -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@700&family=Source+Sans+3:wght@500;600;700&display=swap" rel="stylesheet">
<style>
body{overflow-x:clip}
.sitebar{background:#092d32;color:#eaf5f4;margin-left:calc(50% - 50vw);margin-right:calc(50% - 50vw)}
.sitebar-inner{max-width:860px;margin:0 auto;padding:11px 24px;min-height:52px;box-sizing:border-box;
 display:flex;align-items:center;gap:14px;flex-wrap:wrap;
 font-family:'Source Sans 3',system-ui,-apple-system,'Segoe UI',sans-serif}
.site-mark{font-family:'Libre Baskerville',Georgia,serif;font-weight:700;font-size:.92rem;
 color:#fff;text-decoration:none;white-space:nowrap}
.site-mark:hover{text-decoration:underline}
.site-select-wrap{position:relative;flex:none}
.site-select-wrap::after{content:"";position:absolute;right:12px;top:50%;width:7px;height:7px;
 border-right:2px solid #c6dcda;border-bottom:2px solid #c6dcda;
 transform:translateY(-70%) rotate(45deg);pointer-events:none}
.site-dest{appearance:none;-webkit-appearance:none;background:#123d43;border:1px solid #38636a;
 border-radius:6px;color:#fff;font-family:inherit;font-weight:600;font-size:.88rem;
 padding:7px 34px 7px 11px;min-height:36px;width:min(240px,100%);cursor:pointer}
.site-dest:hover{background:#164a51;border-color:#5f858a}
.site-search{display:flex;align-items:center;height:36px;min-width:280px;margin-left:auto;flex:1 1 auto;max-width:340px}
.site-search input[type=text]{flex:1;min-width:0;height:36px;box-sizing:border-box;
 border:1px solid #38636a;border-right:none;border-radius:6px 0 0 6px;padding:7px 10px;
 font-family:inherit;font-weight:500;font-size:.84rem;color:#10262b;background:#fff}
.site-search input[type=text]::placeholder{color:#66777a}
.site-search button{height:36px;box-sizing:border-box;border:1px solid #38636a;border-radius:0 6px 6px 0;
 background:#165159;color:#fff;font-family:inherit;font-weight:700;font-size:.84rem;
 padding:0 12px;cursor:pointer;flex:none}
.site-search button:hover{background:#1b626b}
.text-toggle{display:flex;align-items:center;gap:8px;color:#eaf5f4;font-size:.84rem;
 font-weight:600;cursor:pointer;white-space:nowrap;flex:none}
.text-toggle input{appearance:none;-webkit-appearance:none;width:38px;height:22px;border-radius:999px;
 background:#123d43;border:1px solid #5f858a;position:relative;cursor:pointer;margin:0;flex:none;
 transition:background .18s,border-color .18s}
.text-toggle input::after{content:"";position:absolute;left:2px;top:2px;width:16px;height:16px;
 border-radius:50%;background:#c6dcda;transition:transform .18s,background .18s}
.text-toggle input:checked{background:#b85f1d;border-color:#b85f1d}
.text-toggle input:checked::after{transform:translateX(16px);background:#fff}
.site-dest:focus-visible,.site-search input[type=text]:focus-visible,
.site-search button:focus-visible,.text-toggle input:focus-visible,.site-mark:focus-visible,
.crumbbar a:focus-visible{outline:3px solid #4fc3b8;outline-offset:2px}
.crumbbar{background:#f5f8f8;border-bottom:1px solid #c9d6d8;
 margin-left:calc(50% - 50vw);margin-right:calc(50% - 50vw);margin-bottom:1.5em}
.crumbbar-inner{max-width:860px;margin:0 auto;padding:8px 24px;box-sizing:border-box;
 display:flex;align-items:center;gap:10px;flex-wrap:wrap;
 font-family:'Source Sans 3',system-ui,-apple-system,'Segoe UI',sans-serif;
 font-size:.8rem;color:#52676b}
.crumbbar a{color:#0b6866;text-decoration:none;font-weight:600}
.crumbbar a:hover{text-decoration:underline}
.crumb-vol{background:#0b6866;color:#fff !important;border-radius:6px;padding:3px 10px;font-weight:700}
.crumb-vol:hover{background:#084c4b;text-decoration:none !important}
.crumb-sep{color:#8aa0a3}
.crumb-pill{font-size:.72rem;font-weight:700;background:#e3ecec;color:#10262b;
 border-radius:999px;padding:2px 10px}
.rth-toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%) translateY(8px);
 background:#092d32;color:#fff;font-family:'Source Sans 3',system-ui,sans-serif;
 font-size:.85rem;font-weight:600;padding:10px 18px;border-radius:8px;opacity:0;
 pointer-events:none;transition:opacity .2s,transform .2s;z-index:9999}
.rth-toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
html.rth-large-text body{font-size:21.333px;line-height:1.65}
@media (max-width:600px){
 .sitebar-inner{gap:8px;padding:10px 14px}
 .site-select-wrap{order:3;width:100%}
 .site-dest{width:100%}
 .site-search{order:4;width:100%;min-width:0;max-width:none;margin-left:0}
 .text-toggle{margin-left:auto}
 .crumbbar-inner{padding:8px 14px}
}
</style>
<script>
(function(){try{if(localStorage.getItem('rth-large-text')==='1'){document.documentElement.classList.add('rth-large-text');}}catch(e){}})();
</script>
<!-- SITENAV-END -->"""

NAV_TMPL = """<!-- SITENAV-NAV-START -->
<nav class="sitebar" aria-label="Proposed global navigation">
<div class="sitebar-inner">
<a class="site-mark" href="{p}">R Theory</a>
<span class="site-select-wrap"><select class="site-dest" id="rthSiteDest" aria-label="Go to section">
<option value="{p}contents/" selected>Contents</option>
<option value="{p}vol0/">Volume 0</option>
<option value="{p}contents/#vol-1">Volume I</option>
<option value="{p}contents/#vol-2">Volume II</option>
<option value="{p}contents/#vol-3">Volume III</option>
<option value="{p}vol4/">Volume IV</option>
<option value="{p}index/">Index</option>
</select></span>
<form class="site-search" id="rthSiteSearch" action="https://www.google.com/search" method="get" target="_blank" rel="noopener" role="search">
<input type="hidden" name="q" id="rthSearchQ" value="">
<input type="text" id="rthSearchTerm" placeholder="Search R Theory" aria-label="Search R Theory" autocomplete="off">
<button type="submit">Search</button>
</form>
<label class="text-toggle"><span>Large text</span><input type="checkbox" id="rthLargeText" role="switch" aria-label="Large text"></label>
</div>
</nav>
<div class="crumbbar"><div class="crumbbar-inner">
{crumb}
</div></div>
<div class="rth-toast" id="rthToast" role="status" aria-live="polite"></div>
<script>
(function(){{
 var toast=document.getElementById('rthToast'),t=null;
 function say(m){{toast.textContent=m;toast.classList.add('show');clearTimeout(t);
  t=setTimeout(function(){{toast.classList.remove('show');}},1500);}}
 var sel=document.getElementById('rthSiteDest');
 sel.addEventListener('change',function(){{if(sel.value)location.href=sel.value;}});
 var form=document.getElementById('rthSiteSearch'),
     term=document.getElementById('rthSearchTerm'),
     q=document.getElementById('rthSearchQ');
 form.addEventListener('submit',function(e){{
  var v=term.value.trim();
  if(!v){{e.preventDefault();term.focus();say('Enter a search term');return;}}
  q.value='site:{site} '+v;
 }});
 var tg=document.getElementById('rthLargeText');
 tg.checked=document.documentElement.classList.contains('rth-large-text');
 tg.addEventListener('change',function(){{
  var on=tg.checked;
  document.documentElement.classList.toggle('rth-large-text',on);
  try{{localStorage.setItem('rth-large-text',on?'1':'0');}}catch(e){{}}
  say(on?'Large text on':'Large text off');
 }});
}})();
</script>
<!-- SITENAV-NAV-END -->"""


def crumb_for(key, prefix):
    if key.startswith("book") and key[4:].isdigit():
        n = int(key[4:])
        vol_name, vol_books, vol_dest = BOOK_VOLUME[n]
        pos = vol_books.index(n) + 1
        return (
            '<a class="crumb-vol" href="{p}{d}">{v}</a>'
            '<span class="crumb-sep">/</span><span>Book {n}</span>'
            '<span class="crumb-pill">{pos} of {total}</span>'
        ).format(p=prefix, d=vol_dest, v=vol_name, n=n, pos=pos,
                 total=len(vol_books))
    if key == "":
        return "<span>Home</span>"
    label = LABELS.get(key, key.replace("-", " ").title())
    return ('<a href="{p}">Home</a><span class="crumb-sep">/</span>'
            "<span>{label}</span>").format(p=prefix, label=label)


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
        parts = rel.split(os.sep)
        key = "" if len(parts) == 1 else parts[0]
        prefix = "../" * (len(parts) - 1)
        with open(page, encoding="utf-8") as fh:
            text = fh.read()

        text, had_css = replace_block(text, "<!-- SITENAV-START -->",
                                      "<!-- SITENAV-END -->", CSS_BLOCK)
        if not had_css:
            assert "</head>" in text, page
            text = text.replace("</head>", CSS_BLOCK + "\n</head>", 1)

        nav = NAV_TMPL.format(p=prefix, site=SITE_RESTRICTION,
                              crumb=crumb_for(key, prefix))
        text, had_nav = replace_block(text, "<!-- SITENAV-NAV-START -->",
                                      "<!-- SITENAV-NAV-END -->", nav)
        if not had_nav:
            m = re.search(r"<body[^>]*>", text)
            assert m, page
            text = text[: m.end()] + "\n" + nav + text[m.end():]

        with open(page, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("injected", rel)


if __name__ == "__main__":
    main()
