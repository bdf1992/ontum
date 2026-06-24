# Done-line 0195 — Bind-at-birth — derive session type, write an idempotent session_binding, emit capability-filtered workstation portals (presence = authorized)

Written before code, per §9.4. When this line is met, stop.

> **Done when:** `loop/session_gateway.py` is a pure stdlib fold+pen (the
> sibling of `loop/inference.py`, mirroring its RBAC template, not rebuilding
> it) that realizes the smallest real spine of bind-at-birth (issue #534,
> session-gateway.proposal.md, the portal model refinement bdo gave 2026-06-23):
> (1) `derive_type(payload) -> "builder" | "node-fill" | "steerer-admin"` is
> PURE, named, and versioned (a `TYPING_VERSION` constant the binding carries —
> §10.1 / doctrine §14: a typing-rule change is new lineage, never a silent
> reinterpretation), with an honest least-privilege fallback when signals are
> absent; (2) a per-type CAPABILITY SET is governed vocabulary — a closed core
> per type in code PLUS admitted `session_capability` extensions (the
> `loop/tags.py` pattern), never a frozen code constant where avoidable;
> (3) `bind(session_id, type, cwd, by)` writes ONE `session_binding` admission
> via `loop.reconcile.append_line` carrying the three A's (who/what · the
> authorized capability set · attributed-to-workspace + `--by` + `ts` +
> `typing_version`) and is IDEMPOTENT — an existing binding for a session is
> REUSED, never blind-recreated (the rescue-branch-sprawl bug §4/§14 names);
> (4) `emit_manifest(binding)` writes the workstation portal(s) — the branded
> tools folded from `.claude/skills/*/SKILL.md` + the `loop/*.py` pens, each one
> line, FILTERED by the type's capability set, with a do-not-hand-edit header and
> regenerable, so the PRESENCE of a tool's portal IS the fact that the gateway
> produced it and this type is authorized to use it; (5) a read-only render +
> `--json` + a clear `done | report | needs-you` stdout line, runnable as
> `python -m loop.session_gateway`. §10 teeth (`tests/test_session_gateway.py`,
> joined to the suite, non-vacuous): (a) a tool ABSENT from a type's capability
> set is ABSENT from that type's emitted manifest, and a constant
> "all-tools-authorized" classifier is CAUGHT; (b) a binding is never
> blind-recreated for a session that already has one (idempotence). The whole
> suite (`python -m unittest discover -s tests -v`) stays green. The work is
> atom-backed (`atom.session-gateway-bind-at-birth.v0`); it claims no arc — the
> proposal proposes the anthology/arc name for bdo (D-4).

## Out of scope (named, not invented away)

- **Creating a new worktree bench** — the provisioning pen that sprouts a fresh
  tree on a code claim (proposal increment #4). This chapter binds and emits
  portals for the CURRENT tree only; new-tree provisioning is the next increment
  and is bdo's to stamp as direction.
- **Wiring the SessionStart hook** — the ambient activation that folds the
  binding on every pulse and routes the deficit. The pen is built and runnable
  by hand; activating it as a hook is a config-as-code change that is bdo's
  stamp (a new standing hook is the owner's to admit).
- **The git-pen enforcement seam** — "no commit without a binding for this
  HEAD" (proposal §5, increment #2). Named, not built here.
