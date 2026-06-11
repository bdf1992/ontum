# Report 0030 — The mirror only speaks tongues it knows

## What landed

Done-line 0030 (a surface kind without a translator refuses to fit) —
met. bdo's queue item 5: reflection surface-kind drift, fixed as
*both* of his either/or — dispatch is the extension point, refusal is
what happens off the table, the shape `RULE_KINDS` already set.

The §10 hole this closes: `python -m loop.reflect register --surface
team-slack --kind slack --address ontum/general --by bdo` was accepted,
and the reflector pen would then have run `gh issue create --repo
ontum/general` against it — the admitted kind was data nobody checked,
two locally-fine records with no seam noticing.

Now:

- **`SURFACE_KINDS`** sits beside `RULE_KINDS` in `loop/reflect.py` —
  the tongues the pen actually speaks (`github-issues` today). The
  `register` CLI refuses a kind off the table (`needs-you`, naming the
  table and the path: a new kind is a new translator, its own stamped
  increment). Deregistering stays possible whatever the kind — history
  may hold admissions older than the table, and superseding is never
  refused.
- **`auto_plan` skips** an enabled rule whose surface kind is
  untranslatable — the beat must never break a turn or guess — and
  **`status` names it** (`surface kind has no translator — the beat
  skips it`), so a skipped surface is visible to eyes, never silent.
- **The pen dispatches through `TRANSLATORS`** — surface kind → how
  `open` and `close` speak there; the gh-issue verbs moved behind the
  `github-issues` entry. A kind with no entry gets a refusal that names
  the known tongues; the injectable runner is never called and nothing
  is recorded as reflected.
- **A test pins `set(TRANSLATORS) == set(SURFACE_KINDS)`** so the
  pen's table and the fold's table cannot drift apart; five more tests
  cover the CLI refusal, the deregister allowance, the beat's skip, the
  status naming, and the pen's refusal (runner uncalled, log untouched).

Suite: 255 tests, OK (6 new).

## needs-you

- **The records pen mints colliding ids — twice bitten, once dodged.**
  `loop/pen.py`'s `next_id` folds over the local directory only, while
  the fleet-safe fold (every ref) lives in `.claude/hooks/placement.py`
  and only the *write_guard* uses it. That is how the two 0027
  done-lines landed on main (PRs #26/#27), and this session the pen
  minted a second 0029 done-line and a second 0027 report — caught and
  hand-renumbered to the placement fold's answer (0030 both). The fix
  is one increment: the pen asks `placement.next_id` first, falling
  back to the local fold — same pattern the write_guard already uses.
  Candidate done-line, not built here (this branch was the reflection
  fix; naming it instead of scope-creeping into it).
- Nothing else; the reflection surface itself needs no action — the
  registered `github-issues` surface carries the translatable kind and
  behaves exactly as before.

## End-state

`report` — surface kinds are a table, the pen dispatches by kind and
refuses what it cannot speak, on branch claude/reflect-kind-dispatch,
suite green, PR open for bdo's stamp.
