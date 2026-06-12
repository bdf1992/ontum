#!/usr/bin/env python3
"""The first Field (done-line 0050): one arc's work-topology as a pure fold.

Given one arc, produce its decomposition ladder — arc -> epic -> story ->
task -> environment -> node -> occupant — where every rung carries state,
evidence (record ids on the log, never prose), and a next_safe_move (an
existing pen's verb, or "needs bdo" when the move is his). The proof that
work has address, scale, parentage, authority, and occupancy. Not a
monitor, not the portal: those are later projections of this map
(epic.the-field); `loop.gaps` is the proof-of-shape this generalises.

The discipline that keeps it honest:

- a pure fold over the log (I-3): it writes nothing, and every move it
  names belongs to an existing pen;
- absence is information: `arc`, `epic`, `story`, and `node` are
  first-class on disk today; `task`, `environment`, and `occupant` are
  partial or implicit — the fold surfaces those rungs as **named gaps**,
  never invents them. A field that fabricates a clean ladder is a mock
  with a bigger bill (the §10 test fails exactly that fabrication);
- occupancy carries authority: an occupant whose identity no `node_real`
  admission ever named (either side) renders **UN-AUTHORISED** — the
  field shows who stands on a node and whether bdo ever stamped them
  there. An id named only as a superseded stage side reads as an
  authorised alias of its admitted seat (the one lifecycle every seat
  shares, done-line 0049).

Stdlib only. CLI ends with a clear result on stdout (D-6): report |
needs-you — read-only, so never `done`-as-an-act.
"""

import argparse
import json
import sys
from pathlib import Path

from loop.reconcile import (DEFAULT_ROOT, PIPELINE, Fold, arc_confirmation,
                            atom_state, load_atoms, load_epics, real_nodes,
                            superseded_atom_ids)
from loop.orchestrate import next_action

RUNGS = ("arc", "epic", "story", "task", "environment", "node", "occupant")

# the rungs that are not first-class records today, each with the honest
# reason — surfaced, never invented (done-line 0050: absence is information)
NOT_FIRST_CLASS = {
    "task": ("tasks live implicitly inside stories and done-lines; no task "
             "record exists on disk"),
    "environment": ("environments live as composed CLAUDE.md scope stacks "
                    "and worktrees, not as records on the log"),
}


def _admission_index(fold):
    """Two maps from the node_real fold: admitted ids -> the admission that
    seated them (latest wins), and superseded stage-side ids -> the same
    admission (the alias trail). A null real_node un-seats (reverts)."""
    seated, aliased = {}, {}
    for adm in fold.admissions:
        if adm.get("type") != "node_real":
            continue
        stage, real = adm.get("stage_node"), adm.get("real_node")
        if real:
            seated[real] = adm
            if stage:
                aliased[stage] = adm
                seated.pop(stage, None)
        elif stage:
            seated.pop(stage, None)
    return seated, aliased


def _arc_rung(fold, epic):
    conf = arc_confirmation(fold, epic["id"])
    if conf:
        return [{
            "subject": epic["id"], "state": "confirmed",
            "evidence": [conf["id"]],
            "next_safe_move": "pieces flow on the standing stamp "
                              "(loop.reconcile / loop.orchestrate); a "
                              "refusal surfaces in the digest",
        }]
    return [{
        "subject": epic["id"], "state": "unconfirmed",
        "evidence": [],
        "next_safe_move": "needs bdo: his arc-confirm gesture "
                          "(arc-intake opens the issue; he closes it "
                          "with a comment)",
    }]


def _epic_rung(epic, present_atoms):
    items = []
    for piece in epic.get("pieces", []):
        atom_id = piece.get("atom")
        if atom_id in present_atoms:
            items.append({"subject": atom_id, "state": "present",
                          "evidence": [atom_id],
                          "next_safe_move": "see the story rung"})
        else:
            items.append({
                "subject": atom_id, "state": "absent",
                "evidence": [],
                "next_safe_move": "author the atom the epic names (a "
                                  "session's work) or it was retired — "
                                  "the log holds the history",
            })
    return items


def _story_rung(fold, real_map, epics, arc_atoms):
    # a version a higher sibling replaces is history (done-line 0056): the
    # field still shows it (topology includes the past) but never calls it a
    # live parked piece — the amend already landed as the newer version.
    superseded = superseded_atom_ids({a["id"] for a, _ in arc_atoms})
    items = []
    for atom, ahash in arc_atoms:
        receipts = [rc["id"] for rc in fold.receipts
                    if rc.get("artifact_hash") == ahash]
        action = next_action(fold, atom, ahash, real_map, epics)
        state = atom_state(fold, ahash)
        if atom["id"] in superseded:
            kind = "superseded"
            move = ("none — a newer version of this atom carries the work; "
                    "this one's receipts stand as history (done-line 0056)")
        elif action is None:
            kind, move = "settled", "none — settled at " + state
        elif action[0] in ("seed", "derive", "judge"):
            kind = f"in-flight ({action[0]})"
            move = "the loop's own step: python -m loop.orchestrate"
        elif action[0] == "await":
            kind = f"awaiting {action[1]}"
            move = ("judge through the one pen if you are the named node: "
                    "python -m loop.node judge")
        else:
            kind = "parked"
            move = ("amend the atom (a new version restarts its pipeline) "
                    "or surface retirement to bdo — the refusal stands as "
                    "history either way")
        items.append({"subject": atom["id"],
                      "state": f"{kind} (pipeline: {state})",
                      "evidence": receipts, "next_safe_move": move})
    return items


def _gap_rung(rung):
    return [{
        "subject": rung, "state": "not-first-class",
        "evidence": [],
        "why": NOT_FIRST_CLASS[rung] + " — absence is information; the "
               "field surfaces this rung, it does not invent it",
        "next_safe_move": "needs bdo: promoting this rung to first-class "
                          "is its own done-line, his to steer",
    }]


def _node_rung(fold, real_map):
    seated, _ = _admission_index(fold)
    items = []
    for stage in PIPELINE:
        mock = stage["node"]
        real = real_map.get(mock)
        if real:
            adm = seated.get(real)
            items.append({"subject": real,
                          "state": f"real (seam {stage['seam']})",
                          "evidence": [adm["id"]] if adm else [],
                          "next_safe_move": "none — admitted; judges when "
                                            "summoned (loop.node judge)"})
        else:
            items.append({
                "subject": mock, "state": f"MOCK (seam {stage['seam']})",
                "evidence": [],
                "next_safe_move": "build and prove the backing, then bdo's "
                                  "gesture: python -m loop.node admit-real "
                                  f"--stage {mock} --node <real-node> --by bdo",
            })
    return items


def _occupant_rung(fold, epic, arc_hashes):
    seated, aliased = _admission_index(fold)
    occupants = {}
    for ev in fold.events:
        if ev.get("artifact_hash") in arc_hashes and ev.get("from_node"):
            occupants.setdefault(ev["from_node"], []).append(ev["id"])
    for rc in fold.receipts:
        on_arc = (rc.get("artifact_hash") in arc_hashes
                  or (rc.get("kind") == "merge" and rc.get("epic") == epic["id"]))
        if on_arc and rc.get("node"):
            occupants.setdefault(rc["node"], []).append(rc["id"])
    items = []
    for node in sorted(occupants):
        evidence = occupants[node]
        if node in seated:
            items.append({"subject": node, "state": "authorised",
                          "evidence": [seated[node]["id"]] + evidence,
                          "next_safe_move": "none — bdo's admission seats it"})
        elif node in aliased:
            adm = aliased[node]
            items.append({"subject": node,
                          "state": f"authorised (alias of {adm['real_node']})",
                          "evidence": [adm["id"]] + evidence,
                          "next_safe_move": "none — the admission names this "
                                            "id as its superseded side"})
        else:
            items.append({
                "subject": node, "state": "UN-AUTHORISED",
                "evidence": evidence,
                "why": "stands on the record with no node_real admission "
                       "on either side — identity self-asserted",
                "next_safe_move": "needs bdo: python -m loop.node "
                                  f"admit-real --stage {node} "
                                  "--node <admitted-id> --by bdo",
            })
    return items


def field(root, epic_id):
    """The ladder for one arc, or None when the arc is not on disk —
    an absent epic is an absence to report, never an empty ladder."""
    root = Path(root)
    epics = load_epics(root)
    epic = next((e for e in epics if e["id"] == epic_id), None)
    if epic is None:
        return None
    fold = Fold(root)
    real_map = real_nodes(fold)
    atoms = load_atoms(root)
    piece_ids = {p.get("atom") for p in epic.get("pieces", [])}
    arc_atoms = [(a, h) for a, h in atoms
                 if a["id"] in piece_ids
                 or epic_id in a.get("incidence", {}).get("serves", [])]
    arc_hashes = {h for _, h in arc_atoms}
    return {
        "arc": epic_id,
        "rungs": [
            {"rung": "arc", "items": _arc_rung(fold, epic)},
            {"rung": "epic", "items": _epic_rung(
                epic, {a["id"] for a, _ in arc_atoms})},
            {"rung": "story", "items": _story_rung(
                fold, real_map, epics, arc_atoms)},
            {"rung": "task", "items": _gap_rung("task")},
            {"rung": "environment", "items": _gap_rung("environment")},
            {"rung": "node", "items": _node_rung(fold, real_map)},
            {"rung": "occupant", "items": _occupant_rung(
                fold, epic, arc_hashes)},
        ],
    }


def render(ladder):
    print(f"# the field — {ladder['arc']}")
    for rung in ladder["rungs"]:
        print(f"\n{rung['rung']}")
        for it in rung["items"]:
            print(f"  {it['subject']} — {it['state']}")
            if it.get("why"):
                print(f"    why: {it['why']}")
            if it["evidence"]:
                print(f"    evidence: {', '.join(it['evidence'][:6])}"
                      + (f" (+{len(it['evidence']) - 6} more)"
                         if len(it["evidence"]) > 6 else ""))
            print(f"    move: {it['next_safe_move']}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--arc", required=True, help="the epic id, e.g. epic.the-field")
    ap.add_argument("--root", type=Path, default=Path(DEFAULT_ROOT))
    ap.add_argument("--json", action="store_true",
                    help="emit the ladder as JSON (the dataset, not the view)")
    args = ap.parse_args(argv)

    ladder = field(args.root, args.arc)
    if ladder is None:
        print(f"result: needs-you — no epic {args.arc!r} on disk; an absent "
              "arc is an absence, not an empty ladder")
        return 2
    if args.json:
        print(json.dumps(ladder, indent=2, sort_keys=True))
    else:
        render(ladder)
    unauth = sum(1 for r in ladder["rungs"] for it in r["items"]
                 if it["state"] == "UN-AUTHORISED")
    gaps = sum(1 for r in ladder["rungs"] for it in r["items"]
               if it["state"] in ("not-first-class", "absent", "MOCK")
               or it["state"].startswith("parked"))
    print(f"\nresult: report — {len(ladder['rungs'])} rungs; "
          f"{gaps} gap(s) surfaced, {unauth} un-authorised occupant(s); "
          "read-only, every move routes through an existing pen")
    return 0


if __name__ == "__main__":
    sys.exit(main())
