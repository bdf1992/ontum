#!/usr/bin/env python3
"""Causality's welcome mat (done-line 0095): the landing page — the system's
first impression, folding the live felt-field from records the loop already
keeps, and rendered in Causality's own visual language.

bdo's frame (2026-06-16): agenda [[anima]]'s felt-field is *emergent* — the
sauce is the process, named after first taste. A session does not author the
felt-field; it builds the surface the field emerges *through*. The welcome mat
is the first impression, and to be *capable of carrying* the felt-field it must
**fold** that field from real records — never paint it. A hand-authored "feels
alive" surface is mercury: it carries nothing.

So this is a **projection** (Causality's one hard rule: never a second source of
truth, no second write path). It reads the felt-field sensors that already live
on main and renders them as the **anima signature** specified in
`causality/display-system.md` (C18): a two-dimensional mood —

  STRENGTH (weak <-> strong)  force / yield / strain   (loop.energy)
  TEMPO    (fast <-> slow)     the hour's heat / cool   (loop.temporal)

whose 2x2 the display *shows as a mood* (vigorous / grounded / jittery /
guttering), with the grounding figures beneath it: the pulse (recent acts), the
breath (the hour's band), and the energy/strain. It re-senses nothing —
Causality reads the sensors, loop owns them — and every figure is the number its
fold emits (the citation discipline); a fabricated constant would diverge from
the fold and the §10 test catches it. An empty log renders "absence", never a
fake zero. `loop.impact` is deliberately absent (not on main, open PR #149).

The look matches `causality/canvas.html`: warm paper, Fraunces / Caveat /
IBM Plex Mono, semantic teal/rust/purple, ink borders and soft shadow — no dark
mode. Stdlib only; a pure fold over the log (§14.1: a cache, never truth). There
is no server, no POST, no verdict path: a welcome mat is read.

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

# Causality's pigment array (causality/canvas.html / lib/causality.js) — the
# recent-act circles cycle through it, so the mat speaks the canvas's palette.
PIGMENT = ["#0e8a7b", "#b8742c", "#7a5ba6", "#bf4a3e", "#3f7cb6", "#6b8f3c"]

# the hour's lean -> the tempo pole (display-system.md C18: FAST <-> SLOW).
LEAN_TEMPO = {"heat": "fast", "steady": "steady", "cool": "slow"}

# the anima 2x2 (display-system.md): tempo x strength -> a named mood + its read.
MOODS = {
    ("fast", "strong"):   ("vigorous", "#0e8a7b", "hot frontier — quick and load-bearing"),
    ("slow", "strong"):   ("grounded", "#0e8a7b", "deep and unhurried — the beat lands"),
    ("steady", "strong"): ("steady", "#0e8a7b", "holding the line — the work is paying"),
    ("fast", "weak"):     ("jittery", "#d4543f", "quick but burning — churn without yield"),
    ("slow", "weak"):     ("guttering", "#d4543f", "slow and strained — more beat spent than meaning made"),
    ("steady", "weak"):   ("laboring", "#b8742c", "holding, but the beat is costing"),
}


# --- the fold (pure; the felt-field, read from the sensors) -----------------

def _ms(v):
    return "—" if v is None else f"{v / 1000:.1f}s"


def _tempo_rate(v):
    return "—" if v is None else f"{v:.1f} tok/s"


def felt_field(root, hour, recent=5):
    """The live felt-field, folded — never painted. Reads `loop.energy` (pulse +
    energy/tempo + strain) and `loop.temporal` (the hour's band). Pure over the
    log; writes nothing. A missing log folds to `empty` (absence, not a fake
    zero)."""
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
            "recent": list(reversed(e["acts"]))[:recent],  # freshest first
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


def mood(field):
    """The anima signature (display-system.md C18): a 2-D mood read *from the
    folds*, never decorative. TEMPO is the hour's lean (loop.temporal); STRENGTH
    is whether the energy is paying (loop.energy) — a field carrying strain, or
    wasting most of its beat, or yielding nothing, reads weak. Returns the pole
    pair, the named mood, and the figures it stands on (so it is traceable).
    None on an empty field (no field to be in a mood about)."""
    if field["empty"]:
        return None
    en = field["energy"]
    st = field["strain"]
    lean = field["rhythm"]["lean"] if field["rhythm"] else "steady"
    tempo = LEAN_TEMPO.get(lean, "steady")
    total = en["total_latency_ms"] or 0
    wasted = st["wasted_latency_ms"] or 0
    strained = bool(st["burned_ids"] or st["fallback_ids"])
    weak = (strained or en["yielding_acts"] == 0
            or (total > 0 and wasted / total > 0.3))
    strength = "weak" if weak else "strong"
    name, color, read = MOODS[(tempo, strength)]
    return {"tempo": tempo, "strength": strength, "name": name, "color": color,
            "read": read, "lean": lean,
            "from": {"tempo": f"the hour leans {lean}",
                     "strength": (f"{len(st['burned_ids'])} burned / "
                                  f"{len(st['fallback_ids'])} fallback, "
                                  f"{_ms(wasted)} of {_ms(total)} wasted"
                                  if strained or total else "no acts yielding")}}


# --- render (Causality's visual language) -----------------------------------

STYLE = """
:root{--paper:#f6f1e7;--ink:#2b2a33;--dim:#8d8678;--faint:#b8b1a2;
--plus:#0e8a7b;--minus:#d4543f;--think:#7a5ba6;--pulse:#e8a13c;}
*{margin:0;padding:0;box-sizing:border-box}
html,body{background:var(--paper);color:var(--ink)}
body{font-family:"Space Grotesk",system-ui,sans-serif;line-height:1.5;
padding:34px 22px 60px;max-width:660px;margin-inline:auto}
header{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;margin-bottom:6px}
header h1{font-family:"Fraunces",serif;font-size:30px;font-weight:300}
header h1 b{color:var(--think);font-weight:600}
.sub{font:300 9.5px "IBM Plex Mono",monospace;color:var(--dim);
letter-spacing:.2em;text-transform:uppercase}
.lede{font:300 13px "Space Grotesk";color:#6b6456;margin:2px 0 26px;max-width:48ch}
.mood{border:1.5px solid var(--ink);border-radius:16px;padding:20px 22px;
background:rgba(255,252,245,.6);box-shadow:3px 4px 0 rgba(43,42,51,.14);margin-bottom:22px}
.mood .tag{font:500 9px "IBM Plex Mono",monospace;letter-spacing:.24em;
text-transform:uppercase;color:var(--dim)}
.mood .name{font-family:"Fraunces",serif;font-style:italic;font-size:34px;
font-weight:300;margin:1px 0 4px}
.mood .read{font:400 14px "Space Grotesk";color:var(--ink)}
.mood .axes{margin-top:13px;display:flex;gap:9px;flex-wrap:wrap}
.chip{font:400 10px "IBM Plex Mono",monospace;color:var(--ink);
border:1.2px solid rgba(43,42,51,.4);border-radius:20px;padding:4px 11px}
.chip b{color:var(--think);font-weight:500}
.card{border:1.5px solid rgba(43,42,51,.4);border-radius:13px;padding:15px 17px;
background:rgba(255,252,245,.55);margin:12px 0}
.card h4{font:500 9px "IBM Plex Mono",monospace;letter-spacing:.22em;
text-transform:uppercase;color:var(--dim);margin-bottom:11px}
.fig{font-family:"Fraunces",serif;font-size:23px;font-weight:300}
.unit{font:400 11px "IBM Plex Mono",monospace;color:var(--dim)}
.circles{display:flex;gap:13px;align-items:flex-end;margin:6px 0 11px;flex-wrap:wrap}
.act{font:400 11px "IBM Plex Mono",monospace;color:#6b6456;line-height:1.7}
.act code{color:var(--ink)}
.act .lab{font-family:"Caveat",cursive;font-size:15px;color:var(--dim);margin-left:4px}
.row{display:flex;justify-content:space-between;font:400 11px "IBM Plex Mono",monospace;
padding:2px 0}
.row .ok{color:var(--plus)}.row .bad{color:var(--minus)}
.strain{margin-top:11px;padding-top:10px;border-top:1px dashed rgba(43,42,51,.25);
font:400 11.5px "Space Grotesk";color:#7a4038;line-height:1.5}
.strain code{font:400 10.5px "IBM Plex Mono",monospace;color:var(--minus)}
.calm{margin-top:9px;font:400 12px "Space Grotesk";color:var(--plus)}
.breath{font-family:"Caveat",cursive;font-size:22px}
.absence{font:300 14px "Space Grotesk";color:#6b6456;line-height:1.6}
.foot{font:300 9px "IBM Plex Mono",monospace;color:var(--faint);
letter-spacing:.06em;margin-top:30px;line-height:1.9}
"""

FONTS = ("https://fonts.googleapis.com/css2?family=Caveat:wght@500;600"
         "&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,600;1,9..144,300"
         "&family=Space+Grotesk:wght@400;500;700"
         "&family=IBM+Plex+Mono:wght@300;400;500&display=swap")


def esc(s):
    return html.escape(str(s), quote=True)


def _act_circle(i, act):
    """One recent act as a water-level circle — Causality's node motif: fill
    rises with the act's yield (tokens), the rim goes rust when the act burned
    (no yield / not ok). A glanceable read of each beat's health."""
    pig = PIGMENT[i % len(PIGMENT)]
    tok = act["tokens"]
    burned = act["outcome"] not in (None, "ok") or tok in (None, 0)
    # fill height 0..34 over a soft token ceiling (256) — representation, not a
    # claim; a burned act sits empty.
    frac = 0.0 if (tok in (None, 0)) else min(1.0, tok / 256.0)
    fill_h = round(34 * frac, 1)
    rim = "#d4543f" if burned else "#2b2a33"
    cid = f"clip{i}"
    return (
        f'<svg width="46" height="46" viewBox="0 0 46 46" aria-hidden="true">'
        f'<defs><clipPath id="{cid}"><circle cx="23" cy="23" r="18"/></clipPath></defs>'
        f'<rect x="5" y="{41 - fill_h}" width="36" height="{fill_h}" fill="{pig}" '
        f'opacity="0.8" clip-path="url(#{cid})"/>'
        f'<circle cx="23" cy="23" r="18" fill="none" stroke="{rim}" stroke-width="1.6"/>'
        f'</svg>')


def _pulse_card(field):
    p = field["pulse"]
    out = ['<div class="card"><h4>pulse · the beat of recent acts</h4>',
           f'<p><span class="fig">{esc(p["acts"])}</span> '
           f'<span class="unit">act(s) on the record</span></p>']
    if p["recent"]:
        out.append('<div class="circles">')
        for i, a in enumerate(p["recent"]):
            out.append(_act_circle(i, a))
        out.append('</div>')
        for a in p["recent"]:
            tok = "no tokens" if a["tokens"] in (None,) else f'{a["tokens"]} tok'
            out.append(f'<div class="act"><code>{esc(a["id"])}</code> — '
                       f'{_ms(a["latency_ms"])} · {esc(tok)}'
                       f'<span class="lab">{esc(a.get("mind") or "—")}</span></div>')
    out.append('</div>')
    return "".join(out)


def _breath_card(field):
    r = field["rhythm"]
    if not r:
        return ('<div class="card"><h4>breath · the hour\'s rhythm</h4>'
                '<p class="absence">the hour falls in no band — the schedule does '
                'not tile the day</p></div>')
    tint = {"heat": "var(--pulse)", "steady": "var(--ink)", "cool": "var(--think)"}
    return ('<div class="card"><h4>breath · the hour\'s rhythm</h4>'
            f'<p class="breath" style="color:{tint.get(r["lean"], "var(--ink)")}">'
            f'leaning {esc(r["lean"])}</p>'
            f'<p class="act"><code>{esc(r["register"])}</code> &nbsp;{esc(r["quality"])}</p>'
            '</div>')


def _energy_card(field):
    en = field["energy"]
    st = field["strain"]
    out = ['<div class="card"><h4>energy · what the acts cost</h4>',
           f'<div class="row"><span>total beat</span>'
           f'<span class="fig" style="font-size:15px">{_ms(en["total_latency_ms"])}</span></div>',
           f'<div class="row"><span>median beat</span><span>{_ms(en["median_latency_ms"])}</span></div>',
           f'<div class="row"><span>yield</span><span>{esc(en["total_tokens"])} tok '
           f'/ {esc(en["yielding_acts"])} act(s)</span></div>',
           f'<div class="row"><span>tempo</span>'
           f'<span class="{"ok" if en["tempo_tokens_per_s"] else ""}">'
           f'{_tempo_rate(en["tempo_tokens_per_s"])}</span></div>']
    if st["burned_ids"] or st["fallback_ids"]:
        out.append(f'<div class="strain"><strong>strain</strong> — '
                   f'{_ms(st["wasted_latency_ms"])} of the beat bought nothing '
                   f'({len(st["burned_ids"])} burned, {len(st["fallback_ids"])} fallback). '
                   f'Two locally-fine acts refuse to fit one calm picture, so the mat '
                   f'shows the strain rather than averaging it away.')
        for a in st["burned"]:
            out.append(f'<br><code>{esc(a["id"])}</code> burned — {_ms(a["latency_ms"])}, '
                       f'outcome {esc(a["outcome"])}')
        for a in st["fallbacks"]:
            out.append(f'<br><code>{esc(a["id"])}</code> fell back from '
                       f'{esc(a["fallback_from"])} — a second act for one answer')
        out.append('</div>')
    else:
        out.append('<p class="calm">no strain — every act yielded; the beat bought meaning</p>')
    out.append('</div>')
    return "".join(out)


def _mood_panel(field):
    m = mood(field)
    if not m:
        return ''
    return ('<div class="mood">'
            '<div class="tag">the loop\'s mood, right now</div>'
            f'<div class="name" style="color:{m["color"]}">{esc(m["name"])}</div>'
            f'<div class="read">{esc(m["read"])}</div>'
            '<div class="axes">'
            f'<span class="chip">tempo · <b>{esc(m["tempo"])}</b> &nbsp;({esc(m["from"]["tempo"])})</span>'
            f'<span class="chip">strength · <b>{esc(m["strength"])}</b> &nbsp;({esc(m["from"]["strength"])})</span>'
            '</div></div>')


def render_html(root, hour, recent=5):
    """The welcome mat as a self-contained page, in Causality's language — a pure
    fold over the log."""
    field = felt_field(root, hour, recent=recent)
    parts = ["<!doctype html><html lang='en'><head><meta charset='utf-8'>",
             "<meta name='viewport' content='width=device-width,initial-scale=1'>",
             "<title>Causality — the felt field</title>",
             "<link rel='preconnect' href='https://fonts.googleapis.com'>",
             f"<link href='{FONTS}' rel='stylesheet'>",
             f"<style>{STYLE}</style></head><body>",
             "<header><h1>Causa<b>lity</b></h1>"
             "<div class='sub'>the felt field · folded, not painted · this moment</div></header>",
             "<p class='lede'>Not a description of the system — a fold of it. What you "
             "feel here is read from the records the loop just kept, this moment.</p>"]
    if field["empty"]:
        parts.append('<div class="mood"><div class="tag">the loop\'s mood, right now</div>'
                     '<div class="name" style="color:var(--faint)">still</div>'
                     '<div class="read">Nothing has stirred yet — no act on the record '
                     'carries the field. This is absence, not zero: the mat has nothing '
                     'to fold until the loop acts, and it will fill the moment it does.</div>'
                     '</div>')
    else:
        parts.append(_mood_panel(field))
        parts.append(_pulse_card(field))
        parts.append(_breath_card(field))
        parts.append(_energy_card(field))
    parts.append("<p class='foot'>a pure fold over .ai-native/log/ — cache, never truth "
                 "(§14.1)&nbsp;·&nbsp;Causality projects; it is never a second source of "
                 "truth and writes nothing&nbsp;·&nbsp;pulse + energy from loop.energy, "
                 "breath from loop.temporal, mood from the anima signature "
                 "(display-system.md C18) — sensors read, not re-sensed.</p>"
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
        out = dict(felt_field(root, hour))
        out["mood"] = mood(out)
        print(json.dumps(out, indent=2, sort_keys=True))
        return 0

    out = args.out if args.out is not None else (REPO / "causality" / "welcome.html")
    out.write_text(render_html(root, hour), encoding="utf-8")
    field = felt_field(root, hour)
    if field["empty"]:
        print(f"result: report — rendered {out} (a fold over the log; cache, never "
              "truth). The field is empty — no act carries it yet (absence, not zero).")
        return 0
    m = mood(field)
    print(f"result: report — rendered {out} (a fold over the log; cache, never truth): "
          f"mood {m['name']} ({m['tempo']}·{m['strength']}), "
          f"{field['pulse']['acts']} act(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
