#!/usr/bin/env python3
"""The fast ambient loop (doctrine §15; report 0002's v-next): a control
session that, each tick, folds the log, senses pressure against an admitted
setpoint, derives a step budget in either direction, and spends it through
the existing reconcile step.

Every actual move is still pass_once — one level-triggered step, idempotent
by (node, artifact_hash) (D-8, I-2). This loop only decides how many steps
to admit this tick and which atoms get them; it routes and makes no value
calls (D-3). It adds no new source of truth (D-5): pressure is a pure fold
over log/, the setpoint is an admitted record (I-8), and every tick is
itself an admitted line in log/admissions.jsonl.

Control is bidirectional (D-11), and cooling is the load-bearing direction
(I-7): too cold -> heat (seed unborn atoms, spend the budget); too hot ->
cool (shed inflow, defer the one step that enters the human queue). The
human stamp is the slow stage the cool path protects: the mocked human
clears at most human_rate stamps per tick, and the loop must hold the
stamp queue at or under its admitted cap without stalling the field.

Stdlib only. Ends with a clear result on stdout (D-6): done | report | needs-you.
"""

import argparse
import json
import sys
from pathlib import Path

from loop.reconcile import (DEFAULT_ROOT, DETERMINISTIC_GATE_NODES, PIPELINE,
                            SEED_EVENT, STAMP_NODE, TERMINAL_EVENT, Fold,
                            append_line, arc_confirmation, atom_state, canon,
                            epic_of, load_atoms, load_epics, now_ts, pass_once,
                            real_nodes, receipt_for_stage, short_hash)

SETPOINT_DIAL = "orchestration.temperature"
SETPOINT_KEYS = ("step_budget_per_tick", "max_inflight_atoms", "human_queue_cap")
HUMAN_NODE = "owner-stamp.mock-bdo.v0"
STAMP_STAGE = next(s for s in PIPELINE if s["node"] == HUMAN_NODE)
# the step that *enters* the human queue: announcing this event puts an atom
# in front of the (rate-limited) stamp — it is the valve the cool path closes
HUMAN_QUEUE_EVENT = "value.accepted"


def read_admissions(root):
    """Admissions are log, not cache: setpoint dials, realness, tick records
    — one fold, one dedup (Fold's)."""
    fold = Fold(root)
    return fold.admissions, fold.admissions_dropped


def read_setpoint(admissions):
    """The dial, read at runtime (I-8): the latest admitted setpoint wins
    (each admission supersedes, never mutates, the one before)."""
    setpoint = None
    for adm in admissions:
        if adm.get("type") == "setpoint" and adm.get("dial") == SETPOINT_DIAL:
            value = adm.get("value")
            if isinstance(value, dict) and all(k in value for k in SETPOINT_KEYS):
                setpoint = adm
    return setpoint


def admit_setpoint(root, value, by, supersedes=None, authorized_by=None,
                   because=None):
    """Append a setpoint admission. `by` is whoever stamps it (D-4: a node
    never admits its own dial).

    `authorized_by` cites a standing authorization the stamper is *executing*
    rather than originating — bdo's auto-admit fence (done-line 0091), the same
    way a merge-node landing cites the confirm-arc it did not author. When set,
    `by` is the loop's disposer identity and `authorized_by` is the fence id, so
    the record reads honestly: the loop moved the dial, bdo's fence authorized
    it. `because` carries the proposer's attribution (the outcomes that caused
    the change), keeping an auto-admitted dial move auditable to its cause."""
    adm = {
        "id": "adm." + short_hash(SETPOINT_DIAL, canon(value), str(by), now_ts()),
        "type": "setpoint",
        "dial": SETPOINT_DIAL,
        "value": value,
        "by": by,
        "supersedes": supersedes,
        "ts": now_ts(),
    }
    if authorized_by is not None:
        adm["authorized_by"] = authorized_by
    if because is not None:
        adm["because"] = because
    append_line(root / "log" / "admissions.jsonl", adm)
    return adm


def next_action(fold, atom, ahash, real_map=None, epics=None):
    """The one step pass_once would take for this atom — classified read-only,
    in pass_once's exact order (seed, then derive, then judge), so the
    controller can budget steps without acting. A pure fold.

    Returns ("seed"|"derive"|"judge"|"await"|"parked", target) or None when
    settled. "await" names a summoned real node the loop must not stand in
    for (D-2, D-10). With `epics` given, the owner's stamp on a confirmed arc
    is the loop's to take, not his — it classifies as "judge", not "await"
    (done-line 0028), so a confirmed arc's pieces never sit in his queue.

    Landed-is-not-closed (done-line 0154, retiring done-0133's settle-on-main):
    reaching main no longer settles an atom — a merge is not a delivery review,
    and "merged = done, no review" is the rubber-stamp value-confirm exists to
    forbid. Landed work flows on to value-confirm and is closed only by a real
    review verdict (the review queue, done-0150). `digest.atoms_on_main` is
    retained as the review's delivery EVIDENCE (read where the review composes),
    never a settle here.
    """
    if real_map is None:
        real_map = real_nodes(fold)
    if not fold.event(SEED_EVENT, ahash):
        return ("seed", SEED_EVENT)
    for stage in PIPELINE:
        rc = receipt_for_stage(fold, stage, ahash, real_map)
        if rc and rc.get("verdict") == stage["verdict"] and not fold.event(stage["next_event"], ahash):
            return ("derive", stage["next_event"])
    for stage in PIPELINE:
        ev = fold.event(stage["event"], ahash)
        if ev is None:
            break
        if receipt_for_stage(fold, stage, ahash, real_map) is None:
            if stage["node"] in real_map:
                real_node = real_map[stage["node"]]
                if epics is not None and stage["node"] == STAMP_NODE:
                    epic = epic_of(atom, epics)
                    if epic is not None and arc_confirmation(fold, epic["id"]) is not None:
                        return ("judge", real_node)
                # a deterministic real gate is a pure fold the loop runs itself
                # (done-line 0107) — never a summoned-node await, the same way a
                # confirmed arc's owner-stamp is the loop's to take.
                if real_node in DETERMINISTIC_GATE_NODES:
                    return ("judge", real_node)
                return ("await", real_node)
            return ("judge", stage["node"])
    if atom_state(fold, ahash) == atom["desired_state"] and fold.event(TERMINAL_EVENT, ahash):
        return None
    return ("parked", None)  # short of goal, nothing derivable: a needs-you, held


def _arc_auto_stampable(fold, atom, epics):
    """True when this atom's owner-stamp is the loop's to take, not the human's
    — its arc is confirmed (done-line 0028). The one predicate the scheduler and
    the backlog counter must agree on, or a confirmed arc's piece both fails to
    schedule and falsely inflates his queue (the first-light divergence)."""
    if epics is None:
        return False
    epic = epic_of(atom, epics)
    return epic is not None and arc_confirmation(fold, epic["id"]) is not None


def sense(fold, atoms, epics=None):
    """Field-state (§15): every signal a pure fold over the log — never a
    number the loop kept in memory. `epics` lets the field see a confirmed
    arc's stamp as the loop's to take (done-line 0028), so its pieces neither
    classify as 'await' nor count against his backlog."""
    pressure = {"unborn": 0, "inflight": 0, "settled": 0, "parked": 0,
                "awaiting": 0, "human_backlog": 0, "queue_depth": 0}
    real_map = real_nodes(fold)
    for atom, ahash in atoms:
        action = next_action(fold, atom, ahash, real_map, epics)
        if action is None:
            pressure["settled"] += 1
        elif action[0] == "seed":
            pressure["unborn"] += 1
        else:
            pressure["inflight"] += 1
            if action[0] == "parked":
                pressure["parked"] += 1
            elif action[0] == "await":
                pressure["awaiting"] += 1
        if (fold.event(HUMAN_QUEUE_EVENT, ahash)
                and receipt_for_stage(fold, STAMP_STAGE, ahash, real_map) is None
                and not _arc_auto_stampable(fold, atom, epics)):
            pressure["human_backlog"] += 1
        for stage in PIPELINE:
            if fold.event(stage["event"], ahash) and receipt_for_stage(fold, stage, ahash, real_map) is None:
                pressure["queue_depth"] += 1
    return pressure


def _rank(action):
    """Drain before feed: the further along an atom's next step, the earlier
    it is scheduled — so under cooling, downstream clears before upstream adds."""
    kind, target = action
    if kind == "seed":
        return -1
    for i, stage in enumerate(PIPELINE):
        if kind == "judge" and target == stage["node"]:
            return i * 2 + 1
        if kind == "derive" and target == stage["next_event"]:
            return i * 2 + 2
    return len(PIPELINE) * 2


def control(pressure, setpoint, fold, atoms, human_rate, epics=None):
    """The bidirectional law (D-11): map (pressure - setpoint) to this tick's
    spend. Heat is the default — spend the budget on whatever is short of
    goal. Cool closes the valves: no seeding past the cap, no announcement
    that would push the human queue over it, never more inflight than
    admitted. Cooling never blocks draining — stamps and downstream steps
    still run, which is what keeps the cool path from becoming a stall (I-7)."""
    sp = setpoint["value"]
    budget = int(sp["step_budget_per_tick"])
    cap = int(sp["human_queue_cap"])
    max_inflight = int(sp["max_inflight_atoms"])
    cooling = pressure["human_backlog"] >= cap
    projected_queue = pressure["human_backlog"]
    inflight = pressure["inflight"]
    human_spent = 0

    real_map = real_nodes(fold)
    field = []
    for atom, ahash in atoms:
        action = next_action(fold, atom, ahash, real_map, epics)
        if action is None or action[0] in ("parked", "await"):
            continue  # settled, held for a human, or held for a summoned node
        field.append((atom, ahash, action))
    field.sort(key=lambda t: (-_rank(t[2]), t[0]["id"]))

    scheduled, deferred = [], []
    for atom, ahash, (kind, target) in field:
        # the valves close on the projected field, before the budget is
        # consulted — a shed step is shed because the field is hot, and the
        # tick record should say so, not "budget spent"
        if kind == "judge" and target == HUMAN_NODE and human_spent >= human_rate:
            deferred.append({"atom": atom["id"], "why": "human at rate"})
            continue
        if kind == "derive" and target == HUMAN_QUEUE_EVENT and projected_queue >= cap:
            deferred.append({"atom": atom["id"], "why": "cool: human queue at cap"})
            continue
        if kind == "seed":
            if cooling or projected_queue >= cap:
                deferred.append({"atom": atom["id"], "why": "cool: inflow shed"})
                continue
            if inflight >= max_inflight:
                deferred.append({"atom": atom["id"], "why": "cool: max inflight"})
                continue
        if len(scheduled) >= budget:
            deferred.append({"atom": atom["id"], "why": "budget spent"})
            continue
        if kind == "judge" and target == HUMAN_NODE:
            human_spent += 1
            projected_queue -= 1
        elif kind == "derive" and target == HUMAN_QUEUE_EVENT:
            projected_queue += 1
        elif kind == "seed":
            inflight += 1
        scheduled.append((atom, ahash, kind, target))
    cooled = cooling or any(d["why"].startswith("cool") for d in deferred)
    return scheduled, deferred, cooled


def tick_record(n, pressure, setpoint, scheduled, deferred, cooled):
    steps = [{"atom": a["id"], "step": f"{k}:{t}"} for a, _, k, t in scheduled]
    return {
        # the id hashes the decision, not just the weather: two sessions can
        # sense identical pressure at the same tick number within one second,
        # and only a tick that also took the same steps is the same tick
        "id": "adm.tick." + short_hash(str(n), canon(pressure), canon(steps),
                                       canon(deferred), now_ts()),
        "type": "tick",
        "tick": n,
        "mode": "cool" if cooled else "heat",
        "pressure": pressure,
        "setpoint_id": setpoint["id"],
        "budget_spent": len(scheduled),
        "scheduled": steps,
        "deferred": deferred,
        "ts": now_ts(),
    }


def orchestrate(root, human_rate=1, max_ticks=200, quiet=False):
    """The fast loop: fold, sense, read the dial, derive the spend, spend it
    through pass_once, admit the tick. Terminal when every atom is settled
    (done) or nothing is schedulable (needs-you, parked for a human)."""
    for n in range(1, max_ticks + 1):
        fold = Fold(root)  # D-5: re-read truth every tick — never carry it
        atoms = load_atoms(root)
        if not atoms:
            print(f"result: needs-you — no atoms in {root / 'atoms'}")
            return 2
        setpoint = read_setpoint(fold.admissions)
        if setpoint is None:
            print("result: needs-you — no admitted setpoint for "
                  f"{SETPOINT_DIAL} (I-8: the dial is an admitted record, "
                  "not a default; admit one with --admit-setpoint)")
            return 2
        epics = load_epics(root)
        pressure = sense(fold, atoms, epics)
        scheduled, deferred, cooled = control(pressure, setpoint, fold, atoms, human_rate, epics)

        if not scheduled:
            if pressure["settled"] == len(atoms):
                print(f"result: done — {len(atoms)} atoms settled after {n - 1} ticks")
                return 0
            real_map = real_nodes(fold)
            waits = [f"{atom['id']} -> {action[1]}"
                     for atom, ahash in atoms
                     for action in [next_action(fold, atom, ahash, real_map, epics)]
                     if action and action[0] == "await"]
            print(f"result: needs-you — nothing schedulable: {canon(pressure)}"
                  + (f"; awaiting summons: {'; '.join(waits)}" if waits else ""))
            return 2

        for atom, ahash, kind, target in scheduled:
            pass_once(root, atom=atom, artifact_hash=ahash, quiet=True)
        append_line(root / "log" / "admissions.jsonl",
                    tick_record(n, pressure, setpoint, scheduled, deferred, cooled))
        if not quiet:
            steps = ", ".join(f"{a['id']}:{k}" for a, _, k, _ in scheduled)
            print(f"tick {n}: mode={'cool' if cooled else 'heat'} "
                  f"backlog={pressure['human_backlog']} inflight={pressure['inflight']} "
                  f"spent={len(scheduled)} deferred={len(deferred)} [{steps}]")
    print(f"result: needs-you — no convergence within {max_ticks} ticks")
    return 2


def field_status(root):
    fold = Fold(root)
    atoms = load_atoms(root)
    admissions, dropped = read_admissions(root)
    setpoint = read_setpoint(admissions)
    epics = load_epics(root)
    pressure = sense(fold, atoms, epics)
    ticks = [a for a in admissions if a.get("type") == "tick"]
    print(f"setpoint: {canon(setpoint['value']) if setpoint else 'NONE ADMITTED'}"
          + (f" (by {setpoint['by']}, {setpoint['id']})" if setpoint else ""))
    print(f"pressure: {canon(pressure)}")
    print(f"ticks admitted: {len(ticks)} (dropped lines: {dropped})")
    for atom, ahash in atoms:
        action = next_action(fold, atom, ahash, epics=epics)
        nxt = "settled" if action is None else f"{action[0]}:{action[1]}"
        print(f"  {atom['id']}: state={atom_state(fold, ahash)} next={nxt}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--admit-setpoint", metavar="JSON",
                    help='append a setpoint admission and exit, e.g. '
                         '\'{"step_budget_per_tick":3,"max_inflight_atoms":8,"human_queue_cap":2}\'')
    ap.add_argument("--by", help="who admits the setpoint (required with --admit-setpoint, D-4)")
    ap.add_argument("--human-rate", type=int, default=1,
                    help="mocked human stamps cleared per tick (the slow stage)")
    ap.add_argument("--max-ticks", type=int, default=200)
    ap.add_argument("--status", action="store_true", help="read-only field summary")
    args = ap.parse_args(argv)

    if args.admit_setpoint:
        if not args.by:
            print("result: needs-you — a setpoint is admitted *by* someone (--by), never self-set (D-4)")
            return 2
        value = json.loads(args.admit_setpoint)
        missing = [k for k in SETPOINT_KEYS if k not in value]
        if missing:
            print(f"result: needs-you — setpoint missing dials: {', '.join(missing)}")
            return 2
        adm = admit_setpoint(args.root, value, args.by)
        print(f"result: report — setpoint {adm['id']} admitted by {args.by}: {canon(value)}")
        return 0
    if args.status:
        return field_status(args.root)
    if args.human_rate < 1:
        print("result: needs-you — human_rate < 1 starves the slow stage: the queue could never drain")
        return 2
    return orchestrate(args.root, human_rate=args.human_rate, max_ticks=args.max_ticks)


if __name__ == "__main__":
    sys.exit(main())
