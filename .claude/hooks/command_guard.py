#!/usr/bin/env python3
"""PreToolUse guard and watcher — raw external commands are gated and seen.

Done-line 0011 / branch-ritual v0.3.0. Two jobs, one hook:

1. Guard: the firm rules are denied outright (exit 2) — raw `gh pr`
   mutations and raw `git add` / `git commit` go through their pens
   (.claude/skills/branch-ritual/{pr,git}.py), nothing pushes to the
   trunk, no one merges or approves their own line. The deny-list is
   NOT this file: it is the family-neutral fence registry
   (fence/policy.py, done-line 0029), compiled to regex shape at
   import — tightening the fence is adding a registry rule, and both
   surfaces (this guard, the rendered .codex/ layer) move together.

2. Watcher: every other raw invocation of an external tool (gh, curl,
   network git, *and now local mutating git* — checkout, branch, merge,
   ...) is allowed but recorded to the watch log
   (.ai-native/log/tool-use.jsonl — a sensor trace, gitignored and
   deletable, not truth). `--report` folds the log into counts: the
   heaviest unwrapped tool is the next wrapper worth building. We only
   build what we use.

3. Shame (`--post`, a PostToolUse hook): using the generic brand when
   no branded wrapper exists gets called out *in the context window*
   via additionalContext — once per tool per session, with the running
   audit count. Surfaced, it becomes a judgment call (mint the wrapper
   or keep it raw); never surfaced, it stays silent. That asymmetry is
   the point.

Stdlib only. As a hook it reads the PreToolUse JSON on stdin and exits
0 (allow) or 2 (deny, stderr explains). Run `--report` by hand or
during branch gardening.
"""

from __future__ import annotations

import datetime
import json
import os
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
WATCH_LOG = pathlib.Path(
    os.environ.get("ONTUM_TOOL_WATCH_LOG", ROOT / ".ai-native" / "log" / "tool-use.jsonl")
)
# The truth-log root the posture fold reads from — the `.ai-native` two
# levels above the sensor trace, so the one env override (ONTUM_TOOL_WATCH_LOG)
# points both the would-deny record and the security_mode admissions it
# branches on at the same temp root under test (done-line 0096).
AI_NATIVE_ROOT = WATCH_LOG.parent.parent
def _compile(argv):
    """A registry argv prefix in this guard's regex shape: the verbs in
    sequence anywhere in the quote-stripped command, refusing to bleed
    into hyphenated cousins (`git commit` is not `git commit-tree`)."""
    parts = []
    for element in argv:
        alternatives = element if isinstance(element, tuple) else (element,)
        escaped = [re.escape(a) for a in alternatives]
        parts.append(escaped[0] if len(escaped) == 1
                     else "(?:" + "|".join(escaped) + ")")
    return r"\b" + r"\s+".join(parts) + r"\b(?!-)"


def _deny_rules():
    """The deny-list IS the fence registry (done-line 0029): one home,
    fence/policy.py, this surface compiled from it at import. A fence
    that can't load fails open — but loudly, on the watch log and
    stderr: a silently unguarded repo that still looks guarded is the
    known failure mode (write_guard learned it first)."""
    try:
        sys.path.insert(0, str(ROOT))
        from fence import policy
        return tuple(
            (rule["id"], _compile(rule["argv"]), rule["justification"])
            for rule in policy.RULES if rule["decision"] == "forbidden"
        )
    except Exception as exc:  # noqa: BLE001 — any load failure degrades, none crashes
        record({"status": "degraded", "rule": "fence-load", "error": repr(exc)})
        print(
            f"[command_guard] fence registry failed to load ({exc!r}) — the "
            "deny-list is EMPTY for this call; fix fence/policy.py",
            file=sys.stderr,
        )
        return ()

# Heads that stay invisible to the watcher: local work, not external reach.
LOCAL_HEADS = {
    "python", "python3", "py", "cd", "ls", "dir", "cat", "type", "echo",
    "head", "tail", "grep", "rg", "find", "findstr", "sed", "awk", "sort",
    "wc", "tee", "jq", "mkdir", "rm", "cp", "mv", "touch", "pwd", "set",
    "export", "if", "for", "while", "do", "then", "else", "fi", "true",
    "false", "test", "exit",
}
GIT_NETWORK = {"push", "fetch", "pull", "clone", "remote", "ls-remote"}
# Local git that *changes* the tree, index, history or refs — visible to
# the watcher so the next verb to brand nominates itself (done-line 0020).
# `add`/`commit` are already denied above and never reach the watcher;
# they sit here so the set means what it says. Read-only git
# (status/log/diff/show) is deliberately absent: a session may always look.
GIT_MUTATING = {
    "add", "commit", "checkout", "switch", "branch", "merge", "rebase",
    "reset", "revert", "cherry-pick", "stash", "tag", "worktree", "clean",
    "restore", "rm", "mv", "am", "apply", "update-ref", "update-index",
    "gc", "prune", "notes", "replace", "commit-tree",
}
# The tree/HEAD-flipping subset — the verbs that change what is checked out,
# discard working state, or rewrite history/refs. FORBIDDEN in bdo's viewport
# (the primary tree): a worker edits only its own workstation (its worktree);
# reading and organizing the viewport are fine, flipping it is not (bdo,
# 2026-06-20 — the workstation fence, done-line 0145). Deliberately a SUBSET
# of GIT_MUTATING: `worktree` (making/pruning workstations) and `tag`/`notes`
# are organizing, not flipping, so they are absent; `add`/`commit` are already
# denied everywhere by the fence registry. Enforced only in the primary tree —
# in a linked worktree these are a session editing its own bench, which is the
# whole point.
GIT_VIEWPORT_FLIP = {
    "checkout", "switch", "reset", "restore", "clean", "merge", "rebase",
    "cherry-pick", "revert", "am", "apply",
}  # always flips; `branch` and `stash` are conditional (see git_viewport_flip)
# `git branch` reads when it lists; it flips when it deletes, renames, forces,
# copies, or creates. These flags mark the flip; an explicit list flag a read.
GIT_BRANCH_FLIP_FLAGS = {"-d", "-D", "-m", "-M", "-f",
                         "--delete", "--move", "--force", "--copy"}
GIT_BRANCH_READ_FLAGS = {"-l", "--list", "-a", "--all", "-v", "-vv", "-r",
                         "--remotes", "--show-current", "--contains",
                         "--merged", "--no-merged", "--points-at"}
# `git stash list`/`show` read; bare `git stash`, push/pop/apply/drop/clear/save
# mutate the working tree.
GIT_STASH_READ_SUBCMDS = {"list", "show"}
# git's own global options that sit BEFORE the subcommand; the verb parser must
# skip them so `git -C <path> switch` is seen as `switch`, not `-C` (the -C
# bypass the independent review of done-line 0145 caught). `-C <path>` also
# RETARGETS the tree, so the guard evaluates that path, not cwd.
GIT_GLOBAL_OPTS_WITH_VALUE = {
    "-C", "-c", "--git-dir", "--work-tree", "--namespace",
    "--exec-path", "--super-prefix",
}
# PowerShell cmdlets are Verb-Noun shaped and local by default; these
# reach the network and stay visible to the watcher.
PS_NETWORK_CMDLETS = {"invoke-webrequest", "invoke-restmethod", "send-mailmessage"}
CMDLET_SHAPE = re.compile(r"[a-z]+-[a-z]+")


QUOTED_SPANS = (
    re.compile(r"@'[\s\S]*?'@"),                        # PS literal here-string
    re.compile(r'@"[\s\S]*?"@'),                        # PS expanding here-string
    re.compile(r"<<-?\s*'?(\w+)'?[\s\S]*?\n\s*\1\b"),   # POSIX heredoc
    re.compile(r"'[^']*'"),
    re.compile(r'"[^"]*"'),
)


def strip_quoted(command):
    """Remove quoted content so prose is never mistaken for commands.

    A commit message or PR body legitimately *mentions* forbidden
    verbs; only the command outside the quotes acts. Caught live: the
    shame hook read words of a here-string commit message as tool
    heads.
    """
    for pattern in QUOTED_SPANS:
        command = pattern.sub(" ", command)
    return command


def pushes_to_trunk(command):
    """True when a `git push` names main/master, in any refspec spelling."""
    for match in re.finditer(r"\bgit\s+push\b([^|;&\n]*)", command):
        for token in match.group(1).split():
            token = token.strip("'\"")
            if token in ("main", "master"):
                return True
            if re.fullmatch(r"[^:\s]*:(main|master)", token):
                return True
    return False


def external_bins(command):
    """The external tool heads a command reaches for, in order, deduped.

    Splits on shell joiners, takes each segment's first word, strips
    paths/.exe, and keeps what is neither local work nor plain local
    git. Heuristic by design — the watcher is a sensor, not a parser.
    """
    seen, found = set(), []
    for segment in re.split(r"[|;&\n{}()]+", strip_quoted(command)):
        words = segment.strip().split()
        if not words:
            continue
        head = words[0].strip("'\"").rsplit("/", 1)[-1].rsplit("\\", 1)[-1].lower()
        head = head[:-4] if head.endswith(".exe") else head
        if head in LOCAL_HEADS or not re.fullmatch(r"[a-z][a-z0-9._-]*", head):
            continue
        if CMDLET_SHAPE.fullmatch(head) and head not in PS_NETWORK_CMDLETS:
            continue  # a local cmdlet (caught live: Remove-Item shamed)
        if head == "git":
            sub = next((w for w in words[1:] if not w.startswith("-")), "")
            if sub not in GIT_NETWORK and sub not in GIT_MUTATING:
                continue
        if head not in seen:
            seen.add(head)
            found.append(head)
    return found


def record(entry):
    entry["ts"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        WATCH_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(WATCH_LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass  # the watcher never breaks the command it watches


def classify_intent(command):
    """The intent of a command via the one shared classifier (loop/tags.py,
    done-line 0032), or None if it cannot be reached — the watcher never
    breaks on the loop's absence (fail-open, the way the fence does)."""
    try:
        sys.path.insert(0, str(ROOT))
        from loop import tags
        return tags.classify(command)
    except Exception:  # noqa: BLE001 — any failure degrades to untagged, never crashes
        return None


def read_mode(session):
    """The security posture for this session at hook time (done-line 0096):
    ("normal", None) by default, ("train", <opening adm id>) under an active
    train admission. A pure fold over the truth log, read fresh every call —
    never a constant, never cached state.

    Fail-open to the STRICT default: any failure to read the fold degrades to
    "normal" (logged like the fence-load path), so a mode can only ever be in
    force when the log positively says so. train relaxes the guard, so its
    absence — or an unreadable fold — must never relax it."""
    try:
        sys.path.insert(0, str(ROOT))
        from loop.reconcile import Fold, active_mode
        return active_mode(Fold(AI_NATIVE_ROOT), session)
    except Exception as exc:  # noqa: BLE001 — any load failure degrades, none crashes
        record({"status": "degraded", "rule": "mode-load",
                "error": repr(exc), "session": session})
        return "normal", None


def _payload():
    try:
        # the harness pipes UTF-8; Windows' default stdin is cp1252 — read
        # bytes, or a command with any non-ASCII character slips the guard
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8", "replace"))
    except (json.JSONDecodeError, ValueError):
        return None
    if payload.get("tool_name") not in ("Bash", "PowerShell"):
        return None
    return payload


DENY_RULES = _deny_rules()  # compiled once per process, after record exists


TRUNK_MESSAGE = (
    "denied, firm: never push to main — push the session's claude/* "
    "branch and PR it through the pen (branch-ritual)."
)


VIEWPORT_FLIP_MESSAGE = (
    "denied, firm: this is bdo's VIEWPORT — the primary tree. A worker edits "
    "only its OWN workstation (its worktree); reading and organizing the "
    "viewport are fine, flipping it is not (bdo, 2026-06-20 — the workstation "
    "fence). Make a workstation and work there:\n"
    "  git worktree add -b claude/<slug> ../ontum-wt/<slug> origin/main\n"
    "To advance the viewport to the trunk, the one sanctioned move is the git "
    "pen (it never flips, only fast-forwards):\n"
    "  python .claude/skills/branch-ritual/git.py sync"
)


def _git_verb_and_args(tokens):
    """The subcommand and its args from the tokens after `git`, skipping git's
    global options so `git -C <path> switch` reads as `switch`, not `-C`. An
    option that takes a value (`-C <path>`, `-c <kv>`) consumes the next token;
    `--git-dir=...` and bare global flags (`--paginate`) consume one."""
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t in GIT_GLOBAL_OPTS_WITH_VALUE:
            i += 2  # option + its value
            continue
        if t.startswith("-"):
            i += 1  # `--git-dir=...`, `--paginate`, `-p`, ... — one token
            continue
        return t, tokens[i + 1:]
    return None, []


def git_viewport_flip(acting):
    """The flipping git verb in `acting`, or None.

    Reads (status/log/diff/show), workstation management (worktree), and the
    branded pen return None. `git branch` flips only when it deletes, renames,
    forces, copies, or creates (a list is a read); `git stash` flips unless it
    is `list`/`show`. Quoted prose is already stripped by the caller."""
    for seg in re.split(r"[|;&\n]+", acting):
        toks = seg.split()
        if "git" not in toks:
            continue
        verb, args = _git_verb_and_args(toks[toks.index("git") + 1:])
        if verb in GIT_VIEWPORT_FLIP:
            return verb
        if verb == "branch":
            if any(a in GIT_BRANCH_FLIP_FLAGS for a in args):
                return "branch"
            if any(a in GIT_BRANCH_READ_FLAGS for a in args):
                continue  # an explicit read form
            if any(not a.startswith("-") for a in args):
                return "branch"  # `git branch <newname> [start]` — creating
        if verb == "stash":
            first = next((a for a in args if not a.startswith("-")), "")
            if first in GIT_STASH_READ_SUBCMDS:
                continue  # `git stash list` / `show` — a read
            return "stash"  # bare / push / pop / apply / drop / clear / save
    return None


def dash_c_paths(acting):
    """The paths a command retargets git at via `git -C <path>` — the tree it
    actually touches, which may not be cwd (the -C bypass the review caught)."""
    paths = []
    for seg in re.split(r"[|;&\n]+", acting):
        toks = seg.split()
        for i, t in enumerate(toks):
            if t == "-C" and i + 1 < len(toks):
                paths.append(toks[i + 1].strip("'\""))
    return paths


def in_primary_viewport(path=None):
    """True when `path` (or cwd when None) is the repo's PRIMARY worktree —
    bdo's viewport — where the per-worktree git-dir equals the shared common
    dir. In a linked worktree the git-dir lives under .git/worktrees/<name> and
    differs. Fails OPEN (False) when git cannot answer: a guard never gates on
    a guess, and a non-repo path is not the viewport. (A determined retarget via
    `--git-dir=`/`--work-tree=` is not resolved here — a named residual of
    done-line 0145; `-C`, the natural form, is.)"""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--git-dir", "--git-common-dir"],
            capture_output=True, text=True, timeout=5,
            cwd=path or None,
        )
    except Exception:
        return False
    if out.returncode != 0:
        return False
    parts = out.stdout.split()
    if len(parts) < 2:
        return False
    try:
        return pathlib.Path(parts[0]).resolve() == pathlib.Path(parts[1]).resolve()
    except Exception:
        return False


def first_deny(acting):
    """The first deny rule this command would hit — the trunk carve-out
    (a push naming main deserves the firm line, not the generic git-push
    refusal the registry also carries), then the fence registry — or
    (None, None). One match, the way normal mode returns on the first hit;
    train reads the same first hit to name what it would have denied."""
    if pushes_to_trunk(acting):
        return "git-push-trunk", TRUNK_MESSAGE
    for rule, pattern, message in DENY_RULES:
        if re.search(pattern, acting):
            return rule, message
    return None, None


def surface_of(command):
    """The tool family a command reaches for (its first external bin, e.g.
    `git`), or the command head when nothing external is named — the surface
    a would-deny record is filed under."""
    bins = external_bins(command)
    if bins:
        return bins[0]
    words = strip_quoted(command).split()
    if not words:
        return ""
    head = words[0].strip("'\"").rsplit("/", 1)[-1].rsplit("\\", 1)[-1].lower()
    return head[:-4] if head.endswith(".exe") else head


def hook():
    payload = _payload()
    if payload is None:
        return 0
    command = (payload.get("tool_input") or {}).get("command") or ""
    session = payload.get("session_id") or ""
    # the SESSION's working dir, from the payload — NOT os.getcwd(): the harness
    # runs the hook from the project dir (the primary tree), so the process cwd
    # is the viewport for every session; only the payload knows where the
    # session actually stands (session_register.py trusts it the same way).
    session_cwd = payload.get("cwd") or os.getcwd()
    acting = strip_quoted(command)  # prose mentions a verb; only this acts

    # the posture in force for this session, read fresh from the truth log
    # (done-line 0096) — "normal" by default; train only ever relaxes
    posture, train_session = read_mode(session)
    training = posture == "train"

    rule, message = first_deny(acting)
    if rule is not None:
        if not training:
            # normal: the firm line — block, explain, exit 2 (unchanged)
            record({"status": "denied", "rule": rule, "command": command,
                    "session": session})
            print(message, file=sys.stderr)
            return 2
        # train: observe-everything / block-nothing — record what would have
        # been denied (no stderr, no exit 2) and fall through to the watch
        record({"status": "would-deny", "rule": rule, "mode": "train",
                "train_session": train_session, "surface": surface_of(command),
                "intent": classify_intent(command),
                "command": command, "session": session})

    # The workstation fence (done-line 0145): a tree/HEAD-flipping git verb is
    # forbidden in bdo's viewport (the primary tree) — a worker flips only its
    # own worktree. Context-dependent, so it lives here, not in the static fence
    # registry (like the trunk-push carve-out). Same train-mode courtesy as the
    # registry rules: observe and record, block nothing.
    flip = git_viewport_flip(acting)
    if flip is not None:
        # The tree this command touches: a `-C <path>` retargets git there, so
        # evaluate those paths; otherwise it acts on cwd. A flip hits the
        # viewport if ANY targeted tree is the primary — so `git -C <primary>`
        # from a worktree is caught, and `git -C <worktree>` from the viewport
        # is allowed (a worker editing its own bench by path).
        targets = dash_c_paths(acting)
        if targets:
            # -C paths are relative to where the session stands
            resolved = [p if os.path.isabs(p) else os.path.join(session_cwd, p)
                        for p in targets]
            hits_viewport = any(in_primary_viewport(p) for p in resolved)
        else:
            hits_viewport = in_primary_viewport(session_cwd)
        if hits_viewport:
            if not training:
                record({"status": "denied", "rule": "viewport-flip", "verb": flip,
                        "command": command, "session": session})
                print(VIEWPORT_FLIP_MESSAGE, file=sys.stderr)
                return 2
            record({"status": "would-deny", "rule": "viewport-flip",
                    "mode": "train", "train_session": train_session,
                    "verb": flip, "surface": "git",
                    "intent": classify_intent(command), "command": command,
                    "session": session})

    bins = external_bins(command)
    if bins:
        entry = {"status": "watched", "bins": bins,
                 "intent": classify_intent(command),
                 "command": command, "session": session}
        if training:  # ordinary watched calls under train carry the stamp too
            entry["mode"] = "train"
            entry["train_session"] = train_session
        record(entry)
    return 0


def _fold_counts(session):
    """Total and this-session use per tool, from the watch log."""
    total, in_session = {}, {}
    if WATCH_LOG.exists():
        for line in WATCH_LOG.read_text(encoding="utf-8").splitlines():
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue  # torn tail: it never happened
            if entry.get("status") != "watched":
                continue
            for bin_ in entry.get("bins", []):
                total[bin_] = total.get(bin_, 0) + 1
                if session and entry.get("session") == session:
                    in_session[bin_] = in_session.get(bin_, 0) + 1
    return total, in_session


def post():
    """PostToolUse: shame unbranded tool use into the context window."""
    payload = _payload()
    if payload is None:
        return 0
    command = (payload.get("tool_input") or {}).get("command") or ""
    bins = external_bins(command)
    if not bins:
        return 0
    session = payload.get("session_id") or ""
    total, in_session = _fold_counts(session)
    # The PreToolUse watcher already logged this very call, so a tool's
    # first use this session folds to 1. Beyond that it has been
    # surfaced — stay silent.
    fresh = [b for b in bins if in_session.get(b, 1) <= 1]
    if not fresh:
        return 0
    uses = ", ".join(f"`{b}` ×{total.get(b, 1)}" for b in fresh)
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": (
            f"[command_guard] unbranded tool use, on the audit record: {uses}. "
            "No branded wrapper exists for this yet — the only branded verb "
            "set is the PR pen (.claude/skills/branch-ritual/pr.py). The "
            "ritual prefers branded tools over the generic brand: if this "
            "tool keeps recurring, surface it to bdo and mint its wrapper "
            "(`python .claude/hooks/command_guard.py --report` for the fold). "
            "Surfaced, it is a judgment call; unsurfaced, it stays silent."
        ),
    }}))
    return 0


def report():
    """Fold the watch log, split by intent (done-line 0032). A raw *read*
    is by-design-raw (a session may always look) and is NOT a wrapper
    candidate; only a raw *mutation* nominates a wrapper. Before intent
    tags, reads inflated the count and `gh pr list` ×65 read as 'wrap gh' —
    the noise the organ census caught."""
    mutate, read, unknown = {}, {}, {}
    examples, denied, branded = {}, 0, 0
    if WATCH_LOG.exists():
        for line in WATCH_LOG.read_text(encoding="utf-8").splitlines():
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue  # torn tail: it never happened
            status = entry.get("status")
            if status == "denied":
                denied += 1
                continue
            if status == "branded":
                branded += 1  # an act that went through a pen — fine
                continue
            # re-derive intent for entries logged before tags existed
            intent = entry.get("intent") if "intent" in entry \
                else classify_intent(entry.get("command", ""))
            bucket = mutate if intent == "mutate" else read if intent == "read" else unknown
            for bin_ in entry.get("bins", []):
                bucket[bin_] = bucket.get(bin_, 0) + 1
                examples.setdefault(bin_, entry.get("command", "")[:100])

    def show(title, counts):
        if not counts:
            return
        print(title)
        for bin_, n in sorted(counts.items(), key=lambda kv: -kv[1]):
            print(f"  {bin_}: {n} raw call(s) — e.g. {examples[bin_]}")

    show("raw MUTATIONS — the next wrapper worth building is the heaviest here:", mutate)
    show("raw reads — by-design-raw (a session may look); not wrapper candidates:", read)
    show("unclassified — teach loop/tags.py a verb→intent line so these resolve:", unknown)

    if not (mutate or read or unknown):
        print(f"result: done — no unwrapped external use on record "
              f"({denied} denial(s), {branded} branded act(s))")
        return 0
    if mutate:
        top = max(mutate, key=lambda b: mutate[b])
        print(f"\nresult: report — {len(mutate)} raw-mutating tool(s); "
              f"`{top}` is the next wrapper worth building "
              f"({denied} denial(s), {branded} branded act(s))")
    else:
        print(f"\nresult: done — no raw mutations on record; the raw use is "
              f"reads (by-design) {'and unclassified verbs ' if unknown else ''}"
              f"({denied} denial(s), {branded} branded act(s))")
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    if "--report" in sys.argv[1:]:
        sys.exit(report())
    elif "--post" in sys.argv[1:]:
        sys.exit(post())
    else:
        sys.exit(hook())
