#!/usr/bin/env python3
"""The reflector pen (done-lines 0018, 0020): apply the drift, receipt every act.

The pure half lives in loop/reflect.py — it computes what each registered
surface should show (one issue per atom at the owner's stamp) and the
drift against what was last reflected. This pen is the only writer to the
outside: it applies exactly that drift through gh (the PR-pen pattern —
network reach lives here, never in loop/) and records each applied act
back onto the log with provenance, so re-running with no drift is a no-op
and a half-applied run resumes instead of double-acting.

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


def _apply_acts(root, surface, address, acts, by, run):
    """One act at a time, recording after each success — the record is
    what makes a crash-resume safe (the next run's drift no longer
    contains what landed). Returns (applied, error_or_None)."""
    applied = 0
    for act in acts:
        try:
            if act["act"] == "open":
                ref = run(["gh", "issue", "create", "--repo", address,
                           "--title", act["title"], "--body", act["body"]])
                ref = ref.splitlines()[-1].strip() if ref else ref
            else:
                ref = act.get("external_ref")
                if not ref:
                    return applied, (f"the open record for {act['atom_id']} "
                                     "carries no external_ref; close it by "
                                     "hand and record the act")
                close_args = ["gh", "issue", "close", str(ref),
                              "--comment", act["comment"]]
                if not str(ref).startswith("http"):
                    close_args += ["--repo", address]
                run(close_args)
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
    address = registered_surfaces(Fold(root))[surface]["address"]
    if not acts:
        print(f"result: done — no drift; {surface} mirrors the log")
        return 0
    applied, err = _apply_acts(root, surface, address, acts, by, run)
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
        address = surfaces[entry["surface"]]["address"]
        applied, err = _apply_acts(root, entry["surface"], address,
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
