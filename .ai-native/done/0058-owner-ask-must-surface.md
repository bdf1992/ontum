# Done-line 0058 — An owner-ask cannot strand silently in a report

Written before code, per §9.4. When this line is met, stop.

> **Done when:** a needs-you / awaiting-bdo item that exists in a session
> report but has reached no surface bdo reads is detected by a pure,
> read-only fold (`loop/owner_asks.py` over `.ai-native/reports/`, paired with
> the reflection record check in `loop/reflect.py`) and is *loudly surfaced*
> two ways that close the hole report 0047 exposed (five taps written only
> into an uncommitted working-tree file): a fail-open `UserPromptSubmit` beat
> screams every unsurfaced owner-ask group every turn and grows louder the
> longer it sits (the `mock_shame` grain), and a new reflect drift kind
> **owner-ask-backlog** (`RULE_KINDS` + `DRIFT_BY_KIND`, the shared gh
> translator unchanged) offers each report's parked asks to his GitHub inbox
> through the existing reflector pen once bdo admits the rule — never a second
> write path, never acting as bdo (D-4). An owner-ask whose id carries an
> `open` reflection record is *silent*: the beat says nothing of it and the
> drift opens nothing. Proven by the §10 pair, hit directly: a locally-complete
> report whose needs-you list no reflection acks refuses to stay hidden (the
> fold returns it, the drift yields one `open` act, the subprocess beat prints
> it), and the same report once an `open` reflection is recorded for its id
> goes silent (drift `[]`, beat quiet) — and the fold returns `[]` (never
> raises, beat exits 0) on a rootless / reportless tree.

## Out of scope, named

- **Auto-closing a surfaced owner-ask.** A free-text report ask carries no
  log-backed "answered" signal, so the mirror is open-only: bdo dismisses an
  issue by his own gesture and it never reopens (the divergence kind's
  close-on-reconcile has no analogue here). A later log-backed resolution
  signal is a separate increment.
- **Suppressing the standing historical backlog.** The fold reads every
  report, so first activation surfaces the real debt already on disk (one
  aggregate issue per report, the divergence grain - not one-per-item); a
  recency/baseline scope to mute pre-existing history is deferred and named,
  not silently coded in.
- **Parsing prose "awaiting bdo" mentions.** The anchor is the scaffolded
  `## needs-you` heading (the report pen's contract); inline prose mentions
  are not treated as asks.
