# Done-line 0024 — Codex admitted as a guest engineering family

Written before code, per §9.4. When this line is met, stop.

> **Done when:** `AGENTS.md` stands at the repo root as Codex's
> composition surface — a thin pointer that *defers to*
> [CONTRIBUTING.md](../../CONTRIBUTING.md), the doctrine, and the
> per-directory `CLAUDE.md` environments (it does not fork their rules),
> and that re-states **as self-enforced discipline** the guardrails the
> Claude-Code hooks enforce for a Claude session but cannot enforce for
> Codex (no raw git mutation to `main`, no editing the log, records
> through `loop.pen`, generated outputs never hand-edited); the
> **`codex/*` branch namespace + worktree workspace** convention is
> named so Codex never clobbers bdo's primary checkout; and the
> "two-party loop" line is **amended on the record** to admit Codex as a
> *guest engineer* — bdo still merges, still the last stop (D-4) — with
> the contract change named in report 0021, not silently authored.

## Direction (bdo, chat, 2026-06-10)

bdo wants Codex working in the repo, with an agent file that *respects
CONTRIBUTING* and a Codex-specific workspace. Settled in this thread:
Codex enters as a **guest engineer** — it works the way a Claude session
does (its own branch namespace and worktree, runs the suite, opens PRs)
but **bdo still merges**; and admitting it is treated as a **contract
change** to the stated two-party loop, recorded as a done-line + report
rather than quietly amended.

The load-bearing asymmetry: a Claude session is fenced by hooks
(`command_guard` denies raw `git add/commit/push` and `gh pr` mutations;
`write_guard` enforces file placement; a SessionStart/UserPromptSubmit
hook injects the loop's state; the Stop beat reflects). **Codex sees none
of that machinery.** So `AGENTS.md` is not a copy of `CLAUDE.md` — it is
the *only* fence Codex has, and it must carry, as discipline Codex upholds
itself, the rules the guards otherwise enforce.

## Out of scope, named (later pieces)

- **Codex as a registered reviewing mind** — the envoy-reception arc (a
  later epic: a reader, a reviewer, a model-registry), where an external
  family is a *receipted disclosure event* and the second set of eyes is
  cross-family. The guest-engineer rail here is the small reversible step
  that *sets that up*; it does not build it.
- **Hook-equivalent enforcement for Codex** — if Codex's self-discipline
  proves leaky, the fence graduates from prose in `AGENTS.md` to an
  actual guard (a pre-commit hook, a CI gate). Named, not built.
- **Nested `AGENTS.md` per module** — not authored; the per-module
  contracts stay single-sourced in each `CLAUDE.md`, and the root
  `AGENTS.md` points Codex at them.
