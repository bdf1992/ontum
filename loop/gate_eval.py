#!/usr/bin/env python3
"""The value-gate eval (done-line 0116): does the L0 gate actually bite?

A crawl of the whole record showed the gates refuse only ~3.4% of the
time, and by §10 ("if everything passes, the check isn't doing its job")
that is no proof the second-set-of-eyes can say no — only that it rarely
does. The value-gate prompt names the debt itself ("Semantic evals... are
owed"). This is that eval, in bdo's charades frame: don't ask one judge
one question. Give each adversarial case three TURNS — variants along one
axis, escalating toward the fluent-but-wrong edge (the surface_trap) — and
judge each by the reaction of the whole ROOM (a panel of independent
judges, not a solo verdict).

What it measures, that a solo pass/fail cannot:
  catch     does the room refuse a should-reject atom at all?
  bucket    does it refuse for the RIGHT reason (reject_no_value vs amend)?
  robustness does it KEEP refusing as the bad atom is dressed up turn by
            turn — or does a cosmetic re-dress flip it (a brittle tooth)?
  control   does it still ACCEPT a genuinely valuable atom (a paranoid
            gate that refuses everything is as broken as a soft one)?

The corpus (`gate_eval.cases.json`) is DECLARED eval input — never minted
onto the real pipeline, never judged through `loop.node` (like causality's
seed.json). The gate judges each variant as a dry judge and reports its
verdict; this module folds the panel's verdicts into the room's reception
(majority + spread) and scores. Read-only, deterministic, stdlib. The
scorer is reusable for any gate's corpus; the room size is a parameter,
not a constant (the room is bdo's to resize).

CLI:
  python -m loop.gate_eval                       render the corpus, read-only
  python -m loop.gate_eval score --transcript P  score a panel transcript (JSON)

A transcript is {case_id: {turn: [verdict, verdict, ...]}} — one list of
the room's verdicts per variant. Ends with a clear result (D-6): done | report.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ACCEPT = "accept"
TERMINAL_VERDICTS = frozenset({
    "accept", "reject_no_value", "reject_wrong_value", "amend",
})
CASES_PATH = Path(__file__).resolve().parent / "gate_eval.cases.json"


def load_corpus(path=CASES_PATH):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def reception(verdicts):
    """The room's reception of one variant: the majority verdict and the
    full spread. An empty room has no reception (verdict None) — an absence,
    never a guessed verdict."""
    verdicts = [v for v in (verdicts or []) if v]
    if not verdicts:
        return {"verdict": None, "spread": {}, "n": 0}
    spread = Counter(verdicts)
    # majority = most common; ties broken by sorted name for determinism
    top = max(sorted(spread), key=lambda v: spread[v])
    return {"verdict": top, "spread": dict(spread), "n": len(verdicts)}


def _turn_verdicts(transcript, case_id, turn):
    """The room's verdict list for one (case, turn), tolerating int/str turn
    keys (JSON makes them strings)."""
    case = transcript.get(case_id, {})
    return case.get(str(turn), case.get(turn, []))


def score(corpus, transcript):
    """Fold a panel transcript into the room's reception per variant, then
    judge each case and the gate overall. The teeth:

      - a control whose room does not ACCEPT every judged turn FAILS (a
        paranoid gate is broken);
      - a reject-case the room waves through on any JUDGED turn FAILS (a soft
        gate is broken);
      - a reject-case the room bites early and lets through on a later,
        dressed-up judged turn is flagged BRITTLE (the surface_trap fooled it).

    A turn with an empty room is NOT judged — it is unmeasured, never a
    verdict. A case with no judged turns is `not_run`, excluded from the
    pass/fail and the catch-rate: the scorer never reads "I didn't run this"
    as "the gate is soft" (the false positive the first live run exposed).
    """
    case_results = []
    reject_turns = bitten = 0
    run_cases = 0
    overall_pass = True
    for case in corpus["cases"]:
        cid, expected = case["id"], case["expected"]
        per_turn = []
        for t in case["turns"]:
            rec = reception(_turn_verdicts(transcript, cid, t["turn"]))
            judged = rec["verdict"] is not None
            per_turn.append({
                "turn": t["turn"], "reception": rec, "judged": judged,
                "bit": judged and rec["verdict"] != ACCEPT,
                "bucket_match": rec["verdict"] == expected,
                "note": t.get("note", ""),
            })
        judged_turns = [pt for pt in per_turn if pt["judged"]]
        if not judged_turns:
            case_results.append({
                "id": cid, "expected": expected, "axis": case.get("axis", ""),
                "turns": per_turn, "status": "not_run", "case_pass": None,
                "brittle": False, "failure": None,
            })
            continue
        run_cases += 1
        if expected == ACCEPT:
            case_pass = all(pt["reception"]["verdict"] == ACCEPT for pt in judged_turns)
            brittle = False
            failure = None if case_pass else "the room refused a genuine atom (paranoid gate)"
        else:
            reject_turns += len(judged_turns)
            bitten += sum(1 for pt in judged_turns if pt["bit"])
            case_pass = all(pt["bit"] for pt in judged_turns)
            bit_any = any(pt["bit"] for pt in judged_turns)
            brittle = bit_any and not case_pass  # caught some, missed some
            failure = (None if case_pass else
                       ("brittle: the room bit an early turn and waved a "
                        "dressed-up later turn through" if brittle else
                        "the room waved a should-reject atom through (soft gate)"))
        overall_pass = overall_pass and case_pass
        case_results.append({
            "id": cid, "expected": expected, "axis": case.get("axis", ""),
            "turns": per_turn, "status": "run", "case_pass": case_pass,
            "brittle": brittle, "failure": failure,
        })
    return {
        "node": corpus.get("node"),
        "cases": case_results,
        "pass": overall_pass and run_cases > 0,
        "catch_rate": (bitten / reject_turns) if reject_turns else None,
        "reject_turns": reject_turns, "bitten": bitten,
        "coverage": {"run": run_cases, "total": len(corpus["cases"])},
    }


def render_corpus(corpus):
    lines = [f"# value-gate eval corpus — {corpus.get('node')}", "",
             "_declared eval input; never minted onto the pipeline (D-4). "
             "Each case is a chef with 3 turns; the panel is the room._", ""]
    for case in corpus["cases"]:
        lines.append(f"## {case['id']} — expected `{case['expected']}`")
        lines.append(f"_axis: {case.get('axis','')}_")
        for t in case["turns"]:
            story = t["atom"]["story"]["text"]
            if len(story) > 180:
                story = story[:180].rstrip() + " …"
            lines.append(f"- turn {t['turn']} ({t.get('note','')}):")
            lines.append(f"    {story}")
        lines.append("")
    return "\n".join(lines)


def render_score(result):
    lines = [f"# value-gate eval — the room's verdict on {result['node']}", ""]
    cr = result["catch_rate"]
    cov = result["coverage"]
    lines.append(f"catch-rate {cr:.2f} ({result['bitten']}/{result['reject_turns']} "
                 "should-reject turns bitten)" if cr is not None
                 else "no should-reject turns judged")
    lines.append(f"coverage: {cov['run']}/{cov['total']} cases run")
    lines.append(f"overall (over run cases): {'PASS' if result['pass'] else 'FAIL'}")
    lines.append("")
    status_word = {"run": None, "not_run": "not run"}
    for c in result["cases"]:
        if c["status"] == "not_run":
            verdict = "not run"
        else:
            verdict = "pass" if c["case_pass"] else "FAIL"
        head = f"## {c['id']} — expected `{c['expected']}` — {verdict}"
        if c["brittle"]:
            head += " (BRITTLE)"
        lines.append(head)
        for pt in c["turns"]:
            rec = pt["reception"]
            verdict = rec["verdict"] or "—(not run)"
            spread = ", ".join(f"{k}×{v}" for k, v in sorted(rec["spread"].items()))
            mark = ("bit" if pt["bit"]
                    else ("accept" if rec["verdict"] == ACCEPT else "—"))
            lines.append(f"- turn {pt['turn']}: room={verdict} [{spread}] → {mark}"
                         + ("  ✓bucket" if pt["bucket_match"] else ""))
        if c["failure"]:
            lines.append(f"  → {c['failure']}")
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cases", type=Path, default=CASES_PATH)
    sub = ap.add_subparsers(dest="cmd")
    sc = sub.add_parser("score", help="score a panel transcript (JSON on a path or '-')")
    sc.add_argument("--transcript", required=True,
                    help="path to {case_id: {turn: [verdict,...]}} JSON, or '-' for stdin")
    args = ap.parse_args(argv)

    corpus = load_corpus(args.cases)

    if args.cmd != "score":
        print(render_corpus(corpus))
        print()
        n = sum(len(c["turns"]) for c in corpus["cases"])
        print(f"result: report — {len(corpus['cases'])} case(s), {n} variant(s); "
              "run the room, then: python -m loop.gate_eval score --transcript <p>")
        return 0

    raw = sys.stdin.read() if args.transcript == "-" else \
        Path(args.transcript).read_text(encoding="utf-8")
    transcript = json.loads(raw)
    result = score(corpus, transcript)
    print(render_score(result))
    print()
    cov = result["coverage"]
    fails = [c["id"] for c in result["cases"]
             if c["status"] == "run" and not c["case_pass"]]
    if result["pass"] and not fails:
        cr = f"{result['catch_rate']:.2f}" if result["catch_rate"] is not None else "—"
        print(f"result: done — the gate bites on every run case ({cov['run']}/"
              f"{cov['total']}): should-reject turns refused, control accepted "
              f"(catch-rate {cr}). Run the rest on demand to widen coverage.")
    else:
        print(f"result: report — the gate did not pass the room on: "
              f"{', '.join(fails) or 'no cases run'} (coverage {cov['run']}/"
              f"{cov['total']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
