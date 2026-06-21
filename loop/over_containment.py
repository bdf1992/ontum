#!/usr/bin/env python3
"""The over-containment counter-test — the shared shadow of T6 and T7.

ontum's most likely failure is **over-containment**: the system grows so
good at refusing/collapsing that it stops being *challenged*, and a
stabilization that means nothing gets read as health. The shadow shows
up at two layers:

  T6  over-containment in ACTION space — the gate refuses so little that
      nothing risky ever reaches it; a stage looks "settled" because no
      novel work was ever pointed at it (the §10 failure the doctrine
      keeps naming: a gate that always passes is not doing its job).
  T7  over-containment in REPRESENTATION space — the equivalence classes
      collapse so hard that real signal is averaged away; a class looks
      "coherent" because it lumped everything together, not because it
      discriminates.

They are ONE shadow at two layers, so they share ONE counter-test. The
shared discriminator is **predictive vs. trivial**: a signal that
stabilized because it became genuinely *predictive* is healthy; a signal
that stabilized because nothing risky or novel was ever tested against it
is over-contained. The same word — "stable" — is health in the first
case and rot in the second; only the *provenance of the stability* tells
them apart.

So the detector never trusts a signal's own claim of being predictive.
It derives the verdict from whether the stabilization was ever **tested**:
did variety / refusal / novel input actually *reach* the signal, AND did
its coherence **rise from a low start** under that input? A signal whose
coherence is simply high, with nothing ever pushed against it, is stable
because *untouched* — that is the over-containment, no matter what it
asserts about itself.

This is a self-contained detector, not a log fold: it defines its own
minimal `signal` shape (below) so it can be the shared counter-test for
T6/T7 before either layer's producer exists. The grip rule still holds —
evidence is the signal's own measured values (`coherence 0.20→0.90 over
4 trials`), never prose, and a finding names its own check.

  signal = {
      "id":              str,            # what stabilized
      "layer":           "action"|"representation"  # T6 or T7 (descriptive)
      "coherence_start": float in [0,1], # coherence BEFORE any input reached it
      "coherence_now":   float in [0,1], # current coherence
      "trials":          [ {"novel": bool, "refused": bool}, ... ],
                                         # the inputs that ACTUALLY reached it
      # any self-asserted "predictive"/"claimed_*" key is IGNORED — the
      # detector derives predictiveness, it never reads an assertion of it.
  }

classify(signal) -> {
    "kind": "predictive" | "trivial-overcontainment",
    "subject": id, "layer": ..., "evidence": [...], "move": ...,
    "tested": bool, "stable": bool, "rose": bool,
}

CLI:
  python -m loop.over_containment          the read-only verdict over samples
  python -m loop.over_containment --json    the raw dataset (machine-readable)

Stdlib only, local-first, no network. Ends with a clear result on stdout
(D-6): done | report. Read-only: it names the over-containment and the
one move; the cut stays the owner's (D-4).
"""

import argparse
import json
import sys

# The discriminator's thresholds. A stabilization counts as EARNED only if
# its coherence both ended high (it settled) and rose to there from a low
# start (it was uncertain first) under input that actually reached it.
STABLE_FLOOR = 0.70    # coherence_now >= this => the signal has stabilized
LOW_START_CEIL = 0.50  # coherence_start <= this => it began from uncertainty
RISE_MIN = 0.20        # coherence_now - coherence_start >= this => it rose


def _trials(signal):
    raw = signal.get("trials")
    return list(raw) if isinstance(raw, list) else []


def _variety_trials(trials):
    """The inputs that were risky/novel — the ones that could have broken the
    signal. A trial that is neither novel nor a refusal is incumbent input:
    it cannot test a stabilization (it is exactly what the signal already
    expects). Only variety counts as a test."""
    return [t for t in trials
            if isinstance(t, dict) and (t.get("novel") or t.get("refused"))]


def classify(signal):
    """Pure: is this stabilization predictive, or trivial over-containment?

    The check (§10): predictiveness is DERIVED, never read off the signal.
    A signal is `predictive` only if it (a) stabilized — coherence ended
    high — AND (b) was tested — variety/refusal/novel input actually reached
    it — AND (c) rose from a low start under that input. Miss any leg and it
    is `trivial-overcontainment`: stable because untouched, the shadow this
    counter-test exists to catch. Crucially, a signal that asserts it is
    predictive (or asserts a coherence rise) but recorded **no trials** fails
    the `tested` leg and is caught — the rise without a test is not evidence
    of prediction, it is the over-containment wearing the costume of health."""
    sid = signal.get("id", "<unnamed>")
    layer = signal.get("layer", "?")
    start = _coerce(signal.get("coherence_start"))
    now = _coerce(signal.get("coherence_now"))
    trials = _trials(signal)
    variety = _variety_trials(trials)
    n_novel = sum(1 for t in variety if t.get("novel"))
    n_refused = sum(1 for t in variety if t.get("refused"))

    stable = now >= STABLE_FLOOR
    tested = len(variety) >= 1
    rose = (start <= LOW_START_CEIL) and (now - start >= RISE_MIN)

    predictive = stable and tested and rose

    ev = [
        f"coherence {start:.2f}->{now:.2f} (delta {now - start:+.2f})",
        f"{len(trials)} trial(s) reached it; {len(variety)} were variety "
        f"({n_novel} novel, {n_refused} refused)",
        f"stable={stable} (floor {STABLE_FLOOR}); tested={tested}; "
        f"rose-from-low={rose} (start<= {LOW_START_CEIL}, rise>= {RISE_MIN})",
    ]

    if predictive:
        move = ("stabilized by becoming predictive — variety reached it and "
                "coherence rose from a low start under that input. Healthy; "
                "keep feeding it novel/risky input so the stability stays earned.")
        kind = "predictive"
    else:
        why = _trivial_reason(stable, tested, rose)
        move = (f"over-contained: {why}. The stability is not earned — point "
                "novel/risky input at it (T6: route un-vetted work to the gate; "
                "T7: feed inputs the equivalence classes have not seen) and "
                "watch whether coherence rises *under* that test. Until it is "
                "tested, read this 'stable' as untouched, not healthy.")
        kind = "trivial-overcontainment"

    return {
        "kind": kind,
        "subject": sid,
        "layer": layer,
        "evidence": ev,
        "move": move,
        "stable": stable,
        "tested": tested,
        "rose": rose,
    }


def _trivial_reason(stable, tested, rose):
    if not tested:
        return ("no variety/novel/refused input ever reached it — stable "
                "because untouched")
    if not stable:
        return "it has not actually stabilized (coherence stayed below the floor)"
    # tested and stable but did not rise from a low start
    return ("variety reached it but coherence never rose from a low start — "
            "its highness predates any test, so it is presumed trivial")


def _coerce(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return 0.0
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


# Sample signals for the CLI: one earned stabilization at each layer, and the
# two shapes of the shadow — an untested-but-high signal, and a fabricated one
# that ASSERTS predictiveness (and even a coherence rise) yet recorded no
# trial. The detector ignores the assertion and catches it on the `tested` leg.
SAMPLE_SIGNALS = (
    {
        "id": "action.value-gate.refusal-rate",
        "layer": "action",
        "coherence_start": 0.20,
        "coherence_now": 0.90,
        "trials": [
            {"novel": True, "refused": True},
            {"novel": True, "refused": False},
            {"novel": True, "refused": True},
            {"novel": False, "refused": False},
        ],
    },
    {
        "id": "representation.equivalence-class.seam",
        "layer": "representation",
        "coherence_start": 0.30,
        "coherence_now": 0.85,
        "trials": [
            {"novel": True, "refused": False},
            {"novel": True, "refused": True},
        ],
    },
    {
        "id": "action.placement-gate.always-passes",
        "layer": "action",
        "coherence_start": 0.95,
        "coherence_now": 0.98,
        "trials": [],  # nothing risky ever reached it — the T6 shadow
    },
    {
        "id": "representation.collapsed-class.pretends-predictive",
        "layer": "representation",
        # asserts both predictiveness AND a coherence rise, yet recorded no
        # trial — the costume of health over an untested stabilization.
        "claimed_predictive": True,
        "coherence_start": 0.10,
        "coherence_now": 0.99,
        "trials": [],
    },
)


def survey(signals=SAMPLE_SIGNALS):
    findings = [classify(s) for s in signals]
    over = [f for f in findings if f["kind"] == "trivial-overcontainment"]
    return {
        "findings": findings,
        "scanned": len(findings),
        "over_containment": len(over),
        "predictive": len(findings) - len(over),
    }


def render(d):
    lines = ["# Over-containment counter-test — predictive or trivial?", "",
             "_the shared shadow of T6 (action space) and T7 (representation "
             "space): a stabilization is healthy only if it was tested; "
             "read-only, the cut stays yours (D-4)._", "",
             f"Surveyed {d['scanned']} signal(s): {d['predictive']} predictive, "
             f"{d['over_containment']} over-contained.", ""]
    for f in d["findings"]:
        mark = "OK" if f["kind"] == "predictive" else "!!"
        lines.append(f"[{mark}] `{f['subject']}` ({f['layer']}) — {f['kind']}")
        for ev in f["evidence"]:
            lines.append(f"    · {ev}")
        lines.append(f"    -> {f['move']}")
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true",
                    help="emit the raw dataset (machine-readable), not the prose")
    args = ap.parse_args(argv)

    d = survey()
    if args.json:
        print(json.dumps(d, indent=2, sort_keys=True))
    else:
        print(render(d))
    n = d["over_containment"]
    if n:
        print(f"result: report — {n} signal(s) flagged as "
              f"trivial-overcontainment; each carries one move (the cut is "
              f"yours, D-4)")
    else:
        print("result: done — every surveyed stabilization reads as predictive")
    return 0


if __name__ == "__main__":
    sys.exit(main())
