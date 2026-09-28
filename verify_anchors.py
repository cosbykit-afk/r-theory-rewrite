#!/usr/bin/env python3
"""Verify every href="#frag" / "page/#frag" resolves to an existing id."""
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))

idmap = {}
for dirpath, _, fns in os.walk(ROOT):
    if ".git" in dirpath:
        continue
    if "index.html" in fns:
        p = os.path.join(dirpath, "index.html")
        text = open(p, encoding="utf-8").read()
        idmap[os.path.relpath(p, ROOT)] = set(
            re.findall(r'id="([^"]+)"', text))

bad = []
for rel in sorted(idmap):
    text = open(os.path.join(ROOT, rel), encoding="utf-8").read()
    base = os.path.dirname(rel)
    for href in re.findall(r'href="([^"]+)"', text):
        if href.startswith(("http", "mailto")) or "#" not in href:
            continue
        path, frag = href.split("#", 1)
        if not path:
            target, target_ids = rel, idmap[rel]
        else:
            target = os.path.normpath(os.path.join(base, path))
            if target in (".", "..", ""):
                target = "index.html"
            elif target.endswith("/"):
                target += "index.html"
            elif target not in idmap and target + "/index.html" in idmap:
                target += "/index.html"
            if target not in idmap:
                bad.append((rel, href, "TARGET PAGE MISSING"))
                continue
            target_ids = idmap[target]
        if frag and frag not in target_ids:
            bad.append((rel, href, "anchor missing in " + target))

if bad:
    print("BROKEN:", len(bad))
    for b in bad[:25]:
        print("  ", b)
else:
    print("OK: all anchors resolve (%d pages checked)" % len(idmap))
