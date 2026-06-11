#!/usr/bin/env python3
"""The mind registry (atom.model-registry.v0 — epic.experience-layer, wave 2).

Pluggable judging minds as admitted records — the sibling of the surface
registry (loop/reflect.py). A `mind` admission registers a backing that can
judge: local the privileged default (zero disclosure), an external family
(GPT, …) the deliberate, receipted exception. Read here as a pure fold;
admitted through this pen (loop.minds register), bdo-only — registering an
external backing is itself a disclosure event. The backing is a *reference*
(an env handle, a named profile, a URL), never a stored secret. The
no-self-signing line grows a which-mind axis: a mind may not judge output its
own backing wrote, even across an API (D-2).

Stdlib only; reads the log, writes only the admission. result: report.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT, Fold, append_line, now_ts, short_hash

FAMILIES = {
    "local": "a local model backing — the privileged default (zero disclosure)",
    "external": "a registered external family (GPT, …) — the receipted exception",
}
DEFAULT_FAMILY = "local"
GRANTOR = "bdo"  # registering a mind is bdo's — a backing is a disclosure event

# a backing names where a mind lives; it is a reference, never the secret
REFERENCE_SCHEMES = ("env:", "profile:", "http://", "https://", "odysseus://", "file:")
_SECRET_MARKERS = re.compile(r"(sk-[A-Za-z0-9]{8,}|AKIA[0-9A-Z]{12,}|api[_-]?key=)", re.I)


def backing_refusal(backing):
    """Why a backing may not be admitted, or None. Credentials are referenced,
    never stored (I-8): an inline secret is refused, and a backing must name a
    reference scheme."""
    b = (backing or "").strip()
    if not b:
        return "a backing is required — a reference to where the mind lives"
    if _SECRET_MARKERS.search(b):
        return ("that backing carries an inline secret — reference it "
                "(env:NAME or profile:NAME); the record never stores a key")
    if not b.lower().startswith(REFERENCE_SCHEMES):
        return ("a backing is a reference, never a stored secret — name one of: "
                + ", ".join(REFERENCE_SCHEMES))
    return None


def mind_refusal(mind_id, family, backing, by):
    """The pure reasons a mind may not be registered, or None. Hit directly by
    the suite (the placement/trust pattern)."""
    if not mind_id or "." not in mind_id:
        return "a mind id is family.name, e.g. local.llama-3.3-70b or external.gpt-5"
    if family not in FAMILIES:
        return f"unknown family {family!r}; families: " + ", ".join(FAMILIES)
    reason = backing_refusal(backing)
    if reason:
        return reason
    if (by or "").strip().lower() != GRANTOR:
        return (f"minds are {GRANTOR}'s to register — --by must be {GRANTOR} "
                "(registering a backing is a disclosure event, D-4)")
    return None


def register(root, mind_id, family, backing, by, supersedes=None):
    """Admit a mind — the surface-registry sibling. Returns the admission, or
    None on refusal (already printed)."""
    reason = mind_refusal(mind_id, family, backing, by)
    if reason:
        print(f"result: needs-you — {reason}")
        return None
    adm = {
        "id": "adm." + short_hash("mind", mind_id, family, str(backing), str(by), now_ts()),
        "type": "mind",
        "mind": mind_id,
        "family": family,
        "backing": backing,
        "by": by,
        "supersedes": supersedes,
        "ts": now_ts(),
    }
    append_line(root / "log" / "admissions.jsonl", adm)
    return adm


def registered_minds(fold):
    """Latest mind admission per id wins; a superseded id drops out (history
    is superseded, never erased)."""
    superseded = {a["supersedes"] for a in fold.admissions if a.get("supersedes")}
    minds = {}
    for adm in fold.admissions:
        if (adm.get("type") == "mind" and adm.get("mind")
                and adm.get("id") not in superseded):
            minds[adm["mind"]] = adm
    return minds


def judge_refusal(judging_mind, writing_mind):
    """A mind may not judge output its own backing wrote — no one signs their
    own line, across the API too (the which-mind axis of D-2). None means it
    may judge."""
    if judging_mind is not None and judging_mind == writing_mind:
        return (f"{judging_mind} may not judge its own backing's output — no "
                "one signs their own line, even across an API (D-2)")
    return None


# ----------------------------------------------------------------- read CLI

def list_lines(root):
    minds = registered_minds(Fold(root))
    if not minds:
        return ["no minds registered — the registry is empty"]
    return [f"  {mid} [{adm.get('family')}] -> {adm.get('backing')} "
            f"(by {adm.get('by')})" for mid, adm in sorted(minds.items())]


def cmd_list(ns):
    for line in list_lines(ns.root):
        print(line)
    n = len(registered_minds(Fold(ns.root)))
    print(f"result: report — {n} mind(s) registered "
          f"(local is the privileged default)")
    return 0


def cmd_register(ns):
    adm = register(ns.root, ns.mind, ns.family, ns.backing, ns.by, ns.supersedes)
    if adm is None:
        return 2
    print(f"result: report — {adm['id']}: registered {ns.mind} "
          f"[{ns.family}] (by {ns.by})")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    li = sub.add_parser("list", help="show registered minds (read-only)")
    li.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    li.set_defaults(func=cmd_list)
    rg = sub.add_parser("register",
                        help="admit a judging mind (bdo only; backing is a reference)")
    rg.add_argument("--mind", required=True, help="family.name, e.g. local.llama-3.3-70b")
    rg.add_argument("--family", default=DEFAULT_FAMILY, help="local | external (default local)")
    rg.add_argument("--backing", required=True,
                    help="a reference: env:NAME / profile:NAME / https://… / odysseus://…")
    rg.add_argument("--by", required=True, help="who registers it (D-4: bdo)")
    rg.add_argument("--supersedes", default=None, help="a prior mind admission id this replaces")
    rg.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    rg.set_defaults(func=cmd_register)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
