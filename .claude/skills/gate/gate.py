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

# The model the headless mind judges with. It MUST be an explicit, valid model
# id (done-line 0138): a child `claude -p` with no `--model` defaults to the
# alias `opus`, which 404s headless. The gate now draws one at RANDOM per run
# from a pool (done-line 0142, bdo's direction): record the model + its cost and
# let `loop.runs` fold cost by model, so the economy of who-judges-for-how-much
# is visible. `ONTUM_GATE_MODEL`, if set, PINS one model and overrides the draw.
GATE_MODEL_POOL = [m for m in (os.environ.get("ONTUM_GATE_MODELS") or "").split(",")
                   if m.strip()] or ["claude-opus-4-8", "claude-sonnet-4-6",
                                     "claude-haiku-4-5"]
GATE_MODEL_PIN = os.environ.get("ONTUM_GATE_MODEL") or None


def pick_model(pool=None, pin=None):
    """The judging model for one run: the pin if set (an admitted override),
    else a uniform random draw from the pool. Random lives in the pen, never in
    a fold (loop/'s determinism law is for the log readers, not this launcher)."""
    pin = pin if pin is not None else GATE_MODEL_PIN
    if pin:
        return pin
    import random
    return random.choice(pool or GATE_MODEL_POOL)


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

    # the arc it serves: the epic whose pieces name this atom
    serves = []
    for ep in EPICS.glob("epic.*.json"):
        data = json.loads(ep.read_text(encoding="utf-8")).get("epic", {})
        if any(p.get("atom") == atom_id for p in data.get("pieces", [])):
            serves.append({"id": data.get("id"), "arc": data.get("arc"),
                           "glue": next((p.get("glue") for p in data.get("pieces", [])
                                         if p.get("atom") == atom_id), None)})

    # the hesitations it inherits: receipts on THIS version of the atom
    prior = [r for r in _jsonl(LOG / "receipts.jsonl")
             if r.get("artifact_id") == atom_id and r.get("artifact_hash") == artifact_hash]

    prompt = "\n".join([
        node_text,
        "\n---\n",
        "## The atom under judgment (the claim)\n",
        "```json", json.dumps(atom, indent=2, ensure_ascii=False), "```",
        "\n## The arc it serves\n",
        json.dumps(serves, indent=2, ensure_ascii=False) if serves
        else "_(this atom is not named by any epic's pieces — it serves no "
             "confirmed arc, which is itself a signal)_",
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


def _parse_cost(envelope):
    """The run's economy, from the `--output-format json` envelope: dollars and
    token usage. None for `usd` when the envelope carried no cost (an unpriced
    run confesses; the audit never reads a missing cost as $0, done-line 0142)."""
    if not isinstance(envelope, dict):
        return {"usd": None, "input_tokens": None, "output_tokens": None}
    usage = envelope.get("usage") or {}
    usd = envelope.get("total_cost_usd")
    return {
        "usd": usd if isinstance(usd, (int, float)) else None,
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
    }


def launch_claude(prompt, atom_id=None, node_id=None, model=None, runner=subprocess.run):
    """Launch the mortal process: real inference, captured, and ALWAYS traced.
    The model is drawn (or pinned) per run; the run's cost is parsed from the
    envelope so `loop.runs` can fold cost by model (done-line 0142). Returns
    (verdict, reason, raw, trace, model, cost) or raises (after writing the
    trace, whose path is named in the error) on a failure to launch/parse.
    `runner` is injectable so the §10 test exercises both paths without a live
    spawn."""
    model = model or pick_model()
    cmd = _launch_cmd(prompt, model)
    cwd = _launch_cwd()
    proc = runner(cmd, capture_output=True, text=True, cwd=cwd, timeout=600)
    raw = proc.stdout or ""
    text = raw
    envelope = None
    try:  # --output-format json wraps the result; unwrap to the model's text
        envelope = json.loads(raw)
        text = envelope.get("result", raw) if isinstance(envelope, dict) else raw
    except json.JSONDecodeError:
        pass
    cost = _parse_cost(envelope)
    # The trace is written BEFORE any parse decision — even an empty, garbled,
    # or crashed run leaves the prompt, raw output, stderr and exit code behind.
    trace = write_trace(atom_id, node_id, {
        "ts": now(), "model": model, "cwd": cwd, "cost": cost,
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
    return v["verdict"], v.get("reason", ""), text, trace, model, cost


def write_verdict(atom_id, node_id, verdict, reason):
    """The verdict lands through the one pen — D-4, never written here."""
    r = subprocess.run(
        ["python", "-m", "loop.node", "judge", "--atom", atom_id,
         "--node", node_id, "--verdict", verdict, "--reason", reason],
        capture_output=True, text=True, cwd=str(ROOT), timeout=60,
    )
    return (r.stdout + r.stderr).strip()


def record_run(node_id, atom_id, by, moved, model=None, cost=None):
    """Note the run on the ledger, carrying the model it used and its cost so
    `loop.runs` can fold cost by model (done-line 0142). A missing cost is
    passed as nothing, never as $0 — an unpriced run confesses."""
    cmd = ["python", "-m", "loop.runs", "record", "--kind", "gate-judgment",
           "--by", by, "--advanced", str(moved),
           "--note", f"{node_id} judged {atom_id}"]
    if model:
        cmd += ["--model", model]
    cost = cost or {}
    if cost.get("usd") is not None:
        cmd += ["--cost-usd", str(cost["usd"])]
    if cost.get("input_tokens") is not None:
        cmd += ["--input-tokens", str(cost["input_tokens"])]
    if cost.get("output_tokens") is not None:
        cmd += ["--output-tokens", str(cost["output_tokens"])]
    subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT), timeout=60)


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
        verdict, reason, _, _, model, cost = launch_claude(prompt, ns.atom, ns.node)
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
        record_run(ns.node, ns.atom, ns.by, moved=1, model=model, cost=cost)
        print(f"result: report — {ns.node} judged {ns.atom} -> {verdict} "
              f"({rcp_id}); issue {ref} closed with the verdict "
              f"[{model}, ${(cost or {}).get('usd') if (cost or {}).get('usd') is not None else '?'}]")
    else:
        issue_comment(address, ref, comment)
        record_run(ns.node, ns.atom, ns.by, moved=0, model=model, cost=cost)
        print(f"result: needs-you — the process returned `{verdict}` but the one "
              f"pen refused it (issue {ref} left open):\n{out}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    lp = sub.add_parser("launch", help="launch a mortal judging process for an atom at a gate")
    lp.add_argument("--atom", required=True)
    lp.add_argument("--node", required=True, help="the gate's node id, e.g. value-gate.claude.v1")
    lp.add_argument("--by", default="claude", help="who launched the run")
    lp.set_defaults(func=cmd_launch)
    ns = ap.parse_args(argv)
    return ns.func(ns)


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
