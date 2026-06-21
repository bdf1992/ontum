#!/usr/bin/env python3
"""The healing fold (done-line 0111): the loop senses where its own teeth
bit too sharp — read-only, propose-only.

The loop is rich in teeth: five gates that can refuse, a placement gate
that catches collisions, a value-confirm that caught a phantom delivery.
But a crawl of the whole record shows the gates almost never refuse
(≈3.4% of all verdicts are non-advancing), and a tooth without a healing
reflex is autoimmunity — the system keeps a correct-but-stale bite
inflamed on the surfaces bdo reads (the `atom.field-topology.v0` 'missed'
that still shows as a parked refusal long after v1 built the thing and
`confirmed`), and it has no part that could ever see a tooth bite
*wrong*. This module is the counterforce bdo named: an part that senses
where a tooth was too sharp or has gone stale, and proposes the heal.

Sibling of `retro` on the *bite* axis. Retro asks "what keeps happening";
heal asks "where did a tooth bite wrong". No second truth (§10): it folds
the same append-only log (`loop.reconcile.Fold`) and reuses the
version-split (`loop.digest._base_version`) and supersession
(`loop.reconcile.superseded_atom_ids`) rather than re-deriving them.
Evidence is cited to receipt ids (the grip rule). It is propose-only
(D-4): it names the over-bite and the one heal move; it never clears a
park, re-opens a verdict, edits the log, or admits anything — a future
increment may earn a *bounded* actuator through the disposer fence, not
this one.

Three detectors (two are the system's first sensors of a failure mode it
cannot yet see — declared even at zero live instances, like the cool
valve, so the sensor exists before the load arrives):

  stale-park     a gate correctly negated an *old* version, and the *live*
                 version then PASSED that same gate — the bite is resolved;
                 only its surfacing on the owner views may be stale. The
                 one real-today finding. Hygiene, not a bad tooth.
  flapping-gate  a gate negates the *live* version of a base after having
                 ADVANCED an earlier one — a current self-contradiction:
                 either the live work regressed (bite correct) or the bar
                 tightened (tooth too sharp). The genuine "too sharp" sensor.
  owner-override bdo's owner-stamp advanced an artifact a real gate had
                 refused — the owner overruled the tooth. The unambiguous
                 proof a bite was too sharp.

The §10 teeth (in `tests/test_heal.py`): a gate that negates a base
*consistently* (never advanced a version of it) is NEVER flagged — a
repeated correct refusal is good backpressure, not an over-bite; and a
genuine open park (a refusal with no later passing version) is never read
as stale.

CLI:
  python -m loop.heal           the healing read, all history, read-only
  python -m loop.heal --json    the raw dataset (machine-readable)

Stdlib only. Ends with a clear result on stdout (D-6): done | report.
"""

import argparse
import sys
from collections import defaultdict
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT, Fold, canon, superseded_atom_ids
from loop import digest as digest_mod

# The verdict vocabulary on the real log, split by direction. A verdict not
# in either set (none seen today) advances nothing and refuses nothing — it
# is ignored rather than guessed at.
ADVANCING_VERDICTS = frozenset({
    "accept", "sound", "ready_for_spec", "confirmed", "landed",
})
NEGATING_VERDICTS = frozenset({
    "reject_no_value", "reject_wrong_value", "send_back", "amend",
    "collision", "missed",
})

OWNER_PREFIX = "owner-stamp"
KIND_ORDER = ("flapping-gate", "owner-override", "stale-park")


def _base(atom_id):
    """Version-blind atom base, via the digest's own split (no second copy
    of the .vN rule — done-line 0111's no-double-build)."""
    return digest_mod._base_version(atom_id)[0]


def _ver(atom_id):
    return digest_mod._base_version(atom_id)[1]


def _is_gate(node):
    """A judging gate whose bar could be too sharp: a node that judges, but
    not a mock (a fixed verdict cannot flap) and not the owner's own stamp
    (the owner steers; his amends are not tooth-instability — owner-override
    reads his stamp, and from the other side)."""
    return bool(node) and ".mock" not in node and not node.startswith(OWNER_PREFIX)


def _by_gate_base(fold):
    """Receipts grouped (gate, base) -> [(ver, atom_id, verdict, rc), …],
    and the set of all atom ids seen per base (for supersession). One pass,
    reused by both gate detectors."""
    by = defaultdict(list)
    ids_by_base = defaultdict(set)
    for rc in fold.receipts:
        node, aid = rc.get("node"), rc.get("artifact_id")
        if not (node and aid):
            continue
        ids_by_base[_base(aid)].add(aid)
        if _is_gate(node):
            by[(node, _base(aid))].append((_ver(aid), aid, rc.get("verdict"), rc))
    return by, ids_by_base


def _cite(rc, atom_id, verdict):
    glance = digest_mod._glance(rc.get("reason"))
    tail = f": {glance}" if glance else ""
    return f"{verdict} {atom_id} ({rc.get('id')}){tail}"


def stale_park_findings(fold):
    """A gate correctly negated an OLD version; the LIVE version of the same
    base then PASSED that gate. The bite is settled — the work was fixed and
    moved on — so its park is history, not a live refusal; surfacing it as
    open on the owner views is the stale wound. The discriminator (§10): the
    live version's verdict at this gate must be advancing — if the gate still
    negates the live version, that is a live park (gaps' job), never stale."""
    by, ids_by_base = _by_gate_base(fold)
    out = []
    for (node, base), recs in sorted(by.items()):
        ids = ids_by_base[base]
        if len(ids) < 2:
            continue  # one version: a negation here has no later pass to be stale against
        superseded = superseded_atom_ids(ids)
        live_ver = max(_ver(a) for a in ids)
        live = [(vd, rc) for v, a, vd, rc in recs if v == live_ver]
        if not any(vd in ADVANCING_VERDICTS for vd, rc in live):
            continue  # the gate still negates (or never judged) the live version
        live_rc = next(rc for vd, rc in live if vd in ADVANCING_VERDICTS)
        live_vd = next(vd for vd, rc in live if vd in ADVANCING_VERDICTS)
        for v, aid, vd, rc in sorted(recs):
            if vd in NEGATING_VERDICTS and aid in superseded:
                out.append({
                    "kind": "stale-park",
                    "subject": aid,
                    "evidence": [
                        _cite(rc, aid, vd),
                        f"but the live {_cite(live_rc, live_rc.get('artifact_id'), live_vd)}",
                    ],
                    "move": "the work was fixed in the live version and passed "
                            f"{node}; the bite is healed. Confirm no owner surface "
                            "(inbox/digest) still shows this version's refusal as "
                            "an open park — the refusal stands as history, not as "
                            "live work.",
                })
    return out


def flapping_findings(fold):
    """A gate negates the LIVE version of a base after having ADVANCED an
    earlier one — a current self-contradiction. Either the live version
    regressed (the bite is right — say so on the record) or the gate's bar
    tightened (the tooth is too sharp — re-pin the prompt/spec). The
    discriminator (§10): a gate that only ever negated this base (never
    advanced a version) is consistent backpressure and never enters here."""
    by, ids_by_base = _by_gate_base(fold)
    out = []
    for (node, base), recs in sorted(by.items()):
        live_ver = max(v for v, a, vd, rc in recs)
        live_neg = [(aid, vd, rc) for v, aid, vd, rc in recs
                    if v == live_ver and vd in NEGATING_VERDICTS]
        earlier_adv = [(v, aid, vd, rc) for v, aid, vd, rc in recs
                       if v < live_ver and vd in ADVANCING_VERDICTS]
        if not (live_neg and earlier_adv):
            continue
        laid, lvd, lrc = live_neg[0]
        ev, eaid, evd, erc = max(earlier_adv)  # the most recent prior pass
        out.append({
            "kind": "flapping-gate",
            "subject": f"{node} on {base}",
            "evidence": [
                f"earlier {_cite(erc, eaid, evd)}",
                f"now {_cite(lrc, laid, lvd)}",
            ],
            "move": f"{node} passed an earlier version of this base and refuses "
                    "the live one. Read the two side by side: either the live "
                    "version genuinely regressed (then the bite is right — record "
                    "why) or the bar moved (the tooth is too sharp — re-pin the "
                    "gate's prompt/spec so it judges the same thing twice).",
        })
    return out


def owner_override_findings(fold):
    """bdo's owner-stamp advanced an artifact a real gate had refused, AFTER
    the refusal — the owner saw the bite and overruled it. The strongest
    possible 'this tooth was too sharp' signal.

    Two discriminators, both load-bearing (§10): same-artifact (an `amend`
    then an accept on a LATER version is the amend working as designed, never
    an override), and ts-ordering — the owner's accept must come AFTER the
    gate's refusal. Without the latter this fires on every normal pipeline:
    owner-stamp is stage 2, and a later-stage gate (handoff/value-confirm)
    refusing at stage 4–5 is NOT an override of a stamp that preceded it.
    The owner advanced what he never saw refused; only a stamp that follows a
    refusal is an override."""
    # atom_id -> {"gate_neg": [(node, verdict, rc)], "owner_adv": [rc]}
    by_aid = defaultdict(lambda: {"gate_neg": [], "owner_adv": []})
    for rc in fold.receipts:
        node, aid, vd = rc.get("node"), rc.get("artifact_id"), rc.get("verdict")
        if not (node and aid):
            continue
        if _is_gate(node) and vd in NEGATING_VERDICTS:
            by_aid[aid]["gate_neg"].append((node, vd, rc))
        elif node.startswith(OWNER_PREFIX) and vd in ADVANCING_VERDICTS:
            by_aid[aid]["owner_adv"].append(rc)
    out = []
    for aid, sides in sorted(by_aid.items()):
        if not (sides["gate_neg"] and sides["owner_adv"]):
            continue
        # the earliest refusal and the latest owner accept: an override needs
        # an owner stamp that lands AFTER a gate said no (ts is ISO-8601 UTC,
        # so a lexical compare is a time compare).
        gnode, gvd, grc = min(sides["gate_neg"], key=lambda x: x[2].get("ts") or "")
        orc = max(sides["owner_adv"], key=lambda r: r.get("ts") or "")
        if (orc.get("ts") or "") <= (grc.get("ts") or ""):
            continue  # the owner stamped before the gate refused — not an override
        # Hash-aware healed-bite check (identity is the content hash, not the
        # .vN id string): if the SAME gate that refused later ADVANCED a
        # DIFFERENT-hash version of this atom, the gate itself relented — the
        # work was fixed and re-judged. That is a healed bite (stale-park's
        # job), never an owner override. The real fixture: the herald, edited
        # in place under one .v0 id (two hashes) and confirmed — was falsely
        # read as "bdo overruled a tooth" because the .vN string hid the
        # second version the gate passed.
        neg_hash, base = grc.get("artifact_hash"), _base(aid)
        if any(rc.get("node") == gnode
               and rc.get("verdict") in ADVANCING_VERDICTS
               and _base(rc.get("artifact_id") or "") == base
               and rc.get("artifact_hash") != neg_hash
               and (rc.get("ts") or "") > (grc.get("ts") or "")
               for rc in fold.receipts):
            continue
        out.append({
            "kind": "owner-override",
            "subject": aid,
            "evidence": [
                f"gate {_cite(grc, aid, gvd)}",
                f"owner {_cite(orc, aid, orc.get('verdict'))}",
            ],
            "move": f"the owner advanced what {gnode} refused, on the same "
                    "artifact. The tooth bit work bdo wanted — re-pin the gate's "
                    "prompt/spec to the owner's bar, or record why the gate was "
                    "right and the owner's stamp was the exception.",
        })
    return out


def heal(root):
    """The fold: over-bites across all history, most-urgent kind first.
    Returns the plain dataset render() turns into prose and --json emits."""
    fold = Fold(root)
    findings = (flapping_findings(fold)
                + owner_override_findings(fold)
                + stale_park_findings(fold))
    from collections import Counter
    return {
        "findings": findings,
        "counts": dict(Counter(f["kind"] for f in findings)),
        "scanned": {"receipts": len(fold.receipts)},
    }


def render(d):
    lines = ["# Healing — where a tooth may need care", "",
             "_a fold for where the loop's own teeth bit too sharp or stale; "
             "read-only, the heal stays yours (D-4)._", ""]
    lines.append(f"Scanned {d['scanned']['receipts']} receipts.")
    lines.append("")
    if not d["findings"]:
        lines.append("No over-bite stands out — every refusal on the record "
                     "reads as backpressure working. (If it always does once the "
                     "gates judge un-vetted work, these sensors are not yet doing "
                     "their job — §10.)")
        return "\n".join(lines)
    by_kind = defaultdict(list)
    for f in d["findings"]:
        by_kind[f["kind"]].append(f)
    titles = {
        "flapping-gate": "## Flapping gates — a tooth contradicting itself on live work",
        "owner-override": "## Owner overrides — a tooth that bit work bdo wanted",
        "stale-park": "## Stale parks — a healed bite still surfaced as open",
    }
    for kind in KIND_ORDER:
        items = by_kind.get(kind)
        if not items:
            continue
        lines.append(titles[kind])
        for f in items:
            lines.append(f"- `{f['subject']}`")
            for ev in f["evidence"]:
                lines.append(f"    · {ev}")
            lines.append(f"    → {f['move']}")
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--json", action="store_true",
                    help="emit the raw dataset (machine-readable), not the prose")
    args = ap.parse_args(argv)

    d = heal(args.root)
    if args.json:
        print(canon(d))
    else:
        print(render(d))
        print()
    n = len(d["findings"])
    if n:
        kinds = ", ".join(f"{k}×{v}" for k, v in sorted(d["counts"].items()))
        print(f"result: report — {n} over-bite finding(s) [{kinds}]; "
              f"each carries one heal move (the heal is yours, D-4)")
    else:
        print("result: done — no over-bite on the current sensors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
