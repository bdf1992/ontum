#!/usr/bin/env python3
"""loop/agent_run.py — agent runs ON THE BOOKS, under a training posture.

bdo 2026-06-22: *"run it on the books as a training program so to speak but
ensure it gets monitored by some process."* A workflow agent run currently
leaves NO receipt — it vanishes (R5/C6 of the agent-summoning requirements):
its work is unwitnessed, uncounted, and nothing marks it training-not-production.
This is the fix, and it is deliberately the smallest real one:

- **on the books** — a *training run* is a posture opened on the log (one
  admission), and every agent run under it is receipted and stamped with the
  run id. The run no longer vanishes; it is a fact the loop can fold.
- **training, not production** — the posture says so. A receipt under it carries
  `training: true`; nothing here advances a pipeline, clears a park, or settles a
  verdict. It is a learning run whose evidence later *earns* the realness stamp —
  the right order (run to learn, recorded, then graduate), never self-asserted
  done.
- **monitored** — `fold_run` is the read-back: what ran, under which governed
  prompt, with what disposition, and what is actionable. A process can poll it
  (`python -m loop.agent_run --run <id>`); the read is the monitor's eyes.

It mirrors `loop/train.py` exactly, one axis over: `train.py` opens a
`security_mode` posture and folds *fence* readings; this opens an
`agent_training_run` posture and folds *agent-run* receipts. Same discipline —
it REPORTS, it never installs; the read-back refuses to invent from no evidence.

The teeth (§10): a run receipt must cite a node whose governed prompt RESOLVES
and PASSES the requirements door (`prompt_req.deliver`), and carry that node's
current prompt hash — a receipt for a ghost node, or one claiming a prompt hash
the node does not have, is REFUSED at the write seam (the term-economy
ghost-citation refusal, on agent runs). An on-the-books receipt is attributable
to a real governed prompt by construction; you cannot book an ungoverned run.
A training run with no receipts folds to an empty monitor read, never a false
"all clear".

Read-only but for the two sanctioned appends (open a run, receipt a run), both
through `reconcile.append_line`. Stdlib only; no network, no subprocess — the
loop/ law. Ends with a clear stdout result (D-6): done | report | needs-you.
"""

import argparse
import sys
from pathlib import Path

from loop import prompt_req
from loop.reconcile import (
    DEFAULT_ROOT, Fold, append_line, canon, now_ts, read_jsonl, short_hash,
)

OPENER_TYPE = "agent_training_run"   # the posture admission (on admissions.jsonl)
RECEIPT_TYPE = "agent_run"           # one agent run on the books (on receipts.jsonl)


def _admissions_path(root):
    return Path(root) / "log" / "admissions.jsonl"


def _receipts_path(root):
    return Path(root) / "log" / "receipts.jsonl"


# ---------------------------------------------------------------- open / close

def open_run(root, by, note=None):
    """Open a training run — the posture, on the books. Returns the run id, which
    every receipt under it carries. A training posture only ever ADDS scrutiny
    (it records more and trusts less), so opening one is the safe direction; the
    opener is attributed (`by`) and stands as history. Mirrors train.py's
    security_mode opener."""
    if not by:
        raise ValueError("a training run must be opened by a named actor (--by)")
    run_id = "atr." + short_hash(by, note or "run", now_ts())
    append_line(_admissions_path(root), {
        "id": run_id,
        "type": OPENER_TYPE,
        "enabled": True,
        "by": by,
        "note": note,
        "ts": now_ts(),
    })
    return run_id


def close_run(root, run_id, by):
    """Close the posture — a superseding admission (the opener stands as
    history; history is never retro-invalidated). Receipts already booked under
    it remain on the books."""
    if not by:
        raise ValueError("closing a training run is attributed (--by)")
    append_line(_admissions_path(root), {
        "id": "atr.close." + short_hash(run_id, by, now_ts()),
        "type": OPENER_TYPE,
        "enabled": False,
        "run": run_id,
        "by": by,
        "ts": now_ts(),
    })


def training_runs(fold):
    """Every opened training run, read from the log (never a constant). A later
    `enabled:false` admission naming the run closes it (it supersedes; the
    opener stands as history)."""
    out = []
    for adm in fold.admissions:
        if adm.get("type") != OPENER_TYPE:
            continue
        if adm.get("enabled", True):
            out.append({
                "id": adm.get("id"),
                "by": adm.get("by"),
                "note": adm.get("note"),
                "ts": adm.get("ts"),
                "closed": False,
            })
        else:
            for o in out:
                if o["id"] == adm.get("run"):
                    o["closed"] = True
    return out


# ---------------------------------------------------------------- the write seam

def book_receipt(root, run_id, node, prompt_hash, subject, verdict, reason):
    """Book one agent run ON THE BOOKS. The §10 teeth at the write seam:

    - the node's governed prompt must RESOLVE and PASS the requirements door
      (`prompt_req.deliver`), else the run is ungoverned — REFUSED;
    - the `prompt_hash` must match the node's current governed hash — a receipt
      claiming a different prompt is a ghost-in-spirit — REFUSED.

    On success appends one `agent_run` receipt (idempotent by (run, node,
    subject)) and returns its id. Raises ValueError naming the refusal otherwise
    — the refusal IS the fail notification, never a silent pass."""
    d = prompt_req.deliver(root, node)
    if not d["found"]:
        raise ValueError(
            f"cannot book a run for ghost node '{node}' — no governed prompt at "
            f".ai-native/nodes/{node}.md (no governed prompt, no on-the-books run)")
    if not d["valid"]:
        raise ValueError(
            f"cannot book a run for '{node}' — its prompt fails the requirements "
            f"door: {'; '.join(d['problems'])}")
    if prompt_hash != d["prompt_hash"]:
        raise ValueError(
            f"prompt_hash mismatch for '{node}': receipt claims {prompt_hash!r} "
            f"but the governed prompt is {d['prompt_hash']!r} — a run is "
            f"attributable to the EXACT prompt that ran, or it is not booked")
    rid = "arun." + short_hash(run_id, node, subject)
    append_line(_receipts_path(root), {
        "id": rid,
        "type": RECEIPT_TYPE,
        "run": run_id,
        "node": node,
        "prompt_hash": prompt_hash,
        "subject": subject,
        "verdict": verdict,
        "reason": reason,
        "training": True,   # never auto-trusted as done — this is a learning run
        "ts": now_ts(),
    })
    return rid


# ---------------------------------------------------------------- the monitor read

def _run_receipts(root, run_id):
    """The agent_run receipts booked under one run, deduped by id (last wins —
    a re-book of the same (run, node, subject) supersedes, like every fold
    here)."""
    raw, _dropped = read_jsonl(_receipts_path(root))
    by_id = {}
    for r in raw:
        if r.get("type") == RECEIPT_TYPE and r.get("run") == run_id:
            by_id[r.get("id")] = r
    return list(by_id.values())


def fold_run(root, run_id):
    """The monitor read for one training run: what ran, by node and by verdict,
    the actionable set, and the governed prompt hashes used. Pure — reads the
    log, writes nothing. The eyes a watching process polls."""
    fold = Fold(root)
    opener = next((s for s in training_runs(fold) if s["id"] == run_id), None)
    receipts = _run_receipts(root, run_id)
    by_node, by_verdict, hashes = {}, {}, {}
    for r in receipts:
        n = r.get("node")
        v = r.get("verdict")
        by_node[n] = by_node.get(n, 0) + 1
        by_verdict[v] = by_verdict.get(v, 0) + 1
        h = r.get("prompt_hash")
        if h:
            hashes.setdefault(n, set()).add(h)
    return {
        "run": run_id,
        "opener": opener,
        "count": len(receipts),
        "by_node": dict(sorted(by_node.items())),
        "by_verdict": dict(sorted(by_verdict.items(), key=lambda kv: (-kv[1], str(kv[0])))),
        "prompt_hashes": {n: sorted(hs) for n, hs in sorted(hashes.items())},
        "receipts": sorted(receipts, key=lambda r: (str(r.get("node")), str(r.get("subject")))),
    }


def overview(root):
    """Every training run and its booked-receipt count — the read a monitor
    opens with."""
    fold = Fold(root)
    runs = training_runs(fold)
    raw, _dropped = read_jsonl(_receipts_path(root))
    counts = {}
    for r in raw:
        if r.get("type") == RECEIPT_TYPE:
            counts[r.get("run")] = counts.get(r.get("run"), 0) + 1
    for run in runs:
        run["count"] = counts.get(run["id"], 0)
    return {"runs": runs}


# ---------------------------------------------------------------- render

def render_overview(d):
    lines = ["# Agent training runs (on the books)", ""]
    if not d["runs"]:
        lines += ["_No training runs on record — no `agent_training_run` "
                  "admission has opened one. Absence is information._", ""]
        return "\n".join(lines)
    for r in d["runs"]:
        state = "closed" if r["closed"] else "open"
        lines.append(f"- `{r['id']}` — by {r['by']} ({state}); {r['count']} "
                     f"agent run(s) booked" + (f" — {r['note']}" if r.get("note") else ""))
    lines += ["", "_`python -m loop.agent_run --run <id>` reads one run's "
              "monitor fold._"]
    return "\n".join(lines)


def render_run(d):
    lines = [f"# Training run `{d['run']}` — the monitor read", ""]
    op = d["opener"]
    if op is None:
        lines += ["_No `agent_training_run` admission with this id — not a known "
                  "run._", ""]
    else:
        state = "closed" if op["closed"] else "open"
        lines += [f"_opened by {op['by']} ({state})"
                  + (f" — {op['note']}" if op.get("note") else "") + "_", ""]
    lines.append(f"## {d['count']} agent run(s) on the books")
    if not d["count"]:
        lines.append("- _none booked — nothing observed (no false all-clear)._")
        return "\n".join(lines)
    lines.append("- by node: " + ", ".join(f"{n} {c}" for n, c in d["by_node"].items()))
    lines.append("- by verdict: " + ", ".join(f"{v} {c}" for v, c in d["by_verdict"].items()))
    lines.append("")
    lines.append("## Each run, attributable to its governed prompt")
    for r in d["receipts"]:
        lines.append(f"- `{r.get('subject')}` → **{r.get('verdict')}** "
                     f"({r.get('node')} @ {r.get('prompt_hash')}): {r.get('reason')}")
    return "\n".join(lines)


# ---------------------------------------------------------------- CLI

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--run", help="a run id to read the monitor fold for")
    ap.add_argument("--json", action="store_true",
                    help="emit the raw dataset (machine-readable), not the prose")
    sub = ap.add_subparsers(dest="cmd")

    op = sub.add_parser("open", help="open a training run (the posture, on the books)")
    op.add_argument("--by", required=True)
    op.add_argument("--note")

    cl = sub.add_parser("close", help="close a training run (superseding admission)")
    cl.add_argument("--run", dest="close_run", required=True)
    cl.add_argument("--by", required=True)

    bk = sub.add_parser("receipt", help="book one agent run on the books (teeth at the seam)")
    bk.add_argument("--run", dest="book_run", required=True)
    bk.add_argument("--node", required=True)
    bk.add_argument("--prompt-hash", required=True)
    bk.add_argument("--subject", required=True)
    bk.add_argument("--verdict", required=True)
    bk.add_argument("--reason", required=True)

    args = ap.parse_args(argv)

    if args.cmd == "open":
        run_id = open_run(args.root, args.by, args.note)
        print(f"result: done — training run opened on the books: {run_id} "
              f"(by {args.by}). Book each agent run with `receipt --run {run_id}`.")
        return 0

    if args.cmd == "close":
        close_run(args.root, args.close_run, args.by)
        print(f"result: done — training run {args.close_run} closed (by {args.by}); "
              "its booked receipts stand as history.")
        return 0

    if args.cmd == "receipt":
        try:
            rid = book_receipt(args.root, args.book_run, args.node, args.prompt_hash,
                               args.subject, args.verdict, args.reason)
        except ValueError as e:
            print(f"result: needs-you — refused: {e}")
            return 2
        print(f"result: done — booked {rid}: {args.subject} -> {args.verdict} "
              f"({args.node}), on the books under {args.book_run}.")
        return 0

    if args.run:
        d = fold_run(args.root, args.run)
        print(canon(d) if args.json else render_run(d))
        print(f"\nresult: report — {d['count']} agent run(s) on the books under "
              f"{args.run} (training; nothing auto-trusted as done).")
        return 0

    d = overview(args.root)
    print(canon(d) if args.json else render_overview(d))
    n = len(d["runs"])
    print(f"\nresult: report — {n} training run(s) on record.")
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
