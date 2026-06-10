---
name: branch-ritual
description: >
  The branch lifecycle ritual for this repo — summon, work, hand off, stamp,
  dissolve. Run it at session end to hand work off toward main, when the
  Branches page needs reading or cleaning, or when work is stranded on a
  merged branch.
version: 0.1.0
owner: bdo
changelog:
  - version: 0.1.0
    note: >
      First form. Lifted from docs/sop/branch-management.md (PR #5) and
      recast from a doc we read into a ritual we run — per §7, this changes
      what sessions admit and route, so it's versioned prompt-as-code, not
      prose. We expect to get better at this; sharpen the file as we do.
---

# The Branch Ritual

The doctrine applied to git: sessions are mortal (D-7), a branch is the
session's container, truth is what's merged to the trunk (D-5), and the owner
is the last stop (D-4). This file is the repeatable form of that. It is ours
to craft — if a pass through it fights the work, change it (see the last
section), don't work around it.

## Standing shape — hold these while doing anything below

- **`main` is the trunk and the only long-lived branch.** Everything on it
  carries the owner's stamp. The repo's default branch is `main`.
- **One session, one branch, one PR, one stamp.** The auto-named `claude/*`
  branch is the session's container; its name carries no meaning — the PR
  title and the session report do.
- **A merged branch is dead. Never push to it.** A commit pushed after the PR
  merged is stranded — nothing is watching it, and it silently never reaches
  `main`. New work means a new branch. *(This rule exists because it
  happened: the README/LICENSE commit stranded after PR #2, recovered in
  PR #4.)*
- **Never merge your own PR; never push to `main`.** Work propels itself, it
  never authorizes itself (§4). The stamp is bdo's. *(Firm.)*

## Hand-off — run at session end, or when the work is done

1. **Tests first:** `python -m unittest discover -s tests -v`. Red means fix
   or shrink scope (§9.5) — don't hand off red without saying so.
2. Confirm you're on this session's `claude/*` branch and everything is
   committed — small, step-shaped commits with messages that say what landed.
3. Push: `git push -u origin <branch>`.
4. Open **exactly one PR** to `main`. The description carries: what landed,
   which done-line it serves, the session report number, and the end-state
   (`done | report | needs-you`).
5. **Stop.** Do not merge it. Tell bdo it's at the stamp.
6. After the stamp lands, the branch gets deleted (the button on the merged
   PR page). Dissolved, not archived — `main` already holds the truth.

## Gardening — run when the Branches page confuses or accumulates

Decode every branch against `main` using the `Behind | Ahead` columns:

| reads | means | move |
|---|---|---|
| `0` ahead | nothing `main` doesn't already have | delete it |
| `N` ahead, open PR | work in flight | normal — at the stamp when ready |
| `N` ahead, no PR | stranded work | open a PR for it, or write it off in a report, then delete |
| `N` behind | `main` moved on — harmless by itself | nothing; matters only if the PR conflicts |

Recovery moves:

| situation | move |
|---|---|
| commit stranded on a merged branch | PR that branch → `main`; stamp; delete (the PR #4 pattern) |
| PR conflicts with `main` | rebase the session branch onto `main` and force-push *your own branch* (never `main`); the stamp still belongs to bdo |
| a branch nobody remembers | `0` ahead → delete; otherwise read its diff, then PR it or write it off in a report — don't leave it to rot |

The page is clean when it reads: `main`, plus whatever is in flight right
now — and nothing else.

## When the ritual itself is wrong

This is a skill we get better at. If running it fights the work, change this
file in the same PR as the work it fought — bump the version, add a changelog
line saying what got sharper, and bdo's merge is the stamp on the new form.
Don't fork a second copy anywhere (I-4): this file is the only form of the
ritual.

## The tripwire, applied here (§12)

Branch gardening is not the work. If a session catches itself tending the
Branches page instead of building the next §11 step: file the PR, dissolve
what's dead, go build.
