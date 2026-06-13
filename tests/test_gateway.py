"""Done-line 0062: the governed local inference plane has teeth.

The §10 test fails a faked plane many ways, and each way is a test here:

  - config-as-records: routes and policies are folds over the log; adding a
    backing or re-steering is one admitted record, NOT a code edit.
  - resolves any backing scheme -> one normalized OpenAI-compatible target.
  - RBAC default-deny: an unauthorized (caller, surface, mind) is REFUSED, no
    completion, a refused receipt; a deny wins over a permit; D-2's which-mind
    axis refuses a mind judging its own backing's output.
  - it thinks for real, with fallback: a real completion lands a receipt; a
    down/hung primary FALLS BACK by the route order to a live backing and
    receipts the fallback (the #95/#96 600s-hang made impossible); a constant
    is not a completion (the real call hits live weights, real latency/tokens).
  - no-bypass: the gateway is the sole sanctioned inference egress; gate.py's
    agentic `claude -p` is the single named legacy exception (its migration is
    atom.gate-through-gateway.v0); a NEW egress anywhere fails the guard.

The transport teeth (ok / fallback / refuse) run everywhere against an
in-process fake OpenAI server — deterministic, no model needed. The "thinks
for real" teeth run only where Ollama actually serves (skipped otherwise), so
the plane is proven against real weights on bdo's machine and the core teeth
still bite in a bare CI.
"""

import http.server
import importlib.util
import json
import pathlib
import re
import shutil
import socket
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

from loop import inference, minds
from loop.reconcile import Fold

REPO = pathlib.Path(__file__).resolve().parents[1]
OLLAMA = "http://localhost:11434"


def _load_gateway():
    path = REPO / ".claude" / "skills" / "gateway" / "gateway.py"
    spec = importlib.util.spec_from_file_location("gateway_pen", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gateway = _load_gateway()


def _ollama_up():
    try:
        with urllib.request.urlopen(OLLAMA + "/api/tags", timeout=2) as r:
            return r.status == 200
    except (urllib.error.URLError, socket.timeout, OSError):
        return False


def _ollama_models():
    try:
        with urllib.request.urlopen(OLLAMA + "/api/tags", timeout=3) as r:
            data = json.loads(r.read().decode("utf-8"))
        return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


class _FakeOpenAI(http.server.BaseHTTPRequestHandler):
    """A deterministic OpenAI-compatible completion endpoint. Echoes the model
    so a test can prove which backing answered, and reports tokens."""

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length).decode("utf-8")) if length else {}
        model = body.get("model", "?")
        out = json.dumps({
            "choices": [{"message": {"role": "assistant",
                                     "content": f"FAKE-ANSWER from {model}"}}],
            "usage": {"total_tokens": 11},
        }).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def log_message(self, *args):
        pass  # silent


class _TempLog(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp())
        (self.root / "log").mkdir()
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def _fake_server(self):
        srv = http.server.HTTPServer(("127.0.0.1", 0), _FakeOpenAI)
        t = threading.Thread(target=srv.serve_forever, daemon=True)
        t.start()
        self.addCleanup(srv.server_close)
        self.addCleanup(srv.shutdown)
        return f"http://127.0.0.1:{srv.server_address[1]}/v1"


# --------------------------------------------------------------- pure folds

class TestConfigPlaneIsRecords(_TempLog):
    def test_route_and_policy_are_folds_over_the_log(self):
        minds.register(self.root, "local.a", "local", "http://x/v1", "bdo")
        inference.set_route(self.root, "default", ["local.a"], "bdo")
        inference.set_policy(self.root, "*", "*", "*", True, "bdo")
        fold = Fold(self.root)
        self.assertEqual(inference.resolve_order(fold, "default"), ["local.a"])
        self.assertEqual(len(inference.policies(fold)), 1)

    def test_route_is_bdo_only_and_a_session_signer_writes_nothing(self):
        self.assertIsNotNone(inference.route_refusal("default", ["local.a"], "claude"))
        self.assertIsNone(inference.set_route(self.root, "default", ["local.a"], "claude"))
        self.assertEqual(inference.resolve_order(Fold(self.root)), [])

    def test_policy_is_bdo_only(self):
        self.assertIsNotNone(inference.policy_refusal("*", "*", "*", "claude"))
        self.assertIsNone(inference.policy_refusal("*", "*", "*", "bdo"))

    def test_supersede_re_steers_with_one_record(self):
        first = inference.set_route(self.root, "default", ["local.a"], "bdo")
        inference.set_route(self.root, "default", ["local.b", "local.a"], "bdo",
                            supersedes=first["id"])
        self.assertEqual(inference.resolve_order(Fold(self.root)),
                         ["local.b", "local.a"])


class TestAuthorize(_TempLog):
    def test_default_deny_no_policy_no_thought(self):
        permit, reason = inference.authorize(Fold(self.root), "x", "y", "local.a")
        self.assertFalse(permit)
        self.assertIn("default-deny", reason)

    def test_a_matching_permit_allows(self):
        inference.set_policy(self.root, "summoned-session", "chat", "local.a", True, "bdo")
        permit, _ = inference.authorize(Fold(self.root), "summoned-session", "chat", "local.a")
        self.assertTrue(permit)

    def test_a_deny_wins_over_a_permit(self):
        inference.set_policy(self.root, "*", "*", "*", True, "bdo")
        inference.set_policy(self.root, "intruder", "*", "*", False, "bdo")
        permit, _ = inference.authorize(Fold(self.root), "intruder", "chat", "local.a")
        self.assertFalse(permit)

    def test_which_mind_axis_refuses_self_judgement(self):
        inference.set_policy(self.root, "*", "*", "*", True, "bdo")
        permit, reason = inference.authorize(Fold(self.root), "c", "s", "local.a",
                                             writing_mind="local.a")
        self.assertFalse(permit)
        self.assertIn("own backing", reason)


class TestNormalizeBacking(unittest.TestCase):
    def test_each_scheme_resolves_to_an_http_target(self):
        self.assertEqual(inference.normalize_backing("http://h:1/v1", "m")["base_url"],
                         "http://h:1/v1")
        self.assertEqual(
            inference.normalize_backing("odysseus://h:8080", "m")["base_url"],
            "http://h:8080/v1")
        self.assertEqual(
            inference.normalize_backing("env:GW", "m", env={"GW": "http://e/v1"})["base_url"],
            "http://e/v1")
        self.assertEqual(
            inference.normalize_backing("profile:work", "m",
                                        env={"ONTUM_PROFILE_WORK": "http://p/v1"})["base_url"],
            "http://p/v1")

    def test_unresolvable_references_raise(self):
        for bad in ("", "ftp://x", "env:MISSING"):
            with self.assertRaises(ValueError):
                inference.normalize_backing(bad, "m", env={})


# --------------------------------------------- transport (fake server, no model)

class TestTransportAndFallback(_TempLog):
    def _permit_all(self):
        inference.set_policy(self.root, "*", "*", "*", True, "bdo")

    def test_a_completion_lands_exactly_one_ok_receipt(self):
        base = self._fake_server()
        minds.register(self.root, "local.fake", "local", base, "bdo", model="m1")
        inference.set_route(self.root, "default", ["local.fake"], "bdo")
        self._permit_all()
        out = gateway.complete("hello", caller="summoned-session", surface="chat",
                               root=self.root, timeout=10)
        self.assertTrue(out["ok"])
        self.assertIn("FAKE-ANSWER from m1", out["content"])
        self.assertEqual(len(out["receipts"]), 1)
        self.assertEqual(out["receipts"][0]["outcome"], "ok")

    def test_down_primary_falls_back_to_a_live_backing_and_receipts_it(self):
        live = self._fake_server()
        dead = "http://127.0.0.1:1/v1"  # nothing serves on port 1
        minds.register(self.root, "local.down", "local", dead, "bdo", model="d")
        minds.register(self.root, "local.up", "local", live, "bdo", model="u")
        inference.set_route(self.root, "default", ["local.down", "local.up"], "bdo")
        self._permit_all()
        out = gateway.complete("hi", caller="summoned-session", surface="chat",
                               root=self.root, timeout=5)
        self.assertTrue(out["ok"])
        self.assertEqual(out["mind"], "local.up")
        self.assertEqual([r["outcome"] for r in out["receipts"]], ["error", "ok"])
        self.assertEqual(out["receipts"][1]["fallback_from"], "local.down")

    def test_a_single_backing_stub_cannot_demonstrate_fallback(self):
        # the §10 teeth: with only one backing, a down primary has nowhere to
        # fall back — the call fails, proving the multi-backing order is real.
        dead = "http://127.0.0.1:1/v1"
        minds.register(self.root, "local.only", "local", dead, "bdo", model="d")
        inference.set_route(self.root, "default", ["local.only"], "bdo")
        self._permit_all()
        out = gateway.complete("hi", caller="s", surface="chat", root=self.root, timeout=5)
        self.assertFalse(out["ok"])
        self.assertEqual([r["outcome"] for r in out["receipts"]], ["error"])

    def test_unauthorized_caller_is_refused_with_no_completion(self):
        base = self._fake_server()
        minds.register(self.root, "local.fake", "local", base, "bdo", model="m1")
        inference.set_route(self.root, "default", ["local.fake"], "bdo")
        # no permit policy -> default-deny
        out = gateway.complete("secret", caller="intruder", surface="chat",
                               root=self.root, timeout=5)
        self.assertFalse(out["ok"])
        self.assertEqual(out["receipts"][0]["outcome"], "refused")

    def test_adding_a_backing_is_one_record_not_a_code_change(self):
        # prove the §10 "adding a backing via an admitted record resolves with
        # no code change": same gateway code, a new mind + re-route, it routes.
        first = self._fake_server()
        second = self._fake_server()
        minds.register(self.root, "local.first", "local", first, "bdo", model="one")
        inference.set_route(self.root, "default", ["local.first"], "bdo")
        self._permit_all()
        out1 = gateway.complete("a", caller="s", surface="chat", root=self.root, timeout=10)
        self.assertEqual(out1["mind"], "local.first")
        # add a backing and re-steer — records only, not a line of code:
        r = Fold(self.root)
        route_id = inference.routes(r)["default"]["id"]
        minds.register(self.root, "local.second", "local", second, "bdo", model="two")
        inference.set_route(self.root, "default", ["local.second", "local.first"],
                            "bdo", supersedes=route_id)
        out2 = gateway.complete("b", caller="s", surface="chat", root=self.root, timeout=10)
        self.assertEqual(out2["mind"], "local.second")


# --------------------------------------------- it thinks for real (live Ollama)

@unittest.skipUnless(_ollama_up(), "Ollama not serving at :11434 — live teeth skipped")
class TestThinksForReal(_TempLog):
    def _two_live_models(self):
        models = _ollama_models()
        prefer = [m for m in ("qwen3:4b", "mistral:latest", "qwen3:14b", "gpt-oss:20b")
                  if m in models]
        if len(prefer) < 2:
            self.skipTest(f"need >=2 served models, have {models}")
        return prefer[0], prefer[1]

    def test_a_real_completion_through_two_distinct_live_backings(self):
        m1, m2 = self._two_live_models()
        base = OLLAMA + "/v1"
        minds.register(self.root, "local.one", "local", base, "bdo", model=m1)
        minds.register(self.root, "local.two", "local", base, "bdo", model=m2)
        inference.set_policy(self.root, "*", "*", "*", True, "bdo")
        for mind_id, model in (("local.one", m1), ("local.two", m2)):
            inference.set_route(self.root, "default", [mind_id], "bdo",
                                supersedes=inference.routes(Fold(self.root)).get("default", {}).get("id"))
            out = gateway.complete("Reply with only the word: ok",
                                   caller="summoned-session", surface="chat",
                                   root=self.root, timeout=180)
            self.assertTrue(out["ok"], f"{model}: {out['reason']}")
            self.assertTrue(out["content"].strip(), f"{model} returned empty")
            rcp = out["receipts"][-1]
            self.assertEqual(rcp["outcome"], "ok")
            self.assertGreater(rcp["latency_ms"], 0)  # a real call took real time

    def test_real_fallback_from_a_down_primary_to_live_ollama(self):
        m1, _ = self._two_live_models()
        minds.register(self.root, "local.dead", "local", "http://127.0.0.1:1/v1",
                       "bdo", model="x")
        minds.register(self.root, "local.live", "local", OLLAMA + "/v1", "bdo", model=m1)
        inference.set_route(self.root, "default", ["local.dead", "local.live"], "bdo")
        inference.set_policy(self.root, "*", "*", "*", True, "bdo")
        out = gateway.complete("Reply with only the word: ok",
                               caller="summoned-session", surface="chat",
                               root=self.root, timeout=180)
        self.assertTrue(out["ok"])
        self.assertEqual(out["mind"], "local.live")
        self.assertEqual(out["receipts"][0]["outcome"], "error")
        self.assertEqual(out["receipts"][-1]["fallback_from"], "local.dead")


# --------------------------------------------------------------- no-bypass

class TestNoBypass(unittest.TestCase):
    """0062 piece 6: the gateway is the sole sanctioned inference egress. The
    one legacy exception is the gate pen's agentic `claude -p`, whose migration
    is atom.gate-through-gateway.v0. A NEW egress anywhere else fails this — RBAC
    without no-bypass is theatre (authorizing the front door while a back door
    stays open)."""

    HTTP_EGRESS = re.compile(r"/chat/completions|/api/generate")
    CLAUDE_P = re.compile(r"""claude["']\s*,\s*["']-p""")

    ALLOWED = {".claude/skills/gateway/gateway.py"}      # the sole sanctioned path
    LEGACY = {".claude/skills/gate/gate.py"}             # the one named exception

    def _scan(self):
        roots = [REPO / "loop", REPO / ".claude" / "skills", REPO / ".claude" / "hooks"]
        hits = {}
        for base in roots:
            for p in base.rglob("*.py"):
                rel = p.relative_to(REPO).as_posix()
                text = p.read_text(encoding="utf-8", errors="ignore")
                if self.HTTP_EGRESS.search(text) or self.CLAUDE_P.search(text):
                    hits[rel] = True
        return set(hits)

    def test_no_inference_egress_outside_the_gateway_and_the_named_legacy(self):
        egress = self._scan()
        rogue = egress - self.ALLOWED - self.LEGACY
        self.assertEqual(rogue, set(),
                         f"new inference egress outside the gateway: {rogue} — "
                         "route it through the gateway pen (no-bypass, 0062)")

    def test_the_gateway_is_actually_an_egress(self):
        # guard against the guard rotting: the allowed path must really egress.
        self.assertIn(".claude/skills/gateway/gateway.py", self._scan())

    def test_the_named_legacy_is_still_the_gate(self):
        # honesty: if gate.py stops bypassing (gate-through-gateway lands), the
        # LEGACY exception must be retired, not left as a silent allowance.
        self.assertIn(".claude/skills/gate/gate.py", self._scan())


if __name__ == "__main__":
    unittest.main()
