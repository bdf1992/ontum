# Done-line 0068 — the server-side atom gate

> **Done when:** a GitHub Actions workflow runs on every PR to main and fails the check (red, blocking) when the PR adds no atom + backing receipt to the log, calling the *same* atom-invariant logic the PR pen enforces (one check, no drift); a single-PR mode exits non-zero on an off-log range and zero on an atom-backed range, pinned by a test; the workflow is committed under a governed .github/ tree, ready for bdo's one branch-protection gesture to make the check required — the moment that turns it from visible to impossible.

## Why

Node 1 (done-line 0066) made an off-log PR *visible* — a read-only audit that names every PR that reached GitHub without an atom on the log. bdo chose *both*: visible is not enough, it must be impossible. Node 1's audit and the PR pen are both client-side — they bind only a hooked session's tool calls. The GitHub web UI, bdo's phone, Codex, the API are unbound, and #107/#114/#118 are the proof that the bypass is routine, not rare. Only a gate on GitHub itself binds every actor equally.

This is that gate: a required status check. It cannot stop a PR from being *typed* (GitHub has no reject-on-create), but it makes a non-conforming PR un-mergeable and loudly red — the enforceable form of impossible. It enforces *toward* the log (refuse anything not on it), so it guards the substrate's first law rather than becoming a second authority — the one shape of GitHub-as-enforcer the doctrine can hold. It reuses node 1's pure check (loop.pr_audit) so the server-side gate and the client-side pen can never disagree about what "on the log" means.

## Shape

A workflow (.github/workflows/) triggers on pull_request to main, checks out base+head, and runs the PR pen's audit in a single-PR mode over the PR's own range — exit non-zero (red, blocking) on an orphan. The .github/ tree earns its own CLAUDE.md (config-as-code, D-9: the first server-side surface, governed like .claude/). The activation — marking the check required in branch protection, and turning off the bare merge button — is bdo's repo-admin gesture, the only part a session cannot do; the workflow is built and tested ready for that one tap.
