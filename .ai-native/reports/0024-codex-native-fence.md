# Report 0024 — The fence lifts off its first surface

## What landed

Done-line 0027 (Codex fenced by machine, from one registry) — met.

bdo asked, in chat (2026-06-10): expand the Codex worksurface using
Codex's now-native hook points, and frame it as the lift — Claude Code
becomes a working **surface** rather than the system itself, with the
shared rules in a registry both families draw from (his words reached
for the Pattern Commons shape: a governed home, not scattered copies).
Done-line 0024 had already named this graduation as a later piece —
the Codex fence moving from prose in `AGENTS.md` to an actual guard.

What exists now:

- **`fence/`** — the family-neutral fence registry. `policy.py` holds
  the firm denials once, as data: eleven rules (raw `git
  add`/`commit`/`push` and the six `gh pr` mutation verbs `forbidden`,
  `git checkout`/`switch` `prompt` — the repo root is bdo's viewport),
  each with its argv prefix, a justification written as a story (the
  why and the pen to use instead, inline), match/not-match examples,
  and the `command_guard` rule ids it mirrors.
- **`fence/render_codex.py`** — the deterministic renderer:
  emits the committed `.codex/` layer. A new family arrives by adding a
  renderer, never by re-authoring the rules.
- **`.codex/`** — the Codex-native surface, generated:
  `rules/ontum.rules` (native `prefix_rule` entries, Starlark,
  ASCII-clean, with load-time-validated examples) and `hooks.json`
  (`SessionStart` + `UserPromptSubmit` → `python -m loop.summon
  --hook`, the same read-only briefing a Claude session gets). Shapes
  verified against the local Codex manual cache
  (`%LOCALAPPDATA%\Temp\openai-docs-cache\codex-manual.md`,
  codex-cli 0.137.0-alpha.4): repo-local layers load once the project
  is trusted; hooks need one-time review via `/hooks`.
- **`tests/test_fence.py`** — the seam, refusing drift three ways:
  every forbidden rule's examples are *denied by the live
  `command_guard`* (subprocess, exit 2) and its not-match examples
  pass; the committed `.codex/` bytes equal a fresh render; every
  example fits (or refuses) its own rule's documented prefix
  semantics; and the `claude_guard` cross-references must cover the
  guard's whole deny-list, both directions — a rule added on one
  surface without its twin fails the suite. §10 probe: removing one
  mirror from the set was noticed (drift → inequality), and the
  denial tests run the real guard, not a model of it.
- **`AGENTS.md`** — amended on the record: the fence section now says
  which lines are machine-held when the `.codex/` layer is trusted,
  and that everything the layer can't see (cloud runs, untrusted
  checkouts, file edits, the log) remains self-discipline.

Suite: 222 tests, OK (11 new).

Named, not built (in the done-line): converging `command_guard.py` to
read the registry directly; a Codex PreToolUse watcher and a
`write_guard` equivalent — both blocked on the same gap, the manual
documents hook *config* shape but not the hook stdin/stdout contract,
so nothing was authored against an undocumented seam.

## needs-you

- **Activate the fence**: open Codex CLI in this repo (the project is
  already trusted in your `~/.codex/config.toml`), run `/hooks`, review
  and trust the two summon hooks; then `codex execpolicy check --pretty
  --rules .codex/rules/ontum.rules -- git add .` should report
  `forbidden`. Two things only you can observe there: whether the rules
  file parses clean in your codex-cli build (rules are marked
  experimental), and whether hook stdout actually lands in Codex's
  context the way Claude's ambient hook does.
- **Your viewport has drifted from origin**: local `main` carries
  9431f6c (a local commit of the codex-guest-engineer work, done-line
  numbered 0021) while the same work merged remotely as done-line 0024
  via PR #23, and origin/main has since moved on through PR #25. This
  branch was cut from origin/main; reconciling the viewport (likely a
  reset of local main onto origin/main, discarding the duplicate local
  commit) is yours — no session touches the primary checkout.
- One naming conflict, named not resolved: chat used "pattern commons
  registry" for this layer. The Pattern Commons of `docs/phase-2/` is a
  governed institution; this fence registry is commons-*shaped* (one
  home, rendered surfaces) but was deliberately not named `commons/` —
  minting that term for harness config felt like vocabulary the
  knolling ritual and your stamp should govern, not a session. If the
  fence should carry the name, say so and it moves.

## End-state

`report` — fence registry + rendered .codex/ layer + parity seam on
branch claude/codex-native-fence, suite green, PR open for your stamp.
