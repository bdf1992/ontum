# Done-line 0149 — the gate/fence primitive: actor-blind barrier-links, a closed fence, a gate as its opening

Written before code, per §9.4. When this line is met, stop.

bdo's shape (2026-06-20): we have *gateways* (policy — they decide), but no
deterministic *gate* that closes a gateway and no *fence* around the route. A
gate and a fence are physical, not political — actor-blind, deterministic: "you
can see through it, you can't pass it, you can't climb it, and touching it
bites." A fence must loop; an open fence accomplishes nothing.

Three terms:

- **barrier-link** — the atom (bdo: "Barrier might be an atomic example"): a
  pure, actor-blind predicate over an act's observable form,
  `decide(act) -> {allow, reason}`. Laws: deterministic, model-free, actor-blind
  — the verdict reads only the act and the object, never *who* acts or their
  authorization (that read is what makes a gateway political).
- **fence** — a *closed loop* of barrier-links around a named territory. Laws:
  closed (every route in is covered — the front, the meshed *seams* between
  links, the tall *top*/escalation), barbed (a blocked act is witnessed, never
  silently deflected), not-opaque (every link carries a cold-reader reason).
- **gate** — a barrier-link at a sanctioned opening *in* a fence.

> **Done when:** \`fence/barrier.py\` declares the barrier-link contract (\`decide\`, the three actor-blind laws, a \`validate\` that REFUSES a link reading actor-authorization) and the fence contract (a closed loop over a territory, \`validate_fence\` enforcing closure across the front/seam/top route taxonomy, barbed-ness, and non-opacity); and \`tests/test_barrier.py\` proves every law BITES on the real trunk-mutation territory — a fence missing the seam route (our actual git-fence tear: \`python\` shelling \`git push\`) is REFUSED, a link reading an authorization record is REFUSED, an opaque link is REFUSED, and the matcher is non-vacuous — the test going red if any law is neutralized.
