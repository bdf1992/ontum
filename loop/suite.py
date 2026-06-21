#!/usr/bin/env python3
"""The test-suite economy (done-line 0171): the loop sensing its test body.

`census.py` senses the loop's *code* body — which organs carry weight,
which lie dormant. This is its sibling for the *test* body: 826 tests
across 67 files that, until now, were accounted only by whatever
`unittest discover` prints. bdo asked for the suite to be **broken down,
typed, accounted, and attributed**, and to run *like running water* —
ambient, taken for granted because it works, not because it is ignored.

This is the foundation piece: the read-only fold the later
operator/administrator nodes and the mutation / change-scope assays all
ride. It does three things, all derived from bytes on disk:

  type        each test resolves to one kind by *structural* evidence —
              guard / refusal / byte-determinism / fold / pen-seam /
              integration / unit — and to an honest **untyped** when no
              signal decides. Derived, not declared (bdo's call): we
              infer from structure and surface the undecidable as a gap,
              never guess a label (the tags.py discipline).
  attribute   each test names the organ(s) it covers (filename
              convention + imports + subprocess/path targets resolved
              against the real loop/*.py, hooks, and skill pens) and the
              done-line(s)/clauses it pins (docstrings + cited tokens).
  account     a census: type histogram, organ -> covering-test count (an
              untested organ named, the census.py wired-idle grain), and
              frozen-done-line -> pinning-test count (an unpinned line is
              an unreceipted-contract finding).

The teeth (§10), pinned by tests/test_suite.py: `refusal` is assigned
only on *evidence* of a rejection assertion, so a test whose NAME claims
refusal but whose body asserts none surfaces as **mislabeled**; an
undecidable test reads **untyped**, never a fabricated type. Read-only
(I-3): this counts and names; the cut stays the owner's (D-4). Stdlib
only; deterministic — re-running over the same committed bytes yields
identical output. CLI ends with a clear result on stdout (D-6).

CLI:
  python -m loop.suite census          the accounting + findings (default)
  python -m loop.suite census --json   the full dataset, machine-readable
"""

import argparse
import ast
import json
import re
import sys
from pathlib import Path

# loop/suite.py -> loop/ -> repo root. Works the same in a worktree.
REPO = Path(__file__).resolve().parent.parent

TEST_GLOB = "tests/test_*.py"

# Organs a test can cover, as (kind, glob) — filesystem-derived so a new
# organ enrolls itself (the census.py grain; no hand-list to rot, §12).
ORGAN_GLOBS = (
    ("loop", "loop/*.py"),
    ("hook", ".claude/hooks/*.py"),
    ("skill", ".claude/skills/*/*.py"),
    ("glyph", "glyphs/*.py"),
    ("causality", "causality/*.py"),
)
SKIP_ORGAN_NAMES = {"__init__", "suite"}  # suite.py does not test itself

DONE_GLOB = ".ai-native/done/[0-9]*.md"

# ---------------------------------------------------------------------------
# signals: regex over a single test method's own source segment
# ---------------------------------------------------------------------------

# Words that, when asserted on, are evidence of a rejection being checked.
REJECT_WORDS = (
    "refus", "deny", "denied", "denies", "forbid", "frozen", "escalat",
    "invalid", "reject", "not allowed", "rejected", "refused", "must not",
    "cannot", "illegal", "nothing", "never", "no rule", "no reach",
)
# Refusal vocabulary in a method NAME (a *claim* about what the test does).
# Strong, word-boundaried verbs only — ambiguous substrings ("block" in
# "unblocker"/"without_blocking", idempotence words "no_op"/"twice") are
# excluded so the mislabel finding stays precise (running water, not noise).
NAME_REFUSAL = re.compile(
    r"(?:^|_)(refus\w*|reject\w*|den(?:y|ies|ied)|forbid\w*|must_not|"
    r"cannot|illegal|invalid\w*|escalat\w*)(?:_|s?$)")
# Determinism / reproducibility vocabulary (the fold kind).
DETERMINISM = re.compile(
    r"determinis|idempot|byte.?identical|replay|rebuild|reproduc|"
    r"round.?trip|same_bytes|stable")
# Seam vocabulary (the one pen / write-twice / wrong-node contract).
SEAM = re.compile(r"\bjudge\(|append_line|loop\.node|write.?twice|"
                  r"second_write|same_receipt|one pen")

ASSERT_CALL = re.compile(r"\bself\.assert\w+\(|\bassert\b")
ASSERT_RAISES = re.compile(r"assertRaises|pytest\.raises|self\.assertRaisesRegex")
READ_BYTES = re.compile(r"\.read_bytes\(")
TEMP_ROOT = re.compile(r"make_root|mkdtemp|TemporaryDirectory|tempfile\.")
SUBPROCESS = re.compile(r"subprocess\.|Popen\(|check_output|\.run\(")
# An exit-2 / non-zero return-code assertion (the guard contract).
EXIT_CODE = re.compile(
    r"returncode|exit.?code|\bcode\b.*\b[12]\b|\[0\]\s*,\s*[12]\b|"
    r"assert\w*\([^)]*\bcode\b[^)]*[,=]\s*[12]\b")
# A negated / absence assertion — a rejection checked by what is NOT there
# (empty, None, False, not-in, equal-to-nothing). Evidence of a refusal
# without a reject-word in sight.
NEGATIVE_ASSERT = re.compile(
    r"assertIsNone\(|assertFalse\(|assertNotIn\(|assertNotEqual\(|"
    r",\s*(?:\[\]|\{\}|\"\"|'')\s*\)|"
    r"==\s*(?:\[\]|\{\}|\"\"|'')")


def _has_reject_word(src):
    low = src.lower()
    return any(w in low for w in REJECT_WORDS)


def method_signals(name, src, file_uses_subprocess):
    """Pure structural read of one test method. No file IO, no guessing —
    every key is a boolean derived from the method's own source bytes
    (plus whether its file imports subprocess, for the guard contract)."""
    has_assert = bool(ASSERT_CALL.search(src))
    uses_subprocess = file_uses_subprocess or bool(SUBPROCESS.search(src))
    asserts_returncode = bool(EXIT_CODE.search(src))
    asserts_raises = bool(ASSERT_RAISES.search(src))

    # rejection EVIDENCE — from the body, never the name. This is what
    # lets the mislabel teeth bite (a name that claims refusal the body
    # never delivers).
    asserts_rejection = has_assert and (
        asserts_raises
        or (uses_subprocess and asserts_returncode)
        or bool(NEGATIVE_ASSERT.search(src))
        or _has_reject_word(src)
    )
    return {
        "has_assert": has_assert,
        "uses_subprocess": uses_subprocess,
        "asserts_returncode": asserts_returncode,
        "asserts_raises": asserts_raises,
        "asserts_rejection": asserts_rejection,
        "name_claims_refusal": bool(NAME_REFUSAL.search(name)),
        "uses_read_bytes": bool(READ_BYTES.search(src)),
        "builds_temp_root": bool(TEMP_ROOT.search(src)),
        "determinism": bool(DETERMINISM.search(src) or DETERMINISM.search(name)),
        "mentions_seam": bool(SEAM.search(src)),
    }


def classify(sig):
    """The one classifier. Deterministic, precedence-ordered, evidence-driven.
    A test asserting nothing, or matching no signal, is `untyped` — an
    honest gap, never a fabricated label (the tags.py / term_economy bar).

    Precedence (first match wins; the test pins it):
      subprocess + exit-code assertion        -> guard
      a rejection asserted (not via a guard)   -> refusal   (§10 fit)
      read_bytes compared                      -> byte-determinism
      determinism/reproducibility vocabulary   -> fold
      the one-pen / wrong-node / write-twice   -> pen-seam
      builds & drives a temp root              -> integration
      asserts on a value, none of the above    -> unit
      asserts nothing decisive                 -> untyped
    """
    if not sig["has_assert"]:
        return "untyped"
    if sig["uses_subprocess"] and sig["asserts_returncode"]:
        return "guard"
    if sig["asserts_rejection"]:
        return "refusal"
    if sig["uses_read_bytes"]:
        return "byte-determinism"
    if sig["determinism"]:
        return "fold"
    if sig["mentions_seam"]:
        return "pen-seam"
    if sig["builds_temp_root"]:
        return "integration"
    return "unit"


TYPES = ("guard", "refusal", "byte-determinism", "fold", "pen-seam",
         "integration", "unit", "untyped")

# ---------------------------------------------------------------------------
# attribution: which organ does a test cover, which done-line does it pin
# ---------------------------------------------------------------------------

def organ_inventory(root):
    """{organ_id: rel_path} for every organ a test could cover. organ_id is
    `<kind>.<name>` so loop/census.py -> loop.census, a hook -> hook.<name>."""
    inv = {}
    for kind, glob in ORGAN_GLOBS:
        for p in sorted(root.glob(glob)):
            name = p.stem
            if name in SKIP_ORGAN_NAMES:
                continue
            inv[f"{kind}.{name}"] = str(p.relative_to(root))
    return inv


def attribute_organs(test_file_stem, file_src, inv):
    """Organs a test file covers, by three evidence kinds, most-trusted first:
    the filename convention (test_<organ>.py), then imports, then any
    subprocess/path reference to a real organ. Only names that resolve in the
    inventory are returned — a reference to nothing is dropped, never coined."""
    by_name = {oid.split(".", 1)[1]: oid for oid in inv}
    found = set()

    # 1. filename convention: test_census.py -> census ; test_freeze_guard.py
    slug = test_file_stem[len("test_"):] if test_file_stem.startswith("test_") else ""
    if slug in by_name:
        found.add(by_name[slug])

    # 2 & 3. imports + subprocess/path targets, scanned over the file bytes.
    for m in re.finditer(r"loop[./]([a-z_]+)", file_src):
        found |= {f"loop.{m.group(1)}"} & set(inv)
    for m in re.finditer(r"hooks/([a-z_]+)\.py", file_src):
        found |= {f"hook.{m.group(1)}"} & set(inv)
    for m in re.finditer(r"glyphs/([a-z_]+)\.py", file_src):
        found |= {f"glyph.{m.group(1)}"} & set(inv)
    for m in re.finditer(r"causality/([a-z_]+)\.py", file_src):
        found |= {f"causality.{m.group(1)}"} & set(inv)
    return found


DONE_REF = re.compile(r"done[- ]?lines?\s*#?\s*0*(\d{2,4})", re.IGNORECASE)


def attribute_pins(src):
    """Done-line ids (zero-padded to 4) a test pins, by the convention
    tests/CLAUDE.md states: named in the docstring (`done-line 0029`)."""
    return {f"{int(m.group(1)):04d}" for m in DONE_REF.finditer(src)}


def frozen_done_lines(root):
    """Ids of the frozen done-lines (the done/ directory is frozen)."""
    ids = set()
    for p in sorted(root.glob(DONE_GLOB)):
        m = re.match(r"(\d{4})-", p.name)
        if m:
            ids.add(m.group(1))
    return ids

# ---------------------------------------------------------------------------
# the fold: walk tests/*.py, build per-test records, then account
# ---------------------------------------------------------------------------

def _test_functions(tree):
    """(class_name | None, func_node) for every `def test_*`, methods and
    module-level alike — robust to either layout."""
    out = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test"):
            out.append((None, node))
        elif isinstance(node, ast.ClassDef):
            for sub in node.body:
                if isinstance(sub, ast.FunctionDef) and sub.name.startswith("test"):
                    out.append((node.name, sub))
    return out


def fold(root):
    """Fold tests/*.py into per-test records + the accounting. Deterministic:
    files and tests sorted, no timestamps; identical bytes -> identical out."""
    inv = organ_inventory(root)
    frozen = frozen_done_lines(root)
    tests = []

    for path in sorted(root.glob(TEST_GLOB)):
        text = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue  # a file that won't parse is a finding for the linter, not us
        rel = str(path.relative_to(root))
        file_uses_subprocess = bool(re.search(r"import subprocess", text))
        file_organs = attribute_organs(path.stem, text, inv)
        module_doc = ast.get_docstring(tree) or ""

        for cls, fn in _test_functions(tree):
            src = ast.get_source_segment(text, fn) or ""
            sig = method_signals(fn.name, src, file_uses_subprocess)
            doc = ast.get_docstring(fn) or ""
            pins = attribute_pins(src) | attribute_pins(module_doc)
            qual = f"{rel}::{cls}::{fn.name}" if cls else f"{rel}::{fn.name}"
            tests.append({
                "id": qual,
                "file": rel,
                "name": fn.name,
                "type": classify(sig),
                "asserts_rejection": sig["asserts_rejection"],
                "name_claims_refusal": sig["name_claims_refusal"],
                "has_docstring": bool(doc),
                "organs": sorted(file_organs),
                "pins": sorted(pins & frozen),
            })

    return account(tests, inv, frozen)


def account(tests, inv, frozen):
    """The census over the per-test records + the gap findings."""
    by_type = {t: 0 for t in TYPES}
    for rec in tests:
        by_type[rec["type"]] = by_type.get(rec["type"], 0) + 1

    by_organ = {oid: 0 for oid in inv}
    for rec in tests:
        for oid in rec["organs"]:
            by_organ[oid] = by_organ.get(oid, 0) + 1
    untested = sorted(oid for oid, n in by_organ.items() if n == 0)

    pinned = {}
    for rec in tests:
        for pid in rec["pins"]:
            pinned[pid] = pinned.get(pid, 0) + 1
    unpinned = sorted(fid for fid in frozen if pinned.get(fid, 0) == 0)

    mislabeled = sorted(
        rec["id"] for rec in tests
        if rec["name_claims_refusal"] and not rec["asserts_rejection"])
    untyped = sorted(rec["id"] for rec in tests if rec["type"] == "untyped")

    gaps = []
    for tid in mislabeled:
        gaps.append({"kind": "mislabeled-test", "subject": tid,
                     "why": "the name claims a refusal the body never asserts",
                     "move": "assert the rejection, or rename to its real shape"})
    if untyped:
        gaps.append({"kind": "untyped-tests", "subject": f"{len(untyped)} tests",
                     "why": "no structural signal decides their kind (an honest "
                            "gap, never a guessed label)",
                     "move": "sharpen the test's asserts, or the classifier",
                     "sample": untyped[:8]})
    for oid in untested:
        gaps.append({"kind": "untested-organ", "subject": oid,
                     "why": "no test names this organ (the census wired-idle grain)",
                     "move": "cover it, or say why silence is by design (the cut is bdo's)"})
    if unpinned:
        gaps.append({"kind": "unreceipted-contract",
                     "subject": f"{len(unpinned)} of {len(frozen)} frozen done-lines",
                     "why": "a frozen done-line no test pins is a contract with no receipt",
                     "move": "pin it from the test that proves it (name it in the docstring)",
                     "sample": unpinned[:8]})

    return {
        "totals": {"tests": len(tests), "files": len({r["file"] for r in tests}),
                   "organs": len(inv), "frozen_done_lines": len(frozen)},
        "by_type": by_type,
        "by_organ": dict(sorted(by_organ.items())),
        "untested_organs": untested,
        "done_lines_pinned": len(frozen) - len(unpinned),
        "done_lines_unpinned": unpinned,
        "fit_coverage": sum(1 for r in tests if r["asserts_rejection"]),
        "gaps": gaps,
        "tests": tests,
    }

# ---------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------

def census_lines(view):
    t = view["totals"]
    L = [f"test-suite economy — {t['tests']} tests, {t['files']} files, "
         f"{t['organs']} organs, {t['frozen_done_lines']} frozen done-lines",
         "",
         "  type breakdown"]
    width = max(len(k) for k in view["by_type"])
    for k in TYPES:
        n = view["by_type"][k]
        bar = "#" * (n * 40 // max(view["totals"]["tests"], 1))
        L.append(f"    {k.ljust(width)}  {str(n).rjust(4)}  {bar}")
    L += ["",
          f"  fit-coverage   {view['fit_coverage']} tests assert a rejection "
          f"(the §10 'refuse to fit' bar)",
          f"  attribution    {view['done_lines_pinned']}/"
          f"{t['frozen_done_lines']} frozen done-lines pinned by a test; "
          f"{len(view['untested_organs'])}/{t['organs']} organs have no test",
          ""]
    if view["gaps"]:
        L.append("  findings (read-only — the cut is bdo's, D-4):")
        for g in view["gaps"]:
            L.append(f"    [{g['kind']}] {g['subject']} — {g['why']}")
            L.append(f"        -> {g['move']}")
            if g.get("sample"):
                L.append(f"        e.g. {', '.join(g['sample'])}")
    else:
        L.append("  no findings — the suite is fully typed, attributed, and pinned")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="loop.suite", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    c = sub.add_parser("census", help="the accounting + findings (default)")
    c.add_argument("--json", action="store_true", help="emit the full dataset")
    ap.add_argument("--json", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args(argv)

    view = fold(REPO)
    as_json = getattr(args, "json", False)
    if as_json:
        print(json.dumps(view, indent=2, sort_keys=True))
    else:
        print(census_lines(view))
    # read-only fold: a clean read is `done`, findings present is `report`.
    # In --json mode stdout stays pure dataset — the result goes to stderr.
    result = (f"result: {'report' if view['gaps'] else 'done'} — "
              f"{view['totals']['tests']} tests folded, "
              f"{len(view['gaps'])} finding(s)")
    print(result, file=sys.stderr if as_json else sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
