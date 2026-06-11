"""Tests for intent tags (done-line 0032): the governed tag pool, the one
shared classifier, the watcher's intent-split report, and the git pen's
mismatch-catch.

The §10 cases are the point. Two locally-fine declarations must be told
apart: `--intent read` on a commit is a *lie* (a known value that
contradicts the verb) and is refused; `--intent escalate` is a *proposal*
(a value outside the pool) and is accepted, flagged, never blocked. A
classifier that refused both, or accepted both, would be doing nothing.
And the report must rank a raw mutation above a raw read — the noise the
organ census caught (`gh pr list` ×65 read as 'wrap gh')."""

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import tags


def _load(name, relpath):
    spec = importlib.util.spec_from_file_location(name, REPO / relpath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


guard = _load("command_guard", ".claude/hooks/command_guard.py")
git_pen = _load("git_pen", ".claude/skills/branch-ritual/git.py")


def make_root(tmp):
    root = Path(tmp) / ".ai-native"
    (root / "log").mkdir(parents=True)
    for f in ("events.jsonl", "receipts.jsonl", "admissions.jsonl"):
        (root / "log" / f).write_text("", encoding="utf-8")
    return root


class Classifier(unittest.TestCase):
    def test_git_verbs(self):
        self.assertEqual(tags.classify("git commit -m x"), "mutate")
        self.assertEqual(tags.classify("git add foo.py"), "mutate")
        self.assertEqual(tags.classify("git push origin main"), "mutate")
        self.assertEqual(tags.classify("git status --porcelain"), "read")
        self.assertEqual(tags.classify("git log --oneline"), "read")

    def test_gh_reads_vs_mutations(self):
        self.assertEqual(tags.classify("gh pr list --state open"), "read")
        self.assertEqual(tags.classify("gh pr view 12"), "read")
        self.assertEqual(tags.classify("gh pr create --title x"), "mutate")
        self.assertEqual(tags.classify("gh issue close 3"), "mutate")

    def test_curl_method(self):
        self.assertEqual(tags.classify("curl https://x"), "read")
        self.assertEqual(tags.classify("curl -X POST https://x"), "mutate")
        self.assertEqual(tags.classify('curl -d "a=b" https://x'), "mutate")

    def test_unknown_is_none_not_guessed(self):
        self.assertIsNone(tags.classify("frobnicate the foo"))
        self.assertIsNone(tags.classify("git wibble"))
        self.assertIsNone(tags.classify(""))


class Pool(unittest.TestCase):
    def setUp(self):
        self.root = make_root(tempfile.mkdtemp())

    def test_core_is_the_spine(self):
        fold = tags.Fold(self.root)
        self.assertEqual(tags.status_of(fold, "intent", "mutate"), "core")
        self.assertEqual(tags.status_of(fold, "intent", "read"), "core")

    def test_proposed_then_admitted_then_withdrawn(self):
        fold = tags.Fold(self.root)
        self.assertEqual(tags.status_of(fold, "intent", "escalate"), "proposed")
        tags.admit_tag(self.root, "intent", "escalate", by="bdo")
        self.assertEqual(tags.status_of(tags.Fold(self.root), "intent", "escalate"),
                         "admitted")
        tags.admit_tag(self.root, "intent", "escalate", by="bdo", withdrawn=True)
        self.assertEqual(tags.status_of(tags.Fold(self.root), "intent", "escalate"),
                         "proposed")

    def test_admit_refuses_unknown_dimension(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = tags.main(["admit", "--root", str(self.root),
                              "--dimension", "nope", "--value", "x", "--by", "bdo"])
        self.assertEqual(code, 2)
        self.assertIn("unknown dimension", buf.getvalue())


class PenMismatchCatch(unittest.TestCase):
    """The §10 bite, on the git pen's pure refusal."""

    def test_lie_is_refused(self):
        # a known value contradicting the verb
        self.assertIsNotNone(
            git_pen.intent_refusal("mutate", "read", in_pool=True))

    def test_truth_passes(self):
        self.assertIsNone(git_pen.intent_refusal("mutate", "mutate", in_pool=True))

    def test_no_declaration_passes(self):
        self.assertIsNone(git_pen.intent_refusal("mutate", None, in_pool=False))

    def test_unknown_value_is_surfaced_not_swallowed(self):
        # an out-of-pool value is refused with the admit path — never
        # silently used (the smoke-test bug: 'escalate' staged quietly)
        reason = git_pen.intent_refusal("mutate", "escalate", in_pool=False)
        self.assertIsNotNone(reason)
        self.assertIn("loop.tags admit", reason)

    def test_known_value_contradicting_the_verb_is_a_lie(self):
        reason = git_pen.intent_refusal("mutate", "read", in_pool=True)
        self.assertIn("lies", reason)


class WatcherReport(unittest.TestCase):
    """The report must split raw mutations from raw reads — the census fix."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.log = self.tmp / "tool-use.jsonl"
        rows = [
            {"status": "watched", "bins": ["gh"], "intent": "read",
             "command": "gh pr list --state open"},
            {"status": "watched", "bins": ["gh"], "intent": "read",
             "command": "gh pr view 12"},
            {"status": "watched", "bins": ["deployer"], "intent": "mutate",
             "command": "deployer ship prod"},
            {"status": "branded", "intent": "mutate", "tool": "git", "verb": "commit"},
            {"status": "denied", "rule": "git-add", "command": "git add ."},
        ]
        self.log.write_text("\n".join(json.dumps(r) for r in rows) + "\n",
                            encoding="utf-8")
        self._saved = guard.WATCH_LOG
        guard.WATCH_LOG = self.log

    def tearDown(self):
        guard.WATCH_LOG = self._saved

    def test_report_nominates_the_mutation_not_the_read(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            guard.report()
        out = buf.getvalue()
        # the mutating tool is the wrapper candidate; gh (read) is not
        self.assertIn("deployer", out.split("raw reads")[0])  # under MUTATIONS
        self.assertIn("`deployer` is the next wrapper", out)
        self.assertIn("1 branded act", out)
        self.assertIn("1 denial", out)

    def test_classify_intent_uses_the_shared_classifier(self):
        self.assertEqual(guard.classify_intent("git commit -m x"), "mutate")
        self.assertEqual(guard.classify_intent("gh pr list"), "read")


if __name__ == "__main__":
    unittest.main()
