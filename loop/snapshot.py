#!/usr/bin/env python3
"""The snapshot acceptance unit (done-line 0155): the spine of
`epic.environments`, the unit a second party accepts.

A snapshot is the natural unit acceptance attaches to — immutable, named,
recorded — the way an atom's identity already IS the sha256 of its bytes
(the identity-is-content-hash architecture note). Work strands because the
acceptance discipline has hung off mutable, mid-flight PRs; a frozen named
snapshot is the unit that does not strand, and the unit that joins the
per-atom (content-hash) and per-PR (git) namespaces `loop/pull.py` made
visible as an open gap.

This module COMPOSES, it does not double-build (§10): it sits OVER the atom
content-hash identity in `reconcile.py` (`load_atoms`), the existing
value-gate/owner-stamp receipts (acceptance is DERIVED, never a second write
path or a second authority), `loop/pull.py`'s namespace_gap, and
`loop/deploy.py`'s stamped-snapshot shape. It is the joining unit across
them, not a second ledger.

The §10 teeth — a snapshot that LIES about its join is caught, not trusted.
Two locally-fine records refuse to fit:

  - A snapshot is a frozen reference to atom bytes; an atom file is editable.
    Each is fine alone. When the atom's live bytes no longer match the hash
    the snapshot froze at mint time, the snapshot is **stale** — it claims a
    join that is no longer real (editing an atom in place mints a new version
    that restarts the pipeline; the frozen reference now points at bytes that
    changed). The fold notices and refuses to call it accepted.

  - A snapshot naming an atom with no resolvable atom file is a **ghost**
    binding — refused at the pen (mint) with a cited reason, and re-checked
    at resolve in case the atom was removed after mint.

Read-only and propose-only but for the one `mint` pen; acceptance is read
off the pipeline's own receipts, never re-derived or asserted (D-4, §10).
Stdlib only, no network, no git (loop/'s law) — a pure fold over the
committed log and the atom files.

CLI:
  python -m loop.snapshot                     the minted snapshots + each one's resolution
  python -m loop.snapshot --json              the raw dataset (machine-readable)
  python -m loop.snapshot resolve --name <n>  one snapshot's resolution
  python -m loop.snapshot mint --name <n> --atoms <id..> --commit <sha> --by <who>
"""

import argparse
import sys
from pathlib import Path

from loop.reconcile import (DEFAULT_ROOT, PIPELINE, Fold, append_line, canon,
                            load_atoms, now_ts, real_nodes, receipt_for_stage,
                            short_hash, superseded_atom_ids)

SNAPSHOT_TYPE = "snapshot"
# The independent acceptance an atom must earn (D-2): the value-gate stage —
# the first second-set-of-eyes the pipeline runs. Read off its receipt; never
# re-judged here (no second authority).
VALUE_STAGE = next(s for s in PIPELINE if s["seam"] == "author-to-value")
STAMP_STAGE = next(s for s in PIPELINE if s["seam"] == "value-to-owner-stamp")


def _atom_hashes(root):
    """id -> live content-hash for every atom file on disk (the field)."""
    return {atom["id"]: h for atom, h in load_atoms(root)}


def snapshots(fold):
    """Every minted snapshot, latest-by-name wins, an `enabled: false` one
    withdrawn (superseded, never erased) — the same shape as every other
    admitted record (arc_confirmation, production_promotion)."""
    active = {}
    for adm in fold.admissions:
        if adm.get("type") != SNAPSHOT_TYPE:
            continue
        name = adm.get("name")
        if not name:
            continue
        active[name] = adm if adm.get("enabled", True) else None
    return {n: a for n, a in active.items() if a is not None}


def _atom_acceptance(fold, frozen_hash, real_map):
    """The DERIVED acceptance of one frozen atom version — read off the
    pipeline's own receipts for the exact bytes the snapshot froze, never
    re-judged. `value_accepted` is the independent second-set-of-eyes (D-2);
    `owner_stamped` is the owner's stamp (or his arc confirmation, which the
    loop satisfies it under). A reject/amend at the value-gate is an explicit
    refusal."""
    rc = receipt_for_stage(fold, VALUE_STAGE, frozen_hash, real_map)
    value_verdict = rc.get("verdict") if rc else None
    stamp = receipt_for_stage(fold, STAMP_STAGE, frozen_hash, real_map)
    return {
        "value_verdict": value_verdict,
        "value_accepted": value_verdict == "accept",
        "owner_stamped": bool(stamp) and stamp.get("verdict") == "accept",
    }


def resolve(name, root=DEFAULT_ROOT, fold=None):
    """Fold a named snapshot to its atoms (each frozen-hash vs live-hash), its
    commit, and the derived acceptance of each — and one snapshot-level verdict.

    The verdict is the most severe defect found, so a snapshot can be accepted
    `once as one thing` only when every atom resolves, is not stale, and has
    earned its independent acceptance:

      ghost      an atom names no resolvable atom file (the join is fiction)
      stale      an atom's live bytes != the hash the snapshot froze
      unaccepted an atom has not earned the value-gate's accept (or was refused)
      accepted   every atom resolves, is current, and is accepted

    Returns the dataset render() and --json share, or None when the name names
    no snapshot."""
    fold = fold or Fold(root)
    snaps = snapshots(fold)
    adm = snaps.get(name)
    if adm is None:
        return None
    real_map = real_nodes(fold)
    live = _atom_hashes(root)

    atoms = []
    ghost = stale = unaccepted = False
    for ref in adm.get("atoms", []):
        aid = ref.get("id")
        frozen = ref.get("frozen_hash")
        live_hash = live.get(aid)
        is_ghost = live_hash is None
        is_stale = (not is_ghost) and live_hash != frozen
        acc = _atom_acceptance(fold, frozen, real_map) if not is_ghost else {
            "value_verdict": None, "value_accepted": False, "owner_stamped": False}
        if is_ghost:
            ghost = True
        elif is_stale:
            stale = True
        elif not acc["value_accepted"]:
            unaccepted = True
        atoms.append({
            "id": aid,
            "frozen_hash": frozen,
            "live_hash": live_hash,
            "ghost": is_ghost,
            "stale": is_stale,
            **acc,
        })

    if ghost:
        verdict = "ghost"
        offenders = [a["id"] for a in atoms if a["ghost"]]
    elif stale:
        verdict = "stale"
        offenders = [a["id"] for a in atoms if a["stale"]]
    elif unaccepted:
        verdict = "unaccepted"
        offenders = [a["id"] for a in atoms if not a["value_accepted"]]
    else:
        verdict = "accepted"
        offenders = []

    return {
        "name": name,
        "commit": adm.get("commit"),
        "by": adm.get("by"),
        "ts": adm.get("ts"),
        "id": adm.get("id"),
        "atoms": atoms,
        "verdict": verdict,
        "offenders": offenders,
        "reason": _reason(verdict, offenders),
    }


def _reason(verdict, offenders):
    names = ", ".join(offenders)
    if verdict == "ghost":
        return (f"snapshot names atom(s) with no resolvable atom file: {names} "
                "— the join is fiction, the snapshot is not a real reference")
    if verdict == "stale":
        return (f"atom(s) edited since mint (live bytes != frozen hash): {names} "
                "— a frozen reference to bytes that changed; re-mint over the "
                "current atom version")
    if verdict == "unaccepted":
        return (f"atom(s) have not earned the value-gate's independent accept: "
                f"{names} — the snapshot cannot be accepted as one thing until "
                "each piece is")
    return "every named atom resolves, is current, and is accepted — the "\
           "snapshot can be accepted once as one thing"


def mint(root, name, atom_ids, commit, by, enabled=True, supersedes=None):
    """The one writer: record a snapshot binding (name -> atoms + commit),
    freezing each named atom's content-hash at mint time. Refuses a ghost
    binding (an atom with no resolvable atom file) at the door — the snapshot
    must be a real reference, not a wish. Returns the admission, or None on
    refusal (already printed). Any node may mint (a snapshot is a checkpoint,
    not an owner gesture); acceptance of it stays the pipeline's (D-2)."""
    if not (name or "").strip():
        print("result: needs-you — a snapshot needs a --name")
        return None
    if not (by or "").strip():
        print("result: needs-you — a snapshot records who minted it — pass --by")
        return None
    if not atom_ids:
        print("result: needs-you — a snapshot binds at least one --atoms <id>")
        return None
    live = _atom_hashes(root)
    missing = [a for a in atom_ids if a not in live]
    if missing:
        print(f"result: needs-you — refused: ghost binding — no atom file for "
              f"{', '.join(missing)} in {root / 'atoms'}; a snapshot must "
              "reference real atoms (mint over an atom that exists)")
        return None
    frozen = [{"id": a, "frozen_hash": live[a]} for a in atom_ids]
    adm = {
        "id": "adm." + short_hash(SNAPSHOT_TYPE, name, commit or "",
                                   str(enabled), str(by), now_ts()),
        "type": SNAPSHOT_TYPE,
        "name": name,
        "commit": (commit or "").strip() or None,
        "atoms": frozen,
        "enabled": bool(enabled),
        "by": by,
        "supersedes": supersedes,
        "ts": now_ts(),
    }
    append_line(root / "log" / "admissions.jsonl", adm)
    return adm


def dataset(root=DEFAULT_ROOT, fold=None):
    """The whole surface: every minted snapshot resolved."""
    fold = fold or Fold(root)
    names = sorted(snapshots(fold))
    return {"snapshots": [resolve(n, root, fold) for n in names]}


def _mark(verdict):
    return {"accepted": "✓", "stale": "⚠", "ghost": "✗", "unaccepted": "·"}.get(
        verdict, "?")


def render(root):
    d = dataset(root)
    snaps = d["snapshots"]
    lines = ["# Snapshots — the acceptance unit (the spine)", ""]
    if not snaps:
        lines += ["_no snapshot minted yet._", "",
                  "Mint one with: python -m loop.snapshot mint --name <n> "
                  "--atoms <id..> --commit <sha> --by <who>"]
        return "\n".join(lines)
    for s in snaps:
        lines.append(f"## {_mark(s['verdict'])} `{s['name']}` — **{s['verdict']}**")
        commit = (s["commit"] or "(no commit)")[:12]
        lines.append(f"- commit `{commit}` · minted by {s['by']} at {s['ts']}")
        for a in s["atoms"]:
            if a["ghost"]:
                state = "GHOST — no atom file"
            elif a["stale"]:
                state = "STALE — edited since mint"
            elif a["value_accepted"]:
                state = "accepted" + (" + owner-stamped" if a["owner_stamped"] else "")
            else:
                state = f"unaccepted (value verdict: {a['value_verdict'] or 'none'})"
            lines.append(f"  - `{a['id']}` — {state}")
        lines.append(f"  → {s['reason']}")
        lines.append("")
    lines.append("_read-only fold; the only writer is the `mint` pen. Acceptance "
                 "is derived from the pipeline's receipts, never a second "
                 "authority (D-4)._")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--json", action="store_true",
                    help="emit the raw dataset (machine-readable), not the prose")
    sub = ap.add_subparsers(dest="cmd")

    r = sub.add_parser("resolve", help="resolve one snapshot to its atoms + verdict")
    r.add_argument("--name", required=True)

    m = sub.add_parser("mint", help="record a snapshot binding (the one writer)")
    m.add_argument("--name", required=True)
    m.add_argument("--atoms", nargs="+", required=True,
                   help="the atom id(s) this snapshot freezes")
    m.add_argument("--commit", default=None, help="the landed commit sha (optional)")
    m.add_argument("--by", required=True, help="who minted it")
    m.add_argument("--off", action="store_true",
                   help="withdraw the snapshot (supersede)")
    m.add_argument("--supersedes", default=None)

    args = ap.parse_args(argv)

    if args.cmd == "mint":
        adm = mint(args.root, args.name, args.atoms, args.commit, args.by,
                   enabled=not args.off, supersedes=args.supersedes)
        if adm is None:
            return 1
        verb = "withdrawn" if args.off else "minted"
        print(f"result: done — snapshot {verb}: `{adm['name']}` over "
              f"{len(adm['atoms'])} atom(s) ({adm['id']})")
        return 0

    if args.cmd == "resolve":
        res = resolve(args.name, args.root)
        if res is None:
            print(f"result: needs-you — no snapshot named `{args.name}`")
            return 1
        if args.json:
            print(canon(res))
        else:
            print(f"snapshot `{res['name']}`: {res['verdict']} — {res['reason']}")
        return 0 if res["verdict"] == "accepted" else (
            0 if res["verdict"] == "unaccepted" else 1)

    # no subcommand: read-only status over all snapshots
    if args.json:
        print(canon(dataset(args.root)))
        return 0
    print(render(args.root))
    print()
    d = dataset(args.root)
    bad = [s for s in d["snapshots"] if s["verdict"] in ("stale", "ghost")]
    if bad:
        print(f"result: report — {len(bad)} snapshot(s) lie about their join "
              f"(stale/ghost); re-mint over the current atoms")
        return 0
    print(f"result: done — {len(d['snapshots'])} snapshot(s); none lie about "
          "their join")
    return 0


if __name__ == "__main__":
    sys.exit(main())
