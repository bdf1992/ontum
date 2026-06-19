#!/usr/bin/env python3
"""Read-only atom search projection for Causality.

This is the first narrow slice of `atom.atom-search-request-node.v0`: search
real atom records, fold their current lifecycle state from the log, and return
typed JSON a canvas/API client can render. It witnesses only; it never mutates
atoms or logs.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from loop import reconcile


WORD = re.compile(r"[a-z0-9][a-z0-9_.-]*")


def tokens(text):
    return WORD.findall(str(text).lower())


def iter_strings(value, prefix=""):
    if isinstance(value, str):
        yield prefix or "value", value
    elif isinstance(value, dict):
        for key in sorted(value):
            child = f"{prefix}.{key}" if prefix else key
            yield from iter_strings(value[key], child)
    elif isinstance(value, list):
        for i, item in enumerate(value):
            child = f"{prefix}[{i}]" if prefix else f"[{i}]"
            yield from iter_strings(item, child)


def snippet(text, token, width=96):
    text = str(text).replace("\n", " ")
    low = text.lower()
    at = low.find(token)
    if at < 0:
        return text[:width]
    start = max(0, at - width // 3)
    end = min(len(text), start + width)
    out = text[start:end]
    if start:
        out = "..." + out
    if end < len(text):
        out += "..."
    return out


def atom_summary(atom, artifact_hash, state, live_ids, query_tokens):
    matches = []
    seen = set()
    searchable = {
        "id": atom.get("id", ""),
        "story": atom.get("story", {}),
        "briefing": atom.get("briefing", {}),
        "concern_surface": atom.get("concern_surface", ""),
        "incidence": atom.get("incidence", {}),
        "desired_state": atom.get("desired_state", ""),
    }
    for field, text in iter_strings(searchable):
        low = text.lower()
        for tok in query_tokens:
            if tok in low and (field, tok) not in seen:
                seen.add((field, tok))
                matches.append({"field": field, "token": tok, "snippet": snippet(text, tok)})
    epics = [
        s for s in atom.get("incidence", {}).get("serves", [])
        if isinstance(s, str) and s.startswith("epic.")
    ]
    return {
        "id": atom["id"],
        "artifact_hash": artifact_hash,
        "state": state,
        "desired_state": atom.get("desired_state"),
        "live": atom["id"] in live_ids,
        "epics": epics,
        "concern_surface": atom.get("concern_surface"),
        "score": len({m["token"] for m in matches}),
        "matches": matches,
        "record_kind": "projected",
    }


def build_projection(query, root=reconcile.DEFAULT_ROOT):
    query_tokens = sorted(set(tokens(query)))
    out = {
        "view": "atom-search",
        "generator": "causality.atom_search",
        "source": "the repo log and atom files are truth; this is a read-only projection",
        "query": " ".join(query_tokens),
        "result_count": 0,
        "results": [],
        "gaps": [],
    }
    if not query_tokens:
        out["gaps"].append({
            "kind": "empty-query",
            "why": "atom search needs at least one alphanumeric token",
            "move": "provide a concrete term, atom id, epic id, file, or story word",
        })
        return out

    fold = reconcile.Fold(root)
    atoms = reconcile.load_atoms(root)
    live_ids = {atom["id"] for atom, _ in atoms} - reconcile.superseded_atom_ids(
        [atom["id"] for atom, _ in atoms])
    for atom, artifact_hash in atoms:
        summary = atom_summary(
            atom, artifact_hash, reconcile.atom_state(fold, artifact_hash),
            live_ids, query_tokens)
        if summary["score"]:
            out["results"].append(summary)
    out["results"].sort(key=lambda r: (-r["score"], r["id"]))
    out["result_count"] = len(out["results"])
    if not out["results"]:
        out["gaps"].append({
            "kind": "no-match",
            "why": f"no atom record matched query tokens {query_tokens}",
            "move": "search a different term, or treat the absence as evidence that no atom names it yet",
        })
    return out


def dumps(projection):
    return json.dumps(projection, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="causality.atom_search",
        description="read-only atom search projection for Causality")
    ap.add_argument("query", nargs="*", help="tokens to search across atom records")
    ap.add_argument("--root", default=str(reconcile.DEFAULT_ROOT),
                    help="records root (default: .ai-native)")
    args = ap.parse_args(argv)
    sys.stdout.write(dumps(build_projection(" ".join(args.query), root=Path(args.root))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
