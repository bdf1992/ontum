#!/usr/bin/env python3
"""The reflector pen (done-lines 0018, 0020): apply the drift, receipt every act.

The pure half lives in loop/reflect.py — it computes what each registered
surface should show (one issue per atom at the owner's stamp) and the
drift against what was last reflected. This pen is the only writer to the
outside: it applies exactly that drift through the surface kind's
translator (done-line 0030 — github-issues today, gh-backed like the PR
pen; network reach lives here, never in loop/) and records each applied
act back onto the log with provenance, so re-running with no drift is a
no-op and a half-applied run resumes instead of double-acting. A surface
whose admitted kind no translator speaks is refused, never guessed at.

Two verbs. `apply` is the deliberate hand: any registered surface, rule
or no rule. `auto` is the beat's verb (done-line 0020): only what the
admitted, enabled rules name — the Stop hook runs it after every turn,
so configured drift clears itself while configured-off drift never
leaves the machine (§10).

The mirror never becomes a write path (D-4): verdicts land through
loop.node judge; this pen only opens and closes the reflection.

  python .claude/skills/reflect/reflect.py apply --surface github-issues --by <who>
  python .claude/skills/reflect/reflect.py auto --by reflect-auto
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from loop.reconcile import Fold  # noqa: E402
from loop.reflect import (auto_plan, drift, record_reflection,  # noqa: E402
                          registered_surfaces)


def _run(args):
    proc = subprocess.run(args, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", cwd=ROOT)
    if proc.returncode != 0:
        raise RuntimeError(f"`{' '.join(args)}` failed: "
                           f"{(proc.stderr or proc.stdout).strip()}")
    return proc.stdout.strip()


# The shared-surface idempotence key (#547). The reflection 'open' ack lives
# on the LOCAL log, but the fleet runs many worktree sessions: a sibling forks
# from main BEFORE the ack exists, so each opens its own mirror and the
# union-merged log keeps one ack while GitHub keeps both issues. The local-log
# check is necessary but not sufficient; the surface itself is the cross-
# worktree shared truth. We stamp each minted mirror with a hidden key — the
# group's own per-kind idempotence identity (`mirror_key`, set by the fold so
# the surface-dedup and the log-dedup never disagree on "this group"): the atom
# VERSION (artifact_hash) for the stamp queue, so an in-place edit gets a fresh
# mirror instead of bdo judging a stale body; the report_id for owner-ask; the
# group label for divergences; "daily-digest" for the perennial digest. So a
# later pass can SEE its own group already mirrored and decline a second open.
# The marker is an HTML comment: invisible in rendered markdown, exact in the
# body text gh returns.
_MIRROR_KEY_RE = re.compile(r"<!--\s*ontum-mirror-key:\s*(\S+)\s*-->")


def _mirror_marker(key):
    return f"\n\n<!-- ontum-mirror-key: {key} -->"


def _open_mirror_keys(address, run):
    """The mirror keys already live as OPEN issues on the surface — the shared
    truth a second worktree must dedupe against (#547). Reads EVERY open issue's
    body for the hidden key, paginating to EXHAUSTION (`gh api --paginate`) so
    the guard can never silently miss a mirror past a finite page cap — the
    capped `gh issue list --limit 500` it replaces would re-mint the #547
    duplicate the moment a repo crosses 500 open issues (finding 1), the bug
    going silent because the read still "succeeded". The issues endpoint also
    returns pull requests, so PRs are filtered out (`select(.pull_request|not)`).
    One read per apply-run (only when an open act is pending), so the common
    no-drift beat pays nothing. A read failure raises (fail-loud): minting blind
    against an unread surface is the double-fire bug, never a default."""
    raw = run(["gh", "api", "--paginate",
               f"repos/{address}/issues?state=open&per_page=100",
               "--jq", ".[] | select(.pull_request | not) | [.html_url, .body] "
                       "| @json"])
    keys = {}
    # split on "\n" only, NOT str.splitlines(): `@json` escapes the standard
    # JSON control chars (\n, \r, \t) but leaves U+2028/U+2029/U+0085 RAW in a
    # body — splitlines() would treat those as line breaks and tear one issue's
    # JSON record in two, crashing the parse and refusing ALL mirroring on
    # arbitrary issue text. jq separates records with a literal newline.
    for line in (raw or "").split("\n"):
        line = line.strip()
        if not line:
            continue
        url, body = json.loads(line)  # one JSON [url, body] pair per open issue
        m = _MIRROR_KEY_RE.search(body or "")
        if m:
            # first open issue per key wins; a human-closed mirror is gone from
            # this set, so the open-only owner-ask mirror still never re-opens
            # what its local ack already recorded
            keys.setdefault(m.group(1), url)
    return keys


def _gh_open(address, act, run):
    """github-issues: an open act is a created issue; the ref is its URL. The
    body carries the hidden mirror-key (#547) — the group's own per-kind
    `mirror_key` — so a sibling worktree's later pass can recognise this group
    is already mirrored and not mint a duplicate."""
    body = act["body"] + _mirror_marker(act["mirror_key"])
    ref = run(["gh", "issue", "create", "--repo", address,
               "--title", act["title"], "--body", body])
    return ref.splitlines()[-1].strip() if ref else ref


def _gh_edit(address, act, run):
    """github-issues: an edit act updates the one live issue's body in place —
    the daily-digest kind is perennial (it re-renders, never re-opens), so its
    issue is edited, not closed-and-reopened (done-line 0166). The hidden
    mirror-key is re-appended (#547): an edit replaces the whole body, so the
    marker must be re-stamped or a later open-dedup could no longer recognise
    this perennial issue and would mint a duplicate."""
    ref = act["external_ref"]
    body = act["body"] + _mirror_marker(act["mirror_key"])
    edit_args = ["gh", "issue", "edit", str(ref), "--body", body]
    if not str(ref).startswith("http"):
        edit_args += ["--repo", address]
    run(edit_args)
    return ref


def _gh_close(address, act, run):
    ref = act["external_ref"]
    close_args = ["gh", "issue", "close", str(ref),
                  "--comment", act["comment"]]
    if not str(ref).startswith("http"):
        close_args += ["--repo", address]
    run(close_args)
    return ref


# The translator table (done-line 0030): surface kind -> how each act
# speaks there. Keyed to exactly loop.reflect.SURFACE_KINDS (pinned by
# test) — a kind off this table is refused, never guessed at with
# gh-shaped verbs. A new surface kind lands as a new entry here plus
# its SURFACE_KINDS row, its own stamped increment.
TRANSLATORS = {
    "github-issues": {"open": _gh_open, "edit": _gh_edit, "close": _gh_close},
}


def _apply_acts(root, surface, adm, acts, by, run):
    """One act at a time, through the surface kind's translator,
    recording after each success — the record is what makes a
    crash-resume safe (the next run's drift no longer contains what
    landed). Returns (applied, error_or_None)."""
    translator = TRANSLATORS.get(adm.get("kind"))
    if translator is None:
        return 0, (f"surface {surface!r} is admitted with kind "
                   f"{adm.get('kind')!r}, which no translator speaks "
                   f"(known: {', '.join(sorted(TRANSLATORS))}); a new kind "
                   "is a new translator in this pen — its own stamped "
                   "increment, not a gh-shaped guess")
    address = adm["address"]
    # Read the surface's already-open mirrors ONCE, before any open (#547): the
    # cross-worktree idempotence guard. Only when an open is actually pending —
    # the common no-drift / close-only beat pays nothing. A read failure is
    # surfaced, never swallowed: minting blind is exactly the double-fire bug.
    open_keys = {}
    if any(a["act"] == "open" for a in acts):
        try:
            open_keys = _open_mirror_keys(address, run)
        except (RuntimeError, ValueError) as err:
            return 0, (f"could not read open mirrors on {surface!r} to dedupe "
                       f"before minting (refusing to open blind — that is the "
                       f"#547 double-fire): {err}")
    applied = 0
    for act in acts:
        try:
            if act["act"] == "open" and act["mirror_key"] in open_keys:
                # this group is ALREADY mirrored to an open issue on the surface
                # (a sibling worktree opened it). Record the ack against the
                # existing issue so the local log catches up, and mint nothing.
                # The match is on the per-kind mirror_key (the atom VERSION for
                # the stamp queue), so an in-place-edited atom's NEW version is
                # not deduped against its own stale issue (#547 finding 2).
                ref = open_keys[act["mirror_key"]]
                record_reflection(root, surface, act["atom_id"],
                                  act["artifact_hash"], "open", ref, by)
                print(f"skip-open (already mirrored): {act['atom_id']} -> {ref}")
                applied += 1
                continue
            if act["act"] != "open" and not act.get("external_ref"):
                return applied, (f"the open record for {act['atom_id']} "
                                 "carries no external_ref; close it by "
                                 "hand and record the act")
            ref = translator[act["act"]](address, act, run)
        except RuntimeError as err:
            return applied, str(err)
        record_reflection(root, surface, act["atom_id"], act["artifact_hash"],
                          act["act"], ref, by)
        print(f"{act['act']}: {act['atom_id']} -> {ref}")
        applied += 1
    return applied, None


def apply(root, surface, by, run=_run):
    """The deliberate hand: apply a registered surface's full drift."""
    try:
        acts = drift(root, surface)
    except ValueError as err:
        print(f"result: needs-you — {err}")
        return 2
    adm = registered_surfaces(Fold(root))[surface]
    if not acts:
        print(f"result: done — no drift; {surface} mirrors the log")
        return 0
    applied, err = _apply_acts(root, surface, adm, acts, by, run)
    if err:
        print(f"applied {applied} of {len(acts)} act(s), then: {err}")
        print("result: needs-you — the applied acts are on the log; "
              "re-run to resume from the rest")
        return 2
    print(f"result: report — {applied} act(s) applied to {surface}; "
          f"each is receipted on the log")
    return 0


def auto(root, by, run=_run):
    """The beat's verb (done-line 0020): apply only what the admitted,
    enabled rules name. Quiet no-op otherwise — this fires after every
    turn and must not spam, block, or reach where no rule points."""
    plan = auto_plan(root)
    if not plan:
        print("result: done — nothing to auto-apply (no enabled rule has drift)")
        return 0
    surfaces = registered_surfaces(Fold(root))
    total = 0
    for entry in plan:
        applied, err = _apply_acts(root, entry["surface"],
                                   surfaces[entry["surface"]],
                                   entry["acts"], by, run)
        total += applied
        if err:
            print(f"applied {applied} act(s) to {entry['surface']}, then: {err}")
            print("result: needs-you — the applied acts are on the log; "
                  "the next beat resumes")
            return 2
    names = ", ".join(e["surface"] for e in plan)
    print(f"result: report — auto-applied {total} act(s) ({names}); "
          f"each is receipted on the log")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("apply", help="apply a registered surface's drift, by hand")
    a.add_argument("--root", type=Path, default=ROOT / ".ai-native")
    a.add_argument("--surface", required=True)
    a.add_argument("--by", required=True,
                   help="who applies (every reflected act is signed)")
    au = sub.add_parser("auto", help="the beat: apply only what enabled rules name")
    au.add_argument("--root", type=Path, default=ROOT / ".ai-native")
    au.add_argument("--by", default="reflect-auto",
                    help="the beat's signature on reflected acts")
    args = ap.parse_args(argv)
    if args.cmd == "auto":
        return auto(args.root, args.by)
    return apply(args.root, args.surface, args.by)


if __name__ == "__main__":
    sys.exit(main())
