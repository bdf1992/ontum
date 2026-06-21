#!/usr/bin/env python3
"""The authority dial (epic.owner-harness): the keystone to the autonomous-
authorship button.

bdo, 2026-06-21: *"ask-forgiveness = risk-tiered authority dial (reversible ->
act + FYI, irreversible -> ask)."* Opening the autonomous-authorship button is
not "let the agent do anything" — it is bounding WHAT THE WORLD MAY BECOME
without bdo in the loop, so most reversible motion never reaches him and what
does is rare and shaped. The dial is that bound.

It COMPOSES, it does not re-derive (§10):
  - `observe.gate` (the consequence-gate) asks the FIRST question — is the act
    OBSERVABLE? can its effect be traced home to its actor? An act that cannot
    name its receipt path halts and never runs; the dial never routes it.
  - the dial asks the NEXT question over the SAME declaration: given an
    observable, declared act, may it ACT-AND-FYI (proceed unattended, leave its
    receipt, surface as an after-the-fact notice), or must it ASK-FIRST (stop
    and request bdo's stamp before it runs)?

The routing is by CONSEQUENCE, not action (the consequence-policy model): never
"what verb is this" but "what may the world become, and can that be undone."
Two axes, both read off the act's own declaration:
  - reversible   the act declares a real undo (a rollback that undoes, not
                 "irreversible" / "none")
  - blast        what the act's effect can reach. LOW = only its own declared
                 scope; HIGH = a shared or owner-critical surface (the trunk,
                 the viewport, the network/outside world, money, identity/
                 persona, deletion, another worker's bench).

DEFAULT-SAFE, and the default is mine to set (bdo: *"set the default and give me
an owner's manual — this isn't ikea, it's apple"*). The dial ACTS-AND-FYI only
when the act is, all at once: **observable, reversible, low-blast, and advancing
a confirmed arc.** ANY doubt -> ask-first. A new, partial, undeclared,
irreversible, high-blast, or off-arc act asks first, every time. The owner
widens or narrows this with ONE gesture (`admit-tiers --by bdo`); the owner's
manual (`docs/culture/the-administrator.md`) names every knob. The tiers are an
admitted setpoint, never a code constant (the setpoints law); `DEFAULT_TIERS` is
the safe fallback used until bdo admits his own.

Pure stdlib, no network. `classify` is a pure function the §10 teeth drive.
CLI ends with a clear result on stdout (D-6): done | report.
"""

import argparse
import json
import sys
from pathlib import Path

from loop import observe

AUTHORITY_DIAL = "authority.tiers"
ACT_AND_FYI = "act_and_fyi"
ASK_FIRST = "ask_first"

# The high-blast surfaces — what, if an act's effect can reach it, forces
# ask-first regardless of reversibility. Substring markers matched against the
# act's declared reach. Conservative and default-safe: when in doubt the act is
# treated as high-blast. bdo tunes this list with `admit-tiers`.
DEFAULT_HIGH_BLAST = [
    "main", "origin/main", "trunk",                  # the shared trunk
    "viewport",                                      # bdo's reading surface
    "network", "egress", "internet", "http", "email", "send",  # the outside world
    "money", "payment", "purchase", "charge",        # money
    "identity", "persona", "as bdo", "voice",        # acting AS the owner
    "delete", "destroy", "overwrite",                # destruction
    "another bench", "another workstation", "foreign-worktree",  # another worker's bench
    "owner-surface", "confirm-arc",                  # the owner's own gates
]

# The dial's default settings — what I set so it works out of the box. Each is
# a knob bdo can move; until he admits his own, these conservative values hold.
DEFAULT_TIERS = {
    "high_blast": DEFAULT_HIGH_BLAST,
    "require_reversible": True,  # an irreversible act always asks first
    "require_arc": True,         # only an act advancing a CONFIRMED arc runs unattended
}
TIER_KEYS = tuple(DEFAULT_TIERS)

# rollback declarations that mean "there is no undo" — an act whose rollback
# path is one of these is NOT reversible (it asks first).
_NO_UNDO = ("irreversible", "no rollback", "none", "cannot", "permanent",
            "no undo", "unrecoverable")


def read_tiers(admissions):
    """The active authority tiers, folded from the log (the setpoints law): the
    latest admitted `authority.tiers` setpoint wins, falling back to
    DEFAULT_TIERS, and PER KEY when an admission is partial — so a half-set dial
    never drops a guard and can never widen past the safe default by omission."""
    value = dict(DEFAULT_TIERS)
    for adm in admissions:
        if adm.get("type") == "setpoint" and adm.get("dial") == AUTHORITY_DIAL:
            v = adm.get("value")
            if isinstance(v, dict):
                for k in TIER_KEYS:
                    if k in v:
                        value[k] = v[k]
    return value


def active_tiers(root):
    """The authority tiers folded from `root`'s log, default-safe on any error
    (a bad read must never widen authority — it falls back to the safe floor).
    `root` is the `.ai-native` directory."""
    try:
        from loop.reconcile import Fold
        return read_tiers(Fold(root).admissions)
    except Exception:
        return dict(DEFAULT_TIERS)


def admit_tiers(root, value, by, supersedes=None):
    """Append an `authority.tiers` setpoint admission — bdo's one gesture to
    widen or narrow the dial (D-4: a node never sets its own authority). Mirrors
    the watcher/orchestrate setpoint pens; the dial reads it at runtime, never a
    constant. `root` is the `.ai-native` root."""
    from loop.reconcile import append_line, canon, now_ts, short_hash
    adm = {
        "id": "adm." + short_hash(AUTHORITY_DIAL, canon(value), str(by), now_ts()),
        "type": "setpoint",
        "dial": AUTHORITY_DIAL,
        "value": value,
        "by": by,
        "supersedes": supersedes,
        "ts": now_ts(),
    }
    append_line(root / "log" / "admissions.jsonl", adm)
    return adm


def _reaches_high_blast(declaration, high_blast):
    """Whether the act's declared reach touches a high-blast surface. The reach
    is read from the act's own words — its `blast` list if given, else its
    `scope` (the consequence-gate field). Default-safe: an act that declares NO
    reach cannot prove it is contained, so it reads as high-blast (asks first)."""
    reach = declaration.get("blast")
    if reach is None:
        reach = declaration.get("scope")
    if not reach:
        return True  # undeclared reach -> cannot prove containment -> high
    text = " ".join(reach) if isinstance(reach, (list, tuple)) else str(reach)
    text = text.lower()
    return any(str(m).strip().lower() in text for m in high_blast if str(m).strip())


def _is_reversible(declaration):
    """Whether the act declares a real undo. Prefers an explicit `reversible`
    bool; else reads the `rollback_path` the consequence-gate already requires
    and refuses the words that mean 'no undo'. Default-safe: absent / ambiguous
    reads as NOT reversible (asks first)."""
    if "reversible" in declaration:
        return bool(declaration["reversible"])
    rb = str(declaration.get("rollback_path") or "").strip().lower()
    if not rb:
        return False
    return not any(w in rb for w in _NO_UNDO)


def classify(declaration, tiers=None, arc_confirmed=None):
    """Route one declared act: ACT_AND_FYI (proceed unattended, FYI after) or
    ASK_FIRST (stop, request bdo's stamp). Pure. Returns (route, reason).

    Order is the doctrine's — Observable FIRST. An act the consequence-gate
    would halt (cannot be traced home) is never eligible to run unattended; it
    asks first, naming the halt. Only over an observable act does the dial weigh
    reversibility x blast x arc, and ACT_AND_FYI requires ALL of: observable,
    reversible, low-blast, in a confirmed arc. Any single failure -> ask first.

    `arc_confirmed` answers 'does this advance an arc bdo confirmed?' — the
    caller (the Administrator) resolves it from the log; when None it reads the
    declaration's own `arc_confirmed`. Default-safe: unknown -> not confirmed.
    """
    tiers = tiers or DEFAULT_TIERS
    decl = declaration if isinstance(declaration, dict) else {}

    verdict = observe.gate(decl)
    if not verdict["cleared"]:
        return (ASK_FIRST, f"not observable -> {verdict['halt_reason']}")

    if tiers.get("require_reversible", True) and not _is_reversible(decl):
        return (ASK_FIRST, "irreversible: the act declares no undo path, so its "
                           "consequence could not be revisited — it asks first")

    if _reaches_high_blast(decl, tiers.get("high_blast", DEFAULT_HIGH_BLAST)):
        return (ASK_FIRST, "high blast-radius: the act's reach touches a shared "
                           "or owner-critical surface — it asks first")

    if tiers.get("require_arc", True):
        in_arc = decl.get("arc_confirmed") if arc_confirmed is None else arc_confirmed
        if not in_arc:
            return (ASK_FIRST, "off-arc: the act does not advance an arc bdo "
                               "confirmed — it asks first")

    return (ACT_AND_FYI, "observable, reversible, low blast-radius, advancing a "
                         "confirmed arc — proceeds unattended and surfaces as FYI")


def render_manual(tiers, admitted):
    """The dial in plain words — the owner's manual surface (`python -m
    loop.authority`). States what runs unattended vs asks first, and how to
    change it."""
    src = "admitted by bdo" if admitted else "DEFAULT (none admitted — my safe default)"
    print("the authority dial — what an agent may do WITHOUT asking bdo first")
    print(f"  settings: {src}")
    print()
    print("  an act PROCEEDS UNATTENDED (acts, leaves a receipt, surfaces as FYI)")
    print("  only when it is ALL of:")
    print("    - observable   its effect can be traced home (the consequence-gate)")
    print(f"    - reversible   it declares a real undo   [require_reversible={tiers.get('require_reversible')}]")
    print("    - low-blast    its reach touches only its own scope, none of:")
    hb = tiers.get("high_blast", DEFAULT_HIGH_BLAST)
    print("                     " + ", ".join(str(m) for m in hb))
    print(f"    - in a confirmed arc   bdo already greenlit the direction   [require_arc={tiers.get('require_arc')}]")
    print()
    print("  ANYTHING ELSE asks first — a new, partial, undeclared, irreversible,")
    print("  high-blast, or off-arc act stops and requests your stamp.")
    print()
    print("  to change a knob (D-4, your gesture):")
    print("    python -m loop.authority admit-tiers --by bdo \\")
    print("      --value '{\"require_arc\": false}'        # e.g. allow off-arc reversible motion")
    print("    (high_blast is the full list to widen/narrow what counts as high-blast)")


def main(argv=None):
    from loop.reconcile import DEFAULT_ROOT, canon
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd")

    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT,
                    help="the .ai-native root the tiers are read from")
    ap.add_argument("--json", dest="as_json", action="store_true",
                    help="emit the active tiers as data")

    pa = sub.add_parser("admit-tiers", help="set the dial (bdo only, D-4)")
    pa.add_argument("--value", required=True, metavar="JSON",
                    help='the tier keys to set, e.g. \'{"require_arc": false}\'')
    pa.add_argument("--by", required=True, help="who sets it (D-4: bdo)")
    pa.add_argument("--root", type=Path, default=DEFAULT_ROOT)

    args = ap.parse_args(argv)

    if args.cmd == "admit-tiers":
        value = json.loads(args.value)
        unknown = [k for k in value if k not in TIER_KEYS]
        if unknown:
            print(f"result: needs-you — unknown tier key(s): {', '.join(unknown)}"
                  f"; the knobs are {', '.join(TIER_KEYS)}")
            return 2
        adm = admit_tiers(args.root, value, args.by)
        print(f"result: report — authority tiers {adm['id']} admitted by "
              f"{args.by}: {canon(value)}")
        return 0

    tiers = active_tiers(args.root)
    admitted = tiers != DEFAULT_TIERS
    if args.as_json:
        print(json.dumps({"tiers": tiers, "admitted": admitted,
                          "act_and_fyi_requires": ["observable", "reversible",
                                                   "low_blast", "in_confirmed_arc"]},
                         indent=2, ensure_ascii=False))
        print("result: done — the active authority tiers (read-only)")
        return 0
    render_manual(tiers, admitted)
    print("result: done — the authority dial (read-only); change a knob with "
          "`admit-tiers --by bdo`")
    return 0


if __name__ == "__main__":
    sys.exit(main())
