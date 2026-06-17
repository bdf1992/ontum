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
import re
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
# The owner's stamp stage — bdo's gate. When the atom's arc is confirmed, the
# loop satisfies this stamp under his standing confirmation (done-line 0028).
STAMP_NODE = next(s["node"] for s in PIPELINE if s["seam"] == "value-to-owner-stamp")


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


def dedup_by_id(records):
    """First occurrence wins (replay-safe)."""
    out, seen = [], set()
    for rec in records:
        if isinstance(rec, dict) and rec.get("id") and rec["id"] not in seen:
            seen.add(rec["id"])
            out.append(rec)
    return out


class Fold:
    """The state of the world is this fold over log/ — never the cache."""

    def __init__(self, root):
        self.events_raw, self.events_dropped = read_jsonl(root / "log" / "events.jsonl")
        self.receipts_raw, self.receipts_dropped = read_jsonl(root / "log" / "receipts.jsonl")
        self.admissions_raw, self.admissions_dropped = read_jsonl(root / "log" / "admissions.jsonl")
        self.events = dedup_by_id(self.events_raw)
        self.receipts = dedup_by_id(self.receipts_raw)
        self.admissions = dedup_by_id(self.admissions_raw)

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


def real_nodes(fold):
    """Which stages are judged by a real node, read from admitted records
    (I-8) — never a code literal. Latest node_real admission per stage wins;
    a null real_node reverts the stage to its mock."""
    real = {}
    for adm in fold.admissions:
        if adm.get("type") == "node_real" and adm.get("stage_node"):
            if adm.get("real_node"):
                real[adm["stage_node"]] = adm["real_node"]
            else:
                real.pop(adm["stage_node"], None)
    return real


def arc_confirmation(fold, epic_id):
    """The active arc_confirmed admission for an epic, or None (done-line 0028).

    bdo confirming an arc once is a standing pre-authorization: every piece
    under that epic clears the owner's stamp on his confirmation, and he is
    escalated only on a gate's refusal or the arc's completion — he steers
    arcs, the loop carries pieces. Latest admission per epic wins; an
    `enabled: false` one withdraws the confirmation (superseded, never
    erased)."""
    active = None
    for adm in fold.admissions:
        if adm.get("type") == "arc_confirmed" and adm.get("epic") == epic_id:
            active = adm if adm.get("enabled", True) else None
    return active


def active_mode(fold, session):
    """The security posture in force for a session — "normal" by default,
    read from admitted records (never a constant), latest-enabled-wins like
    real_nodes/arc_confirmation (done-line 0096).

    train is the first security MODE: observe-everything / block-nothing. A
    `security_mode` admission is bdo's signed open/close switch (see
    loop.node.mode_train); it is scoped to a concrete session_id or "*"
    (global). The latest matching admission wins; an `enabled: false` one
    closes the posture back to "normal" (superseded, never erased).

    A mode only ever RELAXES the guard, so the safe default is the strict
    one: an unreadable or absent fold returns "normal". train can never
    silently un-guard — its absence is information, not permission. Returns
    (posture, opening_admission_id): the id is None under "normal"."""
    posture, opener = "normal", None
    try:
        for adm in fold.admissions:
            if adm.get("type") != "security_mode":
                continue
            scope = adm.get("session")
            if scope != "*" and scope != session:
                continue
            if adm.get("enabled", True):
                posture, opener = adm.get("mode", "normal"), adm.get("id")
            else:
                posture, opener = "normal", None
    except Exception:  # noqa: BLE001 — an unreadable fold stays strict, never relaxes
        return "normal", None
    return posture, opener


def receipt_for_stage(fold, stage, artifact_hash, real_map=None):
    """The receipt that satisfies a stage: from the stage's mock node, or
    from its admitted real node. History is never retro-invalidated (D-5):
    a receipt valid when written stays valid after realness is admitted."""
    if real_map is None:
        real_map = real_nodes(fold)
    rc = fold.receipt_by_node(stage["node"], artifact_hash)
    if rc is None and stage["node"] in real_map:
        rc = fold.receipt_by_node(real_map[stage["node"]], artifact_hash)
    return rc


def load_atoms(root):
    """The field: every atom in atoms/, each with its content hash."""
    out = []
    for path in sorted((root / "atoms").glob("*.json")):
        raw = path.read_bytes()
        atom = json.loads(raw)["atom"]
        out.append((atom, "sha256:" + hashlib.sha256(raw).hexdigest()))
    return out


_VERSION = re.compile(r"^(?P<stem>.+)\.v(?P<n>\d+)$")


def atom_version(atom_id):
    """Split an atom id into ``(stem, version)``. Ids carry a ``.v<N>``
    suffix by convention (`atom.field-topology.v0`); an id that does not
    match is its own stem at version -1 — it can never be read as
    superseded, only as superseding (done-line 0056)."""
    m = _VERSION.match(atom_id)
    if not m:
        return atom_id, -1
    return m.group("stem"), int(m.group("n"))


def superseded_atom_ids(atom_ids):
    """The ids a higher version of the same stem replaces (done-line 0056).
    Editing an atom mints a new version that restarts the pipeline from
    scratch — creating the new version *is* the amend, so the lower one is
    no longer live work (its receipts "stay valid history but no longer
    apply", see the identity-is-content-hash architecture note). This reads
    only the version suffix already on disk; it retires nothing and writes
    nothing — history is untouched, only what counts as *live* changes."""
    latest = {}
    for aid in atom_ids:
        stem, ver = atom_version(aid)
        if stem not in latest or ver > latest[stem][1]:
            latest[stem] = (aid, ver)
    live = {aid for aid, _ in latest.values()}
    return {aid for aid in atom_ids if aid not in live}


def load_atom(root):
    """The single-atom (phase-1) driver's loader; the orchestrator uses load_atoms."""
    atoms = load_atoms(root)
    if len(atoms) != 1:
        raise SystemExit(f"result: needs-you — expected exactly one atom in {root / 'atoms'}, found {len(atoms)}")
    return atoms[0]


def load_epics(root):
    """The arcs bdo steers (done-line 0006): first-class records read like
    atoms — the file is truth for what an epic claims, the log for what its
    pieces have earned."""
    out = []
    edir = root / "epics"
    if not edir.exists():
        return out
    for path in sorted(edir.glob("*.json")):
        out.append(json.loads(path.read_bytes())["epic"])
    return out


def epic_of(atom, epics):
    """An atom files under an epic via its own incidence.serves, or via the
    epic's pieces list — the latter lets settled atoms retro-file without
    re-judging (the epic points at them; their hashes never move)."""
    serves = set(atom.get("incidence", {}).get("serves", []))
    for epic in epics:
        if epic["id"] in serves:
            return epic
        if any(p.get("atom") == atom["id"] for p in epic.get("pieces", [])):
            return epic
    return None


def glue_of(atom, epic):
    """How this local piece composes into the arc, in the epic's words."""
    for piece in (epic or {}).get("pieces", []):
        if piece.get("atom") == atom["id"]:
            return piece.get("glue")
    return None


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


def make_receipt(event, stage, atom_id, artifact_hash, node=None, verdict=None, reason=None,
                 prompt_hash=None):
    """Defaults are the stage's mock; a summoned real node passes its own
    identity, verdict, and reason. A non-advancing verdict suggests no next
    event — the atom parks for a human (D-4). prompt_hash, when a versioned
    node prompt was in force (§7), makes the verdict attributable to the
    exact prompt that judged; it never enters the receipt id, so a prompt
    edit can't reopen a settled verdict (I-2)."""
    node = node or stage["node"]
    verdict = verdict if verdict is not None else stage["verdict"]
    reason = reason if reason is not None else stage["reason"]
    rc = {
        "id": "rcp." + short_hash(node, atom_id, artifact_hash, event["id"]),
        "event_id": event["id"],
        "node": node,
        "artifact_id": atom_id,
        "artifact_hash": artifact_hash,
        "verdict": verdict,
        "reason": reason,
        "next_suggested_event": stage["next_event"] if verdict == stage["verdict"] else None,
        "ts": now_ts(),
    }
    if prompt_hash:
        rc["prompt_hash"] = prompt_hash
    return rc


def node_prompt(root, node):
    """The node's versioned prompt (§7): .ai-native/nodes/<node>.md, hashed
    over bytes like every identity here. Returns (text, "sha256:<hash>") or
    (None, None) — absence is information, not an error: a node without a
    prompt file judges on its summons alone."""
    path = root / "nodes" / f"{node}.md"
    if not path.exists():
        return None, None
    data = path.read_bytes()
    return data.decode("utf-8"), "sha256:" + hashlib.sha256(data).hexdigest()


def atom_state(fold, artifact_hash):
    """Walk the pipeline: state is what the receipts establish, in order."""
    if not fold.event(SEED_EVENT, artifact_hash):
        return "unborn"
    state = "created"
    real_map = real_nodes(fold)
    for stage in PIPELINE:
        rc = receipt_for_stage(fold, stage, artifact_hash, real_map)
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
    real_map = real_nodes(fold)
    for stage in PIPELINE:
        pending = []
        for artifact_hash in artifact_hashes:
            ev = fold.event(stage["event"], artifact_hash)
            if ev is not None and receipt_for_stage(fold, stage, artifact_hash, real_map) is None:
                pending.append(ev)
        (qdir / f"{stage['seam']}.pending.jsonl").write_text(
            "".join(canon(ev) + "\n" for ev in pending), encoding="utf-8")
        stage_nodes = {stage["node"], real_map.get(stage["node"])}
        receipted = [event_index[rc["event_id"]] for rc in fold.receipts
                     if rc.get("node") in stage_nodes and rc.get("event_id") in event_index]
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

    real_map = real_nodes(fold)
    step = None
    next_seam = None
    awaited = None
    if pace:
        time.sleep(pace)

    if not fold.event(SEED_EVENT, artifact_hash):
        # missing: the atom's birth announcement. The author seat de-mocks
        # like any stage (done-line 0049): a node_real admission naming
        # SEED_NODE puts the admitted author on every seed from then on.
        stage0 = PIPELINE[0]
        author = real_map.get(SEED_NODE, SEED_NODE)
        append_line(root / "log" / "events.jsonl", make_event(
            SEED_EVENT, stage0["seam"], author, atom["id"], artifact_hash,
            [stage0["node"]], stage0["terminal_expected"]))
        step = f"announced {SEED_EVENT} (seed, from {author})"
        next_seam = stage0["seam"]
    else:
        # missing: an event a receipt already implies (repair before new work)
        for i, stage in enumerate(PIPELINE):
            rc = receipt_for_stage(fold, stage, artifact_hash, real_map)
            if rc and rc.get("verdict") == stage["verdict"] and not fold.event(stage["next_event"], artifact_hash):
                if stage["next_event"] == TERMINAL_EVENT:
                    seam, requires, terminal = TERMINAL_SEAM, [], []
                else:
                    nxt = PIPELINE[i + 1]
                    seam, requires, terminal = nxt["seam"], [nxt["node"]], nxt["terminal_expected"]
                append_line(root / "log" / "events.jsonl", make_event(
                    stage["next_event"], seam, rc["node"], atom["id"], artifact_hash,
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
                if receipt_for_stage(fold, stage, artifact_hash, real_map) is not None:
                    continue  # already handled this version of the atom (I-2): skip
                if stage["node"] in real_map:
                    # an admitted-real stage is judged by a summoned node,
                    # never by this loop (D-2, D-10): park and name who —
                    # UNLESS this is the owner's stamp and the atom's arc is
                    # confirmed, where bdo's standing confirmation IS the stamp
                    # (done-line 0028: he steers arcs, the loop carries pieces).
                    confirmation, epic = None, None
                    if stage["node"] == STAMP_NODE:
                        epic = epic_of(atom, load_epics(root))
                        if epic is not None:
                            confirmation = arc_confirmation(fold, epic["id"])
                    if confirmation is None:
                        awaited = real_map[stage["node"]]
                        next_seam = stage["seam"]
                        break
                    rc = make_receipt(
                        ev, stage, atom["id"], artifact_hash,
                        node=real_map[stage["node"]], verdict=stage["verdict"],
                        reason=(f"arc {epic['id']} confirmed by {confirmation['by']} "
                                f"({confirmation['id']}) — the owner's standing stamp"))
                    rc["authorized_by"] = confirmation["id"]
                    append_line(root / "log" / "receipts.jsonl", rc)
                    step = (f"{real_map[stage['node']]} stamped {stage['event']} -> "
                            f"{stage['verdict']} on bdo's confirmed arc {epic['id']}")
                    next_seam = stage["seam"]
                    break
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
        print(f"result: {result} — atom {atom['id']} at {state}, desired {desired}"
              + (f" (awaiting summoned node {awaited})" if awaited else ""))
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
