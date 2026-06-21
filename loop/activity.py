#!/usr/bin/env python3
"""The activity-accounting fold (done-line 0143): account for the harness's
own hooks.

bdo, 2026-06-20: *"account for all activity, even Claude hooks like session
start and tool call, and start auditing their data collection and usage for a
shared gateway."*

Every major seam in ontum is already a governed gateway, and the hooks are its
sensors — `command_guard` watches every tool, `spawn_guard` every spawn, the
codex probe every Codex firing. But the sensors' *own* data collection is the
one activity the gateway never accounts for: the hooks collect command strings,
spawn prompts, full raw stdin/argv/env and gh poll results, mostly silently into
gitignored sinks, and most do not even record that they fired. Who watches the
watchers.

This is the accounting layer the git/gh-gateway proposal deferred (*"the
witness-log home and its fold"*), widened from git/gh reads to all activity. It
is the declared half of the shared gateway's witness asymmetry (reads get
witnessed, not authorized) turned on the harness's own metabolism.

The shape, in the `census`/`gaps`/`heal` grain — a pure read-only fold, no
network, no git (loop's law), the cut stays bdo's (D-4):

  - the DECLARED register (`.claude/activity-register.json`) states, per hook,
    what it COLLECTS, what it USES that for, where the data GOES, and whether
    its firing is WITNESSED;
  - the LIVE wiring is derived from `.claude/settings.json` (the ground truth of
    what actually fires);
  - reconcile() crosses them, and the §10 TEETH refuse two ways:
      undeclared-collector — a wired hook with no register entry (a silent
                             collector that was never accounted for);
      ghost                — a register entry whose hook is no longer wired
                             (a stale declaration).

A `claude`-wired entry is enforced against `settings.json`; a `codex`-wired
entry is reconciled against `.codex/hooks.json` only if present (the codex layer
is deferred — done-line 0143); a `prototype` entry is declared-but-unwired by
design (so it cannot be wired later as a silent collector). The register's
*content* (what each hook collects) is the authored audit; this fold enforces
that the register can never fall out of sync with what is wired — you cannot add
a silent collector without declaring it. The runtime witness (every firing -> a
first-class receipt) is organ 2.

`witnessed: false` is not a violation — it is the honest current state, and the
count of unwitnessed hooks is exactly the work organ 2 must do; the fold surfaces
it as the bridge, never as a failure.

CLI:
  python -m loop.activity          the activity accounting, read-only
  python -m loop.activity --json   the raw dataset (machine-readable)
"""

import argparse
import json
import re
import sys
from pathlib import Path

# loop/activity.py -> loop/ -> repo root. Works the same in a worktree.
REPO = Path(__file__).resolve().parent.parent

SETTINGS = ".claude/settings.json"
REGISTER = ".claude/activity-register.json"
CODEX_HOOKS = ".codex/hooks.json"

# The Claude hook events settings.json can wire. Used to label each live key
# with where it fires (informational; the teeth are on key presence).
HOOK_EVENTS = ("PreToolUse", "PostToolUse", "SessionStart", "Stop",
               "UserPromptSubmit")

# Positionals that are hook-event routing (the codex probe is wired as
# `probe_codex.py PreToolUse`), not a pen subcommand — never a verb in the key,
# so one probing activity across events folds to one key.
EVENT_ARGS = frozenset(HOOK_EVENTS) | {"PermissionRequest"}

_FLAG = re.compile(r"^-")


def canonical_key(command):
    """The canonical hook key for a wiring command string. A script is keyed by
    its filename stem; a `-m pkg.mod` invocation by the module's last segment.
    A script with a meaningful subcommand verb (`git.py sync`, `git.py garden`)
    is keyed `stem:verb`, so two distinct activities of one pen are accounted
    separately. A trailing flag (`--post`, `--hook`) is a phase of the same
    hook, not a new one, so it is never appended."""
    toks = [t.strip("'\"") for t in command.split()]
    # `python -m loop.summon --hook` -> module's last segment.
    if "-m" in toks:
        i = toks.index("-m")
        if i + 1 < len(toks):
            return toks[i + 1].split(".")[-1]
    # otherwise the first `*.py` token is the script.
    for j, t in enumerate(toks):
        if t.endswith(".py"):
            stem = Path(t).stem
            # the next non-flag positional is a subcommand verb, if any — but a
            # hook-event name is event routing, not a verb (the codex probe).
            for nxt in toks[j + 1:]:
                if _FLAG.match(nxt):
                    continue
                return stem if nxt in EVENT_ARGS else f"{stem}:{nxt}"
            return stem
    return command.strip()  # unparseable: key by the raw command, never drop it


def live_hooks(settings):
    """The live wiring as {key: sorted[event-labels]}, folded over
    settings.json. The event label carries the matcher (`PreToolUse:Write`) so
    a hook's surface is legible; the key is matcher-blind so Pre/Post phases of
    one guard fold together."""
    out = {}
    hooks = (settings or {}).get("hooks", {})
    for event in HOOK_EVENTS:
        for group in hooks.get(event, []):
            matcher = group.get("matcher")
            label = f"{event}:{matcher}" if matcher else event
            for h in group.get("hooks", []):
                cmd = h.get("command", "")
                if not cmd:
                    continue
                key = canonical_key(cmd)
                out.setdefault(key, set()).add(label)
    return {k: sorted(v) for k, v in out.items()}


def codex_keys(codex_hooks):
    """The Codex-layer keys wired in .codex/hooks.json, folded best-effort. The
    rendered shape is family-specific; we read every command we can find and key
    it the same way, so a `codex`-wired register entry can be verified when the
    layer is present."""
    keys = set()

    def walk(v):
        if isinstance(v, dict):
            cmd = v.get("command")
            if isinstance(cmd, str) and cmd:
                keys.add(canonical_key(cmd))
            elif isinstance(cmd, list) and cmd:
                keys.add(canonical_key(" ".join(str(x) for x in cmd)))
            for x in v.values():
                walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)

    walk(codex_hooks or {})
    return keys


def reconcile(register, live, codex=None):
    """Cross the declared register against the live wiring. Returns the full
    accounting: which hooks are accounted, the §10 violations (undeclared
    collectors, ghosts), the entries wired in another layer, and the
    unwitnessed bridge to organ 2."""
    entries = (register or {}).get("hooks", {})
    live_keys = set(live)
    declared = set(entries)

    claude_declared = {k for k, e in entries.items()
                       if e.get("wiring", "claude") == "claude"}

    # TEETH 1 — a wired hook with no register entry: a silent collector that
    # was never accounted for.
    undeclared = sorted(live_keys - declared)
    # TEETH 2 — a `claude`-wired register entry whose hook is no longer wired.
    ghost = sorted(claude_declared - live_keys)

    accounted = sorted(live_keys & declared)

    # Non-claude entries: verified against their own layer when present, else
    # carried as unverified (deferred, not a violation).
    elsewhere = []
    codex_present = codex is not None
    for k in sorted(declared - live_keys - set(ghost)):
        e = entries[k]
        wiring = e.get("wiring", "claude")
        if wiring == "codex":
            status = ("wired" if (codex_present and k in codex)
                      else "unverified" if not codex_present
                      else "ghost-codex")
        else:
            status = "declared-unwired"  # prototype, by design
        elsewhere.append({"key": k, "wiring": wiring, "status": status})

    # A codex entry that IS present but the layer does not carry it is a real
    # ghost — fold it into the teeth so the codex layer can't drift silently.
    ghost_codex = sorted(e["key"] for e in elsewhere
                         if e["status"] == "ghost-codex")

    unwitnessed = sorted(k for k in accounted
                         if not entries[k].get("witnessed", False))

    rows = []
    for k in accounted:
        e = entries[k]
        rows.append({
            "key": k,
            "events": live[k],
            "collects": e.get("collects", []),
            "uses_for": e.get("uses_for", ""),
            "sink": e.get("sink", ""),
            "witnessed": bool(e.get("witnessed", False)),
        })

    return {
        "rows": rows,
        "accounted": accounted,
        "undeclared": undeclared,
        "ghost": ghost,
        "ghost_codex": ghost_codex,
        "elsewhere": elsewhere,
        "unwitnessed": unwitnessed,
        "violations": undeclared + ghost + ghost_codex,
    }


def validate(register, live, codex=None):
    """The §10 teeth as an importable predicate: the list of accounting
    violations (undeclared collectors + ghosts). Empty == the register
    accounts for exactly what is wired. A fabricated undeclared hook or a stale
    entry makes this non-empty — the proof the check is not vacuous lives in
    tests/test_activity.py."""
    return reconcile(register, live, codex)["violations"]


def _read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def account(repo):
    settings = _read_json(repo / SETTINGS)
    register = _read_json(repo / REGISTER)
    codex_path = repo / CODEX_HOOKS
    codex = codex_keys(_read_json(codex_path)) if codex_path.exists() else None
    live = live_hooks(settings)
    result = reconcile(register, live, codex)
    result["register_missing"] = register is None
    result["settings_missing"] = settings is None
    return result


def render(result):
    if result.get("settings_missing") or result.get("register_missing"):
        miss = []
        if result.get("settings_missing"):
            miss.append(SETTINGS)
        if result.get("register_missing"):
            miss.append(REGISTER)
        print(f"result: needs-you — cannot account for activity: missing "
              f"{', '.join(miss)}. The fold reconciles the register against the "
              f"live wiring; without both there is nothing to cross.")
        return 1

    rows = result["rows"]
    print(f"\naccounted ({len(rows)}) — wired hooks with a declared "
          f"data-practice:")
    for r in rows:
        w = "witnessed" if r["witnessed"] else "UNWITNESSED"
        print(f"  {r['key']}  [{w}]")
        print(f"      fires:    {', '.join(r['events'])}")
        print(f"      collects: {', '.join(r['collects']) or '—'}")
        print(f"      uses for: {r['uses_for']}")
        print(f"      sink:     {r['sink']}")

    if result["elsewhere"]:
        print(f"\nother layers ({len(result['elsewhere'])}) — declared, wired "
              f"outside settings.json:")
        for e in result["elsewhere"]:
            print(f"  {e['key']}  ({e['wiring']}: {e['status']})")

    undeclared = result["undeclared"]
    ghost = result["ghost"] + result["ghost_codex"]
    if undeclared:
        print(f"\nUNDECLARED COLLECTOR ({len(undeclared)}) — wired and "
              f"collecting, but accounted nowhere (§10 teeth):")
        for k in undeclared:
            print(f"  {k} — add its data-practice to {REGISTER} before it lands")
    if ghost:
        print(f"\nGHOST ({len(ghost)}) — declared, but no longer wired (§10 "
              f"teeth):")
        for k in ghost:
            print(f"  {k} — retire its entry from {REGISTER} or re-wire it")

    unwit = result["unwitnessed"]
    print()
    if result["violations"]:
        print(f"result: report — {len(undeclared)} undeclared collector(s), "
              f"{len(ghost)} ghost(s). The register must account for exactly "
              f"what is wired before the gateway can audit it; fix the register "
              f"(a session's move, not bdo's). {len(unwit)} of {len(rows)} "
              f"accounted hooks are still unwitnessed — organ 2's work.")
        return 0
    print(f"result: done — all {len(rows)} wired hook(s) accounted; the "
          f"register and the live wiring agree. {len(unwit)} collect data "
          f"without witnessing their own firing — the runtime witness (organ 2) "
          f"is what closes that, and the cut stays yours (D-4).")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", type=Path, default=REPO,
                    help="repo root to account for (default: this one)")
    ap.add_argument("--json", action="store_true",
                    help="emit the raw dataset (machine-readable)")
    args = ap.parse_args(argv)
    result = account(args.repo)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    return render(result)


if __name__ == "__main__":
    sys.exit(main())
