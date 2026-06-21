#!/usr/bin/env python3
"""The experience-judge: the diagram organ's inference pole.

`qa.py` is the deterministic floor — it refuses a diagram that *lies* (orphan,
crossing, overloaded symbol) or is *illegible* (label clipped, node off-canvas).
But a diagram can pass every honesty check and still be a 2/5: dead whitespace,
no focal point, a shape that fights its own meaning. Composition, hierarchy,
balance, semantic-geometry fit are **felt judgments** — and as bdo put it
(2026-06-20), *E requires inference*: no deterministic rule rates experience.

This pen is that inference half. The organ's own `CLAUDE.md` already names it:
*"a generative pole (a description / gesture, later **bounded inference**) feeds
an ingress gate with teeth ... a deterministic body."* `qa.py` is the gate with
teeth; this is the bounded-inference pole, the half that was never built.

The shape (the `#343` grain — judge deterministically-composed facts):

  1. **floor first.** Run `qa.py`. If it denies, REFUSE to judge — you don't
     grade the composition of a diagram that lies. The floor is never softened
     by this layer; the verdict rides strictly *on top* of an honest diagram.
  2. **compose the facts.** A pure pass extracts the layout's measurable visual
     properties — dead-space bands, caption overflow, content fill, node-size
     spread (a hierarchy proxy). Deterministic evidence, not taste.
  3. **judge.** Launch a mortal headless mind (the `gate.py` rail: explicit
     model, neutral cwd, json out, brace-parsed verdict) with the canon's
     **experience principles** as its SME prompt, the composed facts, and the
     rendered SVG source. It returns a rating with reasons cited to a principle,
     and — the §10 teeth — it must be able to say *poor*.

Local-first: the only outward act is the `claude -p` spawn, and it lives in this
pen (the skills/gate rail), never in `loop/` (no subprocess there). Reads a spec
or an already-rendered SVG; writes nothing but its stdout verdict and the gate
rail's gitignored trace.

Usage:
  python diagrams/judge.py <spec.json>               # facts + inference verdict
  python diagrams/judge.py <spec.json> --facts-only  # the deterministic facts, no spawn
  python diagrams/judge.py <spec.json> --json        # machine-readable verdict
"""
from __future__ import annotations
import argparse
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import compose  # the renderer (spec -> SVG) and the closed node vocab
import qa        # the deterministic floor

# The gate rail (the proven headless-mind launcher): explicit model, neutral cwd
# to dodge the project session hooks, json unwrap, brace-matched verdict parse,
# always-traced. Imported, never re-derived — one rail, no drift (I-4).
GATE = HERE.parent / ".claude" / "skills" / "gate"
sys.path.insert(0, str(GATE))
try:
    import gate as _gate
except Exception:  # pragma: no cover - degrade loudly if the rail moves
    _gate = None

CAPTION_PX = 12          # compose.render_caption font size
CAPTION_CHAR_W = compose.MONO_CHAR_W * (CAPTION_PX / compose.LABEL_SIZE)
CAPTION_X = 32           # compose hardcodes the caption at x=32
TITLE_BASELINE_Y = 38    # compose hardcodes the title baseline


# --- the deterministic facts (the #343 composed evidence) ---

def _boxes(spec):
    out = []
    for n in spec.get("nodes", []):
        out.append((n["x"], n["y"], n["x"] + n["w"], n["y"] + n["h"]))
    for key in ("subgraphs", "regions"):
        for s in spec.get(key, []) or []:
            out.append((s["x"], s["y"], s["x"] + s["w"], s["y"] + s["h"]))
    return out


def layout_facts(spec) -> dict:
    """The render's measurable visual properties. Pure, deterministic — the
    evidence the inference judge weighs, never the verdict itself."""
    w, h = spec.get("size", [900, 500])
    boxes = _boxes(spec)
    nodes = spec.get("nodes", [])

    facts: dict = {"canvas": {"w": w, "h": h}}

    if boxes:
        x1 = min(b[0] for b in boxes)
        y1 = min(b[1] for b in boxes)
        x2 = max(b[2] for b in boxes)
        y2 = max(b[3] for b in boxes)
        facts["content_bbox"] = {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
        # Margins as fractions of the canvas. The top margin is measured from the
        # title baseline (real content starts below the title), so a large value
        # is a genuine dead band, not the expected title gutter.
        facts["dead_bands"] = {
            "top": round(max(0.0, y1 - (TITLE_BASELINE_Y + 12)) / h, 3),
            "bottom": round(max(0.0, h - y2) / h, 3),
            "left": round(max(0.0, x1) / w, 3),
            "right": round(max(0.0, w - x2) / w, 3),
        }
        content_area = (x2 - x1) * (y2 - y1)
        facts["fill_ratio"] = round(content_area / float(w * h), 3)
    else:
        facts["content_bbox"] = None
        facts["dead_bands"] = None
        facts["fill_ratio"] = 0.0

    # Caption containment. The renderer now WRAPS the caption (compose.wrap_caption),
    # so "clipped" must mean "overflows the canvas even after wrapping" — not
    # "exceeds one line". Using the pre-wrap single-line width here faulted
    # captions that render fine wrapped (the phantom the climb loop surfaced;
    # a tooth biting wrong — heal.py's territory). Share the one wrap definition
    # (I-4) so the judge, the renderer, and qa.check_caption never disagree.
    caption = str(spec.get("caption", ""))
    if caption:
        available = w - CAPTION_X - 8
        try:
            lines = compose.wrap_caption(caption, available)
        except Exception:
            lines = caption.split("\n")
        # The block sits at the foot: last baseline at h-18, lines stack 15px up.
        block_top = (h - 18) - (len(lines) - 1) * 15 - 12
        body_bottom = (facts.get("content_bbox") or {}).get("y2", 0)
        facts["caption"] = {
            "chars": len(caption),
            "wrapped_lines": len(lines),
            "available_px": round(available),
            "clipped": block_top < body_bottom or block_top < 0,
        }

    # Hierarchy proxy: the spread of node areas. If every node is ~the same size,
    # nothing is visually emphasized — a flat composition with no focal point.
    areas = [n["w"] * n["h"] for n in nodes if n.get("type") != "chips"]
    if len(areas) >= 2:
        med = statistics.median(areas)
        facts["node_areas"] = {
            "count": len(areas),
            "min": min(areas), "max": max(areas), "median": round(med),
            # max/median ~ 1.0 => uniform sizing => no size-borne hierarchy.
            "emphasis_ratio": round(max(areas) / med, 2) if med else None,
        }
    return facts


# --- the taskmaster: judge the CONSEQUENCE of use, not a checklist ---
#
# bdo's correction (2026-06-21): the judge must NOT ask for specific things. A
# checklist of principles is whack-a-mole — every rule it adds, a fresh failure
# slips past (the §10 spiral, forever; his eye kept finding the next one). So it
# judges ONE thing: the CONSEQUENCE of USING the diagram, against its INTENT —
# freeform, filling the whole intent-volume rather than sampling points on its
# surface — and it NAMES that consequence. It is calibrated by EXEMPLARS and
# NOTORIETIES (good/bad uses, by name), not by enumerated criteria: the
# model-free, exemplar-net shape (the herald's reputation, the Pattern Commons),
# the consequence-gate turned on diagrams. A taskmaster, not an inspector.

EXEMPLAR_DIR = HERE / "exemplars"

# The intent every architecture diagram must serve — the consequence it must
# produce when used. A spec may declare a sharper `intent`; this is the floor.
BASE_INTENT = (
    "A reader with little or no prior context grasps what the diagram is trying "
    "to inform them of — its specific informative intent — and reconstructs the "
    "system: its named parts and how they relate. BOTH carry that intent and BOTH "
    "are judged: the TOPOLOGY (nouns name parts, verbs name relations) AND the "
    "COMPOSITION — the picture itself: balance that fills the frame, a clear focal "
    "anchor on the subject, flow that does not double back, shapes that suggest "
    "their meaning. A topologically-correct diagram that is an ugly, sagging, or "
    "tangled picture FAILS to carry its intent just as a handsome diagram of prose "
    "does. And the PLACEMENT is part of the picture: where each node SITS — its "
    "site — must reflect the topology (a loop laid out as a ring, a hierarchy as "
    "stacked layers, even spacing, things aligned), so the arrangement ITSELF "
    "informs. A scattered or floating placement — nodes sitting wherever rather "
    "than where the structure puts them, a loop that does not read as a loop, a "
    "lonely node tethered across the void — fails to carry intent even when every "
    "label is correct. Judge whether the whole artifact — words, picture, and "
    "placement together — carries its informative intent."
)


def load_exemplars():
    """The calibration library — good exemplars and notorieties, by name. A
    growing 'sauce' (the pentimento): bdo flags a bad diagram, it becomes a
    notoriety; a good one, an exemplar. The judge nets use against it, and the
    authoring agents read it to avoid producing a known notoriety — one shared
    library refining both the making and the judging."""
    out = []
    if EXEMPLAR_DIR.exists():
        for p in sorted(EXEMPLAR_DIR.glob("*.json")):
            try:
                out.append(json.loads(p.read_text(encoding="utf-8")))
            except Exception:
                pass
    return out


def compose_prompt(spec, svg, facts) -> str:
    intent = spec.get("intent") or BASE_INTENT
    exemplars = load_exemplars()
    good = [e for e in exemplars if e.get("kind") == "exemplar"]
    bad = [e for e in exemplars if e.get("kind") == "notoriety"]
    return "\n".join([
        "# You are a taskmaster. Judge the CONSEQUENCE of USING this diagram.\n",
        "You do not run a checklist of features. You judge ONE thing: if a reader "
        "USES this diagram for its intent, what is the CONSEQUENCE — and does that "
        "consequence ALIGN with the intent? Name the consequence in plain words.\n",
        "## The intent (the consequence the diagram must produce)\n",
        intent,
        "\n## Method — fill the volume, do not sample points\n",
        "Imagine actually using the diagram cold. Read every label as a stranger "
        "would, AND look at the picture as a stranger would. What system do you "
        "reconstruct, and is the picture itself good enough to carry it — or does "
        "it sag into a void, bury its subject, tangle its flow, wear a shape that "
        "fights its word, or SCATTER its nodes so the placement does not reflect "
        "the structure (a loop that does not read as a loop, a hierarchy not in "
        "layers, a node floating with one tether across an empty gap)? Both the "
        "words and the picture must carry the "
        "intent; a topology-correct but ugly diagram still fails. Your verdict is "
        "the NAMED CONSEQUENCE of that use, judged against the intent — never a "
        "tally of rules. Weigh the deterministic facts and the SVG as evidence.\n",
        "## You are calibrated by exemplars, not rules\n",
        "GOOD EXEMPLARS (uses that land):\n"
        + (json.dumps(good, indent=2) if good else "_(none yet)_"),
        "\nNOTORIETIES (uses that fail, by name — does this diagram fall into one?):\n"
        + (json.dumps(bad, indent=2) if bad else "_(none yet)_"),
        "\n---\n",
        "## The diagram under judgment\n",
        "### Deterministically-composed layout facts (evidence, not criteria)\n",
        "```json", json.dumps(facts, indent=2), "```",
        "\n### The rendered SVG (read its geometry AND every label cold)\n",
        "```svg", svg, "```",
        "\n---\n",
        "## Your output — read this twice\n",
        "You are a mortal process. Judge this diagram's consequence-of-use against "
        "the intent, netting it against the exemplars and notorieties. Reason in "
        "the open. Then, on the FINAL line, output EXACTLY this and nothing after:\n",
        'VERDICT {"verdict": "<accept|refuse>", "consequence": "<in plain words, '
        'what happens when a reader uses this diagram cold>", "aligns_with_intent": '
        '<true|false>, "layout_rank": <integer 1-5: the quality of the PLACEMENT '
        'itself — where the nodes sit, whether the arrangement reflects the '
        'topology (a loop as a ring, a hierarchy as layers), alignment and even '
        'spacing; 5 = the placement itself informs at a glance, 3 = serviceable, '
        '1 = scattered/floating>, "placement": "<one line on the layout and sites '
        '— what the placement does right or wrong>", "nearest_notoriety": "<a '
        'notoriety id, or none>", "note": "<the crux>"}',
        "\nRefuse when the consequence of use does not align with the intent. Name "
        "the consequence; if it matches a notoriety, name it. The §10 test binds "
        "you: if your verdict could not have been the opposite, you did not judge.",
    ])


# --- the run ---

def render_svg(spec) -> str:
    return compose.render(spec)


def judge(spec, *, facts_only=False):
    """Returns (status, payload). status in {floor-deny, facts, verdict, error}."""
    issues = qa.evaluate(spec)
    errors = [i for i in issues if i[0] == "error"]
    if errors:
        return "floor-deny", {
            "reason": "qa.py denies this diagram — the honesty floor fails, so "
                      "there is nothing to grade for experience yet (fix the lie "
                      "first; the judge never softens the floor).",
            "denials": [{"principle": p, "message": m, "ctx": c}
                        for _s, p, m, c in errors],
        }

    facts = layout_facts(spec)
    if facts_only:
        return "facts", facts

    if _gate is None:
        return "error", {"reason": "the gate rail (.claude/skills/gate/gate.py) "
                         "could not be imported — no mortal mind to launch."}

    svg = render_svg(spec)
    prompt = compose_prompt(spec, svg, facts)
    try:
        verdict, reason, raw, trace = _gate.launch_claude(
            prompt, atom_id=None, node_id="diagram-experience-judge")
    except Exception as e:  # the mind hung/crashed — surface, don't swallow
        return "error", {"reason": f"the headless judge did not return a verdict: {e}"}

    # launch_claude returns only verdict+reason from the object; re-parse the raw
    # to recover the full structured payload (rating, findings, the §10 check).
    objs = _gate._verdict_objects(raw)
    full = objs[-1] if objs else {"verdict": verdict, "reason": reason}
    full["_facts"] = facts
    full["_trace"] = str(trace)
    return "verdict", full


def _print_human(status, payload):
    if status == "floor-deny":
        print("FLOOR-DENY — qa.py refuses; experience is not judged.")
        print(f"  {payload['reason']}")
        for d in payload["denials"]:
            print(f"  deny [{d['principle']}] {d['message']}")
        return 2
    if status == "facts":
        print(json.dumps(payload, indent=2))
        return 0
    if status == "error":
        print(f"result: report — {payload['reason']}")
        return 1
    # verdict
    verdict = payload.get("verdict", "?")
    print(f"TASKMASTER: {verdict.upper()}")
    print(f"  consequence of use: {payload.get('consequence', '?')}")
    print(f"  aligns with intent: {payload.get('aligns_with_intent', '?')}")
    if payload.get("layout_rank") is not None:
        print(f"  LAYOUT / placement rank: {payload.get('layout_rank')}/5")
        print(f"  placement: {payload.get('placement', '?')}")
    nn = payload.get("nearest_notoriety")
    if nn and nn != "none":
        print(f"  falls into notoriety: {nn}")
    if payload.get("note"):
        print(f"  crux: {payload['note']}")
    print(f"  (trace: {payload.get('_trace')})")
    return 0 if verdict == "accept" else 2


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("spec", help="path to a compose.py JSON spec")
    ap.add_argument("--facts-only", action="store_true",
                    help="print the deterministic layout facts and stop (no spawn)")
    ap.add_argument("--json", action="store_true", help="machine-readable verdict")
    args = ap.parse_args(argv)

    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    status, payload = judge(spec, facts_only=args.facts_only)

    if args.json:
        print(json.dumps({"status": status, **(payload if isinstance(payload, dict) else {"value": payload})}, indent=2))
        return 0 if status in ("facts", "verdict") and payload.get("verdict", "accept") == "accept" else 2
    return _print_human(status, payload)


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
