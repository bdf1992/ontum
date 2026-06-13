# Report 0061 — the pen is the write authority — carbon-copy write-through

## What landed

bdo caught a session hand-writing a done-line with the `Write` tool while
leaning on the write guard's id fold to "confirm" the id — the guard was
treating form-resemblance (pattern + id + required sections) as governance and
even lending its fold as a convenience. Form is not the pen.

Built **done-line 0070**: the pen is the write authority, and a raw `Write`
into a `.pen.json` records directory is allowed only as a faithful **carbon
copy** of what the pen would have produced — bdo's write-through model. One
shared definition, `loop.pen.carbon_divergences` (fleet-safe id, the pen's
heading, required sections, LF-only bytes, trailing newline), is imported by
the write guard (from its own repo, so tests still resolve the real pen) and
self-checked by the pen itself, so neither can disagree about what a record is
(I-4). A divergent write is refused with the divergences named — the refusal
*is* the fail notification; if the pen module is unreachable the guard fails
open loudly. Builds on and **rescues the stranded `claude/pen-fleet-safe-id`
branch (done-line 0062)**, which made the pen claim the fleet-safe id — the
prerequisite single id-source. CRLF-on-Windows divergence is now caught, which
the old check missed entirely.

Tests in the §10 spirit (locally-fine records that refuse to fit): a faithful
copy passes; its CRLF twin, a no-trailing-newline copy, a heading-id-vs-
filename mismatch, a wrong-id copy, and a malformed name are each refused and
named; the pen's own output is proven zero-divergence. Full suite 607 passing.
Landed as PR #128 through the PR pen.

## needs-you

- **bdo: name/confirm the arc for PR #128** (lean: `epic.owner-harness`) — it
  is merge-node-eligible the moment its arc is confirmed; the merge-node lands
  it, not me, not you. Confirming the arc also lets the carried done-line 0062
  finally land, retiring the stranded `claude/pen-fleet-safe-id` branch.

## End-state

`report` — carbon-copy write authority built, tested (607 green), and opened as
PR #128 off a rescue of the stranded 0062 branch; awaiting bdo's arc
confirmation for the merge-node to land.
