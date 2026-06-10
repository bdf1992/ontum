#!/usr/bin/env python3
"""The reflector pen (done-line 0018): apply the drift, receipt every act.

The pure half lives in loop/reflect.py — it computes what each registered
surface should show (one issue per atom at the owner's stamp) and the
drift against what was last reflected. This pen is the only writer to the
outside: it applies exactly that drift through gh (the PR-pen pattern —
network reach lives here, never in loop/) and records each applied act
back onto the log with provenance, so re-running with no drift is a no-op
and a half-applied run resumes instead of double-acting.

The mirror never becomes a write path (D-4): verdicts land through
loop.node judge; this pen only opens and closes the reflection.

  python .claude/skills/reflect/reflect.py apply --surface github-issues --by <who>
"""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from loop.reconcile import Fold  # noqa: E402
from loop.reflect import drift, record_reflection, registered_surfaces  # noqa: E402


def _run(args):
    proc = subprocess.run(args, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", cwd=ROOT)
    if proc.returncode != 0:
        raise RuntimeError(f"`{' '.join(args)}` failed: "
                           f"{(proc.stderr or proc.stdout).strip()}")
    return proc.stdout.strip()


def apply(root, surface, by, run=_run):
    """Apply the drift, one act at a time, recording after each success —
    the record is what makes a crash-resume safe (the next run's drift
    no longer contains what landed)."""
    try:
        acts = drift(root, surface)
    except ValueError as err:
        print(f"result: needs-you — {err}")
        return 2
    address = registered_surfaces(Fold(root))[surface]["address"]
    if not acts:
        print(f"result: done — no drift; {surface} mirrors the log")
        return 0
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
                    print(f"result: needs-you — the open record for "
                          f"{act['atom_id']} carries no external_ref; "
                          f"close it by hand and record the act")
                    return 2
                close_args = ["gh", "issue", "close", ref,
                              "--comment", act["comment"]]
                if not str(ref).startswith("http"):
                    close_args += ["--repo", address]
                run(close_args)
        except RuntimeError as err:
            print(f"applied {applied} of {len(acts)} act(s), then: {err}")
            print("result: needs-you — the applied acts are on the log; "
                  "re-run to resume from the rest")
            return 2
        record_reflection(root, surface, act["atom_id"], act["artifact_hash"],
                          act["act"], ref, by)
        print(f"{act['act']}: {act['atom_id']} -> {ref}")
        applied += 1
    print(f"result: report — {applied} act(s) applied to {surface}; "
          f"each is receipted on the log")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("apply", help="apply the drift to a registered surface")
    a.add_argument("--root", type=Path, default=ROOT / ".ai-native")
    a.add_argument("--surface", required=True)
    a.add_argument("--by", required=True,
                   help="who applies (every reflected act is signed)")
    args = ap.parse_args(argv)
    return apply(args.root, args.surface, args.by)


if __name__ == "__main__":
    sys.exit(main())
