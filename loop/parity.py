"""The RepoPrompt boundedness parity matrix — a read-only fold (done-line 0115).

Wave 1 of epic.repoprompt-parity. RepoPrompt CE is mined as a catalogue of
agent-*boundedness* techniques, not a feature list: each row reads one of its
capabilities as "how does this keep an agent bounded?" and answers it in
ontum's idiom with exactly one verdict —

  have               ontum already does this; cites a resolvable repo file
  build              ontum lacks it; names an atom in epic.repoprompt-parity
  dont-double-build  it lives elsewhere; cites a real owning epic

The teeth (§10, the term-economy/gaps grip rule — a citation that points to
nothing is a ghost): `validate()` fails if any `have` path or
`dont-double-build` epic does not resolve on disk, or any `build` names an atom
absent from the epic. tests/test_parity.py proves the check is not vacuous by
showing a fabricated ghost row is caught.

    python -m loop.parity            the matrix + validation, read-only
    python -m loop.parity --json     the raw dataset (machine-readable)
"""

import argparse
import json
import sys
from pathlib import Path

# loop/parity.py -> loop/ -> repo root. Works the same in a worktree.
REPO = Path(__file__).resolve().parent.parent

EPIC_ID = "epic.repoprompt-parity"
SOURCE = "docs/sources/repoprompt-context-engineering.md"
VERDICTS = ("have", "build", "dont-double-build")

# The mine. Each row: the RepoPrompt capability, the boundedness technique it
# represents, the verdict, and what that verdict cites (a file for `have`, an
# atom id for `build`, an epic id for `dont-double-build`).
MATRIX = (
    {
        "capability": "Context Builder — explore, then assemble within a token budget",
        "bounds": "what an agent ingests: curated context, never the whole repo",
        "verdict": "build",
        "cites": "atom.context-fold.v0",
        "note": "promote summon.py's briefing into a named, budgeted fold",
    },
    {
        "capability": "CodeMaps — compressed structural representation",
        "bounds": "representation size: the whole structure seen within budget",
        "verdict": "build",
        "cites": "atom.context-fold.v0",
        "note": "the fold's declared compression / omission policy",
    },
    {
        "capability": "Reviewable handoff — inspect/refine context before it reaches a model",
        "bounds": "the seam: what crosses to the next mind is accountable",
        "verdict": "build",
        "cites": "atom.context-hash.v0",
        "note": "ontum form is pull-not-push — replayable after, not human-gated before",
    },
    {
        "capability": "Token-budget management",
        "bounds": "a hard ceiling on context size",
        "verdict": "build",
        "cites": "atom.context-budget-dial.v0",
        "note": "budget as an admitted setpoint, not a code constant",
    },
    {
        "capability": "Bundled MCP server — search/inspect the repo for outside agents",
        "bounds": "outside reach held read-only: agents read folds, cannot mutate",
        "verdict": "build",
        "cites": "atom.served-fold-surface.v0",
        "note": "one client of epic.causality-surface's API layer, not a second API",
    },
    {
        "capability": "App-managed worktrees — per-agent isolation",
        "bounds": "blast radius: each run isolated on its own branch/tree",
        "verdict": "have",
        "cites": ".claude/skills/branch-ritual/git.py",
        "note": "+ the Agent tool's isolation:worktree",
    },
    {
        "capability": ".worktreeinclude — selective file copying into a worktree",
        "bounds": "what travels into an isolated run: exactly its context, no more",
        "verdict": "build",
        "cites": "atom.worktree-include.v0",
        "note": "the include-set is a context fold scoped to a run",
    },
    {
        "capability": "Multi-root workspaces — unify related repos and docs",
        "bounds": "the working set across repositories",
        "verdict": "have",
        "cites": "loop/field.py",
        "note": "field.py --all folds ontum + odysseus + holonsearch",
    },
    {
        "capability": "Agent orchestration / lifecycle — run & coordinate CLI agents",
        "bounds": "runs held to mortal, summoned, dissolving sessions",
        "verdict": "dont-double-build",
        "cites": "epic.virtual-fleet",
        "note": "+ the merge-node (loop/merge.py) and the gate skill",
    },
    {
        "capability": "Provider plugins — pluggable agent/model backends",
        "bounds": "which mind may run: deny-by-default RBAC over callers",
        "verdict": "dont-double-build",
        "cites": "epic.inference-gateway",
        "note": "minds / route / policy already govern this",
    },
    {
        "capability": "Coordinated developer daemon — background scheduling",
        "bounds": "concurrency: how many runs are in flight at once",
        "verdict": "have",
        "cites": "loop/orchestrate.py",
        "note": "no runtime daemon (hard rule); the level-triggered tick + max_inflight setpoint is the bounded analog",
    },
)


def epic_atom_ids(epic_id=EPIC_ID, repo=REPO):
    """The atom ids a given epic's pieces name — the set a `build` may cite."""
    path = repo / ".ai-native" / "epics" / f"{epic_id}.json"
    if not path.exists():
        return None  # the epic itself is missing — a problem the caller reports
    data = json.loads(path.read_text(encoding="utf-8"))
    return {p.get("atom") for p in data.get("epic", {}).get("pieces", [])}


def _resolves(verdict, cites, repo, atoms):
    """Does this row's citation point at something real? -> None ok, else why."""
    if verdict == "have":
        return None if (repo / cites).exists() else f"file not found: {cites}"
    if verdict == "dont-double-build":
        target = repo / ".ai-native" / "epics" / f"{cites}.json"
        return None if target.exists() else f"epic not found: {cites}"
    if verdict == "build":
        if atoms is None:
            return f"owning epic {EPIC_ID} not found, cannot resolve atom {cites}"
        return None if cites in atoms else f"atom absent from {EPIC_ID}: {cites}"
    return f"unknown verdict: {verdict}"


def validate(matrix=MATRIX, repo=REPO):
    """The §10 teeth: every citation must resolve. Returns a list of problems
    (empty == the matrix is honest). A fabricated row cannot pass."""
    problems = []
    atoms = epic_atom_ids(repo=repo)
    for i, row in enumerate(matrix):
        where = f"row {i} ({row.get('capability', '?')[:40]}…)"
        verdict = row.get("verdict")
        if verdict not in VERDICTS:
            problems.append(f"{where}: verdict must be one of {VERDICTS}, got {verdict!r}")
            continue
        if not row.get("capability") or not row.get("bounds"):
            problems.append(f"{where}: capability and bounds are required")
        cites = row.get("cites")
        if not cites:
            problems.append(f"{where}: a {verdict} row must cite something")
            continue
        why = _resolves(verdict, cites, repo, atoms)
        if why:
            problems.append(f"{where}: {why}")
    return problems


def render(matrix=MATRIX):
    lines = [f"RepoPrompt → ontum boundedness parity matrix  (source: {SOURCE})", ""]
    counts = {v: 0 for v in VERDICTS}
    for v in VERDICTS:
        rows = [r for r in matrix if r.get("verdict") == v]
        if not rows:
            continue
        lines.append(f"[{v}] ({len(rows)})")
        for r in rows:
            counts[v] += 1
            lines.append(f"  • {r['capability']}")
            lines.append(f"      bounds: {r['bounds']}")
            lines.append(f"      → {r['cites']}" + (f"  ({r['note']})" if r.get("note") else ""))
        lines.append("")
    tally = ", ".join(f"{counts[v]} {v}" for v in VERDICTS)
    lines.append(f"{len(matrix)} capabilities mined: {tally}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="emit the raw dataset")
    args = ap.parse_args(argv)

    problems = validate()
    if args.json:
        print(json.dumps({"epic": EPIC_ID, "source": SOURCE,
                          "matrix": list(MATRIX), "problems": problems}, indent=2))
    else:
        print(render())
        print()
        if problems:
            print(f"result: needs-you — {len(problems)} ghost citation(s):")
            for p in problems:
                print(f"  - {p}")
        else:
            print(f"result: done — all {len(MATRIX)} citations resolve "
                  f"(no ghosts; the mine is honest)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
