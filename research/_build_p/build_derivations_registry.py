#!/usr/bin/env python3
"""Build derivations_registry.json: claim id -> appendix anchor mapping.

Claims (Books 2-6) -> P-7-<claim-id> anchors in appendix-proofs/.
New research results -> their P-1..P-6 anchors.
Run after assemble.py; sync_status.py reads this to add 'derivation'
links to the ledger claim tables and book audit tables.
Idempotent: deterministic output.
"""
import json
import os
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RESULTS = {
    # P-1 Casimir
    **{f"casimir-k{i}": f"P-1-k{i}" for i in range(1, 10)},
    "casimir-weyl": "P-1-weyl",
    "casimir-twist-b7": "P-1-twist",
    # P-2 campaign
    "campaign-collapse": "P-2-collapse",
    "campaign-reality": "P-2-reality",
    "campaign-crossphase": "P-2-crossphase",
    "campaign-752": "P-2-752",
    "campaign-commutant": "P-2-commutant",
    "campaign-decoupling": "P-2-decoupling",
    "campaign-sawfirewall": "P-2-sawfirewall",
    "campaign-w4c2a": "P-2-w4c2a",
    "campaign-epsinvis": "P-2-epsinvis",
    "campaign-census": "P-2-census",
    # P-3 dials
    "dial-t1": "P-3-t1",
    "dial-t3": "P-3-t3",
    "dial-t4": "P-3-t4",
    "dial-crossratio": "P-3-crossratio",
    "cal-p6": "P-3-calp6",
    # P-4 modules
    **{f"modules-m{i}": f"P-4-m{i}" for i in range(7, 13)},
    "modules-naive12": "P-4-naive12",
    # P-5 refutations
    "refute-run25": "P-5-run25",
    "refute-commutant-bug": "P-5-commutant-bug",
    "refute-modepure": "P-5-modepure",
    "refute-w4c4": "P-5-w4c4",
    # P-6 standalone
    "thm-secant": "P-6-secant",
    "thm-l9": "P-6-l9",
}

reg = json.load(open(os.path.join(ROOT, "status_registry.json")))
claims = {c["id"]: f"P-7-{c['id']}" for c in reg["claims"]}

out = {
    "meta": {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "note": ("Claim id -> appendix-proofs anchor. 'claims' covers the "
                 "status_registry.json claims (Books 2-6 audit); 'results' "
                 "covers the new research results (P-1..P-6). "
                 "sync_status.py reads this to add derivation links to the "
                 "ledger claim tables and book audit tables."),
    },
    "claims": claims,
    "results": RESULTS,
}
path = os.path.join(ROOT, "derivations_registry.json")
with open(path, "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=1, ensure_ascii=False)
    fh.write("\n")
print(f"wrote {path}: {len(claims)} claims + {len(RESULTS)} results")
