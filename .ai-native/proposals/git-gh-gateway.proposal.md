# The git/gh gateway (PROPOSED — bdo's, 2026-06-19): govern the last ungoverned seam

**Status:** PROPOSED. **Naming and the arc are bdo's (D-4); a session may only
propose.** Born from the 2026-06-19 landing wave (12 PRs cleared by orchestrated
headless merge-nodes) and the retrospective that followed it. The companion
memory is `ontum-git-gh-gateway`.

## The diagnosis

Every major seam in ontum is already a **governed gateway** — a PEP over a flow,
default-deny where it bites:

| seam | gateway |
|---|---|
| thinking (which mind may judge) | the inference gateway (`loop/inference.py`) |
| node-acts (land / judge) | the spawn rail (branded `ontum-node:*`) |
| writes (new files / records) | `write_guard` + the pens |
| tools (external commands) | `command_guard` + the fence registry |
| **delivery to main (git/gh)** | **half-governed — and trusts an outside authority** |

`command_guard` denies raw `git`/`gh` *mutations* and routes them through the
PR pen and git pen — so half a gateway exists. But the pens then call `gh`/`git`
directly and **believe whatever GitHub reports.** That is the hole. Git/gh is
the one major seam that is not a proper gateway, and it is the seam through
which work actually reaches `main`.

## The evidence (the landing wave, on the record)

16 PRs sat unlanded. The digest read *"your move: nothing"* and **all 10 arcs
were confirmed** — so the blocker was never the owner's authority (the loop
already moved his stamp to arc-tier, done-line 0028). It was the ungoverned
delivery seam:

- **GitHub's `mergeable` field lies here.** GitHub computes it *without* our
  `.gitattributes` union-merge driver, so our append-only logs read as
  conflicts on nearly every PR. `pr.py land` refuses on that field
  (`pr.py:743`) — so work that passed every gate could not land because of a
  cache artifact. The truth (`git merge-tree`) showed most PRs clean.
- **A crash shipped CI-green** (#230): a `ValueError` in the shared land path
  passed the off-log gate (no test exercised `cmd_land`'s logic) — it would have
  broken *every future land*. Caught only by a merge-node dry-run, not the gate.
- **Refresh races and stranded worktree state** — no single seam to serialize
  the drainer through; `main` moved every ~6–14 min while agents raced it.

These are not five bugs. They are one missing gateway.

## The shape

Complete the `command_guard`/fence/pen trio into a real gateway in the
separation-of-powers grain (memory `ontum-gateway-separation-of-powers`):

- **PEP (enforcement):** the pens (`git.py`, `pr.py`) — already are.
- **PDP (decision):** policy keyed on reversibility × uncertainty — *what is
  free, what is gated*.
- **PIP (truth):** answer *"mergeable / conflicted / landed?"* from `git`
  (the local source of truth), treating **GitHub as a deterministic reflection
  to reconcile, never an authority.** This is **D-13 (#230) generalized** from
  the merge receipt to all of git/gh.
- **Audit (provenance):** every git/gh act emits a receipt — attributable,
  replayable, the three A's (#239) biting at the delivery seam.

## The load-bearing asymmetry (bdo's, verbatim 2026-06-19)

> *"You can see through the gate, but the patrol will see you."*

**Writes get authorized. Reads get witnessed.** Two verbs, split by
reversibility:

- **Mutation / land** → *authorization*. Default-deny; needs a grant
  (rung / arc-confirm / policy). The patrol can **stop** you.
- **Read** → *attribution*, never authorization. The gate is **open** — no
  prompt, no grant — but you do not pass through it invisibly: the read lands on
  the record (*who read what, at which offset*). The thing made impossible is
  not *reading* but **unobserved reading.**

There is no "authorized read" and we build no read-ACLs — that is the cage.
A read's governance is **the trace it leaves**, not a permission it earns. This
is the **one-way glass**: open to look through, but the room knows you looked.

Two consistencies this preserves:
- It keeps reads frictionless — exactly the lesson of #223 (read-only git
  introspection, just freed from prompting; teeth belong on reversibility ×
  uncertainty, and a read has neither).
- It honors ontum's disclosure stance — *everything in the repo is in-bounds
  for disclosure; the **envoy seal** is the gated egress*. The teeth live on the
  **use/send**, not the look. A sensitive read stays open + witnessed;
  authorization bites when you act on or ship what you read.

And it completes a real provenance hole, the generalization of **`context-hash`
(#204, just landed):** a verdict's full input set — including what it *looked
at* — is on the record, so the decision is truly replayable, and a session can
no longer read off-record and quietly act on it.

## What policy already says — and where it goes silent

The asymmetry is **not new.** `fence/policy.py` (the registry `command_guard`
derives its rules from) already encodes it at the **command-typing surface:**

- **Writes are gated.** Every rule targets a *mutating* verb — `forbidden`
  (`git add`/`commit`/`push`, all `gh pr` writes) or `prompt` (`git merge`/
  `rebase`/`reset`/`rm`, `branch`/`worktree` mutations, `gh issue` mutations,
  `gh api -X POST/PUT/PATCH/DELETE`).
- **Reads pass, and are watched.** No rule matches a read; the fence is a
  prompt/deny list, so unmatched commands are allowed. The registry says it
  verbatim: *"narrowing the argv to the mutating verbs/flags lets read-only
  forms fall through to allowed while topology still prompts. The Claude guard
  watches all of it regardless."* Done-line 0120 (#223) was a deliberate step
  *toward* this — it split `git branch`/`worktree` so read-only introspection
  stopped being prompted.

So the fence is already a witness-reads / authorize-writes PEP. **The gateway is
finishing the fence's own sentence, not starting a new one.**

Where policy goes silent is the exact gap this proposal names. The fence
governs *only what a session types raw* — its own comment: *"the reflector and
gate pens reach GitHub through subprocess, **invisible to this guard — so these
rules govern only what a session types raw.**"* The moment control is **inside a
pen**, policy stops: `pr.py` calls `gh` and trusts GitHub's `mergeable`
(pr.py:743), and no policy governs that, because it is below the typing surface.
The pen's own git/gh reads are not witnessed either.

Two honest measurements of the current state, then:
- Writes: **well-governed at the surface, weakly inside the pens.**
- Reads: **watched but not witnessed** — dumped to `tool-use.jsonl` as a passive
  watch-log, not a first-class attributed receipt. "Logged as reading through
  the gateway" wants this promoted from a watch-trace to provenance.

The gateway extends the fence's existing asymmetry **one layer down, into the
pens**, and promotes the read-witness from a watch-trace to a receipt. Same
rule, pushed where it currently can't reach.

## First organ (the slice to prove the shape)

Do **not** boil the ocean. The gateway's first organ owns one question:

> **"Is this landable?" — answered from `git merge-tree`, never GitHub's field.**

Concretely: relocate the `pr.py:743` mergeable check into the gateway's PIP
(truth from git), receipt every land, and run the landing-throughput drainer
(#226) and the herald through this one seam. That single slice fixes the spurious
`mergeable`, gives the land path a testable contract (closing the #230 class),
and serializes the drainer (killing the races) — the three pains of this session,
in one narrow, behavior-tested increment. Patch the bug **as the first organ**,
not as a one-off in `pr.py`.

## Connections (compose, do not double-build — §10)

- **D-13 / #230** — GitHub as deterministic reflection of local; the gateway is
  the reconciler that enforces it for all git/gh, not just the merge receipt.
- **#245** — the pens don't work from web/mobile; a gateway abstracts the
  surface, so the remote-parity fix falls out of the same arc.
- **landing-throughput-response / the herald** — the drainer is *the* client of
  this gateway; it does not get its own merge path.
- **the inference gateway** — the symmetric twin: that one governs which minds
  may think; this one governs how work reaches main. Both are PEPs over a seam.

## Cautions

- **Thin, local, stdlib.** A PEP hook + the pens, not a service. The local-first
  hard rule holds (no broker, no daemon, no runtime network).
- **Don't prison reads** (the #223 regression in reverse). Witness ≠ gate.
- **Relocate, don't merely patch.** The mergeable fix moves *into* the gateway
  so the next git/gh-trusts-GitHub bug is fixed by construction, not patched
  again at a new call site.
- **Read-witness volume is a fold problem, not a principle problem** — append-only,
  foldable, witnessed at a useful grain (what/who/when), not every byte.

## Open / deferred (named, not invented)

- The full coverage past the land-readiness organ (every git/gh op through the
  seam, reads included).
- The witness-log home and its fold (sibling of `tool-use.jsonl`).
- Remote-surface parity (#245) as a later organ.
- The PDP's policy table (the reversibility × uncertainty cuts) as admitted
  records, not code constants.
