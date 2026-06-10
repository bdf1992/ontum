#!/usr/bin/env python3
"""Phase-1 loop skeleton (doctrine §11): a re-runnable reconcile pass over a file log.

The log is truth (D-5); queues/ and offsets/ are a cache, a pure fold over
log/ (§14.1). Every pass re-reads the log (level-triggered, D-8), moves the
one atom at most one step toward its desired_state, and never double-acts:
a node knows it already handled this version of an atom by its
content-hashed receipt (I-2). Appends are line-atomic with torn-tail
tolerance — a receipt that wasn't fully written didn't happen.

Stdlib only. No broker, no daemon, no network. Every invocation ends with a
clear result on stdout (D-6): done | report | needs-you.
"""

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

DEFAULT_ROOT = Path(".ai-native")

# The mocked pipeline (§14.2 subscriber examples). Each stage: the event a
# node subscribes to, the seam that event crosses, the subscriber, its fixed
# verdict, the event its receipt implies, and the atom state that receipt
# establishes. No node judges its own writer's work (D-2): the story author
# is a separate mock, and every gate below reads someone else's output.
# owner-stamp.mock-bdo stands in for bdo (D-4) for the mocked loop ONLY; it
# must be the first mock replaced when any node becomes real.
PIPELINE = [
    {"event": "atom.created", "seam": "author-to-value",
     "node": "value-gate.mock.v0", "verdict": "accept",
     "reason": "mock L0: fixed accept (phase-1 skeleton)",
     "next_event": "value.accepted", "state": "value_accepted",
     "terminal_expected": ["accept", "reject_no_value", "reject_wrong_value", "amend"]},
    {"event": "value.accepted", "seam": "value-to-owner-stamp",
     "node": "owner-stamp.mock-bdo.v0", "verdict": "accept",
     "reason": "mock owner stamp standing in for bdo (mocked loop only)",
     "next_event": "story.accepted", "state": "story_accepted",
     "terminal_expected": ["accept", "reject_no_value", "reject_wrong_value", "amend"]},
    {"event": "story.accepted", "seam": "value-to-placement",
     "node": "placement-gate.mock.v0", "verdict": "sound",
     "reason": "mock L1: fixed sound (phase-1 skeleton)",
     "next_event": "placement.sound", "state": "placement_sound",
     "terminal_expected": ["sound", "collision", "wrong_seam", "halt_for_human"]},
    {"event": "placement.sound", "seam": "placement-to-handoff",
     "node": "handoff-gate.mock.v0", "verdict": "ready_for_spec",
     "reason": "mock L2: fixed ready_for_spec (phase-1 skeleton)",
     "next_event": "handoff.ready", "state": "handoff_ready",
     "terminal_expected": ["ready_for_spec", "send_back"]},
    {"event": "handoff.ready", "seam": "handoff-to-confirm",
     "node": "value-confirm.mock.v0", "verdict": "confirmed",
     "reason": "mock L0 second check: fixed confirmed (phase-1 skeleton)",
     "next_event": "atom.value_confirmed", "state": "value_confirmed",
     "terminal_expected": ["confirmed", "missed"]},
]
SEED_EVENT = "atom.created"
SEED_NODE = "value-loop.story-author.mock.v0"
TERMINAL_EVENT = "atom.value_confirmed"
TERMINAL_SEAM = "confirm-to-owner"


def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def short_hash(*parts):
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:12]


def now_ts():
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + "Z"


def append_line(path, obj):
    """Whole line + newline, flush + fsync (line-atomic append).

    If the file's tail is torn (no trailing newline), close the torn line
    first so a new append can never merge into it — the torn fragment stays
    an unparseable line the fold drops, i.e. it never happened.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a+b") as f:
        f.seek(0, os.SEEK_END)
        if f.tell() > 0:
            f.seek(-1, os.SEEK_END)
            if f.read(1) != b"\n":
                f.write(b"\n")
        f.write(canon(obj).encode("utf-8") + b"\n")
        f.flush()
        os.fsync(f.fileno())


def read_jsonl(path):
    """Fold input: parse line records, dropping unparseable lines.

    A torn final line (or any garbage line) is dropped — a record that
    wasn't fully written didn't happen; the next pass re-derives.
    """
    records, dropped = [], 0
    if not path.exists():
        return records, dropped
    for line in path.read_bytes().decode("utf-8", errors="replace").split("\n"):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except ValueError:
            dropped += 1
    return records, dropped


class Fold:
    """The state of the world is this fold over log/ — never the cache."""

    def __init__(self, root):
        self.events_raw, self.events_dropped = read_jsonl(root / "log" / "events.jsonl")
        self.receipts_raw, self.receipts_dropped = read_jsonl(root / "log" / "receipts.jsonl")
        # dedup by id, first occurrence wins (replay-safe)
        self.events, seen = [], set()
        for ev in self.events_raw:
            if isinstance(ev, dict) and ev.get("id") and ev["id"] not in seen:
                seen.add(ev["id"])
                self.events.append(ev)
        self.receipts, seen = [], set()
        for rc in self.receipts_raw:
            if isinstance(rc, dict) and rc.get("id") and rc["id"] not in seen:
                seen.add(rc["id"])
                self.receipts.append(rc)

    def event(self, type_, artifact_hash):
        for ev in self.events:
            if ev.get("type") == type_ and ev.get("artifact_hash") == artifact_hash:
                return ev
        return None

    def receipt_by_node(self, node, artifact_hash):
        """The I-2 idempotence key: (node, artifact_hash)."""
        for rc in self.receipts:
            if rc.get("node") == node and rc.get("artifact_hash") == artifact_hash:
                return rc
        return None


def load_atoms(root):
    """The field: every atom in atoms/, each with its content hash."""
    out = []
    for path in sorted((root / "atoms").glob("*.json")):
        raw = path.read_bytes()
        atom = json.loads(raw)["atom"]
        out.append((atom, "sha256:" + hashlib.sha256(raw).hexdigest()))
    return out


def load_atom(root):
    """The single-atom (phase-1) driver's loader; the orchestrator uses load_atoms."""
    atoms = load_atoms(root)
    if len(atoms) != 1:
        raise SystemExit(f"result: needs-you — expected exactly one atom in {root / 'atoms'}, found {len(atoms)}")
    return atoms[0]


def make_event(type_, seam, from_node, atom_id, artifact_hash, requires, terminal_expected):
    return {
        "id": "evt." + short_hash(type_, atom_id, artifact_hash),
        "type": type_,
        "artifact_id": atom_id,
        "artifact_hash": artifact_hash,
        "from_node": from_node,
        "seam": seam,
        "requires": requires,
        "visible_to": sorted(set(requires) | {"surfacer", "reconcile-controller"}),
        "terminal_expected": terminal_expected,
        "ts": now_ts(),
    }


def make_receipt(event, stage, atom_id, artifact_hash):
    return {
        "id": "rcp." + short_hash(stage["node"], atom_id, artifact_hash, event["id"]),
        "event_id": event["id"],
        "node": stage["node"],
        "artifact_id": atom_id,
        "artifact_hash": artifact_hash,
        "verdict": stage["verdict"],
        "reason": stage["reason"],
        "next_suggested_event": stage["next_event"],
        "ts": now_ts(),
    }


def atom_state(fold, artifact_hash):
    """Walk the pipeline: state is what the receipts establish, in order."""
    if not fold.event(SEED_EVENT, artifact_hash):
        return "unborn"
    state = "created"
    for stage in PIPELINE:
        rc = fold.receipt_by_node(stage["node"], artifact_hash)
        if rc and rc.get("verdict") == stage["verdict"]:
            state = stage["state"]
        else:
            break
    return state


def rebuild_cache(root, fold, artifact_hashes):
    """queues/ and offsets/ are a pure fold over log/ — rebuilt from scratch
    each time, byte-deterministic, so deletion + replay is always lossless."""
    if isinstance(artifact_hashes, str):
        artifact_hashes = [artifact_hashes]
    qdir, odir = root / "queues", root / "offsets"
    qdir.mkdir(parents=True, exist_ok=True)
    odir.mkdir(parents=True, exist_ok=True)
    event_index = {ev["id"]: i + 1 for i, ev in enumerate(fold.events)}
    for stage in PIPELINE:
        pending = []
        for artifact_hash in artifact_hashes:
            ev = fold.event(stage["event"], artifact_hash)
            if ev is not None and fold.receipt_by_node(stage["node"], artifact_hash) is None:
                pending.append(ev)
        (qdir / f"{stage['seam']}.pending.jsonl").write_text(
            "".join(canon(ev) + "\n" for ev in pending), encoding="utf-8")
        receipted = [event_index[rc["event_id"]] for rc in fold.receipts
                     if rc.get("node") == stage["node"] and rc.get("event_id") in event_index]
        (odir / f"{stage['node']}.offset").write_text(f"{max(receipted, default=0)}\n", encoding="utf-8")


def pass_once(root, pace=0.0, quiet=False, atom=None, artifact_hash=None):
    """One reconcile pass: re-read the log, move the atom at most one step.

    With no atom given, the single atom in atoms/ is loaded (the phase-1
    driver). The orchestrator hands in which atom to advance; everything
    below keys on artifact_hash, so many atoms share one log safely.

    The pass asks §14.4's questions, each time:
      1. What goal state does this atom want?
      2. What events have been announced?
      3. What receipts exist?
      4. What is missing?
      5. Which seam should receive the next event?
    """
    if atom is None:
        atom, artifact_hash = load_atom(root)
    desired = atom["desired_state"]
    fold = Fold(root)

    step = None
    next_seam = None
    if pace:
        time.sleep(pace)

    if not fold.event(SEED_EVENT, artifact_hash):
        # missing: the atom's birth announcement
        stage0 = PIPELINE[0]
        append_line(root / "log" / "events.jsonl", make_event(
            SEED_EVENT, stage0["seam"], SEED_NODE, atom["id"], artifact_hash,
            [stage0["node"]], stage0["terminal_expected"]))
        step = f"announced {SEED_EVENT} (seed, from {SEED_NODE})"
        next_seam = stage0["seam"]
    else:
        # missing: an event a receipt already implies (repair before new work)
        for i, stage in enumerate(PIPELINE):
            rc = fold.receipt_by_node(stage["node"], artifact_hash)
            if rc and rc.get("verdict") == stage["verdict"] and not fold.event(stage["next_event"], artifact_hash):
                if stage["next_event"] == TERMINAL_EVENT:
                    seam, requires, terminal = TERMINAL_SEAM, [], []
                else:
                    nxt = PIPELINE[i + 1]
                    seam, requires, terminal = nxt["seam"], [nxt["node"]], nxt["terminal_expected"]
                append_line(root / "log" / "events.jsonl", make_event(
                    stage["next_event"], seam, stage["node"], atom["id"], artifact_hash,
                    requires, terminal))
                step = f"derived {stage['next_event']} from receipt {rc['id']}"
                next_seam = seam
                break
        if step is None:
            # missing: the receipt for the first announced-but-unjudged event
            for stage in PIPELINE:
                ev = fold.event(stage["event"], artifact_hash)
                if ev is None:
                    break
                if fold.receipt_by_node(stage["node"], artifact_hash) is not None:
                    continue  # already handled this version of the atom (I-2): skip
                append_line(root / "log" / "receipts.jsonl",
                            make_receipt(ev, stage, atom["id"], artifact_hash))
                step = f"{stage['node']} judged {stage['event']} -> {stage['verdict']}"
                next_seam = stage["seam"]
                break

    fold = Fold(root)  # re-read: the log, not our memory, is what happened
    rebuild_cache(root, fold, [h for _, h in load_atoms(root)])
    state = atom_state(fold, artifact_hash)

    if state == desired and fold.event(TERMINAL_EVENT, artifact_hash):
        result = "done"
    elif step:
        result = "report"
    else:
        result = "needs-you"  # short of goal with nothing derivable: escalate (D-6)

    if not quiet:
        torn = fold.events_dropped + fold.receipts_dropped
        print(f"pass: goal={desired} state={state} events={len(fold.events)} "
              f"receipts={len(fold.receipts)} dropped_lines={torn} "
              f"step={step or 'none'} next_seam={next_seam or '-'}")
        print(f"result: {result} — atom {atom['id']} at {state}, desired {desired}")
    return result, state, step


def until_done(root, pace=0.0, max_passes=50):
    for _ in range(max_passes):
        result, state, step = pass_once(root, pace=pace)
        if result == "done":
            return 0
        if result == "needs-you":
            return 2
    print(f"result: needs-you — no convergence within {max_passes} passes")
    return 2


def status(root):
    entries = load_atoms(root)
    fold = Fold(root)
    print(f"atoms: {len(entries)}")
    print(f"events: {len(fold.events)} (dropped lines: {fold.events_dropped})")
    print(f"receipts: {len(fold.receipts)} (dropped lines: {fold.receipts_dropped})")
    for atom, artifact_hash in entries:
        state = atom_state(fold, artifact_hash)
        print(f"atom: {atom['id']}")
        print(f"  artifact_hash: {artifact_hash}")
        print(f"  state: {state} (desired: {atom['desired_state']})")
        for rc in fold.receipts:
            if rc.get("artifact_hash") == artifact_hash:
                print(f"  {rc['node']}: {rc['verdict']} ({rc['id']})")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--until-done", action="store_true", help="run passes until done or stuck")
    ap.add_argument("--pace", type=float, default=0.0, help="seconds slept inside each pass (test aid)")
    ap.add_argument("--rebuild-cache-only", action="store_true", help="replay: rebuild queues/+offsets/ from log/, mutate nothing else")
    ap.add_argument("--status", action="store_true", help="read-only fold summary")
    args = ap.parse_args(argv)

    if args.status:
        return status(args.root)
    if args.rebuild_cache_only:
        rebuild_cache(args.root, Fold(args.root), [h for _, h in load_atoms(args.root)])
        print("result: report — cache rebuilt from log/ (fold only, no mutation)")
        return 0
    if args.until_done:
        return until_done(args.root, pace=args.pace)
    result, _, _ = pass_once(args.root, pace=args.pace)
    return {"done": 0, "report": 0}.get(result, 2)


if __name__ == "__main__":
    sys.exit(main())
