---
title: SOP — Branch Management
status: in force once merged — the owner's stamp on the PR that lands this file is its adoption (D-4)
owner: bdo
scope: repo operations — how work travels through git; not part of the loop itself
---

# SOP — Branch Management

How branches run in this repo, written down once so no session re-derives it.
The shape is the doctrine applied to git: sessions are mortal (D-7), a branch
is the session's container, truth is what's merged to the trunk (D-5), and the
owner is the last stop (D-4).

## The standing shape

- **`main` is the trunk and the only long-lived branch.** Everything on it
  carries the owner's stamp. The repo's default branch is `main`.
- **One session, one branch.** Each working session gets its own auto-named
  `claude/*` branch off the tip of `main`. The name carries no meaning — the
  PR title and the session report do.
- **Branches are summoned, not staffed (D-10).** No shared branches, no
  long-lived feature branches, no direct pushes to `main`.

## Lifecycle of a session branch

1. **Summon.** The harness creates `claude/<name>` from `main`.
2. **Work.** Small, step-shaped commits; push to the session branch freely.
3. **Hand off.** One PR to `main`, opened by the session. The description
   says what landed, which done-line it serves, and the end-state
   (`done | report | needs-you`).
4. **Stamp.** bdo merges (D-4). A session never merges its own PR — work
   propels itself, it never authorizes itself (§4). *(Firm.)*
5. **Dissolve.** Delete the branch right after the merge (the button on the
   merged PR page). A merged branch is a dissolved node: deleting it loses
   nothing, because what mattered is already in `main`.

## Hard rules

- **A merged branch is dead. Never push to it again.** A commit pushed to a
  branch after its PR merged is stranded — no PR is watching it, and it
  silently never reaches `main`. New work means a new branch. *(This rule
  exists because it happened: the README/LICENSE commit stranded after PR #2,
  recovered in PR #4.)*
- **One branch, one PR, one stamp.** If the work outgrows the branch, close
  it out and summon a new one — don't let a branch accumulate a second life.
- **Delete on merge, every time.** The Branches page should read: `main`,
  plus whatever is in flight right now. Anything else is either unmerged work
  (needs a PR) or a ghost (needs deleting).

## Reading the Branches page

GitHub's `Behind | Ahead` columns, decoded against `main`:

| reads | means | move |
|---|---|---|
| `0` ahead | nothing `main` doesn't already have | delete it |
| `N` ahead, open PR | work in flight | normal — stamp when ready |
| `N` ahead, no PR | stranded work | open a PR for it, or write it off in a report, then delete |
| `N` behind | `main` moved on — harmless by itself | nothing; matters only if the PR conflicts |

## Recovery moves

| situation | move |
|---|---|
| commit stranded on a merged branch | PR that branch → `main`; stamp; delete (the PR #4 pattern) |
| PR conflicts with `main` | the session rebases its branch onto `main` and force-pushes *its own branch* (never `main`); the stamp still belongs to bdo |
| a branch nobody remembers | `0` ahead → delete; otherwise read its diff, then PR it or write it off in a report — don't leave it to rot |

## The tripwire, applied here (§12)

Branch gardening is not the work. If a session catches itself tending this
page instead of building the next §11 step: file the PR, dissolve what's
dead, go build.
