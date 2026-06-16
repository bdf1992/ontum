# Done-line 0086 — The cited sensor — data into evidence, ghosts refused

Written before code, per §9.4. When this line is met, stop.

> **Arc:** epic.digital-experience
> **Piece:** atom.cited-sensor.v0
> **Probe:** P2 (cited sensor)

Derived by the loop-maker from done-line 0085's braid (it read the prior loop's
tie and named this piece next). The data→evidence half of the digital-experience
fold: a read-only sensor over a person's data surface (a directory of files) that
emits **cited** evidence — each record carrying a resolvable citation the way
`causality/term_economy.py` demands of a term's backing. The discipline is
**reused, not rebuilt** (§10): resolution is `term_economy.resolve_evidence`, and
an unresolvable citation is a `ghost`, refused at the door (no evidence, no node).
This is the bottom of bdo's "the information already exists on the machine" fold,
on a real (testable) corpus: the bytes are truth, the citation is the route back.

> **Done when:** `causality/cited_sensor.py` provides `scan(data_root)` (a
read-only walk emitting cited evidence records — file, kind, size, content-anchor)
and reuses `causality.term_economy.resolve_evidence` for the ghost test, with
`cited(data_root)` returning only records whose citation resolves and `ghosts()`
naming those refused; and `tests/test_cited_sensor.py` passes under
`python -m unittest`, proving the teeth — (1) a real tmpdir corpus yields evidence
whose citations all resolve, (2) a record citing a nonexistent path is a ghost,
(3) a record citing a real file with a fabricated content-anchor is a ghost, and
(4) the scan writes nothing (the corpus bytes are unchanged after a scan).
