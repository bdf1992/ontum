#!/usr/bin/env python3
"""PreToolUse guard on AskUserQuestion: the owner's question surface receives
configuration-shaped, recommendation-carrying options — never a generic menu —
and the prompting stays the right amount.

Prototype (named in done-line 0119 as the next increment; designed in
`gateway-policy-spine.proposal.md` as the spine's first-mover PEP — its
`shape_problems()` is a pure function that ports verbatim into a PDP policy).
Not yet wired into settings.json; its build done-line is minted when the spine
work begins.

bdo, 2026-06-18: "we need a hook to make sure this is used right" — that he
receives configuration-shaped items and the right amount of prompting. The
skill + policy (done-line 0119, .claude/skills/ask/) DEFINE the ontum-ask
shape; this ENFORCES it mechanically, the way command_guard / write_guard /
freeze_guard enforce at their seams. It is the active form of the audit named
in 0119.

Two modes:

  (default — PreToolUse on AskUserQuestion) SHAPE. Deny (exit 2) a generic
    menu: any option missing a reasoned `description`, or no single-select
    question carrying a `(Recommended)` option (so bdo always receives reasoned
    options with my pick surfaced, never a menu he must break out of to ask
    "what's recommended?"). The rules enforce policy.md (R1, R2, R4); the deny
    names what is missing and points at the exemplars to reshape from. Every
    ask — allowed or denied — is logged to the watch trace (the audit's data).

  (--rate — UserPromptSubmit beat) RATE. Fold the logged asks in a rolling
    window and surface ESCALATING pressure when prompting is heavy ("the right
    amount"); silent when it is not. NEVER blocks — a genuine fork must always
    be askable; over-asking is pressured, not forbidden (the mock-shame shape).

Gates the session, never bdo (he never invokes this tool). Fails open on its
own errors and must NOT false-deny a well-shaped ask — a broken guard that
blocked legitimate asks would be worse than none, so the shape check is
conservative: it denies only clear violations and allows anything it cannot
confidently judge. Denials are exit 2 + reason on stderr, recorded to the
gitignored watch log (a sensor trace, not truth).
"""

import datetime
import json
import os
import pathlib
import re
import sys
import traceback

ROOT = pathlib.Path(os.environ.get("ONTUM_REPO_ROOT")
                    or pathlib.Path(__file__).resolve().parents[2])
WATCH_LOG = pathlib.Path(os.environ.get(
    "ONTUM_TOOL_WATCH_LOG", ROOT / ".ai-native" / "log" / "tool-use.jsonl"))

RECOMMENDED = re.compile(r"recommended", re.I)
RATE_WINDOW_MIN = 60  # the rolling window the rate beat folds over


def _now():
    return datetime.datetime.now(datetime.timezone.utc)


def record(entry):
    entry.setdefault("tool", "AskUserQuestion")
    entry["ts"] = _now().isoformat()
    try:
        WATCH_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(WATCH_LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass  # the watcher never breaks the work it watches
    return entry


def shape_problems(questions):
    """The deterministic refusal check (policy.md R1/R2/R4). Returns a list of
    human-readable problems; an empty list means the ask is configuration-
    shaped and reaches bdo. Conservative by construction: anything whose shape
    we cannot confidently judge returns [] (allow), so a well-formed ask is
    never false-denied — only a clear generic menu is refused."""
    if not isinstance(questions, list) or not questions:
        return []  # nothing judgeable — allow (fail open)
    problems = []
    single_select = []
    for qi, q in enumerate(questions):
        if not isinstance(q, dict):
            return []  # unexpected shape — allow
        opts = q.get("options")
        if not isinstance(opts, list) or not opts:
            return []  # the tool requires options; if absent, not ours to judge
        header = (q.get("header") or "").strip()
        where = f"question {qi + 1}" + (f" ({header})" if header else "")
        for oi, o in enumerate(opts):
            if not isinstance(o, dict):
                return []  # unexpected option shape — allow
            if not (o.get("description") or "").strip():
                lab = (o.get("label") or f"option {oi + 1}").strip()
                problems.append(
                    f"{where}: option {lab!r} carries no reasoning (empty "
                    "description) — a bare label is a menu, not a reasoned "
                    "route (policy R1/R2)")
        if not q.get("multiSelect"):
            single_select.append(opts)
    # at least one single-select (pick-one) question must surface a pick —
    # a pure config panel of multiSelect dials is exempt (it has no "the pick")
    if single_select:
        has_reco = any(RECOMMENDED.search(o.get("label") or "")
                       for opts in single_select for o in opts
                       if isinstance(o, dict))
        if not has_reco:
            problems.append(
                "no option is marked (Recommended) — bdo must receive your "
                "reasoned pick, not a menu he has to break out of to ask "
                "\"what's recommended?\" (policy R1). Lead with the recommended "
                "option, first, the reasoning in its description.")
    return problems


def rate_pressure():
    """Fold the watch log for asks that actually reached bdo (status=asked) in
    the rolling window; surface escalating pressure when prompting is heavy.
    Never blocks. Silent under the first threshold. The mock-shame shape: the
    pressure is for over-asking, not a cap on it."""
    cutoff = _now() - datetime.timedelta(minutes=RATE_WINDOW_MIN)
    n = 0
    try:
        with open(WATCH_LOG, encoding="utf-8") as fh:
            for line in fh:
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if e.get("tool") != "AskUserQuestion":
                    continue
                if e.get("status") != "asked":
                    continue  # denied asks never reached him; don't count them
                ts = e.get("ts")
                try:
                    t = datetime.datetime.fromisoformat(ts) if ts else None
                except ValueError:
                    t = None
                if t is not None and t >= cutoff:
                    n += 1
    except OSError:
        return
    if n >= 8:
        print(f"[ask-rate] {n} owner-asks in the last hour — heavy prompting. "
              "bdo's question surface is for genuine forks only HE can settle. "
              "Make the call yourself, or batch the dials into one config "
              "panel (policy R4: an ask you could resolve is offloading).")
    elif n >= 5:
        print(f"[ask-rate] {n} owner-asks in the last hour. Before the next: "
              "is it a genuine fork bdo alone can settle, or a call you can "
              "make? (policy R4)")
    elif n >= 3:
        print(f"[ask-rate] {n} owner-asks recently — keep them to genuine "
              "forks; prefer one config panel over several menus.")
    # under 3: silent — light prompting is not a failure


def main(argv):
    if "--rate" in argv:
        try:
            sys.stdin.read()  # drain the hook payload; the fold is the truth
            rate_pressure()
        except Exception:
            pass  # fail-open: a broken rate beat never blocks the owner's prompt
        return 0
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8", "replace"))
    except (json.JSONDecodeError, ValueError):
        return 0
    if payload.get("tool_name") != "AskUserQuestion":
        return 0
    questions = (payload.get("tool_input") or {}).get("questions")
    try:
        problems = shape_problems(questions)
    except Exception:
        traceback.print_exc(file=sys.stderr)
        return 0  # fail open: never false-deny on a guard bug
    n_q = len(questions) if isinstance(questions, list) else 0
    if problems:
        record({"status": "denied", "n_questions": n_q, "problems": problems})
        print("denied: this AskUserQuestion is a generic menu, not a "
              "configuration-shaped ask (the ontum-ask policy "
              ".claude/skills/ask/policy.md):", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        print("Reshape from an exemplar (.claude/skills/ask/exemplars.md): lead "
              "with a (Recommended) option whose description carries the "
              "reasoning, narrate routes in preview — or, if this is a call you "
              "could make yourself, make it and proceed (policy R4).",
              file=sys.stderr)
        return 2
    headers = [(q.get("header") or "") for q in questions
               if isinstance(q, dict)] if isinstance(questions, list) else []
    record({"status": "asked", "n_questions": n_q, "headers": headers})
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
