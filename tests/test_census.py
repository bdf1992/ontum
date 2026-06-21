"""Tests for the part census (done-line 0029): the loop sensing its own
body. The census is a pure fold over two signals — wired (reachable from
the working system, not the part's own test) and exercised (a controlled
literal of the part's is on the record). The §10 case is the whole point:
four parts that are each *locally fine* (real files, plausible code) must
land in distinct verdicts, and the lens must catch the dormant one — a
census that calls everything alive (or everything dead) is doing nothing.

The false positive this guards against is real and was found in the live
run: a generic word ("local") shared between a source literal and a raw
captured command forged a trace and hid a dormant part. The vocabulary
must be controlled fields only — no prose, no raw capture."""

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import census


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_repo(tmp):
    """A miniature repo with one part of each kind we want to prove.

      scribe   — writer whose literal is on the record   -> alive
      plumbed  — writer, imported by live code, no record -> wired·idle
      viewer   — reader, imported by live code, no record -> alive (silent)
      ghost    — neither imported nor an entrypoint nor on record -> dormant
    """
    root = Path(tmp)
    write(root / "loop" / "__init__.py", "")

    # exercised writer: speaks "scribe.happened", which the log holds
    write(root / "loop" / "scribe.py",
          'from loop.reconcile import append_line\n'
          'EVENT = "scribe.happened"\n'
          'def run(): append_line("x", {"type": EVENT})\n')

    # wired writer, never fired: speaks "plumbed.never", absent from the log
    write(root / "loop" / "plumbed.py",
          'from loop.reconcile import append_line\n'
          'KIND = "plumbed.never"\n'
          'def run(): append_line("x", {"type": KIND})\n')

    # wired reader: no append, no .jsonl — silent by design is fine
    write(root / "loop" / "viewer.py",
          'def render(rows):\n'
          '    return "\\n".join(str(r) for r in rows)\n')

    # ghost: not imported, no __main__, no recorded word — dead code
    write(root / "loop" / "ghost.py",
          'GREETING = "ghost.unheard"\n'
          'def greet(): return GREETING\n')

    # the working system: imports plumbed and viewer (wires them), and a
    # placeholder reconcile so the imports above are not dangling
    write(root / "loop" / "reconcile.py",
          'def append_line(path, rec): pass\n')
    write(root / "loop" / "live.py",
          'from loop import plumbed, viewer\n'
          'def go(): plumbed.run(); viewer.render([])\n')

    # the record: only scribe's word has ever flowed. The reason carries
    # "ghost" and "plumbed" as prose — the controlled-field fold must NOT
    # let that forge a trace (the live-run false positive, in miniature).
    log = root / ".ai-native" / "log"
    log.mkdir(parents=True)
    write(log / "events.jsonl",
          json.dumps({"type": "scribe.happened", "id": "evt.1",
                      "reason": "the ghost is plumbed but unheard"}) + "\n")
    write(log / "receipts.jsonl", "")
    write(log / "admissions.jsonl", "")
    return root


class CensusVerdicts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = make_repo(self.tmp)
        self.by_name = {r["name"]: r for r in census.census(self.root)}

    def verdict(self, name):
        return self.by_name[name]["verdict"]

    def test_exercised_writer_is_alive(self):
        self.assertEqual(self.verdict("scribe"), "alive")
        self.assertIn("scribe.happened", self.by_name["scribe"]["traces"])

    def test_wired_writer_with_no_record_is_idle(self):
        self.assertEqual(self.verdict("plumbed"), "wired·idle")
        self.assertTrue(self.by_name["plumbed"]["writer"])
        self.assertFalse(self.by_name["plumbed"]["exercised"])

    def test_wired_reader_is_alive_silent(self):
        self.assertEqual(self.verdict("viewer"), "alive")
        self.assertFalse(self.by_name["viewer"]["exercised"])
        self.assertFalse(self.by_name["viewer"]["writer"])

    def test_disconnected_organ_is_dormant(self):
        self.assertEqual(self.verdict("ghost"), "dormant")

    def test_prose_in_a_reason_forges_no_trace(self):
        # "ghost" and "plumbed" appear in a free-text reason; neither may
        # become a recorded trace. This is the live false positive, caught.
        self.assertFalse(self.by_name["ghost"]["exercised"])
        self.assertFalse(self.by_name["plumbed"]["exercised"])

    def test_the_lens_discriminates(self):
        # the §10 guard: not everything alive, not everything dead
        verdicts = {r["verdict"] for r in self.by_name.values()}
        self.assertGreaterEqual(len(verdicts), 3,
                                f"census collapsed to {verdicts}; it isn't sensing")

    def test_render_is_read_only_and_reports(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = census.render(list(self.by_name.values()))
        out = buf.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("result: report", out)
        self.assertIn("dormant", out)


if __name__ == "__main__":
    unittest.main()
