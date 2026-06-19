# Report 0073 — Hardening the governance seam — classifier + fence, and the overloaded-term gesture left to bdo

## What landed

**Done-line 0101 — the watcher classifier learns the shell verbs; the fence registers the rest of the mutating git+gh surface.** PR #183, atom-backed (atom.harden-govern-seam.v0), judged `accept` by an independent value-gate (value-gate.claude.v1, rcp.060a3f651340).

This answered bdo's question — *what in the system is currently not branded, wrapped, curatable, or registered in a way I'd be happy with?* — by running the folds the repo already has for exactly that. The inside read clean (gaps, census, tags, reflect: no drift). The escapees showed up in the two folds that watch raw behaviour:

- **The classifier (`loop/tags.py`)** knew git/gh/curl verbs but returned `None` for the whole general shell vocabulary — the watcher's long `unclassified` tail. Now: observe-only verbs tag `read`, filesystem-changing verbs tag `mutate`, and interpreters/control words (python, node, bash, for, until, command, xargs) stay honestly `None` (running code is neither cleanly read nor mutate — guessing there is the silent default the module refuses). The `gh` branch also reads `gh api`'s write methods/fields as mutate, GET as read.
- **The fence (`fence/policy.py`)** covered `git add/commit/push` + `gh pr *` but was silent on the rest of the mutating git surface and raw `gh` writes beyond `pr`. Now six prompt-tier rules (four grouped git: history-integrate / reset-discard / tree-edit / branch-topology; two gh: issue-mutate / api-write), each a cold-reader story with its paved path; `.codex` re-rendered 11→17 rules.

Non-breaking by construction: prompt rules are not in the Claude guard's deny-list (only `forbidden` is), and the guard already *watches* every git mutation via `GIT_MUTATING` and every `gh` call as an external head — so zero new Claude-side denial. The hardening lands on the Codex surface (it prompts) and in the registry record. No pen breaks: the reflector and gate reach GitHub through subprocess, invisible to the Bash-level guard. The `test_fence` prompt-rule invariant was widened from git-only to the real rule — a prompt rule's surface is at least *watched* by the guard. Suite green (32 tags+fence; whole suite exit 0).

A fleet id-collision forced the done-line 0100→0101 (claude/inference-verified-cut already held 0100); the atom was re-versioned and re-judged so the record stays honest.

## needs-you

**One owner gesture, not pressing: name a sense for two overloaded terms.** The same review surfaced a third finding via `causality/term_economy.py audit` — `arc` and `seam` each carry two incompatible senses that both resolve (`arc` = the confirmed-admission vs the prose epic field; `seam` = the loop event-surface vs the phase-2 Site primitive). The audit's own move is "split the term, or name one sense the owner." That is your D-4 call over your load-bearing vocabulary, **not** a session rename — so it is surfaced here, not built. Recommendation: let the bare names keep their runtime/minted senses (`arc` = the admission, `seam` = the loop event-surface) and let the documentary/phase-2 senses carry qualified names; the seed split is then a mechanical follow-up. No action required unless you want it resolved.

## End-state

`report` — PR #183 open and merge-node-eligible after arc confirmation; done-line 0101 met; the governance seam's classifier and fence are complete over the mutation surface; the overloaded-term naming is left as bdo's one optional gesture.
