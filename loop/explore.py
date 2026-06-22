#!/usr/bin/env python3
"""The explore lobe (done-line 0140): research over priors that pays out in
one pointed call to action — read-only, propose-only.

Every part this repo grew is an uncertainty-*terminator*: a gate cuts
(yes/no/amend), a fold collapses a span to a verdict, `term_economy`
forces a term into one class, the grip discipline refuses the unproven,
the owner's stamp is the final cut. That is a fully-built convergent
(exploit) lobe and no divergent (explore) one. This module is the missing
half: pointed at a purpose+goal, it researches over priors and emits one
pointed call to action — *marked, proposed-tier, never minted* — that
moves the system toward that goal without closing the future.

The forward-looking twin of `loop/gaps.py`. Where gaps emits calls to
action from the *certain present* (a mock stage, a parked atom — the
maintenance backlog), this emits them from *research over priors toward a
goal* (the opportunity frontier). Same output shape (a move worth making);
opposite lobe feeding it.

The payout is not capital. Capital is the future banked — the most
aggressive terminator there is, one point of one axis. The payout is
*motion*: a call to action is the draw that never spends the principal —
you act *into* the uncertainty and the volume stays whole.

The teeth (§10), reusing causality's resolver with no second truth: a call
to action must cite real **antecedents** — each a `file:line` /
log-record substring that `causality.term_economy.resolve_evidence`
confirms is committed on disk. A candidate move whose antecedents do not
resolve is REFUSED as ungrounded — no antecedent, no call to action (the
ghost refusal causality already makes). A fabricated/constant emitter
cannot pass, because its citations resolve to nothing.

Read-only and propose-only throughout (D-4): it never judges, stamps,
mints, or writes the log. It names the move; taking it stays a session's
or bdo's. The three forks of `epic.explore-lobe` are NOT resolved here:
this slice takes a *handed* purpose (an epic id or an outcome slug) — the
minimal path common to both branches of fork 1 (even a self-aiming part
must act on a given purpose); whether it self-aims (1), the manifold's
true axes (2), and whether a call to action leaves a marked trace (3) stay
bdo's to settle.

CLI:
  python -m loop.explore epic.<id>          one call to action toward an arc
  python -m loop.explore <outcome-slug>     ...or toward an outcome
  python -m loop.explore <purpose> --json   the raw dataset (machine-readable)

Stdlib only, no network, no git (loop/'s law). Ends with a clear result on
stdout (D-6): done | report | needs-you.
"""

import argparse
import json
import sys
from pathlib import Path

from loop.reconcile import (DEFAULT_ROOT, Fold, arc_confirmation, canon,
                            load_atoms, load_epics)
from causality.term_economy import resolve_evidence

# forward-move kinds, highest leverage first — the frontier the fold reads
KIND_ORDER = ("announce-piece", "advance-parked", "ready-for-confirm",
              "open-question")

# the provenance tier every emitted field carries — the grip floor: marked,
# never `minted`. The explore lobe holds; it never claims.
PROPOSED = "proposed"


# ---------------------------------------------------------------------------
# pointing the part: a purpose is an epic id or an outcome slug
# ---------------------------------------------------------------------------

def resolve_purpose(root, purpose):
    """Point the part. Returns ('epic', epic) | ('outcome', rel, slug) |
    None — no purpose, no pointed action (the part is pointed, never free)."""
    for epic in load_epics(root):
        if epic.get("id") == purpose:
            return ("epic", epic)
    odir = Path(root).resolve().parent / "outcomes"
    if odir.exists():
        for p in sorted(odir.glob("*.md")):
            if p.stem == purpose or p.stem.startswith(purpose):
                return ("outcome", f"outcomes/{p.name}", p.stem)
    return None


# ---------------------------------------------------------------------------
# research over priors: the move worth making toward the goal
# ---------------------------------------------------------------------------

def derive_move(root, epic):
    """The single highest-leverage forward move toward the epic's horizon,
    read from the frontier between what the arc claims and what the record
    shows. Returns (kind, subject, move)."""
    pieces = epic.get("pieces", [])
    eid = epic["id"]
    atom_ids = {a["id"] for a, _ in load_atoms(root)}

    # 1 announce-piece: a piece the arc names whose atom is not yet on the
    #   record — the pipeline has not started toward it. The forward move.
    for p in pieces:
        aid = p.get("atom")
        if aid and aid not in atom_ids:
            return ("announce-piece", aid,
                    f"announce {aid} — the arc names it as a piece and (if a "
                    "done-line is among the antecedents) its bar is set, but "
                    "no atom is on the record yet. Announcing it starts the "
                    "pipeline toward the arc's horizon. Forward: the move is "
                    "not on the log — it is the next opening, not a fix.")

    # 2 advance-parked: a piece atom a gate refused, holding (the gaps fold).
    from loop.gaps import parked_piece_gaps
    parked = {g["subject"]: g for g in parked_piece_gaps(root)}
    for aid in sorted({p.get("atom") for p in pieces if p.get("atom")} & set(parked)):
        return ("advance-parked", aid,
                f"advance {aid} — {parked[aid]['why']}. The forward move is to "
                "amend the atom (a new version restarts the pipeline) toward "
                "the arc's horizon.")

    # 3 ready-for-confirm: every piece announced, none parked, arc unconfirmed.
    if arc_confirmation(Fold(root), eid) is None:
        return ("ready-for-confirm", eid,
                f"every piece of {eid} is announced and none is parked; the "
                "forward move is bdo's confirm-arc, which authorizes the loop "
                "to carry the remaining pieces toward the horizon.")

    # 4 open-question: confirmed and announced — the frontier is the open fork.
    return ("open-question", eid,
            f"{eid} is confirmed and its pieces are announced; the frontier is "
            "now its open question — surface the first unresolved fork to bdo "
            "rather than guessing it (a fork is bdo's to settle).")


# ---------------------------------------------------------------------------
# the prior lenses: candidate antecedents from log, folds, docs, graph
# ---------------------------------------------------------------------------

def _graph_antecedents(epic):
    """The causality relation graph as a prior: a term whose name appears in
    the arc's text, cited to its declared evidence (a real file:substring).
    Lazy + best-effort — a missing graph is an absence, not a crash."""
    text = json.dumps(epic)
    try:
        from causality.term_economy import DEFAULT_SEED, load_seed
        seed = load_seed(DEFAULT_SEED)
    except Exception:  # noqa: BLE001 — absence is information, never a crash
        return []
    out = []
    for t in seed.get("terms", []):
        name = t.get("term")
        if name and name in text:
            for e in t.get("evidence", []):
                if e.get("file") and e.get("contains"):
                    out.append({"file": e["file"], "contains": e["contains"],
                                "source": f"causality:{name}"})
                    break
    return out


def antecedent_candidates(root, epic, subject):
    """Every prior that might ground a move toward `subject`, from the four
    lenses the done-line names — the log, the deterministic folds, the arc
    document, and the causality relation graph. These are *candidates*;
    `ground` keeps only the ones that resolve on disk."""
    eid = epic["id"]
    erel = f".ai-native/epics/{eid}.json"
    cands = [
        # the arc document: the purpose's own bytes name the subject and itself
        {"file": erel, "contains": subject, "source": "arc-doc"},
        {"file": erel, "contains": eid, "source": "arc-doc"},
    ]
    # the bar: a frozen done-line whose text names the subject
    ddir = Path(root) / "done"
    for p in sorted(ddir.glob("*.md")):
        try:
            if subject in p.read_text(encoding="utf-8", errors="replace"):
                cands.append({"file": f".ai-native/done/{p.name}",
                              "contains": subject, "source": "done-line"})
                break
        except OSError:
            continue
    # the log: an append-only record that already mentions the subject
    cands.append({"file": ".ai-native/log/events.jsonl",
                  "contains": subject, "source": "log"})
    cands.append({"file": ".ai-native/log/receipts.jsonl",
                  "contains": subject, "source": "log"})
    # the deterministic folds + the causality graph
    cands.extend(_graph_antecedents(epic))
    return cands


# ---------------------------------------------------------------------------
# the teeth: a call to action must be grounded, or it is refused
# ---------------------------------------------------------------------------

def ground(repo_root, candidate):
    """Resolve a candidate move's antecedents against committed bytes and
    keep only the real ones. With at least one resolving, the call to action
    is emitted, marked proposed-tier. With none, it is REFUSED as ungrounded
    — no antecedent, no call to action (the ghost refusal, reused from
    causality so there is one resolver, not two)."""
    resolved, unresolved = [], []
    for ev in candidate.get("antecedents", []):
        r = resolve_evidence(repo_root, ev)
        (resolved if r.get("resolved") else unresolved).append(
            {**ev, "resolved": bool(r.get("resolved"))})
    if not resolved:
        return {
            "kind": "refused-ungrounded",
            "subject": candidate.get("subject"),
            "toward": candidate.get("toward"),
            "why": ("no cited antecedent resolves on disk — no antecedent, no "
                    "call to action (the ghost refusal causality makes)"),
            "unresolved": unresolved,
            "provenance": PROPOSED,
            "grounded": False,
        }
    return {
        "kind": candidate["kind"],
        "subject": candidate["subject"],
        "move": candidate["move"],
        "toward": candidate.get("toward"),
        "antecedents": resolved,
        "dropped": unresolved,
        "provenance": PROPOSED,
        "grounded": True,
    }


def call_to_action(root, purpose):
    """The fold: point at a purpose, research over priors, emit one marked
    call to action — or refuse if the purpose or its antecedents do not
    ground. Writes nothing."""
    res = resolve_purpose(root, purpose)
    if res is None:
        return {
            "kind": "needs-purpose", "subject": purpose,
            "why": ("the purpose resolves to no epic or outcome on disk — no "
                    "purpose, no pointed action (the part is pointed, never "
                    "free)"),
            "provenance": PROPOSED, "grounded": False,
        }
    repo_root = Path(root).resolve().parent
    if res[0] == "epic":
        epic = res[1]
        kind, subject, move = derive_move(root, epic)
        candidate = {"kind": kind, "subject": subject, "move": move,
                     "toward": epic["id"],
                     "antecedents": antecedent_candidates(root, epic, subject)}
        return ground(repo_root, candidate)

    # an outcome purpose (v0, minimal but honest): the forward move is its next
    # unmet probe; the antecedent is the outcome's own committed bytes.
    rel, slug = res[1], res[2]
    text = (repo_root / rel).read_text(encoding="utf-8", errors="replace")
    needle = next((ln.strip() for ln in text.splitlines() if ln.strip()), slug)[:24]
    candidate = {
        "kind": "open-question", "subject": slug, "toward": slug,
        "move": (f"research priors toward outcome '{slug}': the forward move "
                 "is to define or advance its next unmet probe — desired "
                 "reality is evidence-bearing, never aspirational prose."),
        "antecedents": [{"file": rel, "contains": needle, "source": "outcome"}],
    }
    return ground(repo_root, candidate)


# ---------------------------------------------------------------------------
# render + CLI
# ---------------------------------------------------------------------------

def render(cta):
    lines = ["# Explore — the next call to action from research over priors",
             "",
             "_the explore lobe: a pointed move toward a purpose, drawn from "
             "priors and marked proposed — never minted, never a verdict "
             "(D-4). The payout is motion, not capital._", ""]
    if not cta.get("grounded"):
        lines.append(f"**Refused — {cta['kind']}**: `{cta.get('subject')}`")
        lines.append(f"  why: {cta.get('why')}")
        for ev in cta.get("unresolved", []):
            lines.append(f"    · unresolved: {ev['file']} ∌ "
                         f"{ev['contains']!r} ({ev['source']})")
        return "\n".join(lines)
    lines.append(f"**Call to action — {cta['kind']}**  → toward `{cta['toward']}`")
    lines.append(f"  subject: `{cta['subject']}`")
    lines.append(f"  move: {cta['move']}")
    lines.append(f"  provenance: {cta['provenance']} (marked, not minted)")
    lines.append("  antecedents (research over priors — each resolves on disk):")
    for ev in cta["antecedents"]:
        lines.append(f"    · {ev['source']}: {ev['file']} ∋ {ev['contains']!r}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("purpose",
                    help="an epic id (epic.<x>) or an outcome slug — the goal "
                         "to point the part at")
    ap.add_argument("--root", type=Path, default=Path(DEFAULT_ROOT))
    ap.add_argument("--json", action="store_true",
                    help="emit the raw dataset (machine-readable), not the prose")
    args = ap.parse_args(argv)

    cta = call_to_action(args.root, args.purpose)
    if args.json:
        print(canon(cta))
    else:
        print(render(cta))
        print()
    if cta.get("grounded"):
        print(f"result: report — one call to action toward {cta['toward']} "
              f"[{cta['kind']}], marked proposed; taking the move stays a "
              "session's or bdo's (D-4)")
    elif cta.get("kind") == "needs-purpose":
        print(f"result: needs-you — '{args.purpose}' resolves to no epic or "
              "outcome; point the part at a real purpose")
    else:
        print("result: report — candidate refused as ungrounded; no antecedent "
              "resolves (no antecedent, no call to action)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
