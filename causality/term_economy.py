#!/usr/bin/env python3
"""The term-economy fold (done-line 0060) — Causality's first governed slice.

A pure, read-only fold in the grain of `loop/gaps.py` and `loop/census.py`:
stdlib only, no network, no subprocess, no writes except the one explicit
`project --write` that regenerates the committed projection. Evidence is a
`file:line` location or a log-record substring — never prose. The repo is
truth; this fold only *resolves* a declared seed's citations against
committed bytes and *classifies* what it finds.

The discipline (causality/CLAUDE.md): Causality is a projection, never a
second source of truth. A term is not minted by appearing here. A term is
classified by which evidence strata actually resolve on disk:

    minted-runtime   code/log/fold produces or enforces it
    minted-doctrine  defined in the doctrine and used consistently
    minted-workflow  used by skills / reports / node prompts
    projected        visible only on the Causality surface, derived
    proposed         useful but not yet grounded
    poetic           metaphor only; carries no authority
    overloaded       >=2 incompatible meanings that must be split
    orphaned         a lone definition with no live economy
    ghost            claims a backing that does NOT resolve on disk

The teeth (§10, proven by tests/test_term_economy.py): a term with no
resolvable evidence can never be `minted`; a citation that points to
nothing is `ghost`; two incompatible senses surface as `overloaded`. A
fabricated/constant classifier fails the test.
"""

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_SEED = ROOT / "causality" / "examples" / "ontum-terms.seed.json"
DEFAULT_PROJECTION = ROOT / "causality" / "examples" / "ontum-terms.projection.json"

# evidence strata that make a claim about the running system (vs. pure prose).
# An unresolved CLAIMED-evidence is the ghost signal.
CLAIMED_STRATA = {"doctrine", "code", "log", "workflow", "causality"}


# ---------------------------------------------------------------------------
# resolution: does this citation point at real committed bytes?
# ---------------------------------------------------------------------------

def _read_text(root, rel):
    """The committed bytes of a repo-relative file, or None if absent.
    A missing file is an absence, not a crash — absence is information."""
    p = (root / rel)
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except (OSError, ValueError):
        return None


def resolve_evidence(root, ev):
    """Resolve one evidence citation against the tree. Returns a copy with
    `resolved` (bool) and `file_exists` (bool) added. Resolution is purely
    'do these bytes contain the claimed substring' — line numbers drift, a
    substring is stable identity, and a substring that is absent is exactly
    the ghost signal we want to catch."""
    out = dict(ev)
    rel = ev.get("file")
    needle = ev.get("contains")
    text = _read_text(root, rel) if rel else None
    out["file_exists"] = text is not None
    out["resolved"] = bool(text is not None and needle and needle in text)
    return out


def site_id(rel):
    """A deterministic SiteNode id for a repo-relative address."""
    slug = "".join(c.lower() if c.isalnum() else "-" for c in str(rel)).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return f"site:{slug or 'unknown'}"


def site_kind(rel, stratum=None):
    """Classify an evidence address into the contract's SiteNode kinds.

    The path is the stronger signal; stratum is a fallback for unusual seeds.
    This is descriptive only: the file bytes still decide existence/resolution.
    """
    rel = str(rel or "")
    if rel.startswith(".ai-native/log/"):
        return "log"
    if rel.startswith("docs/phase-2/") or rel.startswith("docs/sources/"):
        return "vault"
    if rel.startswith("causality/") or stratum == "causality":
        return "surface"
    if rel.startswith(".claude/") or rel.startswith(".ai-native/"):
        return "workflow"
    if rel.endswith((".py", ".js", ".html", ".json")):
        return "code"
    return {
        "code": "code",
        "log": "log",
        "workflow": "workflow",
        "causality": "surface",
        "doctrine": "doctrine",
    }.get(stratum, "doctrine")


# ---------------------------------------------------------------------------
# classification: the economy class, derived from resolved evidence
# ---------------------------------------------------------------------------

def classify(term, resolved_evs):
    """The one classifier. Deterministic, evidence-driven, precedence-ordered.
    `resolved_evs` is the term's evidence after resolve_evidence().

    Precedence is load-bearing and the test pins it:
      poetic-declared  -> poetic
      claimed but none resolves -> ghost   (check b: a citation to nothing)
      >=2 incompatible senses, resolving -> overloaded   (check c)
      code (+log) -> minted-runtime
      doctrine + a usage -> minted-doctrine
      workflow only -> minted-workflow
      causality only -> projected
      poetic/prose only -> poetic
      lone doctrine, no usage -> orphaned
      else -> proposed   (check a: no evidence is never minted)
    """
    if term.get("declared") == "poetic":
        return "poetic"

    claimed = [e for e in resolved_evs if e.get("stratum") in CLAIMED_STRATA]
    resolved = [e for e in resolved_evs if e.get("resolved")]
    strata = {e["stratum"] for e in resolved}
    senses = sorted({e.get("sense") for e in resolved if e.get("sense")})
    incompatible = len(senses) >= 2 and any(e.get("incompatible") for e in resolved)

    # ghost: it claims a backing, and NONE of those claims resolve on disk.
    if claimed and not any(e.get("resolved") for e in claimed):
        return "ghost"
    # overloaded: two meanings that locally fit but refuse to fit together.
    if incompatible:
        return "overloaded"
    # minted by the running system.
    if "code" in strata:
        return "minted-runtime"
    # minted by the doctrine and actually used.
    if "doctrine" in strata and (strata & {"workflow", "log"}):
        return "minted-doctrine"
    # minted by the workflow layer alone.
    if "workflow" in strata and not (strata & {"doctrine", "code", "log"}):
        return "minted-workflow"
    # lives only on the Causality surface, derived from evidence.
    if strata == {"causality"}:
        return "projected"
    # only prose/poetic bytes carry it.
    if strata and strata <= {"poetic"}:
        return "poetic"
    # a lone definition with no economy around it.
    if strata == {"doctrine"}:
        return "orphaned"
    # nothing solid resolved — useful maybe, grounded no.
    return "proposed"


# ---------------------------------------------------------------------------
# the projection: TermNodes + EvidenceEdges (a deterministic fold)
# ---------------------------------------------------------------------------

def build_projection(root, seed):
    """Fold a seed into a ProjectionView: TermNodes, SiteNodes, EvidenceEdges,
    plus a class summary and gap findings. Deterministic: terms sorted by
    name, evidence kept in declared order, no timestamps. Re-running over the
    same committed bytes yields byte-identical output (the reproducibility
    property the test pins)."""
    terms_out, sites, edges_out, gaps = [], {}, [], []
    terms = sorted(seed.get("terms", []), key=lambda t: t["term"])

    for t in terms:
        name = t["term"]
        resolved_evs = [resolve_evidence(root, e) for e in t.get("evidence", [])]
        klass = classify(t, resolved_evs)
        senses = sorted({e.get("sense") for e in resolved_evs if e.get("sense")})
        resolved_count = sum(1 for e in resolved_evs if e.get("resolved"))

        terms_out.append({
            "id": f"term:{name}",
            "term": name,
            "class": klass,
            "local_meaning": t.get("local_meaning", ""),
            "global_meaning": t.get("global_meaning", ""),
            "must_not_mean": t.get("must_not_mean", []),
            "senses": senses,
            "evidence_count": len(resolved_evs),
            "resolved_count": resolved_count,
            "record_kind": "projected",
        })

        for i, e in enumerate(resolved_evs):
            ref = {k: e[k] for k in ("file", "contains", "line") if k in e}
            rel = e.get("file", "?")
            sid = site_id(rel)
            if sid not in sites:
                sites[sid] = {
                    "id": sid,
                    "address": rel,
                    "kind": site_kind(rel, e.get("stratum")),
                    "exists": e.get("file_exists", False),
                    "_terms": set(),
                    "record_kind": "projected",
                }
            sites[sid]["exists"] = sites[sid]["exists"] or e.get("file_exists", False)
            sites[sid]["_terms"].add(f"term:{name}")
            edges_out.append({
                "id": f"edge:{name}:{i}",
                "from": f"term:{name}",
                "to": sid,
                "stratum": e.get("stratum"),
                "sense": e.get("sense"),
                "claim": e.get("claim", ""),
                "resolved": e.get("resolved", False),
                "file_exists": e.get("file_exists", False),
                "ref": ref,
                "record_kind": "projected",
            })
            # a claimed citation that does not resolve is a finding either way
            if e.get("stratum") in CLAIMED_STRATA and not e.get("resolved"):
                gaps.append({
                    "kind": "unresolved-evidence",
                    "term": name,
                    "why": (f"{name} cites {e.get('file')!r} containing "
                            f"{e.get('contains')!r}, which does not resolve on disk"),
                    "move": "fix the citation, or drop the claim — a stale "
                            "citation reads as a ghost backing",
                })

        # class-level findings (the audit's teeth, surfaced as gaps)
        if klass == "ghost":
            gaps.append({"kind": "ghost-term", "term": name,
                         "why": f"{name} claims a backing that resolves nowhere",
                         "move": "ground it or retire it; it is not minted"})
        elif klass == "overloaded":
            gaps.append({"kind": "overloaded-term", "term": name,
                         "why": f"{name} carries incompatible senses {senses} "
                                "that each resolve but cannot both be 'the' meaning",
                         "move": "split the term, or name one sense the owner"})
        elif klass == "orphaned":
            gaps.append({"kind": "orphaned-term", "term": name,
                         "why": f"{name} is defined once with no live economy",
                         "move": "use it or sunset it"})

        # drift between a self-declared class and the evidence-derived one
        claimed_class = t.get("claimed_class")
        if claimed_class and claimed_class != klass:
            gaps.append({"kind": "class-drift", "term": name,
                         "why": f"{name} is declared {claimed_class!r} but the "
                                f"evidence resolves to {klass!r}",
                         "move": "the evidence wins; correct the declaration"})

    summary = {}
    for tn in terms_out:
        summary[tn["class"]] = summary.get(tn["class"], 0) + 1
    sites_out = []
    for s in sorted(sites.values(), key=lambda x: x["id"]):
        out = dict(s)
        out["inbound_term_count"] = len(out.pop("_terms"))
        sites_out.append(out)

    return {
        "view": "term-economy",
        "generator": "causality.term_economy",
        "source": "the repo is truth; this is a fold, not a record",
        "term_count": len(terms_out),
        "site_count": len(sites_out),
        "class_summary": summary,
        "terms": terms_out,
        "sites": sites_out,
        "evidence_edges": edges_out,
        "gaps": gaps,
    }


def dumps(projection):
    """The one serializer — sorted keys, two-space indent, LF, trailing
    newline. Byte-determinism lives here so the committed projection and a
    fresh run agree exactly."""
    return json.dumps(projection, indent=2, sort_keys=True,
                      ensure_ascii=False) + "\n"


# ---------------------------------------------------------------------------
# the audit view: minted-vs-evidence, gap findings, census
# ---------------------------------------------------------------------------

def audit_lines(projection):
    """The term-fold audit as text: census + every gap, in fixed order. What
    the deterministic reader collected vs. what the terms claim to be."""
    lines = []
    lines.append("term-economy audit — what the evidence resolves to")
    lines.append(f"  terms folded: {projection['term_count']}")
    for klass in sorted(projection["class_summary"]):
        lines.append(f"    {klass:<16} {projection['class_summary'][klass]}")
    gaps = projection["gaps"]
    if not gaps:
        lines.append("  no gaps — every term's class matches its evidence")
        return lines
    lines.append(f"  gaps: {len(gaps)}")
    for g in gaps:
        lines.append(f"    [{g['kind']}] {g['term']}: {g['why']}")
        lines.append(f"        move: {g['move']}")
    return lines


# ---------------------------------------------------------------------------
# the mermaid render: text-first, so the structure is inspectable
# ---------------------------------------------------------------------------

_CLASS_SHAPE = {
    "minted-runtime": ('["', '"]'),     # box
    "minted-doctrine": ('("', '")'),    # rounded
    "minted-workflow": ('("', '")'),
    "projected": ('("', '")'),
    "proposed": ('>"', '"]'),           # flag
    "poetic": ('{{"', '"}}'),           # hexagon
    "overloaded": ('{"', '"}'),         # rhombus — the thing to notice
    "orphaned": ('[/"', '"/]'),
    "ghost": ('{"', '"}'),
}


def mermaid(projection):
    """A flowchart of terms -> sites, shaped by class. Deterministic text,
    in the repo's text-first Mermaid grain (envoy, the-field). Overloaded and
    ghost terms get a rhombus so a reader spots the trouble without reading
    the log."""
    out = ["flowchart LR"]
    for tn in projection["terms"]:
        op, cl = _CLASS_SHAPE.get(tn["class"], ('["', '"]'))
        label = f"{tn['term']} :: {tn['class']}"
        out.append(f"  {_nid(tn['id'])}{op}{label}{cl}")
    site_labels = {}
    for site in projection.get("sites", []):
        nid = _nid(site["id"])
        label = f"{site['address']} :: {site['kind']}"
        if not site.get("exists", False):
            label += " (MISSING)"
        site_labels[site["id"]] = nid
        out.append(f'  {nid}["{label}"]')
    for e in projection["evidence_edges"]:
        arrow = "-->" if e["resolved"] else "-.->"
        tag = e["stratum"] or "?"
        if e.get("sense"):
            tag += f"/{e['sense']}"
        site_node = site_labels.get(e["to"], _nid(e["to"]))
        out.append(f"  {_nid(e['from'])} {arrow}|{tag}| {site_node}")
    return "\n".join(out)


def _nid(s):
    """A mermaid-safe node id."""
    return "".join(c if c.isalnum() else "_" for c in s)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def load_seed(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="causality.term_economy",
        description="the term-economy fold — read-only, deterministic")
    ap.add_argument("mode", choices=["project", "audit", "mermaid"],
                    help="project: the projection | audit: gaps + census | "
                         "mermaid: a text-first graph render")
    ap.add_argument("--seed", default=str(DEFAULT_SEED),
                    help="the seed to fold (default: the committed example)")
    ap.add_argument("--write", action="store_true",
                    help="project only: regenerate the committed projection file")
    args = ap.parse_args(argv)

    seed = load_seed(args.seed)
    projection = build_projection(ROOT, seed)

    if args.mode == "project":
        text = dumps(projection)
        if args.write:
            DEFAULT_PROJECTION.parent.mkdir(parents=True, exist_ok=True)
            DEFAULT_PROJECTION.write_text(text, encoding="utf-8", newline="\n")
            print(f"result: report — wrote {DEFAULT_PROJECTION.relative_to(ROOT).as_posix()} "
                  f"({projection['term_count']} terms, {projection['class_summary']})")
        else:
            sys.stdout.write(text)
        return 0
    if args.mode == "audit":
        for line in audit_lines(projection):
            print(line)
        return 0
    if args.mode == "mermaid":
        print(mermaid(projection))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
