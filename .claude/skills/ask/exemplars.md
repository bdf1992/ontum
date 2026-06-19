# ask — exemplars (the reshape gallery)

The worked **before → after** pairs `ask_guard.py` points a refused session
at, and the concrete twin of [policy.md](policy.md)'s rules. The policy says
*no*; the [skill](SKILL.md) says *what good is*; this file shows it — copy the
shape, don't re-derive it.

Each exemplar is one failure mode the refusal check names: the **✗ menu** (what
gets denied, and why), then the **✓ projection** (the reshape). Shapes are
`AskUserQuestion` calls, trimmed to the load-bearing fields.

When an ask teaches a new shape (a breakout, a praised panel, a refusal you
should have made), the *learning* goes to the registered memory
`ontum-ask-surface-discipline`; the *exemplar* — if it generalizes — comes
here. The memory is the diary; this is the pattern book.

---

## E1 — Recommendation-first (R1). *The canonical breakout.*

The failure bdo named on 2026-06-18: a question that makes him break out to
*Other* to type "whats recommended?" withheld the one thing he wanted.

**✗ menu** — a bare list, no pick surfaced:

```
question: "Which storage backend?"
options:
  - { label: "SQLite",   description: "" }
  - { label: "Postgres", description: "" }
  - { label: "flat JSON", description: "" }
```

> *Refused (R1):* no option is `(Recommended)`; the descriptions are empty.
> A list of options is still a queue. He has to break out to ask for your pick.

**✓ projection** — your reasoned pick, first, the *why* in the description:

```
question: "Which storage backend? (I recommend SQLite)"
options:
  - { label: "SQLite (Recommended)",
      description: "Local-first, zero-config, in the stdlib — matches the
        no-daemon hard rule. The log stays the truth; SQLite is just the
        cache index. My pick unless you want multi-writer." }
  - { label: "Postgres",
      description: "Only if you foresee concurrent writers off one host —
        adds a daemon the local-first rule forbids today." }
  - { label: "flat JSON",
      description: "Simplest, but O(n) scans once the fold grows past a
        few thousand records." }
```

> The pick is already there, with the *divergence seam* (the one reason you'd
> overrule me) set beside his own judgment. He confirms or corrects — he
> never has to ask "what do you think?"

---

## E2 — Narrate routes, don't label them (R2). *Routes are stories.*

When the options are **routes** (paths with consequences), a bare label hides
the cost and risk. Put the story in `preview`.

**✗ menu** — routes flattened to labels:

```
question: "How should I land the conflicting PR?"
options:
  - { label: "rebase onto main",   description: "rebase it" }
  - { label: "merge main in",      description: "merge it" }
  - { label: "recreate the branch", description: "start over" }
```

> *Refused (R2):* these are routes with real and different consequences, told
> as labels. The description restates the label instead of narrating it.

**✓ projection** — each route a concrete story in `preview`:

```
question: "The PR conflicts only on the append-only logs. How do I land it?"
options:
  - label: "Union-merge main (Recommended)"
    description: "The logs union-merge by .gitattributes; no real conflict."
    preview: |
      git merge origin/main  →  the log driver unions both sides,
      no hand-resolution, history preserved. One push, mergeable.
      Cost: a merge commit. Risk: none — the driver is deterministic.
  - label: "Rebase onto main"
    description: "Linear history, but replays every commit over the logs."
    preview: |
      git rebase main  →  N commits replay; each may re-touch the logs.
      Cost: N chances to hand-resolve the same union. Risk: a dropped
      log line if a replay is fumbled. Cleaner graph, more handling.
  - label: "Recreate the branch"
    description: "Only if the history is itself broken."
    preview: |
      Branch fresh from main, cherry-pick the real change.
      Cost: loses the PR thread and review. Risk: drops receipts.
      Reach for this only when the branch is unsalvageable.
```

> The question is now a *fold of where you are genuinely torn* — he reads the
> trade in the box, not in his head.

---

## E3 — Ask only at a genuine fork (R4). *The most common failure: offloading.*

The refusal that fires most: the decision is one **you could resolve** from the
request, the code, or a sensible default. Fronting it as a question is
offloading onto the owner (the hard rule: *support the owner, never offload*).

**✗ menu** — a call the session owns, handed up:

```
question: "Should I name the test file test_compose.py or compose_test.py?"
options:
  - { label: "test_compose.py", description: "prefix style" }
  - { label: "compose_test.py", description: "suffix style" }
```

> *Refused (R4):* the repo already answers this — every test is `tests/
> test_*.py`. There is no fork here; there is a convention to read. Asking
> manufactures an "only you can decide" that isn't.

**✓ not an ask at all** — make the call, name it, proceed:

> "Naming it `tests/test_compose.py` to match the suite's `test_*.py`
> convention (`python -m unittest discover -s tests`). Proceeding."

> The work *is* making the call. Save the surface for what only he can
> settle — an arc's direction, a name to mint, a reversibility line. If you
> truly can't resolve it, say *why* it's his in the recommended option's
> description, so even the genuine ask carries your reading.

---

## E4 — Configuring is a panel, not a menu (R3 + R7). *Compose the move.*

When bdo is **composing your next move** (not picking one option), raise a
**multi-question panel** — one degree of freedom per question (the tool takes
1–4). And when the fork is about a **design whose shape lives in his head**,
lead with a **multiSelect comprehension checklist (R7)**: surface *your current
understanding* as confirmable items so he can see and correct whether you have
the shape — before you build on a misread.

**✗ menu** — a design decision flattened to one pick, shape unverified:

```
question: "How should the audit fold work?"
options:
  - { label: "per-ask", description: "one record per ask" }
  - { label: "rolling window", description: "fold a window" }
```

> *Refused (R7 + R4):* this is a *design*. A single pick neither verifies you
> understood what he wants nor exposes the dials. He can't tell if you have
> the shape — so he can't correct a misread before it's built.

**✓ panel** — checklist first (verify the shape), then the dials:

```
# Q1 (multiSelect, R7) — verify comprehension FIRST
question: "Check what I have right about the audit fold; uncheck what's off:"
multiSelect: true
options:
  - { label: "It reads the ask watch-log, never a second truth",
      description: "A sensor over tool-use.jsonl, like the watcher." }
  - { label: "'Other'-breakouts are the highest-signal row",
      description: "Where you broke out tells me the menu failed." }
  - { label: "It measures genuine-fork vs offloaded asks",
      description: "The R4 refusal, turned from willpower into a reading." }
  - { label: "It writes nothing — read-only fold",
      description: "Findings only; any act stays a pen's (D-4)." }

# Q2 (single-select) — the one dial that's genuinely yours
question: "Window over which to fold the rate? (I recommend rolling-60m)"
options:
  - { label: "Rolling 60m (Recommended)",
      description: "Matches ask_guard's rate beat; one window, no new dial." }
  - { label: "Per-session",
      description: "Sharper attribution, but resets too fast to see drift." }
```

> Q1 lets him *correct your understanding* with a tap ("you're wrong about the
> second-truth part"); Q2 lets him *set the one real dial*. The routes decide;
> the checklist verifies you understood. He composes the move — he doesn't pick
> from it.

---

## The honest limit (R6)

None of these reskins the modal — its chrome (fonts, layout) is the harness's,
not ours (R6). The lever is everything *inside* the call: the recommendation,
the `preview` narration, the checklist, the memory, the audit. Brand there, not
in CSS. And the mirror stays one-way (R5): the ask carries an answer back; a
confirm, a stamp, an arc still land through their own pens.
