#!/usr/bin/env python3
"""The inference config + authorization plane (done-line 0062, epic.inference-gateway).

The control plane of a governed local inference plane, as admitted records on
the log — never a YAML/file outside it (the substrate's first law). Three
record kinds, all bdo-signed and superseded-never-erased, all folded at call
time by the gateway pen (`.claude/skills/gateway/gateway.py`, the data plane):

  mind    — a registered backing (loop/minds.py, the sibling): where a mind
            lives + which served model answers there.
  route   — the selection + fallback order across minds: an ordered list,
            primary first. Adding a backing to the order is one record, not a
            code edit; one stamp re-steers it.
  policy  — the RBAC rule set: (caller, surface, mind) -> permit/refuse,
            default-deny. The same record shape as the rest of the config
            plane (0062 piece 6: "the rule set admitted records of the same
            shape as the config plane"). Identity is a caller's node_real
            admission + its trust-ladder rungs as roles (loop/trust.py); the
            policy is bdo asserting that role at a surface for a mind.

Two rules are *already in code* and fold in beneath the policy set:
  - D-2's which-mind axis — a mind may not be asked to judge output its own
    backing wrote (loop/minds.judge_refusal); the first rule, here honoured
    in `authorize`.
  - the trust ladder — `loop/trust.permits`; a tightening axis named, not yet
    hard-required (a class with no rung is denied everything once wired).

This module is a pure fold (stdlib only, reads the log, resolves backing
*references* with no network — env/file/profile reads are local). It WRITES
only config admissions, exactly as loop/minds.py and loop/reflect.py do.
Outward reach — the HTTP completion itself — lives only in the gateway pen,
never here (the loop/ no-network hard rule). result: report.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT, Fold, append_line, now_ts, short_hash

GRANTOR = "bdo"  # route and policy are config; one stamp re-steers, D-4
DEFAULT_ROUTE = "default"
WILDCARD = "*"

# Backing reference schemes the gateway can resolve to a normalized
# OpenAI-compatible base url. Mirrors loop/minds.REFERENCE_SCHEMES; the
# normalization is pure (env/file/profile are local reads, no network).
REFERENCE_SCHEMES = ("http://", "https://", "env:", "profile:", "odysseus://", "file:")


# ----------------------------------------------------------------- folds

def routes(fold):
    """Latest route admission per name wins; a superseded id drops out."""
    superseded = {a["supersedes"] for a in fold.admissions if a.get("supersedes")}
    out = {}
    for adm in fold.admissions:
        if (adm.get("type") == "route" and adm.get("route")
                and adm.get("id") not in superseded):
            out[adm["route"]] = adm
    return out


def resolve_order(fold, route=DEFAULT_ROUTE):
    """The ordered mind-id list for a route (primary first), or [] if the
    route is unset. The selection + fallback order, folded at call time."""
    adm = routes(fold).get(route)
    return list(adm.get("order", [])) if adm else []


def policies(fold):
    """Active policy admissions (superseded dropped), in admission order."""
    superseded = {a["supersedes"] for a in fold.admissions if a.get("supersedes")}
    return [a for a in fold.admissions
            if a.get("type") == "policy" and a.get("id") not in superseded]


def _matches(rule_value, actual):
    """A policy field matches the actual value if it is the wildcard or equal."""
    return rule_value == WILDCARD or rule_value == actual


def authorize(fold, caller, surface, mind, writing_mind=None):
    """May this (caller, surface, mind) inference proceed? Returns
    (permit: bool, reason: str). The policy enforcement point, default-deny:

      1. D-2 which-mind axis first (the rule already in code) — a mind never
         judges its own backing's output, even across an API.
      2. RBAC over the admitted policy set: an explicit deny wins; else a
         matching permit allows; else default-deny (no thought without a
         permitting policy — the no-bypass invariant's authorization half).
    """
    if writing_mind is not None and mind == writing_mind:
        return (False, f"{mind} may not judge its own backing's output — no one "
                "signs their own line, even across an API (D-2)")
    matched_permit = matched_deny = None
    for p in policies(fold):
        if (_matches(p.get("caller"), caller) and _matches(p.get("surface"), surface)
                and _matches(p.get("mind"), mind)):
            if p.get("permit"):
                matched_permit = p
            else:
                matched_deny = p
    if matched_deny is not None:
        return (False, f"a policy denies ({caller}, {surface}, {mind}) "
                f"[{matched_deny['id']}]")
    if matched_permit is not None:
        return (True, f"permitted by {matched_permit['id']}")
    return (False, f"default-deny: no policy permits ({caller}, {surface}, {mind}) "
            "— RBAC admits no thought without a rule (0062 piece 6)")


def normalize_backing(backing, model=None, env=None):
    """Resolve a backing *reference* to a normalized completion target —
    {scheme, base_url, model} — with no network (env/file/profile are local
    reads). Raises ValueError on an unresolvable reference. This is the pure
    half of 0062 piece 3 ("resolves any backing scheme"); the HTTP POST itself
    is the gateway pen's, never here.
    """
    env = os.environ if env is None else env
    b = (backing or "").strip()
    if not b:
        raise ValueError("empty backing reference")
    low = b.lower()
    if low.startswith(("http://", "https://")):
        base = b
        scheme = "http"
    elif low.startswith("odysseus://"):
        # odysseus serves an OpenAI-compatible API; map host[:port] -> http base
        base = "http://" + b[len("odysseus://"):].rstrip("/") + "/v1"
        scheme = "odysseus"
    elif low.startswith("env:"):
        name = b[len("env:"):]
        val = env.get(name)
        if not val:
            raise ValueError(f"env reference {name!r} is unset — no backing to resolve")
        base = val.strip()
        scheme = "env"
    elif low.startswith("file:"):
        path = Path(b[len("file:"):])
        if not path.exists():
            raise ValueError(f"file reference {path} does not exist")
        base = path.read_text(encoding="utf-8").strip()
        scheme = "file"
    elif low.startswith("profile:"):
        name = b[len("profile:"):]
        val = env.get("ONTUM_PROFILE_" + name.upper().replace("-", "_"))
        if not val:
            raise ValueError(f"profile {name!r} has no ONTUM_PROFILE_{name.upper()} "
                             "backing in the environment")
        base = val.strip()
        scheme = "profile"
    else:
        raise ValueError(f"unknown backing scheme — name one of {REFERENCE_SCHEMES}")
    if not base.lower().startswith(("http://", "https://")):
        raise ValueError(f"resolved backing {base!r} is not an http(s) endpoint")
    return {"scheme": scheme, "base_url": base.rstrip("/"), "model": model}


# ----------------------------------------------------------------- write pens

def route_refusal(name, order, by):
    """Why a route may not be set, or None. Pure over its inputs (the
    placement/trust test pattern)."""
    if not name:
        return "a route needs a name (e.g. 'default')"
    if not order or not all(isinstance(m, str) and m for m in order):
        return "a route is an ordered, non-empty list of mind ids (primary first)"
    if (by or "").strip().lower() != GRANTOR:
        return (f"routes are {GRANTOR}'s to steer — --by must be {GRANTOR} "
                "(the selection/fallback order is config; one stamp re-steers it)")
    return None


def set_route(root, name, order, by, supersedes=None):
    reason = route_refusal(name, order, by)
    if reason:
        print(f"result: needs-you — {reason}")
        return None
    adm = {
        "id": "adm." + short_hash("route", name, "|".join(order), str(by), now_ts()),
        "type": "route",
        "route": name,
        "order": list(order),
        "by": by,
        "supersedes": supersedes,
        "ts": now_ts(),
    }
    append_line(root / "log" / "admissions.jsonl", adm)
    return adm


def policy_refusal(caller, surface, mind, by):
    """Why a policy may not be admitted, or None."""
    if not caller or not surface or not mind:
        return "a policy names (caller, surface, mind) — any may be '*' to widen"
    if (by or "").strip().lower() != GRANTOR:
        return (f"policies are {GRANTOR}'s to set — --by must be {GRANTOR} "
                "(RBAC is governance; the rule set is the owner's, D-4)")
    return None


def set_policy(root, caller, surface, mind, permit, by, supersedes=None):
    reason = policy_refusal(caller, surface, mind, by)
    if reason:
        print(f"result: needs-you — {reason}")
        return None
    adm = {
        "id": "adm." + short_hash("policy", caller, surface, mind,
                                  "permit" if permit else "deny", str(by), now_ts()),
        "type": "policy",
        "caller": caller,
        "surface": surface,
        "mind": mind,
        "permit": bool(permit),
        "by": by,
        "supersedes": supersedes,
        "ts": now_ts(),
    }
    append_line(root / "log" / "admissions.jsonl", adm)
    return adm


# ----------------------------------------------------------------- read CLI

def status_lines(root):
    fold = Fold(root)
    from loop import minds as minds_mod
    mns = minds_mod.registered_minds(fold)
    rts = routes(fold)
    pols = policies(fold)
    lines = ["the inference config plane (folded from the log):"]
    lines.append(f"  minds ({len(mns)}):")
    for mid, adm in sorted(mns.items()):
        lines.append(f"    {mid} [{adm.get('family')}] -> {adm.get('backing')}"
                     + (f" ({adm.get('model')})" if adm.get("model") else ""))
    lines.append(f"  routes ({len(rts)}):")
    for name, adm in sorted(rts.items()):
        lines.append(f"    {name}: " + " -> ".join(adm.get("order", [])))
    lines.append(f"  policies ({len(pols)}):")
    for p in pols:
        verb = "permit" if p.get("permit") else "DENY"
        lines.append(f"    {verb} ({p.get('caller')}, {p.get('surface')}, {p.get('mind')})")
    return lines


def cmd_status(ns):
    for line in status_lines(ns.root):
        print(line)
    print("result: report — the config plane is a fold over the log; "
          "adding a backing or re-steering is one admitted record (--by bdo)")
    return 0


def cmd_route(ns):
    adm = set_route(ns.root, ns.name, ns.order, ns.by, ns.supersedes)
    if adm is None:
        return 2
    print(f"result: report — {adm['id']}: route {ns.name} = "
          + " -> ".join(ns.order) + f" (by {ns.by})")
    return 0


def cmd_policy(ns):
    permit = not ns.deny
    adm = set_policy(ns.root, ns.caller, ns.surface, ns.mind, permit, ns.by, ns.supersedes)
    if adm is None:
        return 2
    verb = "permit" if permit else "DENY"
    print(f"result: report — {adm['id']}: {verb} "
          f"({ns.caller}, {ns.surface}, {ns.mind}) (by {ns.by})")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    st = sub.add_parser("status", help="show the config plane (read-only)")
    st.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    st.set_defaults(func=cmd_status)

    rt = sub.add_parser("route", help="set a route's selection/fallback order (bdo only)")
    rt.add_argument("--name", default=DEFAULT_ROUTE, help="route name (default 'default')")
    rt.add_argument("--order", nargs="+", required=True, help="mind ids, primary first")
    rt.add_argument("--by", required=True, help="who steers it (D-4: bdo)")
    rt.add_argument("--supersedes", default=None)
    rt.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    rt.set_defaults(func=cmd_route)

    po = sub.add_parser("policy", help="grant or deny (caller, surface, mind) (bdo only)")
    po.add_argument("--caller", required=True, help="agent class / node id / '*'")
    po.add_argument("--surface", required=True, help="surface name / '*'")
    po.add_argument("--mind", required=True, help="mind id / '*'")
    po.add_argument("--deny", action="store_true", help="set a deny rule (default permit)")
    po.add_argument("--by", required=True, help="who sets it (D-4: bdo)")
    po.add_argument("--supersedes", default=None)
    po.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    po.set_defaults(func=cmd_policy)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
