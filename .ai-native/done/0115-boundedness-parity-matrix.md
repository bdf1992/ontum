# Done-line 0115 — The RepoPrompt boundedness parity matrix

Written before code, per §9.4. When this line is met, stop.

Wave 1 of `epic.repoprompt-parity` (bdo's arc, 2026-06-17: "mine it for requirements"). RepoPrompt CE is mined as a catalogue of agent-**boundedness** techniques, not a feature list — the matrix is the requirements mine and the durable asset that orders the rest of the arc. Each row reads a RepoPrompt capability as "how does this keep an agent bounded?" and answers it in ontum's idiom.

> **Done when:** a committed, machine-readable parity matrix maps every RepoPrompt CE capability named in `docs/sources/repoprompt-context-engineering.md` to exactly one verdict — `have` (cites a resolvable repo file path), `build` (names an atom in `epic.repoprompt-parity`), or `dont-double-build` (cites a real owning epic) — each row stating the boundedness technique it answers; and a test in `tests/` fails if any `have` file path or `dont-double-build` epic id does not resolve on disk (the term-economy/gaps grip rule: a citation that points to nothing is a ghost), and fails if any `build` verdict names an atom absent from the epic.
