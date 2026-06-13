# Report 0054 — Governed inference plane — the first whole

## The goal

bdo ran `/goal` with "lets work on still work and standing waters." The field
read it back as one thing seen twice: the inference plane was **defined but
unbuilt** (an earlier /goal session wrote done-line **0062**, the governed
plane), and its control plane — `loop/minds.py` — was the purest **standing
water** in the repo (the census named it `wired·idle`: in the path, nothing
flowing; `minds list` → 0 registered). bdo chose the **governed first whole**:
honor 0062's RBAC/no-bypass tooth, defer only the converge pen, then said *Go*.

## What landed

The whole inference-plane code, proven against real weights:

- **Config plane** — `loop/inference.py` (new): `route` (selection + fallback
  order) and `policy` (RBAC rules) as admitted, bdo-signed, superseded-never-
  erased records folded at call time; `normalize_backing` resolves every scheme
  (`http(s)`/`env:`/`profile:`/`odysseus://`/`file:`) to one OpenAI-compatible
  target with no network. `loop/minds.py` gained a served-model axis (`--model`)
  so two minds can name distinct served models at one endpoint (0062's "second
  served model"). Adding a backing or re-steering is **one record, not a code
  edit**.
- **Data plane** — `.claude/skills/gateway/gateway.py` (new pen): folds the log,
  authorizes, resolves, runs **one normalized completion over stdlib urllib
  bounded by a timeout** (the #95/#96 600s-hang made impossible), and writes
  **one receipt per attempt** (mind, prompt_hash, latency_ms, tokens, outcome),
  falling back by route order on a down/hung/refused mind.
- **Authorization plane** — RBAC default-deny at the gateway: `(caller, surface,
  mind)` → permit/refuse, deny-wins, with D-2's which-mind axis as the first
  rule. **No-bypass**: the gateway is the sole sanctioned egress, pinned by a
  guard test that fails on any *new* inference path.

**Proven, not asserted** — `tests/test_gateway.py`, 20/20 green, full suite
green (exit 0). The teeth bite: a real completion through **two distinct live
Ollama backings** (qwen3 + a second served model), **real fallback** from a dead
primary to live Ollama receipting the fallback, an unauthorized caller
**refused** with no completion, a single-backing stub that **cannot** fake
fallback, adding a backing as **records only**, and the **no-bypass** guard.
The live teeth ran on this machine (~127s of real cold-load inference); they
skip where Ollama is absent so the core teeth still bite in a bare CI.

## needs-you

Two items reach bdo's surface; both are genuinely his, neither is a chore I can do:

1. **Stand up the plane (one gesture).** The plane is built and proven but
   **inert until bdo registers the minds** — `minds`/`route`/`policy` are all
   `--by bdo` (a backing is a disclosure event, config is governance; D-4). I
   cannot sign for him. His one stamp registers ≥2 minds + the default route +
   a permit policy, which flips `minds.py`, `inference.py`, and `gateway.py`
   from `wired·idle` to **alive** and clears the standing-water gap. **I am
   opening the GitHub bootstrap issue** with the exact records; his close-with-
   comment authorizes the registration (relayed faithfully, never self-signed).
   A `mind-intake` skill is the clean automation of that relay — named as the
   immediate next piece.
2. **The stranded done-line 0062 collides fleet-wide.** The earlier /goal
   session wrote 0062 but never committed it; the stranded branch
   `claude/pen-fleet-safe-id` already minted `done/0062`. Renumbering a
   **frozen, bdo-authorized** done-line — even keeping the bar byte-identical —
   is adjacent to `supersede-done` (bdo-only), so I did **not** unilaterally
   re-mint it. This build stands on 0062's *bar*, independent of its filing
   number. The arc-confirm that mattered (inference-gateway #99) is already
   landed on origin.

## Named tension (not silently resolved)

0062 piece 6 says "RBAC without no-bypass is theatre." The gateway is the sole
**sanctioned** path and the guard fails on a *new* bypass — but `gate.py`'s
agentic `claude -p` is a distinct, separately-trust-railed path. Its full
migration is `atom.gate-through-gateway.v0` (0062 out-of-scope) and it can't be
a plain chat-completion (it's an agent that reads the repo). I pinned it as the
**single named legacy exception** in the guard rather than hide it. Honest, not
theatre — but bdo should know the one back door stays open until its own atom.

Deferred per 0062, named: the **converge pen** (`atom.mind-infra.v0`, plane 4 —
health-check/drift, the "self-healing" second whole), `atom.replay-evals.v0`.

## End-state

`report` — the governed inference plane is built and proven green against real
Ollama (gateway-pen.v0 + routing-rules.v0 + RBAC/no-bypass + minds-first-light's
code); it goes live and the standing-water gap clears on bdo's one
plane-bootstrap gesture (issue opened); the stranded-0062 fleet-id collision is
his to renumber.
