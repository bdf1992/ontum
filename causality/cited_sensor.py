#!/usr/bin/env python3
"""The cited sensor (done-line 0086): the data->evidence half of the
digital-experience fold.

bdo, 2026-06-15: "the information ALREADY exists on my computer; if you just
infer over it … you can generate a knowledge graph." This is the sensor at the
bottom of that fold. It reads a person's data surface (a directory of files)
**read-only** and emits **cited** evidence — each record carrying a resolvable
citation back to the bytes it came from.

The teeth are not new (§10): the loop's fold over its own log is
byte-deterministic, but a fold over a raw machine is *inference*, so the thing
that keeps it honest is the citation discipline `causality/term_economy.py`
already enforces — `resolve_evidence` is **reused, not rebuilt**. A citation
that points at nothing (a missing path, or a content anchor absent from the
bytes) is a `ghost`, refused at the door: no resolvable evidence, no node. The
inference that sits *above* this sensor may be fuzzy; the citation underneath it
may not.

Pure stdlib + the reused resolver. Read-only: it opens files to read, never to
write, and emits records — it mints nothing.
"""

import argparse
from pathlib import Path

from causality.term_economy import resolve_evidence

STRATUM = "file"           # the evidence stratum this sensor speaks
_ANCHOR_LEN = 80           # a content anchor is a short, stable substring


def _anchor(path):
    """A content anchor: the first non-empty decoded line (<= _ANCHOR_LEN chars)
    of the file, or None for an empty file. The anchor is the citation's
    proof-of-reality — resolution checks it is really in the bytes, so a
    fabricated anchor is caught as a ghost. Citing existence alone (anchor None)
    is honest for an empty file: it claims the path, not any content."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    for line in text.splitlines():
        s = line.strip()
        if s:
            return s[:_ANCHOR_LEN]
    return None


def scan(data_root):
    """Read-only walk of a person's data surface. Emits one cited evidence
    record per file — its path (relative to data_root), kind (suffix), size in
    bytes, and a content anchor (or None) — in deterministic path order. Writes
    nothing; opens files only to read their anchor."""
    root = Path(data_root)
    out = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        try:
            size = p.stat().st_size
        except OSError:
            continue
        out.append({
            "file": p.relative_to(root).as_posix(),
            "stratum": STRATUM,
            "kind": (p.suffix[1:].lower() or "none"),
            "size": size,
            "contains": _anchor(p),
        })
    return out


def is_ghost(data_root, ev):
    """True if the citation does not resolve against the bytes — the path points
    at nothing, or a claimed content anchor is absent from the file. The reused
    `term_economy` discipline made the sensor's door: no resolvable evidence,
    no node."""
    r = resolve_evidence(Path(data_root), ev)
    if not r["file_exists"]:
        return True
    if ev.get("contains") is not None and not r["resolved"]:
        return True
    return False


def cited(data_root, records=None):
    """The honest evidence: every record whose citation resolves. This is the
    door a ghost never passes. Scans the surface when given no records."""
    records = scan(data_root) if records is None else records
    return [ev for ev in records if not is_ghost(data_root, ev)]


def ghosts(data_root, records):
    """The records refused at the door — named, never silently dropped (absence
    is information)."""
    return [ev for ev in records if is_ghost(data_root, ev)]


def operate(data_root, *, mark_root, records=None):
    """Resolve evidence against `data_root`, and each refused ghost leaves a mark
    (done-line 0092): a citation that pointed at nothing becomes a recorded
    signal the harvest can farm. `records` defaults to a fresh honest scan (which
    yields no ghosts); pass claimed evidence to resolve it — ghosts arise from
    *claims*, not from the sensor's own scan. `mark_root` is the records root
    (`.ai-native`), distinct from the scanned `data_root`. The pure scan/resolve
    functions are untouched; this seam is the only writer. Returns (cited,
    ghosts)."""
    records = scan(data_root) if records is None else records
    good, bad = cited(data_root, records), ghosts(data_root, records)
    if bad:
        from loop import signals
        for ev in bad:
            signals.mark(mark_root, "cited-ghost", ev.get("file", "?"),
                         "citation does not resolve to committed bytes")
    return good, bad


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("data_root", help="the data surface to sense (read-only)")
    ap.add_argument("--mark-root", type=Path, default=Path(".ai-native"),
                    help="records root for ghost signals (default .ai-native)")
    args = ap.parse_args(argv)
    records = scan(args.data_root)
    good, bad = operate(args.data_root, mark_root=args.mark_root)
    for ev in good:
        print(f"  cited: {ev['file']} [{ev['kind']}, {ev['size']}B]")
    for ev in bad:
        print(f"  ghost (refused): {ev['file']}")
    print(f"result: report — scanned {len(records)} file(s) under "
          f"{args.data_root}: {len(good)} cited, {len(bad)} ghost(s) refused")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
