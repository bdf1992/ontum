#!/usr/bin/env python3
"""The digest's voice layer — bounded inference narration, grounded by teeth.

bdo, 2026-06-21 (issue #410): the digest should read like great patch notes,
and the pure fold can lay out the *structure* but cannot write the editorial
marquee ("the inference gateway held under load") — that is voice, and voice
needs inference. This module is the **bounded** way to add it without letting
the surface confabulate: the fold stays truth (loop/digest.py, pure), and a
*separate* inference pass narrates the already-computed dataset — but only what
the dataset can ground.

Two pure halves live here (no network — the loop/ law; the reach that actually
calls the gateway lives in the pen):

  build_prompt(dataset) — turns the digest dataset into a bounded prompt: here
      are the facts (atoms, PRs, arcs, horizons, the gesture, the frictions);
      write up to N one-line patch-notes headlines; each MUST cite at least one
      of these atoms / PRs / epics; invent nothing.

  ground(dataset, headlines) — the §10 teeth and the whole reason this is safe.
      A headline is KEPT only if every atom-id / PR# / epic-id it names is in
      the dataset's vocabulary AND it names at least one (a marquee with no
      citation is exactly the prose-facade: confident specificity with nothing
      under it). Any headline naming a token the dataset does not contain is a
      GHOST and is dropped with its reason. Inference proposes; the dataset
      disposes — the same propose/dispose shape as the rest of the loop.

This is the counterforce to a documented failure mode (the prose facade:
fluent prose outrunning the facts). The guard does not trust the model's
fluency; it checks every claim token against the record. A clean run keeps
every headline — and if it always did, the guard would not be doing its job
(§10): the test fabricates a ghost headline and proves it is caught.

Stdlib only, pure, read-only. result: report.
"""

from __future__ import annotations

import re

# Up to this many headlines — a marquee, not a wall. The patch-notes TL;DR is a
# glance; more than a few and it stops being a headline.
MAX_HEADLINES = 3

# The shapes a groundable claim token takes in the dataset's vocabulary.
_ATOM_RE = re.compile(r"atom\.[A-Za-z0-9][A-Za-z0-9.\-]*")
_EPIC_RE = re.compile(r"epic\.[A-Za-z0-9][A-Za-z0-9.\-]*")
_PR_RE = re.compile(r"#(\d+)")


def vocabulary(dataset):
    """Every concrete token a headline is allowed to name, harvested from the
    dataset alone. Three kinds, normalized to one set: atom ids, epic ids, and
    PR numbers (as `#N`). A token outside this set is a ghost — it names work
    the span does not contain, so the headline claiming it is unfounded."""
    atoms, epics, prs = set(), set(), set()
    for ev in dataset.get("landed_in_span", []):
        atoms.update(ev.get("atoms") or [])
        if ev.get("epic"):
            epics.add(ev["epic"])
        if ev.get("pr") is not None:
            prs.add(f"#{ev['pr']}")
    for arc in dataset.get("arcs", []):
        if arc.get("epic"):
            epics.add(arc["epic"])
        for p in arc.get("pieces", []):
            if p.get("atom"):
                atoms.add(p["atom"])
    for p in dataset.get("loose", []):
        if p.get("atom"):
            atoms.add(p["atom"])
    for x in dataset.get("divergences", []):
        if x.get("atom"):
            atoms.add(x["atom"])
        if x.get("epic"):
            epics.add(x["epic"])
    return atoms | epics | prs


def claim_tokens(headline):
    """The concrete tokens a headline names — the claims it stakes that must be
    grounded. Atom ids, epic ids, and PR numbers (normalized `#N`)."""
    found = set(_ATOM_RE.findall(headline)) | set(_EPIC_RE.findall(headline))
    found |= {f"#{n}" for n in _PR_RE.findall(headline)}
    return found


def ground(dataset, headlines):
    """Split proposed headlines into (kept, rejected) against the dataset's
    vocabulary — the teeth. A headline is kept only if it names at least one
    concrete token and every token it names is in the vocabulary. Each rejected
    headline carries the reason (uncited, or the ghost tokens it invented), so
    the drop is named, never silent (loop/'s law)."""
    vocab = vocabulary(dataset)
    kept, rejected = [], []
    for h in headlines:
        tokens = claim_tokens(h)
        if not tokens:
            rejected.append({"headline": h, "why": "uncited — names no atom, "
                             "PR, or epic from the span (a marquee with nothing "
                             "under it is the prose facade)"})
            continue
        ghosts = sorted(t for t in tokens if t not in vocab)
        if ghosts:
            rejected.append({"headline": h, "why": "ghost token(s) not in the "
                             f"span: {', '.join(ghosts)}"})
            continue
        kept.append(h)
    return kept, rejected


def parse_headlines(text):
    """Pull headline lines from a model completion: each non-empty line, with
    leading bullet/number markers and wrapping quotes stripped. We do not trust
    the model's formatting — a small model will wrap a line in quotes and echo
    the requested `- ` bullet *inside* them (`- '- 'epic.x lands''`), so we peel
    markers and surrounding quotes repeatedly until the line stops changing.
    The grounding guard is what makes a headline real; this only un-junks it."""
    out = []
    for raw in (text or "").splitlines():
        line, prev = raw.strip(), None
        if not line:
            continue
        while line != prev:
            prev = line
            line = re.sub(r"^[-*•]\s+", "", line)
            line = re.sub(r"^\d+[.)]\s+", "", line)
            line = line.strip().strip("'\"").strip()
        if line:
            out.append(line)
    return out


def _facts(dataset):
    """The dataset distilled to the lines inference is allowed to draw on —
    nothing it could not see is in the prompt, so it cannot honestly know it."""
    lines = []
    g = [a for a in dataset.get("arcs", [])
         if not a.get("confirmed") and any(p.get("present") for p in a["pieces"])]
    if g:
        lines.append("AWAITING THE OWNER'S STAMP: "
                     + ", ".join(a["epic"] for a in g))
    lines.append("RECENT LANDINGS (newest first):")
    for ev in dataset.get("landed_in_span", [])[:MAX_HEADLINES * 4]:
        atoms = ", ".join(ev.get("atoms") or []) or "(no atom named)"
        pr = f"#{ev['pr']} " if ev.get("pr") else ""
        lines.append(f"  - {pr}{atoms} [{ev.get('epic') or 'no arc'}]")
    lines.append("ARCS (landed/total — horizon):")
    for a in dataset.get("arcs", []):
        total = a.get("total", len(a.get("pieces", [])))
        h = (a.get("horizon") or "").strip().split(". ")[0][:120]
        lines.append(f"  - {a['epic']}: {a.get('landed')}/{total} — {h}")
    if dataset.get("divergences"):
        lines.append("FRICTIONS: " + ", ".join(
            f"{x.get('atom') or x.get('kind')}" for x in dataset["divergences"]))
    return "\n".join(lines)


def build_prompt(dataset, max_headlines=MAX_HEADLINES):
    """The bounded prompt: the facts, and the one job — write patch-notes
    headlines grounded only in them. The grounding rule is stated to the model
    (cite a real atom/PR/epic, invent nothing) AND enforced after by `ground`;
    the prompt is the request, the guard is the contract — belt and braces, the
    way the off-log gate is both asked-for and re-verified."""
    return (
        "You are writing the headline section of a software patch-notes digest, "
        "in the confident, scannable voice of great game patch notes (Path of "
        "Exile, Warframe, League of Legends, Destiny).\n\n"
        f"Write at most {max_headlines} one-line headlines summarising what "
        "matters most in this span. RULES:\n"
        "- Use ONLY the facts below. Invent nothing — no claim that is not in "
        "the facts.\n"
        "- Each headline MUST cite at least one concrete atom id, PR number "
        "(#N), or epic id exactly as written below.\n"
        "- One line each, prefixed with '- '. No preamble, no closing.\n\n"
        "FACTS:\n" + _facts(dataset) + "\n"
    )
