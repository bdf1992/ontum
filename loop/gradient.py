#!/usr/bin/env python3
"""The speed-gradient fold (done-line 0182, epic.graded-speed): the loop
reading its own acts as one graded gradient of *speed* — the meta-level an
act reaches, not its latency.

bdo, 2026-06-21: *"multiple speeds … a gradient, not binary: the thresholds
are binary, the state is graded."* The doctrine already holds the binary
(§14, D-12: the fast loop holds the setpoint, the slow loop moves it). This
fold extends that binary into a **three-band graded reading** off the shared
log — it builds no new control loop (that would double-build §14;
`graded-speed.proposal.md`), it *reads* the acts the existing organs already
write and names the band each sits in.

Bands are named by **act-verb**, carrying fast/medium/slow only as the
gradient label — the naming reconciliation the double-build check forced:
bdo's "medium" (retune config) is the doctrine's "slow loop", so naming bands
by speed would drift two vocabularies.

  respond  (fast)   — use the loop / respond to pressure: every atom event,
                      every pipeline verdict receipt, every `tick`. The fast
                      ambient act (loop/orchestrate.py).
  retune   (medium) — move a dial the loop reads next pass: `setpoint` and
                      `auto_admit_fence` admissions (loop/slowloop.py proposes,
                      loop/disposer.py disposes in-fence).
  author   (slow)   — add machinery read at runtime: `workflow_armed`,
                      `node_real`, `surface`, `herald_introduction`, `tag`
                      admissions. The highest-leverage, least-governed band —
                      it authors what every fast act then runs.

A record whose type this fold does not yet place is counted **unbanded**, not
forced into a band (absence is information).

The §10 tooth — **untraced-band-crossing**: the `author` band is a
disconnected island today (the SPEED-BANDS grounding). A workflow under
`.claude/workflows/*.js` is authored machinery; if its *current bytes* carry
no enabled `workflow_armed` admission, that slow act is not on the ledger —
the fast-norm-administrator cannot ingress it "all down the line". The tooth
flags it, composing `review.is_armed`'s bytes-binding (no second arming
definition, I-4 — `tests/test_gradient.py` cross-checks against a real arm).

Read-only, propose-only (D-4): it names the band and the one move; it moves
and judges nothing. Stdlib only. CLI ends `done | report` (D-6).
"""

import argparse
import hashlib
import sys
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT, Fold

# Band table: (band verb, speed label, level, admission types that sit here).
# `respond` additionally claims every event and every receipt (handled below),
# not only the `tick` admission — the fast act is the whole pipeline exercise.
BANDS = (
    ("respond", "fast", 0, frozenset({"tick"})),
    ("retune", "medium", 1, frozenset({"setpoint", "auto_admit_fence"})),
    ("author", "slow", 2, frozenset(
        {"workflow_armed", "node_real", "surface", "herald_introduction", "tag"})),
)
_ADM_BAND = {t: verb for verb, _s, _l, types in BANDS for t in types}
_SPEED = {verb: speed for verb, speed, _l, _types in BANDS}
_LEVEL = {verb: level for verb, _s, level, _types in BANDS}

ARMED = "workflow_armed"  # the author-band trace review.py writes


def _hash_bytes(raw):
    """The version hash of a workflow file's bytes. MUST match
    review._hash_bytes (I-4): sha256 over the RAW bytes (never read_text —
    universal-newline translation would diverge; the 0007 CRLF trap), with the
    "sha256:" prefix. tests/test_gradient.py arms a real workflow and asserts
    this fold reads it traced, so any drift from review's formula fails."""
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _armed_versions(fold):
    """Fold the log for arm acts: {(workflow, version_hash): enabled}, latest
    wins (a disarm supersedes an arm). Reads the same `workflow_armed` records
    review.py writes — a log fact, not a second arm path (the heal/digest
    pattern: a fold reads verdicts it never wrote)."""
    out = {}
    for adm in fold.admissions:
        if adm.get("type") == ARMED:
            out[(adm.get("workflow"), adm.get("version_hash"))] = adm.get("enabled", True)
    return out


def profile(root):
    """The band profile: per-band count + the record kinds seen there, plus the
    honest unbanded count. A pure read of the three log files."""
    if not (Path(root) / "log").is_dir():
        return None  # no records, no loop: absence, not a false zero-gradient
    fold = Fold(root)
    counts = {verb: 0 for verb, *_ in BANDS}
    kinds = {verb: set() for verb, *_ in BANDS}
    unbanded = 0
    unbanded_kinds = set()

    # respond claims every event and every receipt — the fast pipeline exercise.
    counts["respond"] += len(fold.events) + len(fold.receipts)
    if fold.events:
        kinds["respond"].add("event")
    if fold.receipts:
        kinds["respond"].add("receipt")

    for adm in fold.admissions:
        t = adm.get("type")
        verb = _ADM_BAND.get(t)
        if verb is None:
            unbanded += 1
            unbanded_kinds.add(t or "?")
        else:
            counts[verb] += 1
            kinds[verb].add(t)

    bands = {
        verb: {
            "speed": _SPEED[verb],
            "level": _LEVEL[verb],
            "count": counts[verb],
            "kinds": sorted(kinds[verb]),
        }
        for verb, *_ in BANDS
    }
    return {
        "bands": bands,
        "unbanded": {"count": unbanded, "kinds": sorted(unbanded_kinds)},
    }


def untraced_band_crossings(root):
    """The §10 tooth: authored machinery (`.claude/workflows/*.js`) whose current
    bytes carry no enabled arm admission — a slow act the ledger cannot see.
    Each finding carries kind · subject · why · the one move (gaps grain)."""
    if not (Path(root) / "log").is_dir():
        return []
    repo = Path(root).resolve().parent
    wf_dir = repo / ".claude" / "workflows"
    if not wf_dir.is_dir():
        return []
    armed = _armed_versions(Fold(root))
    armed_slugs = {slug for (slug, _vh), on in armed.items() if on}
    out = []
    for js in sorted(wf_dir.glob("*.js")):
        slug = js.stem
        vh = _hash_bytes(js.read_bytes())
        if armed.get((slug, vh)):
            continue  # traced: current bytes are armed
        stale = slug in armed_slugs  # armed once, at other bytes
        why = ("authored, armed at earlier bytes then edited — the current bytes "
               "carry no enabled arm (stale arm)" if stale else
               "authored machinery with no arm admission — a slow act the ledger "
               "cannot see")
        out.append({
            "kind": "untraced-band-crossing",
            "subject": f".claude/workflows/{slug}.js",
            "band": "author",
            "why": why,
            "move": "review and arm its current bytes: python "
                    f".claude/skills/review-workflow/review.py arm "
                    f".claude/workflows/{slug}.js --by <you>",
        })
    return out


def gradient(root):
    """The whole read: the band profile + the untraced-band-crossing findings."""
    prof = profile(root)
    if prof is None:
        return None
    crossings = untraced_band_crossings(root)
    p = prof["bands"]
    summary = (
        f"respond/fast {p['respond']['count']} · retune/medium {p['retune']['count']} "
        f"· author/slow {p['author']['count']} (unbanded {prof['unbanded']['count']}); "
        f"{len(crossings)} untraced author-band crossing(s)")
    return {
        "bands": prof["bands"],
        "profile": {
            "fast": p["respond"]["count"],
            "medium": p["retune"]["count"],
            "slow": p["author"]["count"],
            "unbanded": prof["unbanded"]["count"],
        },
        "crossings": crossings,
        "summary": summary,
    }


def render(data):
    for verb, *_ in BANDS:
        b = data["bands"][verb]
        kinds = ", ".join(b["kinds"]) or "—"
        print(f"band: {verb} ({b['speed']}, level {b['level']}) — "
              f"{b['count']} act(s) [{kinds}]")
    ub = data["profile"]["unbanded"]
    if ub:
        print(f"unbanded: {ub} record(s) — types this fold does not yet place")
    for c in data["crossings"]:
        print(f"crossing: {c['kind']} — {c['subject']} (band {c['band']})")
        print(f"  why: {c['why']}")
        print(f"  move: {c['move']}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=Path(DEFAULT_ROOT))
    ap.add_argument("--json", action="store_true", help="emit the raw dataset")
    args = ap.parse_args(argv)

    data = gradient(args.root)
    if data is None:
        print("result: report — no log on this root; no gradient to read")
        return 0
    if args.json:
        import json
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    render(data)
    n = len(data["crossings"])
    if n:
        print(f"result: report — {n} untraced author-band crossing(s); the "
              "author band is not yet on the ledger all down the line")
    else:
        print("result: done — every authored crossing is traced on the ledger")
    return 0


if __name__ == "__main__":
    sys.exit(main())
