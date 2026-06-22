# Done-line 0174 — The act-fence — ask-forgiveness as a risk-tiered authority dial over acts

Written before code, per §9.4. When this line is met, stop.

> **Done when:** `loop/act_fence.py` classifies a *declared act* into one of three tiers — **FORGIVENESS** (reversible + contained → act, log, surface as FYI), **PERMISSION** (reversible-but-wide, or weigh-worthy → stop and ask bdo), **FORBIDDEN** (irreversible / outward / as-the-owner → never, no fence saves it) — by reversibility × blast-radius keyed to ontum's *real gestures*, not abstract risk; reads an admitted `act_fence` (bdo's standing per-scope forgiveness authorization), **default-safe / inert when unset** (the disposer's shape); `evaluate()` composes `observe.gate` **first** (an act that cannot name an attributable receipt path HALTS before any tier is read) and returns **admit** (forgiveness + in-fence, citing the fence as `authorized_by`) | **escalate** (permission, or forgiveness with no fence drawn) | **deny** (forbidden) | **halt** (unobservable); a read-only `python -m loop.act_fence` shows the cut and each catalogued act's tier; and `tests/test_act_fence.py` proves the classifier is **non-vacuous** — landing a PR to main is forgiveness **only under a confirmed arc** and permission **without one** (the tier reads the authorization context, not the verb), `confirm-arc`/`admit-real` are forbidden (a fence can never self-admit bdo's own gesture, D-4), a wide/outward act cannot buy forgiveness by *declaring* itself reversible, and a forgiveness act escalates with no fence but self-admits under one. It **actuates nothing** — no real act self-admits yet.

## Why

bdo, 2026-06-21: *"we might also want to install ask for forgiveness on some risk levels."* The repo already had ask-forgiveness in exactly one place — `loop/disposer.py` auto-admits an in-fence *setpoint* change citing bdo's standing fence, never signing its own line. This is that pattern lifted off the setpoint dials and onto **acts**, so "may this act run unattended, or must it stop and ask?" is answered by where the act falls on a cut bdo draws once. It is the keystone toward the autonomous-authorship button (`.ai-native/proposals/authoring-platform.proposal.md`): the tier that lets reversible, contained motion run unattended is also what keeps the owner-present surface **short** — most motion never reaches bdo, so what does is rare and shaped.

## Shape

- **Composition, not a new engine (§10):** the fence is an `act_fence` admission (bdo-signed, read at runtime I-8, inert until drawn) — the disposer's `auto_admit_fence` generalized; `observe.gate` (loop/observe.py) runs first because you cannot call an act reversible if you cannot trace its effect home (Observable is the substrate the tier is computed on); `fence/policy.py` is *not* the home (static argv denials, no middle tier, acts are data-dependent).
- **The committed cut** (bdo's, this session): reversible + contained-to-record/branch → forgiveness; landing-to-main → forgiveness **iff** a confirmed arc already authorized it (the merge-node executing bdo's standing stamp), else permission; `confirm-arc`/`admit-real`/force-destructive/outward-as-owner → forbidden.
- **Read-only / propose-only:** it classifies and *shows*; the actuator (a session act actually self-admitting through this) and bdo's first fence ride later done-lines, gated on his stamp (D-4). Witness before actuator — the grain of `gaps`/`heal`/`census`.

## Not in scope

- bdo drawing the first `act_fence` (his gesture; this only makes it safe and legible to).
- The actuator — wiring a real act to self-admit through this, and into `command_guard` / the session seam.
- The owner-communication-seam enforcement (the present-face rail) — the sibling piece this dial makes short, its own done-line.
- Graduating `epic.authoring-platform` and placing the atom under a confirmed arc (D-4, bdo's confirm).
