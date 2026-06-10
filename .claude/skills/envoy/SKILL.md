---
name: envoy
description: >-
  Export the repo as a sealed package of at most ten flat files — an arc
  with visuals (Mermaid/ASCII), code, tests, documentation, and git
  history — for review by another model family through a chosen
  perspective and framing. Use when asked to export the repo, package it
  for external or outside review, get a second opinion from another
  model (GPT, Gemini, or any foreign reviewer), build a review bundle,
  "send this to another AI," or any natural-language request naming a
  subject, an audience, and a lens. The pen is envoy.py beside this
  file; packages land in exports/ and every seal leaves a receipt on the
  committed disclosure ledger.
version: 0.1.0
owner: bdo
changelog:
  - version: 0.1.0
    note: >-
      First form (done-line 0015). bdo's shaping answers, on the record
      (chat, 2026-06-10): visuals text-first with rendering optional;
      everything in the repo in-bounds for disclosure, synthesized
      documents included; gitignored artifacts + a committed receipt
      per seal; core slots + flex slots.
---

# The Envoy

An envoy carries the repo's story to a foreign court: another model
family, another perspective, another framing. The deliverable is a
package of **at most ten flat files** a reviewer can load whole —
deterministic where determinism is possible (maps, history, diagrams,
embedded code), authored where judgment is the content (the briefing,
the arc, syntheses). The pen (`envoy.py`, beside this file) enforces
the contract; this file is how you use it well.

Two things make an envoy different from a zip of the repo:

1. **It tells an arc.** A reviewer who feels the story — what was being
   built, what broke, what was learned — returns judgment. A reviewer
   handed an inventory returns a summary of the inventory.
2. **It leaves a receipt.** Packages are gitignored artifacts, but every
   seal appends what left, hashed file by file, to
   `exports/log.jsonl` — the committed disclosure ledger. An export is
   an act on the record, not a copy that left quietly.

## Reading the ask (the grammar)

A request arrives in natural language. Resolve it into the spec's six
knobs — and when the ask is thin, these are the slots you are silently
filling, so fill them on purpose (or ask):

| knob | the question it answers | when unstated, default to |
|---|---|---|
| **subject** | what part of the repo carries the story? | the whole repo at survey depth |
| **audience** | which model family / reviewer reads it? | "a capable model outside this repo" |
| **framing** | what lens are they asked to take? | fresh-eyes architecture review |
| **questions** | what must they actually answer? | ask bdo — a reviewer aimed at nothing returns generalities |
| **feedback shape** | what comes back? (findings list, memo, scored rubric, refutation) | a findings list ordered by severity |
| **depth/budget** | how much can the reviewer hold? | 120k tokens total, 40k per file |

Framings that have earned names, and what they imply for the flex
slots (compose freely; these are reaches, not rules):

| framing | flex slots that serve it |
|---|---|
| architecture review | `code` (the load-bearing modules), `tensions` |
| red-team / refute-us | `code` + `data` (logs as evidence), `tensions` sharpened into claims to attack |
| doctrine critique | `doc` (the doctrine verbatim), `excerpt` (where practice diverges from it) |
| fresh-eyes explainer ("what is this repo?") | `synthesis` (the explanation), lighter code |
| due-diligence ("is this sound to build on?") | `metrics`, `code` (tests included — receipts, not claims) |
| pedagogy ("teach this pattern") | `excerpt` with heavy commentary, one `code` exemplar |

The slot kinds the pen knows: `briefing` `arc` `architecture`
`repo-map` `history` (the default core), and `code` `doc` `data`
`metrics` `synthesis` `excerpt` `tensions` as flex. Core is a default,
not a cage — drop core slots on purpose when the ask warrants (the
gate requires only the briefing). Ten files minus core leaves five
flex slots; if the ask wants more than fits, **shrink the scope and
ship the smaller package** (§9.5) — never widen the contract.

## The pass

1. **Resolve the ask** into the six knobs above. State your resolution
   in one sentence before building — if a knob is a guess on something
   bdo would care about (especially *questions*), say so or ask.
2. **Scaffold:** `python .claude/skills/envoy/envoy.py new <name>
   --title "..." --audience "..." --framing "..." --question "..."
   [--slot code:loop-core=loop/reconcile.py,loop/node.py ...]`
   Then shape `exports/<name>/.spec.json` directly — order is file
   order, titles are reviewer-facing, sources are explicit (disclosure
   is named, never globbed casually).
3. **Plan:** `... plan <name>` — token math before bytes. Over budget
   at plan time means cut slots now, not prose later.
4. **Build:** `... build <name>` — pen slots materialize; session
   slots arrive as stubs carrying the framing, the questions, and
   per-slot guidance. Rebuild freely: the pen never clobbers authored
   prose, and refreshes only its own marker-fenced blocks.
5. **Author the stubs.** The voice rules:
   - Write for a reviewer with **zero shared context**. Every
     repo-local term (atom, seam, summons, the stamp, done-line) is
     defined at first use or not used.
   - The **briefing** opens the package: what this is, who you (the
     reviewer) are asked to be, the questions, the feedback shape,
     then the manifest. It is the only file you can be sure gets read.
   - The **arc** is a story with turning points, not a changelog. The
     deterministic timeline sits below it as evidence; the narrative
     should make the reader want to check the evidence.
   - **Tensions are the gift.** Real open questions and known
     compromises get real judgment back; a package that hides its
     seams gets compliments back.
   - Every Mermaid diagram you author must read as text without
     rendering — a reviewer without eyes still gets the structure.
6. **Check:** `... check <name>` — the gate refuses: more than ten
   files, stray files the spec never named, unfilled stubs, empty
   files, budget overruns, a briefing missing its manifest block.
   Refusals are instructions, not errors; clear them, don't code
   around them.
7. **Render (optional):** `... render <name>` — Mermaid to SVG in
   `exports/<name>/rendered/` when a renderer exists; degrades to a
   report when none does. Renders ride outside the sealed ten, for
   multimodal reviewers.
8. **Seal:** `... seal <name> --by <who>` — stamps the manifest into
   the briefing, gates again, appends the receipt. Re-sealing
   unchanged bytes is a no-op; changed bytes get a new receipt
   (history accretes, never rewrites). **What you send is what was
   sealed** — if files change after sealing, `list` says `DRIFTED`;
   re-seal before sending.
9. **Record.** The session report names the package, its framing, and
   where it went (or that it awaits sending). When the review comes
   back, what it found belongs in a report too — an envoy that never
   reports back was a postcard, not an envoy.

## What returns

When feedback returns from the foreign reviewer, treat it like any
outside finding: it enters through a report (and `needs-you` items go
to bdo), never directly into code. The reviewer saw a sealed snapshot;
verify every claim against the live repo before acting on it.

## When the envoy itself is wrong

Same clause as the branch ritual: if a pass through this skill fights
the work, change this file and the pen in the same PR as the work they
fought — bump the version, changelog what got sharper. One pen per
seam (the `loop/node.py` pattern): no second path to exports/, and the
ledger is written by `seal` alone.
