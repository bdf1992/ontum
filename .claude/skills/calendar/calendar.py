#!/usr/bin/env python3
"""calendar.py — the calendar producer/subscriber pen (the first integration).

bdo, 2026-06-22: a private `calendar` repo is the central pub/sub substrate where
every meeting lands, reachable from any device (git is the cross-device layer).
ontum is the **first producer**. This pen is the outward seam between the two —
the reflect.py pattern: the pure fold (`loop/meeting.py`) prepares; this pen
*reaches* (the no-network rule keeps reach out of `loop/`).

Decoupled pub/sub (bdo's call, 2026-06-22): the calendar repo is standalone — it
never needs ontum present.

  PUBLISH   ontum -> calendar : `build_record` (PURE) turns the prepared agenda
            into a meeting record (manifest + AGENDA + CLAUDE); `publish` writes
            it to the calendar repo and records the publish on ontum's log.
  CONSUME   calendar -> ontum : a meeting's `decisions[]` are the RETURN CHANNEL.
            `plan_consume` (PURE) reads which decisions are not yet landed; the
            runner only *wrote intent* in the repo, and ontum *subscribes* —
            recording each decision as a first-class log event (the closing
            evidence) and actuating it through the existing pens (a discharge of
            an owner-ask cites that very event). Idempotent: a decision already
            on the log is never re-applied (the substrate's re-run law).

The split is testable without a network: `build_record`/`plan_consume` are pure;
the gh reach is behind injectable `put_file`/`get_json` (default: the gh CLI),
exactly as reflect.py injects its `run`. Stdlib + the gh CLI, no new dependency.

CLI:
  python .claude/skills/calendar/calendar.py build   [--date YYYY-MM-DD]      # the record, to stdout (dry)
  python .claude/skills/calendar/calendar.py publish --by <who> [--date ...]  # write it to the calendar repo + log
  python .claude/skills/calendar/calendar.py consume --meeting <id> --by <who># land a meeting's decisions back
"""

from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]  # .claude/skills/calendar/ -> repo root
sys.path.insert(0, str(REPO))

from loop.meeting import agenda, render  # noqa: E402
from loop.reconcile import DEFAULT_ROOT, Fold, append_line, now_ts, short_hash  # noqa: E402
from loop import reflect  # noqa: E402

DEFAULT_REPO = "bdf1992/calendar"
PRODUCER = "ontum:loop/meeting.py"
DECISION_EVENT = "meeting_decision"
PUBLISHED_EVENT = "calendar_published"
SLUG = "owner-asks"


# --------------------------------------------------------- pure: identity

def meeting_id(date, slug=SLUG):
    return f"meeting.{date}-{slug}"


def meeting_dir_from_id(mid):
    # meeting.<date>-<slug> -> meetings/<date>-<slug>
    return "meetings/" + mid[len("meeting."):]


# --------------------------------------------------- pure: record building

def _runner_claude_md(date):
    return (
        f"# Daily owner meeting — owner-asks ({date})\n\n"
        "You are the agent running bdo's daily owner-meeting. **This folder is your\n"
        "environment** — opening it is the owner joining the meeting.\n\n"
        "- The agenda is `AGENDA.md`: a ranked, ~30-minute list of decisions parked\n"
        "  on bdo, produced by ontum's `loop/meeting.py` (newest report first,\n"
        "  budget-capped).\n"
        "- Walk each item in order. Serve a **shaped read** (the situation in plain\n"
        "  words, your recommendation, the riskiest part flagged — the Taster's\n"
        "  Clause), then take his decision: **confirm · defer · discharge**.\n"
        "- Record each decision into `manifest.json` `decisions[]` as\n"
        '  `{"id": "<agenda-item-id>", "verdict": "confirm|defer|discharge",\n'
        '  "note": "<one line>", "by": "bdo"}`, and append the conversation to\n'
        "  `TRANSCRIPT.md`. Commit both back to this repo.\n"
        "- **The decisions are the return channel (decoupled pub/sub):** ontum\n"
        "  subscribes and lands them — a `discharge` closes the owner-ask (citing\n"
        "  the decision), a `confirm` runs the arc confirmation. You record intent\n"
        "  here; ontum reconciles it. The calendar repo never needs ontum present.\n"
        "- Keep to the 30-minute budget; items past what fits are deferred to\n"
        "  tomorrow — say so, don't rush them. **You serve; you don't decide (D-4).**\n"
    )


def build_record(root, date, *, repo=DEFAULT_REPO, producer=PRODUCER):
    """PURE: the prepared agenda as a calendar meeting record. Returns
    (meeting_id, {repo_path: content}). No reach, no clock beyond the passed
    date — a fixed root+date yields a fixed record (testable)."""
    data = agenda(root)
    b = data["budget"]
    mid = meeting_id(date)
    mdir = meeting_dir_from_id(mid)
    manifest = {
        "id": mid,
        "date": date,
        "type": "owner-meeting",
        "title": "Daily owner meeting — owner-asks",
        "producer": producer,
        "status": "ready",
        "budget_minutes": b["total_minutes"],
        "stats": {
            "groups_total": data["total_groups"],
            "items_total": data["total_asks"],
            "above_fold": b["above_fold"],
        },
        "agenda": [
            {"id": it["id"], "report_id": it["report_id"], "count": it["count"]}
            for it in data["today"]
        ],
        "deferred_count": data["deferred_count"],
        # the return channel — the runner fills this in the repo; ontum consumes it.
        "decisions": [],
    }
    files = {
        f"{mdir}/manifest.json": json.dumps(manifest, indent=2) + "\n",
        f"{mdir}/AGENDA.md": render(data) + "\n",
        f"{mdir}/CLAUDE.md": _runner_claude_md(date),
    }
    return mid, files


# ----------------------------------------------------- outward: the gh reach

def _gh_get_sha(repo, path):
    out = subprocess.run(["gh", "api", f"repos/{repo}/contents/{path}"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        return None
    try:
        return json.loads(out.stdout).get("sha")
    except (ValueError, KeyError):
        return None


def _gh_put_file(repo, path, content, message, branch="main"):
    """Create-or-update one file in the calendar repo via the Contents API.
    Fetches the current sha so a re-publish updates in place (idempotent write)."""
    b64 = base64.b64encode(content.encode("utf-8")).decode("ascii")
    args = ["gh", "api", "-X", "PUT", f"repos/{repo}/contents/{path}",
            "-f", f"message={message}", "-f", f"content={b64}",
            "-f", f"branch={branch}"]
    sha = _gh_get_sha(repo, path)
    if sha:
        args += ["-f", f"sha={sha}"]
    subprocess.run(args, check=True, capture_output=True, text=True)
    return path


def _gh_get_json(repo, path):
    """Read a JSON file from the calendar repo via the Contents API, or None."""
    out = subprocess.run(["gh", "api", f"repos/{repo}/contents/{path}"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        return None
    try:
        blob = json.loads(out.stdout)
        return json.loads(base64.b64decode(blob["content"]).decode("utf-8"))
    except (ValueError, KeyError):
        return None


# --------------------------------------------------------------- publish

def publish(root, date, *, by, repo=DEFAULT_REPO, put_file=_gh_put_file):
    """Write the prepared meeting record to the calendar repo and record the
    publish on ontum's log (provenance). `put_file` is injectable for tests."""
    mid, files = build_record(root, date, repo=repo)
    written = []
    for path, content in files.items():
        put_file(repo, path, content, f"publish {mid}: {path}")
        written.append(path)
    evt = {
        "id": "evt." + short_hash(PUBLISHED_EVENT, mid, by, now_ts()),
        "type": PUBLISHED_EVENT,
        "meeting_id": mid,
        "repo": repo,
        "files": written,
        "by": by,
        "ts": now_ts(),
    }
    append_line(Path(root) / "log" / "events.jsonl", evt)
    return {"meeting_id": mid, "files": written, "record": evt["id"]}


# ------------------------------------------------- consume (the return leg)

def consumed_decision_keys(fold):
    """Every (meeting:subject) a meeting_decision event has already landed."""
    return {e.get("decision_key") for e in fold.events
            if e.get("type") == DECISION_EVENT}


def _verdict_act(verdict, subject):
    """Which ontum pen actuates a decision. An owner-ask discharge is wired;
    confirm/defer are recorded-only until their handlers land (named, honest)."""
    if verdict == "discharge" and subject.startswith("ask."):
        return "discharge-owner-ask"
    return "record-only"


def plan_consume(fold, mid, decisions):
    """PURE: the meeting decisions not yet landed, each with its mapped act.
    A decision already on the log (by key) is skipped — re-consume is a no-op."""
    seen = consumed_decision_keys(fold)
    plan = []
    for d in decisions or []:
        subject = (d.get("id") or "").strip()
        verdict = (d.get("verdict") or "").strip()
        if not subject or not verdict:
            continue
        key = f"{mid}:{subject}"
        if key in seen:
            continue
        plan.append({
            "key": key, "subject": subject, "verdict": verdict,
            "note": (d.get("note") or "").strip(),
            "act": _verdict_act(verdict, subject),
        })
    return plan


def consume(root, mid, *, by, repo=DEFAULT_REPO, get_json=_gh_get_json):
    """Land a meeting's decisions back into ontum (decoupled). Each not-yet-seen
    decision is recorded as a first-class log event (the closing evidence), then
    actuated through the existing pen: a discharge of an owner-ask cites that
    event. `get_json` is injectable for tests."""
    manifest = get_json(repo, f"{meeting_dir_from_id(mid)}/manifest.json")
    if not manifest:
        return {"meeting_id": mid, "applied": [], "error": "no manifest on the surface"}
    plan = plan_consume(Fold(root), mid, manifest.get("decisions", []))
    applied = []
    for p in plan:
        evt = {
            "id": "evt." + short_hash(DECISION_EVENT, p["key"], by, now_ts()),
            "type": DECISION_EVENT,
            "meeting_id": mid,
            "decision_key": p["key"],
            "subject": p["subject"],
            "verdict": p["verdict"],
            "note": p["note"],
            "by": by,
            "ts": now_ts(),
        }
        append_line(Path(root) / "log" / "events.jsonl", evt)
        result = "recorded"
        if p["act"] == "discharge-owner-ask":
            adm, err = reflect.discharge_owner_ask(
                root, p["subject"], [evt["id"]],
                reason=f"discharged in meeting {mid}: {p['note'] or 'owner decision'}",
                by=by)
            result = "discharged" if adm else f"refused: {err}"
        applied.append({"subject": p["subject"], "verdict": p["verdict"],
                        "result": result})
    return {"meeting_id": mid, "applied": applied}


# --------------------------------------------------------------------- CLI

def _today():
    return now_ts()[:10]


def main(argv=None):
    ap = argparse.ArgumentParser(description="the calendar producer/subscriber pen")
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--repo", default=DEFAULT_REPO)
    sub = ap.add_subparsers(dest="cmd", required=True)
    pb = sub.add_parser("build", help="the meeting record, to stdout (dry)")
    pb.add_argument("--date", default=None)
    pp = sub.add_parser("publish", help="write the record to the calendar repo + log")
    pp.add_argument("--date", default=None)
    pp.add_argument("--by", required=True)
    pc = sub.add_parser("consume", help="land a meeting's decisions back into ontum")
    pc.add_argument("--meeting", required=True, help="the meeting id")
    pc.add_argument("--by", required=True)
    args = ap.parse_args(argv)

    if args.cmd == "build":
        mid, files = build_record(args.root, args.date or _today(), repo=args.repo)
        print(f"# {mid}\n")
        for path, content in files.items():
            print(f"--- {path} ---\n{content}")
        return 0
    if args.cmd == "publish":
        out = publish(args.root, args.date or _today(), by=args.by, repo=args.repo)
        print(f"result: done — published {out['meeting_id']} to {args.repo} "
              f"({len(out['files'])} file(s)); recorded {out['record']}")
        return 0
    if args.cmd == "consume":
        out = consume(args.root, args.meeting, by=args.by, repo=args.repo)
        if out.get("error"):
            print(f"result: report — {args.meeting}: {out['error']}")
            return 0
        n = len(out["applied"])
        print(f"result: done — consumed {n} decision(s) from {args.meeting}: "
              + "; ".join(f"{a['subject']} {a['verdict']} -> {a['result']}"
                          for a in out["applied"]) if n else
              f"result: done — {args.meeting}: no new decisions to land")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
