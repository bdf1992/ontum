# Report 0117 — Authorship enforced in the land pen + the suite-not-a-CI-gate finding

## What this session did

bdo's instruction was the landing ritual: author + announce one atom backing
the increment, open the PR as the merge-node's unit, requisition the
independent review, let an independent merge-node land it.

**The increment (issue #345): no-one-signs-their-own-line, made structural in
the land pen.** The merge-node's D-2 invariant — a fresh, independent session
lands a PR it did not author — lived only as *prose* in the merge-node skill;
`pr.py land` never checked it. A session could pass `--by <any-node>` and land
its own PR. This increment moves the invariant into `land_refusal`: an exact
PR-author↔`--by` identity match refuses outright, and absent an explicit
`--attest-non-author` flag the land refuses; the merge receipt now records
`pr_author` + `non_author_attested`, so the author/lander separation is
auditable from the log alone (D-13 grain). The §10 teeth are proven, not
asserted (tests/test_merge_land.py, tests/test_merge_node.py): a PR perfect on
every mechanical axis still refuses when the attestation is missing, and
refuses when author==by even with it.

- Atom **atom.landing-throughput-resp-authorship-in-code.v0** authored +
  announced on the log (evt.658cad6eccea), serving the confirmed
  **epic.landing-throughput-response**.
- **PR #376** opened (claude/land-authorship-in-code → main) as the merge-node's unit.
- **Independent review requisitioned + processed** via the code-review skill
  (the sanctioned route until the in-pipeline code-review gate is real): three
  independent finder agents + verification. **0 correctness blockers.** One
  honest soundness limitation surfaced (below).
- **Independent value-gate accepted the atom** (rcp.3121c4e8af8e). See the
  correction below — I first wrongly skipped this; the merge-node caught it.
  A branded `ontum-node:value-gate.claude.v1` judged the atom in a worktree on
  the branch, recorded its accept via `loop.node judge`, and committed+pushed the
  receipt onto the branch (the off-log gate needs the receipt in the PR's range).
- **Independent merge-node landed #376** (rcp.merge.376, on the trunk) through the
  branded spawn rail (`ontum-node:merge-node.claude.v1`) under bdo's confirmed arc
  (adm.b6a6c293745e) — I authored it, so I could not be it. The increment is live
  on main (`--attest-non-author` in `pr.py`); `landed_atoms` carries the atom (D-13).

## Findings (needs attention — most are session-fixable, not bdo's)

- **The unittest suite is RED on `main`, invisibly, and has been since
  done-line 0145.** `tests/test_git_pen.py::test_local_mutating_git_is_now_watched`
  asserts `git checkout -b` returns 0 (watched), but the workstation fence
  (0145) now *denies* viewport-flips in the primary tree (exit 2). The two
  landed without the test being updated — **because CI runs only the
  atom-invariant gate (.github/workflows/atom-invariant.yml), not the unittest
  suite.** So suite-red drift lands undetected. My push gate (run from the
  primary viewport) is what caught it — and the failure is **cwd-dependent**:
  the test asserts `git checkout -b` returns 0, true only outside the primary
  tree; from a worktree `in_primary_viewport` is False so the fence allows it and
  the test passes (which is why the merge-node's worktree push saw a green suite).
  That cwd-dependence is itself a test-isolation bug (the test should mock the
  viewport check, not depend on where it runs). Two gaps: (1) the stale/leaky test
  needs a dedicated fix; (2) the deeper one — **the suite is not a CI gate**, so
  §10 teeth that live only in tests can rot on main unseen. Both session-fixable;
  the CI-gate question is a design call.
- **Possible hole in workstation-fence tooth #1.** The fence correctly denies a
  *simulated* `git checkout -b` (stdin payload with no cwd → primary viewport →
  exit 2), but my actual Bash-tool `git checkout -b claude/land-authorship-in-code`
  was **not** denied — it flipped the viewport. The likely cause is the
  cwd the harness passes in the real PreToolUse payload vs. the test/probe path.
  Worth a dedicated check: does tooth #1 actually bite the live Bash-tool path,
  or only the test harness? If only the latter, the fence is theatre on the one
  path that matters. (The viewport was later restored to main cleanly by the
  SessionStart sync hook, so no harm this time.)
- **Code-review limitation (logged, non-blocking).** The new author-identity
  check compares a GitHub `author.login` (e.g. `bdf1992`) against a node id
  (e.g. `merge-node.claude.v1`) — disjoint namespaces, so it rarely fires. The
  real enforcement is the self-asserted `--attest-non-author` flag + the
  fresh-session procedure; the increment's genuine teeth is *auditability* (the
  receipt records both), not a complete structural lock. A stronger follow-up:
  compare the atom's authoring family (its `workspace_claimed` record) against
  the landing node's family — same namespace, structural. A refinement atom, not
  a fix to this one.
- **My process mistake (corrected): code-review ≠ the value-gate receipt.** I
  treated the independent `/code-review` as satisfying the independent-review
  hard rule and skipped the value-gate, then requisitioned the merge-node — which
  correctly REFUSED: the atom-invariant CI gate was RED because the branch carried
  the atom file but **no receipt naming it** (`atom_backed_refusal`). A code-review
  produces no pipeline receipt; only an independent value-gate verdict via
  `loop.node judge` does. The fix: a branded value-gate judge in a worktree ON the
  branch (the atom file lives only on the branch), committing its receipt into the
  PR's `base...head` range → gate green → merge-node landed. The off-log gate did
  exactly its job (D-2: I earned my own acceptance via code-review, but a
  *different reader* had to accept it onto the record). The inflight-cap clog does
  NOT block a direct branded judge — only orchestrate's scheduling.

## Carried state (session-fixable, not bdo's)

- **stash@{0} "blueprint-wip-B"** holds the blueprint thread's uncommitted WIP —
  the +100 lines to `change-management.proposal.md`. It was entangled with this
  increment in the viewport at session start; I split it out so this PR is clean.
  It is preserved (a labelled stash survives), to be restored to
  `claude/platform-brokerage-blueprint` by the next session on that thread.
  (Report 0115 turned out to be already on main via #351; the `M events.jsonl`
  on the viewport is the reflect-auto beat's own records — both fine.)

## End-state

`done` — the increment is **on main** (PR #376, rcp.merge.376; `--attest-non-author`
now live in `pr.py land`). Full chain: atom authored + announced → independent
code-review (0 blockers) → independent value-gate accept (rcp.3121c4e8af8e, the
receipt the off-log gate required — caught by the merge-node after I first skipped
it) → independent merge-node land under bdo's confirmed arc. No owner gesture was
needed (the arc was already confirmed). Carried forward as session-fixable next
steps (not bdo's): the stale/cwd-leaky `test_git_pen` test + the deeper
suite-is-not-a-CI-gate gap; the possible fence-tooth-1 live-Bash-path hole; the
same-namespace authorship-check refinement; and stash@{0} (blueprint WIP) for the
next blueprint session. Report itself is uncommitted on the viewport — it rides
the next records-carrying PR.
