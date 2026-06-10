#!/usr/bin/env python3
"""The envoy pen — the one way a package leaves the repo (done-line 0015).

The envoy skill (SKILL.md beside this file) is the form; this pen is
its enforcement, the way pr.py is the one write path to a PR. A package
is at most ten flat files under exports/<name>/ — an arc with visuals,
code, tests, documentation, and history — for review by another model
family. Three build modes share one slot table (SLOTS):

    pen      deterministic, byte-stable, always rebuilt (never hand-edit)
    session  authored by the session in place of the scaffolded stub
    hybrid   authored prose around a marker-fenced deterministic block

Verbs:
    new      scaffold exports/<pkg>/.spec.json (core slots + flex slots)
    plan     resolve the spec, estimate tokens, say what would build
    build    materialize the package; never clobbers authored prose
    check    the gate — refusals, not warnings (see GATE RULES below)
    seal     gate, stamp the manifest, append the receipt to log.jsonl
    render   mermaid blocks to SVG beside the package, if a renderer exists
    list     packages on disk against the disclosure ledger

Stdlib only. Every invocation ends with a clear stdout result:
done | report | needs-you. A refusal is a `report`: it names what the
package is missing and the paved path to fix it.
"""

from __future__ import annotations

import argparse
import ast
import datetime
import hashlib
import importlib.util
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

PEN = "python .claude/skills/envoy/envoy.py"
MAX_FILES = 10
CHARS_PER_TOKEN = 4  # the cross-family rule of thumb; estimates, not counts
DEFAULT_TOTAL_TOKENS = 120_000   # fits every current frontier context window
DEFAULT_FILE_TOKENS = 40_000
SPEC_NAME = ".spec.json"
LOG_NAME = "log.jsonl"
RENDER_DIR = "rendered"
STUB_MARK = "<!-- envoy:stub"
BLOCK_BEGIN = "<!-- envoy:{name} -->"
BLOCK_END = "<!-- /envoy:{name} -->"
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SKIP_DIRS = {".git", "__pycache__", "exports", "node_modules", ".venv"}
TEXT_SUFFIXES = {".py", ".md", ".json", ".jsonl", ".html", ".txt", ".toml",
                 ".yml", ".yaml", ".gitignore", ".gitattributes", ".cfg"}
FENCE_LANG = {".py": "python", ".json": "json", ".jsonl": "json",
              ".html": "html", ".yml": "yaml", ".yaml": "yaml",
              ".toml": "toml", ".txt": "text"}


def repo_root():
    return pathlib.Path(
        os.environ.get("ONTUM_REPO_ROOT")
        or pathlib.Path(__file__).resolve().parents[3])


# ------------------------------------------------------------------ atoms

def est_tokens(text):
    """Estimate, clearly labeled as one everywhere it surfaces."""
    return max(1, round(len(text) / CHARS_PER_TOKEN))


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def bar(value, peak, width=24):
    if peak <= 0 or value <= 0:
        return ""
    return "█" * max(1, round(width * value / peak))


def write_lf(path, text):
    """LF bytes always — package bytes are identity (the receipt hashes them)."""
    if not text.endswith("\n"):
        text += "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.replace("\r\n", "\n").encode("utf-8"))


def append_line(path, obj):
    """Line-atomic append, torn tail healed first — the loop's append_line
    semantics (loop/reconcile.py), restated so the pen works against any
    root, including roots that carry no loop package."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a+b") as f:
        f.seek(0, os.SEEK_END)
        if f.tell() > 0:
            f.seek(-1, os.SEEK_END)
            if f.read(1) != b"\n":
                f.write(b"\n")
        f.write(json.dumps(obj, ensure_ascii=False).encode("utf-8") + b"\n")
        f.flush()
        os.fsync(f.fileno())


def read_jsonl(path):
    """Tolerant fold: an unparseable line never happened (torn-tail rule)."""
    entries = []
    if not path.exists():
        return entries
    for line in path.read_bytes().decode("utf-8", "replace").splitlines():
        try:
            entries.append(json.loads(line))
        except (json.JSONDecodeError, ValueError):
            continue
    return entries


def run_git(root, *args):
    """Stdout on success, None on any failure — every history section
    degrades to an honest 'no history readable here' instead of crashing."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
    except OSError:
        return None
    return proc.stdout if proc.returncode == 0 else None


def block(name, body):
    """A marker-fenced deterministic block (the knoll.py GLYPH_DATA pattern):
    the pen owns what is between the markers, the session owns the rest."""
    return (BLOCK_BEGIN.format(name=name) + "\n" + body.rstrip("\n")
            + "\n" + BLOCK_END.format(name=name))


def replace_block(text, name, body):
    begin = BLOCK_BEGIN.format(name=name)
    end = BLOCK_END.format(name=name)
    i, j = text.find(begin), text.find(end)
    if i < 0 or j < 0 or j < i:
        return None
    return text[:i] + block(name, body) + text[j + len(end):]


# ------------------------------------------------------------- repo walks

def iter_repo_files(root):
    """The committed surface, sorted — `git ls-files`, so gitignored noise
    (the watch log, packages) can never leak into a package or wobble the
    byte-determinism between builds. Falls back to a directory walk only
    where git is unreadable."""
    tracked = run_git(root, "ls-files", "-z")
    if tracked is not None:
        return sorted(p for p in (root / rel for rel in tracked.split("\0") if rel)
                      if p.is_file())
    out = []
    def walk(d):
        children = sorted(d.iterdir(), key=lambda p: (p.is_file(), p.name))
        for child in children:
            if child.name in SKIP_DIRS:
                continue
            if child.is_dir():
                walk(child)
            else:
                out.append(child)
    walk(root)
    return out


def line_count(path):
    if path.suffix not in TEXT_SUFFIXES and path.name not in TEXT_SUFFIXES:
        return None
    try:
        return len(path.read_bytes().decode("utf-8", "replace").splitlines())
    except OSError:
        return None


def resolve_sources(root, patterns):
    """Globs to sorted unique existing files, all inside the root —
    disclosure is explicit: a source that escapes the repo is refused
    upstream by validate_spec, not silently followed."""
    found = []
    for pattern in patterns:
        try:
            hits = sorted(root.glob(pattern))
        except (ValueError, NotImplementedError):
            hits = []  # glob refuses '..' and absolute patterns; fall through
        if not hits:
            candidate = root / pattern
            hits = [candidate] if candidate.is_file() else []
        found.extend(h for h in hits if h.is_file())
    unique, seen = [], set()
    for path in found:
        if path not in seen:
            seen.add(path)
            unique.append(path)
    return unique


# ------------------------------------------------------------ pen builders
# Every builder returns full markdown text and must be byte-deterministic
# for a given repo state + spec — the tests pin that property.

def build_repo_map(root, spec, slot):
    lines = [f"# {slot['title']}", "",
             "Deterministic, pen-built (`repo-map`). The shape of the repo: "
             "every committed file, its size in lines, and where the "
             "environments (`CLAUDE.md`) live.", ""]
    files = iter_repo_files(root)
    lines += ["## Tree", "", "```text"]
    last_parts = ()
    for path in files:
        rel = path.relative_to(root)
        parts = rel.parts[:-1]
        for depth in range(len(parts)):
            if parts[:depth + 1] != last_parts[:depth + 1]:
                lines.append("    " * depth + parts[depth] + "/")
        last_parts = parts
        count = line_count(path)
        suffix = f"  ({count} lines)" if count is not None else ""
        lines.append("    " * len(parts) + rel.parts[-1] + suffix)
    lines += ["```", ""]
    by_dir = {}
    for path in files:
        rel = path.relative_to(root)
        top = rel.parts[0] if len(rel.parts) > 1 else "(root)"
        count = line_count(path)
        if count is not None:
            by_dir[top] = by_dir.get(top, 0) + count
    if by_dir:
        peak = max(by_dir.values())
        lines += ["## Lines by area", ""]
        width = max(len(k) for k in by_dir)
        for top, count in sorted(by_dir.items(), key=lambda kv: -kv[1]):
            lines.append(f"    {top.ljust(width)}  {bar(count, peak)} {count}")
        lines.append("")
    envs = [p for p in files if p.name == "CLAUDE.md"]
    if envs:
        lines += ["## The environments (each directory's own contract)", ""]
        for path in envs:
            rel = path.relative_to(root).as_posix()
            text = path.read_bytes().decode("utf-8", "replace")
            paragraph = []
            for raw in text.splitlines():
                if raw.startswith("#"):
                    continue
                if not raw.strip():
                    if paragraph:
                        break
                    continue
                paragraph.append(raw.strip())
            lines += [f"- **`{rel}`** — " + " ".join(paragraph)]
        lines.append("")
    return "\n".join(lines)


def build_history(root, spec, slot):
    lines = [f"# {slot['title']}", "",
             "Deterministic, pen-built (`history`). The repo's own account "
             "of how it got here: the commit log, the merge stamps, the "
             "cadence, and the numbered records.", ""]
    log = run_git(root, "log", "--date=short",
                  "--pretty=format:%h%x09%ad%x09%an%x09%s")
    if log is None:
        lines += ["*(no git history readable here)*", ""]
    else:
        rows = log.splitlines()
        lines += [f"## Commits ({len(rows)}, newest first)", "", "```text"]
        shown = rows[:200]
        for row in shown:
            short, date, author, subject = (row.split("\t", 3) + [""] * 4)[:4]
            lines.append(f"{date}  {short}  {subject}  [{author}]")
        if len(rows) > len(shown):
            lines.append(f"... (+{len(rows) - len(shown)} earlier commits "
                         "elided — say so rather than truncate silently)")
        lines += ["```", ""]
        weeks = {}
        for row in rows:
            parts = row.split("\t")
            if len(parts) > 1:
                date = datetime.date.fromisoformat(parts[1])
                year, week, _ = date.isocalendar()
                weeks[f"{year}-W{week:02d}"] = weeks.get(f"{year}-W{week:02d}", 0) + 1
        if weeks:
            peak = max(weeks.values())
            lines += ["## Cadence (commits per ISO week)", ""]
            for week, count in sorted(weeks.items()):
                lines.append(f"    {week}  {bar(count, peak)} {count}")
            lines.append("")
        merges = run_git(root, "log", "--merges", "--date=short",
                         "--pretty=format:%ad%x09%s")
        if merges:
            lines += ["## Merges to the trunk (the owner's stamps)", ""]
            for row in merges.splitlines():
                date, subject = (row.split("\t", 1) + [""])[:2]
                lines.append(f"- {date} — {subject}")
            lines.append("")
    for label, rel in (("Done-lines (scope, written before the work)",
                        ".ai-native/done"),
                       ("Session reports", ".ai-native/reports")):
        directory = root / rel
        if directory.is_dir():
            entries = sorted(p for p in directory.iterdir()
                             if p.is_file() and not p.name.startswith("."))
            if entries:
                lines += [f"## {label}", ""]
                for path in entries:
                    head = path.read_bytes().decode("utf-8", "replace")
                    title = next((l.lstrip("# ").strip()
                                  for l in head.splitlines()
                                  if l.startswith("#")), path.stem)
                    lines.append(f"- `{path.name}` — {title}")
                lines.append("")
    return "\n".join(lines)


def _load_module(path, name):
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception:
        return None  # the section degrades to honesty, never to a crash


def _mermaid_id(text):
    return re.sub(r"[^A-Za-z0-9]", "_", text)


def build_architecture(root, spec, slot):
    lines = [f"# {slot['title']}", "",
             "Deterministic, pen-built (`architecture`). Diagrams are "
             "Mermaid source — render them or read them as text; both "
             "work.", ""]
    reconcile_path = root / "loop" / "reconcile.py"
    module = (_load_module(reconcile_path, "envoy_reconcile")
              if reconcile_path.exists() else None)
    pipeline = getattr(module, "PIPELINE", None) if module else None
    if pipeline:
        lines += ["## The pipeline (from `loop/reconcile.py`, the single "
                  "stage table)", "", "```mermaid", "flowchart LR"]
        for stage in pipeline:
            src = _mermaid_id(stage["event"])
            dst = _mermaid_id(stage["next_event"])
            lines.append(f'    {src}["{stage["event"]}"] '
                         f'-->|{stage["node"]}| {dst}["{stage["next_event"]}"]')
        lines += ["```", "",
                  "| seam | node | verdicts the seam accepts |",
                  "|---|---|---|"]
        for stage in pipeline:
            verdicts = ", ".join(stage.get("terminal_expected", []))
            lines.append(f'| {stage["seam"]} | `{stage["node"]}` '
                         f'| {verdicts} |')
        lines.append("")
    elif reconcile_path.exists():
        lines += ["*(`loop/reconcile.py` exists but would not import — "
                  "pipeline diagram unavailable, which is itself a "
                  "finding)*", ""]
    sources = []
    for rel in ("loop", "glyphs", ".claude/hooks"):
        directory = root / rel
        if directory.is_dir():
            sources += sorted(directory.glob("*.py"))
    sources += sorted((root / ".claude" / "skills").glob("*/*.py"))
    modules, edges, docs = [], set(), {}
    for path in sources:
        rel = path.relative_to(root).as_posix()
        modules.append(rel)
        try:
            tree = ast.parse(path.read_bytes().decode("utf-8", "replace"))
        except SyntaxError:
            continue
        doc = ast.get_docstring(tree)
        docs[rel] = doc.splitlines()[0] if doc else ""
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                top = name.split(".")[0]
                if top in ("loop", "glyphs"):
                    target = name.replace(".", "/") + ".py"
                    if (root / target).exists() and target != rel:
                        edges.add((rel, target))
    if modules:
        lines += ["## Module imports (derived from the AST, not the prose)",
                  "", "```mermaid", "flowchart TD"]
        by_dir = {}
        for rel in modules:
            by_dir.setdefault(rel.rsplit("/", 1)[0], []).append(rel)
        for directory, members in sorted(by_dir.items()):
            lines.append(f'    subgraph {_mermaid_id(directory)}["{directory}/"]')
            for rel in members:
                stem = rel.rsplit("/", 1)[-1].removesuffix(".py")
                lines.append(f'        {_mermaid_id(rel)}["{stem}"]')
            lines.append("    end")
        for src, dst in sorted(edges):
            lines.append(f"    {_mermaid_id(src)} --> {_mermaid_id(dst)}")
        lines += ["```", "", "## Modules", "",
                  "| module | first line of its own docstring |", "|---|---|"]
        for rel in modules:
            lines.append(f"| `{rel}` | {docs.get(rel, '')} |")
        lines.append("")
    return "\n".join(lines)


def build_code(root, spec, slot):
    fence_note = ("Deterministic, pen-built (`doc`). Source documents "
                  "embedded verbatim."
                  if slot["kind"] == "doc" else
                  "Deterministic, pen-built (`code`). Sources embedded "
                  "verbatim — what you are reading is the code, not a "
                  "description of it.")
    lines = [f"# {slot['title']}", "", fence_note, ""]
    for path in resolve_sources(root, slot.get("sources", [])):
        rel = path.relative_to(root).as_posix()
        text = path.read_bytes().decode("utf-8", "replace")
        count = len(text.splitlines())
        lines += [f"## `{rel}` ({count} lines)", ""]
        if path.suffix == ".md":
            lines += ["`````markdown", text.rstrip("\n"), "`````", ""]
        else:
            lang = FENCE_LANG.get(path.suffix, "")
            lines += [f"```{lang}", text.rstrip("\n"), "```", ""]
    return "\n".join(lines)


def build_data(root, spec, slot):
    lines = [f"# {slot['title']}", "",
             "Deterministic, pen-built (`data`). A fold over the append-only "
             "logs: counts and shapes, no interpretation.", ""]
    log_dir = root / ".ai-native" / "log"
    if log_dir.is_dir():
        for path in sorted(log_dir.glob("*.jsonl")):
            entries = read_jsonl(path)
            raw = len(path.read_bytes().decode("utf-8", "replace").splitlines())
            lines += [f"## `{path.name}` — {len(entries)} parseable line(s)"
                      + (f", {raw - len(entries)} torn/dropped" if raw > len(entries) else ""),
                      ""]
            for field in ("type", "kind", "verdict", "node", "status"):
                counts = {}
                for entry in entries:
                    if field in entry:
                        counts[str(entry[field])] = counts.get(str(entry[field]), 0) + 1
                if counts:
                    lines.append(f"by `{field}`:")
                    lines += [f"    {value}: {count}"
                              for value, count in sorted(counts.items())]
                    lines.append("")
    atoms = root / ".ai-native" / "atoms"
    if atoms.is_dir():
        files = sorted(p for p in atoms.iterdir() if p.is_file())
        lines += [f"## Atoms ({len(files)})", ""]
        for path in files:
            digest = sha256_bytes(path.read_bytes())[:12]
            lines.append(f"- `{path.name}` — sha256 `{digest}…`")
        lines.append("")
    return "\n".join(lines)


def build_metrics(root, spec, slot):
    lines = [f"# {slot['title']}", "",
             "Deterministic, pen-built (`metrics`). Numbers a reviewer can "
             "anchor on; every one is recomputed from the working tree at "
             "build time.", ""]
    files = iter_repo_files(root)
    py = [p for p in files if p.suffix == ".py"]
    md = [p for p in files if p.suffix == ".md"]
    tests = [p for p in files if p.parts[-2:-1] == ("tests",)
             and p.name.startswith("test_")]
    test_count = 0
    for path in tests:
        test_count += len(re.findall(r"^\s*def test_", path.read_bytes()
                                     .decode("utf-8", "replace"), re.M))
    commits = run_git(root, "rev-list", "--count", "HEAD")
    authors = run_git(root, "log", "--pretty=format:%an")
    rows = [("files (committed surface)", len(files)),
            ("python modules", len(py)),
            ("markdown documents", len(md)),
            ("test methods", test_count),
            ("commits", int(commits.strip()) if commits else 0)]
    width = max(len(label) for label, _ in rows)
    peak = max(value for _, value in rows) or 1
    lines += [f"    {label.ljust(width)}  {bar(value, peak)} {value}"
              for label, value in rows]
    lines.append("")
    if authors:
        counts = {}
        for name in authors.splitlines():
            counts[name] = counts.get(name, 0) + 1
        lines += ["## Commits by author", ""]
        peak = max(counts.values())
        width = max(len(name) for name in counts)
        for name, count in sorted(counts.items(), key=lambda kv: -kv[1]):
            lines.append(f"    {name.ljust(width)}  {bar(count, peak)} {count}")
        lines.append("")
    return "\n".join(lines)


def build_timeline(root):
    """The arc's deterministic appendix: records and merges, dated from
    the commit that first added each, interleaved oldest-first."""
    added = {}
    log = run_git(root, "log", "--reverse", "--date=short", "--name-status",
                  "--pretty=format:@%ad")
    if log is not None:
        current = None
        for raw in log.splitlines():
            if raw.startswith("@"):
                current = raw[1:]
            elif raw.startswith("A\t") and current:
                added.setdefault(raw.split("\t", 1)[1], current)
    events = []
    for rel, label in ((".ai-native/done", "done-line"),
                       (".ai-native/reports", "report")):
        directory = root / rel
        if directory.is_dir():
            for path in sorted(directory.iterdir()):
                if path.is_file() and not path.name.startswith("."):
                    head = path.read_bytes().decode("utf-8", "replace")
                    title = next((l.lstrip("# ").strip()
                                  for l in head.splitlines()
                                  if l.startswith("#")), path.stem)
                    date = added.get(f"{rel}/{path.name}", "unrecorded")
                    events.append((date, label, title))
    merges = run_git(root, "log", "--merges", "--reverse", "--date=short",
                     "--pretty=format:%ad%x09%s")
    if merges:
        for raw in merges.splitlines():
            date, subject = (raw.split("\t", 1) + [""])[:2]
            events.append((date, "merge", subject))
    events.sort(key=lambda e: (e[0], e[1]))
    lines = ["| date | what | record |", "|---|---|---|"]
    lines += [f"| {date} | {label} | {title} |" for date, label, title in events]
    return "\n".join(lines)


# ----------------------------------------------------------- session slots

def stub_text(spec, slot):
    questions = "".join(f"\n  - {q}" for q in spec.get("questions", [])) or " (none stated)"
    head = [f"# {slot['title']}", "",
            STUB_MARK + f" {slot['kind']}",
            "This slot is authored by the session, not the pen. Replace this",
            "entire comment block with the authored content; `check` refuses",
            "to seal while it remains.",
            f"- audience: {spec.get('audience', '(unstated)')}",
            f"- framing: {spec.get('framing', '(unstated)')}",
            f"- questions the package must answer:{questions}",
            f"- guidance: {SLOTS[slot['kind']]['guidance']}",
            "-->", ""]
    body = []
    if slot["kind"] == "briefing":
        body = ["", "## Manifest", "",
                block("manifest", "(stamped at seal)"), ""]
    if slot["kind"] == "arc":
        body = ["", "## Appendix — the timeline, deterministic",
                "", block("timeline", "(filled at build)"), ""]
    return "\n".join(head + body)


SLOTS = {
    # mode: pen | session | hybrid. Core slots are scaffolded by `new`;
    # only the briefing is *required* by the gate — the rest of the core
    # is a default, not a cage (bdo chose core + flex, 2026-06-10).
    "briefing": {
        "mode": "session", "core": True,
        "guidance": ("Address the reviewer directly: what this package is, "
                     "what the repo is, the perspective they are asked to "
                     "take, the questions to answer, and the shape of "
                     "feedback wanted back. Assume zero shared context; "
                     "define every repo-local term you use. Keep the "
                     "manifest block — seal stamps it.")},
    "arc": {
        "mode": "hybrid", "core": True,
        "guidance": ("Tell the story, not the inventory: what was being "
                     "built, what went wrong, what was learned, where it "
                     "stands. Name turning points. The deterministic "
                     "timeline below the markers is your evidence — the "
                     "narrative should make a reader want to check it.")},
    "architecture": {"mode": "pen", "core": True, "builder": build_architecture,
                     "guidance": ""},
    "repo-map": {"mode": "pen", "core": True, "builder": build_repo_map,
                 "guidance": ""},
    "history": {"mode": "pen", "core": True, "builder": build_history,
                "guidance": ""},
    "code": {"mode": "pen", "needs_sources": True, "builder": build_code,
             "guidance": ""},
    "doc": {"mode": "pen", "needs_sources": True, "builder": build_code,
            "guidance": ""},
    "data": {"mode": "pen", "builder": build_data, "guidance": ""},
    "metrics": {"mode": "pen", "builder": build_metrics, "guidance": ""},
    "synthesis": {
        "mode": "session",
        "guidance": ("A document that exists nowhere in the repo: an "
                     "explanation, comparison, or distillation composed for "
                     "this reviewer. Say in the first paragraph that it is "
                     "synthesized, and from what.")},
    "excerpt": {
        "mode": "session",
        "guidance": ("Curated quotations with commentary. Every quote "
                     "carries its `path:line` provenance; commentary says "
                     "why the reviewer is being shown it.")},
    "tensions": {
        "mode": "session",
        "guidance": ("The honest seams: open questions, known compromises, "
                     "places the authors disagree with themselves. A "
                     "reviewer pointed at real tensions returns real "
                     "judgment instead of compliments.")},
}
CORE_ORDER = ["briefing", "arc", "architecture", "repo-map", "history"]


# ------------------------------------------------------------------- spec

def expected_files(spec):
    return [(i, f"{i:02d}-{slot['slug']}.md", slot)
            for i, slot in enumerate(spec.get("slots", []))]


def validate_spec(spec, root):
    """Problems (refusals) and warnings (named, not blocking) — pure over
    the spec plus source existence."""
    problems, warnings = [], []
    if not (spec.get("title") or "").strip():
        problems.append("the spec needs a title — one line saying what this "
                        "package is for")
    slots = spec.get("slots", [])
    if not slots:
        problems.append("the spec names no slots — nothing would build")
    if len(slots) > MAX_FILES:
        problems.append(f"{len(slots)} slots > {MAX_FILES} — ten flat files "
                        "is the contract, not a suggestion; cut or merge")
    seen = set()
    for i, slot in enumerate(slots):
        kind, slug = slot.get("kind", ""), slot.get("slug", "")
        if not SLUG.match(slug or ""):
            problems.append(f"slot {i}: slug {slug!r} doesn't fit [a-z0-9-] "
                            "— the filename is an address, keep it boring")
        if slug in seen:
            problems.append(f"slot {i}: duplicate slug '{slug}'")
        seen.add(slug)
        if not (slot.get("title") or "").strip():
            problems.append(f"slot {i} ({slug}): a title is required")
        if kind not in SLOTS:
            problems.append(f"slot {i}: unknown kind '{kind}' — known: "
                            + ", ".join(sorted(SLOTS)))
            continue
        if SLOTS[kind].get("needs_sources"):
            sources = slot.get("sources", [])
            if not sources:
                problems.append(f"slot {i} ({slug}): kind '{kind}' needs "
                                "sources — disclosure is explicit, name the "
                                "files")
            else:
                for pattern in sources:
                    hits = resolve_sources(root, [pattern])
                    if not hits:
                        problems.append(f"slot {i} ({slug}): source "
                                        f"'{pattern}' matches nothing")
                    for hit in hits:
                        try:
                            hit.resolve().relative_to(root.resolve())
                        except ValueError:
                            problems.append(
                                f"slot {i} ({slug}): source '{pattern}' "
                                "escapes the repo — only repo files leave "
                                "the repo")
    if slots and slots[0].get("kind") != "briefing":
        problems.append("the first slot must be a briefing — a package "
                        "without one is unreviewable")
    budget = spec.get("budget", {})
    for key in ("total_tokens", "per_file_tokens"):
        value = budget.get(key)
        if value is not None and (not isinstance(value, int) or value <= 0):
            problems.append(f"budget.{key} must be a positive integer")
    for kind in CORE_ORDER:
        if not any(s.get("kind") == kind for s in slots):
            warnings.append(f"no '{kind}' slot — core by default; fine to "
                            "drop, but drop it on purpose")
    for key in ("audience", "framing"):
        if not (spec.get(key) or "").strip():
            warnings.append(f"no {key} stated — the briefing stub will say "
                            "'(unstated)' to the reviewer")
    if not spec.get("questions"):
        warnings.append("no questions stated — a reviewer aimed at nothing "
                        "returns generalities")
    return problems, warnings


def load_spec(root, package):
    pkg_dir = root / "exports" / package
    spec_path = pkg_dir / SPEC_NAME
    if not spec_path.exists():
        return None, pkg_dir
    return json.loads(spec_path.read_bytes().decode("utf-8")), pkg_dir


def budgets(spec):
    budget = spec.get("budget", {})
    return (budget.get("total_tokens", DEFAULT_TOTAL_TOKENS),
            budget.get("per_file_tokens", DEFAULT_FILE_TOKENS))


# ------------------------------------------------------------------- gate

def gate(root, spec, pkg_dir):
    """The check: every reason this package may not be sealed. Refusals,
    not warnings — §10: a locally-fine eleventh file must not fit."""
    problems, _ = validate_spec(spec, root)
    expected = expected_files(spec)
    names = {name for _, name, _ in expected}
    payload = sorted(p for p in pkg_dir.iterdir()
                     if p.is_file() and not p.name.startswith("."))
    for path in sorted(p for p in pkg_dir.iterdir() if p.is_dir()):
        if path.name != RENDER_DIR:
            problems.append(f"unexpected directory '{path.name}/' — a "
                            "package is flat files; only "
                            f"'{RENDER_DIR}/' (render output) may exist")
    if len(payload) > MAX_FILES:
        problems.append(f"{len(payload)} files > {MAX_FILES} — the contract "
                        "is at most ten flat files")
    for path in payload:
        if path.name not in names:
            problems.append(f"stray file '{path.name}' — the spec never "
                            "named it, and a stray file in a disclosure "
                            "package is exactly what this gate is for")
    total_tokens, file_tokens = budgets(spec)
    total = 0
    rows = []
    for _, name, slot in expected:
        path = pkg_dir / name
        if not path.exists():
            problems.append(f"missing '{name}' ({slot['kind']}) — run: "
                            f"{PEN} build {pkg_dir.name}")
            continue
        text = path.read_bytes().decode("utf-8", "replace")
        if not text.strip():
            problems.append(f"'{name}' is empty — an empty file tells the "
                            "reviewer nothing and spends a slot")
        if STUB_MARK in text:
            problems.append(f"'{name}' is still a stub — author it (the "
                            "stub names the framing and the questions), "
                            "then re-check")
        if slot["kind"] == "briefing":
            for marker in (BLOCK_BEGIN, BLOCK_END):
                if marker.format(name="manifest") not in text:
                    problems.append(f"'{name}' lost its manifest markers — "
                                    "seal stamps the manifest between "
                                    "them; restore the block")
                    break
        tokens = est_tokens(text)
        total += tokens
        rows.append((name, slot["kind"], tokens))
        if tokens > file_tokens:
            problems.append(f"'{name}' ≈{tokens} tokens > per-file budget "
                            f"{file_tokens} — split it or cut it")
    if total > total_tokens:
        problems.append(f"package ≈{total} tokens > total budget "
                        f"{total_tokens} — a reviewer who can't load it "
                        "can't review it")
    return problems, rows, total


# ------------------------------------------------------------------ verbs

def cmd_new(ns):
    root = repo_root()
    pkg_dir = root / "exports" / ns.package
    if not SLUG.match(ns.package):
        print(f"result: needs-you — package name {ns.package!r} doesn't fit "
              "[a-z0-9-]; the directory name is an address, keep it boring")
        return 2
    if pkg_dir.exists():
        print(f"result: report — refused: exports/{ns.package} already "
              f"exists; edit its {SPEC_NAME} (or pick a new name) instead "
              "of re-scaffolding over it")
        return 1
    slots = []
    if not ns.no_core:
        slots = [{"kind": kind, "slug": kind,
                  "title": {"briefing": "Briefing — read this first",
                            "arc": "The arc",
                            "architecture": "Architecture",
                            "repo-map": "The repo, mapped",
                            "history": "History"}[kind]}
                 for kind in CORE_ORDER]
    else:
        slots = [{"kind": "briefing", "slug": "briefing",
                  "title": "Briefing — read this first"}]
    for raw in ns.slots:
        head, _, src = raw.partition("=")
        kind, _, slug = head.partition(":")
        slot = {"kind": kind, "slug": slug or kind,
                "title": (slug or kind).replace("-", " ").capitalize()}
        if src:
            slot["sources"] = src.split(",")
        slots.append(slot)
    spec = {"package": ns.package,
            "title": ns.title,
            "audience": ns.audience,
            "framing": ns.framing,
            "questions": ns.questions,
            "feedback_shape": ns.feedback_shape,
            "by": ns.by,
            "budget": {"total_tokens": DEFAULT_TOTAL_TOKENS,
                       "per_file_tokens": DEFAULT_FILE_TOKENS},
            "slots": slots}
    problems, warnings = validate_spec(spec, root)
    pkg_dir.mkdir(parents=True)
    write_lf(pkg_dir / SPEC_NAME, json.dumps(spec, indent=2, ensure_ascii=False))
    for warning in warnings:
        print(f"warning: {warning}")
    if problems:
        print("the scaffolded spec does not hold yet:")
        for problem in problems:
            print(f"  - {problem}")
    print(f"result: report — exports/{ns.package}/{SPEC_NAME} scaffolded "
          f"({len(slots)} slot(s)); shape it, then: {PEN} plan {ns.package}")
    return 0


def cmd_plan(ns):
    root = repo_root()
    spec, pkg_dir = load_spec(root, ns.package)
    if spec is None:
        print(f"result: needs-you — exports/{ns.package}/{SPEC_NAME} not "
              f"found; scaffold it: {PEN} new {ns.package} --title \"...\"")
        return 2
    problems, warnings = validate_spec(spec, root)
    for warning in warnings:
        print(f"warning: {warning}")
    if problems:
        print("the spec does not hold:")
        for problem in problems:
            print(f"  - {problem}")
        print(f"result: report — {len(problems)} problem(s); fix the spec, "
              "then re-plan")
        return 1
    total_tokens, file_tokens = budgets(spec)
    total = 0
    print(f"{'file':34} {'kind':14} {'mode':8} {'est tokens':>10}")
    for _, name, slot in expected_files(spec):
        mode = SLOTS[slot["kind"]]["mode"]
        if mode == "pen":
            text = SLOTS[slot["kind"]]["builder"](root, spec, slot)
            tokens = est_tokens(text)
            total += tokens
            shown = str(tokens)
        else:
            shown = "(authored)"
        print(f"{name:34} {slot['kind']:14} {mode:8} {shown:>10}")
    print(f"\npen-built total ≈{total} tokens; budget {total_tokens} total / "
          f"{file_tokens} per file (authored slots land on top)")
    print(f"result: report — the plan holds; build it: {PEN} build {ns.package}")
    return 0


def cmd_build(ns):
    root = repo_root()
    spec, pkg_dir = load_spec(root, ns.package)
    if spec is None:
        print(f"result: needs-you — exports/{ns.package}/{SPEC_NAME} not "
              f"found; scaffold it: {PEN} new {ns.package} --title \"...\"")
        return 2
    problems, _ = validate_spec(spec, root)
    if problems:
        print("the spec does not hold:")
        for problem in problems:
            print(f"  - {problem}")
        print("result: report — fix the spec, then re-build")
        return 1
    for _, name, slot in expected_files(spec):
        path = pkg_dir / name
        mode = SLOTS[slot["kind"]]["mode"]
        if mode == "pen":
            write_lf(path, SLOTS[slot["kind"]]["builder"](root, spec, slot))
            print(f"built    {name}  (pen, deterministic)")
        elif not path.exists():
            write_lf(path, stub_text(spec, slot))
            print(f"stubbed  {name}  (yours to author)")
        elif STUB_MARK in path.read_bytes().decode("utf-8", "replace"):
            write_lf(path, stub_text(spec, slot))
            print(f"restubbed {name}  (was still a stub)")
        else:
            print(f"kept     {name}  (authored — the pen never clobbers prose)")
        if slot["kind"] == "arc" and path.exists():
            text = path.read_bytes().decode("utf-8", "replace")
            refreshed = replace_block(text, "timeline", build_timeline(root))
            if refreshed is None:
                print(f"note: {name} has no timeline markers — appendix not "
                      "refreshed (restore the envoy:timeline block to get "
                      "the deterministic appendix back)")
            elif refreshed != text:
                write_lf(path, refreshed)
                print(f"refreshed {name} timeline (between the markers only)")
    print(f"result: report — built; author the stubs, then: {PEN} check "
          f"{ns.package}")
    return 0


def cmd_check(ns):
    root = repo_root()
    spec, pkg_dir = load_spec(root, ns.package)
    if spec is None or not pkg_dir.is_dir():
        print(f"result: needs-you — exports/{ns.package} is not a package "
              f"(no {SPEC_NAME}); scaffold it: {PEN} new {ns.package}")
        return 2
    problems, rows, total = gate(root, spec, pkg_dir)
    for name, kind, tokens in rows:
        print(f"{name:34} {kind:14} ≈{tokens:>7} tokens")
    print(f"{'':34} {'total':14} ≈{total:>7} tokens")
    if problems:
        print("\nthe package does not hold:")
        for problem in problems:
            print(f"  - {problem}")
        print(f"result: report — {len(problems)} refusal(s); the gate seals "
              "nothing until they clear")
        return 1
    print(f"result: done — the gate holds; seal it: {PEN} seal {ns.package} "
          f"--by <who>")
    return 0


def cmd_seal(ns):
    root = repo_root()
    spec, pkg_dir = load_spec(root, ns.package)
    if spec is None:
        print(f"result: needs-you — exports/{ns.package}/{SPEC_NAME} not "
              "found; nothing to seal")
        return 2
    # stamp the manifest first: the receipt hashes what the reviewer reads
    expected = expected_files(spec)
    briefing = next((pkg_dir / name for _, name, slot in expected
                     if slot["kind"] == "briefing"), None)
    if briefing and briefing.exists():
        rows = ["| file | kind | est tokens |", "|---|---|---|"]
        for _, name, slot in expected:
            path = pkg_dir / name
            if path == briefing:
                rows.append(f"| `{name}` | {slot['kind']} | (this file) |")
            elif path.exists():
                text = path.read_bytes().decode("utf-8", "replace")
                rows.append(f"| `{name}` | {slot['kind']} | "
                            f"≈{est_tokens(text)} |")
        old = briefing.read_bytes().decode("utf-8", "replace")
        stamped = replace_block(old, "manifest", "\n".join(rows))
        if stamped is not None and stamped != old:
            write_lf(briefing, stamped)
            print("stamped the manifest into the briefing")
    problems, rows, total = gate(root, spec, pkg_dir)
    if problems:
        print("the package does not hold:")
        for problem in problems:
            print(f"  - {problem}")
        print("result: report — refused: clear the gate, then re-seal")
        return 1
    files = []
    for _, name, slot in expected:
        data = (pkg_dir / name).read_bytes()
        files.append({"name": name, "kind": slot["kind"],
                      "sha256": sha256_bytes(data),
                      "tokens": est_tokens(data.decode("utf-8", "replace"))})
    package_hash = sha256_bytes(
        "\n".join(f"{f['name']}:{f['sha256']}" for f in files).encode("utf-8"))
    ledger = root / "exports" / LOG_NAME
    for entry in reversed(read_jsonl(ledger)):
        if entry.get("package") == ns.package:
            if entry.get("package_hash") == package_hash:
                print(f"result: done — already sealed at this exact content "
                      f"({entry.get('ts', 'no ts')}); re-sealing unchanged "
                      "bytes is a no-op")
                return 0
            break
    receipt = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "package": ns.package,
        "title": spec.get("title", ""),
        "audience": spec.get("audience", ""),
        "framing": spec.get("framing", ""),
        "by": ns.by,
        "files": files,
        "total_tokens": total,
        "package_hash": package_hash,
        "spec_sha256": sha256_bytes(
            (pkg_dir / SPEC_NAME).read_bytes()),
    }
    append_line(ledger, receipt)
    print(f"sealed: {len(files)} file(s), ≈{total} tokens, package_hash "
          f"{package_hash[:12]}…")
    print(f"result: done — receipt on the ledger (exports/{LOG_NAME}); the "
          f"package is exports/{ns.package}/ — what you send is what was "
          "sealed")
    return 0


def cmd_render(ns):
    root = repo_root()
    spec, pkg_dir = load_spec(root, ns.package)
    if spec is None or not pkg_dir.is_dir():
        print(f"result: needs-you — exports/{ns.package} is not a package")
        return 2
    out_dir = pkg_dir / RENDER_DIR
    blocks = []
    for path in sorted(pkg_dir.glob("*.md")):
        text = path.read_bytes().decode("utf-8", "replace")
        for i, match in enumerate(
                re.finditer(r"```mermaid\n(.*?)```", text, re.S)):
            blocks.append((f"{path.stem}-{i}", match.group(1)))
    if not blocks:
        print("result: report — no mermaid blocks in this package; nothing "
              "to render")
        return 0
    out_dir.mkdir(exist_ok=True)
    for name, source in blocks:
        write_lf(out_dir / f"{name}.mmd", source)
    renderer = shutil.which("mmdc") or shutil.which("mmdc.cmd")
    if renderer is None:
        print(f"result: report — {len(blocks)} mermaid block(s) extracted to "
              f"exports/{ns.package}/{RENDER_DIR}/*.mmd, but no renderer "
              "found (mmdc — npm i -g @mermaid-js/mermaid-cli); the "
              "text-native package stands on its own, render is an extra")
        return 0
    rendered = 0
    for name, _ in blocks:
        proc = subprocess.run(
            [renderer, "-i", str(out_dir / f"{name}.mmd"),
             "-o", str(out_dir / f"{name}.svg")],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        if proc.returncode == 0:
            rendered += 1
        else:
            print(f"render failed for {name}: "
                  f"{(proc.stderr or proc.stdout).strip().splitlines()[-1]}")
    print(f"result: done — {rendered}/{len(blocks)} block(s) rendered to "
          f"exports/{ns.package}/{RENDER_DIR}/ (outside the sealed ten)")
    return 0


def cmd_list(ns):
    root = repo_root()
    exports = root / "exports"
    ledger = {entry.get("package"): entry
              for entry in read_jsonl(exports / LOG_NAME)}
    packages = sorted(p for p in exports.iterdir()
                      if p.is_dir() and p.name != RENDER_DIR) \
        if exports.is_dir() else []
    if not packages and not ledger:
        print("result: report — no packages, no receipts; start with: "
              f"{PEN} new <name> --title \"...\"")
        return 0
    for pkg_dir in packages:
        entry = ledger.pop(pkg_dir.name, None)
        count = len([p for p in pkg_dir.iterdir()
                     if p.is_file() and not p.name.startswith(".")])
        if entry is None:
            print(f"{pkg_dir.name}: {count} file(s), unsealed")
            continue
        files = []
        spec, _ = load_spec(root, pkg_dir.name)
        if spec:
            for _, name, _slot in expected_files(spec):
                path = pkg_dir / name
                if path.exists():
                    files.append({"name": name,
                                  "sha256": sha256_bytes(path.read_bytes())})
        current = sha256_bytes("\n".join(
            f"{f['name']}:{f['sha256']}" for f in files).encode("utf-8"))
        state = ("sealed" if current == entry.get("package_hash")
                 else "DRIFTED since seal — re-seal before sending")
        print(f"{pkg_dir.name}: {count} file(s), {state} "
              f"({entry.get('ts', 'no ts')})")
    for name, entry in sorted(ledger.items()):
        print(f"{name}: receipt on the ledger but no package on disk "
              f"(sealed {entry.get('ts', 'no ts')}; artifacts are "
              "rebuildable, the receipt is the record)")
    print("result: report — the ledger and the disk, reconciled above")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="envoy.py", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    verbs = parser.add_subparsers(dest="verb", required=True)

    new = verbs.add_parser("new", help="scaffold a package spec")
    new.add_argument("package")
    new.add_argument("--title", required=True,
                     help="one line: what this package is for")
    new.add_argument("--audience", default="",
                     help="who reviews it (model family, perspective)")
    new.add_argument("--framing", default="",
                     help="the lens the reviewer is asked to take")
    new.add_argument("--question", action="append", default=[],
                     dest="questions", help="a question the package must "
                     "answer; repeatable")
    new.add_argument("--feedback-shape", dest="feedback_shape", default="",
                     help="the shape of feedback wanted back")
    new.add_argument("--by", default="claude")
    new.add_argument("--slot", action="append", default=[], dest="slots",
                     metavar="KIND[:SLUG][=SRC,SRC]",
                     help="a flex slot, e.g. code:loop-core=loop/*.py")
    new.add_argument("--no-core", action="store_true", dest="no_core",
                     help="scaffold only the briefing, no other core slots")
    new.set_defaults(func=cmd_new)

    for name, fn, helptext in (
            ("plan", cmd_plan, "resolve the spec and estimate tokens"),
            ("build", cmd_build, "materialize the package files"),
            ("check", cmd_check, "the gate: every reason not to seal"),
            ("render", cmd_render, "mermaid blocks to SVG, if a renderer exists")):
        sub = verbs.add_parser(name, help=helptext)
        sub.add_argument("package")
        sub.set_defaults(func=fn)

    seal = verbs.add_parser("seal", help="gate, stamp the manifest, append "
                            "the receipt")
    seal.add_argument("package")
    seal.add_argument("--by", required=True,
                      help="who seals — receipts are signed (I-8)")
    seal.set_defaults(func=cmd_seal)

    lst = verbs.add_parser("list", help="packages on disk vs the ledger")
    lst.set_defaults(func=cmd_list)

    ns = parser.parse_args(argv)
    return ns.func(ns)


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
