#!/usr/bin/env python3
"""The noise make-over (epic.owner-harness; #628): noise made over into signal.

bdo, 2026-06-22: *"make more beautiful elaborate fold and large inferences to
make over more useful sounds and permission to silence noise by upgrading the
system producing it."* The bundle is `.ai-native/proposals/noise-makeover.proposal.md`.

Two owner surfaces have an automated OPEN path and a manual / in-process-only
CLOSE path, so they only ever accrete:

- **owner-ask mirror issues** (`loop/owner_asks.py` → `reflect.owner_ask_drift`):
  one per report's `needs-you` section. Open-only — a free-text ask carries no
  log-backed "answered" signal, so the mirror never closes itself.
- **gate-run tracker issues** (`.claude/skills/gate/gate.py`): one per headless
  run, opened at the process's *birth*. It closes only from inside the producing
  process, so a process that dies after the verdict lands strands its tracker
  open though the work is settled on the log.

This module is the **make-over fold** (read-only, stdlib, no network): over the
live log it computes, per open noise subject, a RESOLUTION reading —

  - an **owner-ask group** is resolved when an arc it asks bdo to confirm now
    carries an `arc_confirmed` admission (the cite);
  - a **gate-tracker** is resolved when its atom's *current bytes* carry a
    settled value-gate / value-confirm verdict on `receipts.jsonl` (the cite) —
    idempotent: the verdict closes the tracker regardless of which process (or
    none) produced it.

The emit is the **useful sound**: one synthesized digest line, plus a plan of
close-with-reason acts the actuator pen applies through the issue pen and
`reflect.discharge_owner_ask` (never raw `gh`). The §10 teeth: a close with no
provable resolution on the log is REFUSED — it stays open and ESCALATES to a
named conclusion (#628). The teeth hold over inference output too (`transform_
unresolved`): a hallucinated cite is refused exactly like a fabricated one.

The **standing permission** to act on its own is bdo's: a `noise_silence_fence`
admission (the disposer-fence shape, done-line 0091), DEFAULT-INERT until he
stamps it `--by bdo`. Until then the make-over reads and proposes only. Cooling
(silencing proven-resolved noise) is the allowed direction; anything unproven
escalates, never auto-closes. The loop executes bdo's standing stamp; it never
signs its own line (the merge-node / confirm-arc shape).

Outward reach — the `gh` close, the live model completion — lives only in the
actuator pen and the gateway pen, never here (loop/'s no-network law). CLI ends
with a clear result (D-6): done | report | needs-you.

CLI:
  python -m loop.reconcile_noise                 the make-over, read-only
  python -m loop.reconcile_noise --json          the raw dataset (machine-readable)
  python -m loop.reconcile_noise admit-fence --max-closes 10 --by bdo   bdo draws the fence
  python -m loop.reconcile_noise admit-fence --off --by bdo             bdo withdraws it
"""

import argparse
import re
import sys
from pathlib import Path

from loop.reconcile import (DEFAULT_ROOT, Fold, append_line, arc_confirmation,
                            canon, load_atoms, now_ts, short_hash)
from loop.owner_asks import owner_ask_groups
from loop.reflect import record_on_log
from loop import inference

# The value gates whose settled verdict closes a gate-tracker. Read as id
# prefixes so both the mock (value-gate.mock.v0) and the real
# (value-gate.claude.v1, value-confirm.claude.v1) nodes count — never a single
# literal that a renamed node could silently slip past.
VALUE_NODE_PREFIXES = ("value-gate", "value-confirm")

# the make-over's identity at the inference gateway (default-deny): bdo permits
# it with one policy admission (CTA-7), else the transformer degrades.
CALLER = "noise-makeover"
SURFACE = "noise-makeover"

FENCE_TYPE = "noise_silence_fence"
GRANTOR = "bdo"  # the fence is the owner's standing authorization (D-4)

_EPIC_RE = re.compile(r"epic\.[a-z0-9][a-z0-9-]*")


# ----------------------------------------------------------------- resolution readings

def owner_ask_readings(root, fold=None):
    """Per live owner-ask group, whether the record resolves it. The mapping
    the make-over can prove from the log alone: an ask that says "confirm
    `epic.X`" is resolved the moment that arc carries an `arc_confirmed`
    admission — the cite. A group whose asks map to no confirmation stays
    unresolved (it genuinely needs bdo; it escalates, #628)."""
    fold = fold or Fold(root)
    out = []
    for g in owner_ask_groups(root):
        epics = sorted(set(_EPIC_RE.findall(" ".join(g["asks"]))))
        cite = confirmed = None
        for ep in epics:
            conf = arc_confirmation(fold, ep)
            if conf:
                cite, confirmed = conf.get("id"), ep
                break
        resolved = cite is not None
        out.append({
            "kind": "owner-ask",
            "subject": g["id"],
            "report_id": g["report_id"],
            "asks": g["asks"],
            "epics": epics,
            "resolved": resolved,
            "cite": cite,
            "reason": (f"the ask to confirm {confirmed} is satisfied — that arc is "
                       f"now confirmed ({cite}); the mirror issue can close"
                       if resolved else
                       "no log record resolves this ask — it genuinely needs you; "
                       "iterating to a named conclusion (#628)"),
        })
    return out


def _value_receipts(fold):
    return [rc for rc in fold.receipts
            if any((rc.get("node") or "").startswith(p) for p in VALUE_NODE_PREFIXES)]


def gate_tracker_readings(root, fold=None):
    """Per atom a value gate has judged, whether its CURRENT bytes carry a
    settled verdict — the idempotent close (done-line-grain): the tracker closes
    on the settled verdict regardless of which process produced it. A receipt on
    a superseded version does NOT settle the live tracker (identity is the
    content hash; an edited atom restarts the pipeline), so a re-versioned,
    unjudged atom stays open and escalates — the teeth case."""
    fold = fold or Fold(root)
    current = {atom["id"]: ahash for atom, ahash in load_atoms(root)}
    by_atom = {}
    for rc in _value_receipts(fold):
        aid = rc.get("artifact_id")
        if aid:
            by_atom.setdefault(aid, []).append(rc)
    out = []
    for aid, rcs in sorted(by_atom.items()):
        cur = current.get(aid)
        settled = None
        if cur:
            for rc in rcs:
                if rc.get("artifact_hash") == cur and rc.get("verdict"):
                    settled = rc  # the last settled verdict on the live bytes wins
        out.append({
            "kind": "gate-tracker",
            "subject": aid,
            "title_match": f"judging {aid}",  # the gate issue title carries this
            "resolved": settled is not None,
            "cite": settled.get("id") if settled else None,
            "verdict": settled.get("verdict") if settled else None,
            "node": settled.get("node") if settled else None,
            "reason": (f"settled: {settled.get('node')} -> {settled.get('verdict')} "
                       f"on the current bytes ({settled.get('id')}); the tracker "
                       "can close even though its producing process did not"
                       if settled else
                       f"no settled value verdict on the current version of {aid} "
                       "— the tracker holds; escalating (#628)"),
        })
    return out


def readings(root, fold=None):
    fold = fold or Fold(root)
    return owner_ask_readings(root, fold) + gate_tracker_readings(root, fold)


# ----------------------------------------------------------------- the make-over

def _attach_issue_refs(rows, open_issues):
    """Match each reading to an OPEN GitHub issue number by its title, so the
    actuator pen knows which issue to close. The pure fold never lists issues
    (no network); the pen passes `open_issues` (from `gh issue list`), tests
    pass fixtures. A reading with no matching open issue carries issue=None —
    its log-side silence (a discharge) still applies; there is simply no mirror
    to close."""
    for r in rows:
        r["issue"] = None
        for it in open_issues or []:
            title = it.get("title") or ""
            if (r["kind"] == "owner-ask" and "owner-ask" in title
                    and r.get("report_id") and r["report_id"] in title):
                r["issue"] = it.get("number")
                break
            if r["kind"] == "gate-tracker" and r.get("title_match", "") in title:
                r["issue"] = it.get("number")
                break


def _digest_line(silenceable, escalating):
    """The useful sound: one synthesized, organized line. Not a hush — it names
    what the record proved resolved AND what genuinely still needs bdo, by
    name, so the noise becomes signal (N2 of the bundle)."""
    oa = [r for r in silenceable if r["kind"] == "owner-ask"]
    gt = [r for r in silenceable if r["kind"] == "gate-tracker"]
    parts = []
    if oa:
        parts.append(f"reconciled {len(oa)} owner-ask(s) (arc-confirmed)")
    if gt:
        parts.append(f"closed {len(gt)} settled gate run(s)")
    if not parts:
        parts.append("nothing the record proves resolved")
    if escalating:
        named = ", ".join((r.get("report_id") or r["subject"]) for r in escalating[:8])
        tail = (f"; {len(escalating)} genuinely still need you: {named}"
                + (" …" if len(escalating) > 8 else ""))
    else:
        tail = "; none still open"
    return "noise make-over: " + ", ".join(parts) + tail


def partition(rows, fold):
    """The §10 teeth, as one pure split: a reading is silenceable ONLY if it
    claims resolved AND its cite resolves on the log. A reading that *claims*
    resolved but whose cite is absent is REFUSED — downgraded to escalating with
    a REFUSED reason — so a close with no provable resolution never silences
    anything. An honestly-unresolved reading escalates untouched. Returns
    (silenceable, escalating)."""
    silenceable, escalating = [], []
    for r in rows:
        if r.get("resolved") and record_on_log(fold, r.get("cite")):
            silenceable.append(r)
        elif r.get("resolved"):
            escalating.append(dict(
                r, resolved=False, refused=True,
                reason=(f"REFUSED: claimed cite {r.get('cite')!r} is not on the log "
                        "— a close with no provable resolution is refused; it stays "
                        "open and escalates (#628)")))
        else:
            escalating.append(r)
    return silenceable, escalating


def make_over(root, open_issues=None, fold=None):
    """The fold: split every noise reading into PROVEN-resolved (silenceable)
    and unresolved (escalating) through the teeth (`partition`), and synthesize
    the useful sound."""
    fold = fold or Fold(root)
    silenceable, escalating = partition(readings(root, fold), fold)
    rows = silenceable + escalating
    if open_issues is not None:
        _attach_issue_refs(rows, open_issues)
    return {
        "silenceable": silenceable,
        "escalating": escalating,
        "digest_line": _digest_line(silenceable, escalating),
        "fence": read_noise_fence(fold.admissions),
    }


def plan(root, open_issues=None, fold=None):
    """The make-over plus the fence disposition: which silenceable closes are
    AUTHORIZED to auto-silence this run, and which are merely proposed.

    No fence drawn → nothing self-silences (inert; every silenceable close is a
    PROPOSAL for a session/bdo to run). A fence drawn → cooling is the safe
    direction and always allowed, bounded by the fence's per-run `max_closes`
    cap; the overflow is held (proposed), never silently dropped. Escalating
    items are never authorized — unproven always escalates."""
    fold = fold or Fold(root)
    mo = make_over(root, open_issues, fold)
    fence = mo["fence"]
    if fence is None:
        auto, held = [], list(mo["silenceable"])
    else:
        cap = fence.get("max_closes")
        if cap is None:
            auto, held = list(mo["silenceable"]), []
        else:
            auto, held = mo["silenceable"][:cap], mo["silenceable"][cap:]
    return {**mo, "authorized": auto, "held_for_cap": held,
            "fence_id": fence.get("id") if fence else None}


# ----------------------------------------------------------------- the transformer (wave 2)

def _ask_prompt(reading, fold):
    """The transformer's prompt: the free-text ask + a recent log span, so the
    mind reads the ask against what actually happened. Pure string assembly —
    the model call lives in the actuator/gateway pen, never here."""
    span = [canon({k: a.get(k) for k in ("id", "type", "epic", "by", "ts")})
            for a in fold.admissions[-40:]]
    return "\n".join([
        "An owner-ask parked on bdo that maps to no single log event:",
        *[f"- {a}" for a in reading.get("asks", [])],
        "",
        "Recent admissions (the log span):",
        *span,
        "",
        "Decide: is this ask resolved by the record? If yes, name the EXACT record "
        "id (adm./rcp./evt.) that closed it as `cite`; never invent one. Also give "
        "a one-line `sound`: what these asks actually meant, in aggregate.",
        'Return JSON: {"resolved": <bool>, "cite": <record-id or null>, "sound": "<one line>"}',
    ])


def transform_unresolved(root, infer=None, fold=None):
    """Wave 2 — the large inference as a TRANSFORMER (bdo's correction): route a
    free-text owner-ask + the log span through the inference gateway and make it
    over into a useful sound (what these asks meant) + a resolved?/cite.

    `infer(prompt, fold)` is injected (the actuator pen provides the gateway-
    backed one; tests provide a fake). It is None by default — loop/ never
    reaches a model (no-network law), so the pure fold degrades gracefully:
    every unresolved ask escalates BY NAME, never guessed at. The §10 teeth hold
    OVER the inference output — a returned resolved+cite lands only if the cite
    resolves on the log; a hallucinated cite is refused like any other."""
    fold = fold or Fold(root)
    out = []
    for r in [x for x in owner_ask_readings(root, fold) if not x["resolved"]]:
        result = None
        if infer is not None:
            try:
                result = infer(_ask_prompt(r, fold), fold)
            except Exception:
                result = None  # a model that errored leaves the ask escalated, never closed
        if not result:
            out.append({**r, "transformed": False, "sound": None,
                        "reason": "inference unavailable or declined — escalated by "
                                  "name (no gateway policy admitted, or the mind "
                                  "returned nothing); #628"})
            continue
        cite = result.get("cite")
        if result.get("resolved") and cite and record_on_log(fold, cite):
            out.append({**r, "transformed": True, "resolved": True, "cite": cite,
                        "sound": result.get("sound"),
                        "reason": (f"inference resolved this ask and its cite {cite} "
                                   f"is verified on the log: {result.get('sound')}")})
        else:
            bad = bool(cite) and not record_on_log(fold, cite)
            out.append({**r, "transformed": True, "resolved": False, "cite": None,
                        "sound": result.get("sound"),
                        "reason": (f"inference proposed cite {cite!r} but it is NOT on "
                                   "the log — REFUSED; the ask stays open (#628)")
                                  if bad else
                                  "inference did not resolve this ask — escalated (#628)"})
    return out


def gateway_permits(root, fold=None):
    """Whether the make-over's caller may reach a mind (read-only). Default-deny:
    True only when bdo has admitted a permitting policy (CTA-7)."""
    fold = fold or Fold(root)
    permit, _why = inference.authorize(fold, CALLER, SURFACE, inference.WILDCARD)
    return permit


# ----------------------------------------------------------------- the fence (bdo's stamp)

def admit_noise_fence(root, max_closes, by, enabled=True, supersedes=None):
    """Draw (or withdraw) the standing auto-silence authorization — bdo's, like
    every fence (D-4). Refused unless --by is bdo: a session can never grant
    itself the right to silence the owner's surfaces. Returns (adm, None) or
    (None, reason-refused)."""
    if (by or "").strip().lower() != GRANTOR:
        return None, (f"the noise-silence fence is {GRANTOR}'s to draw — --by must be "
                      f"{GRANTOR} (a standing auto-silence authorization is the "
                      "owner's; a session never grants itself the right to silence "
                      "his surfaces)")
    if enabled and (not isinstance(max_closes, int) or max_closes < 0):
        return None, ("the fence bounds auto-closes per run: --max-closes is a "
                      "non-negative integer (cooling is always allowed up to it)")
    adm = {
        "id": "adm." + short_hash(FENCE_TYPE, str(max_closes), str(enabled),
                                  str(by), now_ts()),
        "type": FENCE_TYPE,
        "max_closes": (int(max_closes) if enabled else None),
        "enabled": bool(enabled),
        "by": by,
        "supersedes": supersedes,
        "ts": now_ts(),
    }
    append_line(root / "log" / "admissions.jsonl", adm)
    return adm, None


def read_noise_fence(admissions):
    """The fence in force, read at runtime (I-8): the latest `noise_silence_fence`
    admission wins; an `enabled: false` one withdraws it. None when bdo has drawn
    none — the make-over is then inert (reads and proposes only)."""
    fence = None
    for adm in admissions:
        if adm.get("type") == FENCE_TYPE:
            fence = adm if adm.get("enabled", True) else None
    return fence


# ----------------------------------------------------------------- render / CLI

def render(d):
    lines = ["# Noise make-over", ""]
    fence = d.get("fence")
    if fence:
        cap = fence.get("max_closes")
        lines += [f"fence — by {fence['by']}: auto-silence ON, "
                  f"cap {cap if cap is not None else 'unbounded'} close(s)/run "
                  "(cooling only; unproven escalates)", ""]
    else:
        lines += ["fence — none drawn; the make-over is INERT (reads and proposes "
                  "only). bdo draws it: python -m loop.reconcile_noise admit-fence "
                  "--max-closes 10 --by bdo", ""]
    lines.append(f"**{d['digest_line']}**")
    lines.append("")
    auto = d.get("authorized", [])
    held = d.get("held_for_cap", [])
    if auto:
        lines.append(f"## Authorized to silence ({len(auto)}) — proven, in-fence")
        for r in auto:
            lines.append(f"- `{r['subject']}` ({r['kind']}) — {r['reason']}")
        lines.append("")
    if held:
        lines.append(f"## Proven but held ({len(held)}) — over the fence cap / no fence")
        for r in held:
            lines.append(f"- `{r['subject']}` ({r['kind']}) — {r['reason']}")
        lines.append("")
    esc = d.get("escalating", [])
    if esc:
        lines.append(f"## Still need you ({len(esc)}) — escalates to a named "
                     "conclusion (#628)")
        for r in esc:
            lines.append(f"- `{r['subject']}` ({r['kind']}) — {r['reason']}")
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd")

    af = sub.add_parser("admit-fence", help="draw/withdraw the auto-silence fence (bdo)")
    af.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    af.add_argument("--max-closes", type=int, default=10, dest="max_closes",
                    help="max auto-closes per run (cooling only); default 10")
    af.add_argument("--off", action="store_true", help="withdraw the fence (supersedes)")
    af.add_argument("--by", required=True, help="who draws it (D-4: bdo)")

    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT, dest="root_top")
    ap.add_argument("--json", action="store_true", dest="json_top")
    args = ap.parse_args(argv)

    if args.cmd == "admit-fence":
        adm, err = admit_noise_fence(args.root, args.max_closes, args.by,
                                     enabled=not args.off)
        if err:
            print(f"result: needs-you — {err}")
            return 2
        if args.off:
            print(f"result: report — fence {adm['id']} withdrawn by {args.by}; the "
                  "make-over is inert again (reads and proposes only)")
        else:
            print(f"result: report — fence {adm['id']} drawn by {args.by}: "
                  f"auto-silence ON, cap {adm['max_closes']} close(s)/run. Proven-"
                  "resolved noise now self-silences; unproven still escalates to you.")
        return 0

    d = plan(args.root_top)
    if args.json_top:
        print(canon(d))
    else:
        print(render(d))
    silenceable = d.get("silenceable", [])
    esc = d.get("escalating", [])
    if d.get("fence") is None and silenceable:
        print(f"result: needs-you — {len(silenceable)} proven-resolved item(s) ready "
              "to silence, but no fence is drawn; draw it (admit-fence --by bdo) or "
              f"run the actuator pen by hand. {len(esc)} still need you.")
        return 2
    if esc:
        print(f"result: report — {len(d.get('authorized', []))} authorized to silence, "
              f"{len(esc)} still need you (escalating to a named conclusion, #628)")
        return 0
    print(f"result: done — {len(d.get('authorized', []))} authorized to silence, "
          "nothing left needing you")
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
