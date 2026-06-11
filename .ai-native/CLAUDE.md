# .ai-native/ — the records

The durable half of the loop: everything here is files, and sessions
are mortal — the files are what survives. Byte identity matters in this
tree: `.gitattributes` exempts it from eol conversion entirely and
union-merges the logs (done-line 0007 records why).

- `log/` — three append-only JSONL files: `events.jsonl`,
  `receipts.jsonl`, `admissions.jsonl`. The log is truth; never edit a
  line, only append through `loop.reconcile.append_line` (line-atomic,
  torn-tail tolerant).
- `atoms/` — the units of work. An atom's pipeline identity is the
  sha256 of its file bytes; editing the file restarts its pipeline from
  scratch while old receipts stand as history.
- `nodes/` — versioned node prompts (§7, done-line 0009):
  `<node-id>.md`, delivered by the summons, hashed onto receipts as
  `prompt_hash`.
- `epics/` — first-class arcs (arc, horizon, pieces + glue). The owner
  steers here, not at ticket scale (done-line 0006).
- `done/` — numbered done-lines, written *before* the work (§9.4). When
  the line is met, stop. **Frozen** (done-line 0033): the directory's
  `.pen.json` declares `"frozen": true`, and `freeze_guard` denies any
  in-place edit or overwrite of a written line — the bar you set is not
  a draft. Changing what done meant is additive and deliberately
  painful: `python -m loop.pen supersede-done --abandoning <id>
  --slug <new> --done "<new bar>" --reason "<honest reflection>" --by
  <who>` writes a new line carrying the abandonment reflection, records
  a loud `done_superseded` admission, and never self-authorizes a
  session's own (no one signs their own line — it sits pending bdo).
- `reports/` — numbered session reports; each session ends with one,
  including end-state and anything surfaced as `needs-you`. Conflicts
  between instructions get named here, not silently resolved.

`queues/` and `offsets/`, when present, are cache — a pure fold over
the log, deletable and rebuilt at any time.
