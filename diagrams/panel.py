#!/usr/bin/env python3
"""panel.py — judgment as a PANEL of SMEs, not one omniscient judge.

bdo, 2026-06-21: judging an artifact is "a meeting of two or more SMEs, a panel
of experts." We kept trying to make ONE judge (the diagram taskmaster) catch
everything, and it kept missing what wasn't its expertise — most sharply, that
the gateway diagram OMITTED policy / authN-Z / attribution. That miss never
belonged to the diagram-SME; it belongs to the expert over the CORPUS.

So judgment is a panel. Three seats (the resolution of bdo's two questions):

  - the DIAGRAM-SME — is it a good diagram? (composition / layout / placement /
    topology). Reuses judge.py; reads the exemplar library as its canon.
  - the CORPUS-SME — is it FAITHFUL to the corpus it depicts? Reads the REAL
    corpus (repo files) and checks the drawing's entities/relations against it —
    the expert that catches an omission or a fabrication. The corpus is GROUND
    TRUTH (the log-is-truth grain); the corpus-SME is its expert reader.
  - the STAKEHOLDER — owns the corpus, sets its intent, holds the LAST STOP
    (D-4). Distinct from the corpus-SME: expertise knows the corpus, ownership
    governs it. The stakeholder's accept is a GESTURE, not inference — absent a
    stamp the seat is PENDING and the panel only *recommends*.

The POINT-BASED POLICY is the meeting's combining rule (bdo's point system,
turned on the act of judging): each expert seat casts points toward accept; the
policy weights and sums them against a threshold; the stakeholder is the last
stop. Owner-settable like any setpoint — the default here weights corpus
fidelity heaviest, and requires BOTH a good diagram AND a faithful one to pass.

Local-first: the only outward act is the `claude -p` spawn, via the gate.py
rail, in this pen — never in loop/. Reads specs and corpus files; writes nothing
but its stdout verdict.

Usage:
  python diagrams/panel.py <spec.json> --corpus <path> [--corpus <path> ...] [--stamp <who>]
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import compose  # noqa: E402
import judge    # noqa: E402

GATE = HERE.parent / ".claude" / "skills" / "gate"
sys.path.insert(0, str(GATE))
try:
    import gate as _gate
except Exception:  # pragma: no cover
    _gate = None

# The point policy — owner-settable (a default here; in the live system it is an
# admitted record, like a setpoint). Each EXPERT seat casts its weight toward
# accept; the stakeholder is the last stop, not a point-holder.
POINT_POLICY = {
    "weights": {"diagram-sme": 2, "corpus-sme": 3},  # fidelity weighed heaviest
    "pass_threshold": 5,   # of 5 available expert points → BOTH must pass
    "stakeholder_is_last_stop": True,
}


def _seat(name, verdict, points, reason, detail=None):
    return {"seat": name, "verdict": verdict, "points": points,
            "reason": reason, "detail": detail}


def diagram_sme(spec):
    """Is it a good diagram? Reuses the taskmaster (composition/layout/topology)."""
    status, payload = judge.judge(spec)
    if status != "verdict":
        return _seat("diagram-sme", "abstain", 0,
                     f"could not judge: {payload.get('reason', status)}")
    v = payload.get("verdict")
    pts = POINT_POLICY["weights"]["diagram-sme"] if v == "accept" else 0
    return _seat("diagram-sme", v, pts, payload.get("consequence", ""),
                 {"layout_rank": payload.get("layout_rank"),
                  "placement": payload.get("placement")})


def corpus_sme(spec, corpus_paths):
    """Is it FAITHFUL to the corpus it depicts? Reads the real corpus files and
    judges the drawing's entities/relations against them."""
    if _gate is None:
        return _seat("corpus-sme", "abstain", 0, "no gate rail to launch the SME")
    corpus = []
    for p in corpus_paths:
        fp = HERE.parent / p
        if fp.exists():
            corpus.append(f"### {p}\n{fp.read_text(encoding='utf-8')[:6000]}")
    entities = [str(n.get("label", "")).split("\n")[0]
                for n in spec.get("nodes", [])]
    for n in spec.get("nodes", []):
        if n.get("type") == "chips":
            entities += [str(i.get("label", i) if isinstance(i, dict) else i)
                         for i in (n.get("items") or [])]
    prompt = "\n".join([
        "# You are the CORPUS-SME on a judging panel.\n",
        "You are NOT judging whether this is a good-looking diagram — another SME "
        "does that, and you must not comment on layout or aesthetics. You judge "
        "ONE thing: is the diagram FAITHFUL to the corpus it depicts? Does it name "
        "the entities and relations that are ACTUALLY in the corpus, OMIT nothing "
        "essential the corpus contains, and FABRICATE nothing the corpus does not? "
        "Distinguish what is REAL in the corpus from what is merely proposed or "
        "aspirational there.\n",
        "## The corpus — GROUND TRUTH (what is actually real in the system)\n",
        "\n\n".join(corpus) if corpus else "_(no corpus files resolved)_",
        "\n## The diagram's declared entities (nouns it claims exist)\n",
        json.dumps(entities, indent=2),
        "\n## Your output — reason in the open, then the FINAL line, exactly:\n",
        'VERDICT {"verdict": "<faithful|drifted>", "reason": "<what matches the '
        'corpus, what it OMITS, what it FABRICATES — cite the corpus>", '
        '"omissions": ["entities in the corpus the diagram drops"], '
        '"fabrications": ["entities the diagram shows that the corpus does not '
        'support (or only aspirationally)"]}',
        "\nVerdict 'drifted' if it omits something essential or fabricates/over-"
        "claims. The §10 test binds you: if 'faithful' could not have been "
        "'drifted', you did not check.",
    ])
    try:
        verdict, reason, raw, trace = _gate.launch_claude(
            prompt, atom_id=None, node_id="corpus-sme")
    except Exception as e:
        return _seat("corpus-sme", "abstain", 0, f"SME did not return: {e}")
    objs = _gate._verdict_objects(raw)
    full = objs[-1] if objs else {"verdict": verdict, "reason": reason}
    faithful = full.get("verdict") == "faithful"
    pts = POINT_POLICY["weights"]["corpus-sme"] if faithful else 0
    return _seat("corpus-sme", full.get("verdict"), pts, full.get("reason", ""),
                 {"omissions": full.get("omissions"),
                  "fabrications": full.get("fabrications"), "trace": str(trace)})


def stakeholder_seat(spec, stamp=None):
    """The owner over the corpus — sets the intent, holds the last stop (D-4).
    The accept is a gesture, not inference: absent a stamp the seat is PENDING."""
    if stamp:
        return _seat("stakeholder", "accept", 0, f"owner stamp: {stamp}")
    return _seat("stakeholder", "pending", 0,
                 "the owner over this corpus has not cast — the panel only "
                 "recommends; the last stop is the owner's gesture (D-4)")


def convene(spec, corpus_paths, stamp=None):
    seats = [diagram_sme(spec), corpus_sme(spec, corpus_paths),
             stakeholder_seat(spec, stamp)]
    expert_points = sum(s["points"] for s in seats if s["seat"] != "stakeholder")
    passed = expert_points >= POINT_POLICY["pass_threshold"]
    sh = next(s for s in seats if s["seat"] == "stakeholder")
    if sh["verdict"] == "refuse":
        decision = "REFUSED — stakeholder veto (D-4, the last stop)"
    elif sh["verdict"] == "pending":
        decision = ("RECOMMEND-ACCEPT — awaiting the owner's stamp"
                    if passed else "RECOMMEND-REVISE — awaiting the owner's stamp")
    else:
        decision = "ACCEPTED" if passed else "REVISE"
    return {"decision": decision, "expert_points": expert_points,
            "threshold": POINT_POLICY["pass_threshold"], "seats": seats}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("spec")
    ap.add_argument("--corpus", action="append", default=[],
                    help="a corpus file the corpus-SME judges fidelity against")
    ap.add_argument("--stamp", default=None, help="the owner's last-stop stamp (who)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    result = convene(spec, args.corpus, args.stamp)
    if args.json:
        print(json.dumps(result, indent=2))
        return 0
    print(f"PANEL DECISION: {result['decision']}")
    print(f"  expert points: {result['expert_points']}/{result['threshold']} to pass\n")
    for s in result["seats"]:
        print(f"  [{s['seat']}] {s['verdict']}  (+{s['points']})")
        print(f"     {s['reason']}")
        d = s.get("detail") or {}
        if d.get("omissions"):
            print(f"     OMITS: {d['omissions']}")
        if d.get("fabrications"):
            print(f"     FABRICATES/over-claims: {d['fabrications']}")
        if d.get("layout_rank") is not None:
            print(f"     layout_rank: {d['layout_rank']}/5")
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
