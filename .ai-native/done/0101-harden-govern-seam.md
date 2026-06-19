# Done-line 0101 — The watcher classifier learns the shell verbs; the fence covers the remaining mutating git and gh verbs

Written before code, per §9.4. When this line is met, stop.

bdo asked (2026-06-17) to harden the governance seams the watcher and the
fence already point at. The system's own folds report clean *inside* (gaps,
census, tags, reflect), but the two folds that look at *raw behaviour* name
real escapees: `command_guard.py --report` ranks **git ×100 raw mutations**
as the heaviest unwrapped lever and carries a long **unclassified tail** the
intent classifier cannot yet name; the fence registry covers `git
add/commit/push` and `gh pr *` but is silent on the other mutating git verbs
(`merge`, `rebase`, `reset`, `branch`, `restore`, `clean`, `stash`, `revert`,
`cherry-pick`, `rm`, `mv`, `worktree`) and on raw `gh` mutations beyond `pr`
(`gh issue` writes, `gh api` non-GET). This closes both blind spots at the one
seam they share — the classifier (`loop/tags.py`) and the family-neutral
registry (`fence/policy.py`) — without breaking a workflow: the new git/gh
rules are `prompt`-tier (watched on the Claude side, surfaced on Codex), and
the classifier only sharpens what the watcher already records.

The two `overloaded` terms `arc` and `seam` the term-economy audit surfaces
are a SEPARATE finding whose own resolution — "name one sense the owner" — is
bdo's D-4 gesture, not a session rename of his load-bearing vocabulary; it is
surfaced in the report, not built here.

> **Done when:** `loop.tags.classify()` returns `read`/`mutate` (not `None`)
> for the general shell verbs the watcher's unclassified tail named — reads
> (`ls`, `cat`, `grep`, `head`, `tail`, `sed`, `awk`, `find`, `wc`, `sort`,
> `uniq`, `cut`, `tr`, `which`, `stat`, `diff`, `echo`, `printf` …) and
> mutations (`cp`, `mv`, `rm`, `mkdir`, `rmdir`, `touch`, `ln`, `chmod`,
> `tee`, `dd`, `truncate` …) — while genuinely-ambiguous interpreters and
> control words (`python`, `node`, `bash`, `sh`, `for`, `foreach`, `until`,
> `command`) still honestly return `None` (running code is neither cleanly
> read nor mutate); and `fence/policy.py` carries one rule per remaining
> mutating git verb and per raw `gh` mutation surface named above, each with a
> cold-reader justification naming the paved path and inline match/not_match
> examples, with the committed `.codex/` layer equal to a fresh `python
> fence/render_codex.py`; `tests/test_tags.py` pins the new classifications
> (including the honest `None` cases) and `tests/test_fence.py` validates every
> new rule's examples against the live guard and the prefix semantics; the full
> suite is green and the watcher report's unclassified tail shrinks with git/gh
> mutation counts now carrying accurate intent.
