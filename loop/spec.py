"""loop/spec.py — the spec particle's identity + versioning fold (node 1).

A `spec` is an authored document (requirement, user story, arch diagram,
expectation, suggestion) treated as a first-class, versioned, refactorable
particle — a sibling of the atom (reconcile.py), sharing the log.

Node 1 (the load-bearing floor) builds ONLY criterion 1 of the spec-particle
outcome (grammar/goals.md): identity + versioning + supersession. The gate
(criterion 2), the spec->atom link (3), and per-version acceptance (5) are
later nodes — but they all key off the identity built here.

Identity is the sha256 of the spec file's BYTES, never a `.vN` id-string —
this forbids the recorded id-vs-hash hole (heal/#424) that every later tooth
keys off. Create and supersede are APPENDED provenance admissions (--by, ts,
reason; supersession names old_hash AND new_hash; no retro-invalidation). Spec
state is DERIVED by folding those appends, never from file-bytes/proximity
(D-8): delete the file and the recorded version still stands.

Spec bytes live under `.ai-native/specs/`, already eol-exempt via
`.gitattributes` (`.ai-native/**`) — content-hash identity is vacuous if
checkout mutates CRLF/LF.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from loop.reconcile import append_line, dedup_by_id, now_ts, read_jsonl, short_hash

SPEC_VERSION = "spec_version"
SPEC_SUPERSEDED = "spec_superseded"


def specs_dir(root: Path) -> Path:
    return Path(root) / ".ai-native" / "specs"


def admissions_path(root: Path) -> Path:
    return Path(root) / ".ai-native" / "log" / "admissions.jsonl"


def spec_hash(path) -> str:
    """A spec's identity: sha256 of its file bytes (never an id-string)."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def slug_of(path) -> str:
    """Stable slug from the spec filename, without the .md extension."""
    name = Path(path).name
    if name.endswith(".md"):
        name = name[:-3]
    return name


def _spec_admissions(root: Path):
    recs, _ = read_jsonl(admissions_path(root))
    recs = dedup_by_id(recs)
    return [r for r in recs if r.get("type") in (SPEC_VERSION, SPEC_SUPERSEDED)]


def fold(root: Path) -> dict:
    """Derive spec state from the log (never from files). Per slug: the
    versions seen (by content-hash), the supersession edges, and the live
    head — the known version that no supersession names as old_hash.

    The split is by CONTENT-HASH, never by slug/id-string: two records for one
    slug with different hashes are two versions. An id-string reading would
    collapse them and silently inherit the heal/#424 hole — see
    tests/test_spec.py for the non-vacuity proof."""
    specs: dict = {}
    for r in _spec_admissions(root):
        slug = r.get("spec")
        if not slug:
            continue
        s = specs.setdefault(slug, {"versions": [], "edges": [], "superseded": set()})
        if r["type"] == SPEC_VERSION:
            h = r.get("content_hash")
            if h and h not in s["versions"]:
                s["versions"].append(h)
        elif r["type"] == SPEC_SUPERSEDED:
            old, new = r.get("old_hash"), r.get("new_hash")
            if old and new:
                s["edges"].append((old, new))
                s["superseded"].add(old)
                # the edge attests both endpoints are versions, even if a
                # version record for one has not (yet) been folded.
                for h in (old, new):
                    if h not in s["versions"]:
                        s["versions"].append(h)
    for s in specs.values():
        live = [h for h in s["versions"] if h not in s["superseded"]]
        s["head"] = live[-1] if live else None
        s["live"] = live
        s["superseded"] = sorted(s["superseded"])
    return specs


def head(root: Path, slug: str):
    return fold(root).get(slug, {}).get("head")


def record_version(root: Path, path, by: str, reason: str) -> dict:
    """Record the current bytes of a spec file as a version. If the slug
    already has a different live head, also append the supersession edge
    (old=head -> new). Idempotent: re-recording the same bytes is a no-op
    (same id, first-wins dedup)."""
    p = Path(path)
    h = spec_hash(p)
    slug = slug_of(p)
    prior = head(root, slug)
    ver = {
        "id": "spec." + short_hash(SPEC_VERSION, slug, h),
        "type": SPEC_VERSION,
        "spec": slug,
        "content_hash": h,
        "by": by,
        "reason": reason,
        "ts": now_ts(),
    }
    append_line(admissions_path(root), ver)
    superseded = None
    if prior and prior != h:
        sup = {
            "id": "spec." + short_hash(SPEC_SUPERSEDED, slug, prior, h),
            "type": SPEC_SUPERSEDED,
            "spec": slug,
            "old_hash": prior,
            "new_hash": h,
            "by": by,
            "reason": reason,
            "ts": now_ts(),
        }
        append_line(admissions_path(root), sup)
        superseded = prior
    return {"slug": slug, "content_hash": h, "superseded": superseded}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="loop.spec")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("status")
    sv = sub.add_parser("version")
    sv.add_argument("--path", required=True)
    sv.add_argument("--by", required=True)
    sv.add_argument("--reason", required=True)
    args = ap.parse_args(argv)
    root = Path.cwd()
    if args.cmd == "version":
        res = record_version(root, args.path, by=args.by, reason=args.reason)
        sup = f" (supersedes {res['superseded'][:12]})" if res["superseded"] else ""
        print(f"done — spec {res['slug']} @ {res['content_hash'][:12]}{sup}")
    else:
        specs = fold(root)
        if not specs:
            print("report — no specs recorded")
            return
        for slug, s in sorted(specs.items()):
            h = (s["head"] or "-")[:12]
            print(f"{slug}: head {h} · {len(s['versions'])} version(s) · {len(s['superseded'])} superseded")


if __name__ == "__main__":
    main()
