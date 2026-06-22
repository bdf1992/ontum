#!/usr/bin/env python3
"""The part census (done-line 0029): the loop sensing its own body.

bdo named a turning point — prune what didn't land, care for what did,
and "monitor the signals we have encoded ... to find what needs more
attention and how." The watcher (`.claude/hooks/command_guard.py
--report`) already monitors one signal: which raw tool wants a wrapper.
This is its sibling for the repo's own parts — which modules, hooks,
and pens actually carry weight, and which were built, tested, and then
left dormant.

The census is a fold, never a memory (the loop's law): it derives
everything from what is on disk right now. Two pure signals, both
stdlib — no subprocess, no network, no git (hard rule):

  wired      — some live source file (not the part's own test) imports
               or invokes it. Reachability into the working system.
  exercised  — the part's source speaks at least one *word the record
               actually holds*: a string literal of its that appears as
               a logged value in an append-only ledger. Behavioural
               proof that something has flowed through it.

The verdict crosses the two, and the three states are exactly bdo's
three movements:

  alive       exercised — a piece that landed; give it care.
  wired·idle  connected but never exercised — built into the path, yet
              nothing has flowed (a mock never made real, a ladder never
              climbed). This is what "needs more attention" looks like.
  dormant     neither wired nor exercised — built, perhaps tested, but
              the cycle never touches it. A prune candidate.

"exercised" is a vocabulary trace, not a call graph — it can miss a
part that records only words it shares with no one, and the output
names the word it matched so a human can audit. Read-only (I-3): this
counts and reports; it never prunes. What to cut or make real stays the
owner's call (D-4).

CLI:
  python -m loop.census          the part census, read-only
"""

import argparse
import json
import re
import sys
from pathlib import Path

# loop/census.py -> loop/ -> repo root. Works the same in a worktree.
REPO = Path(__file__).resolve().parent.parent

# Where parts live, as globs under the repo root. Filesystem-derived so
# a new part enrolls itself — no hand-list to rot (the §12 trap).
PART_GLOBS = (
    ("loop-module", "loop/*.py"),
    ("hook", ".claude/hooks/*.py"),
    ("skill-pen", ".claude/skills/*/*.py"),
    ("glyph", "glyphs/*.py"),
)
SKIP_NAMES = {"__init__.py"}

# The append-only ledgers a part's words can land in: the three logs,
# the watcher's audit, and the envoy's disclosure ledger.
LEDGER_GLOBS = (".ai-native/log/*.jsonl", "exports/*.jsonl")

# Keys whose values are prose or raw capture, not controlled vocabulary —
# a reason or a captured shell command shares generic English with any
# source file ("local", "node", "done") and would forge a false trace.
# The record's *naming* fields (type, kind, node, status, verb, by, act)
# are what prove a part's vocabulary actually flowed.
NOISE_KEYS = frozenset({
    "command", "bins", "reason", "headline", "value", "why_now",
    "if_accepted", "if_rejected", "cost_of_wrong_call", "text", "comment",
    "body", "detail", "note", "description", "story", "narrative",
    "summary", "title",
})

# A part is a *writer* if its source can append to a record. A reader —
# a render or summons surface — is meant to be silent; its lack of a trace
# is by design, not neglect. Only a writer with no record is "built but
# never flowed".
WRITER_MARKS = ("append_line", ".jsonl")

# The wiring corpus is the working system — code, config, harness docs —
# not the read-only vault, not the records (a mention in a report is not
# use), not the tests (a part used only by its own test is not wired).
CORPUS_GLOBS = ("*.py", "*.json", "*.md",
                "loop/*", "glyphs/*", "language/*", ".claude/**/*")
CORPUS_EXCLUDE = ("/.git/", "__pycache__", "/tests/", "/docs/",
                  "/.ai-native/", "/exports/")

SETTINGS = Path(".claude/settings.json")

# A string literal in source; >=4 chars to skip noise like "" or "v0".
LITERAL = re.compile(r"""["']([^"'\n]{4,})["']""")
MAINGUARD = "__main__"


def find_parts(repo):
    parts = []
    for kind, glob in PART_GLOBS:
        for p in sorted(repo.glob(glob)):
            if p.name in SKIP_NAMES:
                continue
            parts.append({"kind": kind, "path": p,
                           "rel": p.relative_to(repo).as_posix(),
                           "name": p.stem})
    return parts


def ref_regex(part):
    """The pattern that means 'this part is being used' — an import, a
    dotted use, or a path mention, by kind. Never the bare stem (too many
    words are also a module's name). Covers the repo's dominant import
    style, `from loop import X` (including `from loop import a, X`)."""
    n = re.escape(part["name"])
    pats = [re.escape(part["rel"]), rf"\b{n}\.py\b"]
    if part["kind"] == "loop-module":
        pats += [rf"\bloop\.{n}\b", rf"\bloop/{n}\b",
                 rf"from\s+loop\s+import\s+[^\n]*\b{n}\b",
                 rf"from\s+\.{n}\s+import", rf"from\s+\.\s+import\s+[^\n]*\b{n}\b"]
    elif part["kind"] == "glyph":
        pats += [rf"\bglyphs\.{n}\b", rf"\bglyphs/{n}\b",
                 rf"from\s+glyphs\s+import\s+[^\n]*\b{n}\b"]
    return re.compile("|".join(pats))


def wiring_corpus(repo):
    """Every working-system file's text, keyed by relative path, minus the
    vault, records, and tests. Deduped (the globs overlap on purpose)."""
    seen, out = set(), []
    for glob in CORPUS_GLOBS:
        for p in repo.glob(glob):
            if not p.is_file():
                continue
            rel = p.relative_to(repo).as_posix()
            if rel in seen or any(x.strip("/") in f"/{rel}/" for x in CORPUS_EXCLUDE):
                continue
            seen.add(rel)
            try:
                out.append((rel, p.read_text(encoding="utf-8", errors="ignore")))
            except OSError:
                continue
    return out


def ledger_vocab(repo):
    """Every distinct string value the record actually holds (>=4 chars),
    folded over the append-only ledgers. Torn-tail tolerant: a line that
    won't parse never happened, like the rest of the loop."""
    vocab = set()

    def walk(v):
        if isinstance(v, str):
            # controlled vocabulary only: no prose (whitespace), >=4 chars
            if len(v) >= 4 and not any(c.isspace() for c in v):
                vocab.add(v)
        elif isinstance(v, dict):
            for k, x in v.items():
                if k not in NOISE_KEYS:
                    walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)

    for glob in LEDGER_GLOBS:
        for p in repo.glob(glob):
            try:
                lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
            except OSError:
                continue
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    walk(json.loads(line))
                except json.JSONDecodeError:
                    continue  # torn tail or partial write — it never happened
    return vocab


def classify(part, corpus, vocab, settings_text):
    src = ""
    try:
        src = part["path"].read_text(encoding="utf-8", errors="ignore")
    except OSError:
        pass
    rx = ref_regex(part)

    importers = sorted({rel for rel, text in corpus
                        if rel != part["rel"] and rx.search(text)})
    entrypoint = (MAINGUARD in src) or bool(rx.search(settings_text))

    literals = set(LITERAL.findall(src))
    traces = sorted(literals & vocab)

    wired = bool(importers)
    connected = wired or entrypoint
    exercised = bool(traces)
    writer = any(m in src for m in WRITER_MARKS)

    if exercised:
        verdict = "alive"            # records prove it ran
    elif not connected:
        verdict = "dormant"          # disconnected — prune candidate
    elif writer:
        verdict = "wired·idle"       # built to write, never wrote — attention
    else:
        verdict = "alive"           # a wired read-only surface; silence is by design

    return {**part, "importers": importers, "entrypoint": entrypoint,
            "wired": wired, "connected": connected, "exercised": exercised,
            "writer": writer, "traces": traces, "verdict": verdict}


def census(repo):
    corpus = wiring_corpus(repo)
    vocab = ledger_vocab(repo)
    settings = repo / SETTINGS
    settings_text = settings.read_text(encoding="utf-8", errors="ignore") \
        if settings.exists() else ""
    return [classify(o, corpus, vocab, settings_text)
            for o in find_parts(repo)]


ORDER = {"dormant": 0, "wired·idle": 1, "alive": 2}
GLOSS = {
    "dormant": "neither wired nor exercised — built, maybe tested, "
               "untouched by the cycle; a prune candidate",
    "wired·idle": "connected but never exercised — in the path, but "
                       "nothing has flowed; this is 'needs attention'",
    "alive": "exercised — a word it speaks is on the record; give it care",
}


def render(results):
    by_verdict = {}
    for r in results:
        by_verdict.setdefault(r["verdict"], []).append(r)
    for verdict in sorted(by_verdict, key=lambda v: ORDER.get(v, 9)):
        rows = sorted(by_verdict[verdict], key=lambda r: r["rel"])
        print(f"\n{verdict} ({len(rows)}) — {GLOSS.get(verdict, '')}")
        for r in rows:
            print(f"  {r['rel']}")
            if r["verdict"] == "alive" and r["exercised"]:
                shown = ", ".join(r["traces"][:3])
                more = "…" if len(r["traces"]) > 3 else ""
                print(f"      on the record: {shown}{more}")
            elif r["verdict"] == "alive":
                wiring = (f"imported by {len(r['importers'])}" if r["wired"]
                          else "entrypoint")
                print(f"      read-only surface — silent by design ({wiring})")
            else:
                bits = []
                bits.append(f"imported by {len(r['importers'])}" if r["wired"]
                            else "imported by none")
                if r["entrypoint"]:
                    bits.append("entrypoint")
                bits.append("writer with no record" if r["writer"]
                            else "no recorded trace")
                print(f"      {', '.join(bits)}")
    dormant = len(by_verdict.get("dormant", []))
    idle = len(by_verdict.get("wired·idle", []))
    print()
    if dormant or idle:
        print(f"result: report — {len(results)} part(s): "
              f"{dormant} dormant, {idle} wired·idle, "
              f"{len(by_verdict.get('alive', []))} alive. The dormant ones "
              f"are prune candidates; the idle ones are built-but-not-flowing "
              f"(make them real or retire them). The cut stays yours (D-4).")
    else:
        print(f"result: done — all {len(results)} part(s) alive; "
              f"every part speaks a word the record holds")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", type=Path, default=REPO,
                    help="repo root to take the census of (default: this one)")
    args = ap.parse_args(argv)
    return render(census(args.repo))


if __name__ == "__main__":
    sys.exit(main())
