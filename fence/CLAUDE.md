# fence/ — the family-neutral fence registry

One home for the firm denials every engineering family meets, whatever
harness it arrives through (done-line 0027). Claude Code and Codex are
working **surfaces**; the fence belongs to the repo, not to either
surface — a rule lives here once and each harness renders it into its
native enforcement shape.

```sh
python fence/render_codex.py          # regenerate the .codex/ layer
python -m unittest tests.test_fence -v
```

- [policy.py](policy.py) — the registry. Each rule is one record: the
  argv prefix it matches, the decision (`forbidden` | `prompt`), a
  justification written as a story for a cold reader (the why and the
  paved path inline — a session reading only the refusal knows what to
  do instead), inline `match`/`not_match` examples, and the
  `command_guard` rule ids it mirrors on the Claude side.
- [render_codex.py](render_codex.py) — the deterministic renderer:
  emits `.codex/rules/ontum.rules` (native `prefix_rule` entries,
  Starlark) and `.codex/hooks.json` (the ambient summons). The outputs
  are committed but **never hand-edited** — edit the registry and
  re-render.

Rules of this directory:

- **Parity is tested, not trusted.** `tests/test_fence.py` refuses
  drift in three directions: every forbidden rule's examples must be
  *denied by the live `command_guard`* (subprocess, exit 2); the
  rendered `.codex/` bytes must match a fresh render; every example
  must fit its own rule's prefix semantics. Tightening one surface
  without the other is a failing test, by design.
- **`command_guard.py` still carries its own `DENY_RULES` today.**
  Converging it to read this registry is a named later piece (done-line
  0027); until then the parity test holds the seam.
- **Stdlib only.** The registry is data; the renderer is a pen — small,
  deterministic, no dependencies.
- A new family arrives by adding a renderer (`render_<family>.py`),
  never by re-authoring the rules.
