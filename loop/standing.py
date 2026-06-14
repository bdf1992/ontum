#!/usr/bin/env python3
"""The standing-surface projection (done-line 0071): a registered surface's
open work, ambient at every wake — the inbound twin of `reflect.py`.

`reflect.py` is the *outbound* projection: the log mirrored onto a surface
(drift, log -> surface). This module is its inbound mirror: a registered
surface's open items projected *into* the session (surface -> session). Same
pub/sub grammar, opposite direction, the *same* registered-surface seam
(`reflect.registered_surfaces`) — so GitHub is never the thing this knows, it
is merely the one surface kind that has an adapter today.

The split that keeps it from being glued to GitHub (bdo, 2026-06-14):

  - **this module is pure** (stdlib, no network, no subprocess): it folds a
    *normalized snapshot* — a list of items `{kind, number, title, ref, ...}`
    naming no vendor — into (a) the standing picture and (b) the delta against
    a per-session baseline. It could project a phone inbox or a local file with
    no change.
  - **the adapter lives in the hook layer** (`.claude/hooks/standing_surface.py`),
    where the network reach is allowed, keyed by surface kind — a registered
    surface with no adapter is named, never guessed (reflect's `SURFACE_KINDS`
    discipline). The baseline + throttle (wall-clock state) live there too;
    this module never reads a clock and never holds state across calls.

Pub/sub, level-triggered: the surface is the topic, the session is the
subscriber, the wake (SessionStart / UserPromptSubmit) is the heartbeat, the
standing picture is the projection, the delta is the unconsumed change. No
broker, no daemon, no poll louder than its throttle.

Stdlib only. CLI ends with a clear result on stdout (D-6): done | report.
"""

import argparse
import json
import sys
from pathlib import Path

# A normalized item names no vendor: kind is a generic bucket the projection
# groups by; number/title/ref are the cold-reader fields. An adapter fills
# these from whatever surface it speaks (github-issues fills issue/pr today).
KIND_PLURALS = {"issue": "issues", "pr": "PRs"}


def kind_label(kind, n):
    """'1 issue' / '8 PRs' — pluralized for the known kinds, generic otherwise
    (an unknown kind reads as 'N <kind>(s)', never crashes the picture)."""
    plural = KIND_PLURALS.get(kind, f"{kind}s")
    return f"{n} {kind if n == 1 else plural}"


def item_id(item):
    """The stable identity of one open item across polls — `<kind>#<number>`.
    Two snapshots agree on an item iff they agree on this, so the delta is a
    pure set difference over ids (the title changing is not a new item)."""
    return f"{item.get('kind', '?')}#{item.get('number', '?')}"


def snapshot_ids(items):
    """The id set of a snapshot, sorted — the baseline a session remembers."""
    return sorted({item_id(it) for it in items})


def _one_line(item):
    """A cold-reader line for one open item: id, title, and (for a PR) its
    branch — enough to know what it is without opening it."""
    title = (item.get("title") or "").strip()
    if len(title) > 90:
        title = title[:87] + "…"
    ref = item.get("branch")
    tail = f"  ({ref})" if ref else ""
    return f"  {item.get('kind', '?')} #{item.get('number', '?')} — {title}{tail}"


def _counts_phrase(items):
    """'1 issue, 8 PRs' — the kinds present, in a stable order, pluralized."""
    counts = {}
    for it in items:
        counts[it.get("kind", "?")] = counts.get(it.get("kind", "?"), 0) + 1
    return ", ".join(kind_label(k, counts[k]) for k in sorted(counts))


def format_standing(surface_id, items):
    """The full standing picture for one surface — what a session is handed at
    wake. Pure. Empty open set returns a single quiet line (awareness, not
    silence: 'nothing open' is information at SessionStart)."""
    if not items:
        return f"[standing] {surface_id} — no open work"
    lines = [f"[standing] {surface_id} — {_counts_phrase(items)} open:"]
    # group by kind, stable order, items by descending number (newest first)
    by_kind = {}
    for it in items:
        by_kind.setdefault(it.get("kind", "?"), []).append(it)
    for kind in sorted(by_kind):
        for it in sorted(by_kind[kind],
                         key=lambda i: i.get("number", 0), reverse=True):
            lines.append(_one_line(it))
    return "\n".join(lines)


def compute_delta(baseline_ids, items):
    """The level-triggered change: items whose id is not in the baseline are
    `added`; baseline ids absent from the snapshot are `removed`. Pure — no
    clock, no state. Unchanged set -> both empty (the caller stays silent)."""
    baseline = set(baseline_ids or [])
    current = {item_id(it): it for it in items}
    added = [it for iid, it in current.items() if iid not in baseline]
    removed = sorted(baseline - set(current))
    return {"added": added, "removed": removed}


def delta_is_empty(delta):
    return not delta.get("added") and not delta.get("removed")


def format_delta(surface_id, delta):
    """The tick-up line for a change — printed once, never the whole list
    (that is the anti-spam contract). '' when nothing changed, so the hook
    prints nothing on an unchanged poll."""
    if delta_is_empty(delta):
        return ""
    added, removed = delta.get("added", []), delta.get("removed", [])
    head = f"[standing] {surface_id} changed: +{len(added)} / -{len(removed)}"
    lines = [head]
    for it in sorted(added, key=lambda i: i.get("number", 0), reverse=True):
        lines.append("  + " + _one_line(it).lstrip())
    for iid in removed:
        lines.append(f"  - {iid} closed")
    return "\n".join(lines)


def _load_snapshot(path):
    """Read a normalized snapshot (a JSON list of items) from a file or '-'
    (stdin) — the CLI's input, since this pure module never reaches a network.
    The adapter that builds one from a live surface lives in the hook."""
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    data = json.loads(text)
    if not isinstance(data, list):
        raise ValueError("a snapshot is a JSON list of normalized items")
    return data


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--surface", default="surface",
                    help="surface id for the header (default: 'surface')")
    ap.add_argument("--snapshot", default="-",
                    help="path to a normalized snapshot JSON, or '-' for stdin")
    ap.add_argument("--baseline", default=None,
                    help="path to a baseline-ids JSON list; given, prints the "
                         "delta instead of the full picture")
    args = ap.parse_args(argv)
    try:
        items = _load_snapshot(args.snapshot)
    except (OSError, ValueError) as e:
        print(f"result: needs-you — could not read snapshot: {e}")
        return 2
    if args.baseline is not None:
        try:
            baseline = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            print(f"result: needs-you — could not read baseline: {e}")
            return 2
        text = format_delta(args.surface, compute_delta(baseline, items))
        print(text or f"result: done — {args.surface} unchanged, no tick-up")
        return 0
    print(format_standing(args.surface, items))
    print(f"result: report — {len(items)} open item(s) on {args.surface}")
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
