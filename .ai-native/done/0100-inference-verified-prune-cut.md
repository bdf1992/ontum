# Done-line 0100 — The gardener's branch cut is held until habitual inference affirms it safe

Written before code, per §9.4. When this line is met, stop.

bdo, 2026-06-16: a concurrent gardener pruned a branch that still carried novel,
unlanded code (the spawn-rail helper tier) — an aggressive cut that trusted a
branch state instead of verifying content. His fix: **the CUT of the prune is
verified by habitual inference**, and that verification is a *governed* act —
AuthN (a named admitted caller, not anonymous) and AuthZ (the gateway policy
RBAC, default-deny) expressed across config-as-code (the bdo-signed policy +
the standing cut-authorization), infra-as-code (the garden→gateway wiring, the
single sanctioned egress), and prompt-as-code (a versioned, hashed verification
prompt). Default-deny is the teeth: with no policy stamped, the call is refused
and the gardener holds every cut — the aggressive prune stops before a model is
even consulted, and resumes only when bdo authorizes it, verified and
receipted. This routes the cut THROUGH the existing inference plane
(loop/inference.py + the gateway pen), it does not build a second one (§10).

> **Done when:** the gardener never deletes a branch on a structural signal
> alone — a pure `cut_verdict(unlanded_count, inference_verdict)` (git.py)
> returns **cut** only when (a) the branch has **zero** commits unreachable
> from `origin/main` (a deterministic `git cherry` floor — any unlanded commit
> forces **hold**, and no inference verdict can override it) **and** (b) a
> habitual inference call returned an explicit **affirm-safe**; every other
> case — inference **hold**, uncertain, refused by policy (default-deny),
> down, or unavailable — returns **hold**, so the cut **fails safe** while the
> garden hook stays fail-open; the verification call rides the gateway pen with
> an authenticated caller and surface (AuthN) under its default-deny policy
> (AuthZ), carries a **versioned prompt-as-code** artifact whose `sha256` lands
> on the inference receipt (every cut attributable to the prompt that judged
> it), and `cmd_garden` calls this before any `git branch -D` and never emits a
> blanket "git branch -D" recommendation for a branch carrying unlanded work;
> and `tests/test_garden.py` pins the teeth: an unlanded commit forces hold
> even when inference affirms safe, inference-unavailable forces hold on a
> content-clean branch, and only (zero-unlanded AND affirm-safe) ever cuts.
