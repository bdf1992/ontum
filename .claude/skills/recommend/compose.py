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
    if shape_problems is None:
        refusals.append(
            "the ask floor (shape_problems) could not be loaded — refuse rather "
            "than render an unbounded panel (fail-safe, RC3)")
    else:
        refusals.extend(shape_problems(panel))
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
    # the bad panel must trip: over-cap options, long header, no (Recommended)
    joined = " ".join(b)
    assert "options" in joined and "header" in joined, joined
    assert any("Recommended" in r or "recommended" in r for r in b), b
    print("selftest: ok — bound passes the good panel and bites the bad one")
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
