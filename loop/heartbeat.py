#!/usr/bin/env python3
"""The loop's guaranteed-tick heartbeat (done-line 0178, epic.virtual-fleet).

The value-confirm review queue (done-0150) and the no-settle-on-landing rule
(done-0154) shipped, and the headless review consumer was fixed (#411). But the
loop is level-triggered with **no guaranteed driver** — nothing ticks it — so
atoms sit at `derive:value.accepted` and never reach the real value-confirm
gate; inflight piled to ~57 against a cap of 8. A level-triggered loop without a
guaranteed beat is a clog by construction: the consumer is correct, but nobody
is turning the crank.

This is the crank. One `beat` is one bounded cycle:

  (1) TICK — one setpoint-bounded pass, by reusing `loop.orchestrate`'s existing
      tick (`orchestrate`, run for a single tick). It does NOT reimplement the
      pipeline; it borrows it. This flows confirmed-arc atoms toward
      value-confirm and parks the rest.
  (2) DRAIN — only when `drain_limit > 0`: fire at most `drain_limit` REAL
      value-confirm reviews through the gate pen's `drain` (`gate.py`). Default
      `drain_limit=0` (tick-only), so the cheap, always-safe path never fires
      an expensive headless review.

Why ticking is SAFE (the whole reason this can be a guaranteed, unattended
beat): `owner-stamp.bdo.v1` and `value-confirm.claude.v1` are BOTH admitted
real. So a tick (a) advances a **confirmed-arc** atom — its owner-stamp is
satisfied by bdo's standing arc confirmation (done-0028), the loop executes his
stamp, it never invents one; (b) PARKS an **unconfirmed** atom at the real
owner-stamp — there is no mock human in the loop, and the beat shuts the mock
human valve outright (`human_rate=0`), so an unconfirmed atom can NEVER be
fake-stamped; (c) PARKS an atom that reaches the terminal at the real
value-confirm gate — a merge never auto-settles it (done-0154), only a real
review does. No fake-stamp, no auto-settle, no leak.

Idempotent + level-triggered: the beat re-derives everything from the log each
time. Nothing pending means nothing scheduled means nothing written — a no-op
beat touches no bytes. A review that failed or returned no verdict simply leaves
its atom in the queue for the next beat. That pairing is what makes the tick a
*guarantee* rather than a one-shot.

Two surfaces consume it:
  * the in-harness tick — `--hook`, tick-only and fail-open, wired to
    SessionStart so every session that opens nudges the loop once; it can never
    raise or block a session (exit 0 always);
  * the ambient paced consumer — bdo's activation gesture, an external
    scheduler running `python -m loop.heartbeat --drain-limit N --by
    heartbeat.v0` every few minutes from the repo root, the paced drain that
    burns the backlog down with real reviews (see the done-line for the exact
    Task Scheduler command).

Stdlib only; local-first; the loop/ law. Ends with a clear result on stdout
(D-6): done | report | needs-you.
"""

import argparse
import contextlib
import importlib.util
import io
import sys
from pathlib import Path

from loop import orchestrate, reconcile
from loop.reconcile import DEFAULT_ROOT

# The mock-human valve is shut, always. With the owner-stamp admitted real, a
# confirmed arc's stamp is taken by the loop on bdo's standing confirmation and
# an unconfirmed arc's stamp PARKS — neither path uses the mock human. Pinning
# human_rate to 0 makes "never fake-stamp" structural: even if the owner-stamp
# were ever mock again, the beat could not auto-stamp through it.
HEARTBEAT_HUMAN_RATE = 0

# Where the gate pen lives — it reaches the network (gh) and launches minds, so
# it stays under .claude/, never imported into pure-stdlib loop/. The beat only
# *delegates* to it, and only when actually draining (drain_limit > 0).
_GATE_PY = (Path(__file__).resolve().parents[1]
            / ".claude" / "skills" / "gate" / "gate.py")


def _load_gate():
    """Load the gate pen as a module (it is a script under .claude/, not a
    package). Lazy: only the drain path needs it, so the cheap tick-only beat
    never touches the network-reaching pen."""
    spec = importlib.util.spec_from_file_location("gate_pen", _GATE_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _tick_admissions(root):
    """The set of tick-admission ids on the log right now (a pure fold). The
    diff across a beat tells us which tick this beat appended — and its
    `budget_spent` is exactly how many steps the beat advanced."""
    return {a["id"]: a for a in reconcile.Fold(root).admissions
            if a.get("type") == "tick"}


def beat(root, drain_limit=0, by="heartbeat.v0", review=None,
         human_rate=HEARTBEAT_HUMAN_RATE):
    """Run ONE guaranteed cycle: tick, then (optionally) drain. Returns a
    summary dict {advanced, settled, drained, parked}.

    `review(records_root, atom_id, node_id, by)` is injectable and forwarded to
    the gate pen's drain so a test drives the queue without a live spawn; in
    production it is None and the drain fires the real trust-railed launch.

    Pure-ish: it reads the log, advances at most one setpoint-bounded tick
    through `orchestrate`, and (only if asked) fires at most `drain_limit` real
    reviews. It prints nothing itself — `orchestrate`'s own stdout is captured —
    so callers (CLI, hook, test) decide what to surface."""
    summary = {"advanced": 0, "settled": 0, "drained": 0, "parked": 0}

    # (1) TICK — reuse orchestrate's existing tick for a single bounded pass.
    # max_ticks=1 means one tick; orchestrate writes at most one tick admission
    # (and writes none at all when nothing is schedulable — the idempotent
    # no-op). Its stdout (the trailing result line) is captured: the beat is a
    # function, not a printer.
    before = _tick_admissions(root)
    with contextlib.redirect_stdout(io.StringIO()):
        orchestrate.orchestrate(root, human_rate=human_rate, max_ticks=1,
                                quiet=True)
    after = _tick_admissions(root)
    new_ticks = [after[i] for i in after if i not in before]
    summary["advanced"] = sum(int(t.get("budget_spent", 0)) for t in new_ticks)

    # the post-tick field, re-derived from the log (level-triggered): how many
    # atoms are settled, how many are held (parked short of goal or awaiting a
    # summoned real node — the value-confirm queue lives here).
    fold = reconcile.Fold(root)
    atoms = reconcile.load_atoms(root)
    epics = reconcile.load_epics(root)
    pressure = orchestrate.sense(fold, atoms, epics)
    summary["settled"] = pressure["settled"]
    summary["parked"] = pressure["parked"] + pressure["awaiting"]

    # (2) DRAIN — only when explicitly asked. The default beat (drain_limit=0)
    # never fires an expensive headless review; the paced external consumer
    # passes a positive limit. The gate pen owns the rail and the I-2 idempotence
    # (a judged atom is no longer in the queue), so a re-fire is a no-op.
    if drain_limit and drain_limit > 0:
        fired = _load_gate().drain(root, by=by, limit=drain_limit, review=review)
        summary["drained"] = len(fired)

    return summary


def _has_setpoint(root):
    """Whether a setpoint dial is admitted — the tick is inert without one
    (orchestrate's own rule: the dial is an admitted record, not a default)."""
    return orchestrate.read_setpoint(reconcile.Fold(root).admissions) is not None


def run(root, drain_limit=0, by="heartbeat.v0"):
    """The CLI beat: run one cycle and report. needs-you when no setpoint is
    admitted (nothing can tick); report when something moved; done when the
    field is quiescent (a clean idempotent no-op)."""
    if not _has_setpoint(root):
        print("result: needs-you — no admitted setpoint for "
              f"{orchestrate.SETPOINT_DIAL}: the dial is an admitted record, not "
              "a default (admit one via `python -m loop.orchestrate "
              "--admit-setpoint ... --by bdo`). The heartbeat cannot tick a loop "
              "with no setpoint.")
        return 2
    s = beat(root, drain_limit=drain_limit, by=by)
    moved = s["advanced"] > 0 or s["drained"] > 0
    verb = "report" if moved else "done"
    tail = ("" if moved else " — field quiescent, nothing pending (no-op)")
    print(f"  advanced={s['advanced']} settled={s['settled']} "
          f"parked={s['parked']} drained={s['drained']}")
    print(f"result: {verb} — one heartbeat cycle{tail}; "
          f"{'paced reviews fired' if s['drained'] else 'tick-only'} "
          f"(drain_limit={drain_limit})")
    return 0


def run_hook(root):
    """The in-harness guaranteed tick: TICK-ONLY and FAIL-OPEN. Wired to
    SessionStart, it nudges the loop once whenever a session opens. It catches
    everything and ALWAYS exits 0 — a guaranteed beat that could raise or block
    a session would be worse than no beat at all. It writes a brief line only
    when it actually advanced work, to keep the session surface quiet."""
    try:
        if not _has_setpoint(root):
            return 0  # nothing to tick; silent, never a block
        s = beat(root, drain_limit=0)  # tick-only: the hook never drains
        if s["advanced"]:
            print(f"heartbeat: ticked the loop (advanced={s['advanced']}, "
                  f"settled={s['settled']}, parked={s['parked']})")
    except Exception:  # noqa: BLE001 — fail-open: a beat must never block a session
        pass
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT,
                    help="the .ai-native records root")
    ap.add_argument("--drain-limit", type=int, default=0,
                    help="fire at most N real value-confirm reviews this beat "
                         "(default 0 = tick-only, the cheap path)")
    ap.add_argument("--by", default="heartbeat.v0", help="who ran the beat")
    ap.add_argument("--hook", action="store_true",
                    help="in-harness tick-only mode: fail-open, exit 0 always "
                         "(safe to wire to SessionStart)")
    args = ap.parse_args(argv)
    if args.hook:
        return run_hook(args.root)
    return run(args.root, drain_limit=args.drain_limit, by=args.by)


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
