#!/usr/bin/env python3
"""Literal terms accounting over the accrued .md + .json corpus.

A pure, read-only, stdlib fold. The empirical sibling of `term_economy.py`:
where term_economy resolves a hand-authored seed of canonical terms, this
*accounts the whole corpus literally* — every term the repo has accrued,
classified by the FORMATTING SIGNAL that declared it (the latent graph of
json + md formatting bdo named, 2026-06-21).

The LITERAL layer (deterministic string extraction) only. Embeddings — the
semantic clustering over these literals — are the later admitted layer
(causality/CLAUDE.md: "embeddings are a later admitted part"). This fold
mints nothing and decides nothing: it counts what is literally on disk
(causality's one hard rule — a projection, never a second source of truth).

  python causality/corpus_terms.py            # the accounting, to stdout
  python causality/corpus_terms.py --json      # the raw dataset (machine-readable)
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Directories whose bytes are cache, vendored, or not prose — out of the accounting.
SKIP_PARTS = {".git", "node_modules", ".venv", "__pycache__", "queues", "offsets"}
SKIP_SUFFIX_FILES = {"package-lock.json"}

# The id grammar this repo has accrued — the load-bearing literal tokens.
ID_PATTERNS = {
    "atom-id": re.compile(r"\batom\.[a-z0-9][a-z0-9\-]*(?:\.v\d+)?\b"),
    "epic-id": re.compile(r"\bepic\.[a-z0-9][a-z0-9\-]*\b"),
    "receipt-id": re.compile(r"\brcp\.[a-z0-9.]+\b"),
    "admission-id": re.compile(r"\badm\.[a-z0-9]+\b"),
    "node-id": re.compile(r"\b[a-z][a-z0-9\-]*\.(?:claude|bdo|det|codex)\.v\d+\b"),
    "decision": re.compile(r"\b[DI]-\d+\b"),
    "section": re.compile(r"§\s?\d+(?:\.\d+)*"),
    "done-line": re.compile(r"\bdone-line\s+\d{3,4}\b"),
}

# md formatting-signal extractors
RE_HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*#*$", re.M)
RE_BOLD = re.compile(r"\*\*(.+?)\*\*", re.S)
RE_CODE = re.compile(r"`([^`\n]+?)`")
RE_FM_KEY = re.compile(r"^([A-Za-z_][A-Za-z0-9_\-]*):", re.M)
ARTICLES = {"the", "a", "an"}


def stratum_of(path: Path) -> str:
    rel = path.relative_to(REPO).as_posix()
    if rel == "ai-native-loop-substrate.md":
        return "doctrine"
    if rel.endswith("CLAUDE.md") or rel in ("AGENTS.md", "CONTRIBUTING.md", "README.md"):
        return "governance"
    if rel.startswith(".ai-native/proposals/"):
        return "proposals"
    if rel.startswith(".ai-native/epics/"):
        return "epics"
    if rel.startswith(".ai-native/atoms/"):
        return "atoms"
    if rel.startswith(".ai-native/reports/"):
        return "reports"
    if rel.startswith(".ai-native/done/"):
        return "done"
    if rel.startswith(".ai-native/nodes/"):
        return "nodes"
    if rel.startswith(".ai-native/"):
        return "ai-native-other"
    if rel.startswith("docs/"):
        return "docs"
    if rel.startswith("causality/"):
        return "causality"
    if rel.startswith("language/"):
        return "language"
    if rel.startswith("glyphs/"):
        return "glyphs"
    if rel.startswith(".claude/"):
        return "harness"
    top = rel.split("/", 1)[0]
    return top if "/" in rel else "root"


def discover() -> list[Path]:
    out = []
    for p in REPO.rglob("*"):
        if p.suffix not in (".md", ".json"):
            continue
        if p.name in SKIP_SUFFIX_FILES:
            continue
        if any(part in SKIP_PARTS for part in p.relative_to(REPO).parts):
            continue
        out.append(p)
    return sorted(out)


def norm(term: str):
    """Normalise a candidate term to a counting key + a clean surface form.

    Returns (key, surface) or None if it isn't term-like."""
    s = term.strip().strip(".,;:!?—-‘’“”\"'()[]")
    s = re.sub(r"\s+", " ", s)
    if not s:
        return None
    words = s.split(" ")
    # strip a leading article ("the merge-node" -> "merge-node")
    if len(words) > 1 and words[0].lower() in ARTICLES:
        words = words[1:]
        s = " ".join(words)
    # term-like = short noun phrase, not an emphasised sentence
    if len(words) > 4:
        return None
    if len(s) < 2 or len(s) > 48:
        return None
    # must carry a letter
    if not re.search(r"[A-Za-z]", s):
        return None
    return (s.lower(), s)


def json_strings(obj):
    """Yield ('key', k) and ('val', v) over a parsed JSON structure."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield ("key", str(k))
            yield from json_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from json_strings(v)
    elif isinstance(obj, str):
        yield ("val", obj)


def account():
    files = discover()
    # term key -> data
    terms = defaultdict(lambda: {
        "count": 0,
        "files": set(),
        "signals": Counter(),
        "strata": Counter(),
        "surfaces": Counter(),
    })
    id_tokens = defaultdict(lambda: {"count": 0, "files": set(), "kind": ""})
    strata_files = Counter()
    cooc_files = defaultdict(set)  # term key -> set(file) for top-N co-occurrence

    def add(term_field, signal, stratum, fpath):
        r = norm(term_field)
        if not r:
            return
        key, surface = r
        d = terms[key]
        d["count"] += 1
        d["files"].add(fpath)
        d["signals"][signal] += 1
        d["strata"][stratum] += 1
        d["surfaces"][surface] += 1
        cooc_files[key].add(fpath)

    for p in files:
        rel = p.relative_to(REPO).as_posix()
        stratum = stratum_of(p)
        strata_files[stratum] += 1
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        # id grammar — over raw text of any file
        for kind, pat in ID_PATTERNS.items():
            for m in pat.findall(text):
                tok = m if isinstance(m, str) else m[0]
                tok = tok.strip()
                id_tokens[tok]["count"] += 1
                id_tokens[tok]["files"].add(rel)
                id_tokens[tok]["kind"] = kind

        if p.suffix == ".md":
            # frontmatter block (between leading --- fences)
            fm = ""
            if text.startswith("---"):
                end = text.find("\n---", 3)
                if end != -1:
                    fm = text[3:end]
            for k in RE_FM_KEY.findall(fm):
                add(k, "frontmatter-key", stratum, rel)
            for h in RE_HEADING.findall(text):
                add(h, "heading", stratum, rel)
            for b in RE_BOLD.findall(text):
                add(b, "bold-coinage", stratum, rel)
            for c in RE_CODE.findall(text):
                # inline code is usually an artifact id/path/command; keep short ones
                if len(c.split()) <= 3:
                    add(c, "inline-code", stratum, rel)
        else:  # .json
            try:
                obj = json.loads(text)
            except Exception:
                continue
            for kind, val in json_strings(obj):
                if kind == "key":
                    add(val, "json-key", stratum, rel)
                else:
                    if len(val.split()) <= 4:
                        add(val, "json-value", stratum, rel)

    return files, terms, id_tokens, strata_files, cooc_files


def fmt_signals(c: Counter) -> str:
    return ", ".join(f"{k}:{v}" for k, v in c.most_common())


def report(as_json: bool):
    files, terms, id_tokens, strata_files, cooc_files = account()

    # derived views
    by_count = sorted(terms.items(), key=lambda kv: (-kv[1]["count"], kv[0]))
    total_mentions = sum(d["count"] for d in terms.values())

    def signal_dom(d, sig):
        return d["signals"].get(sig, 0) / max(1, d["count"])

    coinages = sorted(
        ((k, d) for k, d in terms.items() if signal_dom(d, "bold-coinage") >= 0.6 and d["count"] >= 4),
        key=lambda kv: -kv[1]["count"],
    )
    artifacts = sorted(
        ((k, d) for k, d in terms.items() if signal_dom(d, "inline-code") >= 0.6 and d["count"] >= 4),
        key=lambda kv: -kv[1]["count"],
    )
    # load-bearing: declared by >=3 distinct signal kinds AND living in >=4 strata
    load_bearing = sorted(
        ((k, d) for k, d in terms.items() if len(d["signals"]) >= 3 and len(d["strata"]) >= 4),
        key=lambda kv: (-len(kv[1]["strata"]), -kv[1]["count"]),
    )

    # latent-graph: co-occurrence among the top-80 terms (shared-file edges)
    top_keys = [k for k, _ in by_count[:80]]
    edges = Counter()
    for i, a in enumerate(top_keys):
        fa = cooc_files[a]
        for b in top_keys[i + 1:]:
            shared = len(fa & cooc_files[b])
            if shared >= 6:
                edges[(a, b)] = shared
    top_edges = edges.most_common(20)

    if as_json:
        out = {
            "corpus": {"files": len(files), "by_stratum": dict(strata_files)},
            "terms_distinct": len(terms),
            "term_mentions": total_mentions,
            "id_tokens_distinct": len(id_tokens),
            "top_terms": [
                {"term": d["surfaces"].most_common(1)[0][0], "count": d["count"],
                 "files": len(d["files"]), "signals": dict(d["signals"]),
                 "strata": dict(d["strata"])}
                for _, d in by_count[:60]
            ],
            "id_grammar": Counter(t["kind"] for t in id_tokens.values()),
            "load_bearing": [
                {"term": d["surfaces"].most_common(1)[0][0], "count": d["count"],
                 "signals": list(d["signals"]), "strata": list(d["strata"])}
                for _, d in load_bearing[:40]
            ],
            "latent_edges": [{"a": a, "b": b, "shared_files": n} for (a, b), n in top_edges],
        }
        print(json.dumps(out, indent=2, default=lambda o: dict(o) if isinstance(o, Counter) else list(o)))
        return

    P = print
    P("# Literal terms accounting — the accrued .md + .json corpus")
    P("")
    P("_pure read-only fold; counts what is literally on disk by its formatting signal; mints nothing._")
    P("")
    P(f"Corpus: **{len(files)} files** · **{len(terms)} distinct terms** · "
      f"**{total_mentions} term-mentions** · **{len(id_tokens)} distinct id-tokens**")
    P("")
    P("## Corpus by stratum (where the terms live)")
    for s, n in strata_files.most_common():
        P(f"  {s:<20} {n:>4} files")
    P("")
    P("## The id grammar we've accrued (literal tokens)")
    kinds = Counter(t["kind"] for t in id_tokens.values())
    mentions_by_kind = Counter()
    for t in id_tokens.values():
        mentions_by_kind[t["kind"]] += t["count"]
    for kind, n in kinds.most_common():
        P(f"  {kind:<14} {n:>4} distinct   {mentions_by_kind[kind]:>5} mentions")
    P("")
    P("## Top 40 terms overall (by mentions, with their signal mix)")
    for k, d in by_count[:40]:
        surface = d["surfaces"].most_common(1)[0][0]
        P(f"  {d['count']:>4}  {surface:<26} [{len(d['files'])} files] {fmt_signals(d['signals'])}")
    P("")
    P("## Coinages (bold-declared terms — the repo's minted vocabulary)")
    for k, d in coinages[:30]:
        surface = d["surfaces"].most_common(1)[0][0]
        P(f"  {d['count']:>4}  {surface:<30} across {fmt_signals(d['strata'])}")
    P("")
    P("## Artifacts (inline-code terms — files / commands / ids named in prose)")
    for k, d in artifacts[:25]:
        surface = d["surfaces"].most_common(1)[0][0]
        P(f"  {d['count']:>4}  {surface:<34} [{len(d['files'])} files]")
    P("")
    P("## Load-bearing terms (>=3 signal kinds AND >=4 strata — the spine vocabulary)")
    for k, d in load_bearing[:30]:
        surface = d["surfaces"].most_common(1)[0][0]
        P(f"  {surface:<22} {len(d['strata'])} strata, {len(d['signals'])} signals, {d['count']} mentions"
          f"  ({fmt_signals(d['signals'])})")
    P("")
    P("## The latent graph (top co-occurrence edges among the top-80 terms)")
    for (a, b), n in top_edges:
        P(f"  {n:>3} shared files   {a}  —  {b}")
    P("")
    P(f"result: report — {len(terms)} distinct terms accounted across {len(files)} files; "
      f"the embedding layer (semantic clustering over these literals) is the later admitted part")


if __name__ == "__main__":
    report("--json" in sys.argv)
