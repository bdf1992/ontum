# Report 0018 — the reflection automates

## What landed

**Done-line 0020** — bdo's pub/sub directive executed under his chat
stamp ("Lets do it then", 2026-06-10), in the level-triggered form the
substrate allows: **the log is the topic, rules are the subscriptions,
reflection records are the acks, drift is the unconsumed backlog.** No
broker, no daemon.

- **Rules are the translation matrix, admitted:** `reflection_rule`
  admissions (kind × surface → enabled, signed `--by`, latest wins;
  disabling supersedes, never erases). One kind exists —
  `owner-stamp-queue` — and the kinds table in `loop/reflect.py` is
  the named extension point: a new kind is a new drift fold plus
  rules, never a new system.
- **The beat:** a `Stop` hook (`.claude/hooks/reflect_auto.py`) runs
  the reflector pen's new `auto` verb after every turn. `auto` applies
  only what enabled rules name (`auto_plan`, a read-only fold), signs
  every act (`by: reflect-auto`), receipts it on the log before
  attempting the next, and is a quiet no-op when nothing is enabled or
  nothing drifts. Manual `apply` is unchanged: any registered surface,
  rule or no rule.
- **The contract change, named and stamped:** this is the repo's first
  *writing* hook. Its discipline: writes only through the pen, only
  what enabled rules name, fail-open, exit 0 always, never gating the
  owner. A missed beat costs nothing — the next beat re-derives.
- **Tests (6 new, suite 146 OK):** rule latest-wins with both
  admissions standing on the log; the §10 pin twice over —
  configured-off drift must not reflect (no rule, and a disabled
  rule); enabled-rule auto-apply signs and settles, next beat no-op; a
  rule pointing at an unregistered surface reaches nowhere; the hook
  exits 0 on garbage stdin and a penless project dir.
- **Live and armed:** rule `owner-stamp-queue × github-issues = on`
  admitted by bdo (`adm.9450fd2441fb`) on the already-registered
  surface (`adm.556e14c878c4`). Zero drift at hand-off. From here, an
  atom reaching bdo's stamp becomes a GitHub issue *by itself* on the
  next beat, and the stamp landing closes it — the empty-Issues-page
  incident that started done-line 0018 can no longer recur silently in
  either direction.
- SKILL.md → **0.2.0, the pattern commons**: Using (register / rule /
  apply / auto), Extending (new kinds = folds + table entries; new
  surfaces = translators in the pen), Managing (the log is the audit;
  pause by superseding rule; failures resume, never double-act).

**Shared-tree weather, for the record:** the sibling language session
committed onto the just-merged `claude/surface-reflector-ui` (a dead
branch), then its pen `create` rode the `claude/reflection-automates`
branch this session had minted minutes earlier — **PR #13** (language
directory) reached the stamp cleanly by accident. Branch names carry no
meaning, so no harm; this session's build moved to a third branch
(`claude/reflection-matrix`) cut from the merged 0018 tip, with the
sibling's committed record ids (done 0019, report 0017) seeded as
untracked copies so the pens allocated 0020/0018 without collision —
copies removed before hand-off, never committed.

## needs-you

- **PR #13** (the sibling's language directory) is open, non-draft —
  at your stamp.
- **This increment's PR** is at your stamp (open, non-draft).
- **The done-discipline skill** (your ask: what done means, pinning
  evidence in every done-line, the audit fold that replays it) is the
  authorized next increment — queued, not started, one thing at a time.
- **Gardening:** seven remote branches are merged (0 ahead) and safe to
  delete; `great-faraday-djmq2x` (16 ahead) remains cherry-pick-or-retire,
  your call. The local `claude/surface-reflector-ui` still holds the
  sibling's commit (now also on PR #13's branch) — deletable after #13
  lands.

## End-state

`report` — done-line 0020 met and tested (146 OK); the rule is armed
under bdo's stamp; the field is clean; two PRs await the stamp (#13
language, and this one).
