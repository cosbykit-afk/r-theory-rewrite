#!/usr/bin/env python3
"""Add the wireframe's copper volume-handoff state to the existing .booknav
footer dock: the Next card of a volume's final book gets a copper tint
(border + warm background), signalling the boundary into the next volume.

Targets: book6 (Vol I -> II), book13 (Vol II -> III), book16 (Vol III -> IV).
book22 already bridges into Volume I via its Next panel; book19 is the
series' final book (no next volume).

Idempotent: CSS is delimited by <!-- BOOKNAV-CSS-START --> /
<!-- BOOKNAV-CSS-END -->; the handoff class is added once per target page.
"""
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
BOUNDARY_BOOKS = ("book6", "book13", "book16")

HANDOFF_CSS = """
.booknav-panel.booknav-handoff{border-color:#b85f1d;
 background:linear-gradient(180deg,#fffaf5 0%,#f7e7d9 60%,#f3ddc6 100%)}
.booknav-panel.booknav-handoff .booknav-eyebrow{color:#b85f1d}
a.booknav-panel.booknav-handoff:hover{border-color:#b85f1d;
 box-shadow:inset 0 1px 0 #ffffff,0 4px 12px rgba(184,95,29,.22)}"""


def main():
    for dirpath, _, filenames in os.walk(ROOT):
        if ".git" in dirpath or "index.html" not in filenames:
            continue
        key = os.path.basename(dirpath)
        if not (key.startswith("book") and key[4:].isdigit()):
            continue
        page = os.path.join(dirpath, "index.html")
        with open(page, encoding="utf-8") as fh:
            text = fh.read()

        # 1. handoff CSS into the BOOKNAV-CSS block (all book pages).
        # First strip any earlier copy (the first version landed after
        # </style>, where it was dead text), then insert before </style>.
        text = text.replace(HANDOFF_CSS + "\n", "")
        text = text.replace(HANDOFF_CSS, "")
        pat = re.compile(r"</style>\s*<!-- BOOKNAV-CSS-END -->")
        text, n = pat.subn(HANDOFF_CSS + "\n</style>\n<!-- BOOKNAV-CSS-END -->",
                           text, count=1)
        assert n == 1, page

        # 2. handoff class on the Next card (boundary books only)
        if key in BOUNDARY_BOOKS and "booknav-next booknav-handoff" not in text:
            text, n = re.subn(
                r'class="booknav-panel booknav-next"',
                'class="booknav-panel booknav-next booknav-handoff"',
                text, count=1)
            assert n == 1, page

        with open(page, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("handoff", key)


if __name__ == "__main__":
    main()
