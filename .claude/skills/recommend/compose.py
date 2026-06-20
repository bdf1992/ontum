#!/usr/bin/env python3
"""The code bound for /recommend's generative step (skills/recommend/SKILL.md).

recommend composes a generative branching TREE of AskUserQuestion panels: a
route selected in one tab generates the next set of checkboxes, composed live
by the session (the inference). `AskUserQuestion` is a session tool, so the
COMPOSITION cannot live in a subprocess — but the BOUND can, and must: before
any generated panel renders, it passes this check. The settled-safe floor is
code; the fresh composition is inference (`ontum-inference-as-composition`).

This module does NOT re-author /ask's law. It REUSES `shape_problems()` from
the ask guard (.claude/hooks/ask_guard.py) for the per-panel R1/R2 floor (I-4:
one definition, two callers — the guard at the live seam, this at the
generative seam) and adds only the TREE bound recommend needs:

  - the AskUserQuestion cap: 1..4 tabs (questions), each 2..4 options;
  - headers <= 12 chars (the chip cap, learned in the ask discipline);
  - then /ask's deterministic floor on the panel (a route tab carries a
    (Recommended) option; every option carries reasoning).

`refusal_check(panel)` returns a list of human-readable refusals; an empty
list means the panel is bounded and may render. A non-empty list means
recompose — never render an unbounded panel (policy RC3).
"""

import json
import os
import pathlib
import sys

# Reuse the ask guard's per-panel floor — one definition, not a twin (I-4).
_HOOKS = pathlib.Path(os.environ.get("ONTUM_REPO_ROOT")
                      or pathlib.Path(__file__).resolve().parents[3]) / ".claude" / "hooks"
if str(_HOOKS) not in sys.path:
    sys.path.insert(0, str(_HOOKS))
try:
    from ask_guard import shape_problems  # noqa: E402
except Exception:  # pragma: no cover - the floor is required; surface its loss
    shape_problems = None

# Reuse the verb->intent classifier for the auto-run constraint (I-4, the same
# tags.py discipline the git pen uses to refuse an intent that lies about its
# verb). Best-effort: if loop isn't importable, the constraint still holds on the
# declared intent, it just loses the verb cross-check.
_ROOT = pathlib.Path(os.environ.get("ONTUM_REPO_ROOT")
                     or pathlib.Path(__file__).resolve().parents[3])
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
try:
    from loop.tags import classify as _classify  # noqa: E402
except Exception:  # pragma: no cover
    def _classify(_cmd):
        return None

MAX_TABS = 4        # AskUserQuestion: at most 4 questions per call
MIN_OPTIONS = 2     # the tool requires at least 2 options
MAX_OPTIONS = 4     # at most 4 options per question
MAX_HEADER = 12     # the header chip cap (ask discipline, 2026-06-18)


def refusal_check(panel):
    """The tree bound. `panel` is a list of question dicts (one AskUserQuestion
    call). Returns the refusals; empty means bounded — render it. RC3."""
    refusals = []
    if not isinstance(panel, list) or not panel:
        return ["panel is empty — a generated panel must carry 1..4 tabs (RC1)"]
    if len(panel) > MAX_TABS:
        refusals.append(
            f"panel has {len(panel)} tabs — the cap is {MAX_TABS} "
            "(AskUserQuestion; walk the rest down a branch instead, RC1)")
    for qi, q in enumerate(panel):
        where = f"tab {qi + 1}"
        if not isinstance(q, dict):
            refusals.append(f"{where}: not a question object")
            continue
        header = (q.get("header") or "").strip()
        if header:
            where = f"tab {qi + 1} ({header})"
            if len(header) > MAX_HEADER:
                refusals.append(
                    f"{where}: header is {len(header)} chars — cap {MAX_HEADER}")
        opts = q.get("options")
        if not isinstance(opts, list) or not (MIN_OPTIONS <= len(opts) <= MAX_OPTIONS):
            n = len(opts) if isinstance(opts, list) else 0
            refusals.append(
                f"{where}: {n} options — must be {MIN_OPTIONS}..{MAX_OPTIONS} (RC1)")
    # Then /ask's deterministic per-panel floor (R1/R2), reused not re-derived.
    # /ask is recommend's dependency; when it isn't deployed beside us yet (its
    # skill not on this ref — recommend and ask are a stack heading to the same
    # arc), the borrowed floor is simply SKIPPED — fail-OPEN, the same philosophy
    # ask_guard itself holds ("fail open... never false-deny"). The tree bound
    # above and autorun_refusals still bite; the floor activates the moment /ask
    # lands. Re-implementing it here would be the twin I-4 forbids (done-line
    # 0125 non-example).
    if shape_problems is not None:
        refusals.extend(shape_problems(panel))
    return refusals


def autorun_refusals(routes):
    """The ANSWER-side bound (policy RC7): a selection auto-runs deterministic
    code ONLY when it is read-class. `routes` is a list of dicts describing what
    each pickable option is wired to:

        {"option": <label>, "command": <str>, "intent": "read"|"change",
         "autorun": <bool>}

    Returns the refusals; empty means the auto-run wiring is safe.

    The law it enforces — a gesture is evidence, not a command (AIM); a pick that
    fires a mutating/authority act is self-signing (D-4, no-self-sign):
      - a route may auto-run only if its intent is "read";
      - a "change" route must propose -> gate, never auto-run;
      - a route that DECLARES read but whose verb classifies as mutate is lying
        about itself (the tags.py / git-pen discipline) -> refused;
      - "Other"/NL is never a route here -> it always proposes (handled by the
        skill, never auto-run), so the absence of a route is correct, not a gap.
    """
    refusals = []
    if not isinstance(routes, list):
        return ["routes must be a list of {option, command, intent, autorun}"]
    for r in routes:
        if not isinstance(r, dict):
            refusals.append("a route is not an object")
            continue
        opt = r.get("option", "?")
        intent = r.get("intent")
        cmd = (r.get("command") or "").strip()
        if not r.get("autorun"):
            continue  # a propose-route is always allowed; only auto-run is bounded
        if intent != "read":
            refusals.append(
                f"route {opt!r}: auto-run is read-class only; this is {intent!r} "
                "— a change must propose -> gate, never fire on a pick (RC7/AIM)")
            continue
        # declared read — cross-check the verb isn't secretly a mutation (I-4)
        verb_intent = None
        try:
            verb_intent = _classify(cmd) or _classify(cmd.split()[0] if cmd else "")
        except Exception:
            verb_intent = None
        if verb_intent == "mutate":
            refusals.append(
                f"route {opt!r}: declares read but the command {cmd!r} classifies "
                "as mutate — the route lies about its verb (RC7)")
    return refusals


def _selftest():
    """The teeth (§10): the bound must REFUSE a bad panel and PASS a good one.
    If both were silent the bound would be decoration."""
    good = [{
        "question": "Where should the generative composer live?",
        "header": "Composer",
        "multiSelect": False,
        "options": [
            {"label": "Session as inference (Recommended)",
             "description": "prompt-as-code; the session composes, code bounds it",
             "preview": "skill instructs session -> compose.py bounds"},
            {"label": "Headless Python pen",
             "description": "a subprocess renders panels — cannot reach the tool",
             "preview": "loop/compose.py -> AskUserQuestion (impossible)"},
        ],
    }]
    bad = [{
        "question": "Pick one",
        "header": "A header far too long to be a chip",
        "multiSelect": False,
        "options": [
            {"label": "x", "description": ""},
            {"label": "y", "description": ""},
            {"label": "z", "description": "z"},
            {"label": "w", "description": "w"},
            {"label": "v", "description": "v"},  # 5 options -> over cap
        ],
    }]
    g = refusal_check(good)
    b = refusal_check(bad)
    assert g == [], f"good panel was refused: {g}"
    assert b, "bad panel passed — the bound has no teeth"
    # the bad panel must trip the TREE bound regardless of the floor's presence:
    joined = " ".join(b)
    assert "options" in joined and "header" in joined, joined
    # the borrowed /ask floor (R1/R2) only bites when /ask is deployed beside us:
    if shape_problems is not None:
        assert any("Recommended" in r or "recommended" in r for r in b), b
    # the answer-side bound (RC7): read auto-runs, a change auto-run is refused
    safe = [{"option": "show the gaps", "command": "python -m loop.gaps",
             "intent": "read", "autorun": True}]
    unsafe = [{"option": "land it", "command": "pr.py land", "intent": "change",
               "autorun": True}]
    assert autorun_refusals(safe) == [], f"safe auto-run was refused: {autorun_refusals(safe)}"
    ar = autorun_refusals(unsafe)
    assert ar, "a change route claimed auto-run and the bound let it through"
    assert any("change" in r or "propose" in r for r in ar), ar
    print("selftest: ok — bound passes the good panel and bites the bad one")
    print(f"  change-auto-run refused: {autorun_refusals(unsafe)[0]}")
    print(f"  bad-panel refusals ({len(b)}):")
    for r in b:
        print(f"    - {r}")
    return 0


def main(argv):
    if "--selftest" in argv:
        return _selftest()
    # Read a panel (JSON list of questions) from stdin; report the bound.
    try:
        panel = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        print("needs-you: stdin was not a JSON panel (a list of questions)",
              file=sys.stderr)
        return 2
    refusals = refusal_check(panel)
    if refusals:
        print("refused: this generated panel is unbounded — recompose before "
              "rendering (recommend policy.md RC3):", file=sys.stderr)
        for r in refusals:
            print(f"  - {r}", file=sys.stderr)
        return 2
    print("done: panel is bounded — render it")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
