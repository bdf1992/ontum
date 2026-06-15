#!/usr/bin/env python3
"""The energy-per-act fold (done-line 0080): anima's energy/tempo dimension —
what an act costs, folded from compute the log already carries.

Agenda [[anima]] names three dimensions of an ontum's felt field: *pulse* (the
beat of an act), *rhythm/breath* (the orchestrator's heat/cool), and
*energy/tempo* (what an act costs). The rhythm dimension is already sensed by
`loop/temporal` (the hour's lean over the slow loop). This is the energy/tempo
taste: every act on the log has a beat (how long it took) and a yield (how much
meaning it produced), and folding those tells whether the loop's thinking ran
cheap or strained.

It captures **nothing new**. The compute is already on the receipts: inference
acts carry `latency_ms` (the beat) and `tokens` (the yield), recorded by the
gateway the day it first ran (and jammed — issues #95/#96). An *act* here is any
receipt already carrying a numeric `latency_ms`; an absent `tokens` is absence,
not zero — a jammed act burns the beat and yields nothing, and saying it yielded
zero tokens-per-second would be a lie the median and tempo must not tell.

The teeth (§10): a **strain** fold names energy spent without proportional
yield — *burned* acts (the beat happened, nothing came out: outcome ≠ ok, or no
tokens) and *fallback* acts (`fallback_from` set: a second act's energy spent to
answer once). Tempo (tokens/sec) is computed over yielding acts only, so a
burned act's huge latency can never masquerade as throughput. Two locally-valid
receipts — one clean, one burned — refuse to fit one productive picture, and the
fold separates them rather than averaging the strain away.

The shape mirrors `loop/gaps.py` and `loop/temporal.py`: a pure read-only fold
(I-3), stdlib only (loop/ hard rule), every measure citing the receipt ids it
folds (the census / term-economy citation discipline — an auditable pointer,
never prose). A missing log is an absence (`acts == []`), never a crash.

CLI:
  python -m loop.energy            the energy-per-act read
  python -m loop.energy --json     the dataset, machine-readable
"""

import argparse
import json
import sys
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT, Fold

# loop/energy.py -> loop/ -> repo root. Works the same in a worktree.
REPO = Path(__file__).resolve().parent.parent

# the compute already on the log: the beat and the yield of an act.
BEAT = "latency_ms"
YIELD = "tokens"


def _num(v):
    """The numeric value of an energy field, or None. A bool is not a number
    here (JSON true/false is never a latency), and a null/absent/garbage field
    is absence — not coerced to zero, which would let a jammed act read as a
    real measurement (the one hard rule of this fold)."""
    if isinstance(v, bool):
        return None
    return v if isinstance(v, (int, float)) else None


def energy_acts(receipts):
    """Every receipt that carries energy — a measurable act. The beat
    (`latency_ms`) is the spine: every act, even one that failed, took time, so
    an act has energy iff it carries a numeric beat. The yield (`tokens`) is
    optional — a burned act has a beat and no yield. Read-only; nothing is
    captured, only read."""
    acts = []
    for r in receipts:
        beat = _num(r.get(BEAT))
        if beat is None:
            continue  # no beat, no measurable act (absence is information)
        acts.append({
            "id": r.get("id"),
            "ts": r.get("ts"),
            "latency_ms": beat,
            "tokens": _num(r.get(YIELD)),
            "outcome": r.get("outcome"),
            "mind": r.get("mind"),
            "type": r.get("type"),
            "surface": r.get("surface"),
            "fallback_from": r.get("fallback_from"),
            # tempo of this single act: tokens per second, only when it both
            # produced tokens and took time. None otherwise — never a divide,
            # never a zero that lies.
            "tempo_tokens_per_s": (
                _num(r.get(YIELD)) / (beat / 1000)
                if _num(r.get(YIELD)) is not None and beat > 0 else None),
        })
    return acts


def is_burned(act):
    """The beat happened but nothing came out: the act errored, or it yielded
    no tokens. Energy spent for no value — the first half of strain."""
    if act["outcome"] is not None and act["outcome"] != "ok":
        return True
    return act["tokens"] in (None, 0)


def _median(xs):
    s = sorted(xs)
    n = len(s)
    if not n:
        return None
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2


def summarize(acts):
    """The aggregate pulse and tempo over a set of acts. Tempo is computed over
    *yielding* acts only (tokens present and a positive beat) — a burned act's
    latency is real cost but never productive throughput, so it stays out of
    the tokens-per-second figure. Absence stays absence: with no yielding act,
    tempo and mean-tokens are None, never 0."""
    n = len(acts)
    lat = [a["latency_ms"] for a in acts]
    yielding = [a for a in acts if a["tokens"] is not None and a["latency_ms"] > 0]
    tok = [a["tokens"] for a in acts if a["tokens"] is not None]
    tempo_beat = sum(a["latency_ms"] for a in yielding)
    tempo_tok = sum(a["tokens"] for a in yielding)
    return {
        "acts": n,
        "ids": [a["id"] for a in acts],
        "total_latency_ms": sum(lat),
        "mean_latency_ms": (sum(lat) / n) if n else None,
        "median_latency_ms": _median(lat),
        "total_tokens": sum(tok) if tok else 0,
        "mean_tokens": (sum(tok) / len(tok)) if tok else None,
        "yielding_acts": len(yielding),
        "tempo_tokens_per_s": (tempo_tok / (tempo_beat / 1000)) if tempo_beat else None,
    }


def strain(acts):
    """Energy spent without proportional yield — anima sensing waste and jam.
    Two real divergences between energy-spent and value-produced:

      burned    the beat happened, nothing came out (outcome ≠ ok, or no
                tokens): latency burned, zero yield.
      fallback  a *second* spend for one answer (`fallback_from` set): a prior
                act's energy was wasted and this one cost again.

    `wasted_latency_ms` is the beat that produced nothing — the punchy number
    anima reports: how much of the loop's thinking-time bought no meaning."""
    burned = [a for a in acts if is_burned(a)]
    fallbacks = [a for a in acts if a.get("fallback_from")]
    return {
        "burned": burned,
        "burned_ids": [a["id"] for a in burned],
        "fallbacks": fallbacks,
        "fallback_ids": [a["id"] for a in fallbacks],
        "wasted_latency_ms": sum(a["latency_ms"] for a in burned),
    }


def group_by(acts, key):
    """Acts summarized within each value of `key` (mind, outcome, …), sorted by
    the key for byte-deterministic output. A missing key value reads as '—'
    (absence named, never guessed)."""
    groups = {}
    for a in acts:
        groups.setdefault(a.get(key) or "—", []).append(a)
    return {k: summarize(v) for k, v in sorted(groups.items(), key=lambda kv: str(kv[0]))}


def energy(root=None, repo=REPO):
    """The full read: fold the receipts into acts, summarize, group, and name
    the strain. Pure over the log; writes nothing. A missing log folds to an
    empty act set (absence is information)."""
    root = root if root is not None else (repo / DEFAULT_ROOT)
    fold = Fold(Path(root)) if (Path(root) / "log").is_dir() else None
    receipts = fold.receipts if fold else []
    acts = energy_acts(receipts)
    return {
        "acts": acts,
        "summary": summarize(acts),
        "by_mind": group_by(acts, "mind"),
        "by_outcome": group_by(acts, "outcome"),
        "strain": strain(acts),
    }


# --- render -----------------------------------------------------------------

def _ms(v):
    return "—" if v is None else f"{v / 1000:.1f}s"


def _round(v, n=1):
    return None if v is None else round(v, n)


def render(result):
    s = result["summary"]
    st = result["strain"]
    print("energy-per-act — anima's energy/tempo dimension (folded from the log)")
    if not result["acts"]:
        print("  no acts carry energy yet — no receipt on the log carries "
              "latency_ms; anima has nothing to taste here (absence, not zero)")
        return
    print(f"  pulse: {s['acts']} act(s) · total beat {_ms(s['total_latency_ms'])} "
          f"· mean {_ms(s['mean_latency_ms'])} · median {_ms(s['median_latency_ms'])}")
    tempo = ("—" if s["tempo_tokens_per_s"] is None
             else f"{s['tempo_tokens_per_s']:.1f} tok/s")
    print(f"  yield: {s['total_tokens']} tokens over {s['yielding_acts']} "
          f"yielding act(s) · tempo {tempo}")

    if st["burned"] or st["fallbacks"]:
        print(f"  strain — energy spent without yield "
              f"({_ms(st['wasted_latency_ms'])} of the beat bought nothing):")
        for a in st["burned"]:
            print(f"    [burned]   {a['id']} — {_ms(a['latency_ms'])} beat, "
                  f"{a['tokens'] if a['tokens'] is not None else 'no'} tokens, "
                  f"outcome {a['outcome']} ({a['mind'] or '—'})")
        for a in st["fallbacks"]:
            print(f"    [fallback] {a['id']} — fell back from "
                  f"{a['fallback_from']} to {a['mind'] or '—'}: a second act's "
                  f"energy ({_ms(a['latency_ms'])}) for one answer")
    else:
        print("  no strain — every act yielded; the beat bought meaning")

    print("  by mind:")
    for mind, sub in result["by_mind"].items():
        tempo = ("—" if sub["tempo_tokens_per_s"] is None
                 else f"{sub['tempo_tokens_per_s']:.1f} tok/s")
        print(f"    {mind}: {sub['acts']} act(s), total beat "
              f"{_ms(sub['total_latency_ms'])}, tempo {tempo}")
    print("  by outcome:")
    for outcome, sub in result["by_outcome"].items():
        print(f"    {outcome}: {sub['acts']} act(s), total beat "
              f"{_ms(sub['total_latency_ms'])}, {sub['total_tokens']} tokens")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=None,
                    help="records root (default: repo .ai-native)")
    ap.add_argument("--json", action="store_true", help="emit the dataset")
    args = ap.parse_args(argv)

    result = energy(root=args.root)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, default=_round))
        return 0

    render(result)
    if not result["acts"]:
        print("result: report — no acts carry energy on the log yet; the fold "
              "reads what is there (zero new capture), and there is nothing to "
              "taste until an act records its beat")
        return 0
    st = result["strain"]
    if st["burned"] or st["fallbacks"]:
        print(f"result: report — {result['summary']['acts']} act(s) measured; "
              f"{len(st['burned'])} burned ({_ms(st['wasted_latency_ms'])} of "
              f"beat wasted), {len(st['fallbacks'])} fallback(s). The strain is "
              "the signal.")
        return 0
    print(f"result: done — {result['summary']['acts']} act(s) measured, all "
          "yielded; no strain on the record")
    return 0


if __name__ == "__main__":
    sys.exit(main())
