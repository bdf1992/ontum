"""Done-line 0025: the mind registry refuses.

The §10 case for pluggable minds: a mind is registered as a record (local the
default); a backing carrying a secret is refused (credentials referenced, not
stored); only bdo registers; an unknown family refuses; and a mind may not
judge its own backing's output (no one signs their own line, across an API).
The fold and refusals are pure; the write path runs against a temp log.
"""

import pathlib
import shutil
import tempfile
import unittest

from loop import minds
from loop.reconcile import Fold


class _TempLog(unittest.TestCase):
    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp())
        (self.root / "log").mkdir()
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)


class TestRegister(_TempLog):
    def test_register_a_local_mind(self):
        adm = minds.register(self.root, "local.llama-3.3-70b", "local",
                             "odysseus://localhost:8080/v1", "bdo")
        self.assertIsNotNone(adm)
        reg = minds.registered_minds(Fold(self.root))
        self.assertIn("local.llama-3.3-70b", reg)
        self.assertEqual(reg["local.llama-3.3-70b"]["family"], "local")

    def test_supersede_replaces_a_backing(self):
        first = minds.register(self.root, "local.m", "local", "odysseus://a", "bdo")
        minds.register(self.root, "local.m", "local", "odysseus://b", "bdo",
                       supersedes=first["id"])
        reg = minds.registered_minds(Fold(self.root))
        self.assertEqual(reg["local.m"]["backing"], "odysseus://b")


class TestRefusals(_TempLog):
    def test_inline_secret_backing_refused_and_writes_nothing(self):
        adm = minds.register(self.root, "external.gpt-5", "external",
                             "sk-abcdef0123456789abcdef0123456789", "bdo")
        self.assertIsNone(adm)
        self.assertEqual(minds.registered_minds(Fold(self.root)), {})

    def test_url_carrying_a_key_is_refused(self):
        self.assertIsNotNone(
            minds.backing_refusal("https://api.example.com/v1?api_key=shhh"))

    def test_reference_backings_pass(self):
        for ref in ("env:OPENAI_API_KEY", "profile:work",
                    "https://api.example.com/v1", "odysseus://localhost:8080/v1"):
            self.assertIsNone(minds.backing_refusal(ref), ref)

    def test_only_bdo_registers(self):
        self.assertIsNotNone(minds.mind_refusal("local.m", "local", "env:X", "claude"))
        self.assertIsNone(minds.mind_refusal("local.m", "local", "env:X", "bdo"))

    def test_unknown_family_and_unnamespaced_id_refuse(self):
        self.assertIsNotNone(minds.mind_refusal("weird.m", "quantum", "env:X", "bdo"))
        self.assertIsNotNone(minds.mind_refusal("nonamespace", "local", "env:X", "bdo"))


class TestNoSelfSign(unittest.TestCase):
    def test_a_mind_may_not_judge_its_own_output(self):
        reason = minds.judge_refusal("local.m", "local.m")
        self.assertIsNotNone(reason)
        self.assertIn("own backing", reason)

    def test_a_different_mind_may_judge(self):
        self.assertIsNone(minds.judge_refusal("local.m", "external.gpt-5"))


if __name__ == "__main__":
    unittest.main()
