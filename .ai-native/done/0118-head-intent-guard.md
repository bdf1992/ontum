# Done-line 0118 — The HEAD-intent guard — a commit refuses when HEAD moved under the session

Written before code, per §9.4. When this line is met, stop.

The diagnosis (this session, 2026-06-18): a session committed eval work onto a
*parallel* session's branch in the shared primary worktree — the current branch
had switched under it between reading HEAD and committing. Root cause
(session-gateway.proposal.md §2): a git working tree has one HEAD, so "the
current branch" is shared mutable global state while a session treats it as
private and stable. The repo's law: the fix is structural, not "verify HEAD by
hand" — a session's self-discipline is the unreliable component. This is the
cheapest structural closer (proposal increment #1, the "sheath"): the full
session gateway is the arc; this is the one refusal that turns the exact
collision into a clean deny.

The frame (reuse, no new infra): the git pen already computes the current
branch and already refuses detached-HEAD and trunk commits (`commit_refusal`).
The guard adds one assertion: the session *declares* the branch it believes it
is on (`--on <branch>`); the pen refuses if live HEAD differs. Stateless —
per-invocation, explicit intent, nothing another session can race; no pin file,
no session state. Built and committed in an isolated worktree (dogfooding the
insulation principle the proposal names).

> **Done when:** `.claude/skills/branch-ritual/git.py`'s `commit` verb accepts
> `--on <branch>`; when given, the pen refuses (exit 2, reason on stderr) if the
> live current branch differs from the asserted one, naming the session's fix
> (checkout the branch / enter its worktree before committing); when omitted,
> behaviour is unchanged (backward compatible, so existing callers keep
> working). A §10 test (`tests/test_git_pen_head_intent.py` or the branch-ritual
> test module) drives the live pen as a subprocess: asserting a WRONG branch is
> refused with a HEAD-intent reason, asserting the RIGHT branch commits, and
> omitting `--on` still commits — the teeth being that a fabricated guard that
> always passes fails the wrong-branch case. `branch-ritual/SKILL.md` documents
> the flag. The full suite is green and the work is a PR the merge-node can land.

> **Non-example:** a stateful pin another session can race (the assertion is
> per-invocation and explicit, not stored); making `--on` REQUIRED now (that
> breaks every existing caller — it is the "default-per-writer" stretch of the
> arc, a later done-line, not this); inferring the session's intended branch
> from anything other than its explicit assertion (intent cannot be guessed);
> or building the binding/provisioning/gateway here (this increment is only the
> sheath — the refusal — not the issued workspace binding).

> **Arc:** proposed — a chapter of the session-gateway Anthology
> (session-gateway.proposal.md), serving the insulated-workspace throughline.
> bdo names the anthology; this stands on its own done-line until then and takes
> no owner stamp it was not given.
