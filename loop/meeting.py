#!/usr/bin/env python3
"""loop/meeting.py — the prepared owner-meeting agenda (done-line 0183).

bdo, 2026-06-22: *"I need a digest over these owner asks, at most a 30-minute
daily meeting"* — refined the same day to the meeting's true shape: *"an active
30-minute session over a prepared meeting that I get — a meeting link I hand to
an agent, and they have 30 minutes with me."* The deliverable is not a document
he reads; it is a live, time-boxed meeting an agent runs *for* him. This module
is the **deterministic prep** — the part every meeting variant needs: the ranked,
budget-capped agenda. The live link, the meeting-agent, and the perennial
surface are later increments (.ai-native/proposals/owner-ask-digest.proposal.md).

Why a single prepared agenda exists at all is the root-cause fix: the old
`owner-ask-backlog` reflect rule opened one GitHub issue *per report* with a
blind `gh issue create`, deduped only by a branch-local ack — so cloud couriers
and stranded worktrees whose ack never reached main re-minted a fresh duplicate
every session (each of 6 reports opened ~9×). One prepared meeting, ranked and
capped, is the opposite of that pile.

The grain follows the rest of the loop: a pure, read-only, stdlib fold (I-3).
The one write seam is the budget dial — an admitted, signed setpoint (the
substrate's "setpoints are admitted records" law, never a code constant), read
back from the log like the orchestrator's dial and the inference queue's bound.

  - the **source** — `live_owner_asks`: every `owner_ask_groups` entry that is
    not discharged (its closing record cited, done-line 0065) and not baselined
    (predates the guard). Note: *surfaced* is not *answered* — a once-mirrored
    ask whose issue was closed is still on the agenda until it is discharged.
  - the **rank** — `rank`: report freshness (a newer report's asks lead), then
    item-count. Deterministic: a fixed set yields a fixed agenda.
  - the **budget** — `meeting_budget`/`set_budget`: per-ask minutes over a
    meeting length; the above-fold count is `total // per_ask`. Default-safe at
    3 min/ask over 30 min -> 10 above the fold (bdo's "the thing you said"),
    until he admits his own.
  - the **cut** — `agenda`: the ranked source split into *today's agenda*
    (what fits the budget) and a *deferred* tail (a count, never dropped).

CLI:
  python -m loop.meeting                       the prepared agenda, rendered
  python -m loop.meeting --json                the dataset, machine-readable
  python -m loop.meeting admit-budget --per-ask 3 --total 30 --by bdo
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from loop.owner_asks import owner_ask_groups
from loop.reconcile import DEFAULT_ROOT, Fold, append_line, now_ts, short_hash
from loop.reflect import baselined_ask_ids, discharged_ask_ids

BUDGET_TYPE = "meeting_budget"
DEFAULT_PER_ASK_MIN = 3      # bdo's "the thing you said": ~3 min per ask
DEFAULT_TOTAL_MIN = 30       # "at most a 30-minute daily meeting"

_LEADING_NUM = re.compile(r"^(\d+)")


# --------------------------------------------------------------- the budget

def meeting_budget(fold):
    """The admitted budget (latest non-superseded), or the safe default. A pure
    fold — read from the log at call time, never a literal. Returns
    {per_ask_minutes, total_minutes, above_fold}."""
    superseded = {a["supersedes"] for a in fold.admissions if a.get("supersedes")}
    latest = None
    for adm in fold.admissions:
        if (adm.get("type") == BUDGET_TYPE
                and adm.get("id") not in superseded
                and isinstance(adm.get("per_ask_minutes"), int)
                and isinstance(adm.get("total_minutes"), int)):
            latest = adm  # log order is append order; last wins
    per_ask = latest["per_ask_minutes"] if latest else DEFAULT_PER_ASK_MIN
    total = latest["total_minutes"] if latest else DEFAULT_TOTAL_MIN
    per_ask = max(1, int(per_ask))
    total = max(1, int(total))
    return {
        "per_ask_minutes": per_ask,
        "total_minutes": total,
        "above_fold": max(1, total // per_ask),
        "admitted": latest is not None,
    }


def set_budget(root, per_ask_minutes, total_minutes, by, supersedes=None):
    """Admit the meeting budget. Signed config, superseding never erasing
    (mirrors inference_queue.set_bound). Returns the admission, or None if
    either value is not a positive int."""
    try:
        per_ask = int(per_ask_minutes)
        total = int(total_minutes)
    except (TypeError, ValueError):
        return None
    if per_ask < 1 or total < 1:
        return None
    adm = {
        "id": "adm." + short_hash(BUDGET_TYPE, str(per_ask), str(total), by,
                                  now_ts()),
        "type": BUDGET_TYPE,
        "per_ask_minutes": per_ask,
        "total_minutes": total,
        "by": by,
        "supersedes": supersedes,
        "ts": now_ts(),
    }
    append_line(Path(root) / "log" / "admissions.jsonl", adm)
    return adm


# ----------------------------------------------------------- source + rank

def _report_num(report_id):
    """The leading number of a report id ('0122-...' -> 122), or 0. Freshness:
    a higher number is a newer report (the report pen numbers monotonically)."""
    m = _LEADING_NUM.match(report_id or "")
    return int(m.group(1)) if m else 0


def live_owner_asks(root):
    """Every owner-ask group still parked on bdo: in `owner_ask_groups`, not
    discharged, not baselined. Surfaced-but-not-discharged stays — a closed
    mirror issue did not answer the ask. Read-only."""
    fold = Fold(root)
    silent = baselined_ask_ids(fold) | discharged_ask_ids(fold)
    return [g for g in owner_ask_groups(root) if g["id"] not in silent]


def rank(groups):
    """Pressure order over the asks: newer report first, then more items first,
    then report id for a stable tiebreak. Pure and deterministic."""
    return sorted(
        groups,
        key=lambda g: (-_report_num(g["report_id"]), -len(g["asks"]),
                       g["report_id"]),
    )


def _item(group):
    asks = group["asks"]
    return {
        "report_id": group["report_id"],
        "id": group["id"],
        "lead": asks[0] if asks else "",
        "asks": asks,
        "count": len(asks),
    }


def agenda(root, budget=None):
    """The prepared agenda: the ranked live owner-asks split into today's
    agenda (what fits the budget) and a deferred tail (a count, never dropped).
    Pure read-only fold."""
    if budget is None:
        budget = meeting_budget(Fold(root))
    ranked = [_item(g) for g in rank(live_owner_asks(root))]
    cut = budget["above_fold"]
    above = ranked[:cut]
    deferred = ranked[cut:]
    return {
        "budget": budget,
        "today": above,
        "deferred": deferred,
        "deferred_count": len(deferred),
        "total_groups": len(ranked),
        "total_asks": sum(i["count"] for i in ranked),
    }


# --------------------------------------------------------------- rendering

def render(data):
    b = data["budget"]
    src = "admitted" if b["admitted"] else "default (provisional — bdo to admit)"
    lines = [
        "# Daily owner meeting — prepared agenda",
        "",
        (f"**Budget:** {b['total_minutes']} min, ~{b['per_ask_minutes']} min/ask "
         f"-> {b['above_fold']} above the fold ({src})."),
        (f"**Parked:** {data['total_groups']} owner-ask group(s), "
         f"{data['total_asks']} item(s) total."),
        "",
    ]
    if not data["today"]:
        lines.append("Nothing parked on you — the agenda is empty. Result: done.")
        return "\n".join(lines)
    lines.append(f"## Today ({len(data['today'])} group(s), the "
                 f"{b['total_minutes']} minutes)")
    for n, it in enumerate(data["today"], 1):
        lines.append(f"{n}. **{it['report_id']}** ({it['count']} item(s))")
        for ask in it["asks"]:
            lines.append(f"   - {ask}")
    if data["deferred"]:
        lines += ["", (f"## Deferred ({data['deferred_count']} group(s) below "
                       "the fold — next meeting)")]
        for it in data["deferred"]:
            lines.append(f"- {it['report_id']} ({it['count']} item(s)): {it['lead']}")
    return "\n".join(lines)


# --------------------------------------------------------------------- CLI

def _build_parser():
    ap = argparse.ArgumentParser(description="the prepared owner-meeting agenda")
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--json", action="store_true", help="emit the dataset")
    sub = ap.add_subparsers(dest="cmd")
    ab = sub.add_parser("admit-budget", help="admit the meeting budget (signed)")
    ab.add_argument("--per-ask", type=int, required=True,
                    help="minutes per ask")
    ab.add_argument("--total", type=int, required=True,
                    help="meeting length in minutes")
    ab.add_argument("--by", required=True, help="the signer")
    ab.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    return ap


def main(argv=None):
    args = _build_parser().parse_args(argv)
    if args.cmd == "admit-budget":
        adm = set_budget(args.root, args.per_ask, args.total, args.by)
        if adm is None:
            print("result: needs-you — budget needs two positive ints "
                  "(--per-ask, --total)")
            return 2
        print(f"result: done — budget admitted ({adm['id']}): "
              f"{adm['per_ask_minutes']} min/ask over {adm['total_minutes']} min, "
              f"by {adm['by']}")
        return 0
    data = agenda(args.root)
    if args.json:
        print(json.dumps(data, indent=2))
        return 0
    print(render(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
