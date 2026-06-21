#!/usr/bin/env python3
"""The gate pen: a real gate is a launcher of mortal minds.

The hollowness this repo carried for 45 PRs was not "the gates return
constants." It was that the gates never *launched* anything — no process
was born, nothing ran inference, nothing could say no. A mock gate is a
turnstile with a prompt taped to it.

This pen makes a gate real the only way a gate can be real: when an atom
needs judging, it **composes the judging context from the ambient state
of the log** — the node prompt (the criteria), the atom (the claim under
judgment), the epic it serves (how it composes), and the receipts already
on it (the hesitations it inherits) — and **launches a mortal headless
process** (`claude -p`) that runs real inference, returns exactly one
verdict, and dies. The verdict lands through the one pen
(`loop.node judge`, D-4); the pen never writes a verdict itself.

bdo's trust rail (2026-06-11, after I failed him repeatedly): **every
headless run opens a GitHub issue, unconditionally, at the moment the
process is born — before it runs.** A mind that launches and hangs, or
crashes, leaves its issue OPEN; a mind that returns a verdict closes it
with the verdict and the receipt id. No headless run is ever invisible
until the gate has earned the right to run unwatched. The issue is not a
report after the fact — it is the birth certificate, written first.

Outward reach (gh) and process launch (claude) live here, in the pen,
never in loop/ (no network, no subprocess — local-first, even though the
dependency ban lifted). The pen *reads* the log to
compose; it *writes* the verdict only through loop.node judge and the run
only through loop.runs record — the seams stay the seams.

Usage:
  python .claude/skills/gate/gate.py launch --atom <id> --node <node-id> --by <who>
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("ONTUM_REPO_ROOT") or Path(__file__).resolve().parents[3])
LOG = ROOT / ".ai-native" / "log"
ATOMS = ROOT / ".ai-native" / "atoms"
NODES = ROOT / ".ai-native" / "nodes"
EPICS = ROOT / ".ai-native" / "epics"

# The model the headless mind judges with (done-line 0138). It MUST be an
# explicit, valid model id: a child `claude -p` with no `--model` defaults to
# the alias `opus`, which 404s in the headless context (`model: opus` not
# found). Configurable so the model is an admitted choice, not a buried
# constant; the default is the most capable id at authorship.
GATE_MODEL = os.environ.get("ONTUM_GATE_MODEL") or "claude-opus-4-8"

# Where each run leaves its trace — debug cache (gitignored), never truth.
GATE_RUNS = LOG / "gate-runs"

# The class a mortal `claude -p` blinks in as (D-10), and what judging needs.
# The spawn rail gates session-level spawns at the hook layer, but this pen
# births its mind from inside Python where no hook sees it — so the pen asks
# the ladder itself (atom.trust-ladder.v0: "pens and the spawn rail enforce
# the rung at act time"; done-line 0054).
GATE_CLASS = "summoned-session"
GATE_CAP = "judge"


def launch_refusal(root=None):
    """Why no mortal mind may be born for this launch, or None. A pure ask
    of the trust ladder (loop/trust.py) over a records root. Fail-open the
    way the spawn rail documents it: a ladder that cannot be read never
    blocks work — degraded enforcement, not silent extra authority."""
    try:
        sys.path.insert(0, str(ROOT))
        from loop import trust
    except Exception:
        return None  # degraded: cannot enforce, so do not block (the rail's choice)
    ai_root = Path(root) if root else ROOT / ".ai-native"
    if trust.permits(GATE_CLASS, GATE_CAP, ai_root):
        return None
    return (f"{GATE_CLASS} holds no '{GATE_CAP}' rung — the ladder denies what "
            "no admission grants (D-4: nothing grants itself a rung). bdo "
            "grants it by gesture: open the rung-confirm issue "
            f"(python .claude/skills/rung-intake/rung.py open --class {GATE_CLASS} "
            f"--capability {GATE_CAP} --repo <owner/repo>) and his "
            "close-with-comment, read by the rung-intake skill, admits it")


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _jsonl(path):
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            pass  # torn tail: the fold drops it (loop's own discipline)
    return out


def surface_address(surface="github-issues"):
    """The registered surface address (latest admission wins; a null address
    deregisters). The pen reads it from the log, never a code literal (I-8)."""
    addr = None
    for a in _jsonl(LOG / "admissions.jsonl"):
        if a.get("type") == "surface" and a.get("surface") == surface:
            addr = a.get("address")
    return addr


def _arc_confirmed(epic_id):
    """Whether an epic's arc is confirmed — the latest enabled `arc_confirmed`
    admission for it on the log wins (the arc_confirmation shape, done-line
    0028). Pure fold; bdo's standing stamp is policy, read deterministically."""
    confirmed = False
    for adm in _jsonl(LOG / "admissions.jsonl"):
        if adm.get("type") == "arc_confirmed" and adm.get("epic") == epic_id:
            confirmed = bool(adm.get("enabled", True))
    return confirmed


def policy_facts(atom_id, atom=None):
    """The deterministic policy facts the judge weighs (done-line 0146, bdo's
    principle: the data is composed from configuration + policy; only the
    judgment is non-deterministic). A pure fold over the epic records and the
    admissions log — never the atom's self-claims.

    Composes: (1) arc MEMBERSHIP — the epics whose pieces name this atom; (2)
    for each, whether that arc is CONFIRMED on the log; (3) a RECONCILIATION of
    the atom's self-claimed `incidence.serves` against the policy-composed
    membership, naming any discrepancy (a self-claim that no epic backs)."""
    serves = []
    for ep in sorted(EPICS.glob("epic.*.json")):
        data = json.loads(ep.read_text(encoding="utf-8")).get("epic", {})
        if any(p.get("atom") == atom_id for p in data.get("pieces", [])):
            serves.append({
                "id": data.get("id"), "arc": data.get("arc"),
                "confirmed": _arc_confirmed(data.get("id")),
                "glue": next((p.get("glue") for p in data.get("pieces", [])
                              if p.get("atom") == atom_id), None),
            })
    naming = {s["id"] for s in serves}
    self_claimed = list(((atom or {}).get("atom", {}).get("incidence", {}) or {}).get("serves", []))
    reconciliation = [
        {"self_claimed_epic": e, "backed_by_policy": e in naming}
        for e in self_claimed
    ]
    return {
        "arc_membership": serves,  # composed from the epic records
        "serves_confirmed_arc": any(s["confirmed"] for s in serves),
        "self_claimed_serves": self_claimed,
        "reconciliation": reconciliation,
        "unbacked_self_claims": [r["self_claimed_epic"] for r in reconciliation
                                 if not r["backed_by_policy"]],
    }


def compose(atom_id, node_id):
    """Compose the judging context from the ambient state of the log. This IS
    the gate's intelligence: not a fixed verdict, but a prompt assembled from
    everything the log knows about this atom right now."""
    node_path = NODES / f"{node_id}.md"
    if not node_path.exists():
        raise FileNotFoundError(f"no node prompt at {node_path} — a real gate "
                                "judges with a versioned prompt (§7), not vibes")
    node_text = node_path.read_text(encoding="utf-8")
    prompt_hash = sha256(node_text)

    atom_path = ATOMS / f"{atom_id}.json"
    if not atom_path.exists():
        raise FileNotFoundError(f"no atom at {atom_path}")
    atom_bytes = atom_path.read_bytes()
    artifact_hash = "sha256:" + hashlib.sha256(atom_bytes).hexdigest()
    atom = json.loads(atom_bytes)

    # composed policy facts: deterministic, from the epic records + the log,
    # NEVER the atom's self-claims (done-line 0146, bdo's principle)
    facts = policy_facts(atom_id, atom)

    # the hesitations it inherits: receipts on THIS version of the atom
    prior = [r for r in _jsonl(LOG / "receipts.jsonl")
             if r.get("artifact_id") == atom_id and r.get("artifact_hash") == artifact_hash]

    prompt = "\n".join([
        node_text,
        "\n---\n",
        "## The atom under judgment (the claim)\n",
        "```json", json.dumps(atom, indent=2, ensure_ascii=False), "```",
        "\n## Composed policy facts (deterministic — judge THESE, not the atom's self-claims)\n",
        "_Composed from the epic records and the admissions log by a pure fold. "
        "Your judgment is the only non-deterministic step; these facts are not. "
        "Where the atom's `incidence.serves` disagrees with the composed arc "
        "membership, the composed facts are authoritative — the self-claim is a "
        "claim under judgment._\n",
        "```json", json.dumps(facts, indent=2, ensure_ascii=False), "```",
        ("\n_⚠ this atom serves no confirmed arc (no epic names it as a piece, "
         "or its arc is unconfirmed) — itself a signal._"
         if not facts["serves_confirmed_arc"] else ""),
        ("\n_⚠ self-claimed serves NOT backed by policy: "
         + ", ".join(facts["unbacked_self_claims"])
         + " — the atom asserts an arc no epic confirms._"
         if facts["unbacked_self_claims"] else ""),
        "\n## Receipts already on this exact atom version (hesitations you inherit)\n",
        json.dumps([{k: r.get(k) for k in ("node", "verdict", "reason")} for r in prior],
                   indent=2, ensure_ascii=False) if prior else "_(none — you are first)_",
        "\n---\n",
        "## Your output — read this twice\n",
        "You are a mortal process. You judge this one atom, once, and dissolve. "
        "Reason in the open — check the claim against the log above, not vibes; "
        "put your hesitations on the record. Then, on the FINAL line, output "
        "EXACTLY this and nothing after it:\n",
        'VERDICT {"verdict": "<one of the seam\'s terminal verdicts named in '
        'the prompt above>", "reason": "<your reasoning, the receipt\'s payload>"}',
        "\nThe §10 test binds you: if your verdict could not conceivably have "
        "been its opposite, you did not gate — name the one check that could "
        "have failed and didn't.",
    ])
    return prompt, prompt_hash, artifact_hash


def gh(args):
    return subprocess.run(["gh"] + args, capture_output=True, text=True,
                          cwd=str(ROOT), timeout=120)


def issue_open(address, atom_id, node_id, prompt_hash):
    """The birth certificate, written first (the trust rail). Returns the issue
    ref (url), or None if gh failed — a failure here must not eat the run, but
    it is loudly reported, because an unwatched run is exactly what bdo forbade."""
    title = f"headless run: {node_id} judging {atom_id}"
    body = "\n".join([
        f"A mortal judging process was launched at **{now()}**.",
        "",
        f"- **gate (node):** `{node_id}`",
        f"- **atom (claim):** `{atom_id}`",
        f"- **prompt_hash:** `{prompt_hash[:16]}…`",
        "",
        "This issue opened at the process's *birth*, before it ran — bdo's "
        "trust rail: no headless mind runs unwatched until the gate earns it. "
        "It closes when the verdict lands. If it stays open, the process hung "
        "or crashed — and that is the thing you wanted to see.",
    ])
    r = gh(["issue", "create", "--repo", address, "--title", title, "--body", body])
    if r.returncode != 0:
        return None, r.stderr.strip()
    return r.stdout.strip().splitlines()[-1], None


def issue_close(address, ref, comment):
    gh(["issue", "close", str(ref), "--repo", address, "--comment", comment])


def issue_comment(address, ref, comment):
    gh(["issue", "comment", str(ref), "--repo", address, "--body", comment])


def _verdict_objects(text):
    """Every balanced-brace JSON object in the text that carries a string
    `verdict` key, in order. A brace-matching scan (not a `.*?` regex), so a
    `}` inside the reason can't truncate the object and a missing/markdown
    `VERDICT` sentinel can't hide a well-formed verdict the mind did return —
    the brittleness that left a correct `reject_no_value` unparsed on issue
    #58. Decoding is the filter: only objects that actually parse survive."""
    out = []
    for i, ch in enumerate(text):
        if ch != "{":
            continue
        depth = 0
        for j in range(i, len(text)):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        obj = json.loads(text[i:j + 1])
                    except json.JSONDecodeError:
                        pass
                    else:
                        if isinstance(obj, dict) and isinstance(obj.get("verdict"), str):
                            out.append(obj)
                    break
    return out


def _launch_cmd(prompt, model):
    """The argv for the mortal mind. The explicit `--model` is load-bearing:
    without it the child defaults to the `opus` alias, which 404s headless."""
    return ["claude", "-p", prompt, "--model", model, "--output-format", "json"]


def _launch_cwd():
    """A NEUTRAL working directory — NOT the repo root. Running `claude -p` from
    the repo loads its `UserPromptSubmit` session hooks into the headless child,
    which block the prompt (the process exits with num_turns: 0, an empty
    result, is_error: false — the 0-turn vanish the production-gate session hit,
    issues #284/#285). The compose() prompt is fully self-contained, so the
    judge needs no repo cwd; a neutral cwd sidesteps the project hooks."""
    return tempfile.gettempdir()


def write_trace(atom_id, node_id, info):
    """Persist the full run so a failure is debuggable instead of vanishing
    (bdo: 'shouldn't it have written some file?'). Debug cache (gitignored),
    never truth. Returns the path."""
    GATE_RUNS.mkdir(parents=True, exist_ok=True)
    stamp = now().replace(":", "").replace("-", "")
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", f"{stamp}-{atom_id or 'unknown'}-{node_id or 'gate'}")
    path = GATE_RUNS / f"{safe}.json"
    path.write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def launch_claude(prompt, atom_id=None, node_id=None, model=None, runner=subprocess.run):
    """Launch the mortal process: real inference, captured, and ALWAYS traced.
    Returns (verdict, reason, raw, trace) or raises (after writing the trace,
    whose path is named in the error) on a failure to launch/parse. `runner` is
    injectable so the §10 test exercises both paths without a live spawn."""
    model = model or GATE_MODEL
    cmd = _launch_cmd(prompt, model)
    cwd = _launch_cwd()
    proc = runner(cmd, capture_output=True, text=True, cwd=cwd, timeout=600)
    raw = proc.stdout or ""
    text = raw
    try:  # --output-format json wraps the result; unwrap to the model's text
        env = json.loads(raw)
        text = env.get("result", raw) if isinstance(env, dict) else raw
    except json.JSONDecodeError:
        pass
    # The trace is written BEFORE any parse decision — even an empty, garbled,
    # or crashed run leaves the prompt, raw output, stderr and exit code behind.
    trace = write_trace(atom_id, node_id, {
        "ts": now(), "model": model, "cwd": cwd,
        "cmd": cmd[:2] + ["<prompt elided — see 'prompt'>"] + cmd[3:],
        "returncode": proc.returncode, "prompt": prompt,
        "stdout": raw, "stderr": proc.stderr or "", "parsed_text": text,
    })
    if proc.returncode != 0 and not text.strip():
        raise RuntimeError(f"claude -p failed (exit {proc.returncode}); "
                           f"trace: {trace}; stderr: {(proc.stderr or '').strip()[:300]}")
    # Prefer a verdict object the mind tagged with the VERDICT sentinel; fall
    # back to the last well-formed verdict object anywhere in the reasoning
    # (the mind judged; the sentinel is a convention, not the verdict itself).
    tagged = re.search(r'VERDICT\b[^\{]*(\{)', text, re.DOTALL)
    objs = _verdict_objects(text[tagged.start(1):] if tagged else text)
    if not objs:
        objs = _verdict_objects(text)  # sentinel slice was empty/garbled
    if not objs:
        raise ValueError(f"the process returned no parseable verdict object; "
                         f"trace: {trace}; tail: {text.strip()[-300:]}")
    v = objs[-1]
    return v["verdict"], v.get("reason", ""), text, trace


def write_verdict(atom_id, node_id, verdict, reason):
    """The verdict lands through the one pen — D-4, never written here."""
    r = subprocess.run(
        ["python", "-m", "loop.node", "judge", "--atom", atom_id,
         "--node", node_id, "--verdict", verdict, "--reason", reason],
        capture_output=True, text=True, cwd=str(ROOT), timeout=60,
    )
    return (r.stdout + r.stderr).strip()


def record_run(node_id, atom_id, by, moved):
    subprocess.run(
        ["python", "-m", "loop.runs", "record", "--kind", "gate-judgment",
         "--by", by, "--advanced", str(moved),
         "--note", f"{node_id} judged {atom_id}"],
        capture_output=True, text=True, cwd=str(ROOT), timeout=60,
    )


def cmd_launch(ns):
    reason = launch_refusal()
    if reason:
        print(f"result: report — refused to launch: {reason}")
        return 2

    address = surface_address()
    if not address:
        print("result: needs-you — no github-issues surface is registered; the "
              "trust rail (an issue per headless run) has nowhere to write. "
              "Register one: python -m loop.reflect register --surface "
              "github-issues --address <owner/repo> --by bdo")
        return 2

    prompt, prompt_hash, _ = compose(ns.atom, ns.node)

    # the trust rail: the issue is born first, before the process runs
    ref, err = issue_open(address, ns.atom, ns.node, prompt_hash)
    if ref is None:
        print(f"result: needs-you — could not open the trust-rail issue on "
              f"{address}: {err}. Refusing to launch a headless run unwatched.")
        return 2
    print(f"  trust-rail issue opened: {ref}")

    try:
        verdict, reason, _, _ = launch_claude(prompt, ns.atom, ns.node)
    except Exception as e:  # the mind hung or crashed: leave the issue OPEN
        issue_comment(address, ref, f"⚠ the process did not return a verdict: "
                      f"{e}\n\nThe issue stays open — this is the run you wanted "
                      "to see. The full run (prompt, raw output, stderr, exit "
                      "code) is in the trace file named above.")
        record_run(ns.node, ns.atom, ns.by, moved=0)
        print(f"result: report — the headless run failed; issue {ref} left OPEN "
              f"so you see it: {e}")
        return 0

    # the verdict lands through the one pen
    out = write_verdict(ns.atom, ns.node, verdict, reason)
    landed = "result: report" in out  # judge emits report on a written receipt
    rcp = re.search(r'(rcp\.[0-9a-f]+)', out)
    rcp_id = rcp.group(1) if rcp else "(seam refused — see below)"

    comment = "\n".join([
        f"**verdict: `{verdict}`**", "",
        f"> {reason}", "",
        f"- receipt: `{rcp_id}`",
        f"- prompt_hash: `{prompt_hash[:16]}…`",
        f"- closed at {now()}",
        "", "_the one pen's response:_", f"```\n{out}\n```",
    ])
    if landed:
        issue_close(address, ref, comment)
        record_run(ns.node, ns.atom, ns.by, moved=1)
        print(f"result: report — {ns.node} judged {ns.atom} -> {verdict} "
              f"({rcp_id}); issue {ref} closed with the verdict")
    else:
        issue_comment(address, ref, comment)
        record_run(ns.node, ns.atom, ns.by, moved=0)
        print(f"result: needs-you — the process returned `{verdict}` but the one "
              f"pen refused it (issue {ref} left open):\n{out}")
    return 0


# ---------------------------------------------------------------------------
# the guaranteed review queue (done-line 0150)
# ---------------------------------------------------------------------------

# The gate whose queue is the landed-but-unsettled clog: value-confirm PARKS
# landed work awaiting a judge that, with no processor, never came — so finished
# atoms piled up against the inflight cap. A queue is healthy only with a
# guaranteed consumer; this is that consumer.
DEFAULT_REVIEW_NODE = "value-confirm.claude.v1"


def _default_review(records_root, atom_id, node_id, by):
    """Fire ONE real, trust-railed headless review for a queued atom, in its own
    process so every headless run is independently traced and watched (the trust
    rail is per-run). Reuses the `launch` verb verbatim — one rail, no twin path
    (I-4). Returns the launch process's return code."""
    proc = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "launch",
         "--atom", atom_id, "--node", node_id, "--by", by], text=True)
    return proc.returncode


def drain(records_root, by="claude", node=DEFAULT_REVIEW_NODE, review=None,
          dry_run=False, limit=None):
    """The guaranteed processor (done-line 0150): the consumer that turns the
    review queue from a CLOG into a queue. A pure level-triggered fold names the
    work — every atom awaiting an admitted-real non-owner gate
    (`loop.summon.open_summons`, re-derived from the log each call) — and the
    processor fires a REAL review (`review`, default the trust-railed launch) for
    each. It never decides or settles: the verdict and the advance stay the
    gate's and the one pen's (D-4); a `missed` keeps its atom surfaced, never
    force-cleared (no LEAK).

    Idempotent by construction: a judged atom has a receipt, so `open_summons`
    no longer returns it — a second drain fires nothing already judged — and the
    one pen no-ops a repeat verdict anyway (I-2). Level-triggered + idempotent is
    what makes the consumer a *guarantee*: a review that failed or returned no
    verdict simply leaves its atom in the queue, retried next pass — never lost,
    never double-judged.

    `review(records_root, atom_id, node_id, by)` is injectable so the §10 test
    drives the queue with a fake review (a scripted verdict through the real one
    pen) and never spawns a live mind. `records_root` is the `.ai-native` root."""
    sys.path.insert(0, str(ROOT))
    from loop.summon import open_summons
    review = review or _default_review
    queue = [s for s in open_summons(records_root)
             if node is None or s["node"] == node]
    if limit is not None:
        queue = queue[:limit]
    fired = []
    for s in queue:
        aid, nid = s["atom"]["id"], s["node"]
        fired.append({"atom": aid, "node": nid,
                      "fired": "dry-run" if dry_run else review(records_root, aid, nid, by)})
    return fired


def cmd_drain(ns):
    root = ns.root or (ROOT / ".ai-native")
    if not ns.dry_run:
        reason = launch_refusal()
        if reason:
            print(f"result: report — refused to drain: {reason}")
            return 2
    fired = drain(root, by=ns.by, node=ns.node, dry_run=ns.dry_run, limit=ns.limit)
    if not fired:
        print("result: done — the review queue is empty; nothing awaits a real "
              "review (no clog).")
        return 0
    verb = "would fire" if ns.dry_run else "fired"
    for f in fired:
        print(f"  {verb} review: {f['atom']} -> {f['node']}")
    tail = (" (dry run — nothing launched)" if ns.dry_run else
            "; each verdict lands through the one pen (D-4); a `missed` stays "
            "surfaced and a re-run fires nothing already judged (idempotent)")
    print(f"\nresult: report — drained {len(fired)} queued review(s){tail}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    lp = sub.add_parser("launch", help="launch a mortal judging process for an atom at a gate")
    lp.add_argument("--atom", required=True)
    lp.add_argument("--node", required=True, help="the gate's node id, e.g. value-gate.claude.v1")
    lp.add_argument("--by", default="claude", help="who launched the run")
    lp.set_defaults(func=cmd_launch)
    dp = sub.add_parser("drain", help="fire a real review for every atom in the "
                        "review queue — the guaranteed processor (done-line 0150)")
    dp.add_argument("--root", type=Path, default=None,
                    help="the .ai-native records root (default: this repo's)")
    dp.add_argument("--node", default=DEFAULT_REVIEW_NODE,
                    help="only drain this gate's queue (default value-confirm)")
    dp.add_argument("--all", action="store_const", const=None, dest="node",
                    help="drain every admitted-real non-owner gate's queue")
    dp.add_argument("--by", default="claude", help="who ran the drain")
    dp.add_argument("--limit", type=int, default=None,
                    help="fire at most N reviews this pass (pace the queue; the "
                         "rest are picked up the next, level-triggered, pass)")
    dp.add_argument("--dry-run", action="store_true", help="list the queue; fire nothing")
    dp.set_defaults(func=cmd_drain)
    ns = ap.parse_args(argv)
    return ns.func(ns)


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
