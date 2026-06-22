#!/usr/bin/env python3
"""loop/rename.py — the rename ledger (decided once) + the deterministic applier.

bdo, 2026-06-22, naming the failure: "we're not renaming it [per file]; we write
down that it was renamed, ONCE, then we rename it EVERYWHERE." A vocabulary
rename — organ -> part, metabolism -> cycle — kept RECURRING as stranded one-off
sed branches (`organ-to-part-prose`, `heal-organ`, `owner-harness-organs`), each
re-deciding the same swap by hand and each breaking grammar on the way ("an part
that senses", misaligned docstring tables). The recurrence *is* the per-file
re-decision.

The fix is the repo's own spine, applied to vocabulary:

  the log is truth; everything else is a fold.

So a rename is not constants in code and not a workflow of judging agents — it is
an ADMITTED RECORD (written once, signed `--by`, superseding, like a `tag`), and
application is a DETERMINISTIC FOLD over that record across the live tree. Decide
once with `admit`; apply everywhere with `apply`; re-run to see zero in-scope
hits remain — that last property is how "it stops occurring" becomes *checkable*,
not asserted.

Two teeth keep the everywhere-apply safe:

  1. A handle-safe boundary. The word is rewritten ONLY when it stands alone —
     never when it is glued into an identifier, a filename, or a dotted/hyphened
     handle (`organ_gaps`, `find_organs`, `strategy-metabolism.md`,
     `epic.test-metabolism`, the agenda handle `the-metabolism`). The boundary
     treats `_ . / -` as joining chars, so a compound is never touched.

  2. The phrasing door as the gate (I-4, reusing `loop.phrasing`). After the
     substitution, the edit must PROVE prose-only by the very checker the PR pen
     re-runs server-side. A file where the rename would touch a code token (e.g.
     `census.py`, which uses `organs`/`organ` as live identifiers) fails the door
     and is SKIPPED and FLAGGED for the code-tier wave — it is never written.
     Consequence: the whole sweep is provably prose-only, so it lands through the
     phrasing light-lane with no atoms.

Stdlib only; no network; no git (loop/'s law). Read-only except `admit`/`apply`,
which append to the log and write the proven prose edits. Ends with the clear
result line: done | report | needs-you.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT, Fold, append_line, now_ts, short_hash
from loop.phrasing import phrasing_only

# The chars that, adjacent to a match, mean the word is part of a compound
# (identifier / filename / dotted-or-hyphened handle) and must NOT be renamed.
# `\w` is letters+digits+underscore; we add `/`, `-`. A trailing
# `.` is sentence punctuation (renamed); a `.`+wordchar is a dotted
# compound like `.md` (preserved by the (?!\.\w) guard in _rule_regex).
_JOIN = r"[\w/\-]"
_VOWELS = set("aeiou")

# Files the applier may consider at all. Prose + the kinds the phrasing door can
# vet (.md/.py/.json/.txt). The door is the safety gate; this is just the net.
_EXTS = ("md", "txt", "markdown", "py", "json")

# Trees that are records, truth, read-only, or generated — never walked. Records
# are append-only or frozen history; atoms are content-hash identity; docs/phase-2
# and docs/sources are read-only by hard rule; nodes are hashed prompts; the
# generated outputs are derived, not authored.
_EXCLUDE_DIRS = (
    ".git", "node_modules", "__pycache__", ".claude/worktrees",
    ".ai-native/log", ".ai-native/done", ".ai-native/reports",
    ".ai-native/atoms", ".ai-native/epics", ".ai-native/agendas",
    ".ai-native/nodes", ".ai-native/offsets", ".ai-native/queues",
    "docs/phase-2", "docs/sources",
    # exports/ are rebuildable, gitignored envoy artifacts (re-sealed from the
    # renamed source) and the committed log.jsonl is an append-only ledger —
    # never material to rename.
    "exports",
)
# Specific generated, data, or self-referential files (authored siblings in the
# same dirs stay in scope). The rename pen and its test legitimately QUOTE the
# words as examples ("organ -> part"); renaming them would self-corrupt.
_EXCLUDE_FILES = (
    "glyphs/registry.json", "glyphs/knolling.md",
    "loop/gate_eval.cases.json",          # the value-gate eval corpus (data)
    "loop/rename.py", "tests/test_rename.py",  # they document the rename
)
# Generated/data file suffixes that look authored but are folds or evidence.
_EXCLUDE_SUFFIXES = (".projection.json", ".seed.json")


# ----------------------------------------------------------------- the ledger
# A rename is an admitted record: {from, to, by, because, withdrawn, ts}. The
# decision, written ONCE. Latest admission per `from` wins; a withdrawn one drops
# the rule (superseding, never erasing — history is never retro-invalidated).

def admitted_renames(fold):
    """The active rename rules folded from the log, oldest-decided first.
    Latest admission per source word wins; `withdrawn` removes the rule."""
    by_src = {}
    for adm in fold.admissions:
        if adm.get("type") != "rename":
            continue
        frm, to = adm.get("from"), adm.get("to")
        if not frm or not to:
            continue
        by_src[frm.lower()] = None if adm.get("withdrawn") else (frm, to)
    return [v for v in by_src.values() if v]


def admit_rename(root, frm, to, by, because="", withdrawn=False):
    """Write the rename decision once — signed `--by`, superseding a prior one."""
    adm = {
        "id": "adm." + short_hash("rename", frm, to, str(withdrawn), str(by), now_ts()),
        "type": "rename",
        "from": frm,
        "to": to,
        "because": because,
        "withdrawn": bool(withdrawn),
        "by": by,
        "ts": now_ts(),
    }
    append_line(root / "log" / "admissions.jsonl", adm)
    return adm


# ----------------------------------------------------------- the deterministic swap

def _case_like(template, word):
    """Re-case ``word`` to match ``template``'s shape (UPPER / Title / lower)."""
    if template.isupper():
        return word.upper()
    if template[:1].isupper():
        return word[:1].upper() + word[1:]
    return word


def _rule_regex(frm):
    """Match ``frm`` (singular or regular plural), standing alone (not inside a
    compound), optionally preceded by an indefinite article. Case-insensitive;
    the replacement re-cases from the matched text."""
    f = re.escape(frm)
    return re.compile(
        rf"(?P<art>\b[Aa]n?\b[ \t]+)?"      # optional "a "/"an " directly before
        rf"(?<!{_JOIN})(?P<word>{f}s|{f})(?!{_JOIN})(?!\.\w)",
        re.IGNORECASE,
    )


def _replacer(frm, to):
    def repl(m):
        word = m.group("word")
        plural = word.lower().endswith("s") and word.lower() != frm.lower()
        new = to + "s" if plural else to
        new = _case_like(word, new)
        art = m.group("art")
        if not art:
            return new
        # Re-derive the indefinite article from the NEW word's first sound
        # (deterministic vowel-letter heuristic) so "an organ" -> "a part" and
        # "a metabolism" -> "a cycle" come out grammatical, not "an part".
        head = "an" if new[:1].lower() in _VOWELS else "a"
        orig = art.strip()
        ws = art[len(orig):]
        head = _case_like(orig, head)
        return f"{head}{ws}{new}"
    return repl


def _article_fix_regex(to):
    """An indefinite article directly before a `to` word — to repair agreement
    LEFT BY ANY PRIOR RENAME, not only this run's. A naive sed that wrote
    "organ"->"part" left "an organ" as "an part" all over main; this finds that
    wreckage wherever the rename already happened."""
    return re.compile(rf"\b(?P<art>[Aa]n?)(?P<ws>[ \t]+)(?P<w>{re.escape(to)}s?)\b")


def _article_fixer(to):
    def fix(m):
        new = "an" if to[:1].lower() in _VOWELS else "a"
        return f"{_case_like(m.group('art'), new)}{m.group('ws')}{m.group('w')}"
    return fix


def rename_text(text, rules):
    """Apply every rule with the handle-safe boundary, then repair indefinite
    articles before every `to` word — so the fix and ITS grammatical consequence
    propagate together, and a prior sloppy rename's "an part" is healed wherever
    it sits. Pure, deterministic, idempotent (a second pass is a no-op)."""
    for frm, to in rules:
        text = _rule_regex(frm).sub(_replacer(frm, to), text)
    for _, to in rules:
        text = _article_fix_regex(to).sub(_article_fixer(to), text)
    return text


def _preserved_count(text, rules):
    """How many occurrences were deliberately LEFT because the word is glued
    into a compound (identifier/filename/handle) — surfaced so the apply never
    silently caps. A whole-word hit that the safe boundary refused to take."""
    n = 0
    for frm, _ in rules:
        f = re.escape(frm)
        whole = re.compile(rf"\b(?:{f}s|{f})\b", re.IGNORECASE)
        safe = _rule_regex(frm)
        n += len(whole.findall(text)) - len(safe.findall(text))
    return n


# ------------------------------------------------------------------- the walk

def _in_scope(rel):
    rel = rel.replace("\\", "/")
    if any(rel == f or rel.startswith(f + "/") for f in _EXCLUDE_DIRS):
        return False
    if rel in _EXCLUDE_FILES or any(rel.endswith(s) for s in _EXCLUDE_SUFFIXES):
        return False
    return rel.rsplit(".", 1)[-1].lower() in _EXTS if "." in rel else False


def _candidates(repo):
    for p in sorted(repo.rglob("*")):
        if not p.is_file():
            continue
        rel = str(p.relative_to(repo)).replace("\\", "/")
        if _in_scope(rel):
            yield p, rel


def _read(p):
    with open(p, "r", encoding="utf-8", newline="") as fh:  # preserve EOLs
        return fh.read()


def _write(p, text):
    with open(p, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def scan(repo, rules):
    """Pure read: classify every in-scope file with in-scope occurrences into
    `clean` (the rename is prove-prose-only, will land), `flagged` (the rename
    would touch code/schema — the code-tier wave), and `preserved` (compound
    occurrences left whole)."""
    clean, flagged, preserved = [], [], 0
    for p, rel in _candidates(repo):
        try:
            before = _read(p)
        except (OSError, UnicodeDecodeError):
            continue
        after = rename_text(before, rules)
        preserved += _preserved_count(before, rules)
        if after == before:
            continue
        ok, why = phrasing_only(rel, before, after)
        if ok:
            clean.append(rel)
        else:
            flagged.append((rel, why))
    return clean, flagged, preserved


# ----------------------------------------------------------------- the surfaces

def status(root):
    fold = Fold(root)
    rules = admitted_renames(fold)
    if not rules:
        print("result: needs-you — no rename is decided yet. Write the decision "
              "once, then it applies everywhere:\n"
              "  python -m loop.rename admit --from organ --to part --by bdo "
              "--because \"...\"")
        return 2
    print("the rename ledger (decided once, on the log):")
    for frm, to in rules:
        print(f"  {frm} -> {to}")
    repo = root.resolve().parent
    clean, flagged, preserved = scan(repo, rules)
    print(f"\nwould rename {len(clean)} prose file(s) (provably prose-only — "
          f"the phrasing light-lane lands them, no atom):")
    for rel in clean:
        print(f"  {rel}")
    if flagged:
        print(f"\n{len(flagged)} file(s) flagged — the rename would touch code or "
              f"schema (the code-tier wave, route through the pipeline):")
        for rel, why in flagged:
            print(f"  {rel}: {why}")
    if preserved:
        print(f"\npreserved (left whole): {preserved} occurrence(s) glued into an "
              f"identifier/filename/handle — never a silent cap")
    if not clean and not flagged:
        print("\nresult: done — zero in-scope occurrences remain; the rename has "
              "fully landed (this is the 'it stops occurring' check)")
        return 0
    print("\nresult: report — run `python -m loop.rename apply --by <who>` to "
          "land the clean tier; the flagged tier is a code-rename wave")
    return 0


def apply(root, by):
    fold = Fold(root)
    rules = admitted_renames(fold)
    if not rules:
        print("result: needs-you — nothing to apply: decide the rename first "
              "(`python -m loop.rename admit --from organ --to part --by bdo`)")
        return 2
    repo = root.resolve().parent
    clean, flagged, preserved = scan(repo, rules)
    written = []
    for rel in clean:
        p = repo / rel
        before = _read(p)
        after = rename_text(before, rules)
        ok, _ = phrasing_only(rel, before, after)  # re-prove at the write seam
        if after != before and ok:
            _write(p, after)
            written.append(rel)
    if written:
        adm = {
            "id": "adm." + short_hash("rename_applied", by, str(len(written)), now_ts()),
            "type": "rename_applied",
            "rules": [{"from": f, "to": t} for f, t in rules],
            "files": written,
            "preserved": preserved,
            "by": by,
            "ts": now_ts(),
        }
        append_line(root / "log" / "admissions.jsonl", adm)
    print(f"renamed {len(written)} prose file(s) — all provably prose-only "
          f"(phrasing light-lane; mark with `pr.py phrasing` to land without an atom):")
    for rel in written:
        print(f"  {rel}")
    if flagged:
        print(f"\nleft {len(flagged)} file(s) for the code-tier wave (the rename "
              f"would touch code/schema there):")
        for rel, why in flagged:
            print(f"  {rel}: {why}")
    if preserved:
        print(f"\npreserved {preserved} compound occurrence(s) (identifier/handle) "
              f"by design")
    print(f"\nresult: report — {len(written)} file(s) renamed by the deterministic "
          f"applier over the decided ledger; re-run `status` to confirm zero clean "
          f"occurrences remain")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="loop.rename",
                                 description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd")

    st = sub.add_parser("status", help="the ledger + what would rename / is flagged (read-only)")
    st.add_argument("--root", type=Path, default=DEFAULT_ROOT)

    ad = sub.add_parser("admit", help="write a rename decision ONCE (signed --by)")
    ad.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ad.add_argument("--from", dest="frm", required=True, help="the word to retire")
    ad.add_argument("--to", required=True, help="what it becomes")
    ad.add_argument("--because", default="", help="why (provenance for a cold reader)")
    ad.add_argument("--withdraw", dest="withdrawn", action="store_true",
                    help="supersede a prior rename decision (latest wins)")
    ad.add_argument("--by", required=True, help="who decided it (the ledger is signed)")

    ap_ = sub.add_parser("apply", help="rename EVERYWHERE from the decided ledger (phrasing-gated)")
    ap_.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap_.add_argument("--by", required=True, help="who ran the sweep (provenance)")

    args = ap.parse_args(argv)
    if args.cmd == "admit":
        adm = admit_rename(args.root, args.frm, args.to, args.by,
                           because=args.because, withdrawn=args.withdrawn)
        verb = "withdrew" if args.withdrawn else "decided"
        print(f"result: report — {adm['id']}: {verb} rename {args.frm} -> "
              f"{args.to} (by {args.by}). Apply it everywhere: "
              f"python -m loop.rename apply --by {args.by}")
        return 0
    if args.cmd == "apply":
        return apply(args.root, args.by)
    return status(args.root if args.cmd == "status" else DEFAULT_ROOT)


if __name__ == "__main__":
    sys.exit(main())
