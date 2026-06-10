#!/usr/bin/env python3
"""The owner's inbox, rendered for the owner (done-line 0005): a
self-contained, phone-readable page — each item's story told value-first,
mechanism after — plus a small local server whose verdict forms clear
items through the existing pen only.

The page is a pure fold over atoms/ + log/ (§14.1: a cache, never truth —
delete it and a render rebuilds it; I-5: a rendered file is versioned by
its inputs). The server binds to localhost by default; serving beyond
that needs auth, which is named here and deliberately not built (its own
version). There is no second write path: a verdict POST calls the same
judge() the CLI uses (D-4 stays one pen).

Stdlib only. Ends with a clear result on stdout (D-6): report | needs-you.
"""

import argparse
import html
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from loop.node import judge
from loop.orchestrate import HUMAN_NODE, STAMP_STAGE, next_action, read_setpoint
from loop.reconcile import DEFAULT_ROOT, Fold, load_atoms, real_nodes

STYLE = """
body{font-family:-apple-system,'Segoe UI',Roboto,sans-serif;background:#101418;
color:#e6e9ec;margin:0;padding:1rem;max-width:46rem;margin-inline:auto}
h1{font-size:1.25rem}h2{font-size:1rem;color:#9fb0bd;margin-top:2rem}
.card{background:#1a2026;border:1px solid #2a323a;border-radius:12px;
padding:1rem;margin:1rem 0}
.head{font-size:1.05rem;font-weight:600;margin:0 0 .25rem}
.id{color:#7e8b96;font-size:.8rem}
.chip{display:inline-block;background:#243038;color:#9fd0a8;border-radius:8px;
padding:.05rem .5rem;font-size:.75rem;margin-left:.5rem}
.value{margin:.6rem 0;line-height:1.45}
.why{color:#b9c4cd;font-size:.9rem;line-height:1.4}
table{width:100%;border-collapse:collapse;font-size:.85rem;margin:.6rem 0}
td{border-top:1px solid #2a323a;padding:.35rem .4rem;vertical-align:top}
td:first-child{color:#9fb0bd;white-space:nowrap}
details{margin:.5rem 0;font-size:.85rem;color:#b9c4cd}
summary{cursor:pointer;color:#9fb0bd}
.receipt{border-left:3px solid #2a323a;padding-left:.6rem;margin:.5rem 0}
form{margin-top:.8rem;display:flex;flex-wrap:wrap;gap:.5rem}
input[type=text]{flex:1 1 100%;background:#10161b;color:#e6e9ec;
border:1px solid #2a323a;border-radius:8px;padding:.5rem}
button{border:0;border-radius:8px;padding:.5rem .9rem;cursor:pointer;
background:#2a4632;color:#cdebd4}
button.reject{background:#46302a;color:#ebd4cd}
button.amend{background:#3a3a2a;color:#e7e3c0}
code{background:#10161b;border-radius:6px;padding:.1rem .35rem;font-size:.8rem}
.foot{color:#7e8b96;font-size:.75rem;margin-top:2rem}
"""


def esc(s):
    return html.escape(str(s), quote=True)


def gather(root):
    fold = Fold(root)
    atoms = load_atoms(root)
    real_map = real_nodes(fold)
    human = real_map.get(HUMAN_NODE)
    mine, summons, parked = [], [], []
    for atom, ahash in atoms:
        action = next_action(fold, atom, ahash, real_map)
        if action is None:
            continue
        kind, target = action
        if kind == "await" and target == human:
            mine.append((atom, ahash))
        elif kind == "await":
            summons.append((atom, target))
        elif kind == "parked":
            parked.append((atom, ahash))
    return fold, atoms, human, mine, summons, parked


def card(fold, atom, ahash, human, actionable):
    b = atom.get("briefing", {})
    story = atom["story"]
    out = ['<div class="card">']
    out.append(f'<p class="head">{esc(b.get("headline", story["text"]))}'
               f'<span class="chip">confidence: {esc(story["value_confidence"])}</span></p>')
    out.append(f'<p class="id">{esc(atom["id"])}</p>')
    if b:
        out.append(f'<p class="value">{esc(b["value"])}</p>')
        if b.get("why_now"):
            out.append(f'<p class="why"><strong>why now:</strong> {esc(b["why_now"])}</p>')
        out.append("<table>")
        for label, key in (("if you accept", "if_accepted"),
                           ("if you reject", "if_rejected"),
                           ("cost of a wrong call", "cost_of_wrong_call")):
            if b.get(key):
                out.append(f"<tr><td>{label}</td><td>{esc(b[key])}</td></tr>")
        out.append("</table>")
    else:
        out.append(f'<p class="value">{esc(story["text"])}</p>')
    out.append('<details><summary>what the gates said</summary>')
    for rc in fold.receipts:
        if rc.get("artifact_hash") == ahash:
            out.append(f'<div class="receipt"><strong>{esc(rc["node"])}: '
                       f'{esc(rc["verdict"])}</strong><br>{esc(rc["reason"])}</div>')
    out.append("</details>")
    if b.get("mechanism"):
        out.append(f'<details><summary>mechanism (only if you want it)</summary>'
                   f'<p>{esc(b["mechanism"])}</p></details>')
    if b.get("reading"):
        out.append('<details><summary>reading paths</summary><p>'
                   + "<br>".join(f"<code>{esc(p)}</code>" for p in b["reading"]) + "</p></details>")
    if actionable:
        out.append(f'<form method="post" action="/judge">'
                   f'<input type="hidden" name="atom" value="{esc(atom["id"])}">'
                   f'<input type="text" name="reason" placeholder="your reason (required)" required>')
        for v in STAMP_STAGE["terminal_expected"]:
            cls = "" if v == "accept" else (' class="amend"' if v == "amend" else ' class="reject"')
            out.append(f'<button{cls} name="verdict" value="{esc(v)}">{esc(v)}</button>')
        out.append("</form>")
    else:
        out.append(f'<p class="why">clear: <code>python -m loop.node judge --atom {esc(atom["id"])} '
                   f'--node {esc(human)} --verdict &lt;verdict&gt; --reason "&lt;why&gt;"</code></p>')
    out.append("</div>")
    return "".join(out)


def render_html(root, actionable=False):
    fold, atoms, human, mine, summons, parked = gather(root)
    setpoint = read_setpoint(fold.admissions)
    cap = setpoint["value"]["human_queue_cap"] if setpoint else "?"
    parts = ["<!doctype html><html><head><meta charset='utf-8'>",
             "<meta name='viewport' content='width=device-width,initial-scale=1'>",
             f"<title>ontum — your stamp</title><style>{STYLE}</style></head><body>",
             f"<h1>Waiting on you: {len(mine)} <span class='chip'>queue cap {esc(cap)}</span></h1>"]
    if human is None:
        parts.append("<p class='why'>the owner stamp is still mocked — nothing waits on you "
                     "until it is admitted real</p>")
    for atom, ahash in mine:
        parts.append(card(fold, atom, ahash, human, actionable))
    if summons:
        parts.append("<h2>Awaiting summons (routed for you, not by you)</h2>")
        for atom, target in summons:
            parts.append(f"<div class='card'><p class='id'>{esc(atom['id'])} → {esc(target)}</p></div>")
    if parked:
        parts.append("<h2>Parked (yours to amend or retire)</h2>")
        for atom, ahash in parked:
            parts.append(f"<div class='card'><p class='id'>{esc(atom['id'])}</p>")
            for rc in fold.receipts:
                if rc.get("artifact_hash") == ahash and rc.get("next_suggested_event") is None:
                    parts.append(f"<div class='receipt'><strong>{esc(rc['node'])}: "
                                 f"{esc(rc['verdict'])}</strong><br>{esc(rc['reason'])}</div>")
            parts.append("</div>")
    parts.append("<p class='foot'>a pure fold over atoms/ + log/ — cache, never truth (§14.1). "
                 "verdicts write through the one pen (node judge). localhost-only until auth "
                 "is built — do not expose this bind to the open internet.</p></body></html>")
    return "".join(parts)


def make_handler(root):
    class InboxHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            body = render_html(root, actionable=True).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            if self.path != "/judge":
                self.send_error(404)
                return
            length = int(self.headers.get("Content-Length", 0))
            form = parse_qs(self.rfile.read(length).decode("utf-8"))
            atom = form.get("atom", [""])[0]
            verdict = form.get("verdict", [""])[0]
            reason = form.get("reason", [""])[0].strip()
            human = real_nodes(Fold(root)).get(HUMAN_NODE)
            if not (atom and verdict and reason and human):
                self.send_error(400, "atom, verdict, and a reason are required (D-4: stamps carry reasons)")
                return
            if judge(root, atom, human, verdict, reason) != 0:
                self.send_error(400, "the pen refused it — see the server log for the seam's reason")
                return
            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()

        def log_message(self, fmt, *args):
            pass  # the log/ directory is the log; HTTP chatter is not truth

    return InboxHandler


def serve(root, host, port):
    server = ThreadingHTTPServer((host, port), make_handler(root))
    print(f"result: report — serving your inbox at http://{host}:{server.server_address[1]}/ "
          "(one pen, localhost-trust; Ctrl-C to dissolve)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render", help="write the self-contained inbox page (static, phone-readable)")
    r.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    r.add_argument("--out", type=Path, default=None)
    s = sub.add_parser("serve", help="serve the inbox locally with verdict forms (one pen)")
    s.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    s.add_argument("--host", default="127.0.0.1",
                   help="default localhost; binding wider is LAN-trust — auth is not built yet")
    s.add_argument("--port", type=int, default=8787)
    args = ap.parse_args(argv)
    if args.cmd == "render":
        out = args.out or (args.root / "inbox.html")
        out.write_text(render_html(args.root, actionable=False), encoding="utf-8")
        print(f"result: report — rendered {out} (a fold over atoms/ + log/; cache, never truth)")
        return 0
    return serve(args.root, args.host, args.port)


if __name__ == "__main__":
    sys.exit(main())
