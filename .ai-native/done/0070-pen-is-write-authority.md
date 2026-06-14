# Done-line 0070 — the records pen is the write authority — a raw Write must be its carbon copy

A `.pen.json` records directory declares a form, but the write guard only
checked that a raw Write *resembled* the form (pattern + id + required
sections) and then allowed it — even lending its fleet-id fold as a
*convenience* for hand-written records (a session reasoned "the write-guard's
placement will confirm the id" and wrote a done-line by hand). Form-
resemblance is not the pen. The pen alone asserts the fleet-safe id from the
fold, stamps the exact heading, and writes LF/UTF-8 bytes the way `.ai-native`
byte-identity depends on; a raw Write can drift in any of these (CRLF on
Windows is the silent one) and still pass the old check.

bdo's model (live, 2026-06-13): the pen must be respected, but a raw Write may
pass *as a carbon copy* — if its bytes are what the pen itself would have
produced for that filename, it IS the pen's output, typed by another hand. If
the copy diverges, it is refused, and the refusal is the fail notification.
There must be exactly one definition of "what the pen would write," shared by
the pen and the guard (I-4) — never two.

> **Done when:** `loop.pen` exposes one `carbon_divergences(cfg, name,
> content, expected_id)` — the single definition of a faithful pen record
> (fleet-safe id, the pen's heading, required sections, LF-only bytes,
> trailing newline) — and the write guard imports it: a raw Write into a
> penned directory passes iff it is a zero-divergence carbon copy, and is
> otherwise denied with the divergences named and the pen offered; the pen's
> own output is proven zero-divergence; proven by tests where two locally-fine
> records refuse to fit (a faithful copy passes; its CRLF twin and a
> wrong-id/wrong-heading twin are refused).
