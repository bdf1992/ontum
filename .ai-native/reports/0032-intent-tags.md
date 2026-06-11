# Report 0032 — intent tags: the watcher learns read from mutate

## What landed

By done-line 0032: `loop/tags.py` — a governed tag pool, the organ census's
lesson pushed upstream to the write seam. The census found the watcher
couldn't tell a read from a mutation, so its `--report` counted 65 raw `gh`
calls — all reads — and nominated `gh` as the next wrapper. Noise read as
signal. The fix: tools emit a typed tag from a governed vocabulary.

Three seams, one node:

- **The pool** (`loop/tags.py`): dimension `intent` with a small closed core
  `{read, mutate}`, plus the one shared verb→intent `classify()` the watcher
  and git pen both import (I-4, no second copy). Proposed-tier governance:
  an unadmitted value reads as `proposed` drift, promotable by an admitted
  `tag` record (`--by`), never blocked. `surface` and `arc` are the named
  next dimensions.
- **The watcher** (`command_guard.py`) tags every watched command with a
  derived intent, fail-open (a classifier error never gates the owner);
  `--report` now splits raw **mutations** (the real wrapper candidates) from
  raw **reads** (raw-by-design), and lists verbs the classifier doesn't yet
  know — an honest gap to teach, never a silent guess.
- **The git pen** (`git.py`) records its verb's intent and refuses an
  `--intent` that lies about the verb.

The §10 bite is real and was sharpened by a live smoke test: an out-of-pool
`--intent escalate` first staged *silently* (used the verb's intent, dropped
the word). That contradicted "not silently swallowed", so for a derivable
dimension the declaration is now a strict check — a known wrong value is a
lie, an unknown value is refused with the admit path. `tests/test_tags.py`
plants both; full suite 295, green.

## needs-you

- **Promote the core intent values when you're ready.** Until you run
  `python -m loop.tags admit --dimension intent --value mutate --by bdo`
  (and `read`), the core rides as code-defined spine; the admit path is how
  the pool grows under your stamp. Not blocking — the report and pen work now.
- **The next dimension is `arc`** — which epic an action serves. Intent was
  derivable so this slice derived it; the *require-a-declared-tag* "dropdown"
  pattern you described earns its keep on a non-derivable dimension, and the
  arc tag feeds the arc-confirmation you built (done-line 0028) and the
  inbox. That's the natural next slice.
- **Id collision flagged:** a parallel session also took done-line 0032
  (merge-node, PR #39) and likely report 0032. This is the chronic
  fleet-numbering collision (four 0029s already coexist on trunk). Renumber
  one on merge if it bothers you, or let them coexist by slug
  (`0032-intent-tags` vs `0032-merge-node`). bdo merges.

## End-state

`report` — intent tags shipped on `claude/intent-tags`; PR opened for your
merge. The watcher can now tell read from mutate, so it will stop nominating
`gh` (reads) and surface the real raw mutations as wrapper candidates. The
pool is governed and proposed-tier; the pattern is proven on one dimension
and one pen, ready to extend to `arc` next.
