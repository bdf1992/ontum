# Done-line 0106 — The construction flag + the Complexity slider on one three-word phrase

# Done-line 0106 — The construction flag (game-dev missing-texture rule) + the Complexity slider on one three-word phrase

Written before code, per §9.4. When this line is met, stop.

bdo, at the Story demo: *"I need a rule used in game dev. Anything that is mock or
not done, get a special flag so I can see the state of construction. I want to
bring in the slider now, and start with just one phrase, three words. The Cat Naps."*

The game-dev rule is the **missing-texture convention** — a placeholder/unfinished
asset renders in a deliberately glaring magenta (the Source-engine purple/black
checker), so it can never be mistaken for finished or silently ship. It is the
visual twin of ontum's mock-shame: a mock that moves fake work cannot hide. So
construction state becomes a first-class, schema-driven render token, and the
Story demo reduces to the single three-word phrase the slider grows.

> **Done when:** `canvas-system.js` carries a `BUILD` construction-state token
> table (real / mock / wip — the magenta missing-texture rule) with §10 refusal
> teeth in `canvas-system.test.js`; the Story demo renders a single staged phrase
> that opens at the three words "The cat naps" and a live **Complexity** slider
> grows it (3 words → the full cat·sunbeam·warmth·shadow mesh, sentence and mesh
> together); every element that is mock or not-yet-built — the four unbuilt
> sliders and the hand-authored (not yet composition-generated, iterations 0008)
> relations — carries the construction flag with a legend; all causality node
> tests stay green (`canvas-system.test.js`, `phrases.test.js`).
