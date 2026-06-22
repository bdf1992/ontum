#!/usr/bin/env python3
"""loop/prompt_req.py — the prompt-requirements door (C3 of the agent-summoning
requirements; bdo 2026-06-22 "wire it").

A prompt is code (§7), and §5/§7 say a node prompt MUST declare its edges: the
ROLE it plays, what it READS, what it RETURNS, what it WON'T do (D-2), and the
EVALS that back it. Nothing enforced that — a prompt could ship missing an edge
and the rail would deliver it anyway. This is the §10 teeth on prompts
themselves: the same door shape as `loop/phrasing.py` — it PROVES the edges are
declared and REFUSES the prompt otherwise, naming what is missing.

It also serves the rail (C4): `deliver` loads a node's prompt with its sha256
(reusing `reconcile.node_prompt` — the same hash the receipt records) AND its
validity, so a workflow agent is pinned to a GOVERNED prompt with a fingerprint
instead of an inline string, and a prompt that fails the door HALTS the summon
rather than running ungoverned.

Read-only; stdlib; the loop/ law. The edges are matched tolerantly (the existing
node prompts use `## Role` / `## You read` / `## You return` / `## You will not`
/ `## Evals`, but a `## Reads` / `## Won't` phrasing satisfies the same edge) so
the door checks the CONTRACT, not the spelling. Ends with a clear result line.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from loop import reconcile
from loop.reconcile import DEFAULT_ROOT

# Each edge: (key, human name, the heading patterns that satisfy it). A node
# prompt declares the edge by carrying one of its headings. Matched on `##`-level
# headings, case-insensitive — the contract, not the exact words.
EDGES = [
    ("role", "the role it plays", [r"role\b"]),
    ("reads", "what it reads", [r"you read\b", r"reads?\b", r"what you read\b", r"inputs?\b"]),
    ("returns", "what it returns (one verdict from the terminal set)",
     [r"you return\b", r"returns?\b", r"output\b", r"verdict\b"]),
    ("wont", "what it will not do (D-2)",
     [r"you will not\b", r"will not\b", r"won'?t\b", r"you won'?t\b", r"refus", r"never\b"]),
    ("evals", "the evals that back it", [r"evals?\b", r"eval\b", r"tests?\b"]),
]

_HEADING = re.compile(r"(?m)^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$")
_VERSION = re.compile(r"(?mi)^\s*version:\s*\S")
_TITLE = re.compile(r"(?m)^\s{0,3}#\s+\S")


def _headings(text):
    return [m.group(1).strip().lower() for m in _HEADING.finditer(text)]


def validate(text):
    """Return the list of problems (empty == the prompt declares every edge). A
    prompt with no problems passes the door; any problem refuses it."""
    problems = []
    if not _TITLE.search(text or ""):
        problems.append("no title heading (`# <node-id> — <what it is>`)")
    if not _VERSION.search(text or ""):
        problems.append("no `version:` line (§7: a prompt is versioned source)")
    heads = _headings(text or "")
    blob = " || ".join(heads)
    for key, name, pats in EDGES:
        if not any(re.search(p, blob) for p in pats):
            problems.append(f"missing the **{key}** edge — {name} "
                            f"(no heading matches {pats[0]!r})")
    return problems


def deliver(root, node):
    """Load a node's governed prompt with its sha256 and its validity — the
    bridge that pins a workflow agent to prompt-as-code (C4). Returns
    {node, found, prompt, prompt_hash, valid, problems}. A missing prompt file is
    `found: False` (absence is information); a present-but-invalid prompt is
    `valid: False` with the problems named, so the caller HALTS rather than
    runs an ungoverned prompt."""
    text, phash = reconcile.node_prompt(Path(root), node)
    if text is None:
        return {"node": node, "found": False, "prompt": None,
                "prompt_hash": None, "valid": False,
                "problems": [f"no prompt file at .ai-native/nodes/{node}.md"]}
    problems = validate(text)
    return {"node": node, "found": True, "prompt": text, "prompt_hash": phash,
            "valid": not problems, "problems": problems}


def _all_nodes(root):
    d = Path(root) / "nodes"
    if not d.is_dir():
        return []
    return sorted(p.stem for p in d.glob("*.md"))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=Path(DEFAULT_ROOT))
    sub = ap.add_subparsers(dest="cmd")

    cp = sub.add_parser("check", help="validate one node prompt (the door)")
    cp.add_argument("--node", required=True)

    sub.add_parser("check-all", help="fold the door over every node prompt")

    dp = sub.add_parser("deliver", help="load a node's governed prompt + hash + validity (the rail bridge)")
    dp.add_argument("--node", required=True)
    dp.add_argument("--json", action="store_true")

    args = ap.parse_args(argv)
    cmd = args.cmd or "check-all"

    if cmd == "deliver":
        d = deliver(args.root, args.node)
        if args.json:
            print(json.dumps(d, ensure_ascii=False))
            return 0
        if not d["found"]:
            print(f"result: needs-you — {d['problems'][0]}")
            return 2
        if not d["valid"]:
            print(f"result: needs-you — prompt '{args.node}' fails the door:\n  - "
                  + "\n  - ".join(d["problems"]))
            return 2
        print(f"  {args.node} — {d['prompt_hash']} — valid")
        print(f"result: done — governed prompt delivered ({len(d['prompt'])} bytes, "
              f"{d['prompt_hash']}); pin the agent to this hash")
        return 0

    if cmd == "check":
        problems = deliver(args.root, args.node)["problems"]
        if problems:
            print(f"result: report — '{args.node}' fails the prompt-requirements "
                  f"door:\n  - " + "\n  - ".join(problems))
            return 2
        print(f"result: done — '{args.node}' declares every required edge "
              "(role · reads · returns · won't · evals + version + title)")
        return 0

    # check-all
    nodes = _all_nodes(args.root)
    if not nodes:
        print("result: report — no node prompts found")
        return 0
    bad = 0
    print("# the prompt-requirements door, over every node prompt\n")
    for n in nodes:
        problems = validate(reconcile.node_prompt(args.root, n)[0] or "")
        if problems:
            bad += 1
            print(f"- {n}: FAILS — {len(problems)} missing ({problems[0].split('—')[0].strip()} …)")
        else:
            print(f"- {n}: ok")
    verb = "report" if bad else "done"
    print(f"\nresult: {verb} — {len(nodes)} prompt(s), {bad} fail the door; a "
          "failing prompt may not be summoned (it ships missing an edge)")
    return 0 if not bad else 2


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
