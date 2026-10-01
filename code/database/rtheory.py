#!/usr/bin/env python3
"""rtheory — CLI for the R Theory database (theorems + prose, single source).

The website builds from this DB's exported feeds. Proof sessions write
verdicts here; the site build regenerates pages from the feeds.

Usage:
    rtheory.py init [--db PATH]
    rtheory.py import-status-registry [--db PATH] [--registry PATH]
    rtheory.py set-status ID CODE --evidence "..." [--actor NAME]
    rtheory.py add-prose --id SLUG --title T --page P --section S --body-file F
    rtheory.py link-prose PROSE_ID THEOREM_ID
    rtheory.py export-feeds [--db PATH] [--out DIR]
    rtheory.py render-ledger [--db PATH]          # ledger claim table HTML
    rtheory.py stats [--db PATH]
"""
import argparse
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone

HOME = os.path.expanduser("~")
DB_DIR = os.path.join(HOME, "workspace", "r-theory-db")
DEFAULT_DB = os.path.join(DB_DIR, "rtheory.db")
SCHEMA = os.path.join(DB_DIR, "schema.sql")
DEFAULT_REGISTRY = os.path.join(HOME, "workspace", "r-theory-rewrite",
                                "status_registry.json")


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")


def connect(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def changelog(con, actor, table, row_id, action, detail=""):
    con.execute(
        "INSERT INTO changelog (at, actor, table_name, row_id, action, detail)"
        " VALUES (?,?,?,?,?,?)",
        (now(), actor, table, row_id, action, detail))


# ------------------------------------------------------------------ commands

def cmd_init(args):
    if os.path.exists(args.db) and not args.force:
        print(f"exists: {args.db} (use --force to rebuild)")
        return
    if args.force and os.path.exists(args.db):
        os.remove(args.db)
    con = connect(args.db)
    con.executescript(open(SCHEMA).read())
    con.commit()
    print(f"initialized {args.db}")


def cmd_import_registry(args):
    reg = json.load(open(args.registry))
    con = connect(args.db)
    # 1. status codes from the registry key
    for code, k in reg["key"].items():
        con.execute(
            """INSERT INTO status_codes (code, label, meaning, ledger_status)
               VALUES (?,?,?,?)
               ON CONFLICT(code) DO UPDATE SET
                 label=excluded.label, meaning=excluded.meaning,
                 ledger_status=excluded.ledger_status""",
            (code, k["label"], k["meaning"], k.get("ledger")))
    # 2. theorems (claims)
    n_new = n_upd = 0
    for c in reg["claims"]:
        row = con.execute("SELECT * FROM theorems WHERE id=?",
                          (c["id"],)).fetchone()
        book = c.get("book")
        if row is None:
            con.execute(
                """INSERT INTO theorems
                   (id, book, section, label, statement, status_code,
                    evidence, source, version, created_at, updated_at, notes)
                   VALUES (?,?,?,?,?,?,?,?,1,?,?,?)""",
                (c["id"], book, c.get("section", ""), "",
                 c.get("claim", ""), c["site_code"],
                 c.get("basis", ""), c.get("source", "status_registry.json"),
                 now(), now(), ""))
            changelog(con, "import", "theorems", c["id"], "insert",
                      "from status_registry.json")
            n_new += 1
        else:
            changed = (row["statement"] != c.get("claim", "") or
                       row["status_code"] != c["site_code"] or
                       row["section"] != c.get("section", ""))
            if changed:
                old_code = row["status_code"]
                con.execute(
                    """UPDATE theorems SET book=?, section=?, statement=?,
                       status_code=?, evidence=?, source=?,
                       version=version+1, updated_at=? WHERE id=?""",
                    (book, c.get("section", ""), c.get("claim", ""),
                     c["site_code"], c.get("basis", ""),
                     c.get("source", "status_registry.json"), now(), c["id"]))
                act = ("status-change"
                       if old_code != c["site_code"] else "update")
                changelog(con, "import", "theorems", c["id"], act,
                          f"{old_code} -> {c['site_code']}")
                n_upd += 1
    con.commit()
    codes = con.execute("SELECT COUNT(*) FROM status_codes").fetchone()[0]
    th = con.execute("SELECT COUNT(*) FROM theorems").fetchone()[0]
    print(f"codes={codes} theorems={th} new={n_new} updated={n_upd}")


def cmd_set_status(args):
    con = connect(args.db)
    row = con.execute("SELECT status_code FROM theorems WHERE id=?",
                      (args.id,)).fetchone()
    if row is None:
        sys.exit(f"no theorem {args.id}")
    if con.execute("SELECT 1 FROM status_codes WHERE code=?",
                   (args.code,)).fetchone() is None:
        sys.exit(f"unknown code {args.code}")
    old = row["status_code"]
    con.execute(
        "UPDATE theorems SET status_code=?, evidence=?, version=version+1,"
        " updated_at=? WHERE id=?",
        (args.code, args.evidence or "", now(), args.id))
    changelog(con, args.actor, "theorems", args.id, "status-change",
              f"{old} -> {args.code}: {args.evidence or ''}")
    con.commit()
    print(f"{args.id}: {old} -> {args.code}")


def cmd_add_prose(args):
    con = connect(args.db)
    body = open(args.body_file).read() if args.body_file else args.body
    con.execute(
        """INSERT INTO prose (id, title, page, section, body, audience, status,
                              version, created_at, updated_at)
           VALUES (?,?,?,?,?,?,?,1,?,?)
           ON CONFLICT(id) DO UPDATE SET
             title=excluded.title, page=excluded.page, section=excluded.section,
             body=excluded.body, audience=excluded.audience,
             status=excluded.status, version=prose.version+1,
             updated_at=excluded.updated_at""",
        (args.id, args.title, args.page, args.section, body, args.audience,
         args.status, now(), now()))
    changelog(con, args.actor, "prose", args.id, "update",
              f"status={args.status}")
    con.commit()
    print(f"prose {args.id} ({args.status})")


def cmd_link_prose(args):
    con = connect(args.db)
    con.execute("INSERT OR IGNORE INTO prose_theorems (prose_id, theorem_id)"
                " VALUES (?,?)", (args.prose, args.theorem))
    con.commit()
    print(f"linked {args.prose} -> {args.theorem}")


def cmd_export_feeds(args):
    con = connect(args.db)
    out = args.out
    os.makedirs(out, exist_ok=True)
    feeds = {}
    feeds["status_key"] = {
        r["code"]: {"label": r["label"], "meaning": r["meaning"],
                    "ledger_status": r["ledger_status"]}
        for r in con.execute("SELECT * FROM status_codes ORDER BY code")}
    theorems = [dict(r) for r in con.execute("SELECT * FROM v_theorems")]
    feeds["theorems"] = {"generated": now(), "count": len(theorems),
                         "theorems": theorems}
    books = sorted({t["book"] for t in theorems if t["book"] is not None})
    for b in books:
        bt = [t for t in theorems if t["book"] == b]
        feeds[f"theorems_book{b}"] = {"generated": now(), "book": b,
                                     "count": len(bt), "theorems": bt}
    prose = [dict(r) for r in con.execute(
        "SELECT * FROM v_prose_live ORDER BY page, section")]
    links = {}
    for r in con.execute("SELECT prose_id, theorem_id FROM prose_theorems"):
        links.setdefault(r["prose_id"], []).append(r["theorem_id"])
    for p in prose:
        p["theorems"] = links.get(p["id"], [])
    feeds["prose"] = {"generated": now(), "count": len(prose), "prose": prose}
    chunks = [dict(r) for r in con.execute(
        "SELECT page, chunk_index, body, char_start, char_end, chunker,"
        " chunk_size, chunk_overlap FROM prose_chunks"
        " ORDER BY page, chunk_index")]
    feeds["prose_chunks"] = {"generated": now(), "count": len(chunks),
                             "chunker": "ai.chunking_recursive_character_text_splitter",
                             "chunk_size": 800, "chunk_overlap": 400,
                             "chunks": chunks}
    graphs = [dict(r) for r in con.execute(
        "SELECT id, page, graph_id, fallback_id, fallback_src, fallback_alt,"
        " figure_title, figure_anchor, section, caption, viewport,"
        " expressions, prose_chunk_id FROM desmos_graphs"
        " ORDER BY page, graph_id")]
    for g in graphs:
        g["viewport"] = json.loads(g["viewport"] or "{}")
        g["expressions"] = json.loads(g["expressions"] or "[]")
    feeds["desmos_graphs"] = {"generated": now(), "count": len(graphs),
                              "graphs": graphs}
    for name, payload in feeds.items():
        path = os.path.join(out, f"{name}.json")
        json.dump(payload, open(path, "w"), indent=1, ensure_ascii=False)
    print(f"exported {len(feeds)} feeds to {out}")


def cmd_render_ledger(args):
    """Render the public ledger claim table from the DB (demo of site feed)."""
    con = connect(args.db)
    rows = con.execute(
        "SELECT * FROM v_theorems ORDER BY book, section, id").fetchall()
    lines = ['<table class="claim-table">',
             "<thead><tr><th>ID</th><th>Claim</th><th>Status</th>"
             "<th>Evidence</th></tr></thead>", "<tbody>"]
    for r in rows:
        lines.append(
            f'<tr><td><code data-claim="{r["id"]}">{r["id"]}</code></td>'
            f"<td>{r['statement']}</td>"
            f'<td><span class="tag {r["code"]}" title="{r["code_meaning"]}">'
            f'{r["code"]}</span></td>'
            f"<td>{r['evidence'] or ''}</td></tr>")
    lines += ["</tbody>", "</table>"]
    html = "\n".join(lines)
    if args.out:
        open(args.out, "w").write(html)
        print(f"wrote {args.out} ({len(rows)} claims)")
    else:
        print(html)


def cmd_stats(args):
    con = connect(args.db)
    print("theorems:", con.execute(
        "SELECT COUNT(*) FROM theorems").fetchone()[0])
    print("by code:")
    for r in con.execute(
            "SELECT status_code, COUNT(*) n FROM theorems GROUP BY 1 ORDER BY 2 DESC"):
        print(f"  {r['status_code']}: {r['n']}")
    print("prose:", con.execute("SELECT COUNT(*) FROM prose").fetchone()[0])
    print("prose_theorem links:",
          con.execute("SELECT COUNT(*) FROM prose_theorems").fetchone()[0])


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser(prog="rtheory")
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--actor", default="Muse")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init")
    s.add_argument("--force", action="store_true")

    s = sub.add_parser("import-status-registry")
    s.add_argument("--registry", default=DEFAULT_REGISTRY)

    s = sub.add_parser("set-status")
    s.add_argument("id")
    s.add_argument("code")
    s.add_argument("--evidence", default="")

    s = sub.add_parser("add-prose")
    s.add_argument("--id", required=True)
    s.add_argument("--title", required=True)
    s.add_argument("--page", default="")
    s.add_argument("--section", default="")
    s.add_argument("--body", default="")
    s.add_argument("--body-file", default="")
    s.add_argument("--audience", default="intuition-first")
    s.add_argument("--status", default="draft",
                   choices=["draft", "review", "live"])

    s = sub.add_parser("link-prose")
    s.add_argument("prose")
    s.add_argument("theorem")

    s = sub.add_parser("export-feeds")
    s.add_argument("--out", default=os.path.join(DB_DIR, "feeds"))

    s = sub.add_parser("render-ledger")
    s.add_argument("--out", default="")

    sub.add_parser("stats")

    args = ap.parse_args()
    {"init": cmd_init, "import-status-registry": cmd_import_registry,
     "set-status": cmd_set_status, "add-prose": cmd_add_prose,
     "link-prose": cmd_link_prose, "export-feeds": cmd_export_feeds,
     "render-ledger": cmd_render_ledger,
     "stats": cmd_stats}[args.cmd](args)


if __name__ == "__main__":
    main()
