#!/usr/bin/env python3
"""tool-scout — read-only fold over what tools exist to answer a query.

Sources indexed, each a pure read of files/PATH already on disk:
  - path:     executables found on $PATH (name only; no subprocess per file)
  - skill:    this repo's .claude/skills/*/SKILL.md (name + description)
  - workflow: this repo's .claude/workflows/*.js (meta.name + meta.description)
  - loop:     `python -m loop.<x>` / `python loop/<x>.py` commands documented
              in loop/CLAUDE.md, with their inline comment as description

No network, no subprocess execution of discovered tools, no writes. This is
a search index over what's already named on disk/PATH — never a claim that
an unindexed source (installed GUI apps, other machines, unattached repos)
doesn't exist. Absence from the index is absence of evidence, not evidence
of absence.
"""
import argparse
import json
import os
import re
import sys

TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")


def tokenize(text):
    return set(t.lower() for t in TOKEN_RE.findall(text or ""))


def score(query_tokens, item):
    hay = tokenize(item["name"]) | tokenize(item.get("description", ""))
    overlap = query_tokens & hay
    s = len(overlap)
    name_l = item["name"].lower()
    for qt in query_tokens:
        if qt in name_l:
            s += 2
    return s


def index_path_tools():
    items = {}
    for d in os.environ.get("PATH", "").split(os.pathsep):
        if not d or not os.path.isdir(d):
            continue
        try:
            entries = os.listdir(d)
        except OSError:
            continue
        for name in entries:
            if name in items:
                continue  # first PATH hit wins, same precedence as the shell
            full = os.path.join(d, name)
            try:
                if os.path.isfile(full) and os.access(full, os.X_OK):
                    items[name] = {
                        "kind": "path",
                        "name": name,
                        "description": f"executable on PATH ({d})",
                        "source": full,
                    }
            except OSError:
                continue
    return list(items.values())


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def parse_skill_frontmatter(text):
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, None
    fm = m.group(1)
    name_m = re.search(r"^name:\s*(.+)$", fm, re.MULTILINE)
    name = name_m.group(1).strip() if name_m else None
    desc_m = re.search(
        r"^description:\s*(>-?|\|-?)?\s*\n?(.*?)(?=^\S[\w-]*:|\Z)",
        fm,
        re.MULTILINE | re.DOTALL,
    )
    desc = None
    if desc_m:
        raw = desc_m.group(2)
        lines = [ln.strip() for ln in raw.strip("\n").splitlines()]
        desc = " ".join(ln for ln in lines if ln)
        desc = desc.strip().strip('"')
    return name, desc


def index_repo_skills(root):
    items = []
    skills_dir = os.path.join(root, ".claude", "skills")
    if not os.path.isdir(skills_dir):
        return items
    for entry in sorted(os.listdir(skills_dir)):
        skill_md = os.path.join(skills_dir, entry, "SKILL.md")
        if not os.path.isfile(skill_md):
            continue
        try:
            with open(skill_md, "r", encoding="utf-8") as f:
                text = f.read()
        except OSError:
            continue
        name, desc = parse_skill_frontmatter(text)
        items.append(
            {
                "kind": "skill",
                "name": name or entry,
                "description": desc or "",
                "source": skill_md,
            }
        )
    return items


# A JS string literal's closing quote may be backslash-escaped inside the
# string (e.g. `'...bdo\'s, D-4)...'`); `[^'"]+` would stop there instead of
# finding the real close. Match `\.` (any escaped char) or any non-quote,
# non-backslash char, then unescape on capture.
_JS_STRING = r"(['\"])((?:\\.|(?!\1)[^\\])*)\1"
META_NAME_RE = re.compile(r"name:\s*" + _JS_STRING)
META_DESC_RE = re.compile(r"description:\s*" + _JS_STRING)


def _js_unescape(raw):
    return re.sub(r"\\(.)", r"\1", raw)


def index_repo_workflows(root):
    items = []
    wf_dir = os.path.join(root, ".claude", "workflows")
    if not os.path.isdir(wf_dir):
        return items
    for entry in sorted(os.listdir(wf_dir)):
        if not entry.endswith(".js"):
            continue
        full = os.path.join(wf_dir, entry)
        try:
            with open(full, "r", encoding="utf-8") as f:
                head = f.read(4000)
        except OSError:
            continue
        name_m = META_NAME_RE.search(head)
        desc_m = META_DESC_RE.search(head)
        items.append(
            {
                "kind": "workflow",
                "name": (_js_unescape(name_m.group(2)) if name_m else entry[:-3]),
                "description": _js_unescape(desc_m.group(2)) if desc_m else "",
                "source": full,
            }
        )
    return items


LOOP_CMD_RE = re.compile(
    r"^(python(?:3)? (?:-m )?(?:loop\.\S+|loop/\S+\.py)[^\n#]*?)(?:\s+#\s*(.*))?$",
    re.MULTILINE,
)


def index_loop_commands(root):
    items = []
    claude_md = os.path.join(root, "loop", "CLAUDE.md")
    if not os.path.isfile(claude_md):
        return items
    try:
        with open(claude_md, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return items
    fence_blocks = re.findall(r"```sh\n(.*?)```", text, re.DOTALL)
    seen = set()
    for block in fence_blocks:
        for m in LOOP_CMD_RE.finditer(block):
            cmd = m.group(1).strip()
            desc = (m.group(2) or "").strip()
            if cmd in seen:
                continue
            seen.add(cmd)
            items.append(
                {
                    "kind": "loop",
                    "name": cmd,
                    "description": desc,
                    "source": claude_md,
                }
            )
    return items


def build_index(repo_roots, kinds):
    items = []
    if "path" in kinds:
        items += index_path_tools()
    for root in repo_roots:
        if "skill" in kinds:
            items += index_repo_skills(root)
        if "workflow" in kinds:
            items += index_repo_workflows(root)
        if "loop" in kinds:
            items += index_loop_commands(root)
    return items


def search(query, items, top):
    qtokens = tokenize(query)
    if not qtokens:
        ranked = items
    else:
        scored = [(score(qtokens, it), it) for it in items]
        scored = [(s, it) for s, it in scored if s > 0]
        scored.sort(key=lambda p: (-p[0], p[1]["name"]))
        ranked = [it for _, it in scored]
    return ranked[:top]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("query", nargs="?", default="", help="search terms")
    ap.add_argument(
        "--repo",
        action="append",
        default=None,
        help="repo root to index (default: this repo root, cwd-relative)",
    )
    ap.add_argument(
        "--kind",
        action="append",
        choices=["path", "skill", "workflow", "loop"],
        default=None,
        help="restrict to one or more sources (default: all)",
    )
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    default_root = os.path.abspath(os.path.join(here, "..", "..", ".."))
    repo_roots = args.repo or [default_root]
    kinds = set(args.kind) if args.kind else {"path", "skill", "workflow", "loop"}

    items = build_index(repo_roots, kinds)
    results = search(args.query, items, args.top)

    if args.json:
        print(json.dumps({"query": args.query, "results": results}, indent=2))
        return

    if not results:
        print(f"no matches for {args.query!r} across {sorted(kinds)}")
        print("this indexes PATH executables + this repo's skills/workflows/loop")
        print("commands only — an unindexed source (GUI apps, other machines,")
        print("unattached repos) is absence of evidence, not evidence of absence.")
        return

    print(f"{len(results)} match(es) for {args.query!r}:\n")
    for it in results:
        desc = it.get("description") or "(no description on record)"
        print(f"[{it['kind']:8}] {it['name']}")
        print(f"           {desc}")
        print(f"           source: {it['source']}\n")


if __name__ == "__main__":
    main()
