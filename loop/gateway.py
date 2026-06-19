#!/usr/bin/env python3
"""The ambient gateway — the typed-message door (done-line 0126, The Polity).

The first chapter of **The Polity** (the self-governing-body anthology) and the
smallest landable cut of `ambient-gateway.chapter.md` increment #1: the **door**.

Every message entering the gateway is **typed at the seam before any routing**
(§13.4): a message is matched against a governed registry, and one that is
untyped, of an unknown type, or missing its type's required fields is **refused
→ dead-letter**, naming exactly what is missing. The door that cannot refuse is
a contract that can't gate (§13.9). The PDP/PEP `route()` that generalizes
`inference.authorize`, and the threshold actuator, are increments #2–#3 — out of
this line.

The registry mirrors `loop/tags.py`: a closed **core** in code (the spine) +
admitted **`message_type`** records that extend it (proposed-tier — an unknown
type reads as `proposed` drift, promotable by `admit-type`, never silently
guessed). A type binds `{schema (required fields), gloss}` here; its `route` and
`ingress/egress policy` (§13.4) are declared by later increments, not faked now.

This is the AuthZEN shape built native: the door is the entry of a PEP/PDP/PIP
gateway. **Distinct from the *inference* gateway** (`loop/inference.py` +
`.claude/skills/gateway/`, done-line 0062, tested by `tests/test_gateway.py`):
that is one *flavor* (AuthZ/inference) of the gateway shape; this is the general
typed-message gateway it is an instance of. The name overlap is real and flagged.

Stdlib only, pure fold; the only write is `admit_type`. Outward reach (actual
routing/acting) is a later increment, never here. Ends with a clear
`done | report | needs-you`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT, Fold, append_line, now_ts, short_hash

# ----------------------------------------------------------------- the schema
# The closed core: the message types the gateway knows in code (the spine).
# Each binds the required fields the door checks and a gloss. `tool-request` is
# the routable act (the PIP input — who acts on what, the native AuthZEN
# subject/action/resource); `work-item` is the patrol's find, presented to the
# gateway. Other types (e.g. `chat-message`, §13.4) arrive as admitted
# extensions — a new type is a record, not a code edit.
CORE_TYPES = {
    "tool-request": {
        "required": ("caller", "action", "resource"),
        "gloss": "a request to act on a resource — the routable unit "
                 "(the PIP input: who acts on what)",
    },
    "work-item": {
        "required": ("seam", "subject"),
        "gloss": "a unit of work surfaced near a seam — the patrol's find, "
                 "presented to the gateway",
    },
}

TYPED = "typed"
DEAD_LETTER = "dead-letter"


# --------------------------------------------------------------- the registry
# core + admitted, folded from the log. Mirrors loop/tags.admitted_values.

def admitted_types(fold):
    """Message types admitted beyond core: latest `message_type` admission per
    name wins; a withdrawn one drops out. The proposed→admitted path, on the
    log. A spec is `{required, gloss, by}` carried by the admission."""
    out = {}
    for adm in fold.admissions:
        if adm.get("type") != "message_type":
            continue
        name = adm.get("name")
        if not name:
            continue
        if adm.get("withdrawn"):
            out.pop(name, None)
        else:
            out[name] = {
                "required": tuple(adm.get("required", ())),
                "gloss": adm.get("gloss", ""),
                "by": adm.get("by"),
            }
    return out


def registry(fold):
    """The full message-type registry: the closed core plus admitted
    extensions. Core is the spine — an admission may not shadow a core name
    (refused at admit time; ignored here for robustness)."""
    reg = {name: dict(spec) for name, spec in CORE_TYPES.items()}
    for name, spec in admitted_types(fold).items():
        if name in CORE_TYPES:
            continue  # core is the closed spine
        reg[name] = spec
    return reg


def type_status(fold, name):
    """Where a type stands: `core` (spine), `admitted` (promoted), or
    `proposed` (named but not in the registry — drift, not error). Mirrors
    loop/tags.status_of."""
    if name in CORE_TYPES:
        return "core"
    if name in admitted_types(fold):
        return "admitted"
    return "proposed"


# ------------------------------------------------------------------- the door

def _dead(type_name, status, missing, reason):
    return {
        "outcome": DEAD_LETTER,
        "type": type_name,
        "type_status": status,
        "missing": list(missing),
        "reason": reason,
    }


def type_message(fold, msg):
    """Type a message at the door — purely. Returns a typed result:

        {outcome: 'typed' | 'dead-letter', type, type_status, missing, reason}

    `typed` means the message declares a **registered** type and carries that
    type's **required fields** — ready for the router (increment #2). Every
    other case is a `dead-letter` carrying a reason a cold sender can act on
    (the carry-the-prompt UX, §13.4): not an object, untyped, an unknown type,
    or named missing fields. A field is *missing* when its key is absent or its
    value is empty (`None`/`""`). This is the gate's teeth — the door that
    cannot refuse is a contract, not a contract checker (§13.9)."""
    reg = registry(fold)
    known = ", ".join(sorted(reg))
    if not isinstance(msg, dict):
        return _dead(None, "missing", [],
                     "a message must be a JSON object carrying a `type`")
    name = msg.get("type")
    if not name:
        return _dead(None, "missing", [],
                     f"untyped: a message must declare its `type` "
                     f"(registered: {known})")
    spec = reg.get(name)
    if spec is None:
        return _dead(name, "proposed", [],
                     f"unknown type {name!r}: not in the registry — proposed "
                     f"drift; admit it (loop.gateway admit-type --name {name} "
                     f"--required ... --by <who>) before it may route")
    missing = [f for f in spec.get("required", ()) if not msg.get(f)]
    if missing:
        return _dead(name, type_status(fold, name), missing,
                     f"missing required field(s) for type {name!r}: "
                     + ", ".join(missing))
    return {
        "outcome": TYPED,
        "type": name,
        "type_status": type_status(fold, name),
        "missing": [],
        "reason": f"typed as {name!r} ({type_status(fold, name)}); all "
                  "required fields present",
    }


# ----------------------------------------------------------------- the pen
# The one write: promote a proposed type into the registry (or withdraw it,
# superseding). Signed `--by`, like loop/tags.admit_tag.

def type_refusal(name, by, withdrawn=False):
    """Why a `message_type` admission may not be written, or None. Pure."""
    if not name:
        return "a message type needs a name"
    if not withdrawn and name in CORE_TYPES:
        return (f"{name!r} is a core type — the closed spine; it can't be "
                "re-admitted or shadowed (a core change is a code edit, §7)")
    if not by or not str(by).strip():
        return "an admission is signed — name --by (the registry is governed)"
    return None


def admit_type(root, name, required, gloss, by, withdrawn=False):
    """Admit (or withdraw) a `message_type` record extending the registry."""
    reason = type_refusal(name, by, withdrawn=withdrawn)
    if reason:
        print(f"result: needs-you — {reason}")
        return None
    adm = {
        "id": "adm." + short_hash("message_type", name, "|".join(required or ()),
                                  str(withdrawn), str(by), now_ts()),
        "type": "message_type",
        "name": name,
        "required": list(required or ()),
        "gloss": gloss or "",
        "withdrawn": bool(withdrawn),
        "by": by,
        "ts": now_ts(),
    }
    append_line(root / "log" / "admissions.jsonl", adm)
    return adm


# ----------------------------------------------------------------- the surface

def registry_lines(root):
    fold = Fold(root)
    reg = registry(fold)
    lines = ["the typed-message registry (core + admitted, folded from the log):"]
    for name in sorted(reg):
        spec = reg[name]
        req = ", ".join(spec.get("required", ())) or "(none)"
        lines.append(f"  {name} [{type_status(fold, name)}] — requires: {req}")
        if spec.get("gloss"):
            lines.append(f"      {spec['gloss']}")
    return lines


def cmd_registry(ns):
    for line in registry_lines(ns.root):
        print(line)
    print("result: report — the registry is a fold over the log; a new type is "
          "one admitted record (admit-type --by <who>), never a code edit")
    return 0


def cmd_type(ns):
    """Type one message from the CLI — the door, exercised by hand."""
    try:
        msg = json.loads(ns.json)
    except json.JSONDecodeError as e:
        print(f"result: needs-you — --json is not valid JSON: {e}")
        return 2
    result = type_message(Fold(ns.root), msg)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["outcome"] == TYPED:
        print(f"result: done — {result['reason']}")
        return 0
    print(f"result: report — dead-letter: {result['reason']}")
    return 0


def cmd_admit_type(ns):
    adm = admit_type(ns.root, ns.name, ns.required, ns.gloss, ns.by,
                     withdrawn=ns.withdrawn)
    if adm is None:
        return 2
    verb = "withdrew" if ns.withdrawn else "admitted"
    print(f"result: report — {adm['id']}: {verb} message type {ns.name!r} "
          f"(requires: {', '.join(ns.required or ()) or 'none'}) (by {ns.by})")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    rg = sub.add_parser("registry", help="show the typed-message registry (read-only)")
    rg.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    rg.set_defaults(func=cmd_registry)

    ty = sub.add_parser("type", help="type one message at the door (read-only)")
    ty.add_argument("--json", required=True, help="the message as a JSON object")
    ty.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ty.set_defaults(func=cmd_type)

    at = sub.add_parser("admit-type", help="promote (or --withdraw) a message type")
    at.add_argument("--name", required=True)
    at.add_argument("--required", nargs="*", default=[], help="required field names")
    at.add_argument("--gloss", default="", help="one-line description")
    at.add_argument("--withdraw", dest="withdrawn", action="store_true",
                    help="supersede a prior admission (latest wins)")
    at.add_argument("--by", required=True, help="who admits it (governed, signed)")
    at.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    at.set_defaults(func=cmd_admit_type)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
