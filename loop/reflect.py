#!/usr/bin/env python3
"""The reflection fold (done-line 0018): the owner's queue, mirrored outward.

bdo looked at GitHub Issues, saw nothing, and concluded the hook was lying
— the queue was real, the surface he visits showed none of it. His amend
(rcp.558ad49545cd) named the pattern and his stamp on the surface-registry
story (rcp.f68f73f3fee8) authorized it: external surfaces are *registered*
as admitted records, and what the log holds is *reflected* onto them, so
the external view is a mirror of the truth instead of a parallel world.

This module is the pure half — stdlib, no network, no subprocess (hard
rule). It computes, for each registered surface, the desired view (one
open item per atom awaiting the admitted-real owner stamp, briefed
arc-first) and the drift against what was last reflected. Reflections are
log records (events.jsonl, type "surface.reflected"), so drift is itself
a fold — deleting nothing, trusting no memory. The applying half is the
reflector pen (.claude/skills/reflect/reflect.py, gh-backed like the PR
pen): it applies exactly this drift and records each act back here.

Verdicts never flow in from a surface: the issue is a mirror, not a
second write path (D-4) — clearing stays loop.node judge.

Automation (done-line 0020) is the same fold with a dial: a reflection
*rule* — kind × surface → enabled — is an admitted record, and the auto
beat (a Stop hook running the pen's `auto` verb) applies exactly the
drift the enabled rules name. The log is the topic, rules are the
subscriptions, reflection records are the acks, drift is the unconsumed
backlog — pub/sub semantics, level-triggered, no broker, no daemon
(bdo's directive and stamp, chat 2026-06-10).

CLI (read-only except register and rule):
  python -m loop.reflect                    drift status across surfaces
  python -m loop.reflect register --surface github-issues \
      --address owner/repo --by bdo        admit a surface (omit --address
                                            to deregister; latest wins, I-8)
  python -m loop.reflect rule --kind owner-stamp-queue \
      --surface github-issues --on --by bdo    admit a rule (--off disables;
                                                latest wins, I-8)
"""

import argparse
import sys
from pathlib import Path

from loop.reconcile import (DEFAULT_ROOT, Fold, append_line, epic_of, glue_of,
                            load_atoms, load_epics, now_ts, real_nodes,
                            receipt_for_stage, short_hash)
from loop.orchestrate import HUMAN_NODE, STAMP_STAGE, next_action
from loop.digest import digest as compute_digest
from loop.owner_asks import owner_ask_groups

REFLECTED_EVENT = "surface.reflected"
PEN = "python .claude/skills/reflect/reflect.py"

# The kinds table — the extension point (done-line 0020). A kind is a
# named drift fold; a new kind joins as an entry here (plus rules to
# enable it), never as a new system. Three kinds today: the owner's stamp
# queue (drift, one issue per atom), the post-merge divergence surface
# (divergence_drift, one AGGREGATE issue per divergence group, done-line
# 0037), and the owner-ask backlog (owner_ask_drift, one aggregate issue
# per report whose needs-you items reached no surface, done-line 0058 — so
# an ad-hoc "awaiting bdo" cannot strand in a report he never opens).
# DRIFT_BY_KIND (below, after the folds) maps each to its fold.
RULE_KINDS = ("owner-stamp-queue", "merge-divergences", "owner-ask-backlog")

# The surface kinds table (done-line 0030): the tongues the reflector
# pen actually speaks — its translator table is keyed to exactly this
# tuple (pinned by test). A surface admitted with a kind off this table
# is named by status() and skipped by the beat; registering one is
# refused at the CLI. A new surface kind is a new translator — its own
# stamped increment, never a silent gh-shaped guess.
SURFACE_KINDS = ("github-issues",)


def admit_surface(root, surface, address, by, kind="github-issues"):
    """A surface is an admitted record (I-8), never a code literal: id,
    kind, address, signed --by. A null address deregisters (latest wins),
    superseding — never erasing — the admission before it."""
    adm = {
        "id": "adm." + short_hash("surface", surface, str(address), str(by), now_ts()),
        "type": "surface",
        "surface": surface,
        "kind": kind,
        "address": address,
        "by": by,
        "ts": now_ts(),
    }
    append_line(root / "log" / "admissions.jsonl", adm)
    return adm


def registered_surfaces(fold):
    """Latest surface admission per id wins; a null address deregisters."""
    surfaces = {}
    for adm in fold.admissions:
        if adm.get("type") == "surface" and adm.get("surface"):
            if adm.get("address"):
                surfaces[adm["surface"]] = adm
            else:
                surfaces.pop(adm["surface"], None)
    return surfaces


def admit_rule(root, kind, surface, enabled, by):
    """A reflection rule is the translation matrix's cell, admitted (I-8):
    this kind reflects to this surface, or stops doing so. Latest
    (kind, surface) admission wins; disabling is a superseding record,
    never an erasure."""
    adm = {
        "id": "adm." + short_hash("reflection_rule", kind, surface,
                                  str(enabled), str(by), now_ts()),
        "type": "reflection_rule",
        "kind": kind,
        "surface": surface,
        "enabled": bool(enabled),
        "by": by,
        "ts": now_ts(),
    }
    append_line(root / "log" / "admissions.jsonl", adm)
    return adm


def rules(fold):
    """The matrix: latest admission per (kind, surface) cell wins."""
    out = {}
    for adm in fold.admissions:
        if adm.get("type") == "reflection_rule" and adm.get("kind") and adm.get("surface"):
            out[(adm["kind"], adm["surface"])] = adm
    return out


def enabled_rules(fold):
    return {key: adm for key, adm in rules(fold).items() if adm.get("enabled")}


def auto_plan(root):
    """What the beat would do, as a read-only fold: for every enabled rule
    whose kind is known and whose surface is registered, the drift to
    apply. Unknown kinds and unregistered surfaces are skipped here — the
    beat must never break a turn; status() names them for eyes instead."""
    fold = Fold(root)
    surfaces = registered_surfaces(fold)
    plan = []
    for (kind, surface), adm in sorted(enabled_rules(fold).items()):
        if kind not in RULE_KINDS or surface not in surfaces:
            continue
        if surfaces[surface].get("kind") not in SURFACE_KINDS:
            continue  # no translator speaks it (done-line 0030); status() names it
        acts = DRIFT_BY_KIND[kind](root, surface)  # dispatch by kind, not assume one
        if acts:
            plan.append({"kind": kind, "surface": surface, "acts": acts})
    return plan


def reflections(fold, surface):
    """What this surface has been told, by (artifact_hash, act) — first
    record wins (the fold dedups by id, so re-recording is a no-op)."""
    out = {}
    for ev in fold.events:
        if ev.get("type") == REFLECTED_EVENT and ev.get("surface") == surface:
            out.setdefault((ev.get("artifact_hash"), ev.get("act")), ev)
    return out


def record_reflection(root, surface, atom_id, artifact_hash, act, external_ref, by):
    """The applying pen's receipt: one applied act, on the log, with
    provenance. Content-derived id — recording the same act twice folds
    to one (I-2)."""
    ev = {
        "id": "evt." + short_hash(REFLECTED_EVENT, surface, artifact_hash, act),
        "type": REFLECTED_EVENT,
        "surface": surface,
        "artifact_id": atom_id,
        "artifact_hash": artifact_hash,
        "act": act,
        "external_ref": external_ref,
        "by": by,
        "ts": now_ts(),
    }
    append_line(root / "log" / "events.jsonl", ev)
    return ev


def awaiting_stamp(root, fold, real_map):
    """The owner's queue: every atom whose next action is the admitted-real
    stamp — the same fold the inbox and the hook count from."""
    human = real_map.get(HUMAN_NODE)
    if human is None:
        return []
    return [(atom, ahash) for atom, ahash in load_atoms(root)
            if next_action(fold, atom, ahash, real_map) == ("await", human)]


def item_title(atom):
    headline = atom.get("briefing", {}).get("headline", "")
    title = f"[stamp] {atom['id']}"
    return f"{title} — {headline}" if headline else title


def item_body(root, fold, atom, ahash, epics, human):
    """The briefing, arc-first (done-line 0006), as markdown — the same
    layers the inbox prints, shaped for the surface bdo actually opens."""
    epic = epic_of(atom, epics)
    lines = []
    if epic:
        lines += [f"## the arc", f"**{epic['id']}** — {epic['value']}"]
        glue = glue_of(atom, epic)
        if glue:
            lines.append(f"*glues in:* {glue}")
        lines.append("")
    briefing = atom.get("briefing", {})
    lines.append("## the item")
    if briefing.get("headline"):
        lines.append(f"**{briefing['headline']}**")
    for label, key in (("value", "value"), ("why now", "why_now"),
                       ("if you accept", "if_accepted"),
                       ("if you reject", "if_rejected"),
                       ("cost of a wrong call", "cost_of_wrong_call")):
        if briefing.get(key):
            lines.append(f"- **{label}:** {briefing[key]}")
    lines += ["", f"*story:* {atom['story']['text']}",
              f"*author's confidence:* {atom['story']['value_confidence']}"]
    receipts = [rc for rc in fold.receipts if rc.get("artifact_hash") == ahash]
    if receipts:
        lines += ["", "## receipts so far"]
        lines += [f"- `{rc['node']}`: **{rc['verdict']}** — {rc['reason']}"
                  for rc in receipts]
    lines += [
        "",
        "## your verdict",
        f"`{' | '.join(STAMP_STAGE['terminal_expected'])}`",
        "",
        "This issue is a **mirror** of the loop's owner inbox — judging it",
        "here does nothing; the verdict lands through the one pen (D-4),",
        "in chat or:",
        "```sh",
        f"python -m loop.node judge --atom {atom['id']} --node {human} "
        "--verdict <verdict> --reason \"<why>\"",
        "```",
        "Reflected from the log by `loop/reflect.py`; when the stamp lands,",
        "the reflector closes this issue with the verdict and receipt id.",
    ]
    return "\n".join(lines)


def drift(root, surface):
    """desired view minus reflected view, as the acts that would close the
    gap. Pure: this computes; only the pen applies. Raises on an
    unregistered surface — reflecting to a surface nobody admitted is the
    §10 thing that must not fit."""
    fold = Fold(root)
    surfaces = registered_surfaces(fold)
    if surface not in surfaces:
        known = ", ".join(sorted(surfaces)) or "none registered"
        raise ValueError(f"surface {surface!r} is not admitted ({known}); "
                         f"register it: python -m loop.reflect register "
                         f"--surface {surface} --address <owner/repo> --by <who>")
    real_map = real_nodes(fold)
    human = real_map.get(HUMAN_NODE)
    epics = load_epics(root)
    seen = reflections(fold, surface)
    awaiting = awaiting_stamp(root, fold, real_map)
    acts = []
    for atom, ahash in awaiting:
        if (ahash, "open") not in seen:
            acts.append({"act": "open", "atom_id": atom["id"],
                         "artifact_hash": ahash,
                         "title": item_title(atom),
                         "body": item_body(root, fold, atom, ahash, epics, human)})
    awaiting_hashes = {ahash for _, ahash in awaiting}
    for (ahash, act), ev in sorted(seen.items(), key=lambda kv: kv[1]["id"]):
        if act != "open" or ahash in awaiting_hashes or (ahash, "close") in seen:
            continue
        rc = receipt_for_stage(fold, STAMP_STAGE, ahash, real_map)
        if rc:
            comment = (f"the stamp landed: **{rc['verdict']}** ({rc['id']}) — "
                       f"{rc['reason']}")
        else:
            comment = ("no longer at the stamp — the atom advanced, was "
                       "amended to a new version, or was retired; the log "
                       "holds the history")
        acts.append({"act": "close", "atom_id": ev.get("artifact_id"),
                     "artifact_hash": ahash,
                     "external_ref": ev.get("external_ref"),
                     "comment": comment})
    return acts


def _divergence_groups(divergences):
    """Fold the digest's divergences into aggregate groups — one issue per
    group, not one per data point (bdo's shape, 2026-06-11: aggregate
    surfacing, never a per-PR echo). Refusals group by the confirmed arc they
    sit under; cap-breaches group as one. Each group's id is stable over its
    key, so an open is idempotent and a close fires only when the group
    reconciles (its data points all clear). Returns {group_id: group}."""
    refusals, caps = {}, []
    for d in divergences:
        if d.get("kind") == "refusal-under-confirmed-arc":
            refusals.setdefault(d.get("epic"), []).append(d)
        elif d.get("kind") == "queue-over-cap":
            caps.append(d)

    groups = {}
    for epic, items in sorted(refusals.items()):
        gid = "div." + short_hash("refusal-under-confirmed-arc", str(epic))
        lines = [f"## refusals under confirmed arc `{epic}`",
                 f"You confirmed this arc, yet {len(items)} of its piece(s) "
                 "earned a gate's refusal — confirm-arc means the loop carries "
                 "the pieces, so a refusal here is the pattern that needs you:",
                 ""]
        lines += [f"- **{d.get('atom')}** — {d.get('node')} → "
                  f"`{d.get('verdict')}`: {d.get('reason') or 'no reason given'}"
                  for d in items]
        lines += ["", "*Reconcile by amending the refused piece(s) or "
                  "withdrawing the arc (`confirm-arc --off`). Live detail: "
                  "`python -m loop.digest`. This issue is a mirror — it closes "
                  "itself when the pattern reconciles (no refusal left under "
                  "this arc).*"]
        groups[gid] = {"label": f"refusals:{epic}",
                       "title": f"[divergence] {len(items)} refusal(s) under "
                                f"confirmed arc {epic}",
                       "body": "\n".join(lines)}
    if caps:
        gid = "div." + short_hash("queue-over-cap")
        lines = [f"## the human queue breached its cap ({len(caps)} tick(s))",
                 "The cool valve is meant to hold the owner's queue at or under "
                 "its admitted cap; these ticks ran over it:", ""]
        lines += [f"- tick {d.get('tick')}: backlog {d.get('backlog')} > "
                  f"cap {d.get('cap')} (setpoint {d.get('setpoint_id')})"
                  for d in caps]
        lines += ["", "*Reconcile by raising the cap or shedding inflow "
                  "(`loop.orchestrate --admit-setpoint`). Live detail: "
                  "`python -m loop.digest`. Closes when no tick in the span "
                  "breaches its cap.*"]
        groups[gid] = {"label": "queue-over-cap",
                       "title": f"[divergence] human queue breached its cap "
                                f"({len(caps)} tick(s))",
                       "body": "\n".join(lines)}
    return groups


def divergence_drift(root, surface):
    """The merge-divergences kind (done-line 0037): aggregate divergence
    groups, mirrored as issues. Same drift shape as drift() — open the groups
    not yet opened, close the opened groups that have reconciled — keyed by
    group id in the artifact_hash slot, so the gh translator and the
    reflection records work unchanged. Pure; only the pen applies."""
    fold = Fold(root)
    surfaces = registered_surfaces(fold)
    if surface not in surfaces:
        known = ", ".join(sorted(surfaces)) or "none registered"
        raise ValueError(f"surface {surface!r} is not admitted ({known}); "
                         f"register it: python -m loop.reflect register "
                         f"--surface {surface} --address <owner/repo> --by <who>")
    seen = reflections(fold, surface)
    groups = _divergence_groups(compute_digest(root).get("divergences", []))
    acts = []
    for gid, g in groups.items():
        if (gid, "open") not in seen:
            acts.append({"act": "open", "atom_id": g["label"],
                         "artifact_hash": gid, "title": g["title"],
                         "body": g["body"]})
    for (ahash, act), ev in sorted(seen.items(), key=lambda kv: kv[1]["id"]):
        if act != "open" or ahash in groups or (ahash, "close") in seen:
            continue
        acts.append({"act": "close", "atom_id": ev.get("artifact_id"),
                     "artifact_hash": ahash,
                     "external_ref": ev.get("external_ref"),
                     "comment": "reconciled — this divergence pattern no longer "
                                "appears in the digest; closed by the mirror"})
    return acts


def owner_ask_drift(root, surface):
    """The owner-ask-backlog kind (done-line 0058): a needs-you item written
    only into a session report reaches bdo's inbox, instead of stranding in a
    working-tree file he never opens (the hole report 0047's five invisible
    taps exposed). One aggregate issue per report with parked asks — the
    divergence grain (one per group, not one per item, bdo 2026-06-11) — keyed
    by the group id in the artifact_hash slot so the gh translator and the
    reflection records work unchanged. Open-only: a free-text ask carries no
    log-backed 'answered' signal, so bdo dismisses it by his own gesture and
    the mirror never reopens what it surfaced once. Pure; only the pen
    applies. Raises on an unregistered surface, like the other folds."""
    fold = Fold(root)
    surfaces = registered_surfaces(fold)
    if surface not in surfaces:
        known = ", ".join(sorted(surfaces)) or "none registered"
        raise ValueError(f"surface {surface!r} is not admitted ({known}); "
                         f"register it: python -m loop.reflect register "
                         f"--surface {surface} --address <owner/repo> --by <who>")
    seen = reflections(fold, surface)
    acts = []
    for g in owner_ask_groups(root):
        if (g["id"], "open") not in seen:
            acts.append({"act": "open", "atom_id": g["report_id"],
                         "artifact_hash": g["id"], "title": g["title"],
                         "body": g["body"]})
    return acts


def surfaced_open_ids(fold):
    """Every artifact (atom/group/ask) that an 'open' reflection record has
    already named — on any surface. The ack-set the shame floor reads to know
    what has reached bdo and what is still stranded."""
    return {ev.get("artifact_hash") for ev in fold.events
            if ev.get("type") == REFLECTED_EVENT and ev.get("act") == "open"}


def unsurfaced_owner_ask_groups(root):
    """Owner-ask groups no surface has been told — the durable hole the shame
    beat screams. Surfaced means an 'open' reflection record carries the
    group id (on any surface); until then the ask is parked invisibly and the
    floor keeps screaming it. Read-only (I-3). A reportless tree short-circuits
    before the log fold — absence is [], never a raise."""
    groups = owner_ask_groups(root)
    if not groups:
        return []
    surfaced = surfaced_open_ids(Fold(root))
    return [g for g in groups if g["id"] not in surfaced]


# A kind is a named drift fold (RULE_KINDS); this maps each to its fold, so
# the beat (auto_plan) and status dispatch by kind instead of assuming one.
DRIFT_BY_KIND = {
    "owner-stamp-queue": drift,
    "merge-divergences": divergence_drift,
    "owner-ask-backlog": owner_ask_drift,
}


def status(root):
    """Read-only (I-3): every registered surface and its drift."""
    fold = Fold(root)
    surfaces = registered_surfaces(fold)
    if not surfaces:
        print("result: done — no surfaces registered; the inbox reaches only "
              "this repo (register one: python -m loop.reflect register "
              "--surface <id> --address <owner/repo> --by <who>)")
        return 0
    matrix = rules(fold)
    auto_pairs = set()  # (kind, surface) with an enabled, applicable rule
    for (kind, surface), adm in sorted(matrix.items()):
        state = "on" if adm.get("enabled") else "off"
        note = ""
        if kind not in RULE_KINDS:
            note = " (unknown kind — the beat skips it)"
        elif surface not in surfaces:
            note = " (surface not registered — the beat skips it)"
        elif surfaces[surface].get("kind") not in SURFACE_KINDS:
            note = (" (surface kind has no translator — the beat skips it; "
                    "done-line 0030)")
        elif adm.get("enabled"):
            auto_pairs.add((kind, surface))
        print(f"rule: {kind} x {surface} = {state} "
              f"(admitted by {adm['by']}, {adm['id']}){note}")
    total = 0
    for sid, adm in sorted(surfaces.items()):
        print(f"surface: {sid} ({adm['kind']}) -> {adm['address']} "
              f"(admitted by {adm['by']}, {adm['id']})")
        any_acts = False
        for kind in RULE_KINDS:
            # owner-stamp-queue shows always (back-compat); other kinds only
            # where a rule enables them — a surface mirrors many kinds at once
            if kind != "owner-stamp-queue" and (kind, sid) not in auto_pairs:
                continue
            acts = DRIFT_BY_KIND[kind](root, sid)
            total += len(acts)
            beat = "auto" if (kind, sid) in auto_pairs else "manual only (no enabled rule)"
            for a in acts:
                any_acts = True
                ref = f" [{a.get('external_ref')}]" if a.get("external_ref") else ""
                print(f"  [{kind}, {beat}] {a['act']}: {a['atom_id']}{ref}")
        if not any_acts:
            print("  no drift — the surface mirrors the log")
    if total:
        print(f"result: report — {total} act(s) of drift; the beat clears what "
              f"rules name, or apply by hand: {PEN} apply --surface <id> --by <who>")
    else:
        print("result: done — every registered surface mirrors the log")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd")

    st = sub.add_parser("status", help="registered surfaces and their drift, read-only")
    st.add_argument("--root", type=Path, default=DEFAULT_ROOT)

    reg = sub.add_parser("register", help="admit a surface (I-8: a signed record, latest wins)")
    reg.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    reg.add_argument("--surface", required=True, help="surface id, e.g. github-issues")
    reg.add_argument("--kind", default="github-issues",
                     help=f"surface kind; one the pen translates: "
                          f"{', '.join(SURFACE_KINDS)}")
    reg.add_argument("--address", default=None,
                     help="where it lives, e.g. owner/repo (omit to deregister)")
    reg.add_argument("--by", required=True,
                     help="who admits it (D-4: surfaces are signed, never self-set)")

    ru = sub.add_parser("rule", help="admit a reflection rule: kind x surface -> enabled (I-8)")
    ru.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ru.add_argument("--kind", required=True, help=f"one of: {', '.join(RULE_KINDS)}")
    ru.add_argument("--surface", required=True)
    onoff = ru.add_mutually_exclusive_group(required=True)
    onoff.add_argument("--on", dest="enabled", action="store_true")
    onoff.add_argument("--off", dest="enabled", action="store_false")
    ru.add_argument("--by", required=True,
                    help="who admits it (the dial is signed, never self-set)")

    args = ap.parse_args(argv)
    if args.cmd == "rule":
        if args.kind not in RULE_KINDS:
            print(f"result: needs-you — unknown kind {args.kind!r}; the kinds "
                  f"table in loop/reflect.py holds: {', '.join(RULE_KINDS)} "
                  f"(a new kind is a new fold — its own stamped increment)")
            return 2
        adm = admit_rule(args.root, args.kind, args.surface, args.enabled, args.by)
        print(f"result: report — {adm['id']}: rule {args.kind} x {args.surface} "
              f"= {'on' if args.enabled else 'off'} (admitted by {args.by})")
        return 0
    if args.cmd == "register":
        if args.address and args.kind not in SURFACE_KINDS:
            print(f"result: needs-you — no translator speaks kind "
                  f"{args.kind!r}; the surface kinds table in "
                  f"loop/reflect.py holds: {', '.join(SURFACE_KINDS)} "
                  f"(a new surface kind is a new translator in the "
                  f"reflector pen — its own stamped increment)")
            return 2
        adm = admit_surface(args.root, args.surface, args.address, args.by, kind=args.kind)
        print(f"result: report — {adm['id']}: surface {args.surface} "
              + (f"registered at {args.address}" if args.address else "deregistered")
              + f" (admitted by {args.by})")
        return 0
    root = args.root if args.cmd == "status" else DEFAULT_ROOT
    return status(root)


if __name__ == "__main__":
    sys.exit(main())
