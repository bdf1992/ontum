#!/usr/bin/env python3
"""The session gateway — bind-at-birth (issue #534, session-gateway.proposal.md).

The first real chapter of the session gateway. `loop/inference.py` is the proven
template — a real policy-enforcement point over admitted records (default-deny
RBAC). This is its sibling at a different seam: where the inference gateway
authorizes a *thought*, this authorizes a *session* — it binds a session to a
type and hands it the set of tools that type is allowed to use, at birth, as a
signed record, instead of letting the session infer its state from a shared HEAD.

**The portal model (bdo, 2026-06-23).** The workstation manifest is not
documentation — it is a *portal / capability token*. Its PRESENCE in the
workstation is the fact: if a tool's portal line is present, the gateway produced
it and this session is AUTHORIZED to use that tool. The set of portals present IS
the environment this session is capable of using, derived from its type (its
START) and its consequences. This turns the three A's — authenticated,
authorized, attributed — into something physical and checkable.

Three pure parts (the proposal's increment #3, smallest-first):

  derive_type(payload)  — PURE, named, versioned (a typing-fn the binding hash
                          could cover, §10.1 / doctrine §14: a typing-rule change
                          is new lineage, never a silent reinterpretation). Maps a
                          session's birth signals to one of three types:
                            builder       — opened in a worktree bench;
                            node-fill     — a branded `ontum-node:<id>` spawn;
                            steerer-admin — the viewport / primary tree.
                          Honest least-privilege fallback when signals are absent
                          (we never hand steerer powers to a tree we cannot
                          confirm is the viewport).

  bind(...)             — writes ONE `session_binding` admission carrying the
                          three A's (who/what · the authorized capability set ·
                          attributed-to-workspace + --by + ts + typing_version).
                          IDEMPOTENT: an existing binding for a session is REUSED,
                          never blind-recreated — the rescue-branch-sprawl bug the
                          proposal §4/§14 names.

  emit_manifest(...)    — writes the workstation portal(s): the branded tools
                          (folded from `.claude/skills/*/SKILL.md` + `loop/*.py`),
                          each one line, FILTERED by the type's capability set.
                          Presence = authorized.

Capability sets are GOVERNED vocabulary (loop/tags.py pattern): a closed core per
type in code PLUS admitted `session_capability` extensions — a small named
default per type for v0, admitted-extensible, never a frozen code-only constant.

Stdlib only, local-first (loop/'s law). A pure fold over the log; WRITES only
config admissions (`session_binding`, `session_capability`) exactly as
inference.py / tags.py do, plus the generated workstation manifest file (a
deletable, regenerable cache, never truth). Outward reach — actually creating a
new worktree bench — is NOT here (the next increment). Ends with a clear
`done | report | needs-you` line.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT, Fold, append_line, now_ts, short_hash

# loop/session_gateway.py -> loop/ -> repo (or worktree) root.
REPO = Path(__file__).resolve().parent.parent

# ----------------------------------------------------------------- the types
# The closed set of session types. A type is a ROLE, not a privilege ladder —
# each is bounded to a different seam (proposal §5).
BUILDER = "builder"
NODE_FILL = "node-fill"
STEERER_ADMIN = "steerer-admin"
SESSION_TYPES = (BUILDER, NODE_FILL, STEERER_ADMIN)

# The typing function is named and VERSIONED (proposal §10.1 / doctrine §14):
# the binding carries this so a typing-rule change is new lineage, not a silent
# reinterpretation of a settled binding (I-2). Bump on any change to the rules
# in derive_type below.
TYPING_VERSION = "session-type.v0"

# Birth-signal markers for derive_type. A branded node spawn announces itself;
# a worktree bench lives under this path in every checkout.
NODE_BRAND_PREFIX = "ontum-node:"
WORKTREE_MARKER = "/.claude/worktrees/"


def _norm(path):
    """A path normalized for comparison: forward slashes, no trailing slash,
    lowercased (Windows trees are case-insensitive). '' for a falsy input."""
    if not path:
        return ""
    return str(path).replace("\\", "/").rstrip("/").lower()


def derive_type(payload):
    """The PURE, named, versioned typing function (proposal §10.1).

    Maps a session's birth signals to one of SESSION_TYPES. Reads only the
    payload — no git, no network, no clock — so the same signals always derive
    the same type (the equivalence the hash relies on). Signals, in priority:

      1. a branded `ontum-node:<id>` spawn   -> node-fill
      2. a cwd under a worktree bench         -> builder
      3. a cwd we can CONFIRM is the viewport
         (it equals the supplied `primary`)   -> steerer-admin
      4. anything else                         -> builder (the honest floor)

    The floor is least-privilege by design: we never hand steerer (viewport)
    powers to a tree we cannot positively confirm is the viewport, and a builder
    bench is the safe default — its work isolates and lands only through review.
    Detecting the *true* primary (git-dir == git-common-dir) needs git, which
    pure loop/ forbids; the caller (a future hook, with that reach) supplies
    `primary`. Absent it, even the real viewport reads as builder — under-, never
    over-privileging."""
    payload = payload or {}
    brand = str(payload.get("brand") or payload.get("node")
                or payload.get("node_id") or "").strip()
    if brand.startswith(NODE_BRAND_PREFIX):
        return NODE_FILL
    cwd = _norm(payload.get("cwd"))
    primary = _norm(payload.get("primary"))
    if cwd and WORKTREE_MARKER in cwd:
        return BUILDER
    if cwd and primary and cwd == primary:
        return STEERER_ADMIN
    return BUILDER


# ----------------------------------------------------------- capability sets
# Capability TOKENS — the closed vocabulary of what a session may do, by kind:
#   read   — observe / fold (universal across types, but NEVER an unmapped
#            tool's silent default — a tool earns `read` only by being
#            classified read-only in CAPABILITY_BY_TOOL below)
#   build  — produce a code diff in a bench, open a PR (never land it)
#   land   — land work to main (the merge-node's seat — in no default type, by
#            design: no one lands their own line, D-2)
#   judge  — write a verdict / admission into the pipeline
#   steer  — owner-tier steering of the field (arcs, setpoints, fences)
READ, BUILD, LAND, JUDGE, STEER = "read", "build", "land", "judge", "steer"
CAPABILITY_CORE = (READ, BUILD, LAND, JUDGE, STEER)

# The closed CORE capability set per type (proposal: a small named default,
# admitted-extensible). `land` is deliberately in none — the merge-node is an
# independent role a later type names; a default session never lands its own
# work. `build` is in none but builder — the viewport steerer delegates building
# to spawned benches (the workstation fence forbids it building in the viewport).
TYPE_CAPABILITIES = {
    BUILDER: (READ, BUILD),
    NODE_FILL: (READ, JUDGE),
    STEERER_ADMIN: (READ, STEER),
}

# Tool -> the capability it requires. A CLOSED classifier; an unlisted tool gets
# NO capability and therefore NO portal in ANY type's manifest (review #1,
# deny-and-surface — fail CLOSED). The earlier design defaulted the unlisted to
# `read`, and because `read` is core for every type, every unmapped tool —
# including real MUTATING pens (pen.py, web.py, watcher.py, tags.py, rename.py,
# heartbeat.py, reconcile_noise.py, act_fence.py, the issue/continue-probe
# skills) — became an authorized portal in EVERY manifest. The portal model is
# "presence = authorized"; that default over-authorized. So there is no silent
# default now: a read-only fold earns `read` by being LISTED below, and an
# unmapped tool is surfaced by `unmapped_tools()` as a gap to classify ("absence
# is information") — never granted a portal. The cost is the honest one absence
# buys, and the safe direction: a new read-only fold is invisible (a surfaced
# gap) until classified here, where before a new MUTATING pen rode in silently.
# Classifying every fold is the named later increment (the enforced, governed
# tool->capability admission, proposal §14.3); this map is the floor that fails
# closed in the meantime, and is reviewed when any pen lands.
CAPABILITY_BY_TOOL = {
    # read — pure read-only folds (loop/CLAUDE.md describes each as read-only).
    # Listed EXPLICITLY (not defaulted): only a confirmed read-only fold is a
    # read portal. Anything not here (a mutating/ambiguous pen) gets no portal.
    "census": READ,
    "gaps": READ,
    "digest": READ,
    "retro": READ,
    "heal": READ,
    "parity": READ,
    "activity": READ,
    "gradient": READ,
    "forest": READ,
    "consequence_graph": READ,
    "observe": READ,
    "relation_ledger": READ,
    "over_containment": READ,
    "summon": READ,
    "gate_eval": READ,
    "phrasing": READ,
    "pull": READ,
    # build — produce a diff / author work in a bench
    "branch-ritual": BUILD,
    "author-workflow": BUILD,
    "review-workflow": BUILD,
    "envoy": BUILD,
    "session_gateway": BUILD,
    # land — land to main (the merge-node's seat)
    "merge-node": LAND,
    # judge — write a verdict / admission into the pipeline
    "gate": JUDGE,
    "node": JUDGE,
    "realness-intake": JUDGE,
    "rung-intake": JUDGE,
    "policy-intake": JUDGE,
    # steer — owner-tier steering of the field
    "orchestrate": STEER,
    "slowloop": STEER,
    "disposer": STEER,
    "arc-intake": STEER,
    "inference": STEER,
    "inference_queue": STEER,
    "reflect": STEER,
}


def tool_capability(name):
    """The capability a tool requires, or None if UNMAPPED (review #1). There is
    NO silent default: a tool not in CAPABILITY_BY_TOOL gets NO capability and so
    NO portal in any type's manifest (deny-and-surface, fail CLOSED), and is
    surfaced by `unmapped_tools` as a gap to classify. A read-only fold earns
    `read` only by being listed (the loop/tags.py shape — an unclassified thing
    is a visible gap, never a silent grant)."""
    return CAPABILITY_BY_TOOL.get(name)


def unmapped_tools(tools):
    """The branded tools with no CAPABILITY_BY_TOOL entry — DENIED a portal and
    surfaced as gaps to classify (review #1: deny-and-surface). A newly-landed
    MUTATING pen lands here, visible, until it earns a mapping — it can no longer
    ride into every manifest as a read portal (the honest-gap discipline; tags.py
    surfaces unclassified verbs the same way)."""
    return [t for t in tools if t.get("tool") not in CAPABILITY_BY_TOOL]


def _cap_order(adm):
    """The ts-then-id sort key for a session_capability record (deterministic,
    None-safe)."""
    return (adm.get("ts") or "", adm.get("id") or "")


def admitted_capabilities(fold):
    """Extra capabilities admitted per type (beyond core): the LATEST
    `session_capability` per (type, capability) decides — withdrawn drops it,
    admitted grants it. The governed-vocabulary extension path on the log (the
    tags.py pattern).

    UNION-MERGE-SAFE (review #3): two branches' admit/withdraw records merge into
    the log in arbitrary FILE order, so the latest-wins is resolved by `ts`
    (then id), never by file layout — the old fold's `out.get(st, set()).discard`
    was a silent no-op unless the admit happened to precede the withdraw in the
    file, the exact order-dependence union-merge breaks. Withdrawals also carry an
    explicit `supersedes` (see admit_capability), so the revoked admit drops from
    the non-superseded set regardless of order."""
    superseded = {a["supersedes"] for a in fold.admissions if a.get("supersedes")}
    latest = {}
    for adm in fold.admissions:
        if adm.get("type") != "session_capability" or adm.get("id") in superseded:
            continue
        st, cap = adm.get("session_type"), adm.get("capability")
        if not st or not cap:
            continue
        key = (st, cap)
        prev = latest.get(key)
        if prev is None or _cap_order(adm) >= _cap_order(prev):
            latest[key] = adm
    out = {}
    for (st, cap), adm in latest.items():
        if not adm.get("withdrawn"):
            out.setdefault(st, set()).add(cap)
    return out


def _latest_capability_admit(fold, session_type, capability):
    """The live (non-superseded, non-withdrawn) admit for (type, capability),
    latest by ts — what a withdrawal supersedes. None if there is none."""
    superseded = {a["supersedes"] for a in fold.admissions if a.get("supersedes")}
    best = None
    for adm in fold.admissions:
        if (adm.get("type") != "session_capability"
                or adm.get("id") in superseded
                or adm.get("withdrawn")
                or adm.get("session_type") != session_type
                or adm.get("capability") != capability):
            continue
        if best is None or _cap_order(adm) >= _cap_order(best):
            best = adm
    return best


def type_capabilities(fold, session_type):
    """The full capability set of a type: closed core plus admitted extensions.
    The set the manifest filters by."""
    core = set(TYPE_CAPABILITIES.get(session_type, ()))
    return core | admitted_capabilities(fold).get(session_type, set())


def capability_status(fold, session_type, capability):
    """Where a capability stands for a type: core (spine), admitted (extended),
    or absent (neither — not granted)."""
    if capability in TYPE_CAPABILITIES.get(session_type, ()):
        return "core"
    if capability in admitted_capabilities(fold).get(session_type, set()):
        return "admitted"
    return "absent"


# ------------------------------------------------------------- branded tools
def branded_tools(tree):
    """Fold the repo's branded tools off disk — the two surfaces a session
    reaches through: the skills (`.claude/skills/*/SKILL.md`, the ritual brand)
    and the loop pens (`loop/*.py`). Each is one tool carrying the capability it
    requires. Filesystem-derived so a new tool enrolls itself (the census's
    no-hand-list rule). Deterministic order."""
    tree = Path(tree)
    tools = []
    for skill in sorted(tree.glob(".claude/skills/*/SKILL.md")):
        name = skill.parent.name
        tools.append({"tool": name, "kind": "skill",
                      "ref": skill.relative_to(tree).as_posix(),
                      "capability": tool_capability(name)})
    for pen in sorted(tree.glob("loop/*.py")):
        if pen.name == "__init__.py":
            continue
        name = pen.stem
        tools.append({"tool": name, "kind": "pen",
                      "ref": pen.relative_to(tree).as_posix(),
                      "capability": tool_capability(name)})
    return tools


def authorized_tools(tools, capabilities):
    """The portals a capability set opens: the tools whose required capability
    is granted. This is the pure FILTER the portal model rests on — presence in
    this list is what becomes a portal's presence in the workstation. A tool
    whose capability is not in the set is absent, full stop (the §10 tooth)."""
    caps = set(capabilities)
    return [t for t in tools if t.get("capability") in caps]


# ----------------------------------------------------------------- the binding
def existing_binding(fold, session_id):
    """The live `session_binding` for a session, or None. Latest-wins, a
    superseded one drops. This is the idempotence read: a session that already
    has a binding is REUSED, never bound again — the rescue-branch-sprawl bug the
    proposal §4/§14 names (a mortal session re-bound on every blink sprawls)."""
    superseded = {a["supersedes"] for a in fold.admissions if a.get("supersedes")}
    latest = None
    for adm in fold.admissions:
        if (adm.get("type") == "session_binding"
                and adm.get("session_id") == session_id
                and adm.get("id") not in superseded):
            latest = adm
    return latest


def binding_refusal(session_id, session_type, by):
    """Why a binding may not be written, or None (pure, the inference.py shape)."""
    if not session_id:
        return "a binding needs a session id (who is being bound)"
    if session_type not in SESSION_TYPES:
        return (f"unknown session type {session_type!r}; the closed set is "
                f"{', '.join(SESSION_TYPES)} (a type is a role, not free text)")
    if not (by or "").strip():
        return "a binding is signed (--by) like every record on the log"
    return None


def bind(root, session_id, session_type, cwd, by, capabilities=None):
    """Bind a session to a type at birth — ONE `session_binding` admission
    carrying the three A's:
      authenticated — session_id + session_type (who/what)
      authorized    — the type's capability set (what it may use)
      attributed    — workspace (cwd) + by + ts + typing_version (signed,
                      attributable; you cannot attribute what you inferred).

    The capability set is FROZEN into the binding at birth — that is the
    attribution (the set is given and signed, not re-inferred each pulse). A
    capability admitted to the type later reaches an already-bound session only by
    re-issuing the binding; correcting/re-typing a binding is a bounded supersede
    verb (bdo's, the supersede-done shape) named as a later increment — not a
    blind re-create here (proposal §14.3).

    IDEMPOTENT: if a binding already exists for this session it is REUSED and
    NOTHING is written (returns (binding, created=False)) — never blind-recreated.
    Returns (binding, created: bool) on success, or (None, False) on refusal
    (a needs-you is printed)."""
    reason = binding_refusal(session_id, session_type, by)
    if reason:
        print(f"result: needs-you — {reason}")
        return None, False
    fold = Fold(root)
    prior = existing_binding(fold, session_id)
    if prior is not None:
        # the idempotence floor: a session is bound once. Re-binding would sprawl
        # (a new branch/binding per blink) — exactly the failure §4/§14 names.
        return prior, False
    caps = (sorted(capabilities) if capabilities is not None
            else sorted(type_capabilities(fold, session_type)))
    adm = {
        "id": "adm." + short_hash("session_binding", session_id, session_type,
                                  _norm(cwd), str(by), now_ts()),
        "type": "session_binding",
        "session_id": session_id,
        "session_type": session_type,
        "capabilities": caps,
        "workspace": str(cwd) if cwd else None,
        "typing_version": TYPING_VERSION,
        "by": by,
        "supersedes": None,
        "ts": now_ts(),
    }
    append_line(root / "log" / "admissions.jsonl", adm)
    return adm, True


def admit_capability(root, session_type, capability, by, withdrawn=False):
    """Extend (or --withdraw) a type's capability set — the governed-vocabulary
    promotion path (tags.py shape), signed `--by`. Superseding, never erasing.

    A withdrawal carries an explicit `supersedes` pointing at the admit it revokes
    (review #3): the provenance edge makes the fold union-merge-safe — it does not
    rely on file order to know which admit a withdraw cancels. (Owner-gating of
    this verb lives in cmd_admit_capability, the supersede-done shape.)"""
    supersedes = None
    if withdrawn:
        prior = _latest_capability_admit(Fold(root), session_type, capability)
        if prior is not None:
            supersedes = prior.get("id")
    adm = {
        "id": "adm." + short_hash("session_capability", session_type, capability,
                                  str(withdrawn), str(by), now_ts()),
        "type": "session_capability",
        "session_type": session_type,
        "capability": capability,
        "withdrawn": bool(withdrawn),
        "by": by,
        "supersedes": supersedes,
        "ts": now_ts(),
    }
    append_line(root / "log" / "admissions.jsonl", adm)
    return adm


# --------------------------------------------------------------- the manifest
WORKSTATION_DIR = ".workstation"
MANIFEST_NAME = "MANIFEST.md"


def manifest_path(tree):
    """Where a tree's workstation manifest lives — a per-tree generated cache
    (gitignored, deletable, regenerable), never truth."""
    return Path(tree) / WORKSTATION_DIR / MANIFEST_NAME


def manifest_dataset(binding, tools):
    """The pure manifest dataset for a binding: the authorized portals plus the
    binding's three A's. `--json`'s twin and the renderer's input."""
    caps = list(binding.get("capabilities", []))
    portals = authorized_tools(tools, caps)
    return {
        "session_id": binding.get("session_id"),
        "session_type": binding.get("session_type"),
        "typing_version": binding.get("typing_version"),
        "workspace": binding.get("workspace"),
        "capabilities": caps,
        "by": binding.get("by"),
        "ts": binding.get("ts"),
        "binding_id": binding.get("id"),
        "portals": [{"tool": t["tool"], "kind": t["kind"],
                     "capability": t["capability"], "ref": t["ref"]}
                    for t in portals],
    }


def render_manifest(data):
    """The workstation manifest text — generated output, do-not-hand-edit. Each
    portal is one line: the PRESENCE of a tool's line is the fact that the
    gateway produced it and this type is authorized to use that tool."""
    lines = [
        "# WORKSTATION MANIFEST — generated by loop.session_gateway; do not hand-edit.",
        "# regenerate: python -m loop.session_gateway manifest "
        f"--session {data['session_id']} --write",
        "#",
        "# Each non-comment line below is a PORTAL. Its PRESENCE is the fact:",
        "# the gateway produced it, so this workstation is AUTHORIZED to use that",
        "# tool. A tool whose capability is not in this type's set is absent here.",
        "# (the portal model — bdo, 2026-06-23)",
        "#",
        f"# session:      {data['session_id']}",
        f"# type:         {data['session_type']} (typing {data['typing_version']})",
        f"# workspace:    {data['workspace']}",
        f"# capabilities: {', '.join(data['capabilities'])}",
        f"# bound-by:     {data['by']} at {data['ts']} ({data['binding_id']})",
        "",
    ]
    for p in data["portals"]:
        lines.append(f"{p['kind']:6}  {p['tool']:24}  [{p['capability']:5}]  {p['ref']}")
    return "\n".join(lines) + "\n"


def emit_manifest(binding, tree, write=False):
    """Emit the workstation portals for a binding. Default returns the rendered
    text (read-only-safe); `write=True` writes the regenerable manifest file to
    the tree's workstation dir. The tree defaults to the binding's workspace when
    that is a real directory, else the supplied `tree`. Returns (text, dataset)."""
    ws = binding.get("workspace")
    root = Path(ws) if ws and Path(ws).is_dir() else Path(tree)
    tools = branded_tools(root)
    data = manifest_dataset(binding, tools)
    text = render_manifest(data)
    if write:
        path = manifest_path(root)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
        data["written_to"] = path.as_posix()
    return text, data


# ----------------------------------------------------------------- read CLI
def _payload_from_ns(ns):
    return {"cwd": ns.cwd, "primary": getattr(ns, "primary", None),
            "brand": getattr(ns, "brand", None)}


def cmd_status(ns):
    """Read-only: derive the type for the given signals (or --type) and show the
    manifest that WOULD be emitted — no binding written, no file touched."""
    fold = Fold(ns.root)
    session_type = ns.type or derive_type(_payload_from_ns(ns))
    if session_type not in SESSION_TYPES:
        print(f"result: needs-you — unknown type {session_type!r}; the closed "
              f"set is {', '.join(SESSION_TYPES)}")
        return 2
    caps = sorted(type_capabilities(fold, session_type))
    preview = {
        "session_id": ns.session or "(unbound preview)",
        "session_type": session_type,
        "typing_version": TYPING_VERSION,
        "workspace": ns.cwd,
        "capabilities": caps,
        "by": "(preview)",
        "ts": "(preview)",
        "id": "(preview)",
    }
    tools = branded_tools(ns.cwd if ns.cwd and Path(ns.cwd).is_dir() else ns.tree)
    data = manifest_dataset(preview, tools)
    unmapped = unmapped_tools(tools)
    if ns.json:
        data["unmapped_denied"] = [t["tool"] for t in unmapped]
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(render_manifest(data), end="")
        if unmapped:
            print(f"\n# {len(unmapped)} tool(s) UNMAPPED — denied a portal (no "
                  "capability classification). Absence is information: classify "
                  "each in CAPABILITY_BY_TOOL (read-only fold -> read; a mutating "
                  "pen -> its real capability): "
                  + ", ".join(t["tool"] for t in unmapped[:8])
                  + ("…" if len(unmapped) > 8 else ""))
    print(f"result: report — type {session_type} (typing {TYPING_VERSION}) would "
          f"open {len(data['portals'])} of {len(tools)} branded tools as portals "
          f"({len(unmapped)} unmapped, denied — classify them); no binding written "
          "(read-only). Bind with `bind --session <id> --by <who>`.")
    return 0


def cmd_bind(ns):
    derived = derive_type(_payload_from_ns(ns))
    session_type = ns.type or derived
    # the escalation guard (review #4, D-2/D-4): --type is an ASSERTION, and a
    # session could force a higher-privileged type than its birth signals derive
    # (e.g. --type steerer-admin from a plain bench) to bypass derive_type's
    # least-privilege floor. If the forced type confers a capability the derived
    # floor would NOT grant, raising privilege is an owner act — it requires
    # --by bdo (the supersede-done shape). Asserting the derived type, or a strict
    # de-escalation, needs no stamp.
    if ns.type and ns.type != derived:
        gained = set(TYPE_CAPABILITIES.get(ns.type, ())) - set(
            TYPE_CAPABILITIES.get(derived, ()))
        if gained and (ns.by or "").strip().lower() != "bdo":
            print(f"result: needs-you — forcing --type {ns.type} asserts "
                  f"{', '.join(sorted(gained))} that the derived floor "
                  f"({derived}) would not grant; raising a session's privilege "
                  "above its least-privilege floor is bdo's alone (D-4). Re-run "
                  "with --by bdo, or drop --type to bind at the derived floor. "
                  "Nothing written.")
            return 2
    binding, created = bind(ns.root, ns.session, session_type, ns.cwd, ns.by)
    if binding is None:
        return 2
    _, data = emit_manifest(binding, ns.tree, write=ns.write)
    if created:
        where = f"; manifest written to {data.get('written_to')}" if ns.write else ""
        print(f"result: report — bound {ns.session} as {binding['session_type']} "
              f"({binding['id']}, by {ns.by}); {len(data['portals'])} portals open"
              f"{where}")
    else:
        print(f"result: report — {ns.session} is ALREADY bound as "
              f"{binding['session_type']} ({binding['id']}) — reused, not "
              "re-created (a session binds once; re-binding would sprawl). "
              f"{len(data['portals'])} portals open.")
    return 0


def cmd_manifest(ns):
    fold = Fold(ns.root)
    binding = existing_binding(fold, ns.session)
    if binding is None:
        print(f"result: needs-you — {ns.session!r} has no binding yet; bind it "
              "first (`bind --session <id> --by <who>`). A manifest is the "
              "projection of a binding — no binding, no portals.")
        return 2
    text, data = emit_manifest(binding, ns.tree, write=ns.write)
    if ns.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(text, end="")
    where = f" (written to {data.get('written_to')})" if ns.write else ""
    print(f"result: report — {len(data['portals'])} portals for {ns.session} "
          f"as {binding['session_type']}{where}")
    return 0


def cmd_admit_capability(ns):
    # owner-only (review #4, D-4): admitting a capability WIDENS what a session
    # TYPE may do — a governance change no session may self-admit (--by anything
    # would let a session grant itself powers). It is bdo's alone, the same
    # bdo-only refusal loop/pen.py's supersede-done makes. Gate FIRST: a non-bdo
    # signer is refused before any record is shaped, nothing written.
    if (ns.by or "").strip().lower() != "bdo":
        print("result: needs-you — admitting a capability is bdo's alone (D-4): "
              "it widens what a session type may do, a governance change no "
              "session may self-admit. Re-run with --by bdo. Nothing written.")
        return 2
    if ns.session_type not in SESSION_TYPES:
        print(f"result: needs-you — unknown type {ns.session_type!r}; the closed "
              f"set is {', '.join(SESSION_TYPES)}")
        return 2
    if ns.capability not in CAPABILITY_CORE:
        print(f"result: needs-you — unknown capability {ns.capability!r}; the "
              f"closed core is {', '.join(CAPABILITY_CORE)} (a new capability "
              "token is its own increment, not a free-text grant)")
        return 2
    if ns.withdrawn and ns.capability in TYPE_CAPABILITIES.get(ns.session_type, ()):
        print(f"result: needs-you — {ns.capability} is a CORE capability of "
              f"{ns.session_type}, closed in code (the spine); it cannot be "
              "withdrawn by admission — withdraw applies only to admitted "
              "extensions, and the core is never retro-invalidated. Nothing "
              "written.")
        return 2
    adm = admit_capability(ns.root, ns.session_type, ns.capability, ns.by,
                           withdrawn=ns.withdrawn)
    verb = "withdrew" if ns.withdrawn else "admitted"
    print(f"result: report — {adm['id']}: {verb} {ns.capability} for "
          f"{ns.session_type} (by {ns.by})")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd")

    def common(p):
        p.add_argument("--root", type=Path, default=DEFAULT_ROOT,
                       help="the records root for log appends (default .ai-native)")
        p.add_argument("--tree", type=Path, default=REPO,
                       help="the workstation tree root (default: this checkout)")

    st = sub.add_parser("status", help="read-only: the type + manifest that WOULD "
                                       "be emitted for given signals (no write)")
    common(st)
    st.add_argument("--session", default=None, help="session id (preview only)")
    st.add_argument("--type", default=None, choices=SESSION_TYPES,
                    help="force a type instead of deriving it")
    st.add_argument("--cwd", default=None, help="the session's cwd (a derive signal)")
    st.add_argument("--primary", default=None,
                    help="the primary/viewport root (lets derive_type read steerer-admin)")
    st.add_argument("--brand", default=None, help="the spawn brand (e.g. ontum-node:<id>)")
    st.add_argument("--json", action="store_true")
    st.set_defaults(func=cmd_status)

    bd = sub.add_parser("bind", help="bind a session at birth (idempotent); writes "
                                     "one session_binding admission")
    common(bd)
    bd.add_argument("--session", required=True, help="the session id to bind")
    bd.add_argument("--by", required=True, help="who is binding it (signed, attributed)")
    bd.add_argument("--type", default=None, choices=SESSION_TYPES,
                    help="force a type instead of deriving it from the signals")
    bd.add_argument("--cwd", default=None, help="the session's cwd / workspace")
    bd.add_argument("--primary", default=None, help="the primary/viewport root")
    bd.add_argument("--brand", default=None, help="the spawn brand (e.g. ontum-node:<id>)")
    bd.add_argument("--write", action="store_true",
                    help="also write the workstation manifest file")
    bd.set_defaults(func=cmd_bind)

    mf = sub.add_parser("manifest", help="emit the workstation portals for a bound "
                                         "session (stdout; --write writes the file)")
    common(mf)
    mf.add_argument("--session", required=True, help="the bound session id")
    mf.add_argument("--write", action="store_true",
                    help="write the manifest file to the tree's .workstation dir")
    mf.add_argument("--json", action="store_true")
    mf.set_defaults(func=cmd_manifest)

    ac = sub.add_parser("admit-capability",
                        help="extend (or --withdraw) a type's capability set")
    ac.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ac.add_argument("--session-type", required=True, dest="session_type",
                    choices=SESSION_TYPES)
    ac.add_argument("--capability", required=True, choices=CAPABILITY_CORE)
    ac.add_argument("--withdraw", dest="withdrawn", action="store_true")
    ac.add_argument("--by", required=True, help="who admits it (D-4: bdo)")
    ac.set_defaults(func=cmd_admit_capability)

    args = ap.parse_args(argv)
    if not getattr(args, "func", None):
        # default: a read-only status preview for this tree
        return cmd_status(ap.parse_args(["status"]))
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
