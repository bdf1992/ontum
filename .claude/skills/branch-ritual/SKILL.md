---
name: branch-ritual
description: >
  The branch lifecycle ritual for this repo — summon, work, hand off, stamp,
  dissolve. Run it at session end to hand work off toward main, when the
  Branches page needs reading or cleaning, or when work is stranded on a
  merged branch.
version: 0.2.0
owner: bdo
changelog:
  - version: 0.2.0
    note: >
      Sharpened after PR #8 reached the stamp story-less: a recovery PR
      wore the auto-title over an empty body, and the stranding it
      recovered (pushes to busy-feynman after PR #6 merged) repeated the
      PR #2 failure. The story rule now binds every PR to main, recovery
      included; hand-off checks for a dead branch before pushing; and
      `gh pr edit` is named as the repair for an unwritten story.
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
- **Every PR to `main` carries its story — recovery PRs included.** A PR
  wearing the auto-title (the branch name) over an empty body is an
  unwritten story: not at the stamp, however green the merge button.
  GitHub's "Compare & pull request" button produces exactly this — fill
  the form, or repair after the fact with `gh pr edit <n> --title --body`.
  *(This rule exists because it happened: PR #1 and PR #8 both reached
  bdo story-less.)*

## Hand-off — run at session end, or when the work is done

1. **Tests first:** `python -m unittest discover -s tests -v`. Red means fix
   or shrink scope (§9.5) — don't hand off red without saying so.
2. Confirm you're on this session's `claude/*` branch and everything is
   committed — small, step-shaped commits with messages that say what landed.
3. **Confirm the branch is alive** before pushing: if a PR from it has
   already merged (`gh pr list --head <branch> --state merged`), the
   branch is dead — cut a fresh branch from where you stand and push that
   instead. *(The PR #6 → #8 stranding happened exactly here: nine commits
   pushed to a branch whose PR had merged an hour earlier.)*
4. Push: `git push -u origin <branch>`.
5. Open **exactly one PR** to `main`, story written in — explicit
   `--title` and `--body`, never the defaults. The description carries:
   what landed, which done-line it serves, the session report number, the
   end-state (`done | report | needs-you`), and anything the commits
   flagged *for bdo* — the PR is where those flags surface, or they
   scroll away with the log.
6. **Stop.** Do not merge it. Tell bdo it's at the stamp.
7. After the stamp lands, the branch gets deleted (the button on the merged
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
| commit stranded on a merged branch | PR that branch → `main` — with its story (what stranded, how, what it carries); stamp; delete (the PR #4 pattern) |
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
