# Report 0027 — One table, two surfaces, and an instrument on the seam

## What landed

Done-line 0029 (the guard reads the registry; a probe listens on
Codex's seam) — met. Two items of bdo's post-#26 queue, built in one
increment because they share the fence's home.

**Convergence (bdo's item 4).** `command_guard.py` no longer carries
its own deny-list: `DENY_RULES` is derived at import from
`fence/policy.py` — each forbidden registry row's argv prefix compiled
to the guard's regex shape (`\b`-anchored, `(?!-)` so `git commit`
never bleeds into `git commit-tree`), its justification becoming the
refusal message verbatim. The trunk-push carve-out keeps its firmer
"never push to main" line ahead of the generic registry refusal. A
registry that fails to load degrades **loudly** — a `degraded` entry on
the watch log and a stderr warning — and fails open, because a silently
unguarded repo that still looks guarded is the known failure mode. The
now-redundant `claude_guard` cross-references left the registry, the
coverage-by-enumeration test became a structural derivation check, and
a new test proves the degraded path is loud, not quiet. Three existing
guard tests asserted the old rule ids (`git-add-raw` → now `git-add`,
etc.) and were updated to the registry's family-neutral ids — named
here because watch-log consumers see the new ids too.

**The probe (bdo's item 2, the "only after" honored).**
`fence/probe_codex.py` is wired through the rendered `.codex/hooks.json`
into `PreToolUse`, `PostToolUse`, and `PermissionRequest`: each firing
appends its argv, raw stdin, cwd, and CODEX-shaped environment to
`.ai-native/log/codex-hook-probe.jsonl` (gitignored sensor trace,
deletable, not truth). It writes nothing to stdout, swallows its own
errors, exits 0 always. Once bdo has run a Codex session here, the
trace holds the real hook contract — and the Codex watcher plus the
`apply_patch` write-guard equivalent (queue items 2's second half and
3) get designed from observation, not authored against the
undocumented seam.

Also this session, outside the branch: the primary checkout was
fast-forwarded to origin/main (138e610) — the divergence reported in
report 0024 had already resolved upstream — and `docs/sources/files.zip`
was left in place, untracked (it blocks nothing; contents below).

Suite: 251 tests, OK (13 in the fence module).

## needs-you

- **Re-trust the hooks**: the rendered `hooks.json` changed (probe
  added), so Codex marks the definitions for review again — `/hooks`,
  trust, then work a short session here so the probe trace fills. The
  `/hooks` step is interactive inside Codex and stays yours by design;
  no `codex` binary is reachable from Claude's shells at all.
- **`docs/sources/files.zip` decision**: it holds six session
  artifacts (handoff-ontabet-session, landing-map,
  recursive-pilish-basin-v0, s-frame-placements-v0.json, viewer.html,
  memo-creole-glyph-language-claude). At least the s-frame placements
  and the ontabet arc already landed in the repo via PR #27; the rest
  may be transport residue. Keep it, commit it as a source, or delete
  it — your call; sessions leave `docs/sources/` alone.
- **Done-line id 0027 collided on main**: PR #26 added
  `0027-codex-native-fence.md` and PR #27 added `0027-ontabet-harness.md`
  in parallel — the placement cross-ref fold (done-line 0023) sees
  sibling worktrees' checked-out branches, but two unmerged PRs racing
  to main slip past it. History stands (no renumbering); whether the
  placement fold should also count open PR heads is a candidate
  done-line if collisions repeat.

## End-state

`report` — convergence + probe on branch claude/fence-converges, suite
green, PR open for your stamp; reflection kind-drift (queue item 5) is
the next branch, this session.
