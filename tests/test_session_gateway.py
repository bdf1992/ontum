"""Tests for the session gateway — bind-at-birth (done-line 0195, issue #534).

The §10 cases are the point, and they are two locally-fine things refusing to
fit:

  (a) the PORTAL teeth — a tool whose required capability is NOT in a type's set
      is ABSENT from that type's emitted manifest, and a constant
      "all-tools-authorized" classifier (the gauge-not-a-gate failure) is CAUGHT:
      it would let the absent tool through, so it differs from the real filter.

  (b) the IDEMPOTENCE teeth — a session that already has a binding is REUSED,
      never blind-recreated (the rescue-branch-sprawl bug §4/§14 names). Binding
      twice writes ONE record, not two.

Plus the typing function's purity/versioning and the governed-vocabulary
capability extension (the tags.py shape)."""

import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import session_gateway as sg
from loop.reconcile import Fold


def make_root(tmp):
    root = Path(tmp) / ".ai-native"
    (root / "log").mkdir(parents=True)
    for f in ("events.jsonl", "receipts.jsonl", "admissions.jsonl"):
        (root / "log" / f).write_text("", encoding="utf-8")
    return root


class DeriveType(unittest.TestCase):
    """The typing function is PURE, named, versioned, with an honest floor."""

    def test_branded_node_spawn_is_node_fill(self):
        self.assertEqual(sg.derive_type({"brand": "ontum-node:value-gate.v1"}),
                         sg.NODE_FILL)
        # the brand can arrive under any of the carrier fields
        self.assertEqual(sg.derive_type({"node": "ontum-node:x"}), sg.NODE_FILL)

    def test_worktree_cwd_is_builder(self):
        cwd = r"C:\Users\bdf19\ontum\.claude\worktrees\agent-abc"
        self.assertEqual(sg.derive_type({"cwd": cwd}), sg.BUILDER)

    def test_confirmed_viewport_is_steerer_admin(self):
        primary = r"C:\Users\bdf19\ontum"
        self.assertEqual(
            sg.derive_type({"cwd": primary, "primary": primary}), sg.STEERER_ADMIN)

    def test_fallback_is_least_privilege_builder(self):
        # no usable signal -> builder (never steerer; we never hand viewport
        # powers to a tree we cannot confirm is the viewport)
        self.assertEqual(sg.derive_type({}), sg.BUILDER)
        self.assertEqual(sg.derive_type(None), sg.BUILDER)
        # an off-primary tree with no primary supplied still reads builder, never
        # steerer-admin (under-, never over-privileging)
        self.assertEqual(sg.derive_type({"cwd": "/some/other/tree"}), sg.BUILDER)

    def test_pure_ignores_process_state(self):
        # non-vacuous purity: the SAME payload must derive the SAME type even
        # when the process cwd changes between calls — a derive_type that read
        # os.getcwd() (instead of payload['cwd']) would diverge here.
        import os
        payload = {"cwd": "/x/.claude/worktrees/y"}
        here = os.getcwd()
        try:
            first = sg.derive_type(dict(payload))
            os.chdir(tempfile.mkdtemp())
            second = sg.derive_type(dict(payload))
        finally:
            os.chdir(here)
        self.assertEqual(first, second)
        self.assertEqual(first, sg.BUILDER)

    def test_typing_version_is_named(self):
        self.assertTrue(sg.TYPING_VERSION)


class Capabilities(unittest.TestCase):
    """Governed vocabulary: a closed core per type plus admitted extensions."""

    def setUp(self):
        self.root = make_root(tempfile.mkdtemp())

    def test_core_is_the_spine(self):
        fold = Fold(self.root)
        self.assertEqual(sg.type_capabilities(fold, sg.BUILDER), {sg.READ, sg.BUILD})
        self.assertEqual(sg.type_capabilities(fold, sg.NODE_FILL), {sg.READ, sg.JUDGE})
        self.assertEqual(sg.type_capabilities(fold, sg.STEERER_ADMIN),
                         {sg.READ, sg.STEER})

    def test_no_default_type_lands_its_own_line(self):
        # `land` (the merge-node's seat) is in no default type by design (D-2)
        fold = Fold(self.root)
        for t in sg.SESSION_TYPES:
            self.assertNotIn(sg.LAND, sg.type_capabilities(fold, t))

    def test_admitted_extension_then_withdraw(self):
        self.assertEqual(sg.capability_status(Fold(self.root), sg.NODE_FILL, sg.BUILD),
                         "absent")
        sg.admit_capability(self.root, sg.NODE_FILL, sg.BUILD, by="bdo")
        self.assertEqual(sg.capability_status(Fold(self.root), sg.NODE_FILL, sg.BUILD),
                         "admitted")
        self.assertIn(sg.BUILD, sg.type_capabilities(Fold(self.root), sg.NODE_FILL))
        sg.admit_capability(self.root, sg.NODE_FILL, sg.BUILD, by="bdo", withdrawn=True)
        self.assertEqual(sg.capability_status(Fold(self.root), sg.NODE_FILL, sg.BUILD),
                         "absent")

    def test_withdrawing_a_core_capability_is_refused(self):
        # a core capability is closed in code; admit-capability --withdraw on it
        # must REFUSE (not falsely report success) — the core is the spine and is
        # never retro-invalidated. build is core for builder.
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = sg.main(["admit-capability", "--root", str(self.root),
                            "--session-type", sg.BUILDER, "--capability", sg.BUILD,
                            "--withdraw", "--by", "bdo"])
        self.assertEqual(code, 2)
        self.assertIn("CORE capability", buf.getvalue())
        # and nothing was written: build is still core, no session_capability rec
        self.assertEqual(sg.capability_status(Fold(self.root), sg.BUILDER, sg.BUILD),
                         "core")
        recs = [a for a in Fold(self.root).admissions
                if a.get("type") == "session_capability"]
        self.assertEqual(recs, [])


class PortalTeeth(unittest.TestCase):
    """(a) An absent capability means an absent portal; a constant classifier
    that authorizes everything is caught."""

    def _tools(self):
        # one tool per capability — a controlled corpus the filter must split
        return [
            {"tool": "reader", "kind": "pen", "ref": "loop/reader.py",
             "capability": sg.READ},
            {"tool": "judge-pen", "kind": "pen", "ref": "loop/judge.py",
             "capability": sg.JUDGE},
            {"tool": "land-pen", "kind": "pen", "ref": "loop/land.py",
             "capability": sg.LAND},
        ]

    def test_absent_capability_is_absent_portal(self):
        tools = self._tools()
        builder_caps = sg.TYPE_CAPABILITIES[sg.BUILDER]  # read, build (no judge)
        opened = {t["tool"] for t in sg.authorized_tools(tools, builder_caps)}
        self.assertIn("reader", opened)        # read is granted
        self.assertNotIn("judge-pen", opened)  # judge is NOT — absent portal
        self.assertNotIn("land-pen", opened)   # land is in no default type

    def test_constant_all_authorized_classifier_is_caught(self):
        # the gauge-not-a-gate failure: a classifier that returns every tool
        # regardless of capability. It must differ from the real filter — if
        # they agreed, the filter would be doing nothing (§10).
        tools = self._tools()
        caps = sg.TYPE_CAPABILITIES[sg.NODE_FILL]  # read, judge (no land)

        def constant_all_authorized(tools, capabilities):
            return list(tools)

        real = {t["tool"] for t in sg.authorized_tools(tools, caps)}
        fake = {t["tool"] for t in constant_all_authorized(tools, caps)}
        self.assertNotEqual(real, fake)
        self.assertIn("land-pen", fake)      # the constant lets it through
        self.assertNotIn("land-pen", real)   # the real filter does not

    def test_live_manifest_excludes_an_out_of_capability_tool(self):
        # ties the teeth to the real on-disk fold: a builder's emitted manifest
        # carries a read tool (census) and excludes a judge tool (the gate skill)
        root = make_root(tempfile.mkdtemp())
        binding, created = sg.bind(root, "sess-live", sg.BUILDER,
                                   str(REPO), by="test-bdo")
        self.assertTrue(created)
        _, data = sg.emit_manifest(binding, REPO, write=False)
        portals = {p["tool"] for p in data["portals"]}
        self.assertIn("census", portals)      # a read pen — universal
        self.assertNotIn("gate", portals)     # a judge skill — not a builder's
        self.assertNotIn("merge-node", portals)  # land — no default type's


class Idempotence(unittest.TestCase):
    """(b) A binding is never blind-recreated for a session that already has one."""

    def setUp(self):
        self.root = make_root(tempfile.mkdtemp())

    def test_second_bind_reuses_never_recreates(self):
        b1, created1 = sg.bind(self.root, "sess-1", sg.BUILDER, "/x", by="test-bdo")
        self.assertTrue(created1)
        b2, created2 = sg.bind(self.root, "sess-1", sg.BUILDER, "/x", by="test-bdo")
        self.assertFalse(created2)            # reused, not created
        self.assertEqual(b1["id"], b2["id"])  # the same binding handed back

        # and only ONE session_binding is on the log for this session
        fold = Fold(self.root)
        bindings = [a for a in fold.admissions
                    if a.get("type") == "session_binding"
                    and a.get("session_id") == "sess-1"]
        self.assertEqual(len(bindings), 1)

    def test_rebind_under_a_different_type_still_does_not_sprawl(self):
        # the sprawl bug would re-bind a re-typed session on every blink; the
        # floor refuses — the existing binding wins until superseded
        sg.bind(self.root, "sess-2", sg.BUILDER, "/x", by="test-bdo")
        b2, created = sg.bind(self.root, "sess-2", sg.NODE_FILL, "/x", by="test-bdo")
        self.assertFalse(created)
        self.assertEqual(b2["session_type"], sg.BUILDER)  # the first binding holds
        fold = Fold(self.root)
        bindings = [a for a in fold.admissions
                    if a.get("type") == "session_binding"
                    and a.get("session_id") == "sess-2"]
        self.assertEqual(len(bindings), 1)

    def test_binding_carries_the_three_As(self):
        b, _ = sg.bind(self.root, "sess-3", sg.NODE_FILL, "/work/here", by="test-bdo")
        self.assertEqual(b["session_id"], "sess-3")          # authenticated (who)
        self.assertEqual(b["session_type"], sg.NODE_FILL)    # authenticated (what)
        self.assertEqual(sorted(b["capabilities"]), [sg.JUDGE, sg.READ])  # authorized
        self.assertEqual(b["workspace"], "/work/here")       # attributed (where)
        self.assertEqual(b["by"], "test-bdo")                # attributed (by whom)
        self.assertEqual(b["typing_version"], sg.TYPING_VERSION)  # lineage
        self.assertTrue(b["ts"])

    def test_refusals(self):
        self.assertEqual(sg.bind(self.root, "", sg.BUILDER, "/x", by="bdo"),
                         (None, False))
        self.assertEqual(sg.bind(self.root, "s", "nonsense", "/x", by="bdo"),
                         (None, False))
        self.assertEqual(sg.bind(self.root, "s", sg.BUILDER, "/x", by=""),
                         (None, False))


if __name__ == "__main__":
    unittest.main()
