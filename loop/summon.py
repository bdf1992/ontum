#!/usr/bin/env python3
"""The summons surface (D-10, §8): who is summoned right now, as a pure fold.

Every report since 0005 names the gap: summoning is hand-routed. An atom
parks awaiting an admitted-real node and nothing fires — a human notices,
starts a session, pastes context. This module is the wire: it renders the
open summons from the log (read-only, I-3) so the harness can inject them
into any session that blinks in here. The session is the virtual node — it
reads its summons, judges through the one pen (loop.node judge), and
dissolves. This surface never judges, never writes, and never stands in
for the summoned node (D-2). The owner's stamp queue is deliberately not
here: that is the inbox (D-4), not a session's summons.

Two mouths, one fold:
- CLI:  python -m loop.summon          human-readable open summons
- hook: python -m loop.summon --hook   Claude Code hook mode (§8: hooks
  are how summoned nodes fire). Reads the hook JSON from stdin, prints
  the briefing to stdout (Claude Code adds hook stdout to the session's
  context on SessionStart and UserPromptSubmit), and always exits 0 — a
  broken hook must never block the owner's prompt.

Stdlib only. CLI ends with a clear result on stdout (D-6): done | report.
"""

import argparse
import json
import os
import sys
from pathlib import Path

from loop.reconcile import (DEFAULT_ROOT, PIPELINE, Fold, load_atoms,
                            real_nodes, receipt_for_stage)
from loop.orchestrate import HUMAN_NODE, next_action


def open_summons(root):
    """The fold: every (atom, node, stage) awaiting an admitted-real node
    other than the owner's stamp. Same walk judge() takes — the first
    announced-but-unsatisfied stage is the one open for judgement."""
    fold = Fold(root)
    real_map = real_nodes(fold)
    human = real_map.get(HUMAN_NODE)
    out = []
    for atom, ahash in load_atoms(root):
        action = next_action(fold, atom, ahash, real_map)
        if action is None:
            continue
        kind, target = action
        if kind != "await" or target == human:
            continue
        for stage in PIPELINE:
            ev = fold.event(stage["event"], ahash)
            if ev is None:
                break
            if receipt_for_stage(fold, stage, ahash, real_map) is None:
                out.append({"atom": atom, "artifact_hash": ahash,
                            "node": target, "stage": stage})
                break
    return out


def briefing(s):
    atom, stage = s["atom"], s["stage"]
    return "\n".join([
        f"summons: {s['node']} — {atom['id']} awaits your verdict at seam {stage['seam']}",
        f"  story: {atom['story']['text']}",
        f"  verdicts: {' | '.join(stage['terminal_expected'])}",
        f"  judge: python -m loop.node judge --atom {atom['id']} --node {s['node']}"
        f" --verdict <verdict> --reason \"<why>\"",
        "  contract: judge this one event only; never an event you announced"
        " (D-2); the receipt is your only pen (I-2).",
    ])


def resolve_root(arg_root):
    """Hooks run wherever the harness runs them; the project dir is the
    anchor when given (CLAUDE_PROJECT_DIR), the CWD default otherwise."""
    if arg_root is not None:
        return arg_root
    project = os.environ.get("CLAUDE_PROJECT_DIR")
    if project:
        return Path(project) / DEFAULT_ROOT
    return DEFAULT_ROOT


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=None)
    ap.add_argument("--hook", action="store_true",
                    help="Claude Code hook mode: JSON on stdin, briefing on stdout, exit 0 always")
    args = ap.parse_args(argv)
    root = resolve_root(args.root)

    if args.hook:
        try:
            sys.stdin.read()  # the hook payload; the fold below is the truth, not it
            summons = open_summons(root)
            if summons:
                print("[loop] open summons in this repo — if you are the named node,"
                      " judge through the one pen; otherwise leave them parked:")
                for s in summons:
                    print(briefing(s))
        except Exception:
            pass  # a broken hook must never block the owner's prompt
        return 0

    summons = open_summons(root)
    for s in summons:
        print(briefing(s))
        print()
    if not summons:
        print("result: done — no open summons; nothing awaits a virtual node")
    else:
        print(f"result: report — {len(summons)} open summons")
    return 0


if __name__ == "__main__":
    sys.exit(main())
