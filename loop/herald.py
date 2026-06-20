#!/usr/bin/env python3
"""The herald (epic.landing-throughput-response): agents are an open set, so
the registry is inverted the way the log inverts all state — log the
*introductions*, not the agents; "registered" and "reputation" are FOLDS
over the log, never a table.

A *herald* introduces a suitable agent (name, title) and the introduction
mints a *credential* — a stable content hash that is the agent's identity
for the pipeline, the way an atom's identity is the hash of its bytes. Every
later act an agent takes cites that credential, and standing is read back as
a pure fold over those acts. Nothing asserts its own reputation: it is only
ever earned *forward*, along the log's provenance edges.

This is the distributed-value reading. Reputation propagates along the
edges the log already records:

  - the agent earns from its own acts — exemplars (acts that advanced the
    work) net against notorieties (refusals / violations).
  - the herald that vouched earns a *meta-reputation* — a fold over the
    standing of every credential it introduced. A herald sits on its
    agents' provenance edge, so a bad voucher (one whose agents accrue
    notorieties) is visible by construction, never by assertion.

A freshly-introduced credential starts at the floor: rank is the trust
ladder's lowest rung (`loop.trust`, read — never a hardcoded string) and
standing is 0 — zero privilege until acts on the record earn it.

The pen (`introduce`) is deliberately dumb, like `loop.node`: it enforces a
minimal contract and holds no judgement. The roster and the reputation are
read-only folds, like `census`/`gaps`/`retro`. History is superseded, never
erased (a later introduction supersedes an earlier credential).

Stdlib only; reads the log, the pen appends one admission. Ends with a clear
result on stdout (D-6): done | report | needs-you.

CLI:
  python -m loop.herald                                    the roster + reputation, read-only
  python -m loop.herald --json                             the raw dataset (machine-readable)
  python -m loop.herald introduce --herald <id> --name <n> --title <t> --by <who>
"""

import argparse
import sys
from collections import defaultdict
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT, Fold, append_line, canon, now_ts, short_hash
from loop import trust

# The verdicts that did NOT advance the work — a refusal/rework signal, the
# same honest "this got pushed back" vocabulary `loop.retro` reads. An act
# attributed to a credential that carries one of these is a notoriety on that
# agent's ledger; anything else attributable to it is an exemplar.
NEGATING_VERDICTS = frozenset({
    "reject_no_value", "reject_wrong_value", "send_back", "amend",
    "collision", "wrong_seam", "halt_for_human", "missed", "refuse",
})

# The fields a record can name its actor in. A credential is "the actor" of a
# record when it appears in any of these — the provenance edge reputation
# propagates along (an announced event's from_node, a receipt's judging node,
# an admission's by, an explicit actor).
ACTOR_FIELDS = ("from_node", "actor", "node", "by")


def floor_rank():
    """The trust ladder's lowest rung — read from `loop.trust`, so "rank
    starts at the floor" is literally true in code, never an invented
    string."""
    return trust.CAPABILITIES[0]


def credential_for(name, title, by):
    """An agent's pipeline identity: a stable short hash of name+title+by.
    Deterministic — the same agent introduced again resolves to the same
    credential (the way identical atom bytes resolve to the same hash)."""
    return "cred." + short_hash("herald_credential", name, title, by)


# --------------------------------------------------------------------- the pen

def introduce(root, herald, name, title, by, supersedes=None):
    """Append ONE `herald_introduction` admission — the one write path.

    Dumb on purpose (the `loop.node` pattern): it mints the credential, stamps
    the floor rank, and records who vouched (`herald`) and who signed (`by`).
    It holds no judgement of the agent — standing is earned later, on the
    record. Returns the admission."""
    adm = {
        "id": "adm." + short_hash("herald_introduction", herald, name, title, str(by), now_ts()),
        "type": "herald_introduction",
        "herald": herald,
        "credential": credential_for(name, title, by),
        "name": name,
        "title": title,
        "rank": floor_rank(),
        "by": by,
        "supersedes": supersedes,
        "ts": now_ts(),
    }
    append_line(root / "log" / "admissions.jsonl", adm)
    return adm


def introduce_refusal(herald, name, title, by):
    """Why an introduction may NOT be written, or None. Pure over its inputs,
    so the suite hits it without writing the log (the placement/trust pattern)."""
    for label, val in (("herald", herald), ("name", name),
                       ("title", title), ("by", by)):
        if not (val or "").strip():
            return (f"{label} must be a non-empty value — a herald introduces a "
                    "named, titled agent and signs who vouched")
    return None


# ------------------------------------------------------------- the read folds

def _roster(fold):
    """Registered credentials as a fold over `herald_introduction` records —
    never a table. A later admission supersedes an earlier one (by id), and a
    re-introduction of the same credential lets the latest record win; history
    is superseded, never erased."""
    superseded = {a.get("supersedes") for a in fold.admissions if a.get("supersedes")}
    out = {}
    for a in fold.admissions:
        if a.get("type") != "herald_introduction" or a.get("id") in superseded:
            continue
        cred = a.get("credential")
        if not cred:
            continue
        prev = out.get(cred)
        if prev is None or a.get("ts", "") >= prev.get("ts", ""):
            out[cred] = a
    return out


def roster(root):
    """The registered credentials: {credential: {credential, name, title,
    rank, herald, ts}}. Registered is a fold, never a table."""
    reg = _roster(Fold(root))
    return {cred: {"credential": cred, "name": a.get("name"),
                   "title": a.get("title"), "rank": a.get("rank"),
                   "herald": a.get("herald"), "ts": a.get("ts")}
            for cred, a in reg.items()}


def _actor_is(record, credential):
    """Is this record an act attributable to the credential? True when the
    credential appears in any actor field — the provenance edge."""
    return any(record.get(f) == credential for f in ACTOR_FIELDS)


def _acts_for(fold, credential):
    """Every act on the record attributable to a credential, split into
    exemplars (advancing) and notorieties (refusals/violations). Derived only
    from log records — a credential never acted has empty lists (standing 0,
    the floor). Returns (exemplar_ids, notoriety_ids)."""
    exemplars, notorieties = [], []
    for rc in fold.receipts:
        if _actor_is(rc, credential):
            bucket = notorieties if rc.get("verdict") in NEGATING_VERDICTS else exemplars
            bucket.append(rc.get("id"))
    for ev in fold.events:
        if _actor_is(ev, credential):
            # announcing an event advances the work — an exemplar by default;
            # an explicitly-flagged violation is a notoriety.
            (notorieties if ev.get("violation") else exemplars).append(ev.get("id"))
    return exemplars, notorieties


def reputation(root):
    """The distributed-value fold. For each registered credential, standing is
    `len(exemplars) - len(notorieties)`, recomputed from the log's provenance
    edges (never asserted, never stored). For each herald, a meta-reputation:
    the sum of the standing of the credentials it introduced — it sits on
    their edge, so a herald whose agents accrue notorieties carries a lower
    meta-reputation by construction.

    Returns {"credentials": {cred: {...standing...}},
             "heralds": {herald: {introduced, meta, exemplars, notorieties}}}."""
    fold = Fold(root)
    reg = _roster(fold)
    credentials = {}
    for cred, a in reg.items():
        exemplars, notorieties = _acts_for(fold, cred)
        credentials[cred] = {
            "credential": cred,
            "name": a.get("name"),
            "title": a.get("title"),
            "rank": a.get("rank"),
            "herald": a.get("herald"),
            "exemplars": exemplars,
            "notorieties": notorieties,
            "standing": len(exemplars) - len(notorieties),
        }
    heralds = defaultdict(lambda: {"introduced": [], "meta": 0,
                                   "exemplars": 0, "notorieties": 0})
    for cred, c in credentials.items():
        h = heralds[c["herald"]]
        h["introduced"].append(cred)
        h["meta"] += c["standing"]
        h["exemplars"] += len(c["exemplars"])
        h["notorieties"] += len(c["notorieties"])
    return {"credentials": credentials, "heralds": dict(heralds)}


# --------------------------------------------------------------------- the CLI

def dataset(root):
    """The full read-only dataset: roster + reputation + herald meta."""
    return {"roster": roster(root), "reputation": reputation(root)}


def render(d):
    reg = d["roster"]
    rep = d["reputation"]
    lines = ["# The herald roster — registered is a fold, not a table", ""]
    if not reg:
        lines.append("No credential introduced yet. A herald vouches for an "
                     "agent:")
        lines.append("  python -m loop.herald introduce --herald <id> "
                     "--name <n> --title <t> --by <who>")
        return "\n".join(lines)
    creds = rep["credentials"]
    lines.append("## Credentials — standing is earned forward, never asserted")
    for cred in sorted(reg):
        c = creds.get(cred, {})
        r = reg[cred]
        lines.append(f"- `{cred}` — {r.get('name')} ({r.get('title')}) "
                     f"@ rank '{r.get('rank')}', vouched by {r.get('herald')}")
        lines.append(f"    standing {c.get('standing', 0)}  "
                     f"({len(c.get('exemplars', []))} exemplar(s), "
                     f"{len(c.get('notorieties', []))} notoriety(ies))")
        ev = (c.get("exemplars", []) + c.get("notorieties", []))[:4]
        if ev:
            lines.append("    on the record: " + ", ".join(ev))
    lines.append("")
    lines.append("## Heralds — meta-reputation, a fold over whom they minted")
    for h in sorted(rep["heralds"]):
        hd = rep["heralds"][h]
        lines.append(f"- `{h}` — meta {hd['meta']} over "
                     f"{len(hd['introduced'])} credential(s) "
                     f"({hd['exemplars']} exemplar(s), {hd['notorieties']} notoriety(ies))")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--json", action="store_true",
                    help="emit the raw dataset (machine-readable), not the prose")
    sub = ap.add_subparsers(dest="cmd")

    intro = sub.add_parser("introduce",
                           help="a herald vouches for an agent — mints its credential")
    intro.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    intro.add_argument("--herald", required=True, help="the vouching herald/skill id")
    intro.add_argument("--name", required=True, help="the agent's name")
    intro.add_argument("--title", required=True, help="the agent's title")
    intro.add_argument("--by", required=True, help="who signs the introduction")
    intro.add_argument("--supersedes", default=None,
                       help="a prior introduction id this replaces")

    args = ap.parse_args(argv)

    if args.cmd == "introduce":
        reason = introduce_refusal(args.herald, args.name, args.title, args.by)
        if reason:
            print(f"result: needs-you — {reason}")
            return 2
        adm = introduce(args.root, args.herald, args.name, args.title,
                        args.by, args.supersedes)
        print(f"result: done — {adm['id']}: {args.herald} introduced "
              f"{args.name} ({args.title}) as {adm['credential']} @ rank "
              f"'{adm['rank']}' (the floor; standing is earned forward)")
        return 0

    d = dataset(args.root)
    if args.json:
        print(canon(d))
    else:
        print(render(d))
    n = len(d["roster"])
    h = len(d["reputation"]["heralds"])
    print(f"result: report — {n} credential(s) registered across {h} "
          f"herald(s); standing is a fold over the log, earned forward (D-4)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
