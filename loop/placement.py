#!/usr/bin/env python3
"""The placement fold — a worker belongs in its own worktree, not the viewport.

Done-line 0160, the placement part of the session gateway
(`session-gateway.proposal.md` §11 increment #4; bdo's "gateway start, platform
level", 2026-06-20). The workstation fence just landed (#341/#346) FORBIDS a
worker writing or flipping the **viewport** (the shared trunk primary checkout,
bdo's reading surface) at the *tool* seam. This is its complement at the
*session* seam — the door beside the wall: it computes WHERE a worker belongs
(its own worktree) and detects when one is trespassing in the viewport, so the
prohibition never has to fire.

Platform-level by design: a pure fold in `loop/` (family-neutral), the decision a
Claude-Code SessionStart render and a Codex session-start both consume — the same
define-once / render-per-family split `fence/` uses. The provisioning ACTUATOR
(`git worktree add`) and the SessionStart render are later waves; this wave is the
pure decision only.

The shape mirrors `workspace.py` / `trust.py`: a focused fold over state plus a
pure refusal the hook/pen imports. It never drives git and never reaches the
network (loop's hard rules). The one git fact it needs — which checkout is the
viewport — is a *filesystem* read (the git common-dir), gathered for the CLI and
passed into the pure functions, which the suite hits directly.

The §10 bite: "this checkout is the trunk (the viewport)" and "I am a worker
serving claim W" are each locally fine and must not fit — a worker in the viewport
is trespassing, and the fold says so, naming the placement it should have instead.

Stdlib only. Every CLI invocation ends with a clear result: done | report | needs-you.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT  # noqa: F401  (kept for CLI root parity)
from loop import workspace  # noqa: F401  (the binding fold this composes with)

# The convention every render shares: a worker's worktree is ../ontum-wt/<slug>,
# a sibling of the repo (never inside it), so it is never the viewport and never
# nests under the trunk tree. The trunk branch the viewport rides.
WT_ROOT_DEFAULT = "../ontum-wt"
TRUNK = "main"


def branch_slug(branch):
    """The worktree slug for a branch: its last path segment.
    'claude/placement-gateway' -> 'placement-gateway'. Pure, deterministic."""
    if not branch:
        return ""
    return branch.rstrip("/").rsplit("/", 1)[-1]


def placement_path(branch, wt_root=WT_ROOT_DEFAULT):
    """The deterministic worktree a branch belongs in: `<wt_root>/<slug>`.

    The single source of truth for "where does this work live" — *derived*, so no
    binding needs to carry a path: `workspace.py`'s binding carries branch+claim,
    and the path follows from the branch. Returns a string, or None for no branch."""
    slug = branch_slug(branch)
    if not slug:
        return None
    return f"{wt_root.rstrip('/')}/{slug}"


def _norm(p):
    """Normalize a path for comparison: resolve, forward-slash, drop a trailing
    slash, case-fold (Windows drives/paths are case-insensitive). Pure — resolve
    touches the filesystem only to canonicalize and never raises out."""
    if p is None:
        return None
    try:
        s = str(Path(p).resolve())
    except (OSError, ValueError, RuntimeError):
        s = str(p)
    return s.replace("\\", "/").rstrip("/").lower()


def is_viewport(cwd, viewport_path):
    """Is `cwd` the viewport (the trunk primary checkout)? A pure path compare."""
    n = _norm(cwd)
    return n is not None and n == _norm(viewport_path)


def placement_refusal(cwd, branch, claim, viewport_path, wt_root=WT_ROOT_DEFAULT):
    """Why a worker serving `claim` may not do code-work from `cwd`, or None.

    The contract a SessionStart render (or a future commit guard) enforces:

      - a worker with a claim sitting IN THE VIEWPORT is **trespassing** — the
        §10 bite: "this is the trunk reading surface" and "I am a worker doing W"
        are each fine and must not fit — and is told the worktree it belongs in;
      - a worker whose cwd is NOT its branch's placement is in the wrong tree;
      - a worker in its correct worktree passes (None).

    No claim => no check (opt-in, like `binding_refusal`'s `--claim`): a reader,
    or the viewport's own owner session, is not a worker and is left alone."""
    if not claim:
        return None
    target = placement_path(branch, wt_root)
    if is_viewport(cwd, viewport_path):
        return (
            f"this is the viewport (the trunk checkout at {viewport_path}) — a "
            f"worker serving '{claim}' is placed in its OWN worktree, never the "
            f"shared reading surface (the fence forbids writing it; this is the "
            f"door beside that wall). Your placement is:\n"
            f"  {target}\n"
            f"  git worktree add -b {branch} {target} origin/{TRUNK}\n"
            f"(the provisioning actuator that runs this for you is a later wave of "
            f"the placement gateway)."
        )
    if target is not None and _norm(cwd) != _norm(target):
        return (
            f"this worktree ({cwd}) is not the placement for '{branch}' — its work "
            f"belongs in {target}. Either you are in the wrong tree, or the branch "
            f"was checked out somewhere ad hoc; place it where its slug says so a "
            f"later session can find the work by its branch (the binding's premise)."
        )
    return None


def placement_status(registry, viewport_path, wt_root=WT_ROOT_DEFAULT):
    """Fold the session registry into placement verdicts. `registry` is
    `{session_id: {"cwd": ..., ...}}` (the watcher's registry). Returns a list of
    `{session, cwd, verdict}`, sorted, where verdict is:

      - 'in-viewport' — a session working in the shared trunk checkout (the
                        trespass the fence forbids and this would have placed);
      - 'placed'      — cwd is a worktree under `wt_root` (its own tree);
      - 'elsewhere'   — cwd is neither the viewport nor a `wt_root` worktree.

    Read-only and pure; the surface a SessionStart render or the watcher consumes."""
    out = []
    nwt = _norm(wt_root)
    for sid, info in sorted((registry or {}).items()):
        cwd = (info or {}).get("cwd") if isinstance(info, dict) else None
        ncwd = _norm(cwd)
        if is_viewport(cwd, viewport_path):
            verdict = "in-viewport"
        elif ncwd is not None and nwt is not None and ncwd.startswith(nwt + "/"):
            verdict = "placed"
        else:
            verdict = "elsewhere"
        out.append({"session": sid, "cwd": cwd, "verdict": verdict})
    return out


def viewport_root(start=None):
    """The viewport: the trunk primary checkout (git's *main* worktree). Resolved
    by **filesystem**, never a subprocess (loop's hard rule): a primary checkout's
    `.git` is a directory; a worktree's `.git` is a file pointing at
    `<common>/.git/worktrees/<name>`, whose grandparent `<common>` is the viewport.
    Returns a path string, or None if it cannot be resolved (fail-open: the caller
    treats an unknown viewport as "cannot judge trespass", never as a false flag)."""
    start = Path(start or Path.cwd())
    gitpath = None
    for d in [start, *start.parents]:
        g = d / ".git"
        if g.exists():
            gitpath = g
            break
    if gitpath is None:
        return None
    if gitpath.is_dir():
        return str(gitpath.parent)  # primary checkout — its parent is the viewport
    try:
        txt = gitpath.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if txt.startswith("gitdir:"):
        wt_gitdir = Path(txt.split(":", 1)[1].strip())
        try:
            return str(wt_gitdir.parents[1].parent)
        except IndexError:
            return None
    return None


def cmd_status(ns):
    try:
        from loop import watcher
        registry = watcher.load_registry()
    except Exception:  # noqa: BLE001
        registry = {}
    vp = viewport_root()
    rows = placement_status(registry, vp, ns.wt_root)
    if vp is None:
        print("result: needs-you — could not resolve the viewport (the trunk "
              "checkout) from here; placement cannot judge trespass without it.")
        return 0
    if not rows:
        print(f"result: done — no sessions registered; viewport {vp}")
        return 0
    trespass = [r for r in rows if r["verdict"] == "in-viewport"]
    for r in rows:
        print(f"  {r['verdict']:<12} {r['session']}  ({r['cwd']})")
    if trespass:
        print(f"result: report — {len(trespass)} session(s) in the viewport "
              f"(trespassing the trunk reading surface); each belongs in its own "
              f"worktree (../ontum-wt/<slug>).")
    else:
        print(f"result: done — all {len(rows)} session(s) placed outside the viewport {vp}")
    return 0


def cmd_where(ns):
    target = placement_path(ns.branch, ns.wt_root)
    if target is None:
        print("result: needs-you — no branch given to place")
        return 0
    print(target)
    print(f"result: done — '{ns.branch}' is placed at {target}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="the placement fold (read-only)")
    ap.add_argument("--wt-root", default=WT_ROOT_DEFAULT,
                    help="the worktree root (default: ../ontum-wt)")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("status", help="the placement census over the session registry")
    w = sub.add_parser("where", help="the deterministic placement path for a branch")
    w.add_argument("--branch", required=True)
    ns = ap.parse_args(argv)
    if ns.cmd == "where":
        return cmd_where(ns)
    return cmd_status(ns)


if __name__ == "__main__":
    sys.exit(main())
