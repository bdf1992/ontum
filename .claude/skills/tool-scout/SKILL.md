---
name: tool-scout
description: >-
  Agentic search over what tools actually exist to do a job — CLI programs
  on PATH, and this repo's own skills, workflows, and loop.* commands. Use
  when bdo or a session asks "what tool do I have for X", "is there already
  something that does Y", "find a program/command for Z", or before building
  new tooling (to check it isn't a double-build, §10). Not a registry: it
  indexes what is actually on disk/PATH right now, so a fresh scan is always
  live. Installed GUI applications and repos outside this session's scope are
  named out of index, not claimed absent.
version: 0.1.0
owner: bdo
changelog:
  - version: 0.1.0
    note: >-
      First cut, built to a 15-minute window (bdo, 2026-08-14). Indexes four
      sources with one pure stdlib pen (scout.py, no network, no writes, no
      subprocess execution of what it finds): PATH executables, this repo's
      .claude/skills/*/SKILL.md, .claude/workflows/*.js meta blocks, and the
      python -m loop.* commands documented in loop/CLAUDE.md. Simple
      token-overlap ranking, not embeddings — good enough to shortlist, the
      session reads the shortlist and judges. Cross-repo indexing is wired
      (--repo, repeatable) but this session only has one repo attached
      (bdf1992/ontum); a sibling repo's tools are indexed the moment it's
      attached and passed with --repo, never assumed present. Forking the
      causality/term_economy.py graph engine was considered and declined —
      different domain (ontum's vocabulary vs. installed tools) and doctrine's
      "don't double-build" (§10); this pen reuses the *pattern* (pure,
      read-only, stdlib fold; sibling of loop/gaps.py and
      causality/term_economy.py in grain) instead of forking the code.
      Naming note (surfaced, not silently resolved): this repo already has a
      capital-S **Scout** — `loop/scout.py` / `ScoutCTA` (done-line 0148,
      epic.strategy wave 2), a strategic-conjecture generator that derives
      and emits a grounded call-to-action toward an arc. Unrelated to this
      skill: that Scout reasons about *what move to make next on an arc*;
      this tool-scout indexes *what CLI/skill/workflow tools already exist*.
      Kept the requested name (bdo's literal ask) since the hyphenated
      compound reads distinctly, but naming this here so `causality`'s
      overloaded-term check has the disambiguation on record if it ever
      mines this file.
---

# tool-scout — find the tool before you build one

A session (or bdo) asks "is there already something that does X?" more often
than the answer is discoverable in fifteen seconds. This skill is the
answer: a deterministic, read-only index over what tools actually exist,
searched by keyword.

**Not to be confused with:** `loop/scout.py` (capital-S Scout / `ScoutCTA`,
done-line 0148) — that's the strategic-conjecture generator for
`epic.strategy`, unrelated in purpose. This skill finds *tools*; that one
proposes *moves*.

## When to use this

- Before building new tooling — check it isn't a double-build (doctrine §10,
  "don't double-build `epic.the-field`'s fold or the minted surfaces").
- "What CLI program handles \<task\>?"
- "Do we already have a skill/workflow/loop command for \<thing\>?"
- Orienting in an unfamiliar corner of this repo's tool surface.

## What it indexes (and what it honestly doesn't)

`scout.py` is a pure stdlib fold — no network, no writes, and it never
executes anything it finds. Four sources, each a plain read of files/PATH
already on disk:

| kind       | source                                              |
| ---------- | ---------------------------------------------------- |
| `path`     | every executable found on `$PATH`                    |
| `skill`    | `.claude/skills/*/SKILL.md` (name + description)     |
| `workflow` | `.claude/workflows/*.js` (`meta.name`/`description`) |
| `loop`     | `python -m loop.<x>` commands documented in `loop/CLAUDE.md`, with their inline comment |

**Not indexed, named honestly rather than silently missing:** installed GUI
applications (this session runs in a container with no desktop), any repo
not attached to this session (`add_repo` first, then pass `--repo`), and
anything not named on PATH or in the four sources above. Absence from a
result set means "not found in what was indexed," never "does not exist."

## Running it

```sh
python .claude/skills/tool-scout/scout.py "<query>"                  # all sources, this repo
python .claude/skills/tool-scout/scout.py "<query>" --kind path      # PATH only
python .claude/skills/tool-scout/scout.py "<query>" --kind skill --kind workflow --kind loop
python .claude/skills/tool-scout/scout.py "<query>" --repo /path/to/other-repo   # index another attached repo too (repeatable)
python .claude/skills/tool-scout/scout.py "<query>" --json --top 10  # structured, for a session to reason over
```

Ranking is plain token overlap between the query and each item's
name+description (plus a substring bonus on the name) — no embeddings, no
inference call. It is a **shortlist generator**, not a final answer: read
the shortlist, then judge (the session's own acceptance, before anyone
else's — see the doctrine's "earn your own acceptance first" invariant).

## Agentic use (how a session should drive this, not just run it)

1. Turn the natural-language ask into 2-4 keyword queries (synonyms too —
   token overlap is literal, not semantic: "graph" won't match "visualize").
2. Run each query, `--json` if you're going to parse results rather than
   read them.
3. Read the top few hits' descriptions before answering — a name match
   without a description read is a guess, not a finding.
4. If nothing lands, say so plainly and name what wasn't indexed (a repo not
   attached, a GUI app this container can't see) rather than asserting the
   tool doesn't exist anywhere.

## Extending it

A new source is a new `index_*(root)` function returning a list of
`{kind, name, description, source}` dicts, wired into `build_index`'s
`kinds` set — the same shape every source already returns, so ranking and
output need no changes. Keep it read-only and stdlib; if a source needs a
dependency, name it in the changelog the way the repo's blanket-ban lift
requires (`loop/CLAUDE.md`: "a third-party dependency is admissible when
common sense says it creates real value... provided it stays offline and is
named").

## In plain English

This is a fast, offline search tool: type in what you're looking for (like
"graph" or "export"), and it lists matching command-line programs on this
machine plus matching skills, workflows, and loop commands already in this
repo — so you can check whether something already exists before building it
again. It does not see installed desktop apps or other repos unless you
attach and point it at them. It only searches and lists; it never runs
anything or changes anything.
