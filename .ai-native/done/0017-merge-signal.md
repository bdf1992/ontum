# Done-line 0017 — the merge signal: a draft cannot be stamped

Written before code, per §9.4. When this line is met, stop.

> **Done when:** the owner can no longer merge by accident — a PR a
> session is still appending to opens as a GitHub **draft** (merge
> button disabled by the platform, not by convention), the pen grows
> the pair of verbs that owns the transition (`create --rolling` opens
> the draft; `ready <n>` re-validates the story, requires a green or
> declared-red suite, and flips it — the one unambiguous "bdo, it's
> yours now"), raw `gh pr ready` joins the deny list, the branch
> ritual states the reading rule in one line (**open non-draft PR =
> please merge; draft = not yet**), and a test pins that a rolling
> create without the draft flag cannot happen.

Decision recorded at ~02:10; enforcement landed later the same night
once the 0014–0016 increment committed and freed the pen files. The
convention was agreed
with bdo in chat (2026-06-10 ~02:10) after PR #9 was stamped mid-build
— his read: "it needs to be more clear when you want me to merge,
right?" Right — and clearer prose is not the fix; a disabled button
is. Implementation waits because the in-flight 0014–0016 increment
(the other session) currently owns pr.py, command_guard.py, and
SKILL.md — two pens don't share an inkwell mid-stroke. Until then the
interim reading rule stands: an open non-draft PR is at the stamp and
frozen; a session with more work holds it locally or cuts the next
branch.
