#!/usr/bin/env python3
"""The local-preview deployment face (done-line 0161): serve a named snapshot
on localhost so bdo eyeballs it before anything leaves the machine.

The LOCAL-tier DEPLOYMENT face of `epic.environments` (bdo's confirmed arc),
sibling of the local-tier WORKING face already landed (the snapshot spine,
`loop/snapshot.py`). A snapshot is promoted across environments; this is its
first rung — local. The act is recorded as a promotion to the local
environment (the local deploy ledger), so "what was served, of what snapshot,
by whom" is answerable from the log.

COMPOSES, does not double-build (§10): it reads `loop/snapshot.py`'s `resolve`
for the snapshot's acceptance verdict (it NEVER re-judges acceptance — that
stays the pipeline's, D-4) and reuses `loop/web.py`'s localhost-serve pattern
for the actual serving. It adds only the local-deploy GATE (the teeth) and the
local-deploy LEDGER (the record).

The §10 teeth: you do not preview a lie. Only an ACCEPTED snapshot may be
served to the local deployment env; a snapshot that resolves stale, ghost, or
unaccepted is refused at the gate and NOTHING is recorded. Two locally-fine
records — a snapshot and the local-deploy gate — refuse to fit when the
snapshot lies about its join, and the gate notices.

Local-first: a localhost server is local coordination, not the no-network
ban's egress (the `loop/web.py` precedent). No git — verifying the served
commit equals the working tree belongs to the git/CI layer, a later increment.

CLI:
  python -m loop.preview                       the local deploy ledger + serveable snapshots
  python -m loop.preview --json                the raw dataset (machine-readable)
  python -m loop.preview gate --name <n>       CI seam: exit 0 deployable / non-zero held
  python -m loop.preview serve --name <n> --by <who>   gate + record + serve on localhost
"""

import argparse
import functools
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from loop.reconcile import (DEFAULT_ROOT, Fold, append_line, canon, now_ts,
                            short_hash)
from loop import snapshot

LOCAL_DEPLOY_TYPE = "local_deployment"
ENVIRONMENT = "local"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000


def gate(name, root=DEFAULT_ROOT, fold=None):
    """Is the named snapshot serveable to the local env? Deployable iff it
    resolves `accepted` — a stale/ghost/unaccepted snapshot is held, with the
    resolve verdict cited. Composes snapshot.resolve; re-judges nothing."""
    fold = fold or Fold(root)
    res = snapshot.resolve(name, root, fold)
    if res is None:
        return {"deployable": False, "verdict": "unknown", "commit": None,
                "reason": f"no snapshot named `{name}` to preview"}
    deployable = res["verdict"] == "accepted"
    return {
        "deployable": deployable,
        "verdict": res["verdict"],
        "commit": res["commit"],
        "reason": (f"snapshot `{name}` is accepted — serveable to the local env"
                   if deployable else
                   f"snapshot `{name}` is {res['verdict']} — not serveable; you "
                   f"do not preview a lie ({res['reason']})"),
    }


def deploy_local(root, name, by, host=DEFAULT_HOST, port=DEFAULT_PORT, fold=None):
    """The one writer: on an accepted snapshot, append a `local_deployment`
    admission recording the promotion to the local env, and return it. On a
    non-accepted snapshot (or a missing signer) it refuses and writes NOTHING.
    Returns (admission, gate) or (None, gate)."""
    fold = fold or Fold(root)
    g = gate(name, root, fold)
    if not g["deployable"]:
        print(f"result: needs-you — refused: {g['reason']}")
        return None, g
    if not (by or "").strip():
        print("result: needs-you — a local deployment records who served it — "
              "pass --by")
        return None, g
    url = f"http://{host}:{port}/"
    # the ledger is append-only history (a snapshot is previewed many times); a
    # per-snapshot sequence keeps repeated same-second deploys distinct so the
    # dedup fold never drops one (the collision the spine's id fix also closed).
    seq = sum(1 for a in local_deployments(fold) if a.get("snapshot") == name)
    adm = {
        "id": "adm." + short_hash(LOCAL_DEPLOY_TYPE, name, g["commit"] or "",
                                  url, str(seq), str(by), now_ts()),
        "type": LOCAL_DEPLOY_TYPE,
        "environment": ENVIRONMENT,
        "snapshot": name,
        "commit": g["commit"],
        "url": url,
        "by": by,
        "ts": now_ts(),
    }
    append_line(root / "log" / "admissions.jsonl", adm)
    return adm, g


def local_deployments(fold):
    """The local deploy ledger — every local_deployment recorded, in order
    (append-only history; a snapshot can be previewed many times)."""
    return [adm for adm in fold.admissions
            if adm.get("type") == LOCAL_DEPLOY_TYPE]


def serve_tree(directory, host=DEFAULT_HOST, port=DEFAULT_PORT):
    """Serve `directory` statically on localhost — the deployable surface
    (the same static content pages.yml deploys), so bdo opens the browser and
    eyeballs it. The web.py serve pattern (ThreadingHTTPServer), local-first.
    Blocks until interrupted."""
    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(directory))
    server = ThreadingHTTPServer((host, port), handler)
    print(f"serving {directory} at http://{host}:{port}/ — Ctrl-C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


def render(root):
    fold = Fold(root)
    snaps = snapshot.dataset(root, fold)["snapshots"]
    ledger = local_deployments(fold)
    lines = ["# Local preview — the local deployment env", ""]
    serveable = [s for s in snaps if s["verdict"] == "accepted"]
    if serveable:
        lines.append(f"## Serveable now ({len(serveable)}) — accepted snapshots")
        lines += [f"- `{s['name']}` (commit `{(s['commit'] or '?')[:12]}`)"
                  for s in serveable]
        lines.append("")
    held = [s for s in snaps if s["verdict"] != "accepted"]
    if held:
        lines.append(f"## Not serveable ({len(held)}) — a snapshot you cannot preview")
        lines += [f"- `{s['name']}` — {s['verdict']}" for s in held]
        lines.append("")
    lines.append(f"## Local deploy ledger ({len(ledger)})")
    if ledger:
        lines += [f"- `{a['snapshot']}` → {a['url']} (commit "
                  f"`{(a.get('commit') or '?')[:12]}`, by {a['by']} at {a['ts']})"
                  for a in ledger]
    else:
        lines.append("- _no local deployment yet._")
    lines += ["",
              "Serve one with: python -m loop.preview serve --name <n> --by <who>",
              "_read-only fold; the only writer is the deploy_local pen. "
              "Acceptance is read from snapshot.resolve (D-4)._"]
    return "\n".join(lines)


def dataset(root=DEFAULT_ROOT):
    fold = Fold(root)
    snaps = snapshot.dataset(root, fold)["snapshots"]
    return {
        "serveable": [s["name"] for s in snaps if s["verdict"] == "accepted"],
        "not_serveable": [{"name": s["name"], "verdict": s["verdict"]}
                          for s in snaps if s["verdict"] != "accepted"],
        "ledger": local_deployments(fold),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--json", action="store_true",
                    help="emit the raw dataset (machine-readable), not the prose")
    sub = ap.add_subparsers(dest="cmd")

    g = sub.add_parser("gate", help="CI seam: exit 0 deployable / non-zero held")
    g.add_argument("--name", required=True)

    s = sub.add_parser("serve", help="gate + record + serve the snapshot on localhost")
    s.add_argument("--name", required=True)
    s.add_argument("--by", required=True, help="who served it")
    s.add_argument("--host", default=DEFAULT_HOST)
    s.add_argument("--port", type=int, default=DEFAULT_PORT)
    s.add_argument("--no-serve", action="store_true",
                   help="record the local deployment but do not block serving")
    s.add_argument("--dir", default=".",
                   help="the directory to serve (default: repo root, the "
                        "deployable static surface)")

    args = ap.parse_args(argv)

    if args.cmd == "gate":
        r = gate(args.name, args.root)
        print(f"gate: {'deployable' if r['deployable'] else 'held'} — {r['reason']}")
        if not r["deployable"]:
            print("result: needs-you — snapshot not serveable to the local env")
            return 1
        print("result: done — deployable to the local env")
        return 0

    if args.cmd == "serve":
        adm, _ = deploy_local(args.root, args.name, args.by,
                              host=args.host, port=args.port)
        if adm is None:
            return 1
        print(f"local deployment recorded: `{adm['snapshot']}` → {adm['url']} "
              f"({adm['id']})")
        if not args.no_serve:
            serve_tree(args.dir, args.host, args.port)  # blocks until Ctrl-C
        # the result line is last, after the (blocking) serve ends — D-6
        print(f"result: done — local deployment `{adm['snapshot']}` served at "
              f"{adm['url']}")
        return 0

    # no subcommand: read-only status
    if args.json:
        print(canon(dataset(args.root)))
    else:
        print(render(args.root))
        print()
    fold = Fold(args.root)
    n = len(local_deployments(fold))
    print(f"result: done — {n} local deployment(s) on the ledger")
    return 0


if __name__ == "__main__":
    sys.exit(main())
