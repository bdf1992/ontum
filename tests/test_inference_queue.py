"""Done-line 0149: the inference admission queue has teeth.

The §10 bar is that a *locally-fine* thing refuses to fit and the mechanism
notices. Here the locally-fine thing is "one more completion" — each request is
fine alone; the bound is what makes the (N+1)th refuse to fit:

  - the bound BITES: with bound=1 a second concurrent acquire is refused, and a
    fabricated "infinite bound" would let it through (the check is not vacuous).
  - a slot self-heals: a hard-killed caller's slot (its lease expired) is
    reclaimed by the next acquire — the substrate's mortality property, here for
    the semaphore; a non-leased lock would deadlock forever.
  - release is token-guarded: a caller whose lease expired and whose slot was
    stolen cannot delete the live holder's slot.
  - the dial is an admitted record, not a constant: setting it changes the
    bound a fold reads; the default holds when unset.
  - the gateway witnesses backpressure: a saturated plane yields a `saturated`
    receipt (proven against an in-process fake server with the bound pre-held),
    and the stats fold counts it.

Stdlib unittest + tempfile only; the transport teeth use an in-process fake
OpenAI server (no model needed), matching tests/test_gateway.py.
"""

import http.server
import importlib.util
import json
import multiprocessing
import os
import pathlib
import random
import tempfile
import threading
import time
import unittest

from loop import inference, inference_queue as q, minds
from loop.reconcile import Fold

REPO = pathlib.Path(__file__).resolve().parents[1]


def _load_gateway():
    path = REPO / ".claude" / "skills" / "gateway" / "gateway.py"
    spec = importlib.util.spec_from_file_location("gateway_pen_q", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gateway = _load_gateway()


def _make_root():
    """A throwaway .ai-native with the three log files, like the rest of the
    suite. Returns the root path."""
    root = pathlib.Path(tempfile.mkdtemp()) / ".ai-native"
    (root / "log").mkdir(parents=True)
    for name in ("events.jsonl", "receipts.jsonl", "admissions.jsonl"):
        (root / "log" / name).write_text("", encoding="utf-8")
    return root


def _concurrency_worker(args):
    """One real worker PROCESS: repeatedly claim a slot, and while holding it
    drop a marker file then count how many markers exist — a DIRECT, clock-free
    count of concurrent holders (sound across processes, unlike comparing
    per-process clocks). Returns (peak_seen, refusals, [error_names]). Must be a
    module-level function so the spawn start method can pickle it."""
    root, markers, bound, n, wait_ms, seed = args
    random.seed(seed)
    root, markers = pathlib.Path(root), pathlib.Path(markers)
    peak, refusals, errors = 0, 0, []
    for k in range(n):
        try:
            h = q.acquire(root, bound=bound, lease_ms=30000, wait_ms=wait_ms, poll_ms=3)
        except Exception as e:        # an acquire must never raise (Windows file-locking, etc.)
            errors.append(type(e).__name__); continue
        if h is None:
            refusals += 1; continue
        mk = markers / f"{os.getpid()}-{k}"
        try:
            mk.write_text("x")
            peak = max(peak, len(list(markers.iterdir())))  # holders present right now
            time.sleep(random.uniform(0.03, 0.06))          # hold long enough to overlap
        finally:
            try:
                mk.unlink()
            except OSError:
                pass
            try:
                q.release(h)
            except Exception as e:
                errors.append(type(e).__name__)
    return peak, refusals, errors


class TestConcurrencyUnderRealParallelism(unittest.TestCase):
    """The §10 gate whose absence let a real bound violation land. The
    sequential tests above exercise the LOGIC; they cannot exercise the
    cross-process race. A non-atomic create-then-write let a concurrent reader
    see a freshly-created (still-empty) slot, judge it `stale`, and double-claim
    it — a stress test measured 6 holders on a bound of 3, and 2 on a bound of
    1, plus Windows PermissionErrors. The claim is now atomic-with-content
    (`os.link`). This test spawns REAL parallel processes and asserts the bound
    holds and no acquire/release ever raises."""

    def test_bound_holds_under_real_parallel_contention(self):
        bound, workers, cycles, wait_ms = 2, 8, 8, 2000
        root = pathlib.Path(tempfile.mkdtemp())
        markers = pathlib.Path(tempfile.mkdtemp())
        args = [(str(root), str(markers), bound, cycles, wait_ms, i)
                for i in range(workers)]
        ctx = multiprocessing.get_context("spawn")  # the cross-platform start method
        with ctx.Pool(workers) as pool:
            results = pool.map(_concurrency_worker, args)
        peak = max(p for p, _, _ in results)
        errors = [e for _, _, errs in results for e in errs]
        self.assertEqual(errors, [],
                         f"acquire/release raised under contention: {errors}")
        self.assertLessEqual(
            peak, bound,
            f"BOUND VIOLATED: {peak} concurrent holders on a bound of {bound} "
            "— the create-then-write race is back")
        # not vacuous: the run must have actually exercised concurrency, else it
        # proves nothing. With 8 workers on bound=2 and a generous wait, real
        # overlap is expected.
        self.assertGreaterEqual(
            peak, 2, "the test did not exercise real concurrency (vacuous)")


class TestTheBoundBites(unittest.TestCase):
    def setUp(self):
        self.root = _make_root()

    def test_second_concurrent_acquire_is_refused(self):
        h1 = q.acquire(self.root, bound=1, lease_ms=60000, wait_ms=80)
        self.assertIsNotNone(h1, "the first acquire must win")
        h2 = q.acquire(self.root, bound=1, lease_ms=60000, wait_ms=80)
        self.assertIsNone(h2, "the bound must REFUSE the second concurrent acquire")
        self.assertEqual(q.live_inflight(self.root), 1)

    def test_check_is_not_vacuous_a_wider_bound_admits_more(self):
        # the same two requests that refuse to fit at bound=1 fit at bound=2 —
        # so the refusal above is the bound biting, not acquire always failing.
        h1 = q.acquire(self.root, bound=2, lease_ms=60000, wait_ms=80)
        h2 = q.acquire(self.root, bound=2, lease_ms=60000, wait_ms=80)
        self.assertIsNotNone(h1)
        self.assertIsNotNone(h2, "a wider bound must admit the second — not vacuous")
        h3 = q.acquire(self.root, bound=2, lease_ms=60000, wait_ms=80)
        self.assertIsNone(h3, "and bound=2 still refuses the third")

    def test_release_frees_a_slot(self):
        h1 = q.acquire(self.root, bound=1, lease_ms=60000, wait_ms=80)
        q.release(h1)
        h2 = q.acquire(self.root, bound=1, lease_ms=60000, wait_ms=80)
        self.assertIsNotNone(h2, "a released slot must be re-acquirable")


class TestLeaseSelfHeals(unittest.TestCase):
    def setUp(self):
        self.root = _make_root()

    def test_expired_lease_is_reclaimed(self):
        # a hard-killed caller leaves a slot it never releases. Its lease
        # expires; the next acquire must reclaim it (no deadlock).
        dead = q.acquire(self.root, bound=1, lease_ms=60, wait_ms=80)
        self.assertIsNotNone(dead)
        time.sleep(0.15)  # the lease (60ms) lapses
        live = q.acquire(self.root, bound=1, lease_ms=60000, wait_ms=300)
        self.assertIsNotNone(live, "an expired lease must self-heal, not deadlock")

    def test_stale_holders_release_cannot_steal_the_live_slot(self):
        dead = q.acquire(self.root, bound=1, lease_ms=60, wait_ms=80)
        time.sleep(0.15)
        live = q.acquire(self.root, bound=1, lease_ms=60000, wait_ms=300)
        q.release(dead)  # the overdue caller finally returns and releases
        self.assertEqual(q.live_inflight(self.root), 1,
                         "a stale holder must not delete the live holder's slot")
        # and the live holder can still release its own slot
        q.release(live)
        self.assertEqual(q.live_inflight(self.root), 0)


class TestTheDialIsAdmitted(unittest.TestCase):
    def setUp(self):
        self.root = _make_root()

    def test_default_when_unset_then_the_admitted_bound_wins(self):
        fold = Fold(self.root)
        self.assertEqual(q.concurrency_bound(fold), q.DEFAULT_BOUND,
                         "unset, the bound is the safe default, not zero")
        adm = q.set_bound(self.root, 5, by="test-bdo")
        self.assertIsNotNone(adm)
        self.assertEqual(q.concurrency_bound(Fold(self.root)), 5,
                         "an admitted dial is read from the log, not a constant")

    def test_superseding_dial_moves_the_bound(self):
        a1 = q.set_bound(self.root, 4, by="test-bdo")
        q.set_bound(self.root, 1, by="test-bdo", supersedes=a1["id"])
        self.assertEqual(q.concurrency_bound(Fold(self.root)), 1,
                         "the superseding dial wins; history is not erased")

    def test_a_non_positive_bound_is_refused(self):
        self.assertIsNone(q.set_bound(self.root, 0, by="test-bdo"))
        self.assertIsNone(q.set_bound(self.root, "two", by="test-bdo"))


# --- the gateway witnesses backpressure (in-process fake server) ------------

class _FakeOpenAI(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):  # quiet
        pass

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        self.rfile.read(n)
        body = json.dumps({
            "choices": [{"message": {"content": "ok"}}],
            "usage": {"total_tokens": 3},
        }).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class TestGatewaySaturation(unittest.TestCase):
    def setUp(self):
        self.root = _make_root()
        self.srv = http.server.HTTPServer(("127.0.0.1", 0), _FakeOpenAI)
        self.port = self.srv.server_address[1]
        self.t = threading.Thread(target=self.srv.serve_forever, daemon=True)
        self.t.start()
        base = f"http://127.0.0.1:{self.port}"
        # minds/routes/policies are bdo-governed config (D-4) — they require
        # the owner's signature, matching tests/test_gateway.py.
        minds.register(self.root, "local.fake", "local", base, "bdo",
                       model="fake-model")
        inference.set_route(self.root, "default", ["local.fake"], "bdo")
        inference.set_policy(self.root, "tester", "chat", "local.fake", True, "bdo")
        q.set_bound(self.root, 1, by="test-bdo")

    def tearDown(self):
        self.srv.shutdown()
        self.srv.server_close()

    def test_saturated_plane_yields_a_witnessed_saturated_receipt(self):
        # pre-hold the only slot, as a concurrent caller would, then call:
        held = q.acquire(self.root, bound=1, lease_ms=60000, wait_ms=80)
        self.assertIsNotNone(held)
        out = gateway.complete(
            "hi", caller="tester", surface="chat", route="default",
            root=str(self.root), by="test-bdo", timeout=5, queue_wait_ms=120)
        self.assertFalse(out["ok"], "a saturated plane must not complete")
        outcomes = [r["outcome"] for r in out["receipts"]]
        self.assertIn("saturated", outcomes,
                      "saturation must be a receipt on the record (witnessed)")
        # and the stats fold counts it
        st = q.stats(Fold(self.root), root=self.root)
        self.assertGreaterEqual(st["saturated"], 1)

    def test_with_a_free_slot_the_same_call_completes(self):
        # the not-vacuous twin: nothing pre-held, the call goes through —
        # so the refusal above was the bound, not a broken gateway.
        out = gateway.complete(
            "hi", caller="tester", surface="chat", route="default",
            root=str(self.root), by="test-bdo", timeout=5, queue_wait_ms=120)
        self.assertTrue(out["ok"], "with a free slot the completion lands")
        self.assertEqual(q.live_inflight(self.root), 0,
                         "the slot is released after the completion")


if __name__ == "__main__":
    unittest.main()
