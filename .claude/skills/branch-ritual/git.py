#!/usr/bin/env python3
"""The git pen — the one way a session stages or commits in this repo.

Done-line 0020. The git wrapper, mirroring the gh wrapper (pr.py beside
this file): raw mutating git is denied by the command_guard PreToolUse
hook and routed here, the way raw `gh pr` mutations are routed to the PR
pen. First cut is the two highest-risk verbs in the shared-tree fleet —
`add` and `commit` — where a single `git add .` would sweep in another
session's uncommitted work (the parallel-fleet hazard). Read-only git
(`status` / `log` / `diff`) stays raw-and-watched, exactly as `gh pr
list` does; this pen does not stand between a session and looking.

The spine bdo admitted (three refusals the pen owns, not passthrough):

  explicit-path  no sweep — `add .` / `-A` / `-u`, `commit -a` are
                 refused; name the paths or the commit names them.
  real message   a commit carries a step-shaped message (-m), never an
                 editor that hangs, never empty.
  never the trunk a session commits on its claude/* branch; main is
                 bdo's stamp (firm — the same line pr.py holds for push).

A fourth refusal joined the spine later (done-line 0053):

  record-id      a NEW .ai-native/done|reports file whose 4-digit id
                 already names a different file on any ref (local heads,
                 origin/*) is refused at commit — the id fold is
                 fleet-wide, not local (the 0020 incident); the same file
                 propagated unchanged stays allowed, and the check fails
                 open when refs cannot be listed.

Everything else git add / git commit take is forwarded for parity — a
branded tool that loses features invites the workaround it exists to
prevent (the lesson pr.py push records, changelog 0.4.0).

Done-line 0031 adds `sync`, the merge's return leg: the primary
worktree is bdo's viewport on the trunk, and merges land on origin —
nothing ever carried them back, so the viewport drifted stale (4
commits the day it was asked; 38 the day the workbenches were cut).
`sync` fetches and fast-forwards the viewport to origin/main. A viewport
stranded off the trunk is the *session's* to restore — `sync` checks the
branch work out and returns the viewport to main whenever that work is
safe (clean tree, all commits on origin), because supporting bdo is the
job, not handing him the cleanup (2026-06-11: rules now expect support,
not offload). It surfaces only to preserve work a restore would lose
(uncommitted changes, unpushed commits, or local commits sitting on main)
— and then it names the session's own fix (commit, push, branch), never
asks bdo to do it. ff-only cannot conflict: it succeeds or it surfaces.
In hook mode (`--hook`, wired to SessionStart) it is fail-open and exits
0 always — it never gates a session's start.

Stdlib only. Every invocation ends with a clear stdout result:
done | report | needs-you. A refusal is a `report` — it tells the
session what the act is missing; nothing here escalates to bdo.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
PEN = "python .claude/skills/branch-ritual/git.py"
TRUNK = ("main", "master")
END_STATES = ("done", "report", "needs-you")


def _tags():
    """The shared tag pool (loop/tags.py, done-line 0032), or None if loop
    isn't importable — intent tagging is additive; the pen runs untagged
    without it (the same fail-soft the watcher uses for the classifier)."""
    try:
        sys.path.insert(0, str(ROOT))
        from loop import tags
        return tags
    except Exception:  # noqa: BLE001 — additive feature, never breaks the pen
        return None


def intent_refusal(verb_intent, declared, in_pool):
    """Why a declared `--intent` may not stand, or None.

    Intent is *derivable* from the verb, so a declaration is a check, not
    a proposal — anything but the truth is refused, never silently
    swallowed (the §10 bite: a tag the tool can't trust is worse than no
    tag). A *known* value contradicting the verb is a lie; an *unknown*
    value is surfaced with the admit path (proposed-tier: a new word is
    proposed through the pool, not smuggled in on a git flag)."""
    if not declared or declared == verb_intent:
        return None
    if in_pool:
        return (f"--intent {declared} lies about this verb — it is a "
                f"{verb_intent}; drop the flag or declare {verb_intent}")
    return (f"--intent {declared} is not a known intent value (the pool is "
            f"read/mutate plus what's admitted); propose it first — "
            f"`python -m loop.tags admit --dimension intent --value {declared} "
            f"--by bdo` — or drop the flag")


def _intent_precheck(ns, verb):
    """Refuse a lying --intent and return (tags_module, verb_intent). The
    branded act is noted by the caller after the verb succeeds."""
    tags = _tags()
    if tags is None:
        return None, None
    verb_intent = tags.verb_intent("git", verb) or "mutate"
    declared = getattr(ns, "intent", None)
    if declared:
        fold = tags.Fold(ROOT / ".ai-native")
        in_pool = tags.status_of(fold, "intent", declared) in ("core", "admitted")
        reason = intent_refusal(verb_intent, declared, in_pool)
        if reason:
            _refuse(reason)
    return tags, verb_intent

# Tokens that stage more than the session named — the shared-tree hazard.
ADD_SWEEPS = {".", "*", "-A", "--all", "-u", "--update", ":/", ":(top)"}
ADD_INTERACTIVE = {"-i", "--interactive", "-p", "--patch", "-e", "--edit"}
# git commit: -a/--all auto-stages every tracked change (the sweep) and is
# refused; -i/--include and -o/--only are path-scoped (you name the paths)
# and stay allowed. -p/--patch, --interactive and -e/--edit open a TTY a
# hook-driven session does not have.
COMMIT_SWEEPS = {"-a", "--all"}
COMMIT_INTERACTIVE = {"-p", "--patch", "--interactive", "-e", "--edit"}


# ------------------------------------------------------------- pure refusals
# Mirrors pr.py's push_refusal / forward_refusal: the *reasons* an act may
# not happen are pure functions over their inputs, so the test suite hits
# them directly without driving git.

def add_refusal(tokens):
    """Why this `git add` may not run, or None. `tokens` is everything
    after `add`."""
    paths = []
    for token in tokens:
        bare = token.strip("'\"")
        if bare in ADD_SWEEPS:
            return (
                f"no sweep: `{bare}` stages more than you named — in the "
                "shared-tree fleet it pulls in another session's uncommitted "
                f"work. Name the paths: {PEN} add <path> <path>"
            )
        if bare in ADD_INTERACTIVE:
            return f"`{bare}` is interactive and cannot run here (no TTY) — name the paths instead"
        if not bare.startswith("-"):
            paths.append(bare)
    if not paths:
        return (
            "name at least one path to stage — explicit paths only "
            "(the shared-tree fleet; `add .` / `-A` / `-u` are refused)"
        )
    return None


def commit_refusal(branch, message, forwarded):
    """Why this `git commit` may not run, or None.

    `branch` is the current branch, `message` the list of -m values,
    `forwarded` every other token handed to commit.
    """
    if not branch:
        return "detached HEAD — a session commits on its claude/* branch, not a loose HEAD"
    if branch in TRUNK:
        return (
            f"never commit the trunk ('{branch}') — work lands on the session's "
            "claude/* branch; main carries only bdo's stamp (firm)"
        )
    has_file = False
    for token in forwarded:
        bare = token.strip("'\"")
        if bare in COMMIT_SWEEPS:
            return (
                f"no `{bare}`: it auto-stages every tracked change — in the "
                "shared-tree fleet that sweeps in another session's work. "
                f"Stage named paths first ({PEN} add ...) or pass them to commit"
            )
        if bare in COMMIT_INTERACTIVE:
            return f"`{bare}` is interactive and cannot run here (no TTY)"
        if bare == "--allow-empty-message":
            return "a commit carries a real message — --allow-empty-message is refused"
        if bare in ("-F", "--file"):
            has_file = True  # a message from a file is still a real message
    if not has_file and not (message and "".join(message).strip()):
        return (
            "a commit needs a real message: -m \"<what landed>\" (or -F <file>) "
            "— step-shaped, say what landed, not where it sat"
        )
    return None


# Numbered records whose id must be fleet-unique: a new done-line or report
# minted against a stale local fold collides with one already on a sibling
# branch — the four 0020 done-lines are the incident, tonight's 0050 the
# near-miss (done-line 0053). The fence stands here, at the commit seam,
# because loop/pen.py stays pure (no git, the placement-gate discipline).
RECORD_RE = re.compile(r"^\.ai-native/(done|reports)/(\d{4})-(.+\.md)$")


def record_id_collision(staged_new, ref_listing):
    """Why these newly-staged record files may not commit, or None.

    `staged_new` is the paths staged as additions (not in HEAD);
    `ref_listing` is {ref: [record paths on that ref]}. The law: a new
    done/reports file whose 4-digit id already names a *different* file in
    the same directory on any ref refuses to commit — the id fold is
    fleet-wide, not local. The same full path on a ref is propagation, not
    collision (carrying a sibling branch's record unchanged stays allowed),
    and only newly-staged files are judged, so history's existing duplicate
    ids are never retro-flagged (history is never retro-invalidated)."""
    for path in staged_new or []:
        mine = RECORD_RE.match(path)
        if not mine:
            continue
        directory, record_id, filename = mine.groups()
        for ref, paths in (ref_listing or {}).items():
            for other in paths:
                theirs = RECORD_RE.match(other)
                if not theirs:
                    continue
                if (theirs.group(1) == directory
                        and theirs.group(2) == record_id
                        and other != path):
                    return (
                        f"record id {record_id} is already taken in "
                        f".ai-native/{directory}/ on {ref} by "
                        f"{pathlib.PurePosixPath(other).name} — "
                        f"{filename} would mint a colliding id (the 0020 "
                        "incident). Re-mint after the local fold sees that "
                        "record (fetch and carry it, or pick the next id): "
                        "python -m loop.pen next " + directory
                    )
    return None


def restore_blocked(clean, pushed):
    """Why a viewport stranded off the trunk may NOT be auto-restored to
    main, or None. Restoring discards the branch checkout, so it is safe
    only when that work is already preserved — a clean tree and every commit
    on origin. Otherwise the session preserves its own work first (commit,
    push); it is never bdo's to hand-fix (rules expect support, 2026-06-11).
    """
    if not clean:
        return (
            "the viewport has uncommitted changes — the session commits and "
            "pushes them on their branch, then sync restores the viewport to "
            "main; the session preserves its own work, it is never bdo's to fix"
        )
    if not pushed:
        return (
            "the viewport's branch has commits not on origin — the session "
            "pushes them, then sync restores the viewport to main; the session "
            "preserves its own work, it is never bdo's to fix"
        )
    return None


def sync_refusal(branch, ahead):
    """Why a viewport already on the trunk may not be fast-forwarded, or None.
    Off-trunk is no longer refused here — a stranded viewport is restored when
    safe (see `restore_blocked`). The one hard stop is local commits sitting on
    main: they belong on a branch and a PR, which is the session's to do."""
    if ahead:
        return (
            f"the trunk carries {ahead} local commit(s) origin does not have "
            "— main is never committed locally (firm); the session moves them "
            "to a branch and PRs them, never asks bdo to sort it out"
        )
    return None


def garden_verdict(uncommitted, has_open_pr, has_merged_pr):
    """What to do with one non-trunk worktree — pure, and the safety of the
    whole auto-pruner lives here: it removes only what is provably done and
    surfaces everything a human might still want.

      keep     an open PR is in flight — an active workbench, left alone.
      surface  uncommitted work (stranded — commit or discard), or committed
               work with no PR at all (the mortal-session debris: PR it so the
               merge-node lands it, or delete the branch). Never removed.
      prune    a clean worktree whose branch carries a merged PR — the only
               case safe to remove without a human.

    A merged-but-dirty worktree (branch landed, yet uncommitted work sits in
    the tree) is the §10 bite: 'the branch is done' and 'the work is unsaved'
    are each locally fine and refuse to fit. Uncommitted wins — the work is
    surfaced, never pruned away."""
    if has_open_pr:
        return ("keep", "an open PR is in flight")
    if uncommitted:
        return ("surface", f"{uncommitted} uncommitted change(s) — stranded; commit or discard")
    if has_merged_pr:
        return ("prune", "branch merged — removed")
    return ("surface", "committed but no PR — stranded; PR it (the merge-node lands) or delete the branch")


# ------------------------------------------------------------------- runtime

def _refuse(message):
    print(f"result: report — refused: {message}")
    sys.exit(1)


def _run(args):
    proc = subprocess.run(
        args, capture_output=True, text=True, encoding="utf-8",
        errors="replace", cwd=ROOT,
    )
    if proc.returncode != 0:
        _refuse(f"`{' '.join(args)}` failed:\n{(proc.stderr or proc.stdout).strip()}")
    return proc.stdout


def cmd_add(ns):
    tokens = ns.forward
    reason = add_refusal(tokens)
    if reason:
        _refuse(reason)
    tags, intent = _intent_precheck(ns, "add")
    _run(["git", "add"] + tokens)
    staged = _run(["git", "diff", "--cached", "--name-only"]).strip()
    names = staged.splitlines()
    if tags:
        tags.note(ROOT, status="branded", tool="git", verb="add",
                  intent=intent, branded=True)
    tag = f" [intent: {intent}]" if intent else ""
    print(f"result: done — staged {len(names)} path(s): {', '.join(names) or '(none new)'}{tag}")


def _ref_record_listing(staged_new):
    """{ref: [record paths]} across local heads and origin/* — gathered only
    when a record file is actually staged (zero cost otherwise), and None on
    any sensor failure (fail open: a broken fold never blocks a commit)."""
    if not any(RECORD_RE.match(p) for p in staged_new):
        return {}
    try:
        refs = subprocess.run(
            ["git", "for-each-ref", "refs/heads", "refs/remotes/origin",
             "--format=%(refname:short)"],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", cwd=ROOT, timeout=15)
        if refs.returncode != 0:
            return None
        listing = {}
        for ref in refs.stdout.split():
            tree = subprocess.run(
                ["git", "ls-tree", "-r", "--name-only", ref,
                 "--", ".ai-native/done", ".ai-native/reports"],
                capture_output=True, text=True, encoding="utf-8",
                errors="replace", cwd=ROOT, timeout=15)
            if tree.returncode == 0:
                listing[ref] = tree.stdout.split()
        return listing
    except Exception:  # noqa: BLE001 — the fence protects, it never gates itself
        return None


def cmd_commit(ns):
    branch = _run(["git", "branch", "--show-current"]).strip()
    reason = commit_refusal(branch, ns.message, ns.forward)
    if reason:
        _refuse(reason)
    staged_new = _run(["git", "diff", "--cached", "--name-only",
                       "--diff-filter=A"]).split()
    listing = _ref_record_listing(staged_new)
    if listing is not None:
        reason = record_id_collision(staged_new, listing)
        if reason:
            _refuse(reason)
    tags, intent = _intent_precheck(ns, "commit")
    args = ["git", "commit"]
    for message in ns.message:
        args += ["-m", message]
    args += ns.forward  # parity: paths and any other commit flags ride along
    out = _run(args).strip()
    if out:
        print(out)
    if tags:
        tags.note(ROOT, status="branded", tool="git", verb="commit",
                  intent=intent, branded=True)
    tag = f" [intent: {intent}]" if intent else ""
    print(f"result: done — committed on {branch}{tag} "
          f"(hand-off still leaves the machine only through `{PEN.replace('git.py', 'pr.py')} push`)")


def cmd_sync(ns):
    """Fast-forward the viewport (the primary worktree) to origin/main —
    the merge's return leg (done-line 0031). ff-only cannot conflict: it
    succeeds or it surfaces. Hook mode never exits nonzero and never
    gates a session's start; a refusal there is one ambient line."""
    def emit(state, message):
        print(f"result: {state} — viewport-sync: {message}")

    def bail(message):
        emit("report", message)
        sys.exit(0 if ns.hook else 1)

    def git(args, cwd, timeout=None):
        return subprocess.run(
            ["git"] + args, capture_output=True, text=True,
            encoding="utf-8", errors="replace", cwd=cwd, timeout=timeout)

    try:
        # The viewport is the primary worktree — `git worktree list`
        # names it first from anywhere in the fleet.
        listing = git(["worktree", "list", "--porcelain"], ROOT)
        first = next((line for line in listing.stdout.splitlines()
                      if line.startswith("worktree ")), None)
        if listing.returncode != 0 or not first:
            bail("could not locate the viewport (`git worktree list` gave nothing)")
        viewport = first.split(" ", 1)[1].strip()
        fetched = git(["fetch", "origin", "main"], viewport,
                      timeout=ns.fetch_timeout)
        if fetched.returncode != 0:
            detail = (fetched.stderr or fetched.stdout).strip().splitlines()
            bail("fetch failed (offline?): " + (detail[-1] if detail else "no detail"))
        branch = git(["branch", "--show-current"], viewport).stdout.strip()
        if branch not in TRUNK:
            # A stranded viewport is the session's to restore, not bdo's to be
            # handed — but only when the branch work is safe (clean + pushed).
            clean = not git(["status", "--porcelain"], viewport).stdout.strip()
            upstream = git(["rev-parse", "--verify", "--quiet",
                            f"origin/{branch}"], viewport) if branch else None
            pushed = bool(branch) and upstream is not None and \
                upstream.returncode == 0 and not git(
                    ["rev-list", "--count", f"origin/{branch}..HEAD"],
                    viewport).stdout.strip().lstrip("0")
            blocked = restore_blocked(clean, pushed)
            if blocked:
                bail(f"the viewport is on '{branch or 'a detached HEAD'}' — "
                     + blocked)
            restored = git(["checkout", "main"], viewport)
            if restored.returncode != 0:
                detail = (restored.stderr or restored.stdout).strip().splitlines()
                bail("could not restore the viewport to main: "
                     + (detail[-1] if detail else "no detail"))
            emit("done", f"restored the viewport from '{branch}' to main "
                 "(its work is safe on origin); syncing")
            branch = "main"
        ahead = int(git(["rev-list", "--count", "origin/main..main"],
                        viewport).stdout.strip() or 0)
        reason = sync_refusal(branch, ahead)
        if reason:
            bail(reason)
        behind = int(git(["rev-list", "--count", "main..origin/main"],
                         viewport).stdout.strip() or 0)
        if not behind:
            if not ns.hook:  # ambient mode stays silent when there is nothing to say
                emit("done", "the viewport is current")
            return
        merged = git(["merge", "--ff-only", "origin/main"], viewport)
        if merged.returncode != 0:
            detail = (merged.stderr or merged.stdout).strip().splitlines()
            bail("fast-forward refused — " + (detail[-1] if detail else "no detail")
                 + "; the session sorts the divergence (branch + PR the stray "
                 "commits), it is never bdo's to hand-fix")
        emit("done", f"the viewport fast-forwarded {behind} commit(s) to origin/main")
    except subprocess.TimeoutExpired:
        bail(f"fetch exceeded {ns.fetch_timeout}s (offline?) — the viewport stays where it is")
    except Exception as error:  # fail open: the pen's own bug never gates a session
        bail(f"unexpected: {error}")


def cmd_garden(ns):
    """Remove worktrees whose branch has merged and whose tree is clean;
    surface everything else (done-line 0037). Auto-pruning a shared tree is
    only safe if it is conservative: prune the provably-done, never blind (gh
    unreachable → nothing removed), never touch the viewport or this session's
    own worktree. Hook mode is fail-open and exits 0 always, like sync."""
    import json

    lines = []

    def finish(state):
        head = lines[0] if lines else "nothing to garden"
        print(f"result: {state} — garden: {head}")
        for extra in lines[1:]:
            print(f"  · {extra}")
        sys.exit(0)

    def git(args, cwd):
        return subprocess.run(["git"] + args, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", cwd=cwd)

    try:
        listing = git(["worktree", "list", "--porcelain"], ROOT)
        worktrees, path = [], None
        for line in listing.stdout.splitlines():
            if line.startswith("worktree "):
                path = line.split(" ", 1)[1].strip()
            elif line.startswith("branch "):
                branch = line.split(" ", 1)[1].strip().replace("refs/heads/", "", 1)
                worktrees.append((path, branch))
                path = None
            elif line.startswith("detached"):
                worktrees.append((path, None))
                path = None
        if len(worktrees) <= 1:
            if not ns.hook:
                lines.append("no extra worktrees to garden")
            finish("done")

        viewport = pathlib.Path(worktrees[0][0]).resolve()
        here = pathlib.Path.cwd().resolve()

        gh = subprocess.run(
            ["gh", "pr", "list", "--state", "all", "--limit", "300",
             "--json", "headRefName,state"],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", cwd=ROOT, timeout=ns.gh_timeout)
        gh_ok = gh.returncode == 0
        pr_states = {}
        if gh_ok:
            for pr in json.loads(gh.stdout or "[]"):
                pr_states.setdefault(pr["headRefName"], set()).add(pr["state"])

        pruned, chores, wt_branches = [], [], set()
        for wpath, branch in worktrees:
            rp = pathlib.Path(wpath).resolve()
            if branch:
                wt_branches.add(branch)
            if rp == viewport or rp == here or branch in TRUNK:
                continue  # never the viewport, this session's tree, or the trunk
            slug = pathlib.Path(wpath).name
            states = pr_states.get(branch, set())
            has_open = "OPEN" in states
            has_merged = "MERGED" in states and not has_open
            unc = len([ln for ln in git(["status", "--porcelain"], wpath)
                       .stdout.splitlines() if ln.strip()])
            verdict, reason = garden_verdict(unc, has_open, has_merged)
            if verdict == "prune":
                if not gh_ok:
                    chores.append(f"{slug}: looks merged but gh is unreachable — left in place")
                    continue
                rm = git(["worktree", "remove", wpath], ROOT)
                if rm.returncode != 0:
                    tail = (rm.stderr or rm.stdout).strip().splitlines()
                    chores.append(f"{slug}: merged but remove refused — {tail[-1] if tail else 'no detail'}")
                    continue
                if branch:
                    git(["branch", "-D", branch], ROOT)
                pruned.append(slug)
            elif verdict == "surface":
                chores.append(f"{slug}: {reason}")
            # keep: silent

        # loose branches (no worktree): a lighter cleanup chore, same gh fold
        loose_merged, loose_stranded = 0, []
        if gh_ok:
            for b in git(["branch", "--format=%(refname:short)"], ROOT).stdout.split():
                if b in TRUNK or b in wt_branches:
                    continue
                s = pr_states.get(b, set())
                if not s:
                    loose_stranded.append(b)
                elif "MERGED" in s and "OPEN" not in s:
                    loose_merged += 1

        if not (pruned or chores or loose_merged or loose_stranded):
            if not ns.hook:
                lines.append("nothing to garden — the tree is tidy")
            finish("done")

        head_bits = []
        if pruned:
            head_bits.append(f"pruned {len(pruned)} merged worktree(s): {', '.join(pruned)}")
        if chores:
            head_bits.append(f"{len(chores)} worktree chore(s)")
        if loose_stranded:
            head_bits.append(f"{len(loose_stranded)} stranded branch(es): {', '.join(loose_stranded)}")
        if loose_merged:
            head_bits.append(f"{loose_merged} merged branch(es) with no worktree (git branch -D)")
        lines.append("; ".join(head_bits))
        lines.extend(chores)
        finish("report" if (chores or loose_stranded) else "done")
    except subprocess.TimeoutExpired:
        print(f"result: report — garden: gh exceeded {ns.gh_timeout}s — nothing pruned this run")
        sys.exit(0)
    except Exception as error:  # fail open: the pen's own bug never gates a session
        print(f"result: report — garden: unexpected: {error}")
        sys.exit(0)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="git.py", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    verbs = parser.add_subparsers(dest="verb", required=True)

    add = verbs.add_parser(
        "add", help="stage named paths only — `add .` / `-A` / `-u` are refused "
                    "(extra git-add flags forward for parity)")
    add.add_argument("--intent", metavar="VALUE",
                     help="optional intent tag; a known value that lies about "
                          "the verb is refused, a new one rides as proposed")
    add.set_defaults(func=cmd_add)

    commit = verbs.add_parser(
        "commit", help="commit on the session's claude/* branch with a real "
                       "message; `-a`/`--all` refused; paths and other flags forward")
    commit.add_argument("-m", "--message", action="append", default=[],
                        metavar="MSG",
                        help="the commit message (repeatable, like git); a real "
                             "step-shaped line saying what landed")
    commit.add_argument("--intent", metavar="VALUE",
                        help="optional intent tag; a known value that lies about "
                             "the verb is refused, a new one rides as proposed")
    commit.set_defaults(func=cmd_commit)

    sync = verbs.add_parser(
        "sync", help="fast-forward the viewport (primary worktree) to "
                     "origin/main — the merge's return leg; restores a "
                     "stranded viewport to main when its work is safe, "
                     "surfaces only to preserve unpushed work")
    sync.add_argument("--hook", action="store_true",
                      help="hook mode: at most one line, exit 0 always — "
                           "fail-open, never gates a session's start")
    sync.add_argument("--fetch-timeout", dest="fetch_timeout", type=int,
                      default=20, metavar="SECONDS",
                      help="seconds to wait on the network before reporting")
    sync.set_defaults(func=cmd_sync)

    garden = verbs.add_parser(
        "garden", help="remove worktrees whose branch has merged (clean tree "
                       "only); surface stranded work and chores — never prunes "
                       "blind or destroys unsaved work")
    garden.add_argument("--hook", action="store_true",
                        help="hook mode: concise, exit 0 always — fail-open, "
                             "never gates a session's start")
    garden.add_argument("--gh-timeout", dest="gh_timeout", type=int,
                        default=20, metavar="SECONDS",
                        help="seconds to wait on gh before skipping the prune")
    garden.set_defaults(func=cmd_garden)

    ns, extra = parser.parse_known_args(argv)
    ns.forward = extra
    ns.func(ns)


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    main()
