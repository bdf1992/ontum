#!/usr/bin/env python3
"""commons.py — done-line 0097: the Pattern Commons, DERIVED from the repo's own
common patterns, not authored from a catalog.

bdo's steer (2026-06-17): "derive pattern commons from our common patterns."
This is the term_economy.py / holonsearch-forge grain — a type is *folded from
evidence and graded*, never hand-declared. A candidate pattern names its
**etymon** (the `file:symbol` it recurs at); the fold **resolves** that etymon
against committed bytes and **grades** it: an etymon that resolves grounds the
pattern (mint-eligible), one that does not holds it at `proposed` (the closure
rule — no grounding, no mint). Same refusal term_economy.py and loop/gaps.py
already make. Read-only, stdlib, no network: it reads the repo, it mints nothing
(promotion past `proposed` stays D-4, a human/owner stamp).

Scope: the **grounded subset** (bdo's pick) — the type families that resolve on
disk today: `node` / `site` / `edge` plus the strata `fundamental` / `derived` /
`learned` / `divergence`. The rest of the display-system catalog
(space/glyph/pulse/iteration/anima) is a named hole, not faked here.

The teeth are real, not fabricated: `learned` has no on-disk grounding yet
(display-system C3 hole — "no learned datum is displayed beside its derived
oracle"), so it derives as `proposed` while the others ground. Two locally-fine
things — a declared type family and the bytes — refuse to fit, and the fold says
so without a contrived control.

Usage:
    python causality/commons.py derive            # the derived Commons, to stdout
    python causality/commons.py derive --json      # the raw dataset (machine-readable)
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


# ── the candidate patterns: where each common pattern RECURS (its etymon) and
#    the required fields a generator must emit for it (from the contract + the
#    display-system type table). The candidates are declared; their grounding is
#    FOLDED from bytes — nothing here is minted by being listed.
def _candidates(repo):
    """Each candidate: id, type, the required fields, and an etymon to resolve
    (file + a `contains` substring that proves the pattern lives there). The
    node candidates are themselves derived from canvas.js's SCHEMA — the engine's
    own per-type patterns — so the Commons is mined from the code, not invented."""
    cands = []

    # node:<kind> — one pattern per node kind the engine already carries. Derived
    # by reading the SCHEMA keys out of canvas.js (the common pattern made data).
    node_fields = ["id", "type", "label", "config", "sites", "space",
                   "strata", "divergence"]
    for kind in _schema_kinds(repo):
        cands.append({
            "id": f"node:{kind}", "type": "node", "kind": kind,
            "required": node_fields,
            "etymon": {"file": "causality/canvas.js", "contains": f"{kind}:"},
        })

    # edge — the typed connection (sync wire). Recurs in the canvas EDGE_SCHEMA
    # and the evidence-edge contract schema.
    cands.append({
        "id": "edge", "type": "edge",
        "required": ["from", "to", "kind", "sign", "port_compat", "stratum"],
        "etymon": {"file": "causality/canvas.js", "contains": "EDGE_SCHEMA"},
    })

    # site — a place a node lives. Recurs as the SiteNode contract family.
    cands.append({
        "id": "site", "type": "site",
        "required": ["id", "address", "stratum", "resolved"],
        "etymon": {"file": "causality/contracts/projection-api.md",
                   "contains": "SiteNode"},
    })

    # the three strata + the comparator (display-system planes 1) — grounded
    # where each stratum's data actually lives.
    cands.append({
        "id": "fundamental", "type": "fundamental",
        "required": ["address", "hash", "append_only"],
        "etymon": {"file": ".ai-native/log/events.jsonl", "contains": ""},
    })
    cands.append({
        "id": "derived", "type": "derived",
        "required": ["fold", "inputs", "determinism"],
        "etymon": {"file": "causality/term_economy.py", "contains": "def classify"},
    })
    cands.append({
        # learned — the model's reach. display-system C3 names the hole: no
        # learned datum is displayed beside its derived oracle yet. So its etymon
        # points at the surface that would carry it, and it does NOT resolve —
        # the pattern stays proposed. This is the real tooth, not a contrivance.
        "id": "learned", "type": "learned",
        "required": ["model", "input", "oracle_ref", "divergence"],
        "etymon": {"file": "causality/learned_oracle.py", "contains": "oracle"},
    })
    cands.append({
        "id": "divergence", "type": "divergence",
        "required": ["strata", "metric", "verdict"],
        "etymon": {"file": "causality/term_economy.py", "contains": "def classify"},
    })
    return cands


def _schema_kinds(repo):
    """Derive the node kinds from canvas.js's SCHEMA block — the engine's own
    common patterns, read as data (no JS eval; a tolerant line scan)."""
    path = repo / "causality" / "canvas.js"
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    m = re.search(r"const SCHEMA = \{(.*?)\n\};", text, re.S)
    if not m:
        return []
    kinds = []
    for line in m.group(1).splitlines():
        km = re.match(r"\s*([a-z][a-z0-9]*)\s*:\s*\[", line)
        if km:
            kinds.append(km.group(1))
    return kinds


def _resolve(etymon, repo):
    """Resolve an etymon against committed bytes: the file must exist and (when a
    `contains` is named) the substring must be present. The bytes win — a
    candidate cannot ground itself by assertion (the term_economy rule)."""
    f = repo / etymon["file"]
    if not f.is_file():
        return False, f"no file at {etymon['file']}"
    needle = etymon.get("contains", "")
    if needle and needle not in f.read_text(encoding="utf-8", errors="replace"):
        return False, f"`{needle}` not found in {etymon['file']}"
    return True, f"{etymon['file']}" + (f" :: {needle}" if needle else "")


def derive(repo=REPO):
    """The fold: resolve every candidate's etymon, grade it, return the Commons.
    A grounded pattern is `minted-eligible` (it CAN be admitted — the stamp is
    still bdo's, D-4); an unresolved one is held `proposed`; a named etymon whose
    file is wholly absent surfaces `ghost`."""
    patterns = []
    for c in _candidates(repo):
        ok, why = _resolve(c["etymon"], repo)
        f_present = (repo / c["etymon"]["file"]).is_file()
        if ok:
            grade = "minted-eligible"
        elif not f_present:
            grade = "ghost"          # claims a backing that does not resolve at all
        else:
            grade = "proposed"       # the surface exists but the pattern is not on it yet
        patterns.append({
            "id": c["id"], "type": c["type"], "kind": c.get("kind"),
            "required": c["required"], "etymon": c["etymon"],
            "grounded": ok, "grade": grade, "why": why,
        })
    grounded = [p for p in patterns if p["grounded"]]
    return {
        "commons": "ontum.pattern-commons.grounded-subset",
        "derived_from": "the repo's common patterns (canvas SCHEMA, the "
                        "projection-api contract, term_economy, the log)",
        "subset": ["node", "site", "edge", "fundamental", "derived",
                   "learned", "divergence"],
        "pattern_count": len(patterns),
        "grounded_count": len(grounded),
        "grade_summary": _tally(p["grade"] for p in patterns),
        "patterns": patterns,
    }


def _tally(values):
    out = {}
    for v in values:
        out[v] = out.get(v, 0) + 1
    return dict(sorted(out.items()))


def render(result):
    lines = [f"Pattern Commons — {result['commons']}",
             f"  derived from: {result['derived_from']}",
             f"  {result['grounded_count']}/{result['pattern_count']} grounded "
             f"· {result['grade_summary']}"]
    for p in result["patterns"]:
        mark = "✓" if p["grounded"] else "·"
        lines.append(f"  {mark} {p['id']:<14} [{p['grade']}] {p['why']}")
    return "\n".join(lines)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    verb = argv[0] if argv else "derive"
    as_json = "--json" in argv
    if verb != "derive":
        print(f"result: needs-you — unknown verb {verb!r}; try `derive`")
        return 2
    result = derive()
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(render(result))
    print(f"result: done — {result['grounded_count']}/{result['pattern_count']} "
          f"patterns grounded (the rest held proposed/ghost; minting is bdo's, D-4)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
