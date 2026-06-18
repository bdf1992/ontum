#!/usr/bin/env python3
"""loop/phrasing.py — the phrasing backdoor's pure checker (done-line 0117).

bdo, 2026-06-18: fixing a few pedantic English phrases ("on his phone" ->
"wherever he is") should not cost a branch, an atom, a value-gate summons and a
spawned judge — the full work-particle mantra (§15/D-5) for a change the machine
never reads as logic. He named the fix: a backdoor route for quick edits to
"semantic and pedantic phrases, not syntax or schema", packaged the same way as
whiteout (done-line 0064) — a session-usable move with COMPUTABLE TEETH that
refuses the instant the change leaves its low-impact bounds and names the
escalation.

This module is the PURE half (loop/'s hard rule: stdlib only, no git, no
network). It decides, given the before/after bytes of one file, whether the
edit is PHRASING-ONLY: human-readable prose the machine cannot branch on. The
reach that has git — `pr.py` — gathers the before/after and the route verb, and
RE-RUNS this exact check server-side in the off-log gate, so the prose door
cannot be lied to (a code or schema change can never slip through it).

The teeth, per file kind:

  .md / .txt   body prose is free; but a change to the YAML frontmatter KEY SET,
               or to the `name`/`version` values, is NOT phrasing (those are a
               skill's identity/contract, read as config).
  .py          tokenized: every non-comment, non-string token must be
               byte-identical. Only COMMENT text and STRING/docstring contents
               may differ. A code token, or a token added/removed, refuses.
  .json        parsed: identical structure (keys, nesting, types) and identical
               non-string values; only string values under a prose-field
               allowlist (PROSE_KEYS) may differ. A renamed key, a changed
               number/bool/null, or a changed id/verdict string refuses.

Any other file kind is not covered by v0 and refuses (route it through the atom
pipeline). The refusal always NAMES what disqualified it.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import tokenize

# JSON leaf keys whose string values are human prose (editable through the
# door). Everything else — ids, verdicts, nodes, file paths (e.g. `reading`),
# atom references — must be byte-identical. Widening this list is a named later
# increment, never a silent growth (done-line 0117 scope).
PROSE_KEYS = frozenset({
    "horizon", "value", "arc", "context", "glue", "story", "text",
    "description", "headline", "why_now", "if_accepted", "if_rejected",
    "cost_of_wrong_call", "mechanism",
})

_PROSE_EXTS = ("md", "txt", "markdown")


def _as_text(data):
    """Normalise bytes|str -> str (utf-8). The check works on text; the reach
    may hand either."""
    if isinstance(data, bytes):
        return data.decode("utf-8")
    return data


def _ext(path):
    p = path.replace("\\", "/").rsplit("/", 1)[-1]
    return p.rsplit(".", 1)[-1].lower() if "." in p else ""


# ------------------------------------------------------------------ markdown
def _frontmatter(text):
    """The YAML frontmatter block (between the leading `---` fences) as a list
    of lines, or None when the file has none. v0 reads it line-shaped, not as a
    YAML parse (no dependency): enough to compare the key set and the protected
    `name`/`version` lines."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i]
    return None  # an unterminated fence is not frontmatter


def _fm_keys(fm_lines):
    keys = []
    for ln in fm_lines:
        stripped = ln.lstrip()
        if ln[:1] not in (" ", "\t") and ":" in stripped:  # a top-level key line
            keys.append(stripped.split(":", 1)[0].strip())
    return keys


def _fm_line(fm_lines, key):
    for ln in fm_lines:
        if ln.lstrip().startswith(key + ":") and ln[:1] not in (" ", "\t"):
            return ln
    return None


def _md_phrasing(before, after):
    fb, fa = _frontmatter(before), _frontmatter(after)
    if (fb is None) != (fa is None):
        return False, "the YAML frontmatter was added or removed — that is a structural (schema) change, not phrasing"
    if fb is not None:
        if _fm_keys(fb) != _fm_keys(fa):
            return False, "the frontmatter key set changed — a skill's config keys are schema, not phrasing"
        for k in ("name", "version"):
            if _fm_line(fb, k) != _fm_line(fa, k):
                return False, (f"the frontmatter '{k}' changed — a skill's "
                               f"{k} is its identity/contract, not phrasing")
    return True, None  # body prose (and non-name/version frontmatter values) free


# ------------------------------------------------------------------ python
def _py_tokens(text):
    """The token spine with comment/string CONTENT erased: each comment or
    string collapses to a bare marker of its type, every other token keeps its
    exact text. Two files with the same spine differ only in prose."""
    spine = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type in (tokenize.ENCODING, tokenize.NL, tokenize.NEWLINE):
                # newlines are structural but a docstring's internal line count
                # is prose; keep NEWLINE/NL so added/removed CODE lines refuse,
                # while a one-token string swap (same lines) passes.
                spine.append((tok.type, ""))
            elif tok.type in (tokenize.COMMENT, tokenize.STRING):
                spine.append((tok.type, "<prose>"))
            else:
                spine.append((tok.type, tok.string))
    except (tokenize.TokenError, IndentationError, SyntaxError) as e:
        return None, f"does not tokenize as Python ({e})"
    return spine, None


def _py_phrasing(before, after):
    sb, err = _py_tokens(before)
    if sb is None:
        return False, f"the before-version {err}"
    sa, err = _py_tokens(after)
    if sa is None:
        return False, f"the edited version {err}"
    if sb == sa:
        return True, None
    # name the first divergent code token
    for i, (b, a) in enumerate(zip(sb, sa)):
        if b != a:
            return False, (f"a non-comment/non-string token changed "
                           f"(token #{i}: {b!r} -> {a!r}) — that is code, not "
                           "phrasing")
    return False, ("the number of code tokens changed (lines of code added or "
                   "removed) — that is code, not phrasing")


# ------------------------------------------------------------------ json
def _json_walk(before, after, key, path):
    if type(before) is not type(after):
        return False, (f"{path}: the value type changed "
                       f"({type(before).__name__} -> {type(after).__name__}) — "
                       "structure is schema, not phrasing")
    if isinstance(before, dict):
        if set(before) != set(after):
            added = sorted(set(after) - set(before))
            removed = sorted(set(before) - set(after))
            return False, (f"{path}: JSON keys changed (added {added}, removed "
                           f"{removed}) — keys are schema, not phrasing")
        for k in before:
            ok, why = _json_walk(before[k], after[k], k, f"{path}.{k}")
            if not ok:
                return ok, why
        return True, None
    if isinstance(before, list):
        if len(before) != len(after):
            return False, (f"{path}: list length changed "
                           f"({len(before)} -> {len(after)}) — structure is "
                           "schema, not phrasing")
        for i, (b, a) in enumerate(zip(before, after)):
            ok, why = _json_walk(b, a, key, f"{path}[{i}]")  # items inherit key
            if not ok:
                return ok, why
        return True, None
    # leaf
    if before == after:
        return True, None
    if isinstance(before, str) and isinstance(after, str) and key in PROSE_KEYS:
        return True, None
    return False, (f"{path}: a non-prose value changed (key '{key}' is not a "
                   "prose field) — only the listed prose strings may change")


def _json_phrasing(before, after):
    try:
        bo = json.loads(before)
    except json.JSONDecodeError as e:
        return False, f"the before-version is not valid JSON ({e})"
    try:
        ao = json.loads(after)
    except json.JSONDecodeError as e:
        return False, f"the edited version is not valid JSON ({e})"
    return _json_walk(bo, ao, None, "$")


# ------------------------------------------------------------------ the door
def phrasing_only(path, before, after):
    """Is the edit to ``path`` phrasing-only? Returns (ok, reason). ``before``
    and ``after`` are the file's bytes|str before and after the edit. The
    reason is None on a pass and names the disqualifier on a refusal."""
    before, after = _as_text(before), _as_text(after)
    if before == after:
        return True, None  # a no-op is trivially phrasing
    ext = _ext(path)
    if ext in _PROSE_EXTS:
        return _md_phrasing(before, after)
    if ext == "py":
        return _py_phrasing(before, after)
    if ext == "json":
        return _json_phrasing(before, after)
    return False, (f"file kind '.{ext}' is not covered by the phrasing door "
                   "(v0 covers .md, .py, .json) — route it through the atom "
                   "pipeline")


def branch_phrasing_clean(changes):
    """Given ``changes`` — a list of {path, before, after} for every changed
    NON-LOG file on a branch — is the whole branch a phrasing-only edit?
    Returns (clean, reasons). Clean requires at least one changed file and
    every one of them phrasing-only; the first non-phrasing file disqualifies
    the branch (the off-log gate's second way to be backed). ``reasons`` names
    each refusal for the surface."""
    if not changes:
        return False, ["no non-log file changed — nothing to take through the "
                       "phrasing door"]
    reasons = []
    for ch in changes:
        ok, why = phrasing_only(ch["path"], ch.get("before", ""),
                                ch.get("after", ""))
        if not ok:
            reasons.append(f"{ch['path']}: {why}")
    return (not reasons), reasons


def main(argv=None):
    """`python -m loop.phrasing check --before A --after B --path P` — the
    read-only, standalone check (a test aid and a session's pre-flight). The
    git-bearing route lives in the PR pen (`pr.py phrasing`)."""
    ap = argparse.ArgumentParser(prog="loop.phrasing",
                                 description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    chk = sub.add_parser("check", help="check one before/after pair")
    chk.add_argument("--path", required=True)
    chk.add_argument("--before", required=True, help="path to the before-bytes")
    chk.add_argument("--after", required=True, help="path to the after-bytes")
    ns = ap.parse_args(argv if argv is not None else sys.argv[1:])
    before = open(ns.before, "rb").read()
    after = open(ns.after, "rb").read()
    ok, why = phrasing_only(ns.path, before, after)
    if ok:
        print(f"result: done — {ns.path} is a phrasing-only edit; it may take "
              "the backdoor (no atom needed)")
        return 0
    print(f"result: report — {ns.path} is NOT phrasing-only: {why}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
