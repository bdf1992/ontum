#!/usr/bin/env python3
"""The gap fold (done-line 0048): the loop's own gaps become the next work.

Every sensing surface this repo grew — the shame beat's still-mock set,
the inbox's parked pieces, reflection drift, the organ census — *surfaces*
a gap and then waits for a session to choose to care. The conversion from
surfaced to worked has been a session's self-discipline, and the record
shows that is the unreliable component (a session can narrate around a
scream for turns). This module is the conversion made ambient: one pure
read-only fold that enumerates the open gaps derivable from records
already on disk, in one fixed pressure order, each carrying the one
concrete next move — and the summons hook hands the highest-pressure gap
to every session that blinks in. The idle default becomes "work the
backlog the harness generated", never "wait for direction".

The pressure ranking is fixed in code (it is an ordering, not a dial —
nothing here moves work or judges it, so there is no setpoint to admit):

  1. mock-stage        a PIPELINE stage no node_real admission replaced —
                       fake work moving is the worst gap (done-line 0033)
  2. mock-actor        a .mock actor on the record the stage lifecycle
                       does not own (done-line 0049: an effective mock is
                       mocked, suffix or not)
  3. unadmitted-actor  a record-writer no admission ever named — identity
                       self-asserted (done-line 0049)
  4. parked-piece      an atom a gate refused, holding; amend or retire
  5. surface-drift     acts not yet reflected to a registered surface
  6. idle-organ        census wired·idle — a writer plumbed in, never fired
  7. dormant-organ     census dormant — a prune candidate (the cut is bdo's)

The fold computes lazily in priority order: the cheap log folds answer
before the census walks the tree, so the every-prompt hook pays the
census cost only when everything above it is clean. Read-only (I-3):
every move named here belongs to an existing pen.

Stdlib only. CLI ends with a clear result on stdout (D-6): done | report.
"""

import argparse
import sys
from pathlib import Path

from loop.reconcile import (DEFAULT_ROOT, PIPELINE, Fold, load_atoms,
                            load_epics, real_nodes)
from loop.orchestrate import next_action
from loop.reflect import drift, registered_surfaces

KIND_ORDER = ("mock-stage", "mock-actor", "unadmitted-actor",
              "parked-piece", "surface-drift", "idle-organ", "dormant-organ")

PIPELINE_MOCKS = frozenset(s["node"] for s in PIPELINE if ".mock" in s["node"])


def effective_mocks(root):
    """Anything effectively mock, with its basis (done-line 0049, bdo's
    directive: what is effectively mocked gets *mocked* — no hiding behind
    a missing `.mock` suffix). Three bases, one pure fold:

    - pipeline-stage   a PIPELINE stage no node_real admission replaced
                       (the original shame set, done-line 0033)
    - mock-actor       a `.mock`-marked node standing as an actor on the
                       record outside the PIPELINE lifecycle (the story-
                       author seed was invisible to every surface)
    - unadmitted-actor a node writing events/receipts that no node_real
                       admission has ever named on either side — its
                       identity is self-asserted (the merge-node landed
                       22 PRs this way)

    An admission clears both its sides: the stage/old id reads superseded,
    the admitted id reads real. History stands either way (I-2)."""
    if not (Path(root) / "log").is_dir():
        return []  # no records, no loop: absence, not a field of mocks
    fold = Fold(root)
    cleared = set()
    for adm in fold.admissions:
        if adm.get("type") == "node_real":
            cleared.add(adm.get("stage_node"))
            cleared.add(adm.get("real_node"))
    real = real_nodes(fold)
    out = [{"basis": "pipeline-stage", "actor": s["node"], "records": 0}
           for s in PIPELINE
           if ".mock" in s["node"] and s["node"] not in real]
    actors = {}
    for ev in fold.events:
        n = ev.get("from_node")
        if n:
            actors[n] = actors.get(n, 0) + 1
    for rc in fold.receipts:
        n = rc.get("node")
        if n:
            actors[n] = actors.get(n, 0) + 1
    for n in sorted(actors):
        if n in PIPELINE_MOCKS or n in cleared:
            continue  # the stage lifecycle owns it / an admission named it
        out.append({"basis": "mock-actor" if ".mock" in n
                    else "unadmitted-actor", "actor": n,
                    "records": actors[n]})
    return out


def _mock_gap(m):
    basis, actor = m["basis"], m["actor"]
    if basis == "pipeline-stage":
        return {
            "kind": "mock-stage", "subject": actor,
            "why": "fixed verdict, no judgement — every advance it "
                   "stamps is a mock moving fake work",
            "move": "build and prove the judging backing, then bdo's "
                    "realness gesture admits it: python -m loop.node "
                    f"admit-real --stage {actor} --node <real-node> --by bdo",
        }
    if basis == "mock-actor":
        return {
            "kind": "mock-actor", "subject": actor,
            "why": f"a .mock actor standing on the record outside the "
                   f"pipeline lifecycle — {m['records']} record(s) carry "
                   "its name and no surface screamed it",
            "move": "name its real seat (today's truth, not an aspiration), "
                    "then bdo's gesture admits it: python -m loop.node "
                    f"admit-real --stage {actor} --node <real-node> --by bdo",
        }
    return {
        "kind": "unadmitted-actor", "subject": actor,
        "why": f"writes to the record with no node_real admission on "
               f"either side — identity self-asserted across "
               f"{m['records']} record(s)",
        "move": "bdo's realness gesture admits the actor: python -m "
                f"loop.node admit-real --stage {actor} "
                "--node <admitted-id> --by bdo",
    }


def mock_stage_gaps(root):
    """The shame beat's fold (done-line 0033), as work: every PIPELINE
    stage still mock — no node_real admission has replaced it."""
    return sorted((_mock_gap(m) for m in effective_mocks(root)
                   if m["basis"] == "pipeline-stage"),
                  key=lambda g: g["subject"])


def mock_actor_gaps(root):
    """Effective mocks beyond the pipeline (done-line 0049): .mock actors
    the stage lifecycle does not own."""
    return sorted((_mock_gap(m) for m in effective_mocks(root)
                   if m["basis"] == "mock-actor"),
                  key=lambda g: g["subject"])


def unadmitted_actor_gaps(root):
    """Self-asserted identities on the record (done-line 0049): writers no
    admission ever named."""
    return sorted((_mock_gap(m) for m in effective_mocks(root)
                   if m["basis"] == "unadmitted-actor"),
                  key=lambda g: g["subject"])


def parked_piece_gaps(root):
    """The inbox's parked section (D-4), as work: atoms a gate refused,
    holding. The held-by receipt is the why — the gate already said it."""
    fold = Fold(root)
    real_map = real_nodes(fold)
    epics = load_epics(root)
    out = []
    for atom, ahash in load_atoms(root):
        action = next_action(fold, atom, ahash, real_map, epics)
        if not action or action[0] != "parked":
            continue
        held = [rc for rc in fold.receipts
                if rc.get("artifact_hash") == ahash
                and rc.get("next_suggested_event") is None]
        why = (f"held by {held[-1]['node']}: {held[-1]['verdict']} — "
               f"{held[-1]['reason']}" if held
               else "parked with no advancing event")
        out.append({
            "kind": "parked-piece", "subject": atom["id"],
            "why": why,
            "move": "amend the atom (a new version restarts its pipeline) "
                    "or surface retirement to bdo — the refusal stands as "
                    "history either way",
        })
    return sorted(out, key=lambda g: g["subject"])


def surface_drift_gaps(root):
    """Reflection drift (done-line 0018), as work: a registered surface
    showing less than the log knows."""
    out = []
    for sid in sorted(registered_surfaces(Fold(root))):
        acts = drift(root, sid)
        if acts:
            out.append({
                "kind": "surface-drift", "subject": sid,
                "why": f"{len(acts)} act(s) the log knows and the surface "
                       "does not show",
                "move": "python -m loop.reflect (the drift), then the "
                        "reflector pen applies what enabled rules name",
            })
    return out


def organ_gaps(root):
    """The census verdicts (done-line 0029), as work. Imported lazily and
    walked last: this is the one fold that reads the tree, not the log."""
    from loop import census as census_mod
    repo = Path(root).resolve().parent
    moves = {
        "wired·idle": ("idle-organ",
                       "exercise it through the working system so a word "
                       "of its lands on the record, or say why silence is "
                       "by design"),
        "dormant": ("dormant-organ",
                    "propose the prune with the census as evidence — the "
                    "cut stays bdo's (D-4)"),
    }
    out = []
    for r in census_mod.census(repo):
        entry = moves.get(r["verdict"])
        if entry is None:
            continue
        kind, move = entry
        out.append({
            "kind": kind, "subject": r["rel"],
            "why": census_mod.GLOSS[r["verdict"]],
            "move": move,
        })
    return sorted(out, key=lambda g: (KIND_ORDER.index(g["kind"]), g["subject"]))


def gaps(root, first_kind_only=False):
    """All open gaps in pressure order. With first_kind_only the walk
    stops at the first kind that has members — the hook path, so the
    every-prompt surface never pays for folds below the answer."""
    if not (Path(root) / "log").is_dir():
        # no records, no loop: a missing root is an absence, not a field
        # of mock stages (the hook runs in repos that are not this one)
        return []
    folds = (mock_stage_gaps, mock_actor_gaps, unadmitted_actor_gaps,
             parked_piece_gaps, surface_drift_gaps, organ_gaps)
    out = []
    for fold_fn in folds:
        out.extend(fold_fn(root))
        if first_kind_only and out:
            break
    return out


def top_gap(root):
    """The single highest-pressure gap, or None on a clean field."""
    found = gaps(root, first_kind_only=True)
    return found[0] if found else None


def render(found):
    for g in found:
        print(f"gap: {g['kind']} — {g['subject']}")
        print(f"  why: {g['why']}")
        print(f"  move: {g['move']}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=Path(DEFAULT_ROOT))
    args = ap.parse_args(argv)

    found = gaps(args.root)
    render(found)
    if not found:
        print("result: done — no open gaps; the field is clean")
    else:
        kinds = len({g["kind"] for g in found})
        print(f"result: report — {len(found)} open gap(s) across "
              f"{kinds} kind(s); the top one is the work")
    return 0


if __name__ == "__main__":
    sys.exit(main())
