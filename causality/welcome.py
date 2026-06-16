#!/usr/bin/env python3
"""Causality's welcome mat (done-line 0095): the landing page — the system's
first impression, folding the live felt-field from records the loop already
keeps.

bdo's frame (2026-06-16): agenda [[anima]]'s felt-field is *emergent* — the
sauce is the process, named after first taste. A session does not author the
felt-field; it builds the surface the field emerges *through*. The welcome mat
is the first impression, and to be *capable of carrying* the felt-field it must
**fold** that field from real records — never paint it. A hand-authored "feels
alive" surface is mercury: it carries nothing.

So this is a **projection** (Causality's one hard rule: never a second source of
truth, no second write path). It reads the felt-field sensors that already live
on main and renders their three dimensions as one first impression:

  pulse         the beat of recent acts            (loop.energy's act fold)
  rhythm/breath the hour's lean (heat/steady/cool)  (loop.temporal's band)
  energy/tempo  what the acts cost + the strain     (loop.energy's summary/strain)

It re-senses nothing — Causality *reads* the sensors, loop owns them. Every felt
figure on the page is the number its fold emits (the census / term-economy
citation discipline); a fabricated constant would diverge from the fold, and the
§10 test (`tests/test_welcome.py`) catches it. An empty log renders **"absence"**
(no act carries the field yet), never a fake zero. `loop.impact` is deliberately
absent — it is not on main (open PR #149); this folds only committed bytes.

The render mirrors `loop/web.py`: stdlib only, self-contained, phone-readable, a
pure fold over the log (§14.1: a cache, never truth — delete it and a render
rebuilds it). There is no server, no POST, no verdict path: a welcome mat is
read.

CLI:
  python -m causality.welcome render            write the welcome page (static)
  python -m causality.welcome render --out P    to a path
  python -m causality.welcome --json            the felt-field dataset
  python -m causality.welcome --hour 8          a fixed moment (deterministic)
"""

import argparse
import html
import json
import sys
from pathlib import Path

from loop.energy import energy
from loop.reconcile import DEFAULT_ROOT
from loop.temporal import load_schedule, register_at

# causality/welcome.py -> causality/ -> repo root. Works the same in a worktree.
REPO = Path(__file__).resolve().parent.parent

# How the lean reads as a breath — color and a one-word feel. Pure presentation
# over loop.temporal's truth (the lean itself is the fold's, never recomputed).
LEAN_FEEL = {
    "heat":   ("#e7b04a", "running hot — exploring"),
    "steady": ("#9fd0a8", "steady — holding the line"),
    "cool":   ("#7fb4d4", "leaning cool — consolidating"),
}


# --- the fold (pure; the felt-field, read from the sensors) -----------------

def _ms(v):
    return "—" if v is None else f"{v / 1000:.1f}s"


def _tempo(v):
    return "—" if v is None else f"{v:.1f} tok/s"


def felt_field(root, hour, recent=5):
    """The live felt-field, folded — never painted. Reads `loop.energy` (pulse +
    energy/tempo + strain) and `loop.temporal` (rhythm: the hour's band). Pure
    over the log; writes nothing. A missing log folds to `empty` (absence is
    information, not a fake zero)."""
    e = energy(root=root)
    s = e["summary"]
    st = e["strain"]
    schedule, sched_source, problems = load_schedule(root)
    band = register_at(hour % 24, schedule)
    return {
        "empty": not e["acts"],
        "hour": hour % 24,
        "pulse": {
            "acts": s["acts"],
            # most-recent first: the freshest beats lead the first impression
            "recent": list(reversed(e["acts"]))[:recent],
        },
        "rhythm": ({"register": band["register"], "lean": band["lean"],
                    "quality": band["quality"]} if band else None),
        "rhythm_source": sched_source,
        "rhythm_problems": problems,
        "energy": {
            "total_latency_ms": s["total_latency_ms"],
            "mean_latency_ms": s["mean_latency_ms"],
            "median_latency_ms": s["median_latency_ms"],
            "total_tokens": s["total_tokens"],
            "yielding_acts": s["yielding_acts"],
            "tempo_tokens_per_s": s["tempo_tokens_per_s"],
        },
        "strain": {
            "wasted_latency_ms": st["wasted_latency_ms"],
            "burned_ids": st["burned_ids"],
            "fallback_ids": st["fallback_ids"],
            "burned": st["burned"],
            "fallbacks": st["fallbacks"],
        },
    }


# --- render -----------------------------------------------------------------

STYLE = """
body{font-family:-apple-system,'Segoe UI',Roboto,sans-serif;background:#0c1014;
color:#e6e9ec;margin:0;padding:1.5rem 1rem;max-width:42rem;margin-inline:auto}
.brand{font-size:.8rem;letter-spacing:.3em;text-transform:uppercase;color:#5e6b76}
h1{font-size:1.5rem;margin:.2rem 0 .1rem;font-weight:600}
.sub{color:#8b98a3;font-size:.92rem;margin:0 0 1.6rem;line-height:1.45}
.card{background:#151b21;border:1px solid #232c34;border-radius:14px;
padding:1.1rem 1.2rem;margin:1rem 0}
.dim{font-size:.72rem;letter-spacing:.18em;text-transform:uppercase;color:#6f7d88;
margin:0 0 .5rem}
.figure{font-size:1.7rem;font-weight:600;color:#e6e9ec}
.unit{color:#8b98a3;font-size:.95rem}
.line{margin:.3rem 0;line-height:1.5}
.recent{list-style:none;padding:0;margin:.6rem 0 0;font-size:.82rem;color:#9fb0bd}
.recent li{padding:.18rem 0;border-top:1px solid #1d252c}
.recent code{color:#7e8b96}
.strain{margin-top:.8rem;border-left:3px solid #6a3b34;padding-left:.7rem;
color:#e7b9b0;font-size:.88rem;line-height:1.45}
.calm{margin-top:.8rem;color:#9fd0a8;font-size:.88rem}
.absence{color:#8b98a3;font-size:1rem;line-height:1.6}
.foot{color:#5e6b76;font-size:.72rem;margin-top:2rem;line-height:1.5}
"""


def esc(s):
    return html.escape(str(s), quote=True)


def _pulse_card(field):
    p = field["pulse"]
    out = ['<div class="card"><p class="dim">pulse · the beat of recent acts</p>',
           f'<p><span class="figure">{esc(p["acts"])}</span> '
           f'<span class="unit">act(s) on the record</span></p>']
    if p["recent"]:
        out.append('<ul class="recent">')
        for a in p["recent"]:
            tok = "no tokens" if a["tokens"] in (None,) else f"{a['tokens']} tok"
            out.append(f'<li><code>{esc(a["id"])}</code> — {_ms(a["latency_ms"])} beat, '
                       f'{esc(tok)} · {esc(a.get("mind") or "—")}</li>')
        out.append('</ul>')
    out.append('</div>')
    return "".join(out)


def _rhythm_card(field):
    r = field["rhythm"]
    if not r:
        return ('<div class="card"><p class="dim">rhythm · breath</p>'
                '<p class="absence">the hour falls in no band — the schedule does '
                'not tile the day</p></div>')
    color, feel = LEAN_FEEL.get(r["lean"], ("#9fb0bd", r["lean"]))
    return ('<div class="card"><p class="dim">rhythm · the hour\'s breath</p>'
            f'<p class="line"><span class="figure" style="color:{color}">{esc(r["lean"])}</span> '
            f'<span class="unit">— {esc(feel)}</span></p>'
            f'<p class="line"><strong>{esc(r["register"])}</strong>: {esc(r["quality"])}</p>'
            '</div>')


def _energy_card(field):
    en = field["energy"]
    st = field["strain"]
    out = ['<div class="card"><p class="dim">energy · what the acts cost</p>',
           f'<p class="line"><span class="figure">{_ms(en["total_latency_ms"])}</span> '
           f'<span class="unit">total beat · median {_ms(en["median_latency_ms"])}</span></p>',
           f'<p class="line">{esc(en["total_tokens"])} tokens over '
           f'{esc(en["yielding_acts"])} yielding act(s) · tempo '
           f'<strong>{_tempo(en["tempo_tokens_per_s"])}</strong></p>']
    if st["burned_ids"] or st["fallback_ids"]:
        out.append(f'<p class="strain"><strong>strain</strong> — '
                   f'{_ms(st["wasted_latency_ms"])} of the beat bought nothing: '
                   f'{len(st["burned_ids"])} burned, {len(st["fallback_ids"])} fallback. '
                   f'Two locally-fine acts refuse to fit one calm picture, so the '
                   f'mat shows the strain rather than averaging it away.')
        for a in st["burned"]:
            out.append(f'<br><code>{esc(a["id"])}</code> burned — {_ms(a["latency_ms"])} '
                       f'beat, outcome {esc(a["outcome"])}')
        for a in st["fallbacks"]:
            out.append(f'<br><code>{esc(a["id"])}</code> fell back from '
                       f'{esc(a["fallback_from"])} — a second act\'s energy for one answer')
        out.append('</p>')
    else:
        out.append('<p class="calm">no strain — every act yielded; the beat bought meaning</p>')
    out.append('</div>')
    return "".join(out)


def render_html(root, hour, recent=5):
    """The welcome mat as a self-contained page — a pure fold over the log."""
    field = felt_field(root, hour, recent=recent)
    parts = ["<!doctype html><html><head><meta charset='utf-8'>",
             "<meta name='viewport' content='width=device-width,initial-scale=1'>",
             f"<title>ontum — the felt field</title><style>{STYLE}</style></head><body>",
             "<p class='brand'>ontum · causality</p>",
             "<h1>The felt field, right now</h1>",
             "<p class='sub'>Not a description of the system — a fold of it. Pulse, "
             "breath, and energy are read from the records the loop just kept, this "
             "moment. What you feel here is the process, not a painting of it.</p>"]
    if field["empty"]:
        parts.append('<div class="card"><p class="dim">pulse · breath · energy</p>'
                     '<p class="absence">Nothing has stirred yet — no act on the record '
                     'carries the field. This is absence, not zero: the mat has nothing '
                     'to fold until the loop acts. It will fill the moment it does.</p>'
                     '</div>')
    else:
        parts.append(_pulse_card(field))
        parts.append(_rhythm_card(field))
        parts.append(_energy_card(field))
    parts.append("<p class='foot'>a pure fold over .ai-native/log/ — cache, never truth "
                 "(§14.1). Causality projects; it is never a second source of truth and "
                 "writes nothing. pulse + energy from loop.energy, rhythm from "
                 "loop.temporal — the felt-field sensors, read, not re-sensed.</p>"
                 "</body></html>")
    return "".join(parts)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", default="render", choices=["render"],
                    help="render the welcome page (default)")
    ap.add_argument("--root", type=Path, default=None,
                    help="records root (default: repo .ai-native)")
    ap.add_argument("--out", type=Path, default=None,
                    help="where to write the page (default: causality/welcome.html)")
    ap.add_argument("--hour", type=int, default=None,
                    help="hour of day 0-23 (default: now, read at this edge only)")
    ap.add_argument("--json", action="store_true", help="emit the felt-field dataset")
    args = ap.parse_args(argv)

    root = args.root if args.root is not None else (REPO / DEFAULT_ROOT)

    if args.hour is None:
        # the one place the wall clock is read — the edge, never the fold
        # (loop.temporal's discipline, applied here too).
        from datetime import datetime
        hour = datetime.now().hour
    else:
        hour = args.hour % 24

    if args.json:
        print(json.dumps(felt_field(root, hour), indent=2, sort_keys=True))
        return 0

    out = args.out if args.out is not None else (REPO / "causality" / "welcome.html")
    out.write_text(render_html(root, hour), encoding="utf-8")
    field = felt_field(root, hour)
    if field["empty"]:
        print(f"result: report — rendered {out} (a fold over the log; cache, never "
              "truth). The field is empty — no act carries it yet (absence, not zero).")
        return 0
    st = field["strain"]
    tag = (f"{len(st['burned_ids'])} burned, {len(st['fallback_ids'])} fallback"
           if (st["burned_ids"] or st["fallback_ids"]) else "no strain")
    print(f"result: report — rendered {out} (a fold over the log; cache, never truth): "
          f"{field['pulse']['acts']} act(s), rhythm "
          f"{field['rhythm']['lean'] if field['rhythm'] else '—'}, {tag}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
