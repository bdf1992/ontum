#!/usr/bin/env python3
"""The reflection fold (done-line 0018): the owner's queue, mirrored outward.

bdo looked at GitHub Issues, saw nothing, and concluded the hook was lying
— the queue was real, the surface he visits showed none of it. His amend
(rcp.558ad49545cd) named the pattern and his stamp on the surface-registry
story (rcp.f68f73f3fee8) authorized it: external surfaces are *registered*
as admitted records, and what the log holds is *reflected* onto them, so
the external view is a mirror of the truth instead of a parallel world.

This module is the pure half — stdlib, no network, no subprocess (hard
rule). It computes, for each registered surface, the desired view (one
open item per atom awaiting the admitted-real owner stamp, briefed
arc-first) and the drift against what was last reflected. Reflections are
log records (events.jsonl, type "surface.reflected"), so drift is itself
a fold — deleting nothing, trusting no memory. The applying half is the
reflector pen (.claude/skills/reflect/reflect.py, gh-backed like the PR
pen): it applies exactly this drift and records each act back here.

Verdicts never flow in from a surface: the issue is a mirror, not a
second write path (D-4) — clearing stays loop.node judge.

CLI (read-only except register):
  python -m loop.reflect                    drift status across surfaces
  python -m loop.reflect register --surface github-issues \
      --address owner/repo --by bdo        admit a surface (omit --address
                                            to deregister; latest wins, I-8)
"""

import argparse
import sys
from pathlib import Path

from loop.reconcile import (DEFAULT_ROOT, Fold, append_line, epic_of, glue_of,
                            load_atoms, load_epics, now_ts, real_nodes,
                            receipt_for_stage, short_hash)
from loop.orchestrate import HUMAN_NODE, STAMP_STAGE, next_action

REFLECTED_EVENT = "surface.reflected"
PEN = "python .claude/skills/reflect/reflect.py"


def admit_surface(root, surface, address, by, kind="github-issues"):
    """A surface is an admitted record (I-8), never a code literal: id,
    kind, address, signed --by. A null address deregisters (latest wins),
    superseding — never erasing — the admission before it."""
    adm = {
        "id": "adm." + short_hash("surface", surface, str(address), str(by), now_ts()),
        "type": "surface",
        "surface": surface,
        "kind": kind,
        "address": address,
        "by": by,
        "ts": now_ts(),
    }
    append_line(root / "log" / "admissions.jsonl", adm)
    return adm


def registered_surfaces(fold):
    """Latest surface admission per id wins; a null address deregisters."""
    surfaces = {}
    for adm in fold.admissions:
        if adm.get("type") == "surface" and adm.get("surface"):
            if adm.get("address"):
                surfaces[adm["surface"]] = adm
            else:
                surfaces.pop(adm["surface"], None)
    return surfaces


def reflections(fold, surface):
    """What this surface has been told, by (artifact_hash, act) — first
    record wins (the fold dedups by id, so re-recording is a no-op)."""
    out = {}
    for ev in fold.events:
        if ev.get("type") == REFLECTED_EVENT and ev.get("surface") == surface:
            out.setdefault((ev.get("artifact_hash"), ev.get("act")), ev)
    return out


def record_reflection(root, surface, atom_id, artifact_hash, act, external_ref, by):
    """The applying pen's receipt: one applied act, on the log, with
    provenance. Content-derived id — recording the same act twice folds
    to one (I-2)."""
    ev = {
        "id": "evt." + short_hash(REFLECTED_EVENT, surface, artifact_hash, act),
        "type": REFLECTED_EVENT,
        "surface": surface,
        "artifact_id": atom_id,
        "artifact_hash": artifact_hash,
        "act": act,
        "external_ref": external_ref,
        "by": by,
        "ts": now_ts(),
    }
    append_line(root / "log" / "events.jsonl", ev)
    return ev


def awaiting_stamp(root, fold, real_map):
    """The owner's queue: every atom whose next action is the admitted-real
    stamp — the same fold the inbox and the hook count from."""
    human = real_map.get(HUMAN_NODE)
    if human is None:
        return []
    return [(atom, ahash) for atom, ahash in load_atoms(root)
            if next_action(fold, atom, ahash, real_map) == ("await", human)]


def item_title(atom):
    headline = atom.get("briefing", {}).get("headline", "")
    title = f"[stamp] {atom['id']}"
    return f"{title} — {headline}" if headline else title


def item_body(root, fold, atom, ahash, epics, human):
    """The briefing, arc-first (done-line 0006), as markdown — the same
    layers the inbox prints, shaped for the surface bdo actually opens."""
    epic = epic_of(atom, epics)
    lines = []
    if epic:
        lines += [f"## the arc", f"**{epic['id']}** — {epic['value']}"]
        glue = glue_of(atom, epic)
        if glue:
            lines.append(f"*glues in:* {glue}")
        lines.append("")
    briefing = atom.get("briefing", {})
    lines.append("## the item")
    if briefing.get("headline"):
        lines.append(f"**{briefing['headline']}**")
    for label, key in (("value", "value"), ("why now", "why_now"),
                       ("if you accept", "if_accepted"),
                       ("if you reject", "if_rejected"),
                       ("cost of a wrong call", "cost_of_wrong_call")):
        if briefing.get(key):
            lines.append(f"- **{label}:** {briefing[key]}")
    lines += ["", f"*story:* {atom['story']['text']}",
              f"*author's confidence:* {atom['story']['value_confidence']}"]
    receipts = [rc for rc in fold.receipts if rc.get("artifact_hash") == ahash]
    if receipts:
        lines += ["", "## receipts so far"]
        lines += [f"- `{rc['node']}`: **{rc['verdict']}** — {rc['reason']}"
                  for rc in receipts]
    lines += [
        "",
        "## your verdict",
        f"`{' | '.join(STAMP_STAGE['terminal_expected'])}`",
        "",
        "This issue is a **mirror** of the loop's owner inbox — judging it",
        "here does nothing; the verdict lands through the one pen (D-4),",
        "in chat or:",
        "```sh",
        f"python -m loop.node judge --atom {atom['id']} --node {human} "
        "--verdict <verdict> --reason \"<why>\"",
        "```",
        "Reflected from the log by `loop/reflect.py`; when the stamp lands,",
        "the reflector closes this issue with the verdict and receipt id.",
    ]
    return "\n".join(lines)


def drift(root, surface):
    """desired view minus reflected view, as the acts that would close the
    gap. Pure: this computes; only the pen applies. Raises on an
    unregistered surface — reflecting to a surface nobody admitted is the
    §10 thing that must not fit."""
    fold = Fold(root)
    surfaces = registered_surfaces(fold)
    if surface not in surfaces:
        known = ", ".join(sorted(surfaces)) or "none registered"
        raise ValueError(f"surface {surface!r} is not admitted ({known}); "
                         f"register it: python -m loop.reflect register "
                         f"--surface {surface} --address <owner/repo> --by <who>")
    real_map = real_nodes(fold)
    human = real_map.get(HUMAN_NODE)
    epics = load_epics(root)
    seen = reflections(fold, surface)
    awaiting = awaiting_stamp(root, fold, real_map)
    acts = []
    for atom, ahash in awaiting:
        if (ahash, "open") not in seen:
            acts.append({"act": "open", "atom_id": atom["id"],
                         "artifact_hash": ahash,
                         "title": item_title(atom),
                         "body": item_body(root, fold, atom, ahash, epics, human)})
    awaiting_hashes = {ahash for _, ahash in awaiting}
    for (ahash, act), ev in sorted(seen.items(), key=lambda kv: kv[1]["id"]):
        if act != "open" or ahash in awaiting_hashes or (ahash, "close") in seen:
            continue
        rc = receipt_for_stage(fold, STAMP_STAGE, ahash, real_map)
        if rc:
            comment = (f"the stamp landed: **{rc['verdict']}** ({rc['id']}) — "
                       f"{rc['reason']}")
        else:
            comment = ("no longer at the stamp — the atom advanced, was "
                       "amended to a new version, or was retired; the log "
                       "holds the history")
        acts.append({"act": "close", "atom_id": ev.get("artifact_id"),
                     "artifact_hash": ahash,
                     "external_ref": ev.get("external_ref"),
                     "comment": comment})
    return acts


def status(root):
    """Read-only (I-3): every registered surface and its drift."""
    fold = Fold(root)
    surfaces = registered_surfaces(fold)
    if not surfaces:
        print("result: done — no surfaces registered; the inbox reaches only "
              "this repo (register one: python -m loop.reflect register "
              "--surface <id> --address <owner/repo> --by <who>)")
        return 0
    total = 0
    for sid, adm in sorted(surfaces.items()):
        acts = drift(root, sid)
        total += len(acts)
        print(f"surface: {sid} ({adm['kind']}) -> {adm['address']} "
              f"(admitted by {adm['by']}, {adm['id']})")
        for a in acts:
            ref = f" [{a.get('external_ref')}]" if a.get("external_ref") else ""
            print(f"  {a['act']}: {a['atom_id']}{ref}")
        if not acts:
            print("  no drift — the surface mirrors the log")
    if total:
        print(f"result: report — {total} act(s) of drift; apply through the "
              f"reflector pen: {PEN} apply --surface <id> --by <who>")
    else:
        print("result: done — every registered surface mirrors the log")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd")

    st = sub.add_parser("status", help="registered surfaces and their drift, read-only")
    st.add_argument("--root", type=Path, default=DEFAULT_ROOT)

    reg = sub.add_parser("register", help="admit a surface (I-8: a signed record, latest wins)")
    reg.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    reg.add_argument("--surface", required=True, help="surface id, e.g. github-issues")
    reg.add_argument("--kind", default="github-issues")
    reg.add_argument("--address", default=None,
                     help="where it lives, e.g. owner/repo (omit to deregister)")
    reg.add_argument("--by", required=True,
                     help="who admits it (D-4: surfaces are signed, never self-set)")

    args = ap.parse_args(argv)
    if args.cmd == "register":
        adm = admit_surface(args.root, args.surface, args.address, args.by, kind=args.kind)
        print(f"result: report — {adm['id']}: surface {args.surface} "
              + (f"registered at {args.address}" if args.address else "deregistered")
              + f" (admitted by {args.by})")
        return 0
    root = args.root if args.cmd == "status" else DEFAULT_ROOT
    return status(root)


if __name__ == "__main__":
    sys.exit(main())
