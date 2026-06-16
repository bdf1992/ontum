# .github/ — the server-side enforcement surface (config-as-code)

The repo's first surface that runs *on GitHub* instead of in a hooked
session. Everything here is config-as-code (§7, like `.claude/`):
versioned, landed as stamped increments, never hand-tuned silently.

It exists for one reason (done-line 0068): the atom invariant — every
work-particle is an atom on the log (§15/D-5) — was enforced only
client-side (the PR pen refuses to open a non-atom PR; the lander
refuses to land one), so a PR opened on GitHub directly (the web UI,
bdo's phone, Codex, the API) bypassed it entirely. #107/#114/#118 were
the proof. A client-side guard binds only a hooked session's tool calls;
only a gate on GitHub binds every actor equally.

## The one law this tree may hold

A check here enforces **toward the log** — it refuses what is *not* on
the log, never decides what *is* true. That keeps GitHub a guard for the
substrate's first law (the log is truth), not a second authority that
could disagree with it. A workflow that judged work, ranked it, or wrote
a verdict would be a second source of truth and is out of bounds; this
tree only ever says "this did / did not go through the machinery."

## Workflows

- `workflows/atom-invariant.yml` — on every PR to main, runs the PR
  pen's audit over the PR's own range (`pr.py audit --range BASE HEAD`)
  and fails the check (red, blocking) when the PR adds no atom + backing
  receipt. It calls the *same* `loop.pr_audit` pure check the client-side
  pen uses, so the server-side gate and the pen can never drift about
  what "on the log" means. It cannot stop a PR from being *created*
  (GitHub has no reject-on-create) — it makes a non-conforming PR
  un-mergeable and loudly red, the enforceable form of impossible.

## Ports, and the registry we deliberately did *not* build (a named hole)

The enforcement logic is provider-agnostic; only the `.yml` is
GitHub-bound. Two generic ports carry the seam:

- the **enforcer port** — `pr.py audit --range BASE HEAD`, exit non-zero
  on an orphan. Any CI (GitLab, Gitea, a local `pre-receive` hook, a
  second GitHub org) gates on this exact verb; its `.yml`/glue is a leaf
  adapter with no logic.
- the **consumer port** — `pr.py audit --json` (and `loop.pr_audit
  --json`), the verdict dataset for a reader that is not enforcing.

What is **not** built, on purpose: a *registry of enforcement surfaces*
— admitted records naming which providers enforce and which consumers
read, the symmetric twin of reflect's inbound surface registry
(`reflect register --surface …`). There is one provider today, and the
ports above already make a second one a thin adapter, so a registry now
would be governance invented ahead of a real second consumer (against
"open beats invented / absence is information", the hard rule). The
shape it would take when a second provider/consumer is real: an admitted
`enforcement_surface` record (kind × address), folded like reflect's
surfaces, each mapping to its adapter. Until then this is a named hole,
not an accident.

## What stays bdo's

Marking the check **required** in branch protection, and turning off the
bare merge button, is the owner's repo-admin gesture — the one tap that
turns this from *visible* to *impossible*. A session builds and tests the
workflow ready for that tap; it never flips the protection itself (D-4).
