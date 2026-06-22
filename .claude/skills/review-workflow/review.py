#!/usr/bin/env python3
"""The workflow-authoring wrapper's review interface (A3).

The review half of the branded wrapper (mirrors the PR pen): a drafted workflow
is rendered as the SHAPED READ a reviewer needs — *what it does · its phases ·
its blast radius · the riskiest step* (the Taster's Clause: a shaped choice, not
a raw script dump) — and, on approval, an **arm** act is recorded on the log.

Arming binds to the workflow's BYTES (sha256), the repo's content-hash identity
invariant: editing a workflow un-arms it, so a changed workflow must be reviewed
again before it can run. The run rail (A4) refuses any workflow that is not armed
at its current bytes.

  render: python .claude/skills/review-workflow/review.py render <workflow.js> [--json]
  arm:    python .claude/skills/review-workflow/review.py arm <workflow.js> --by <who>
  status: python .claude/skills/review-workflow/review.py status <workflow.js>

Render is read-only. Arm refuses a draft that fails the authoring check (lint.py)
— a malformed workflow cannot be armed.
"""

import hashlib
import importlib.util
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]

# Reuse the authoring check as the ONE authority on well-formedness + the
# mutation flag (I-4: the wrapper must not grow a second, drifting definition).
# If the check is unreachable, fail CLOSED but NAMED — an actuator (arm) must
# never proceed on an absent gate, and never die with a bare traceback.
_LINT = ROOT / ".claude" / "skills" / "author-workflow" / "lint.py"
_LINT_ERR = None
try:
    _spec = importlib.util.spec_from_file_location("workflow_lint", _LINT)
    _lint = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_lint)
except Exception as exc:  # noqa: BLE001 — any import failure must fail closed
    _lint = None
    _LINT_ERR = str(exc)

# The log append path + helpers — the same write seam (and the same READ fold,
# read_jsonl) every pen uses; no second read path (I-4).
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from loop.reconcile import append_line, now_ts, read_jsonl, short_hash  # noqa: E402

ARMED = "workflow_armed"


def _hash_bytes(raw):
    # identity is sha256 over the RAW file bytes (reconcile.py atom id), never
    # read_text — universal-newline translation would diverge from the repo's
    # canonical hash (the 0007 CRLF trap). .claude/workflows/*.js is -text-pinned.
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _meta_titles(block):
    """The phase titles declared in the meta literal, in order."""
    return re.findall(r"\btitle\s*:\s*['\"]([^'\"]+)['\"]", block or "")


def _description(block):
    """meta.description — the run of string literals (possibly `+`-joined)
    immediately after `description:`, concatenated."""
    if not block:
        return ""
    m = re.search(r"\bdescription\s*:\s*", block)
    if not m:
        return ""
    pat = re.compile(r"\s*\+?\s*(['\"])(.*?)\1", re.DOTALL)
    out, pos, tail = [], 0, block[m.end():]
    while True:
        mm = pat.match(tail, pos)
        if not mm:
            break
        out.append(mm.group(2))
        pos = mm.end()
    return "".join(out).strip()


def render(workflow_path):
    p = pathlib.Path(workflow_path)
    slug = p.stem
    if _lint is None:  # fail closed but named: no gate, no shaped read
        return {"slug": slug, "version_hash": None, "what": "", "phases": [],
                "blast_radius": "unknown", "riskiest_step": "unknown",
                "lint_ok": False, "fit_ok": False, "dangling": [],
                "problems": [f"the authoring check is unreachable ({_LINT_ERR}) "
                             "— cannot verify or arm this workflow"]}
    lint = _lint.lint(str(p))
    fit = _lint.fit(str(p))
    text = p.read_text(encoding="utf-8") if p.exists() else ""
    raw = p.read_bytes() if p.exists() else b""
    block = _lint._meta_block(text) if text else None
    mutates = lint["flags"].get("mutates", False)
    titles = _meta_titles(block)
    return {
        "slug": lint["slug"],
        "version_hash": _hash_bytes(raw) if text else None,
        "what": _description(block),
        "phases": titles,
        "blast_radius": "mutates" if mutates else "read-only",
        "riskiest_step": (
            "writes/changes files — must run worktree-isolated; review the "
            "mutating step before arming"
            if mutates else
            "none — read-only; worst case is wasted tokens"
        ),
        "lint_ok": lint["ok"],
        "fit_ok": fit["ok"],
        "dangling": fit["dangling"],
        "problems": lint["problems"],
    }


def armings(root):
    """Fold the log for arm acts: {(slug, version_hash): latest record}, latest
    wins (so a disarm supersedes an arm). Folds through the canonical read_jsonl
    — no second read path (I-4); it already drops torn lines."""
    records, _ = read_jsonl(pathlib.Path(root) / ".ai-native" / "log" / "admissions.jsonl")
    out = {}
    for rec in records:
        if rec.get("type") == ARMED:
            out[(rec.get("workflow"), rec.get("version_hash"))] = rec
    return out


def is_armed(slug, version_hash, root=ROOT):
    """Armed iff the latest arm record for these exact bytes is enabled — a
    disarm (enabled:false, superseding) flips it back, never an erase."""
    rec = armings(root).get((slug, version_hash))
    return bool(rec) and rec.get("enabled", True)


def _arm_record(r, by, enabled):
    # idempotence keyed on CONTENT, not the clock (I-2: a re-arm of the same
    # bytes by the same approver folds to one record). Disarm carries a distinct
    # marker so it is its own line. The path is the D-13 carbon copy — which
    # bytes were armed is re-joinable from the log alone.
    marker = (ARMED,) if enabled else (ARMED, "disarm")
    return {
        "id": "adm." + short_hash(*marker, r["slug"], r["version_hash"], str(by)),
        "type": ARMED,
        "workflow": r["slug"],
        "path": f".claude/workflows/{r['slug']}.js",
        "version_hash": r["version_hash"],
        "blast_radius": r["blast_radius"],
        "enabled": enabled,
        "by": by,
        "ts": now_ts(),
    }


def arm(workflow_path, by, root=ROOT):
    """Record approval to run — refuses a workflow that fails the authoring check
    OR the §10 fit check (a dangling workflow() reference). Binds to the bytes,
    so a later edit un-arms it. Returns the admission, or None on refusal."""
    r = render(workflow_path)
    if not r["lint_ok"] or not r.get("fit_ok", True):
        problems = list(r["problems"]) + [f"dangling workflow() reference: {x}"
                                           for x in r.get("dangling", [])]
        print("result: needs-you — cannot arm; the workflow does not pass the "
              "gate:\n  - " + "\n  - ".join(problems), file=sys.stderr)
        return None
    adm = _arm_record(r, by, enabled=True)
    append_line(pathlib.Path(root) / ".ai-native" / "log" / "admissions.jsonl", adm)
    return adm


def disarm(workflow_path, by, root=ROOT):
    """Withdraw approval on the record (supersede-never-erase) — a workflow found
    dangerous without a byte edit can be un-armed. Returns the admission."""
    r = render(workflow_path)
    if not r["version_hash"]:
        print("result: needs-you — nothing to disarm (no workflow bytes)", file=sys.stderr)
        return None
    adm = _arm_record(r, by, enabled=False)
    append_line(pathlib.Path(root) / ".ai-native" / "log" / "admissions.jsonl", adm)
    return adm


def _print_read(r, root):
    armed = r["version_hash"] and is_armed(r["slug"], r["version_hash"], root)
    print(f"workflow: {r['slug']}   [{r['blast_radius']}]   "
          + ("ARMED" if armed else "not armed"))
    if not r["lint_ok"] or not r.get("fit_ok", True):
        print("  REFUSED by the gate:")
        for prob in r["problems"]:
            print(f"    - {prob}")
        for ref in r.get("dangling", []):
            print(f"    - dangling workflow() reference: {ref}")
        return
    print(f"  what: {r['what']}")
    if r["phases"]:
        print("  phases: " + " → ".join(r["phases"]))
    print(f"  riskiest step: {r['riskiest_step']}")
    if not armed:
        print(f"  to arm: review.py arm {r['slug']}.js --by <you>")


def main(argv):
    if not argv:
        print("usage: review.py <render|arm|status> <workflow.js> [--json] [--by <who>]",
              file=sys.stderr)
        return 2
    verb = argv[0]
    rest = argv[1:]
    paths = [a for a in rest if not a.startswith("--")]
    by = None
    if "--by" in rest:
        i = rest.index("--by")
        by = rest[i + 1] if i + 1 < len(rest) else None
    if not paths:
        print("usage: review.py <verb> <workflow.js> ...", file=sys.stderr)
        return 2
    wf = paths[0]

    if verb in ("render", "status"):
        r = render(wf)
        if "--json" in rest:
            r["armed"] = bool(r["version_hash"] and is_armed(r["slug"], r["version_hash"], ROOT))
            print(json.dumps(r, ensure_ascii=False, indent=2))
        else:
            _print_read(r, ROOT)
        return 0 if (r["lint_ok"] and r.get("fit_ok", True)) else 1
    if verb in ("arm", "disarm"):
        if not by:
            print(f"result: needs-you — {verb} requires --by <who> (the approver "
                  "is recorded on the log)", file=sys.stderr)
            return 2
        adm = (arm if verb == "arm" else disarm)(wf, by)
        if adm is None:
            return 1
        word = "armed" if adm["enabled"] else "disarmed"
        print(f"result: done — {word} {adm['workflow']} ({adm['blast_radius']}) "
              f"by {by} at {adm['version_hash'][:19]}…  [{adm['id']}]")
        return 0
    print(f"unknown verb {verb!r}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
