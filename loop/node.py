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
                            load_atoms, make_receipt, now_ts, real_nodes,
                            receipt_for_stage, short_hash)


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
    rc = make_receipt(event, target, atom_id, artifact_hash,
                      node=node, verdict=verdict, reason=reason)
    append_line(root / "log" / "receipts.jsonl", rc)
    advancing = verdict == target["verdict"]
    print(f"result: report — {node} judged {target['event']} -> {verdict} ({rc['id']}); "
          + ("the atom advances on the next pass" if advancing
             else "the atom parks for a human (D-4)"))
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

    r = sub.add_parser("admit-real", help="admit that a stage is judged by a real node from now on")
    r.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    r.add_argument("--stage", required=True, help="the pipeline stage's node id being replaced")
    r.add_argument("--node", default=None, help="the real node id (omit to revert the stage to its mock)")
    r.add_argument("--by", required=True, help="who admits it (D-4: realness is signed, never self-set)")

    args = ap.parse_args(argv)
    if args.cmd == "judge":
        return judge(args.root, args.atom, args.node, args.verdict, args.reason)
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
