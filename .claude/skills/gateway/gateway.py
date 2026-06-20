#!/usr/bin/env python3
"""The inference gateway pen: the data plane of a governed local inference plane.

Done-line 0062 (epic.inference-gateway). The loop's single way to think. Today
the only way to run inference was a bare `claude -p` inside the gate pen — and
the day it was first used in anger it jammed twice (600s timeouts, #95/#96) and
a human filled the seat by hand. This pen is the local-first answer: not a
dependency-heavy proxy with YAML for a brain, but what a proxy would be if it
were a loop citizen — the config plane (loop/inference.py + loop/minds.py) as
the control plane of admitted, bdo-signed records; this pen as the data plane.

One call does five things, in order:
  1. fold the log — the route's mind order, the registered minds, the policies;
  2. authorize — the policy enforcement point: (caller, surface, mind) ->
     permit/refuse, default-deny (RBAC, the no-bypass invariant's other half);
  3. resolve — any backing scheme (http/https/env/profile/odysseus/file) to one
     normalized OpenAI-compatible target (loop/inference.normalize_backing);
  4. complete — ONE normalized completion over stdlib urllib, bounded by a
     timeout so a hung backing can never become a 600s stuck gate again;
  5. receipt — exactly one receipt per attempt (mind, backing, prompt_hash,
     latency_ms, tokens, outcome), and on a down/hung/refused mind it FALLS
     BACK by the route order to the next, receipting the fallback.

No-bypass (0062 piece 6): this pen is the sole sanctioned inference path.
Outward reach (the HTTP POST) and any future external-family disclosure live
ONLY here, never in loop/ (the stdlib no-network hard rule). The one legacy
exception is the gate pen's agentic `claude -p`, whose migration is
atom.gate-through-gateway.v0 — tests/test_gateway.py::test_no_bypass pins it as
the single named egress and fails the moment a SECOND one appears.

Usage:
  python .claude/skills/gateway/gateway.py complete \\
      --caller summoned-session --surface chat --route default \\
      --prompt "..."   [--mind <id>] [--by claude] [--timeout 60]
"""

import argparse
import hashlib
import json
import os
import socket
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(os.environ.get("ONTUM_REPO_ROOT") or Path(__file__).resolve().parents[3])
sys.path.insert(0, str(ROOT))

from loop import inference, inference_queue, minds  # noqa: E402
from loop.reconcile import Fold, append_line, now_ts, short_hash  # noqa: E402


def sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _post_completion(base_url, model, prompt, timeout):
    """One normalized OpenAI-compatible chat completion over stdlib urllib.
    Returns (content, tokens). Raises on any transport/HTTP/parse failure so
    the caller can receipt the failure and fall back. Bounded by `timeout` —
    the #95/#96 600s-hang made impossible: no single attempt can exceed it."""
    url = base_url.rstrip("/") + "/chat/completions"
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    choices = body.get("choices") or []
    if not choices:
        raise ValueError(f"no choices in completion response: {str(body)[:200]}")
    content = choices[0].get("message", {}).get("content", "")
    usage = body.get("usage") or {}
    tokens = usage.get("total_tokens")
    return content, tokens


def _receipt(root, *, mind, backing, model, prompt_hash, latency_ms, tokens,
             outcome, caller, surface, route, attempt, fallback_from=None,
             reason=None, by="claude"):
    """Append exactly one inference receipt. The proof a thought happened (or
    was refused/failed) and what it cost — the act on the record."""
    rcp = {
        "id": "rcp." + short_hash("inference", str(mind), prompt_hash,
                                  now_ts(), str(attempt)),
        "type": "inference",
        "mind": mind,
        "backing": backing,
        "model": model,
        "prompt_hash": prompt_hash,
        "latency_ms": latency_ms,
        "tokens": tokens,
        "outcome": outcome,           # ok | error | refused | unregistered
        "caller": caller,
        "surface": surface,
        "route": route,
        "fallback_from": fallback_from,
        "reason": reason,
        "by": by,
        "ts": now_ts(),
    }
    append_line(root / "log" / "receipts.jsonl", rcp)
    return rcp


def complete(prompt, *, caller, surface, route="default", mind=None,
             root=None, by="claude", timeout=60, writing_mind=None,
             queue_wait_ms=None):
    """Route one prompt through the governed plane. Returns a dict:
      {ok, content, mind, receipts, reason}.
    Walks the route order (or the single explicit --mind); for each mind:
    authorize -> admit (claim an in-flight slot) -> resolve backing -> bounded
    completion. The first authorized, live mind answers; a refused/down/hung
    mind is receipted and falls back to the next; a saturated plane is refused
    with a witnessed receipt. result reported by the CLI; receipts are the
    truth. `queue_wait_ms` is how long a request waits for a slot before that
    refusal (default: one `timeout`)."""
    ai_root = Path(root) if root else ROOT / ".ai-native"
    if queue_wait_ms is None:
        queue_wait_ms = timeout * 1000
    fold = Fold(ai_root)
    registered = minds.registered_minds(fold)
    order = [mind] if mind else inference.resolve_order(fold, route)
    prompt_hash = sha256(prompt)
    receipts = []

    if not order:
        return {"ok": False, "content": None, "mind": None, "receipts": [],
                "reason": (f"no minds in route {route!r} — register a mind "
                           "(loop.minds register --by bdo) and set the route "
                           "(loop.inference route --by bdo)")}

    primary = order[0]
    for attempt, mind_id in enumerate(order):
        fallback_from = primary if mind_id != primary else None
        adm = registered.get(mind_id)
        if adm is None:
            receipts.append(_receipt(
                ai_root, mind=mind_id, backing=None, model=None,
                prompt_hash=prompt_hash, latency_ms=0, tokens=None,
                outcome="unregistered", caller=caller, surface=surface,
                route=route, attempt=attempt, fallback_from=fallback_from,
                reason="no mind admission by this id", by=by))
            continue

        permit, reason = inference.authorize(fold, caller, surface, mind_id, writing_mind)
        if not permit:
            receipts.append(_receipt(
                ai_root, mind=mind_id, backing=adm.get("backing"),
                model=adm.get("model"), prompt_hash=prompt_hash, latency_ms=0,
                tokens=None, outcome="refused", caller=caller, surface=surface,
                route=route, attempt=attempt, fallback_from=fallback_from,
                reason=reason, by=by))
            continue

        try:
            target = inference.normalize_backing(adm.get("backing"), adm.get("model"))
        except ValueError as e:
            receipts.append(_receipt(
                ai_root, mind=mind_id, backing=adm.get("backing"),
                model=adm.get("model"), prompt_hash=prompt_hash, latency_ms=0,
                tokens=None, outcome="error", caller=caller, surface=surface,
                route=route, attempt=attempt, fallback_from=fallback_from,
                reason=f"unresolvable backing: {e}", by=by))
            continue

        # admission control: claim one of `bound` in-flight slots before the
        # completion. A burst of callers can never hold more than the bound's
        # worth of model/KV-cache resident at once; excess waits, and a plane
        # that stays saturated for the whole wait is REFUSED with a witnessed
        # receipt — backpressure on the record, never a silent host-kill. The
        # slot is held only for the duration of the POST (the memory-consuming
        # part); a lease makes a hard-killed caller's slot self-heal.
        bound = inference_queue.concurrency_bound(fold)
        lease_ms = (timeout + inference_queue.LEASE_GRACE_S) * 1000
        slot = inference_queue.acquire(
            ai_root, bound=bound, lease_ms=lease_ms, wait_ms=queue_wait_ms)
        if slot is None:
            receipts.append(_receipt(
                ai_root, mind=mind_id, backing=adm.get("backing"),
                model=target.get("model"), prompt_hash=prompt_hash,
                latency_ms=0, tokens=None, outcome="saturated", caller=caller,
                surface=surface, route=route, attempt=attempt,
                fallback_from=fallback_from,
                reason=(f"inference plane saturated: {bound} in flight, waited "
                        f"{queue_wait_ms}ms for a slot"), by=by))
            break  # host-level backpressure — a fallback hits the same host

        start = time.monotonic()
        try:
            content, tokens = _post_completion(
                target["base_url"], target["model"], prompt, timeout)
        except (urllib.error.URLError, socket.timeout, OSError, ValueError,
                json.JSONDecodeError) as e:
            latency_ms = int((time.monotonic() - start) * 1000)
            receipts.append(_receipt(
                ai_root, mind=mind_id, backing=adm.get("backing"),
                model=target.get("model"), prompt_hash=prompt_hash,
                latency_ms=latency_ms, tokens=None, outcome="error",
                caller=caller, surface=surface, route=route, attempt=attempt,
                fallback_from=fallback_from,
                reason=f"{type(e).__name__}: {str(e)[:160]}", by=by))
            continue
        finally:
            inference_queue.release(slot)

        latency_ms = int((time.monotonic() - start) * 1000)
        rcp = _receipt(
            ai_root, mind=mind_id, backing=adm.get("backing"),
            model=target.get("model"), prompt_hash=prompt_hash,
            latency_ms=latency_ms, tokens=tokens, outcome="ok", caller=caller,
            surface=surface, route=route, attempt=attempt,
            fallback_from=fallback_from, reason=None, by=by)
        receipts.append(rcp)
        return {"ok": True, "content": content, "mind": mind_id,
                "receipts": receipts, "reason": None}

    return {"ok": False, "content": None, "mind": None, "receipts": receipts,
            "reason": "no authorized live backing in the route — every mind "
                      "refused or failed; the receipts say which"}


def cmd_complete(ns):
    prompt = ns.prompt
    if ns.prompt_file:
        prompt = Path(ns.prompt_file).read_text(encoding="utf-8")
    if not prompt:
        print("result: needs-you — a prompt is required (--prompt or --prompt-file)")
        return 2
    out = complete(prompt, caller=ns.caller, surface=ns.surface, route=ns.route,
                   mind=ns.mind, by=ns.by, timeout=ns.timeout,
                   queue_wait_ms=(None if ns.queue_wait is None
                                  else int(ns.queue_wait * 1000)))
    for r in out["receipts"]:
        tail = f" <- fallback from {r['fallback_from']}" if r.get("fallback_from") else ""
        extra = f" ({r['reason']})" if r.get("reason") else ""
        print(f"  receipt {r['id']}: {r['mind']} -> {r['outcome']} "
              f"[{r['latency_ms']}ms]{tail}{extra}")
    if out["ok"]:
        print(f"\n{out['content']}\n")
        print(f"result: report — {out['mind']} answered through the gateway "
              f"({len(out['receipts'])} receipt(s); a thought on the record)")
        return 0
    print(f"result: needs-you — {out['reason']}")
    return 2


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    cp = sub.add_parser("complete", help="route one completion through the governed plane")
    cp.add_argument("--prompt", default=None, help="the prompt text")
    cp.add_argument("--prompt-file", default=None, help="read the prompt from a file")
    cp.add_argument("--caller", required=True,
                    help="the caller's identity: an agent class / node id")
    cp.add_argument("--surface", required=True, help="the surface the call rides")
    cp.add_argument("--route", default="default", help="route name (default 'default')")
    cp.add_argument("--mind", default=None,
                    help="an explicit mind id, bypassing the route order")
    cp.add_argument("--by", default="claude", help="who ran the call")
    cp.add_argument("--timeout", type=int, default=60,
                    help="per-attempt seconds — bounds a hung backing (#95/#96)")
    cp.add_argument("--queue-wait", type=float, default=None, dest="queue_wait",
                    help="seconds to wait for an in-flight slot before refusing "
                         "as saturated (default: one --timeout)")
    cp.set_defaults(func=cmd_complete)
    ns = ap.parse_args(argv)
    return ns.func(ns)


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
