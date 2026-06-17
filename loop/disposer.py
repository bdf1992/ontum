#!/usr/bin/env python3
"""The slow loop's disposer (done-line 0091): the outside the proposer left open,
wired to bdo's standing fence.

`loop/slowloop.py` (done-line 0074) deliberately reaches only halfway — it
*proposes* a setpoint change caused by outcomes, and never disposes it, because
a closed loop has no outside and "the owner is the last stop" (D-4). bdo
answered who that outside is (2026-06-16): a **bounded standing auto-admit**, the
arc-confirm shape (done-line 0028). He draws a **fence** once — per-dial bounds,
signed `--by bdo` — and from then on a proposal that stays *inside* the fence
self-admits, while one that wants to *leave* it still escalates to him.

The authority is bdo's, executed by the loop — never invented by it. An
auto-admitted setpoint is attributed to the loop and **cites the fence as
`authorized_by`**, exactly as a merge-node landing cites the confirm-arc it did
not author: a node propels, it never authorizes itself. So this is not the
proposer signing its own line; it is the loop carrying out a standing stamp the
outside already made.

The rule bdo named, made mechanical in `evaluate`:
  - a **heating** key (one that raises load — a larger budget, more inflight, a
    higher human cap) auto-admits only up to its ceiling `hi`;
  - a **cooling** key (one that sheds load — the safe direction) always
    auto-admits ("cooling always allowed"), even below the floor;
  - a key the fence does not name **escalates** (the fence authorizes only what
    it names — absence is information, the hard rule);
  - and **one out-of-fence key escalates the whole proposal** (§10): a proposal
    is admitted only if every key it changes is in-fence.

The fence is read from the log at runtime (I-8), never a constant. A run with no
admitted fence disposes nothing — inert until bdo stamps one. Stdlib only; the
only write is the one append (`admit_setpoint`, citing the fence). CLI ends with
a clear result (D-6): done | report | needs-you.

CLI:
  python -m loop.disposer                          the fence in force + what it would dispose
  python -m loop.disposer admit-fence \
      --bounds '{"step_budget_per_tick":[2,5]}' --by bdo     draw the fence (bdo)
  python -m loop.disposer dispose --by slow-loop.disposer         dispose one pending proposal
  python -m loop.disposer dispose --hour 8                      a fixed moment (deterministic)
"""

import argparse
import json
import sys
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT, Fold, append_line, canon, now_ts, short_hash
from loop.orchestrate import (SETPOINT_KEYS, admit_setpoint, read_setpoint)
from loop.slowloop import slowloop

FENCE_TYPE = "auto_admit_fence"
# the loop's signer when it executes the fence: not bdo (he signs the fence, not
# each change) and not "slow-loop" the proposer (no node signs its own line) —
# a distinct disposer identity whose every act cites the fence that authorized it.
DISPOSER = "slow-loop.disposer"

# which direction sheds load for each dial. cooling is that direction; it is
# always allowed (bdo). heating is the other way, and it is capped at the fence
# ceiling. all three of today's dials shed load by *decreasing* (a smaller
# budget, fewer inflight, an earlier human cap all protect the slow stage), so
# cooling == decrease for each. recorded explicitly so a future dial whose safe
# direction is *up* is a one-line entry, never a buried assumption.
COOLS_BY_DECREASE = {
    "step_budget_per_tick": True,
    "max_inflight_atoms": True,
    "human_queue_cap": True,
}


def valid_bounds(bounds):
    """A fence's bounds are well-formed: a non-empty map of known dials to
    `[lo, hi]` with lo <= hi, both numbers. Returns (ok, reason)."""
    if not isinstance(bounds, dict) or not bounds:
        return False, "a fence draws at least one dial's [lo, hi] bounds"
    for key, rng in bounds.items():
        if key not in SETPOINT_KEYS:
            return False, (f"unknown dial {key!r}; the fence names only "
                           f"{', '.join(SETPOINT_KEYS)}")
        if (not isinstance(rng, (list, tuple)) or len(rng) != 2
                or not all(isinstance(x, (int, float)) for x in rng)):
            return False, f"dial {key!r} needs a [lo, hi] pair of numbers"
        if rng[0] > rng[1]:
            return False, f"dial {key!r} has lo > hi ({rng[0]} > {rng[1]})"
    return True, None


def admit_fence(root, bounds, by):
    """Append a fence admission — bdo's standing auto-admit authorization (D-4:
    signed `--by`, the loop never draws its own fence). Returns (adm, None) or
    (None, reason-refused)."""
    if not (by or "").strip():
        return None, "a fence is signed (--by) like every admitted record"
    ok, why = valid_bounds(bounds)
    if not ok:
        return None, why
    # normalise to lists so the bytes are deterministic regardless of input shape
    norm = {k: [bounds[k][0], bounds[k][1]] for k in sorted(bounds)}
    adm = {
        "id": "adm." + short_hash(FENCE_TYPE, canon(norm), str(by), now_ts()),
        "type": FENCE_TYPE,
        "bounds": norm,
        "by": by,
        "ts": now_ts(),
    }
    append_line(root / "log" / "admissions.jsonl", adm)
    return adm, None


def read_fence(admissions):
    """The fence in force, read at runtime (I-8): the latest well-formed
    `auto_admit_fence` admission wins (each supersedes the one before). None when
    bdo has drawn none — the disposer is then inert."""
    fence = None
    for adm in admissions:
        if adm.get("type") == FENCE_TYPE:
            ok, _ = valid_bounds(adm.get("bounds"))
            if ok:
                fence = adm
    return fence


def evaluate(fence, current, proposed):
    """The decision, pure over (fence, current, proposed): admit / escalate /
    noop, with a reason per changed dial. The teeth (§10): one out-of-fence key
    escalates the whole proposal — a locally-fine heating step on one dial does
    not buy an out-of-bounds step on another.

    Returns {"verdict", "reasons": [(key, in_fence, why)], "deltas"}.
    """
    deltas = {k: (current.get(k), proposed.get(k))
              for k in proposed
              if k in current and proposed.get(k) != current.get(k)}
    if not deltas:
        return {"verdict": "noop", "reasons": [], "deltas": {}}
    if not fence:
        return {"verdict": "escalate", "deltas": deltas,
                "reasons": [(k, False, "no fence is drawn — nothing self-admits "
                             "(inert until bdo stamps one)") for k in deltas]}
    bounds = fence["bounds"]
    reasons, all_in = [], True
    for key, (cur, prop) in deltas.items():
        rng = bounds.get(key)
        if rng is None:
            reasons.append((key, False, f"the fence does not name {key!r} — only "
                            "what it names self-admits (absence is information)"))
            all_in = False
            continue
        lo, hi = rng
        cooling = (prop < cur) if COOLS_BY_DECREASE.get(key, True) else (prop > cur)
        if cooling:
            reasons.append((key, True, f"cooling ({cur}→{prop}) — the safe "
                            "direction; always self-admits"))
        elif lo <= prop <= hi:
            reasons.append((key, True, f"heating ({cur}→{prop}) within the "
                            f"fence [{lo}, {hi}]"))
        else:
            reasons.append((key, False, f"heating ({cur}→{prop}) past the "
                            f"ceiling {hi} (fence [{lo}, {hi}]) — escalates"))
            all_in = False
    return {"verdict": "admit" if all_in else "escalate",
            "reasons": reasons, "deltas": deltas}


def dispose(root, hour, by=DISPOSER):
    """Read the proposer's current proposal and dispose it through bdo's fence:
    self-admit an in-fence change (one `admit_setpoint`, citing the fence), or
    write nothing and leave an out-of-fence change for him. One disposition per
    call (a level-triggered step, like `pass_once`): after an admit the dial
    bdo's fence raised becomes the new current, and the next proposal is folded
    afresh from it.

    Returns a dict describing what it did — verdict, the evaluation, and the
    admitted setpoint id when it admitted one."""
    fold = Fold(Path(root))
    state = slowloop(root, hour)
    setpoint = state["setpoint"]
    proposal = state["proposal"]
    if setpoint is None:
        return {"verdict": "no-setpoint", "admitted": None, "proposal": None}
    if not proposal or not proposal["change"]:
        return {"verdict": "noop", "admitted": None, "proposal": proposal,
                "fence": read_fence(fold.admissions)}
    fence = read_fence(fold.admissions)
    decision = evaluate(fence, proposal["current"], proposal["proposed"])
    out = {"verdict": decision["verdict"], "admitted": None,
           "proposal": proposal, "fence": fence, "decision": decision}
    if decision["verdict"] == "admit":
        adm = admit_setpoint(root, proposal["proposed"], by=by,
                             supersedes=setpoint["id"],
                             authorized_by=fence["id"],
                             because="; ".join(proposal["because"]))
        out["admitted"] = adm["id"]
    return out


def _bounds_line(fence):
    return ", ".join(f"{k} [{lo}, {hi}]" for k, (lo, hi) in fence["bounds"].items())


def render(root, hour):
    fold = Fold(Path(root))
    fence = read_fence(fold.admissions)
    state = slowloop(root, hour)
    if fence:
        print(f"fence — by {fence['by']}: {_bounds_line(fence)}")
    else:
        print("fence — none drawn; the disposer is inert until bdo stamps one "
              "(python -m loop.disposer admit-fence --bounds '...' --by bdo)")
    sp, proposal = state["setpoint"], state["proposal"]
    if sp is None:
        print("  no admitted setpoint to dispose (I-8)")
        return
    if not proposal["change"]:
        print(f"  proposal: hold — {canon(proposal['current'])} (nothing to dispose)")
        return
    decision = evaluate(fence, proposal["current"], proposal["proposed"])
    print(f"  proposal: {canon(proposal['proposed'])} "
          f"(delta {canon(proposal['deltas'])})")
    print(f"  would: {decision['verdict'].upper()}")
    for key, in_fence, why in decision["reasons"]:
        mark = "in" if in_fence else "OUT"
        print(f"    [{mark}] {why}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd")

    af = sub.add_parser("admit-fence", help="draw the fence (bdo's one stamp)")
    af.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    af.add_argument("--bounds", required=True,
                    help='JSON map of dial -> [lo, hi], e.g. '
                         '\'{"step_budget_per_tick":[2,5]}\'')
    af.add_argument("--by", required=True, help="who draws the fence (D-4)")

    dp = sub.add_parser("dispose", help="dispose one pending proposal through the fence")
    dp.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    dp.add_argument("--hour", type=int, default=None,
                    help="hour 0-23 (default: now, read only at this edge)")
    dp.add_argument("--by", default=DISPOSER,
                    help="the disposer identity (cites the fence; never bdo, "
                         "never the proposer)")

    for p in (ap,):  # the bare verb: show the fence and what it would do
        p.add_argument("--root", type=Path, default=DEFAULT_ROOT, dest="root_top")
        p.add_argument("--hour", type=int, default=None, dest="hour_top")
    args = ap.parse_args(argv)

    def _hour(h):
        if h is None:
            from datetime import datetime
            return datetime.now().hour
        return h % 24

    if args.cmd == "admit-fence":
        try:
            bounds = json.loads(args.bounds)
        except json.JSONDecodeError as e:
            print(f"result: needs-you — --bounds is not valid JSON: {e}")
            return 2
        adm, err = admit_fence(args.root, bounds, args.by)
        if err:
            print(f"result: needs-you — {err}")
            return 2
        print(f"result: report — fence {adm['id']} drawn by {args.by}: "
              f"{_bounds_line(adm)}. In-fence slow-loop proposals now self-admit; "
              f"out-of-fence ones still escalate to you (python -m loop.disposer).")
        return 0

    if args.cmd == "dispose":
        out = dispose(args.root, _hour(args.hour), by=args.by)
        v = out["verdict"]
        if v == "no-setpoint":
            print("result: needs-you — no admitted setpoint to dispose (I-8)")
            return 2
        if v == "noop":
            print("result: done — the slow loop proposes no change; nothing to dispose")
            return 0
        if v == "admit":
            print(f"result: report — disposed: setpoint {out['admitted']} "
                  f"self-admitted as {args.by}, authorized by fence "
                  f"{out['fence']['id']} (delta {canon(out['decision']['deltas'])}). "
                  "The slow loop moved its own dial, inside the fence bdo drew.")
            return 0
        # escalate
        outk = [k for k, in_f, _ in out["decision"]["reasons"] if not in_f]
        print(f"result: needs-you — the proposal leaves the fence on {', '.join(outk)}; "
              "it does not self-admit. It stays a proposal for bdo "
              "(python -m loop.slowloop).")
        return 0

    render(args.root_top, _hour(args.hour_top))
    return 0


if __name__ == "__main__":
    sys.exit(main())
