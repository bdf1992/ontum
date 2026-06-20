# fence/ — the family-neutral fence registry

One home for the firm denials every engineering family meets, whatever
harness it arrives through (done-line 0027). Claude Code and Codex are
working **surfaces**; the fence belongs to the repo, not to either
surface — a rule lives here once and each harness renders it into its
native enforcement shape.

```sh
python fence/render_codex.py          # regenerate the .codex/ layer
python fence/barrier.py               # the gate/fence primitive + the trunk reading
python -m unittest tests.test_fence tests.test_barrier -v
```

- [policy.py](policy.py) — the registry. Each rule is one record: the
  argv prefix it matches, the decision (`forbidden` | `prompt`), a
  justification written as a story for a cold reader (the why and the
  paved path inline — a session reading only the refusal knows what to
  do instead), and inline `match`/`not_match` examples.
- [barrier.py](barrier.py) — the gate/fence primitive (done-line 0148).
  bdo's shape: we have *gateways* (policy — they decide "is this *actor*
  permitted?"), but no deterministic *gate* that closes one and no *fence*
  around the route. A gate and a fence are physical, not political — "you can
  see through it, you can't pass it, you can't climb it, and touching it
  bites." The atom is a **barrier-link**: a pure, **actor-blind** predicate
  over an act's observable form (the discriminator from a gateway — it never
  reads who acts). A **fence** is a *closed loop* of links around a
  **territory**, validated for **closure** across the front/seam/top route
  taxonomy (the **meshed** seams and **tall** top, not just the front),
  **barbed**-ness (a blocked act is witnessed), and **non-opacity** (every link
  carries a cold-reader reason); a **gate** is a link at a sanctioned opening
  in it. `validate_link`/`validate_fence` are the §10 teeth, and
  `tests/test_barrier.py` proves each one bites on the real trunk-mutation
  territory — including that `command_guard`'s own perimeter is **torn at the
  seam** (a `python` that shells `git push` slips its quote-stripping front
  link), sealed by one raw-command link. The contract; the *installed* fences
  (sealing that seam, fencing the inference surface) are later increments.
- [render_codex.py](render_codex.py) — the deterministic renderer:
  emits `.codex/rules/ontum.rules` (native `prefix_rule` entries,
  Starlark) and `.codex/hooks.json` (the ambient summons + the hook
  probe). The outputs are committed but **never hand-edited** — edit
  the registry and re-render.
- [probe_codex.py](probe_codex.py) — the hook-seam probe (done-line
  0029): wired through the rendered `hooks.json`, it records each
  `PreToolUse`/`PostToolUse`/`PermissionRequest` firing (argv, raw
  stdin, environment) to the gitignored sensor trace
  `.ai-native/log/codex-hook-probe.jsonl`. The Codex watcher and any
  `apply_patch` write-guard get designed from those readings — never
  against the undocumented contract.

Rules of this directory:

- **Parity is structural** (done-line 0029): `command_guard.py` derives
  its `DENY_RULES` from this registry at runtime — one table, two
  surfaces, no twin lists to drift. A registry that fails to load
  degrades the Claude guard *loudly* (watch-log `degraded` entry +
  stderr) and fails open.
- **And still tested behaviorally.** `tests/test_fence.py` runs every
  forbidden rule's examples through the live `command_guard`
  (subprocess, exit 2), requires the committed `.codex/` bytes to equal
  a fresh render, and checks every example against its own rule's
  prefix semantics.
- **Stdlib-first.** The registry is data; the renderer is a pen — small
  and deterministic, so it needs no dependency (the repo's blanket
  no-dependency ban was lifted 2026-06-12, but this pen earns none).
- A new family arrives by adding a renderer (`render_<family>.py`),
  never by re-authoring the rules.
