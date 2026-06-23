#!/usr/bin/env python3
"""The noise make-over's actuator pen — the one network-reaching half.

`loop/reconcile_noise.py` is the pure fold: it reads the open noise surfaces
against the log, splits them into PROVEN-resolved (silenceable) and unresolved
(escalating) through the §10 teeth, and synthesizes the useful sound (one digest
line). It reaches nothing — loop/ is network-free.

This pen is the actuator. It:
  1. lists the OPEN GitHub issues (`gh issue list`) and hands them to the fold so
     each reading is matched to its mirror issue number;
  2. for each reading the fence AUTHORIZES (cooling only; default-inert until bdo
     stamps the fence), SILENCES it on the record —
       - an owner-ask through `reflect.discharge_owner_ask` (which RE-VERIFIES the
         cite teeth — a discharge with no real cite is refused at the pen too),
       - and closes its mirror issue through the **issue pen** (never raw `gh`);
       - a gate-tracker closes its tracker issue through the issue pen, citing the
         settled receipt as the provenance;
  3. prints the useful sound and the named escalations (#628).

Default is DRY-RUN: it shows the plan and reaches nothing. `--apply` acts — and
acts only on what the fence authorizes, so with no fence drawn it silences
nothing (the standing permission is bdo's). Outward reach lives here; the teeth
live in the fold AND in the issue pen / discharge — neither can be lied to.

Usage:
  python .claude/skills/noise-makeover/makeover.py                 dry-run (the plan)
  python .claude/skills/noise-makeover/makeover.py --apply --by claude
"""

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(os.environ.get("ONTUM_REPO_ROOT") or Path(__file__).resolve().parents[3])
sys.path.insert(0, str(ROOT))

from loop import reconcile_noise, reflect  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "issue_pen", ROOT / ".claude" / "skills" / "issue" / "issue.py")
issue_pen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(issue_pen)

AI_ROOT = ROOT / ".ai-native"


def gh(args):
    return subprocess.run(["gh"] + args, capture_output=True, text=True,
                          cwd=str(ROOT), timeout=120)


def list_open_issues(gh_run=None):
    """The OPEN issues, as [{number, title}] — read-only. A failure here is not
    fatal: the fold still silences the log side (a discharge) of what it proves
    resolved; only the mirror-close needs the issue number."""
    gh_run = gh_run or gh
    proc = gh_run(["issue", "list", "--state", "open", "--limit", "500",
                   "--json", "number,title"])
    if proc.returncode != 0:
        return [], (proc.stderr or proc.stdout or "").strip()
    try:
        return json.loads(proc.stdout or "[]"), None
    except json.JSONDecodeError as e:
        return [], f"could not parse gh output: {e}"


def silence_owner_ask(reading, by, apply, repo=None):
    """Discharge the ask on the record (re-verifies the cite teeth), then close
    its mirror issue through the issue pen. Returns a result dict."""
    if not apply:
        return {"act": "would-discharge+close", "subject": reading["subject"],
                "issue": reading.get("issue")}
    adm, err = reflect.discharge_owner_ask(
        AI_ROOT, reading["subject"], [reading["cite"]],
        reason=reading["reason"], by=by)
    if err:  # the teeth bit at the pen too — never closes what it cannot discharge
        return {"act": "REFUSED", "subject": reading["subject"], "error": err}
    out = {"act": "discharged", "subject": reading["subject"], "adm": adm["id"]}
    if reading.get("issue"):
        try:
            issue_pen.do_close(reading["issue"], reading["reason"], by, repo=repo)
            out["closed_issue"] = reading["issue"]
        except Exception as e:
            out["close_error"] = str(e)
    return out


def silence_gate_tracker(reading, by, apply, repo=None):
    """Close the tracker issue through the issue pen, citing the settled receipt.
    Idempotent: the fold only marks it silenceable when the live bytes carry a
    settled verdict, regardless of which process produced it."""
    if not apply:
        return {"act": "would-close", "subject": reading["subject"],
                "issue": reading.get("issue")}
    if not reading.get("issue"):
        return {"act": "no-mirror", "subject": reading["subject"],
                "note": "settled on the log; no open tracker issue to close"}
    reason = (f"settled on the log: {reading.get('node')} -> {reading.get('verdict')} "
              f"({reading['cite']}). Closed by the noise make-over — the tracker's "
              "producing process did not, but the verdict did land.")
    try:
        issue_pen.do_close(reading["issue"], reason, by, repo=repo)
        return {"act": "closed", "subject": reading["subject"],
                "closed_issue": reading["issue"]}
    except Exception as e:
        return {"act": "close-error", "subject": reading["subject"], "error": str(e)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true",
                    help="act (default dry-run); acts only on what the fence authorizes")
    ap.add_argument("--by", default="noise-makeover", help="who runs it (the signer)")
    ap.add_argument("--repo", default=None, help="owner/repo (default inferred)")
    ns = ap.parse_args(argv)

    open_issues, err = list_open_issues()
    if err:
        print(f"  (could not list open issues: {err} — silencing the log side only)")

    p = reconcile_noise.plan(AI_ROOT, open_issues=open_issues)
    print(f"**{p['digest_line']}**\n")

    if p["fence"] is None and not ns.apply:
        print("fence — none drawn; this is a dry-run and the make-over is inert. "
              "bdo draws it: python -m loop.reconcile_noise admit-fence --by bdo\n")

    results = []
    for r in p["authorized"]:
        if r["kind"] == "owner-ask":
            results.append(silence_owner_ask(r, ns.by, ns.apply, ns.repo))
        else:
            results.append(silence_gate_tracker(r, ns.by, ns.apply, ns.repo))

    for res in results:
        print(f"  {res}")

    held, esc = p.get("held_for_cap", []), p.get("escalating", [])
    if held:
        print(f"\n  {len(held)} proven-resolved item(s) held (over the fence cap, or "
              "no fence) — proposed, not silenced.")
    if esc:
        print(f"  {len(esc)} still need you (escalating to a named conclusion, #628): "
              + ", ".join((r.get("report_id") or r["subject"]) for r in esc[:12]))

    if not ns.apply:
        print("\nresult: report — dry-run; nothing reached. Re-run with --apply --by "
              "<who> to silence what the fence authorizes.")
        return 0
    acted = sum(1 for r in results if r.get("act") in ("discharged", "closed"))
    print(f"\nresult: report — silenced {acted} proven-resolved item(s) through the "
          f"governed pens; {len(esc)} escalated (#628).")
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
