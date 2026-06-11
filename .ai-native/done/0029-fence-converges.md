# Done-line 0029 — The guard reads the registry; a probe listens on Codex's seam

Written before code, per §9.4. When this line is met, stop.

> **Done when:** parity between the two fence surfaces is **structural,
> not tested** — `.claude/hooks/command_guard.py` derives its deny-list
> from `fence/policy.py` at runtime (argv prefixes compiled to the
> guard's regex shape, justifications becoming the refusal messages, a
> degraded-fence event recorded loudly if the registry can't load), the
> now-redundant `claude_guard` cross-references and the
> coverage-by-enumeration test are gone, and the behavioral tests (real
> subprocess, exit 2) still pass unchanged; **and** a probe listens on
> Codex's hook seam — `fence/probe_codex.py`, wired into the rendered
> `.codex/hooks.json` for `PreToolUse`/`PostToolUse`/`PermissionRequest`,
> appending each event's argv, stdin, and environment to a gitignored
> sensor trace (`.ai-native/log/codex-hook-probe.jsonl`), exit 0 always —
> so the real stdin/stdout contract can be *observed* before any Codex
> watcher or `apply_patch` write-guard is authored against it.

## Direction (bdo, chat, 2026-06-10)

Two items of bdo's five-point queue after stamping PR #26: "Converge
Claude command_guard.py onto fence/policy.py so parity is structural,
not just tested" and "Build a Codex hook probe/watch layer only after
observing the real hook stdin/stdout contract" — the probe is the
instrument that observation needs; the watcher waits for its readings.

## Out of scope, named (later pieces)

- **The Codex watcher and the `apply_patch` write-guard equivalent** —
  authored only after the probe log holds real payloads (bdo's items 2
  and 3; the "only after" is his line).
- **The two `prompt` rules stay registry-only** — Claude's side keeps
  watching `checkout`/`switch` rather than prompting; the watcher's
  report decides if that ever hardens.
