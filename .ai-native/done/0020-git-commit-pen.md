# Done-line 0020 — the git commit pen, branded

Written before code, per §9.4. When this line is met, stop.

The git wrapper, mirroring the gh wrapper (branch-ritual / pr.py): raw
mutating git is denied and routed through a pen, the way raw `gh pr`
mutations already are. First cut is `commit` + `add` — the watcher's
second-heaviest unwrapped tool (report: git 12, behind only gh's reads)
and the highest risk in the shared-tree fleet, where a single
`git add .` sweeps in another session's uncommitted work. Read-only git
(`status` / `log` / `diff`) stays allowed-and-watched, exactly as
`gh pr list` does — denying it would diverge from the gh precedent, not
match it.

> **Done when:** raw `git add` and `git commit` are denied toward a
> branded git pen that refuses a sweep (`add .` / `-A` / `commit -a`)
> and a trunk commit, requires named paths and a real message, and
> forwards everything else for feature parity; the watcher folds
> standalone local git mutations so the next verb nominates itself; and
> a test proves a locally-fine `git add .` refuses to fit.
