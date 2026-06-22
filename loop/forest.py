#!/usr/bin/env python3
"""The whole-tree viewport forest fold (done-line 0186): the loop sensing the
whole forest of in-flight work, not just the landed trunk.

bdo, 2026-06-22: *"I want my viewport to be the whole tree, not just a viewport
into only the working now trunk ... a decorated/tagged/flagged instance of the
work, in repo, managed automatically, so I can see the sessions that are
happening and their files/environments. I don't want MY viewport to be a blocker
anymore."* Today the viewport is the primary checkout pinned to origin/main, so
it shows only LANDED work; the whole forest — worktrees, branches, parked atoms,
open PRs — is invisible from it, and the physical checkout is load-bearing. This
fold folds the forest into ONE decorated read so the checkout becomes one leaf.

Sibling of `census`/`digest`/`gaps` on the *forest* axis, in their exact grain:
a pure read-only fold, stdlib, deterministic, `--json`, ending in a clear
`done | report | needs-you` line (D-6). It composes — it does not rebuild (§10):

  - the git forest is sensed the same way `git.py garden`/`garden_verdict` sense
    it (the git pen, beside this comment's cite): `git worktree list --porcelain`
    → worktrees + their branches, `gh pr list --state all --json
    headRefName,state` → PR states, per-worktree `git status --porcelain` →
    uncommitted, plus loose branches with no worktree. git.py is a skill pen, not
    importable, so re-sensing via subprocess like garden does is correct and is
    NOT a second truth (the same sources, one reader more);
  - each atom's pipeline state is `loop.reconcile.Fold` + `orchestrate.next_action`
    (the same reader the digest uses), and "did atom X reach main?" is the
    digest's `atoms_on_main` (the D-13 per-atom↔per-PR join) — never re-derived.

The decoration is a closed status vocabulary (`STATUSES`), and the §10 teeth live
in the two pure classifiers: a *stranded* worktree (uncommitted work) can never be
flagged `merged` even when its branch landed (the garden merged-but-dirty bite —
the work wins), and a *parked* atom can never read `merged`/landed.
`tests/test_forest.py` proves a constant/fabricated classifier is caught.

Read-only (I-3): it senses and names; it never prunes, commits, or judges. The
surface (`FOREST.md`) is generated output, never hand-kept — `--write` regenerates
it; default renders to stdout and writes nothing.

CLI:
  python -m loop.forest            render FOREST.md to stdout (read-only-safe)
  python -m loop.forest --json     the raw dataset (machine-readable)
  python -m loop.forest --write    (re)generate FOREST.md at the repo root
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from loop.reconcile import (DEFAULT_ROOT, Fold, canon, load_atoms, load_epics,
                            now_ts, real_nodes)
from loop.orchestrate import next_action
from loop.digest import atoms_on_main

# loop/forest.py -> loop/ -> repo root. Works the same in a worktree.
REPO = Path(__file__).resolve().parent.parent
TRUNK = ("main", "master")

# The closed status vocabulary a work-item can wear (decision: closed in code for
# v0; the proposal asks whether it should be admitted). Ordered worst-pressure
# first so the surface and the counts lead with what needs a human.
STATUSES = ("parked-atom", "stranded", "live-worktree", "in-review", "merged")

STATUS_GLOSS = {
    "parked-atom": "a gate refused this atom — it holds; amend or retire it",
    "stranded": "committed/uncommitted work with no open PR — mortal-session "
                "debris; PR it (the merge-node lands) or clean it up",
    "live-worktree": "an active bench — a worktree carrying uncommitted work",
    "in-review": "up for an independent look — an open PR, or an atom awaiting "
                 "its judging node",
    "merged": "landed on main — a clean worktree whose branch merged, or an atom "
              "a merge receipt confirms reached main (D-13)",
}


# ------------------------------------------------------------- pure classifiers
# The teeth live here, as pure functions over already-sensed inputs — so the test
# suite hits them directly without driving git (the garden_verdict pattern).

def git_node_status(uncommitted, has_open_pr, has_merged_pr, has_worktree):
    """The status of one git-forest node (a worktree or a loose branch), pure.

    Mirrors `git.py garden_verdict`'s safety ordering with richer labels:

      live-worktree  an open PR AND a worktree still carrying uncommitted work —
                     an active bench mid-task.
      in-review      an open PR (work submitted for an independent look).
      stranded       uncommitted work with no open PR, OR committed work no PR
                     ever covered — the mortal-session debris.
      merged         a clean tree whose branch has a merged PR (no open one).

    The §10 bite (the garden merged-but-dirty case): uncommitted work is checked
    BEFORE `has_merged_pr`, so a branch that landed yet still holds unsaved work
    reads `stranded`, never `merged` — the work wins over the tidiness, and a
    classifier that smoothed it to `merged` is caught by the test."""
    if has_open_pr:
        return "live-worktree" if (has_worktree and uncommitted) else "in-review"
    if uncommitted:
        return "stranded"          # the bite: unsaved work is never `merged`
    if has_merged_pr:
        return "merged"
    return "stranded"              # committed but no PR — stranded debris


def atom_node_status(action, on_main):
    """The status of one atom node, pure. `action` is `orchestrate.next_action`'s
    return (None=settled/terminal, ("await", node), ("parked", _), or an
    in-flight ("seed"|"derive"|"judge", _)); `on_main` is whether a merge receipt
    confirms it reached main (the digest's D-13 join).

    The §10 bite: a *parked* atom can never read `merged`/landed — `parked-atom`
    is decided before any landed reading, so a gate's honest refusal is never
    smoothed into 'it landed'. A constant 'merged' classifier is caught."""
    if action is not None and action[0] == "parked":
        return "parked-atom"       # the bite: a refused atom is never `merged`
    if on_main or action is None:
        return "merged"            # confirmed on main, or terminal+desired reached
    if action[0] == "await":
        return "in-review"         # awaiting its independent judging node
    return "in-review"            # otherwise moving through the gates — in flight


# ------------------------------------------------------------------- sensing
# The outward reach (subprocess to git/gh) lives only here, never in the pure
# functions above — exactly as garden keeps `cmd_garden` apart from
# `garden_verdict`. Every sensor fails soft: a forest read must never crash the
# fold (the same fail-open the census/digest folds hold).

def _git(args, cwd, timeout=20):
    try:
        return subprocess.run(["git"] + args, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", cwd=cwd,
                              timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return None


def sense_worktrees(repo):
    """[(path, branch_or_None, is_primary)] from `git worktree list --porcelain`
    — the primary (the viewport) is the first entry git names. Empty on any
    sensor failure (absence is information, never a crash)."""
    proc = _git(["worktree", "list", "--porcelain"], repo)
    if proc is None or proc.returncode != 0:
        return []
    out, path = [], None
    for line in proc.stdout.splitlines():
        if line.startswith("worktree "):
            path = line.split(" ", 1)[1].strip()
        elif line.startswith("branch "):
            branch = line.split(" ", 1)[1].strip().replace("refs/heads/", "", 1)
            out.append((path, branch, len(out) == 0))
            path = None
        elif line.startswith("detached"):
            out.append((path, None, len(out) == 0))
            path = None
    return out


def sense_pr_states(repo, timeout=20):
    """{branch: set(PR states)} from `gh pr list --state all` — exactly garden's
    fold. (None, {}) when gh is unreachable, so the surface can say so honestly
    rather than guessing a branch merged (garden never prunes blind, nor do we
    flag `merged` blind)."""
    try:
        gh = subprocess.run(
            ["gh", "pr", "list", "--state", "all", "--limit", "300",
             "--json", "headRefName,state"],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", cwd=repo, timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return None, {}
    if gh.returncode != 0:
        return None, {}
    states = {}
    try:
        for pr in json.loads(gh.stdout or "[]"):
            states.setdefault(pr["headRefName"], set()).add(pr["state"])
    except (ValueError, KeyError):
        return None, {}
    return True, states


def sense_uncommitted(path):
    """The count of changed paths in one worktree (`git status --porcelain`),
    like garden. 0 on any sensor failure."""
    proc = _git(["status", "--porcelain"], path)
    if proc is None or proc.returncode != 0:
        return 0
    return len([ln for ln in proc.stdout.splitlines() if ln.strip()])


def sense_loose_branches(repo, worktree_branches):
    """Local branches with no worktree of their own — the lighter cleanup chore
    garden's loose-branch fold names. [] on any sensor failure."""
    proc = _git(["branch", "--format=%(refname:short)"], repo)
    if proc is None or proc.returncode != 0:
        return []
    return [b for b in proc.stdout.split()
            if b not in TRUNK and b not in worktree_branches]


# ------------------------------------------------------------- the forest fold

def _pr_flags(branch, pr_states):
    states = pr_states.get(branch, set()) if branch else set()
    has_open = "OPEN" in states
    return has_open, ("MERGED" in states and not has_open), sorted(states)


def build_forest(worktrees, loose_branches, pr_states, atom_rows, gh_ok):
    """The pure composition: already-sensed inputs → the decorated forest model.

    `worktrees` is [(path, branch, is_primary, uncommitted)]; `loose_branches`
    is [branch]; `pr_states` is {branch: set(states)}; `atom_rows` is
    [(atom_id, hash, state, action, on_main)]; `gh_ok` records whether the PR
    sense succeeded (so the surface never claims `merged` on a blind read). Pure
    and total — the §10 teeth are the two classifiers it calls."""
    wt_nodes = []
    for path, branch, is_primary, uncommitted in worktrees:
        has_open, has_merged, states = _pr_flags(branch, pr_states)
        if is_primary:
            status = "merged"      # the viewport tracks the trunk — the leaf, by definition
        else:
            status = git_node_status(uncommitted, has_open, has_merged, True)
        wt_nodes.append({
            "kind": "worktree",
            "path": path,
            "slug": Path(path).name,
            "branch": branch,
            "is_primary": is_primary,
            "uncommitted": uncommitted,
            "pr_states": states,
            "status": status,
        })

    branch_nodes = []
    for branch in loose_branches:
        has_open, has_merged, states = _pr_flags(branch, pr_states)
        branch_nodes.append({
            "kind": "branch",
            "branch": branch,
            "pr_states": states,
            # a loose branch has no tree of its own to be dirty
            "status": git_node_status(0, has_open, has_merged, False),
        })

    atom_nodes = []
    for atom_id, ahash, state, action, on_main in atom_rows:
        atom_nodes.append({
            "kind": "atom",
            "atom": atom_id,
            "artifact_hash": ahash,
            "state": state,
            "on_main": on_main,
            "status": atom_node_status(action, on_main),
        })

    all_nodes = wt_nodes + branch_nodes + atom_nodes
    counts = {s: sum(1 for n in all_nodes if n["status"] == s) for s in STATUSES}
    viewport = next((n for n in wt_nodes if n["is_primary"]), None)
    return {
        "generated_by": "loop/forest.py",
        "generated_at": now_ts(),
        "gh_ok": gh_ok,
        "viewport": ({"path": viewport["path"], "branch": viewport["branch"]}
                     if viewport else None),
        "worktrees": wt_nodes,
        "branches": branch_nodes,
        "atoms": atom_nodes,
        "counts": counts,
        "totals": {"worktrees": len(wt_nodes), "branches": len(branch_nodes),
                   "atoms": len(atom_nodes)},
    }


def forest(repo=REPO, root=None):
    """Sense the whole forest and fold it into the decorated model. `repo` is the
    git root (for the git/gh sensing); `root` is the `.ai-native` records root
    (defaults to `repo/.ai-native`) for the atom fold."""
    root = root or (repo / DEFAULT_ROOT.name)
    sensed_wts = sense_worktrees(repo)
    wt_branches = {b for _, b, _ in sensed_wts if b}
    worktrees = [(p, b, primary, sense_uncommitted(p))
                 for p, b, primary in sensed_wts]
    gh_ok, pr_states = sense_pr_states(repo)
    loose = sense_loose_branches(repo, wt_branches)

    fold = Fold(root)
    real_map = real_nodes(fold)
    epics = load_epics(root)
    on_main = atoms_on_main(fold)
    atom_rows = []
    for atom, ahash in load_atoms(root):
        from loop.reconcile import atom_state
        action = next_action(fold, atom, ahash, real_map, epics=epics)
        atom_rows.append((atom["id"], ahash, atom_state(fold, ahash), action,
                          atom["id"] in on_main))
    return build_forest(worktrees, loose, pr_states, atom_rows, gh_ok)


# ------------------------------------------------------------------- rendering

MARK = {"parked-atom": "⛔", "stranded": "⚠", "live-worktree": "🔨",
        "in-review": "👁", "merged": "✓"}


def render(d):
    """The dataset as a decorated, scannable read. Generated output — the file
    carries a do-not-hand-edit note (`render_file`); never hand-kept."""
    lines = [f"# The work forest — {d['totals']['worktrees']} worktree(s), "
             f"{d['totals']['branches']} loose branch(es), "
             f"{d['totals']['atoms']} atom(s)", ""]
    vp = d.get("viewport")
    if vp:
        lines.append(f"Viewport (the primary checkout): `{vp['path']}` on "
                     f"`{vp['branch']}` — one leaf, not the lens.")
    if not d.get("gh_ok"):
        lines.append("_gh was unreachable this run — PR states are unknown, so "
                     "no node is flagged `merged` on a blind read._")
    lines.append("")

    lines.append("## At a glance")
    for s in STATUSES:
        n = d["counts"].get(s, 0)
        if n:
            lines.append(f"- {MARK.get(s, '·')} **{s}** ({n}) — {STATUS_GLOSS[s]}")
    lines.append("")

    lines.append(f"## Worktrees ({d['totals']['worktrees']})")
    for w in d["worktrees"]:
        tag = " · _viewport_" if w["is_primary"] else ""
        prs = (" · PR " + "/".join(w["pr_states"])) if w["pr_states"] else ""
        unc = (f" · {w['uncommitted']} uncommitted" if w["uncommitted"] else "")
        branch = w["branch"] or "(detached)"
        lines.append(f"- {MARK.get(w['status'], '·')} `{w['slug']}` — "
                     f"`{branch}` — **{w['status']}**{unc}{prs}{tag}")
    lines.append("")

    if d["branches"]:
        lines.append(f"## Loose branches ({d['totals']['branches']}) — no worktree")
        for b in d["branches"]:
            prs = (" · PR " + "/".join(b["pr_states"])) if b["pr_states"] else ""
            lines.append(f"- {MARK.get(b['status'], '·')} `{b['branch']}` — "
                         f"**{b['status']}**{prs}")
        lines.append("")

    lines.append(f"## Atoms ({d['totals']['atoms']})")
    # lead with the work that needs a human — parked, then everything not merged
    shown = [a for a in d["atoms"] if a["status"] != "merged"]
    shown.sort(key=lambda a: STATUSES.index(a["status"]))
    for a in shown:
        lines.append(f"- {MARK.get(a['status'], '·')} `{a['atom']}` — "
                     f"**{a['status']}** (pipeline: {a['state']})")
    merged_atoms = d["counts"].get("merged", 0) - sum(
        1 for w in d["worktrees"] if w["status"] == "merged") - sum(
        1 for b in d["branches"] if b["status"] == "merged")
    if merged_atoms > 0:
        lines.append(f"- ✓ _…+{merged_atoms} atom(s) merged / landed on main, "
                     "folded into the count above_")
    lines.append("")
    return "\n".join(lines)


FILE_HEADER = ("<!-- Generated by loop/forest.py — do NOT hand-edit. "
               "Regenerate with `python -m loop.forest --write`. -->\n\n")


def render_file(d):
    return FILE_HEADER + render(d) + "\n"


def open_count(d):
    """Everything the forest leaves open for a human: parked atoms and stranded
    git nodes — the work that is no one's bench and no gate's to settle. The end
    line may never claim cleaner than the dataset above it."""
    return d["counts"].get("parked-atom", 0) + d["counts"].get("stranded", 0)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", type=Path, default=REPO,
                    help="git root to fold the forest of (default: this one)")
    ap.add_argument("--root", type=Path, default=None,
                    help="the .ai-native records root (default: <repo>/.ai-native)")
    ap.add_argument("--json", action="store_true",
                    help="emit the raw dataset (machine-readable), not the prose")
    ap.add_argument("--write", action="store_true",
                    help="(re)generate FOREST.md at the repo root")
    args = ap.parse_args(argv)

    d = forest(args.repo, args.root)
    if args.json:
        print(canon(d))
    elif args.write:
        target = args.repo / "FOREST.md"
        target.write_text(render_file(d), encoding="utf-8")
        print(f"result: report — regenerated {target} "
              f"({sum(d['totals'].values())} node(s))")
        return 0
    else:
        print(render(d))

    opens = open_count(d)
    if not args.write:
        if opens:
            print(f"result: report — {d['counts'].get('parked-atom', 0)} parked "
                  f"atom(s), {d['counts'].get('stranded', 0)} stranded git "
                  "node(s) in the forest; the cut stays yours (D-4)")
        else:
            print("result: done — the forest is tidy: nothing parked, nothing "
                  "stranded")
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
