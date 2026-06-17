# Done-line 0097 — Pattern Commons derived from common patterns, served curl-first

Written before code, per §9.4. When this line is met, stop.

> **Arc:** causality-canvas

bdo's steer (2026-06-17): the Causality surface is **api-first — "curl first"**;
the **Pattern Commons** replaces hand-built templates; and the Commons is
**derived from our common patterns**, not authored from a catalog — the
`term_economy.py` / holonsearch-forge grain (types are folded from evidence and
graded, never hand-declared). Scope this cut to the **grounded subset** (his
pick): the type families that resolve on disk today — `node` / `site` / `edge`
plus the strata `fundamental` / `derived` / `learned` / `divergence`. The
contract is already written (`causality/contracts/projection-api.md`: "today the
API is the term_economy CLI ... a future HTTP layer drives the same operations")
— this lands that HTTP layer, curl-addressable, with the canvas demoted to one
client. It does NOT mint anything (D-4): an ungrounded pattern stays `proposed`.
The AI-native authoring / experience-skill connection is a NAMED next leaf, not
this node (the referenced "experience skill" does not resolve on disk — surfaced
in the report, not invented here).

> **Done when:** (1) a read-only fold `causality/commons.py` **derives** the
> Pattern Commons from the repo's own common patterns — each pattern carrying its
> `type`, its required-field `schema`, and its `etymon` (the `file:symbol` it
> recurs at) — over the grounded subset (`node`/`site`/`edge` +
> `fundamental`/`derived`/`learned`/`divergence`), and **refuses to mint** a
> pattern whose etymon does not resolve (it stays `proposed`/`ghost`, never
> minted — the closure rule, teeth); (2) a stdlib HTTP layer `causality/api.py`
> serves it **curl-first** — `GET /commons` (the derived Commons) and
> `GET /projection` (the committed term-economy ProjectionView), localhost,
> contract-shaped per `projection-api.md`, an unknown path 404s; (3) the canvas's
> real-evidence load is wired to fetch `GET /projection` from the API (the
> browser becomes one client, not the authority), falling back to the committed
> file when the API is down; and (4) a §10 headless test (`tests/test_commons.py`,
> joining the suite) drives the fold AND the HTTP handler in-process, asserts the
> derived Commons is contract-shaped and reproducible, and has **teeth** — a
> pattern with an unresolvable etymon is held at `proposed`, a negative control
> the test would fail to catch if the fold minted it anyway.
