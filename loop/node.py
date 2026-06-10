#!/usr/bin/env python3
"""The summoned node's pen (D-10): a real node blinks in, reads the place,
judges one announced event, writes one receipt here, and dissolves.

This CLI is deliberately dumb: it holds no judgement of its own. The verdict
arrives from whoever was summoned — a session, a model, bdo — and this only
enforces the seam contract: the stage must be admitted-real (I-8), the
writer must be the admitted node, the verdict must come from the stage's
terminal set, a node may not judge an event it announced (D-2), and writing
twice is a no-op (I-2).

Realness itself is admitted here too (admit-real), because making a node
real changes what the system will admit — that is code, and it is signed
(§7, D-4). Reverting a stage to its mock is a superseding admission, never
an erasure.

Stdlib only. Ends with a clear result on stdout (D-6): report | needs-you.
"""

import argparse
import sys
from pathlib import Path

from loop.reconcile import (DEFAULT_ROOT, PIPELINE, Fold, append_line,
                            epic_of, glue_of, load_atoms, load_epics,
                            make_receipt, node_prompt, now_ts, real_nodes,
                            receipt_for_stage, short_hash)
from loop.orchestrate import HUMAN_NODE, STAMP_STAGE, next_action


def admit_real(root, stage_node, real_node, by, supersedes=None):
    adm = {
        "id": "adm." + short_hash("node_real", stage_node, str(real_node), str(by), now_ts()),
        "type": "node_real",
        "stage_node": stage_node,
        "real_node": real_node,
        "by": by,
        "supersedes": supersedes,
        "ts": now_ts(),
    }
    append_line(root / "log" / "admissions.jsonl", adm)
    return adm


def judge(root, atom_id, node, verdict, reason):
    entries = [(a, h) for a, h in load_atoms(root) if a["id"] == atom_id]
    if len(entries) != 1:
        print(f"result: needs-you — atom {atom_id} not found in {root / 'atoms'}")
        return 2
    atom, artifact_hash = entries[0]
    fold = Fold(root)
    real_map = real_nodes(fold)

    # I-2 first: this node already handled this version of the atom
    existing = fold.receipt_by_node(node, artifact_hash)
    if existing is not None:
        print(f"result: report — receipt {existing['id']} already exists for "
              f"({node}, this atom version); no-op (I-2)")
        return 0

    # the first announced-but-unsatisfied stage is the one open for judgement
    target, event = None, None
    for stage in PIPELINE:
        ev = fold.event(stage["event"], artifact_hash)
        if ev is None:
            break
        if receipt_for_stage(fold, stage, artifact_hash, real_map) is None:
            target, event = stage, ev
            break
    if target is None:
        print(f"result: needs-you — no announced event awaits judgement for {atom_id}")
        return 2
    expected = real_map.get(target["node"])
    if expected is None:
        print(f"result: needs-you — stage {target['node']} is not admitted-real; the loop judges its own mocks")
        return 2
    if node != expected:
        print(f"result: needs-you — this seam awaits {expected}, not {node}")
        return 2
    if node == event.get("from_node"):
        print(f"result: needs-you — {node} announced this event and may not judge it (D-2)")
        return 2
    if verdict not in target["terminal_expected"]:
        print(f"result: needs-you — verdict {verdict!r} is not in this seam's terminal set: "
              f"{', '.join(target['terminal_expected'])}")
        return 2
    _, prompt_hash = node_prompt(root, node)  # the prompt in force, if any (§7)
    rc = make_receipt(event, target, atom_id, artifact_hash,
                      node=node, verdict=verdict, reason=reason,
                      prompt_hash=prompt_hash)
    append_line(root / "log" / "receipts.jsonl", rc)
    advancing = verdict == target["verdict"]
    print(f"result: report — {node} judged {target['event']} -> {verdict} ({rc['id']}); "
          + ("the atom advances on the next pass" if advancing
             else "the atom parks for a human (D-4)"))
    return 0


def inbox(root):
    """The owner's open items, read-only (I-3: this view writes nothing).

    Three sections: atoms awaiting bdo's stamp (yours — everything needed
    to judge is printed, plus the one line that clears it); atoms awaiting
    other summoned nodes (the control session routes those, not you); and
    atoms parked by a reject or a dead end (yours to amend or retire,
    D-4). Clearing stays the one existing pen: judge."""
    fold = Fold(root)
    atoms = load_atoms(root)
    real_map = real_nodes(fold)
    human = real_map.get(HUMAN_NODE)
    mine, summons, parked = [], [], []
    for atom, ahash in atoms:
        action = next_action(fold, atom, ahash, real_map)
        if action is None:
            continue
        kind, target = action
        if kind == "await" and target == human:
            mine.append((atom, ahash))
        elif kind == "await":
            summons.append((atom, target))
        elif kind == "parked":
            parked.append((atom, ahash))

    if human is None:
        print("note: the owner stamp is still mocked — nothing waits on you "
              "until it is admitted real (node admit-real)")
    epics = load_epics(root)
    # epic-first (done-line 0006): brief the arc, then the items inside it
    mine.sort(key=lambda item: (epic_of(item[0], epics) or {}).get("id", "~unfiled"))
    last_key = object()  # sentinel: distinct from None (the unfiled group)
    for atom, ahash in mine:
        epic = epic_of(atom, epics)
        key = epic["id"] if epic else None
        if key != last_key:
            last_key = key
            if epic:
                print(f"\n== {epic['id']} — {epic['value']}")
            else:
                print("\n== unfiled — no epic claims this yet")
        print(f"\n{atom['id']} — awaiting your stamp ({human})")
        glue = glue_of(atom, epic)
        if glue:
            print(f"  glues in: {glue}")
        briefing = atom.get("briefing", {})
        if briefing:
            # value first, mechanism after (done-line 0005)
            print(f"  {briefing.get('headline', '')}")
            print(f"  value: {briefing['value']}")
            if briefing.get("why_now"):
                print(f"  why now: {briefing['why_now']}")
            for label, key in (("if you accept", "if_accepted"),
                               ("if you reject", "if_rejected"),
                               ("cost of a wrong call", "cost_of_wrong_call")):
                if briefing.get(key):
                    print(f"  {label}: {briefing[key]}")
        print(f"  story: {atom['story']['text']}")
        print(f"  author's confidence: {atom['story']['value_confidence']}")
        for rc in fold.receipts:
            if rc.get("artifact_hash") == ahash:
                print(f"  {rc['node']}: {rc['verdict']} — {rc['reason']}")
        print(f"  verdicts: {' | '.join(STAMP_STAGE['terminal_expected'])}")
        print(f"  clear: python -m loop.node judge --atom {atom['id']} "
              f"--node {human} --verdict <verdict> --reason \"<why>\"")
    for atom, target in summons:
        print(f"\n{atom['id']} — awaiting summons: {target} (the control session routes this, not you)")
    for atom, ahash in parked:
        print(f"\n{atom['id']} — parked (yours to amend or retire, D-4)")
        for rc in fold.receipts:
            if rc.get("artifact_hash") == ahash and rc.get("next_suggested_event") is None:
                print(f"  held by {rc['node']}: {rc['verdict']} — {rc['reason']}")
    print(f"\nresult: report — {len(mine)} item(s) awaiting your stamp, "
          f"{len(summons)} awaiting summons, {len(parked)} parked")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    j = sub.add_parser("judge", help="write one summoned verdict as a receipt")
    j.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    j.add_argument("--atom", required=True, help="atom id, e.g. atom.real-value-gate.v0")
    j.add_argument("--node", required=True, help="the summoned node's id (must match the admitted real node)")
    j.add_argument("--verdict", required=True)
    j.add_argument("--reason", required=True)

    i = sub.add_parser("inbox", help="the owner's open items, read-only")
    i.add_argument("--root", type=Path, default=DEFAULT_ROOT)

    r = sub.add_parser("admit-real", help="admit that a stage is judged by a real node from now on")
    r.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    r.add_argument("--stage", required=True, help="the pipeline stage's node id being replaced")
    r.add_argument("--node", default=None, help="the real node id (omit to revert the stage to its mock)")
    r.add_argument("--by", required=True, help="who admits it (D-4: realness is signed, never self-set)")

    args = ap.parse_args(argv)
    if args.cmd == "judge":
        return judge(args.root, args.atom, args.node, args.verdict, args.reason)
    if args.cmd == "inbox":
        return inbox(args.root)
    stages = {s["node"] for s in PIPELINE}
    if args.stage not in stages:
        print(f"result: needs-you — unknown stage {args.stage}; stages: {', '.join(sorted(stages))}")
        return 2
    adm = admit_real(args.root, args.stage, args.node, args.by)
    print(f"result: report — {adm['id']}: {args.stage} is now judged by "
          + (args.node if args.node else "its mock again") + f" (admitted by {args.by})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
