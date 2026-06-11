# Done-line 0042 — A gate goes live by bdo's GitHub gesture, not a CLI (realness-intake)

Written before code, per §9.4. When this line is met, stop.

> **Done when:** a mock pipeline stage that has a built, tested real backing can
> go live by bdo's **GitHub gesture**, never a CLI. A `realness-intake` pen does
> the deterministic gh I/O around the gesture (mirroring arc-intake, done-line
> 0038): `open` posts the stage's realness-confirm issue carrying a hidden marker
> that encodes both the `stage_node` and the `real_node`; `pending` returns the
> issues bdo **closed**, each with the stage/node it carries and his closing
> comment, skipping any already acted on (I-2 at the surface); `reply` echoes
> back, reopens to ask again, or marks intake-done. The pen never judges intent
> and never runs `admit-real` itself. The realness-intake **SKILL** reads bdo's
> words and, on a *clear confirm*, runs `python -m loop.node admit-real --stage
> <s> --node <n> --by bdo` — his closed-issue-with-comment is the authorization
> the session executes (D-4), exactly as arc-intake executes `confirm-arc`.
> Proven §10 by a test pinning the deterministic extraction: the marker
> round-trips stage **and** node, a no-marker issue is refused (not guessed), an
> `intake-done` issue is skipped, and bdo's last *own* comment is picked among
> many logins — the locally-fine two-author issue where picking the wrong comment
> reads the wrong intent.

## Out of scope, named

- **The placement gate's own realness stamp.** This build gives bdo the gesture;
  closing the issue it opens is his act, in his time — not performed here.
- **Unifying arc-intake and realness-intake.** They share shape but are distinct
  authority acts (which arc to carry vs. which node to trust to judge); a later
  refactor only if the duplication earns it (KISS over premature DRY).
