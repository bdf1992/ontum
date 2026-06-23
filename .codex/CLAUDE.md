# .codex/ — the Codex-native fence (a rendered surface)

The repo-local config layer Codex CLI loads once this project is
trusted (done-line 0027). Everything here **except this file is
generated** by `python fence/render_codex.py` from the family-neutral
registry `fence/policy.py` — never hand-edit it; edit the registry and
re-render (`tests/test_fence.py` refuses a stale render).

- `rules/ontum.rules` — the firm denials as native `prefix_rule`
  entries: raw `git add`/`commit`/`push` and the `gh pr` mutations are
  `forbidden` (each justification names the pen to use instead);
  `git checkout`/`git switch` `prompt`, because the repo root is bdo's
  viewport. Codex validates the inline `match`/`not_match` examples at
  load; `codex execpolicy check --pretty --rules .codex/rules/ontum.rules
  -- <cmd>` tests a command by hand.
- `hooks.json` — the ambient session surface: `SessionStart` runs the
  safe guaranteed tick (`python -m loop.heartbeat --hook`) and then the
  summons briefing; `UserPromptSubmit` runs
  `python -m loop.summon --hook`, the same read-only briefing a Claude
  session is handed each turn. It also carries the hook-seam probe
  (done-line 0029: `fence/probe_codex.py` on
  `PreToolUse`/`PostToolUse`/`PermissionRequest`, recording each
  firing's real payload to the gitignored
  `.ai-native/log/codex-hook-probe.jsonl` so the watcher and any
  `apply_patch` guard are designed from observation). Hooks need a
  one-time review and trust via `/hooks` inside Codex (re-required
  whenever the rendered definition changes — trust is recorded against
  the hash).

What this layer cannot see — cloud runs, untrusted checkouts, file
edits, the log — stays self-discipline, held by [AGENTS.md](../AGENTS.md).
