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
import collections
import datetime
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


def head_intent_refusal(branch, expected):
    """Why this commit may not run because HEAD is not where the session
    thinks it is, or None (done-line 0118).

    `expected` is the branch the session ASSERTS it is on (`--on`); `branch`
    is live HEAD. In the shared-tree fleet a parallel session can move the
    worktree's branch between a session reading HEAD and committing — so a
    commit that names its branch is refused when the names disagree (the
    collision that authored this guard). The assertion is per-invocation and
    explicit: nothing stored, nothing another session can race. Omitting
    `--on` refuses: branch intent is mandatory after the moving-viewport
    incident."""
    # Hotfix: branch intent is mandatory; do not infer it from live HEAD.
    if not expected:
        return (
            "HEAD-intent required: commit with `--on <branch>` naming the "
            "branch this work is meant for. A moving shared viewport already "
            "landed a commit on the wrong branch; the pen will not infer "
            "intent from live HEAD."
        )
    if branch != expected:
        return (
            f"HEAD-intent mismatch: you declared --on '{expected}', but live HEAD "
            f"is '{branch or 'detached'}'. A parallel session may have moved the "
            f"shared worktree's branch under you. Check out '{expected}' (or work "
            f"from its own worktree) before committing — this is the branch "
            f"collision turned into a clean deny (done-line 0118)."
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


def dirty_viewport_refusal(modified, untracked):
    """Why a behind-but-not-ahead viewport may not be fast-forwarded — the
    honest diagnosis when the working tree is dirty, or None when it is clean.

    A fast-forward refuses when uncommitted modifications to *tracked* files
    would be overwritten by the incoming commits; untracked files do not block
    a ff (they only collide if the incoming tree adds the same path). The
    earlier code reported the raw `merge --ff-only` failure as "branch + PR the
    stray commits" — but `sync_refusal` already bailed on any local commit, so
    that branch is only ever reached with zero stray commits: it always
    misdiagnoses. Name the real blocker instead. The workstation fence
    (done-line 0145) forbids a worker from reverting the viewport, so the
    sanctioned move is to preserve precious work to a worktree branch; this pen
    diagnoses, it does not silently mutate bdo's viewport.
    """
    if not modified and not untracked:
        return None
    tracked = (
        f"{modified} tracked file(s) carry uncommitted modifications that "
        "block the fast-forward"
        if modified else
        "untracked files are present (they do not block the fast-forward, but "
        "the tree is not clean)"
    )
    extra = f" (plus {untracked} untracked path(s))" if modified and untracked else ""
    return (
        f"the viewport has uncommitted changes, not stray commits — {tracked}"
        f"{extra}. The workstation fence forbids a worker from reverting or "
        "cleaning the viewport; preserve any precious work to a worktree branch "
        "(`git worktree add -b claude/<slug> ../ontum-wt/<slug> origin/main`, "
        "copy the files in, commit with the git pen), then the tree is clean "
        "and sync fast-forwards. It is never bdo's to hand-fix."
    )


def rescue_branch_name(today, existing, label="viewport"):
    """The rescue branch a whiteout commits a dirty viewport's pile onto:
    `claude/rescue-viewport-<date>`, with a `-N` suffix when that name is
    already taken so a second whiteout the same day never clobbers the first
    (done-line 0170, #415). Pure: the date and the existing-ref set are passed
    in, so the name is a deterministic fold, not a clock read."""
    base = f"claude/rescue-{label}-{today}"
    if base not in existing:
        return base
    n = 2
    while f"{base}-{n}" in existing:
        n += 1
    return f"{base}-{n}"


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


# ------------------------------------------------- the inference-verified cut
# Done-line 0100. A branch deletion is irreversible and was once taken on a
# branch-state signal alone — a concurrent gardener cut a branch that still
# carried novel, unlanded code. bdo's fix: the CUT is verified by *habitual
# inference*, and that verification is a GOVERNED act, AuthN + AuthZ across the
# three as-code layers:
#   config-as-code  the bdo-signed gateway policy (default-deny) authorizes the
#                   call AND stands as the cut-authorization (loop/inference.py).
#   infra-as-code   the garden→gateway wiring; the gateway is the one sanctioned
#                   inference egress (loop's no-network rule holds — the HTTP
#                   POST lives only in the gateway pen, never here).
#   prompt-as-code  CUT_VERIFIER_PROMPT below — versioned source, and its sha256
#                   rides the filled prompt so it lands on the inference receipt
#                   (every cut attributable to the prompt that judged it, §7).
# The cut FAILS SAFE: anything short of (clean content floor AND an explicit
# inference affirmation) holds the branch — while the garden hook stays
# fail-open. Default-deny means: until bdo stamps the policy, every cut is held.

CUT_VERIFIER_CALLER = "branch-ritual.garden"   # AuthN: the named caller, never anonymous
CUT_VERIFIER_SURFACE = "branch-cut"            # the surface the policy authorizes

CUT_VERIFIER_PROMPT = """\
You are the cut-verifier for an automated git branch gardener. A branch is about
to be DELETED. Deleting a branch that still holds work not yet on the main line
loses that work irreversibly; a stale branch costs nothing. Decide whether
deleting this branch is SAFE.

SAFE means every change on this branch is already present on origin/main —
nothing novel would be lost. If the branch carries ANY work not yet on main, or
you cannot tell from the evidence, it is NOT safe.

Evidence — the branch's commits not reachable from origin/main, with their
summary (an empty list means the content is already upstream):

{evidence}

Answer with exactly ONE line and nothing else:
  SAFE: <short reason>   — every change is already on main; deleting loses nothing
  HOLD: <short reason>   — novel/unlanded work, or you cannot be sure
Default to HOLD when uncertain. Losing work is worse than keeping a stale branch.
"""


def cut_prompt_sha():
    """The prompt-as-code artifact's identity (done-line 0100, §7)."""
    import hashlib
    return hashlib.sha256(CUT_VERIFIER_PROMPT.encode("utf-8")).hexdigest()


def cut_verdict(unlanded_count, inference_verdict):
    """Whether one branch may be deleted — pure, and the whole safety of the
    inference-verified prune lives here. Two gates, in strict order:

      1. the deterministic content floor — a branch with ANY commit unreachable
         from origin/main carries unlanded work and is HELD, and no inference
         verdict can override it (the spawn-rail loss: a cut on a branch state
         while novel code sat on the branch);
      2. the habitual inference affirmation — only an explicit `safe` cuts;
         every other verdict (hold, uncertain, unavailable) holds the branch.

    Returns ("cut" | "hold", reason). The §10 bite: cut_verdict(2, "safe")
    holds — two locally-fine signals (merged-looking, model says safe) still
    refuse to fit against the hard truth that unlanded commits exist."""
    if unlanded_count > 0:
        return ("hold", f"{unlanded_count} commit(s) not on origin/main — "
                "unlanded work; the content floor is absolute, no inference "
                "verdict overrides it")
    if inference_verdict == "safe":
        return ("cut", "content-clean (no unlanded commits) and habitual "
                "inference affirmed the cut safe")
    return ("hold", "habitual inference did not affirm safe "
            f"(verdict: {inference_verdict}) — the cut fails safe")


def parse_inference_verdict(raw):
    """Map a cut-verifier reply (or None) to safe | hold | uncertain |
    unavailable. None is the gateway returning no answer — refused by policy
    (default-deny AuthZ), down, or unregistered — and maps to `unavailable`,
    which cut_verdict treats exactly like hold (fail-safe)."""
    if raw is None:
        return "unavailable"
    head = raw.strip().upper()
    # the token must stand alone — `\b` so an off-script "SAFEGUARD" is not read
    # as SAFE (inert today, since the content floor already protects every cut,
    # but the parser should not lie). Affirmation is narrow on purpose.
    if re.match(r"SAFE\b", head):
        return "safe"
    if re.match(r"HOLD\b", head):
        return "hold"
    return "uncertain"


def branch_cut_evidence(branch, git_fn):
    """(unlanded_count, evidence_text) for one branch vs origin/main, via the
    injected `git_fn(args) -> stdout`. unlanded_count counts commits not already
    equivalent upstream (`git cherry`, the deterministic floor); evidence_text
    is those commits' subjects + a bounded diffstat — the material the verifier
    reasons over."""
    cherry = git_fn(["cherry", "origin/main", branch]).splitlines()
    unlanded = len([ln for ln in cherry if ln.strip().startswith("+")])
    if unlanded == 0:
        return 0, "(no commits unreachable from origin/main — content is already upstream)"
    subjects = git_fn(["log", "--oneline", "--no-decorate",
                       f"origin/main..{branch}"]).strip()
    stat = git_fn(["diff", "--stat", f"origin/main...{branch}"]).strip()
    stat_lines = stat.splitlines()
    if len(stat_lines) > 40:  # bound the evidence — a giant branch can't blow the prompt
        stat = "\n".join(stat_lines[:40] + [f"... (+{len(stat_lines) - 40} more)"])
    return unlanded, f"commits:\n{subjects}\n\ndiffstat:\n{stat}"


def _gateway_complete(prompt, *, timeout, by, root):
    """Route one cut-verification through the governed gateway pen — the single
    sanctioned inference path (done-line 0062). Returns the reply content, or
    None when the plane gives no answer (refused by policy / down / no mind):
    AuthZ said no, or no mind could think, and the cut must fail safe. The
    outward reach lives here, never in the pure functions above."""
    import importlib.util
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    gw_path = ROOT / ".claude" / "skills" / "gateway" / "gateway.py"
    spec = importlib.util.spec_from_file_location("ontum_gateway", gw_path)
    gw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gw)
    out = gw.complete(prompt, caller=CUT_VERIFIER_CALLER,
                      surface=CUT_VERIFIER_SURFACE, route="default",
                      by=by, timeout=timeout, root=str(root / ".ai-native"))
    return out.get("content") if out.get("ok") else None


def verify_cut(branch, git_fn, complete_fn=None, *, timeout=45):
    """Decide whether `branch` may be deleted — the inference-verified cut
    (done-line 0100). Gathers the content evidence, applies the deterministic
    floor, and — only when the floor passes, i.e. a cut is actually possible —
    consults the governed gateway *habitually* before affirming. Returns
    ("cut" | "hold", reason). `complete_fn(prompt) -> reply|None` is injected
    for tests; production routes through the gateway pen.

    Fail-safe and fail-soft: any error gathering evidence or thinking holds the
    branch (never an accidental cut) without raising, so the garden hook stays
    fail-open."""
    try:
        unlanded, evidence = branch_cut_evidence(branch, git_fn)
    except Exception as error:  # noqa: BLE001 — a sensor failure holds, never cuts
        return ("hold", f"could not gather cut evidence ({error}) — held, not cut")
    if unlanded > 0:
        return cut_verdict(unlanded, "floor-hold")  # no thought can override the floor
    fn = complete_fn or (lambda prompt: _gateway_complete(
        prompt, timeout=timeout, by=CUT_VERIFIER_CALLER, root=ROOT))
    filled = (f"[cut-verifier prompt-as-code sha256:{cut_prompt_sha()}]\n\n"
              + CUT_VERIFIER_PROMPT.format(evidence=evidence))
    try:
        raw = fn(filled)
    except Exception:  # noqa: BLE001 — thinking failed → unavailable → hold
        raw = None
    return cut_verdict(unlanded, parse_inference_verdict(raw))


# ------------------------------------------------------------------- runtime

def _refuse(message):
    print(f"result: report — refused: {message}")
    sys.exit(1)


def _git_toplevel(cwd):
    proc = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, encoding="utf-8",
        errors="replace", cwd=cwd,
    )
    if proc.returncode != 0:
        return None
    return pathlib.Path(proc.stdout.strip()).resolve()


def invocation_root_refusal(pen_root, cwd_root):
    """Why this pen invocation may not mutate, or None.

    The pen is worktree-local law: a session in worktree A must not be able to
    invoke worktree B's pen and accidentally stage or commit in B.
    """
    if cwd_root is None:
        return (
            "not inside a git worktree - run the pen from the worktree whose "
            "branch you are mutating"
        )
    pen_root = pathlib.Path(pen_root).resolve()
    cwd_root = pathlib.Path(cwd_root).resolve()
    if pen_root != cwd_root:
        return (
            f"pen/worktree mismatch: this pen belongs to {pen_root}, but the "
            f"caller is in {cwd_root}. Use the pen from that worktree "
            "(`python .claude/skills/branch-ritual/git.py ...` from its root) "
            "so the environment and the tool agree."
        )
    return None


def _assert_invocation_root():
    reason = invocation_root_refusal(ROOT, _git_toplevel(pathlib.Path.cwd()))
    if reason:
        _refuse(reason)


def _run(args):
    proc = subprocess.run(
        args, capture_output=True, text=True, encoding="utf-8",
        errors="replace", cwd=ROOT,
    )
    if proc.returncode != 0:
        _refuse(f"`{' '.join(args)}` failed:\n{(proc.stderr or proc.stdout).strip()}")
    return proc.stdout


def cmd_add(ns):
    _assert_invocation_root()
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


def _workspace():
    """The workspace-binding module (loop/workspace.py, done-line 0121), or
    None if loop isn't importable. The fold and the pure `binding_refusal`
    live there; the pen only enforces."""
    try:
        sys.path.insert(0, str(ROOT))
        from loop import workspace
        return workspace
    except Exception:  # noqa: BLE001 — handled at the call site
        return None


def cmd_commit(ns):
    _assert_invocation_root()
    branch = _run(["git", "branch", "--show-current"]).strip()
    reason = head_intent_refusal(branch, ns.on)
    if reason:
        _refuse(reason)
    # The claim↔workspace binding (done-line 0121): a commit asserting it
    # serves a claim (`--claim`) is refused unless this branch is bound to that
    # claim — the branch belongs to its work, not the mortal session (§4).
    # Opt-in like `--on`; omitted, the binding is never consulted.
    if getattr(ns, "claim", None):
        ws = _workspace()
        if ws is None:
            _refuse("--claim asked for the workspace-binding check, but "
                    "loop.workspace is not importable from here — run from the "
                    "repo root, or drop --claim")
        reason = ws.binding_refusal(branch, ns.claim, ws.active_bindings(ROOT / ".ai-native"))
        if reason:
            _refuse(reason)
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


def _oneline(proc):
    """The last line of a subprocess's stderr/stdout, for a terse refusal."""
    detail = (proc.stderr or proc.stdout).strip().splitlines()
    return detail[-1] if detail else "no detail"


Preserved = collections.namedtuple(
    "Preserved", "ok rescue staged push_note started error")


def _current_ref(git, worktree):
    """The ref a worktree sits on: its branch name, or the HEAD sha when
    detached — so a rescue can branch from it and a rollback can return to it."""
    branch = git(["branch", "--show-current"], worktree).stdout.strip()
    return branch or git(["rev-parse", "HEAD"], worktree).stdout.strip()


def _existing_refs(git, worktree):
    """The local + remote ref names a rescue name must avoid — remote-tracking
    branches counted under their BARE name too, so a rescue pushed earlier but
    since deleted locally still lives on origin and is never re-minted and
    clobbered on push."""
    raw = git(["for-each-ref", "--format=%(refname:short)",
               "refs/heads", "refs/remotes"], worktree).stdout.split()
    return set(raw) | {r.split("/", 1)[1] for r in raw if r.startswith("origin/")}


def preserve_pile(worktree, git, label, fetch_timeout=20):
    """Preserve a worktree's ENTIRE uncommitted pile onto a fresh dated rescue
    branch — proof-carrying (the whiteout shape, done-lines 0064/0170): stage
    the whole pile (`add -A`), commit it, and push it BEFORE anything is
    cleaned, so nothing is ever discarded. This is the ONE rescue definition
    `whiteout` (the viewport) and `rescue` (any bench) both call (I-4,
    done-line 0193).

    A CLEAN tree is a safe no-op (`.rescue is None`, `.staged == []`). On a git
    failure the worktree is restored to exactly where it started and `.ok` is
    False (no half-made rescue branch is left behind). On success the worktree
    is left CHECKED OUT on the rescue branch (its pile committed there, so the
    tree is clean); the caller decides whether to walk it back to a trunk."""
    started = _current_ref(git, worktree)
    if not git(["status", "--porcelain"], worktree).stdout.strip():
        return Preserved(True, None, [], "", started, None)

    head = git(["rev-parse", "--short", "HEAD"], worktree).stdout.strip()
    rescue = rescue_branch_name(
        datetime.date.today().isoformat(), _existing_refs(git, worktree), label)

    made = git(["checkout", "-b", rescue], worktree)
    if made.returncode != 0:
        return Preserved(False, rescue, [], "", started,
                         f"could not open the rescue branch '{rescue}' — "
                         f"{_oneline(made)}; the worktree is untouched")
    added = git(["add", "-A"], worktree)
    if added.returncode != 0:
        git(["checkout", started], worktree)
        git(["branch", "-D", rescue], worktree)
        return Preserved(False, rescue, [], "", started,
                         f"could not stage the pile — {_oneline(added)}; the "
                         "work is still in the worktree, untouched")
    staged = [p for p in git(["diff", "--cached", "--name-only"],
                             worktree).stdout.splitlines() if p]
    if not staged:
        # the tree read dirty but nothing staged (an ignored-only change) —
        # never leave an empty rescue branch behind
        git(["checkout", started], worktree)
        git(["branch", "-D", rescue], worktree)
        return Preserved(True, None, [], "", started, None)

    message = (
        f"rescue: preserve the {label} pile ({len(staged)} path(s)) off {head}\n\n"
        "Proof-carrying recovery (#415, done-lines 0064/0170/0193): the worktree "
        "was dirty and the pile is preserved on this branch BEFORE anything is "
        "cleaned — nothing is discarded. Reconcile what is still wanted into a "
        "real PR, or drop this branch once the pile is accounted for.")
    committed = git(["commit", "-m", message], worktree)
    if committed.returncode != 0:
        git(["checkout", started], worktree)
        git(["branch", "-D", rescue], worktree)
        return Preserved(False, rescue, [], "", started,
                         f"could not commit the rescue pile — "
                         f"{_oneline(committed)}; the worktree is untouched")
    pushed = git(["push", "-u", "origin", rescue], worktree, timeout=fetch_timeout)
    push_note = ("pushed to origin" if pushed.returncode == 0
                 else f"NOT pushed (offline?: {_oneline(pushed)}) — it is "
                      "committed locally and safe; push it with the PR pen")
    return Preserved(True, rescue, staged, push_note, started, None)


def recover_dirty_viewport(viewport, git, emit, bail, ns):
    """The whiteout utensil's actuator (done-line 0170, #415): sort a DIRTY
    viewport without losing a byte.

    A session cannot do this itself — the workstation fence forbids every
    working-state git verb in the primary tree (checkout/reset/restore/clean/
    stash), and the git pen refuses to commit on the trunk. The pen is the one
    actor sanctioned to flip the viewport (it already runs checkout + merge
    here), so recovery is the pen's. It is proof-carrying, the whiteout shape of
    the phrasing door (done-line 0064): it PRESERVES before it cleans — the
    entire pile is committed (`add -A`, a total snapshot) and pushed onto a
    rescue branch FIRST, and only then is the now-clean viewport fast-forwarded
    to origin/main. Nothing is discarded; the rescue branch is surfaced for
    reconciliation. Caller guarantees: the viewport is on the trunk, dirty, and
    carries no local commits origin lacks (a clean fast-forward but for the
    tree).

    The preserve-the-pile core is shared with the `rescue` verb
    (`preserve_pile`, done-line 0193 — one rescue definition, I-4); this
    function adds only the viewport-specific tail: return the clean tree to the
    trunk and fast-forward it to origin/main."""
    result = preserve_pile(viewport, git, "viewport", fetch_timeout=ns.fetch_timeout)
    if not result.ok:
        bail(f"whiteout {result.error}")
    rescue, staged, push_note = result.rescue, result.staged, result.push_note
    trunk = result.started or "main"

    # return the viewport to a clean trunk and fast-forward to origin/main.
    # preserve_pile leaves us on the rescue branch only when it made one.
    if rescue:
        back = git(["checkout", trunk], viewport)
        if back.returncode != 0:
            bail(f"whiteout preserved the pile on '{rescue}' ({push_note}) but "
                 f"could not return the viewport to {trunk} — {_oneline(back)}; "
                 f"the work is safe, restore {trunk} by hand")
    behind = int(git(["rev-list", "--count", f"{trunk}..origin/main"],
                     viewport).stdout.strip() or 0)
    if behind:
        merged = git(["merge", "--ff-only", "origin/main"], viewport)
        if merged.returncode != 0:
            where = (f"preserved the pile on '{rescue}' ({push_note}) and " if
                     staged else "")
            bail(f"whiteout {where}left the viewport clean, but the "
                 f"fast-forward was refused — {_oneline(merged)}")
    if staged:
        emit("done",
             f"whiteout recovered the dirty viewport: {len(staged)} path(s) "
             f"preserved on '{rescue}' ({push_note}); the viewport returned to "
             f"{trunk} and fast-forwarded {behind} commit(s) to origin/main. "
             "Open the reconciliation PR for the rescue branch with the PR pen "
             "(python .claude/skills/branch-ritual/pr.py create, from a "
             f"worktree on '{rescue}') — until then the garden surfaces it as "
             "committed-but-no-PR. Nothing was lost.")
    else:
        emit("done", f"whiteout: the viewport was already clean — "
             f"fast-forwarded {behind} commit(s) to origin/main; "
             "nothing to recover.")


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
        # The whiteout utensil (done-line 0170, #415): a dirty viewport cannot
        # be fast-forwarded (the merge would fail on the unsaved tree) and a
        # session cannot clean it itself (the workstation fence). The pen sorts
        # it — but only when explicitly asked. In hook mode (ambient
        # SessionStart) it surfaces a pointer rather than branching and pushing
        # autonomously at every dirty start; `whiteout` (or an explicit `sync`)
        # actuates it.
        dirty = bool(git(["status", "--porcelain"], viewport).stdout.strip())
        if dirty:
            if ns.hook and not getattr(ns, "recover", False):
                bail("the viewport is dirty (uncommitted work) — a session "
                     "cannot clean the primary tree itself (the workstation "
                     "fence). Recover it with the whiteout utensil, which "
                     "preserves the pile on a rescue branch before it cleans: "
                     "python .claude/skills/branch-ritual/git.py whiteout")
            recover_dirty_viewport(viewport, git, emit, bail, ns)
            return
        behind = int(git(["rev-list", "--count", "main..origin/main"],
                         viewport).stdout.strip() or 0)
        if not behind:
            if not ns.hook:  # ambient mode stays silent when there is nothing to say
                emit("done", "the viewport is current")
            return
        # ahead == 0 here (sync_refusal bailed otherwise), so a ff can only be
        # blocked by uncommitted tracked changes — diagnose that honestly rather
        # than letting the raw merge error read as phantom stray commits.
        status = [ln for ln in git(["status", "--porcelain"], viewport)
                  .stdout.splitlines() if ln.strip()]
        modified = sum(1 for ln in status if not ln.startswith("??"))
        untracked = sum(1 for ln in status if ln.startswith("??"))
        dirty = dirty_viewport_refusal(modified, untracked)
        if dirty:
            bail(dirty)
        merged = git(["merge", "--ff-only", "origin/main"], viewport)
        if merged.returncode != 0:
            detail = (merged.stderr or merged.stdout).strip().splitlines()
            bail("fast-forward refused — " + (detail[-1] if detail else "no detail")
                 + "; the tree is clean and not ahead, so this is an unexpected "
                 "non-fast-forward — surface it, it is never bdo's to hand-fix")
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
                # A merged PR is necessary but NOT sufficient (done-line 0100):
                # before the irreversible cut, the content floor + habitual
                # inference must agree. Default-deny holds the cut until bdo
                # stamps the policy — the aggressive prune stops here, safely.
                decision, why = (verify_cut(branch, lambda a: git(a, ROOT).stdout)
                                 if branch else ("hold", "detached — no branch to verify"))
                if decision != "cut":
                    chores.append(f"{slug}: merged PR, but the cut is held — {why}")
                    continue
                rm = git(["worktree", "remove", wpath], ROOT)
                if rm.returncode != 0:
                    tail = (rm.stderr or rm.stdout).strip().splitlines()
                    chores.append(f"{slug}: merged but remove refused — {tail[-1] if tail else 'no detail'}")
                    continue
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
            # Never a blanket `git branch -D` invitation (done-line 0100): that
            # recommendation is how a branch carrying unlanded work gets swept
            # by hand. The garden is the one pruner and it verifies every cut.
            head_bits.append(f"{loose_merged} merged branch(es) with no worktree "
                             "— left in place; pruning is the garden's, and each "
                             "cut is verified (no blind delete)")
        lines.append("; ".join(head_bits))
        lines.extend(chores)
        finish("report" if (chores or loose_stranded) else "done")
    except subprocess.TimeoutExpired:
        print(f"result: report — garden: gh exceeded {ns.gh_timeout}s — nothing pruned this run")
        sys.exit(0)
    except Exception as error:  # fail open: the pen's own bug never gates a session
        print(f"result: report — garden: unexpected: {error}")
        sys.exit(0)


def cmd_whiteout(ns):
    """The `:whiteout` utensil (done-line 0170, #415): recover a dirty viewport
    without losing work. A thin, explicitly-named alias over `sync` that always
    actuates the recovery — where `sync --hook` only points at the utensil at an
    ambient session start, `whiteout` is the verb a session reaches for to
    actually sort the tree. On a CLEAN viewport it is simply a sync (fast-forward
    to origin/main); there is nothing to recover and nothing is lost either way.
    The named utensil bdo asked every workstation to ship with."""
    ns.recover = True
    ns.hook = False
    cmd_sync(ns)


def _rescue_label(worktree):
    """A short, ref-safe label for a worktree's rescue branch — its directory
    name reduced to [a-z0-9-], so the branch reads
    `claude/rescue-<name>-<date>`. The viewport keeps its own 'viewport' label
    (recover_dirty_viewport passes it explicitly)."""
    name = re.sub(r"[^a-z0-9-]+", "-", pathlib.Path(worktree).name.lower())
    return name.strip("-") or "worktree"


def cmd_rescue(ns):
    """Preserve ANY worktree's uncommitted pile onto a dated rescue branch — the
    bench-rescue verb (done-line 0193). `whiteout` aims the same proof-carrying
    rescue core (`preserve_pile`) at the VIEWPORT and then walks the clean tree
    back to the trunk; `rescue` aims it at any worktree (a stranded bench, a
    forest leaf) and leaves it ON the rescue branch, its pile committed and
    pushed. A CLEAN worktree is a safe no-op. So the forest never strands: any
    bench's uncommitted pile is one verb away from preserved-and-pushed."""
    def emit(state, message):
        print(f"result: {state} — rescue: {message}")

    def bail(message):
        emit("report", message)
        sys.exit(0 if getattr(ns, "hook", False) else 1)

    def git(args, cwd, timeout=None):
        return subprocess.run(
            ["git"] + args, capture_output=True, text=True,
            encoding="utf-8", errors="replace", cwd=cwd, timeout=timeout)

    target = getattr(ns, "worktree_flag", None) or ns.worktree
    if not target:
        bail(f"name the worktree to rescue: {PEN} rescue <path> "
             "(or --worktree <path>)")
    try:
        path = pathlib.Path(target).expanduser()
        if not path.exists():
            bail(f"no such worktree: {target}")
        inside = git(["rev-parse", "--is-inside-work-tree"], str(path))
        if inside.returncode != 0 or inside.stdout.strip() != "true":
            bail(f"{target} is not a git worktree — {_oneline(inside)}")
        worktree = str(path.resolve())

        if not git(["status", "--porcelain"], worktree).stdout.strip():
            emit("done", f"nothing to rescue — {target} is already clean")
            return

        result = preserve_pile(worktree, git, _rescue_label(worktree),
                               fetch_timeout=ns.fetch_timeout)
        if not result.ok:
            bail(result.error)
        if not result.staged:
            emit("done", f"nothing to rescue — {target} is already clean")
            return
        emit("done",
             f"rescued {target}: {len(result.staged)} path(s) preserved on "
             f"'{result.rescue}' ({result.push_note}); the worktree is on the "
             "rescue branch with a clean tree — nothing was lost. Open a "
             "reconciliation PR for the rescue branch with the PR pen, or drop "
             "it once the pile is accounted for.")
    except subprocess.TimeoutExpired:
        bail(f"push exceeded {ns.fetch_timeout}s (offline?) — the pile is "
             "committed locally and safe; push the rescue branch with the PR pen")
    except Exception as error:  # fail open like sync — the pen's bug never strands
        bail(f"unexpected: {error}")


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
    commit.add_argument("--on", metavar="BRANCH",
                        help="required branch intent; the pen refuses "
                             "if live HEAD differs — the HEAD-intent guard "
                             "(done-line 0118), for the shared-tree fleet")
    commit.add_argument("--claim", metavar="WORK",
                        help="the work this branch serves; the pen refuses if the "
                             "branch is unbound or bound to a different claim — "
                             "the workspace binding (done-line 0121). Bind first "
                             "with `python -m loop.workspace claim`")
    commit.set_defaults(func=cmd_commit)

    sync = verbs.add_parser(
        "sync", help="fast-forward the viewport (primary worktree) to "
                     "origin/main — the merge's return leg; restores a "
                     "stranded viewport to main when its work is safe; an "
                     "explicit run on a DIRTY viewport recovers it via the "
                     "whiteout utensil (preserve the pile, then sync), while "
                     "--hook only points at the utensil")
    sync.add_argument("--hook", action="store_true",
                      help="hook mode: at most one line, exit 0 always — "
                           "fail-open, never gates a session's start")
    sync.add_argument("--fetch-timeout", dest="fetch_timeout", type=int,
                      default=20, metavar="SECONDS",
                      help="seconds to wait on the network before reporting")
    sync.set_defaults(func=cmd_sync, recover=False)

    whiteout = verbs.add_parser(
        "whiteout", help="recover a DIRTY viewport without losing work — "
                         "preserve the whole pile on a rescue branch, then "
                         "sync the clean viewport to origin/main (#415, the "
                         "named mistake-recovery utensil)")
    whiteout.add_argument("--fetch-timeout", dest="fetch_timeout", type=int,
                          default=20, metavar="SECONDS",
                          help="seconds to wait on the network before reporting")
    whiteout.set_defaults(func=cmd_whiteout, hook=False, recover=True)

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

    rescue = verbs.add_parser(
        "rescue", help="preserve ANY worktree's uncommitted pile onto a dated "
                       "rescue branch (committed + pushed, proof-carrying) so "
                       "the forest never strands; a clean worktree is a safe "
                       "no-op (done-line 0193)")
    rescue.add_argument("worktree", metavar="WORKTREE", nargs="?",
                        help="path to the worktree to rescue (positional)")
    rescue.add_argument("--worktree", dest="worktree_flag", metavar="PATH",
                        help="path to the worktree to rescue (same as the "
                             "positional argument)")
    rescue.add_argument("--fetch-timeout", dest="fetch_timeout", type=int,
                        default=20, metavar="SECONDS",
                        help="seconds to wait on the push before reporting")
    rescue.set_defaults(func=cmd_rescue, hook=False)

    ns, extra = parser.parse_known_args(argv)
    ns.forward = extra
    ns.func(ns)


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    main()
