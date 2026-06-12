# Report 0049 — Version supersession becomes a fold-level truth — the Field's phantom parked piece is gone

This session opened to bdo's gestures already landed (epic.the-field confirmed,
adm.6e3ccedc1f0b; the judge rung granted to the summoned-session and the
branded-subagent classes) and the gap backlog handing every session the same
top gap: atom.field-topology.v0, parked. That gap was a phantom, and removing
the phantom — not re-working the settled piece — was the work.

## What was true

The Field's first piece had already settled: `atom.field-topology.v1` walked all
five gates and was value-confirmed (rcp.7f20dabffacd), and `loop/field.py` exists
and folds an arc's topology. The parked atom the backlog pointed at, `.v0`, was
the predecessor the value-confirm gate correctly *missed* when it announced
delivery before the build existed — the §10 catch working exactly as designed.
v1 is the amend of v0. But `loop.gaps` and `loop.field` judged each atom version
in isolation, so a settled piece haunted the backlog as the loop's #1 work item,
and the summon hook handed that phantom to every fresh session.

## What changed (done-line 0056)

Version supersession is now a fold-level truth, placed where identity is already
defined. `reconcile.py` gains `atom_version` / `superseded_atom_ids`: an id parses
as `<stem>.v<N>`, the highest N per stem is live, the rest are superseded. It reads
only the suffix already on disk — retires nothing, writes nothing, admits nothing.
The architecture's own corollary (editing an atom mints a new version; old receipts
"stay valid history but no longer apply") made into a pure function.

- `loop.gaps.parked_piece_gaps` suppresses a superseded version. The
  field-topology phantom is gone; the honest next gap (an idle organ) takes the
  top line.
- `loop.field._story_rung` relabels a superseded version "superseded", not
  "parked": the topology still shows v0 (the past is part of the map) but never
  miscalls it a live held piece.

The §10 pair is pinned both ways: the real divergence (parked v0 under confirmed
v1) must NOT surface, AND a still-highest parked version with no successor MUST
still surface — a fix that silenced the held piece with the phantom fails the
second half. Plus a direct unit test of the helper. Full suite green: 575.

## End-state

- PR #106 open and merge-node eligible (under confirmed epic.the-field); branch
  `claude/version-supersedes-parked`, commit 888ae41. Landing is the merge-node's,
  not mine and not bdo's.
- done-line 0056 written before the code and met; minted one-shot through the
  pen after a first stub tripped the freeze guard (see needs-you).
- Viewport restored to `main` by this session at end (no off-trunk strand left).

## needs-you

- **Nothing blocking.** Two things surfaced, not offloaded:
- **The done-pen / freeze-guard seam.** `loop.pen new done` (without `--body`)
  scaffolds a placeholder line, then `freeze_guard` immediately freezes that
  placeholder — so the only way to author a done-line is the one-shot `--body`
  path; the scaffold-then-fill path the pen's own message advertises ("fill the
  placeholders before committing") is dead on a frozen dir. I worked around it
  (removed the stub, re-minted with `--body`). Worth a decision: either drop the
  placeholder note for frozen dirs, or let freeze_guard permit a fill while the
  required `> **Done when:**` line is still the literal placeholder. Your call —
  it is a contract surface.
- **A prior session's stranded handoff, left as found.** `report 0047`,
  `.ai-native/epics/epic.causality-surface.json`, and
  `docs/sources/epic.test-metabolism.v2.md` are untracked, and `exports/log.jsonl`
  carries uncommitted envoy seals — all from the session that ended mid-arc and
  handed the Field build off (report 0047 itself). Your arc-confirm and the rung
  grants are already committed and safe; this loose state is not mine to land
  under this PR (it would conflate authorship), so I left it untouched and name
  it here.
