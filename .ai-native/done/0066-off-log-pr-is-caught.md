# Done-line 0066 — an off-log PR is caught

> **Done when:** a read-only audit reads every open GitHub PR and names each whose branch adds no atom + backing receipt to the log as an off-log orphan; its pure check is pinned by a test (an orphan branch is caught, an atom-backed branch passes clean); and a live run proves it on the field today — #107 (no atom, no receipt) named, #111 (atom.inbound-envoy-seam.v0 + receipt) clean.

## Why

bdo asked whether the loop has any process that resolves open PRs, then named the real hole: it should be impossible to create work in GitHub without going through the machinery. It is not. The atom invariant — every work-particle is an atom on the log (§15/D-5) — lives only in two client-side places: the PR pen refuses to *open* a non-atom PR (atom_backed_refusal), and the lander refuses to *land* one. Both bind only a hooked Claude session's tool calls. The GitHub web UI, bdo's phone, Codex, the API — all unbound. PR #107 is the proof: authored straight on GitHub, zero atoms, zero receipts, invisible to every fold the loop runs. Nothing ambient sees it, so nothing resolves it; it is forgotten by construction.

The full resolution bdo chose is *both* a detection fold (in-philosophy, read-only, surfaces orphans so none is forgotten) and a server-side required check (the hard backstop that makes a non-conforming PR un-mergeable by anyone). This is node 1: detection — the cheap, fully-in-philosophy half that makes the #107-class orphan visible immediately. The server-side gate (the first .github/workflows/ in the repo, plus branch protection, which needs bdo's repo-admin gesture to activate) is node 2, its own contract.

## Shape

The audit is a thin reach (gh pr list -> open PRs + head branches) feeding a pure check: for each PR, does its branch diff against main add an atom under .ai-native/atoms/ and a log receipt naming it? The reach is impure and lives at the edge; the check is pure and testable on branch-diff facts, never on live gh — the same split reflect uses (drift fold in loop/, outward reach in the pen). The check reuses the pen's own atom-backing logic so the audit and the open-time refusal cannot drift. An orphan becomes a surfaced gap/divergence, never an edit and never a guess — the disposition of any orphan (re-home through the pen, or close) stays a judgment call surfaced to bdo, D-4.
