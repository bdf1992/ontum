#!/usr/bin/env python3
"""The authoring bench's draft check (A2) — a deterministic gate over an
authored workflow file before it is shown or armed.

A workflow is config-as-code (§7): a malformed draft must be refused with a
named reason, not rendered as if it were sound. This checker is stdlib-only and
does no JS execution — it verifies the structural contract the wrapper convention
declares (`.claude/workflows/CLAUDE.md`):

  1. the file is a non-empty `.js` script;
  2. it begins with a `export const meta = { ... }` block;
  3. that block is a PURE LITERAL (no `${...}` interpolation, no call
     expressions) — the Workflow tool requires it;
  4. meta carries `name`, `description`, `phases`;
  5. `meta.name` equals the file's slug (the launch handle matches the file);
  6. the body uses at least one orchestration primitive
     (`agent(` / `phase(` / `parallel(` / `pipeline(`).

It also computes one REVIEW FLAG, not a failure: whether the workflow appears to
MUTATE (declares `isolation: 'worktree'` or asks an agent to write/edit/commit).
A3 (the review interface) consumes that flag to decide what needs a human's eye.

`lint(path)` returns a result dict; `--json` emits it; a non-clean check exits 1.
"""

import json
import pathlib
import re
import sys

PRIMITIVES = ("agent(", "phase(", "parallel(", "pipeline(")
# a workflow may invoke another by name: workflow('slug') / workflow("slug").
# The {scriptPath} object form and variable form carry no string arg, so they
# are not statically resolvable and are skipped (honest gap, not a false catch).
WORKFLOW_REF = re.compile(r"\bworkflow\(\s*['\"]([^'\"]+)['\"]")
MUTATION_HINTS = (
    "isolation: 'worktree'",
    'isolation: "worktree"',
    "isolation:'worktree'",
)
# words in an agent prompt that imply the run changes the tree
MUTATION_VERBS = re.compile(
    r"\b(write|edit|commit|push|delete|rm\b|mutat|apply the|create the file|overwrite)\w*",
    re.IGNORECASE,
)


def _meta_block(text):
    """Return the source of the meta object literal (the outer {...}), or None.
    Brace-matched from the first '{' after `export const meta =`."""
    m = re.search(r"export\s+const\s+meta\s*=\s*", text)
    if not m:
        return None
    i = text.find("{", m.end())
    if i == -1:
        return None
    depth, j = 0, i
    in_str, quote = False, ""
    while j < len(text):
        c = text[j]
        if in_str:
            if c == "\\":
                j += 2
                continue
            if c == quote:
                in_str = False
        elif c in "'\"`":
            in_str, quote = True, c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[i : j + 1]
        j += 1
    return None


def _strip_strings(block):
    """Replace the CONTENTS of every string literal with spaces (keeping the
    quotes and length), so structural checks don't trip on prose. Returns
    (stripped, had_template_interpolation) — the second is True iff a backtick
    string actually contains `${`, the only real interpolation."""
    out, had_interp = [], False
    i, n = 0, len(block)
    while i < n:
        c = block[i]
        if c in "'\"`":
            quote = c
            out.append(c)
            j = i + 1
            while j < n:
                d = block[j]
                if d == "\\":
                    out.append("  ")
                    j += 2
                    continue
                if d == quote:
                    out.append(quote)
                    j += 1
                    break
                if quote == "`" and d == "$" and j + 1 < n and block[j + 1] == "{":
                    had_interp = True
                out.append(" ")
                j += 1
            i = j
        else:
            out.append(c)
            i += 1
    return "".join(out), had_interp


def _starts_with_meta(text):
    """meta must be the first statement — only comments/whitespace before it."""
    stripped = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    stripped = re.sub(r"(?m)^\s*//.*$", "", stripped)
    return bool(re.match(r"\s*export\s+const\s+meta\s*=", stripped))


def lint(path):
    p = pathlib.Path(path)
    slug = p.stem
    problems, flags = [], {"mutates": False}
    result = {"path": str(p), "slug": slug, "ok": False,
              "problems": problems, "flags": flags, "meta": {}}

    if p.suffix != ".js":
        problems.append(f"not a .js workflow file (suffix {p.suffix!r})")
        return result
    if not p.exists():
        problems.append("file does not exist")
        return result
    text = p.read_text(encoding="utf-8")
    if not text.strip():
        problems.append("file is empty")
        return result

    block = _meta_block(text)
    if block is None:
        problems.append("no `export const meta = { ... }` block found")
        return result
    if not _starts_with_meta(text):
        problems.append("meta is not the first statement (the Workflow tool "
                        "requires the script to begin with `export const meta`)")

    # pure-literal: no interpolation, no call expressions inside meta. Check
    # the structure with string CONTENTS blanked, so prose can't trip it.
    structure, had_interp = _strip_strings(block)
    if had_interp:
        problems.append("meta contains `${...}` interpolation — it must be a "
                        "pure literal")
    if re.search(r"[A-Za-z_$][\w$]*\s*\(", structure):
        problems.append("meta contains a call expression — it must be a pure "
                        "literal (no function calls, variables, or spreads)")

    for key in ("name", "description", "phases"):
        if not re.search(rf"\b{key}\s*:", block):
            problems.append(f"meta is missing `{key}`")

    name_m = re.search(r"\bname\s*:\s*['\"]([^'\"]+)['\"]", block)
    meta_name = name_m.group(1) if name_m else None
    result["meta"]["name"] = meta_name
    if meta_name is None:
        problems.append("meta.name is not a string literal")
    elif meta_name != slug:
        problems.append(f"meta.name {meta_name!r} != file slug {slug!r} "
                        "(the launch handle must match the filename)")

    result["meta"]["phases"] = len(re.findall(r"\btitle\s*:", block))

    body = text[text.index(block) + len(block):]
    if not any(prim in body for prim in PRIMITIVES):
        problems.append("body uses no orchestration primitive "
                        "(agent/phase/parallel/pipeline) — nothing would run")

    # mutation is read from the BODY (worktree isolation + agent-prompt verbs),
    # never the meta prose — a description that says "no mutation" must not trip.
    if any(h in body for h in MUTATION_HINTS) or MUTATION_VERBS.search(body):
        flags["mutates"] = True

    result["ok"] = not problems
    return result


def fit(path, workflows_dir=None):
    """The §10 cross-file seam check: every `workflow('slug')` reference must
    resolve to a sibling workflow file that ITSELF passes the cell check. A
    locally-fine workflow that invokes a missing or malformed sibling is the
    misfit the per-file `lint` cannot see — two valid-alone files that refuse to
    fit. Read-only. Returns {ok, refs, dangling}."""
    p = pathlib.Path(path)
    d = pathlib.Path(workflows_dir) if workflows_dir else p.parent
    out = {"path": str(p), "slug": p.stem, "ok": True, "refs": [], "dangling": []}
    if not p.exists():
        out["ok"] = False
        out["dangling"].append("(file does not exist)")
        return out
    text = p.read_text(encoding="utf-8")
    block = _meta_block(text)
    body = text[text.index(block) + len(block):] if block else text
    refs = sorted({m.group(1) for m in WORKFLOW_REF.finditer(body)
                   if m.group(1) != p.stem})  # self-reference resolves to self
    out["refs"] = refs
    for ref in refs:
        sib = d / f"{ref}.js"
        if not sib.exists():
            out["dangling"].append(f"{ref} (no .claude/workflows/{ref}.js)")
        else:
            sub = lint(str(sib))
            if not sub["ok"]:
                out["dangling"].append(f"{ref} (malformed: {sub['problems'][0]})")
    out["ok"] = not out["dangling"]
    return out


def main(argv):
    as_json = "--json" in argv
    paths = [a for a in argv if not a.startswith("--")]
    if not paths:
        print("usage: lint.py <workflow.js> [--json]", file=sys.stderr)
        return 2
    rc = 0
    for path in paths:
        r = lint(path)
        f = fit(path)
        if as_json:
            print(json.dumps({**r, "fit": f}, ensure_ascii=False, indent=2))
        else:
            ok = r["ok"] and f["ok"]
            tag = "ok" if ok else "REFUSED"
            print(f"[{tag}] {r['slug']}"
                  + ("  (mutates — needs review)" if r["flags"]["mutates"] else ""))
            for prob in r["problems"]:
                print(f"  - {prob}")
            for ref in f["dangling"]:
                print(f"  - dangling workflow() reference: {ref}")
        if not (r["ok"] and f["ok"]):
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
