# Report 0016 — verification stamps and the reflector

## What landed

**No done-line (the audit):** bdo asked how the "done" review was
validated and the honest answer was: mostly it wasn't — records about
the work were read as the work. The back-fill pass converted that:
suite green (140 OK by session end), `prompt_hash` lineage verified
byte-for-byte (receipt hash == disk hash of
`.ai-native/nodes/value-gate.claude.v1.md`), `.gitattributes` guards
inspected, the envoy ledger receipt inspected, `git push` / `gh pr
ready` denials probed live (exit 2, correct messages), the write
guard's wiring proven end-to-end by a refused wrong-id Write, and all
twelve done-line files 0001–0012 confirmed in `origin/main`'s tree.
Lesson named: every claim of "done" should carry its evidence class —
behavior-verified / log-verified / merged-only / prose-only. A
**done-discipline skill** (what a done-line must contain, pinning
evidence named in the file, an audit fold that replays it) was asked
for by bdo and is owed its own done-line.

**Instructive near-miss:** the first `gh pr ready` probe returned exit
0 — not a hole in done-line 0017 but a malformed probe: the PowerShell
5.1 pipe mangled the JSON payload and the guard failed open silently,
as designed. The same payload through a clean pipe refused correctly.
A verification procedure can itself be the broken part; use the pinned
tests as probes, not hand-rolled ones.

**PR #10:** flipped to merged by bdo himself (the pen's `ready` verb
was mid-flight when he clicked the button — the owner path the guards
deliberately leave open). Done-lines 0013–0017 are on `main`. The
pen's refusal afterwards ("PR #10 is merged — only an open PR can come
to the stamp") was correct behavior.

**Verdicts routed (bdo, chat, "ALL apporoved, make it happen"):**
`atom.epic-layer.v0` accepted at the real stamp (rcp.299dbd326422,
verbatim provenance) and settled by the orchestrator;
`atom.github-verdict-mirror.v0` retired (98e6c67) under the
owner-inbox v0→v1 precedent — its amend lives on as the settled
surface-registry story; every log line stands.

**Done-line 0018 (this session's build):** the inbox reaches the
owner. Surfaces are admitted records (`loop.reflect register`, signed,
latest-wins); `loop/reflect.py` computes each surface's desired view
(one issue per atom at the admitted-real stamp, briefed arc-first) and
the drift against the last-reflected state — reflections are log
records, so drift is a fold; the reflector pen
(`.claude/skills/reflect/`) applies exactly that drift via `gh` and
records each act before attempting the next (re-run = no-op,
half-applied = resumes); the summon hook names unreflected drift
ambiently. One-way mirror (D-4): verdicts land only through
`loop.node judge`. 13 tests, including the §10 pin (a cleared atom
whose issue stays open must show as drift). Live: `github-issues`
registered at `bdf1992/ontum` by bdo (adm.556e14c878c4); drift is
zero because the queue is empty — the next atom to reach the stamp
opens issue #12-or-whatever with one `apply`.

**Origin story, for the record:** bdo looked at GitHub Issues
mid-session, saw 0 open, and concluded the hook was outdated. It
wasn't — the queue was real and the surface he visits showed none of
it. Done-line 0018 was built the same day the gap bit its owner.

## needs-you

- **bdo's pub/sub directive (chat, mid-build, verbatim):** "Reflect
  should likey use a programatic set, where when local files are
  create we have a pubsub with a translation matrix capable of
  automating the reflection if it's configured, so this skill should
  becomes a pattern commons dedicated to using, extesing,m and
  managing that servce as applicaiotn" (spelling his). Read as: (1) a
  translation matrix — which log kinds reflect to which surfaces, how
  — as configured records, not code; (2) automated reflection when
  configured; (3) the reflect skill grows into the commons that uses,
  extends, and manages that service. The session's recommendation
  (argued to bdo in chat): the *matrix* and *automation* fit the
  substrate as admitted records + level-triggered folds on the loop's
  existing beats — a broker daemon does not (hard rule: no broker, no
  daemon; an edge-triggered queue can drop what a level-triggered fold
  re-derives). Needs bdo's stamp as its own done-line before any of it
  is built; today's hooks still never write.
- **Report debt acknowledged:** done-lines 0014 and 0017 have no
  dedicated session reports (their work is described in PR #10's
  story and this report's predecessor commits). Named, not paid here.
- **docs/sources working-tree changes** (`rosetta-creole.md` new,
  `README.md` modified) are still bdo's uncommitted drop — untouched
  by sessions, awaiting his word.
- **gh auth flaked mid-session:** API calls 401'd for several minutes
  (REST and GraphQL, token pinned) then recovered with no re-auth.
  Logged to session memory: retry before asking bdo to re-login.

## End-state

`report` — done-line 0018 met and tested (140 OK); both owner verdicts
routed and settled; the queue is empty and the registered surface
mirrors it; the pub/sub evolution awaits bdo's stamp as its own
increment.
