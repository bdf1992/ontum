#!/usr/bin/env python3
"""The tag pool (done-line 0032): governed vocabulary for what tools do.

The part census found the watcher could not tell a read from a mutation,
so its `--report` counted 65 raw `gh` calls — all of them reads `gh pr
list` style, by-design-raw — and nominated `gh` as the next wrapper to
build. Noise read as signal. bdo's fix, pushed upstream to the write
seam: stop inferring intent from raw capture; have the tool emit a typed
tag from a governed pool, so the record is data-rich instead of a blob
the reader must guess at.

This module is the pool and the one classifier both seams share (I-4):

  dimension   a typed axis of meaning. One today: `intent` — does this
              action change state (`mutate`) or only observe it (`read`).
  core        the small closed vocabulary of a dimension, in code (like
              reflect.RULE_KINDS). Known, stable, the spine.
  proposed    a value outside the pool, *accepted and recorded* but
              flagged as drift — never blocked. Promotable by an admitted
              `tag` record (`--by`). Mirrors the language/ PROPOSED gate:
              loading is not stamping (bdo's chosen governance).

The classifier `classify()` maps a raw command to a core intent, or to
None when it does not yet know the verb — an honest "teach me", surfaced,
never a silent guess. The watcher tags every watched command with it; the
git pen carries it for its own verbs and refuses a declaration that lies
about what the verb does.

Stdlib only. Read-only except `admit`. Ends with done | report | needs-you.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT, Fold, append_line, now_ts, short_hash

# ----------------------------------------------------------------- the schema
# A dimension's core is the closed vocabulary, defined here (the spine);
# admitted `tag` records extend it (the proposed→admitted path). One
# dimension today; `surface` and `arc` are named in done-line 0032 as the
# next slices, not pre-built.
DIMENSIONS = {
    "intent": {
        "core": ("read", "mutate"),
        "gloss": "does this action change state (mutate) or only observe it (read)",
    },
}

READ, MUTATE = "read", "mutate"

# ------------------------------------------------------------- the classifier
# The one place the read/mutate knowledge lives. The watcher imports it to
# tag what it watches; the git pen imports it to know its own verbs. A verb
# the maps do not name returns None — unclassified, surfaced, not guessed.

_GIT_MUTATE = {
    "add", "commit", "checkout", "switch", "branch", "merge", "rebase",
    "reset", "revert", "cherry-pick", "stash", "tag", "worktree", "clean",
    "restore", "rm", "mv", "am", "apply", "update-ref", "update-index",
    "gc", "prune", "notes", "replace", "commit-tree", "push",
}
_GIT_READ = {
    "status", "log", "diff", "show", "fetch", "pull", "ls-remote",
    "rev-parse", "rev-list", "describe", "blame", "cat-file", "ls-files",
    "shortlog", "reflog", "remote", "config", "for-each-ref", "merge-base",
}
_GH_MUTATE = {
    "create", "edit", "merge", "close", "reopen", "delete", "ready",
    "unready", "review", "comment", "add", "remove", "set", "rename",
    "lock", "unlock", "pin", "unpin", "transfer", "develop", "restore",
    "integrate",
}
_GH_READ = {"list", "view", "status", "diff", "checks", "get"}
_CURL_MUTATE_METHODS = {"POST", "PUT", "DELETE", "PATCH"}

# The general shell vocabulary, keyed on the command head (the verb is the
# tool itself, not a subcommand). The part census caught the watcher's
# unclassified tail — `uniq`, `cut`, `tr`, `sleep`, `cp` … read as nothing —
# and the fix is the same as for git/gh: name what the verb does so the
# report carries signal, not a blob. Coarse and head-first by design (like
# `git reset`→mutate regardless of flags): a stream tool's common case is to
# observe (write to stdout), so `sed`/`awk` read here; the rare `sed -i` is
# an accepted imprecision, not an enforcement seam. What stays OUT of both
# sets is honest None: interpreters and control words (`python`, `node`,
# `bash`, `for`, `until`, `command`) run arbitrary work that is neither
# cleanly read nor mutate — guessing there would be the silent default this
# module exists to refuse.
_SHELL_READ = {
    # inspect / observe — change no state
    "ls", "dir", "cat", "bat", "head", "tail", "less", "more",
    "grep", "egrep", "fgrep", "rg", "ag", "ack",
    "find", "fd", "locate", "which", "where", "whereis", "type",
    "wc", "sort", "uniq", "cut", "tr", "nl", "tac", "rev", "column",
    "fold", "paste", "join", "comm", "diff", "cmp",
    "sed", "awk", "jq", "yq", "xmllint",
    "stat", "file", "du", "df",
    "basename", "dirname", "realpath", "readlink", "pwd", "whoami",
    "hostname", "uname", "id", "date", "cal", "uptime",
    "echo", "printf", "yes", "seq", "sleep", "true", "false", "test",
    "expr", "printenv",
    "md5sum", "sha1sum", "sha256sum", "shasum", "cksum", "base64",
    "od", "xxd", "hexdump", "strings",
}
_SHELL_MUTATE = {
    # change the filesystem / on-disk state
    "cp", "mv", "rm", "rmdir", "mkdir", "touch", "ln", "link", "unlink",
    "chmod", "chown", "chgrp", "tee", "dd", "truncate", "shred",
    "install", "mktemp", "rsync", "patch",
}


def _first_verb(tokens):
    """The first non-flag token after the head — a tool's subcommand."""
    return next((t.strip("'\"") for t in tokens if not t.startswith("-")), "")


def classify(command):
    """The intent of a raw command: 'read', 'mutate', or None (unknown).

    Pure and head-first, like the watcher's sensor: it reads the tool and
    its verb, never executes. None is information — an honest gap to teach,
    surfaced by status(), not a silent default."""
    words = (command or "").strip().split()
    if not words:
        return None
    head = words[0].rsplit("/", 1)[-1].rsplit("\\", 1)[-1].lower()
    head = head[:-4] if head.endswith(".exe") else head
    rest = words[1:]
    if head == "git":
        verb = _first_verb(rest)
        if verb in _GIT_MUTATE:
            return MUTATE
        if verb in _GIT_READ:
            return READ
        return None
    if head == "gh":
        # gh nests: `gh pr list` — the action verb is the last known word.
        verbs = [t for t in rest if not t.startswith("-")]
        if "api" in verbs:
            # `gh api` is a raw GitHub call: GET by default (a read), a write
            # when a method or a field flag is present (gh's curl-shaped seam).
            upper = command.upper()
            if any(f"-X {m}" in upper or f"-X{m}" in upper or f"--METHOD {m}" in upper
                   for m in _CURL_MUTATE_METHODS):
                return MUTATE
            if re.search(r"(?<!\S)(-f|-F|--field|--raw-field|--input)\b", command):
                return MUTATE
            return READ
        for v in reversed(verbs):
            if v in _GH_MUTATE:
                return MUTATE
            if v in _GH_READ:
                return READ
        return None
    if head in ("curl", "wget"):
        upper = command.upper()
        for m in _CURL_MUTATE_METHODS:
            if f"-X {m}" in upper or f"--REQUEST {m}" in upper:
                return MUTATE
        if re.search(r"(?<!-)\B(-d|--data|-F|--form|-T|--upload-file)\b", command) \
                and " -G" not in command and " --get" not in command:
            return MUTATE
        return READ
    if head in _SHELL_MUTATE:
        return MUTATE
    if head in _SHELL_READ:
        return READ
    return None


def verb_intent(tool, verb):
    """The intent of a known pen verb — the classifier's view, addressed
    by (tool, verb) instead of a raw string. None when unknown."""
    return classify(f"{tool} {verb}")


# --------------------------------------------------------------- the pool fold

def admitted_values(fold):
    """Extra values admitted per dimension (beyond core): latest `tag`
    admission per (dimension, value) wins; a withdrawn one is dropped.
    The proposed→admitted promotion path, on the log (I-8)."""
    out = {}
    for adm in fold.admissions:
        if adm.get("type") != "tag":
            continue
        dim, val = adm.get("dimension"), adm.get("value")
        if not dim or not val:
            continue
        if adm.get("withdrawn"):
            out.get(dim, set()).discard(val)
        else:
            out.setdefault(dim, set()).add(val)
    return out


def pool(fold, dimension):
    """The full accepted vocabulary of a dimension: core plus admitted."""
    core = set(DIMENSIONS.get(dimension, {}).get("core", ()))
    return core | admitted_values(fold).get(dimension, set())


def status_of(fold, dimension, value):
    """Where a value stands: core (spine), admitted (promoted), or
    proposed (seen but not yet stamped — drift, not error)."""
    if value in DIMENSIONS.get(dimension, {}).get("core", ()):
        return "core"
    if value in admitted_values(fold).get(dimension, set()):
        return "admitted"
    return "proposed"


def admit_tag(root, dimension, value, by, withdrawn=False):
    """Promote a proposed value into the pool — or withdraw it (superseding,
    never erasing). Signed `--by`; an unknown dimension is refused."""
    adm = {
        "id": "adm." + short_hash("tag", dimension, value, str(withdrawn),
                                  str(by), now_ts()),
        "type": "tag",
        "dimension": dimension,
        "value": value,
        "withdrawn": bool(withdrawn),
        "by": by,
        "ts": now_ts(),
    }
    append_line(root / "log" / "admissions.jsonl", adm)
    return adm


# ------------------------------------------------------- the shared sensor log
# The watch log is the watcher's sensor trace (gitignored, deletable). The
# pen records its own branded acts here too, so the report can tell an act
# that went through a pen from a raw one. The path mirrors command_guard's
# deliberately — robustness over DRY: the guard must resolve its log even
# if loop fails to import, so it keeps its own copy of this address.

def watch_log(root):
    env = os.environ.get("ONTUM_TOOL_WATCH_LOG")
    return Path(env) if env else Path(root) / ".ai-native" / "log" / "tool-use.jsonl"


def note(root, **fields):
    """Append one tagged act to the sensor log, best-effort — a recorder
    that breaks the act it records is worse than no record (the watcher's
    own law). Stamps ts; never raises."""
    fields["ts"] = now_ts()
    try:
        path = watch_log(root)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(fields, ensure_ascii=False) + "\n")
    except OSError:
        pass


def _read_sensor(root):
    path = watch_log(root)
    if not path.exists():
        return []
    out = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    for line in lines:
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue  # torn tail: it never happened
    return out


# ----------------------------------------------------------------- the surface

def status(root):
    """Read-only: the pool per dimension, and the drift the sensor shows —
    proposed values awaiting a stamp, and commands the classifier cannot
    yet name (the honest gaps to teach)."""
    fold = Fold(root)
    for dim, spec in DIMENSIONS.items():
        core = ", ".join(spec["core"])
        extra = sorted(admitted_values(fold).get(dim, set()))
        line = f"dimension: {dim} — core {{{core}}}"
        if extra:
            line += f"; admitted {{{', '.join(extra)}}}"
        print(f"{line}\n  ({spec['gloss']})")

    sensor = _read_sensor(root)
    proposed, unclassified = {}, 0
    for e in sensor:
        intent = e.get("intent")
        if intent is None and e.get("status") == "watched":
            unclassified += 1
        elif intent is not None and status_of(fold, "intent", intent) == "proposed":
            proposed[intent] = proposed.get(intent, 0) + 1

    if proposed:
        print("\nproposed intent values (accepted, awaiting your stamp):")
        for val, n in sorted(proposed.items(), key=lambda kv: -kv[1]):
            print(f"  {val} ×{n} — admit: python -m loop.tags admit "
                  f"--dimension intent --value {val} --by bdo")
    if unclassified:
        print(f"\nunclassified: {unclassified} watched command(s) the classifier "
              "does not name yet — teach it in loop/tags.py (a verb→intent line)")

    if proposed or unclassified:
        print("\nresult: report — the pool holds; drift above is yours to "
              "stamp or teach")
    else:
        print("\nresult: done — every recorded intent is in the pool; no drift")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd")

    st = sub.add_parser("status", help="the pool and its drift, read-only")
    st.add_argument("--root", type=Path, default=DEFAULT_ROOT)

    ad = sub.add_parser("admit", help="promote (or --withdraw) a value into a dimension's pool")
    ad.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ad.add_argument("--dimension", required=True, help=f"one of: {', '.join(DIMENSIONS)}")
    ad.add_argument("--value", required=True)
    ad.add_argument("--withdraw", dest="withdrawn", action="store_true",
                    help="supersede a prior admission (latest wins, I-8)")
    ad.add_argument("--by", required=True, help="who admits it (the pool is signed, never self-set)")

    args = ap.parse_args(argv)
    if args.cmd == "admit":
        if args.dimension not in DIMENSIONS:
            print(f"result: needs-you — unknown dimension {args.dimension!r}; "
                  f"the schema holds: {', '.join(DIMENSIONS)} (a new dimension "
                  "is a new slice, its own stamped increment)")
            return 2
        adm = admit_tag(args.root, args.dimension, args.value, args.by,
                        withdrawn=args.withdrawn)
        verb = "withdrew" if args.withdrawn else "admitted"
        print(f"result: report — {adm['id']}: {verb} {args.dimension}="
              f"{args.value} (by {args.by})")
        return 0
    root = args.root if args.cmd == "status" else DEFAULT_ROOT
    return status(root)


if __name__ == "__main__":
    sys.exit(main())
