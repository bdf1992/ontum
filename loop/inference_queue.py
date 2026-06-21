#!/usr/bin/env python3
"""loop/inference_queue.py — the inference admission queue (done-line 0149).

The gateway (`.claude/skills/gateway/gateway.py`) authorizes and receipts every
completion, but it fired each one **immediately and synchronously** — no
admission control, no concurrency bound, no backpressure. N concurrent callers
became N concurrent loads on the metal; the only queue was Ollama's internal
one, which the loop neither controlled nor witnessed. That unbounded fan-in is
the mechanism behind "hammering kills my PC" — a burst of completions stacks
models and KV-cache past physical memory and the host swap-thrashes into a
freeze.

This is the **summon queue on a new axis**: `loop/summon.py` admits *atoms*
waiting for *nodes*; this admits *requests* waiting for a *model slot*. Three
parts, all stdlib and local-first (the loop/ no-network law — a file semaphore
is a local coordination primitive, not a daemon):

  1. the **dial** — `concurrency_bound`/`set_bound`: how many completions may be
     in flight at once is an admitted, bdo-signed record (default-safe when
     unset, never a code constant — the substrate's "setpoints are admitted
     records" law).
  2. the **semaphore** — `acquire`/`release`: a lease-based file semaphore. A
     slot is claimed atomically by `os.link`-ing an already-written file into
     place (so the slot is never observed empty — see `_try_claim`); a request
     that finds every slot taken waits up to a bound and, still saturated, is
     refused. The lease
     makes it **torn-tail safe**: a hard-killed caller's slot self-heals on the
     next acquire once its lease expires — the same mortality property the fold
     relies on (a partially-done thing "never happened"; the next pass
     re-derives).
  3. the **stats fold** — `stats`: a read-only fold over the inference receipts
     (throughput, per-mind latency, saturation) plus the live in-flight count.
     The receipts were already the stats channel; this just reads them.

The gateway acquires a slot before the completion and releases after,
receipting a `saturated` outcome when it cannot within the wait — backpressure
on the record, never a silent host-kill. Read-only but for the one dial setter;
the cut (what the bound should be) stays bdo's (D-4). result: report.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT, Fold, append_line, now_ts, short_hash

GRANTOR = "bdo"  # the bound is a dial; one stamp re-steers it (D-4)
DIAL_TYPE = "inference_concurrency"

# The default when no dial is admitted. Safe, not zero: it allows *some*
# concurrency (one model can serve more than one call) while keeping the
# in-flight footprint bounded well under a single host's memory. bdo tunes it
# from measurement via `admit --bound N --by bdo` — never edited here.
DEFAULT_BOUND = 2

# A slot's lease outlives the call it guards by this grace, so a slot is
# reclaimed only when its holder is genuinely overdue (truly hung or dead),
# never merely slow.
LEASE_GRACE_S = 15

SLOTS_DIRNAME = "inference-slots"  # ephemeral cache under .ai-native/ (gitignored)


# --------------------------------------------------------------- the dial

def concurrency_bound(fold):
    """The admitted in-flight bound (latest non-superseded dial), or the safe
    default. A pure fold — the bound is read from the log at call time, never a
    literal."""
    superseded = {a["supersedes"] for a in fold.admissions if a.get("supersedes")}
    latest = None
    for adm in fold.admissions:
        if (adm.get("type") == DIAL_TYPE
                and adm.get("id") not in superseded
                and isinstance(adm.get("bound"), int)):
            latest = adm  # log order is append order; last wins
    if latest is None:
        return DEFAULT_BOUND
    return max(1, int(latest["bound"]))


def set_bound(root, bound, by, supersedes=None):
    """Admit the concurrency dial. bdo-signed config, superseding never erasing
    (mirrors loop.inference.set_route). Returns the admission, or None if the
    bound is not a positive int."""
    try:
        bound = int(bound)
    except (TypeError, ValueError):
        return None
    if bound < 1:
        return None
    adm = {
        "id": "adm." + short_hash(DIAL_TYPE, str(bound), by, now_ts()),
        "type": DIAL_TYPE,
        "bound": bound,
        "by": by,
        "supersedes": supersedes,
        "ts": now_ts(),
    }
    append_line(Path(root) / "log" / "admissions.jsonl", adm)
    return adm


# ----------------------------------------------------------- the semaphore

def slots_dir(root):
    return Path(root) / SLOTS_DIRNAME


def _slot_path(root, i):
    return slots_dir(root) / f"slot-{i}.lock"


def _is_stale(path, *, _now=None):
    """A slot is stale when its lease has expired (holder overdue or dead) or
    its file is unreadable/torn — either way it is reclaimable. An unparseable
    slot reads as stale, never as a permanent lock (torn-tail tolerance)."""
    now = time.time() if _now is None else _now
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return True
    deadline = data.get("lease_deadline")
    if not isinstance(deadline, (int, float)):
        return True
    return now >= deadline


def _try_claim(root, i, lease_s):
    """Atomically claim slot i, or return None if it is held by a live lease.
    The claim writes the FULLY-FORMED slot content to a private temp file, then
    `os.link`s it into the slot path: link is atomic and fails if the slot
    already exists, so two racing callers can never both win the same index AND
    the slot file is never observed empty. (An `O_EXCL` *create* is atomic, but
    create-then-write leaves a window where a concurrent reader sees an empty
    file, mis-judges it `stale`, and double-claims it — the bound violation the
    concurrency stress test caught: 6 holders on a bound of 3.) A genuinely
    stale slot is stolen (unlink + re-link); the loser of a steal race simply
    moves on."""
    path = _slot_path(root, i)
    token = short_hash("slot", str(i), str(os.getpid()), repr(time.time_ns()))
    payload = json.dumps({
        "slot": i,
        "pid": os.getpid(),
        "token": token,
        "acquired": time.time(),
        "lease_deadline": time.time() + lease_s,
    })
    fd, tmp = tempfile.mkstemp(dir=str(slots_dir(root)), prefix=f".slot-{i}.")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(payload)
        for steal in (False, True):
            try:
                os.link(tmp, str(path))  # atomic exclusive claim, content already present
            except FileExistsError:
                if steal:
                    return None
                if _is_stale(path):
                    try:
                        os.unlink(str(path))
                    except OSError:
                        pass
                    continue  # retry the atomic link (steal pass)
                return None
            except OSError:
                # the filesystem could not complete the link (a transient I/O
                # error, or a volume without hardlink support). `acquire`'s
                # contract is to return a handle or None, never to raise; this
                # slot is simply unavailable this sweep — acquire's poll loop
                # retries it. (Slot files live under .ai-native/ on the repo's
                # own volume, which supports hardlinks; this is the floor.)
                return None
            return {"path": path, "token": token, "slot": i}
        return None
    finally:
        try:
            os.unlink(tmp)  # drop the temp name; the slot path keeps the inode
        except OSError:
            pass


def acquire(root, *, bound, lease_ms, wait_ms, poll_ms=50):
    """Claim one of `bound` in-flight slots, or None if the plane stays
    saturated for the whole wait. Reaps expired leases each sweep, so a dead
    caller's slot frees itself. Returns an opaque handle for `release`."""
    slots_dir(root).mkdir(parents=True, exist_ok=True)
    lease_s = lease_ms / 1000.0
    deadline = time.monotonic() + wait_ms / 1000.0
    while True:
        for i in range(bound):
            handle = _try_claim(root, i, lease_s)
            if handle is not None:
                return handle
        if time.monotonic() >= deadline:
            return None
        time.sleep(poll_ms / 1000.0)


def release(handle):
    """Release a held slot. Verifies the token before unlinking, so a caller
    whose lease expired and whose slot was already reclaimed by another can
    never delete the new holder's slot. Idempotent and failure-safe."""
    if not handle:
        return
    path = handle.get("path")
    if path is None:
        return
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return  # already gone or torn — nothing of ours to release
    if data.get("token") != handle.get("token"):
        return  # reclaimed by another holder; not ours to delete
    if _is_stale(path):
        # our own lease has lapsed: the slot is the lease's to reclaim now,
        # not ours to delete. Unlinking here would race a stealer that claimed
        # it in the window between our token-read and this unlink, deleting the
        # NEW holder's slot. A lapsed holder has no right to mutate the slot;
        # the next acquire reaps it by lease. (When the lease is still valid no
        # steal can intervene, so the unlink below is safe.)
        return
    try:
        os.unlink(str(path))
    except OSError:
        pass


def live_inflight(root, *, bound=None):
    """How many slots are currently held by a live lease — the live in-flight
    count, a side read for the stats fold and surfaces. Stale slots do not
    count (they are reclaimable)."""
    d = slots_dir(root)
    if not d.exists():
        return 0
    now = time.time()
    n = 0
    for path in d.glob("slot-*.lock"):
        if not _is_stale(path, _now=now):
            n += 1
    return n


# ----------------------------------------------------------- the stats fold

def _percentile(sorted_vals, q):
    """Nearest-rank percentile over a sorted list (no numpy — stdlib only)."""
    if not sorted_vals:
        return None
    k = max(0, min(len(sorted_vals) - 1, int(round(q * (len(sorted_vals) - 1)))))
    return sorted_vals[k]


def stats(fold, *, root=None):
    """A read-only fold over the inference receipts: counts by outcome,
    per-mind latency (p50/p95 over the calls that actually ran), saturation
    events, and the live in-flight count. The receipts are the truth; this
    only reads them."""
    receipts = [r for r in fold.receipts if r.get("type") == "inference"]
    by_outcome = {}
    by_mind = {}
    for r in receipts:
        outcome = r.get("outcome") or "unknown"
        by_outcome[outcome] = by_outcome.get(outcome, 0) + 1
        mind = r.get("mind") or "(none)"
        m = by_mind.setdefault(mind, {"calls": 0, "ok": 0, "latencies": []})
        m["calls"] += 1
        if outcome == "ok":
            m["ok"] += 1
            lat = r.get("latency_ms")
            if isinstance(lat, (int, float)) and lat > 0:
                m["latencies"].append(int(lat))
    minds_out = {}
    for mind, m in sorted(by_mind.items()):
        lats = sorted(m["latencies"])
        minds_out[mind] = {
            "calls": m["calls"],
            "ok": m["ok"],
            "p50_ms": _percentile(lats, 0.50),
            "p95_ms": _percentile(lats, 0.95),
        }
    out = {
        "total_calls": len(receipts),
        "by_outcome": by_outcome,
        "saturated": by_outcome.get("saturated", 0),
        "by_mind": minds_out,
    }
    if root is not None:
        out["live_inflight"] = live_inflight(root)
    return out


# ------------------------------------------------------------------- CLI

def _render(st):
    lines = [f"inference plane — {st['total_calls']} call(s) on the record"]
    if "live_inflight" in st:
        lines.append(f"  in-flight now: {st['live_inflight']}")
    if st["by_outcome"]:
        parts = ", ".join(f"{k}:{v}" for k, v in sorted(st["by_outcome"].items()))
        lines.append(f"  outcomes: {parts}")
    if st["saturated"]:
        lines.append(f"  ⚠ saturated (backpressure refusals): {st['saturated']}")
    for mind, m in st["by_mind"].items():
        p50 = f"{m['p50_ms']}ms" if m["p50_ms"] is not None else "—"
        p95 = f"{m['p95_ms']}ms" if m["p95_ms"] is not None else "—"
        lines.append(f"  {mind}: {m['ok']}/{m['calls']} ok  p50 {p50}  p95 {p95}")
    return "\n".join(lines)


def cmd_stats(ns):
    root = Path(ns.root)
    fold = Fold(root)
    st = stats(fold, root=root)
    if ns.json:
        print(json.dumps(st, indent=2))
    else:
        print(_render(st))
        bound = concurrency_bound(fold)
        print(f"\nresult: report — bound {bound} in-flight "
              f"({'admitted' if any(a.get('type') == DIAL_TYPE for a in fold.admissions) else 'default'}); "
              "read-only fold over the receipts")
    return 0


def cmd_admit(ns):
    root = Path(ns.root)
    adm = set_bound(root, ns.bound, ns.by, ns.supersedes)
    if adm is None:
        print("result: needs-you — --bound must be a positive integer")
        return 2
    print(f"result: report — {adm['id']}: inference in-flight bound = "
          f"{adm['bound']} (by {ns.by})")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=str(DEFAULT_ROOT),
                    help="the .ai-native root (default the repo's)")
    sub = ap.add_subparsers(dest="cmd")

    st = sub.add_parser("stats", help="the read-only stats fold (default)")
    st.add_argument("--json", action="store_true", help="emit the raw dataset")
    st.set_defaults(func=cmd_stats)

    ad = sub.add_parser("admit", help="set the in-flight concurrency dial (bdo)")
    ad.add_argument("--bound", required=True, help="max completions in flight at once")
    ad.add_argument("--by", required=True, help="who admits the dial (bdo)")
    ad.add_argument("--supersedes", default=None, help="the prior dial id, if any")
    ad.set_defaults(func=cmd_admit)

    ns = ap.parse_args(argv)
    if not getattr(ns, "func", None):
        ns = ap.parse_args((argv or []) + ["stats"])
    return ns.func(ns)


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
