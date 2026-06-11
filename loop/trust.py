#!/usr/bin/env python3
"""The trust ladder (atom.trust-ladder.v0 — epic.experience-layer, wave 1).

Capability rungs as admitted records (I-8): what each class of agent may do
in this system. A rung is a `trust_rung` admission signed --by bdo, read here
as a pure fold over the log; nothing grants itself a rung (D-4), and trust
accrues as receipts against rungs, not as assertions in prose.

Rungs are written through the one pen (`loop.node admit-rung`) and read here.
The top capability, `ontum-touch` (authoring or mutating fabric units), is
LOCKED: no admission grants it, the pen refuses to write one, and bdo's trust
boundary is the standing reason it stays closed —

    "the capabilities that would let an agent touch ontum are NOT met — one
     ontum on disk needs the topos, the glyphs, and the language under it, so
     fabric-touch is out of this epic's remit"
    — bdo's boundary, recorded in epic.experience-layer (2026-06-10)

Unlocking ontum-touch is a deliberate change to the pen by bdo, never a flag a
session can pass. Stdlib only; reads the log, writes nothing. result: report.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT

# The classes of agent the system can summon — the program is the place, the
# mind is a pluggable admitted backing (the morphic-agent reading, D-9/D-10).
AGENT_CLASSES = {
    "summoned-session": "a mortal Claude session blinked into a place (D-10)",
    "branded-subagent": "a spawned subagent — prompt-pinned, receipted (wave 2)",
    "local-model": "a registered local model backing — the privileged default",
    "external-mind": "a registered external family (GPT, …) — receipted exception",
    "deterministic-rule": "code whose verdict is law, not inference (e.g. placement)",
}

# The ladder, lowest rung to highest. Cumulative: a granted rung covers every
# capability at or below it. ontum-touch is the locked top.
CAPABILITIES = ["read", "judge", "author", "ontum-touch"]
LOCKED = "ontum-touch"
GRANTOR = "bdo"  # rungs are bdo's to grant — no one signs their own line (D-4)

ONTUM_TOUCH_BOUNDARY = (
    "the capabilities that would let an agent touch ontum are NOT met — one "
    "ontum on disk needs the topos, the glyphs, and the language under it, so "
    "fabric-touch is out of this epic's remit"
)


def _admissions(root):
    """Every admission line, torn-tail tolerant (a half-written line is
    dropped and re-derived next pass — the log-is-truth property)."""
    path = Path(root) / "log" / "admissions.jsonl"
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def active_rungs(root=DEFAULT_ROOT):
    """The fold: {agent_class: highest capability granted}, after dropping any
    rung a later admission supersedes (history is superseded, never erased)."""
    adms = _admissions(root)
    superseded = {a["supersedes"] for a in adms if a.get("supersedes")}
    granted = {}
    for a in adms:
        if a.get("type") != "trust_rung" or a.get("id") in superseded:
            continue
        cls, cap = a.get("agent_class"), a.get("capability")
        if cls not in AGENT_CLASSES or cap not in CAPABILITIES:
            continue
        if cls not in granted or CAPABILITIES.index(cap) > CAPABILITIES.index(granted[cls]):
            granted[cls] = cap
    return granted


def permits(agent_class, capability, root=DEFAULT_ROOT):
    """May this class do this act? The ladder is cumulative; ontum-touch is
    never granted (LOCKED), so it is denied for every class until bdo unlocks
    the pen itself."""
    if capability not in CAPABILITIES:
        return False
    held = active_rungs(root).get(agent_class)
    if held is None:
        return False
    return CAPABILITIES.index(capability) <= CAPABILITIES.index(held)


def rung_refusal(agent_class, capability, by):
    """Why a trust_rung may NOT be admitted, or None. Pure over its inputs, so
    the suite hits it without writing the log (the placement/pr pattern)."""
    if agent_class not in AGENT_CLASSES:
        return f"unknown agent class {agent_class!r}; classes: " + ", ".join(AGENT_CLASSES)
    if capability not in CAPABILITIES:
        return f"unknown capability {capability!r}; the ladder is " + " < ".join(CAPABILITIES)
    if capability == LOCKED:
        return (f"{LOCKED} is LOCKED — no rung grants it. bdo's boundary: "
                f"\"{ONTUM_TOUCH_BOUNDARY}\". Unlocking it is a deliberate change "
                "to this pen, never a grant a session can pass (D-4)")
    if (by or "").strip().lower() != GRANTOR:
        return (f"rungs are {GRANTOR}'s to grant — --by must be {GRANTOR} "
                "(nothing grants itself a rung; no one signs their own line)")
    return None


# ----------------------------------------------------------------- read CLI

def ladder_lines(root):
    granted = active_rungs(root)
    lines = ["the trust ladder — capabilities low to high: " + " < ".join(CAPABILITIES),
             f"  ({LOCKED} is LOCKED for every class; bdo's boundary stands)"]
    for cls, desc in AGENT_CLASSES.items():
        held = granted.get(cls)
        state = f"holds up to '{held}'" if held else "no rung admitted — denied everything"
        lines.append(f"  {cls}: {state}  — {desc}")
    return lines


def cmd_ladder(ns):
    for line in ladder_lines(ns.root):
        print(line)
    print(f"result: report — {len(active_rungs(ns.root))} class(es) hold a rung; "
          f"{LOCKED} LOCKED")
    return 0


def cmd_permits(ns):
    ok = permits(ns.agent_class, ns.capability, ns.root)
    locked = ns.capability == LOCKED and not ok
    print(f"result: report — {ns.agent_class} {'MAY' if ok else 'may NOT'} "
          f"{ns.capability}" + (" (LOCKED)" if locked else ""))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    la = sub.add_parser("ladder", help="show every class and the rung it holds (read-only)")
    la.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    la.set_defaults(func=cmd_ladder)
    pe = sub.add_parser("permits", help="ask whether a class may do a capability")
    pe.add_argument("agent_class")
    pe.add_argument("capability")
    pe.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    pe.set_defaults(func=cmd_permits)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
