# Report 0042 — The un-named mocks: found, screamed, and gated

## What landed

**Done-line 0049 — effective mocks are mocked (PR #81, epic.substrate).**
bdo asked for a scan ("I'm sure we have some") and then gave the
directive: anything effectively mocked should be *mocked*. The scan
found three holes the `.mock` suffix was hiding:

1. **The story-author seed** (`value-loop.story-author.mock.v0`)
   announces every atom's birth, is not a PIPELINE stage, and so was
   invisible to the shame beat and the gap fold — 14 records, zero
   screams.
2. **The merge-node** landed 22 PRs under two self-asserted ids
   (`merge-node.claude.v0` ×19, `.v1` ×4) with zero `node_real`
   admissions, despite loop/CLAUDE.md's plain sentence that it does not
   move until bdo admits it real. The land pen checked only that `--by`
   was non-empty; the PR `author` field was fetched and never read.
3. **The trust ladder** is real code with zero rungs granted, and every
   spawn runs unbranded around it (named, left for its own line).

The build: `effective_mocks()` in loop/gaps.py — one pure fold, three
bases (pipeline-stage / mock-actor / unadmitted-actor), two new gap
kinds ranked under mock-stage; the shame beat screams the whole set
with the basis in brackets; `pr.py land` refuses a lander origin/main's
admissions never named (real side admits, later stage side supersedes);
reconcile stamps the seed author through the admitted map so the author
seat de-mocks by one ordinary admission. 14 new/updated tests; suite
513 OK. On the live records the fold's top three gaps are exactly the
scan's findings.

## needs-you (two taps, and a freeze to know about)

- **Issue #82 — the merge seat.** Once PR #81 is on main, the merge-node
  cannot land anything until you close this issue (yes admits
  `merge-node.claude.v1`; the v0 history stands). The freeze is the
  architecture working: the hand that touches main is the one seat whose
  identity you explicitly trust.
- **Issue #83 — the author seat.** Yes admits `story-author.session.v1`
  (the session is today's true author); the machine-author stays the
  corpus-to-system arc's later rung. No keeps the scream, which is also
  an answer.

## End-state

`report` — done-line 0049 built and green (PR #81 at the merge-node);
realness issues #82/#83 opened; this report and #81 land back-to-back
before the new gate freezes the seat; after that, landings wait on your
#82 tap by design.
