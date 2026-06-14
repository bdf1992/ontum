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
                            node_prompt, real_nodes, receipt_for_stage)
from loop.gaps import top_gap
from loop.orchestrate import HUMAN_NODE, next_action
from loop.reflect import drift, registered_surfaces


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
                ptext, phash = node_prompt(root, target)
                out.append({"atom": atom, "artifact_hash": ahash,
                            "node": target, "stage": stage,
                            "prompt_text": ptext, "prompt_hash": phash})
                break
    return out


def briefing(s):
    atom, stage = s["atom"], s["stage"]
    lines = [
        f"summons: {s['node']} — {atom['id']} awaits your verdict at seam {stage['seam']}",
        f"  story: {atom['story']['text']}",
        f"  verdicts: {' | '.join(stage['terminal_expected'])}",
    ]
    if s.get("prompt_text"):
        # the session's operating prompt arrives with the summons (§7);
        # the hash on the receipt will say this exact version judged
        lines += [
            f"  prompt-version: {s['prompt_hash']} (.ai-native/nodes/{s['node']}.md)",
            "  --- your operating prompt, versioned (§7) ---",
            s["prompt_text"].rstrip(),
            "  --- end prompt ---",
        ]
    lines += [
        f"  judge: python -m loop.node judge --atom {atom['id']} --node {s['node']}"
        f" --verdict <verdict> --reason \"<why>\"",
        "  contract: judge this one event only; never an event you announced"
        " (D-2); the receipt is your only pen (I-2).",
    ]
    return "\n".join(lines)


def owner_backlog(root):
    """Atoms awaiting the admitted-real owner stamp (D-4). Surfaced as a
    count only — the inbox is the briefing surface, this is the surfacer's
    pointer at it (§6)."""
    fold = Fold(root)
    real_map = real_nodes(fold)
    human = real_map.get(HUMAN_NODE)
    if human is None:
        return []
    return [atom["id"] for atom, ahash in load_atoms(root)
            if next_action(fold, atom, ahash, real_map) == ("await", human)]


def outcome_pressure_lines(root, hour=None):
    """OP2 (done-line 0073): the situation a waking session inherits — the
    outcome's gap modulated by the hour, not only the janitorial backlog.

    Imports the folds (loop.pressure, via loop.temporal); it never
    reimplements them — one fold, one truth. Tied to the same `root` the rest
    of the hook reads: the probe-set is resolved from that repo, so a foreign
    or missing root yields no line, never a crash and never another repo's
    pressure — fail-soft, because the hook that calls it is exit-0-always. The
    wall clock is read here, at the edge, never inside a fold."""
    from loop.pressure import DEFAULT_PROBES
    repo = Path(root).resolve().parent
    probes_path = repo / "outcomes" / DEFAULT_PROBES.name
    if not probes_path.exists():
        return None
    if hour is None:
        from datetime import datetime
        hour = datetime.now().hour
    from loop import temporal as temporal_mod
    result = temporal_mod.temporal(hour, probes_path=probes_path, repo=repo,
                                   root=root)
    pr, view = result["pressure"], result["temporal"]
    if pr["phase"] == "met" or not view or not view["focus"]:
        return None  # the outcome resolved, or no capability work to surface
    unresolved = len(pr["partial"]) + len(pr["unmet"]) + len(pr["dormant"])
    top = pr["top_leverage"]["id"] if pr["top_leverage"] else "—"
    move = view["next_move"]
    if len(move) > 220:
        move = move[:220].rstrip() + " …"
    return [
        f"[loop] outcome-pressure — {pr['outcome']}:",
        f"[loop]   phase {pr['phase']}, {unresolved} unresolved · leverage-top "
        f"{top} · the hour leans {view['lean']} ({view['register']}) → "
        f"focus {view['focus']}",
        f"[loop]   the move: {move}",
        "[loop]   the full read: python -m loop.temporal",
    ]


def slowloop_lines(root, hour=None):
    """The slow loop's dial proposal (done-line 0075), surfaced read-only —
    informational, never actionable here. A session sees the field's own
    outcomes proposing a temperature change, but it cannot dispose it: the
    dial moves only when the outside admits the proposal (D-4). This honours
    propose-vs-dispose at the surface too — showing a proposal is not routing
    anyone into admitting it. Tied to the same root; fail-soft, since the hook
    is exit-0-always. The wall clock is read here, at the edge."""
    if not (Path(root) / "log").is_dir():
        return None
    from loop import slowloop as slowloop_mod
    if hour is None:
        from datetime import datetime
        hour = datetime.now().hour
    result = slowloop_mod.slowloop(root, hour)
    p = result["proposal"]
    if not p or not p["change"]:
        return None  # no admitted setpoint, or the slow loop proposes no change
    delta = ", ".join(f"{k} {p['current'][k]}→{p['proposed'][k]}" for k in p["deltas"])
    because = p["because"][0] if p["because"] else ""
    if len(because) > 200:
        because = because[:200].rstrip() + " …"
    return [
        "[loop] slow-loop dial — the field's outcomes propose a setpoint change:",
        f"[loop]   {delta} · because {because}",
        "[loop]   a proposal, not a change — the dial moves only when the outside "
        "admits it (D-4); the full read: python -m loop.slowloop",
    ]


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
            backlog = owner_backlog(root)
            if backlog:
                print(f"[loop] {len(backlog)} item(s) await bdo's stamp"
                      " — python -m loop.node inbox")
            unreflected = sum(len(drift(root, sid))
                              for sid in registered_surfaces(Fold(root)))
            if unreflected:
                # a stale surface is surfaced, never silently wrong
                # (done-line 0018); applying stays the reflector pen's act
                print(f"[loop] surface drift: {unreflected} act(s) not yet "
                      "reflected — python -m loop.reflect")
            # OP2 (done-line 0073): the outcome's gap, modulated by the hour —
            # the situation, surfaced beside the work-pressure below (composing,
            # not replacing it; the single ranked field is OP3).
            op_lines = outcome_pressure_lines(root)
            if op_lines:
                for ln in op_lines:
                    print(ln)
            # done-line 0075: the slow loop's dial proposal, read-only — shown,
            # never disposed (showing a proposal is not routing anyone to admit it)
            sl_lines = slowloop_lines(root)
            if sl_lines:
                for ln in sl_lines:
                    print(ln)
            gap = top_gap(root)
            if gap:
                # gap-to-work (done-line 0048): the idle default is the
                # backlog the harness generated, never "wait for direction".
                # The why is clipped to a line — the full text is one
                # command away, and a briefing that floods stops being read.
                why = gap["why"]
                if len(why) > 200:
                    why = why[:200].rstrip() + " …"
                print(f"[loop] the next gap ({gap['kind']}): {gap['subject']}"
                      f" — {why}")
                print(f"[loop]   the move: {gap['move']}")
                print("[loop]   full backlog: python -m loop.gaps")
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
