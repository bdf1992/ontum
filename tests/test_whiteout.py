"""Tests for the Whiteout pen against done-line 0064: a marked, recoverable
correction that refuses what's been consumed.

Whiteout is correction fluid for the log. It LEAVES A MARK (a superseding
append, never an edit), you can STILL SEE UNDER IT (the original stays on the
append-only log), and it does NOT work on HUGE mistakes (a target anything
downstream has consumed is un-whiteoutable — that needs a retro or bdo's hand).

The §10 bar lives here, hit directly: two locally-fine corrections the one
verb must tell apart — a small, UNCONSUMED mistake is corrected and the
original stays readable under the mark; a CONSUMED target (a later record
cites it) refuses to fit and names where it must go instead; and softening a
frozen done-line's bar stays bdo's supersede, never a whiteout. The refusals
are asserted over the log files themselves (nothing written), never internals.
"""

import io
import contextlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import pen, reconcile
from loop.reconcile import append_line, Fold, TERMINAL_EVENT

DONE_CFG = REPO / ".ai-native" / "done" / ".pen.json"
SKELETON_ATOM = REPO / ".ai-native" / "atoms" / "atom.loop-skeleton.v0.json"


def make_root(tmp):
    """A throwaway .ai-native root with an empty log/ — records are appended
    line by line, the way the loop writes them (D-5: assert over the files)."""
    root = Path(tmp) / ".ai-native"
    (root / "log").mkdir(parents=True)
    return root


def make_field_root(tmp):
    """A throwaway root carrying the real loop-skeleton atom, so the verifier's
    repro can be driven through `reconcile.pass_once` rather than hand-faked:
    the loop itself derives the value-gate receipt and the value.accepted event
    it implies (D-5 — exercise the real fold, not a guessed log shape)."""
    base = Path(tmp) / "field"
    base.mkdir(parents=True, exist_ok=True)
    root = make_root(base)
    (root / "atoms").mkdir(parents=True)
    shutil.copy(SKELETON_ATOM, root / "atoms" / SKELETON_ATOM.name)
    return root


def read_jsonl(path):
    if not path.exists():
        return []
    return [json.loads(line) for line in
            path.read_text(encoding="utf-8").splitlines() if line.strip()]


def run(*argv):
    """Drive the pen function, capturing stdout and the exit code."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = pen.main(list(argv))
    return code, out.getvalue()


class WhiteoutTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.root = make_root(self.tmp)
        self.events = self.root / "log" / "events.jsonl"
        self.receipts = self.root / "log" / "receipts.jsonl"
        self.adms = self.root / "log" / "admissions.jsonl"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # --- the happy tooth: a small, unconsumed mistake is corrected ----------
    def test_unconsumed_mistake_corrected_and_original_readable_underneath(self):
        # an ordinary log record with a mistake in it, that nothing cites
        original = {"id": "evt.mistake1", "type": "note.recorded",
                    "artifact_hash": "sha256:lonely",
                    "text": "the budget is 30 (typo)"}
        append_line(self.events, original)

        code, msg = run("whiteout", "--root", str(self.root),
                        "--target", "evt.mistake1",
                        "--correction", "the budget is 3, not 30 — a typo",
                        "--reason", "fat-fingered the setpoint in the note",
                        "--by", "test-session")
        self.assertEqual(code, 0, msg)

        # the correction is a single appended admission — never an edit
        adms = read_jsonl(self.adms)
        whiteouts = [a for a in adms if a.get("type") == "whiteout"]
        self.assertEqual(len(whiteouts), 1)
        wo = whiteouts[0]
        self.assertEqual(wo["target"], "evt.mistake1")
        self.assertIn("not 30", wo["correction"])
        self.assertEqual(wo["covered"], original)  # the mark carries the story

        # SEE UNDER IT: the original line is still on the events stream, byte
        # for byte unchanged — nothing was erased
        still_there = [e for e in read_jsonl(self.events) if e["id"] == "evt.mistake1"]
        self.assertEqual(still_there, [original])

        # the fold honours the correction as the default view (now/covered/why)
        view = pen.effective_record(Fold(self.root), "evt.mistake1")
        self.assertTrue(view["marked"])
        self.assertIn("not 30", view["now"])           # the correction is now
        self.assertEqual(view["covered"], original)    # the original underneath
        self.assertIn("fat-fingered", view["why"])

    # --- the refusal tooth: a consumed target will not fit ------------------
    def test_consumed_target_refuses_and_writes_nothing(self):
        # an event, then a receipt that CITES it (event_id) — downstream has
        # consumed it, exactly as the pipeline references a judged event
        ev = {"id": "evt.judged", "type": "value.gate",
              "artifact_hash": "sha256:consumed"}
        rc = {"id": "rcp.onit", "event_id": "evt.judged", "node": "value-gate",
              "artifact_hash": "sha256:consumed", "verdict": "accept"}
        append_line(self.events, ev)
        append_line(self.receipts, rc)

        code, msg = run("whiteout", "--root", str(self.root),
                        "--target", "evt.judged",
                        "--correction", "actually it was a reject",
                        "--reason", "I want to rewrite the verdict",
                        "--by", "test-session")
        self.assertEqual(code, 2)
        self.assertIn("consumed", msg)
        self.assertIn("rcp.onit", msg)          # names the citer
        self.assertIn("retro", msg)             # names the escalation
        self.assertIn("supersede", msg)
        # nothing written: no whiteout admission landed
        self.assertEqual([a for a in read_jsonl(self.adms)
                          if a.get("type") == "whiteout"], [])

    # --- a target whose atom already landed/confirmed is also un-whiteoutable
    def test_terminal_atom_refuses(self):
        early = {"id": "rcp.early", "node": "value-gate",
                 "artifact_hash": "sha256:done", "verdict": "accept"}
        terminal = {"id": "evt.confirmed", "type": TERMINAL_EVENT,
                    "artifact_hash": "sha256:done"}
        append_line(self.receipts, early)
        append_line(self.events, terminal)

        code, msg = run("whiteout", "--root", str(self.root),
                        "--target", "rcp.early",
                        "--correction", "rewrite a settled verdict",
                        "--reason", "second thoughts after it landed",
                        "--by", "test-session")
        self.assertEqual(code, 2)
        self.assertIn("terminal", msg.lower())
        self.assertEqual([a for a in read_jsonl(self.adms)
                          if a.get("type") == "whiteout"], [])

    # --- the stage-progression tooth: a receipt whose verdict already advanced
    #     the atom one stage is consumed, even though NOTHING cites the receipt
    #     id and the atom is not terminal yet. Driven through real pass_once,
    #     exactly as the adversarial verifier drove it.
    def test_receipt_whose_verdict_advanced_the_atom_refuses(self):
        field = make_field_root(self.tmp)
        # drive the real loop until the value-gate verdict has propagated into
        # the value.accepted event — but stop well short of terminal
        for _ in range(6):
            reconcile.pass_once(field, quiet=True)
            fold = Fold(field)
            advanced = any(e.get("type") == "value.accepted" for e in fold.events)
            terminal = any(e.get("type") == TERMINAL_EVENT for e in fold.events)
            if advanced and not terminal:
                break
        self.assertTrue(advanced, "loop never derived value.accepted")
        self.assertFalse(terminal, "drove too far — atom already terminal")

        # the value-gate receipt: it derived value.accepted (next_suggested_event)
        rc = next(r for r in fold.receipts
                  if r.get("next_suggested_event") == "value.accepted")
        rid = rc["id"]

        # the verifier's three observations, asserted directly:
        self.assertEqual(pen.consumers(fold, rc), [])          # nothing cites it
        self.assertFalse(pen.is_terminal(fold, rc))            # not terminal yet
        self.assertEqual(pen.stage_progressed(fold, rc),       # but it progressed
                         "value.accepted")

        log = field / "log"
        before = (log / "admissions.jsonl").read_bytes() \
            if (log / "admissions.jsonl").exists() else b""
        code, msg = run("whiteout", "--root", str(field),
                        "--target", rid,
                        "--correction", "FLIP the verdict to reject",
                        "--reason", "I want to rewrite a verdict that already moved",
                        "--by", "test-session")
        self.assertEqual(code, 2, msg)                         # REFUSES (was a bug)
        self.assertIn("consumed", msg)
        self.assertIn("advanced", msg)                         # names the progression
        self.assertIn("value.accepted", msg)
        self.assertIn("retro", msg)                            # names the escalation
        self.assertIn("supersede", msg)
        # nothing written: no whiteout admission landed
        after = (log / "admissions.jsonl").read_bytes() \
            if (log / "admissions.jsonl").exists() else b""
        self.assertEqual(after, before)
        self.assertEqual([a for a in read_jsonl(log / "admissions.jsonl")
                          if a.get("type") == "whiteout"], [])

    # --- the over-refusal guard: a freshly written, un-acted-on advancing
    #     record CAN still be whited out. The receipt shares its atom's hash
    #     with the seed event, but its verdict has NOT yet propagated (the
    #     value.accepted event it would derive is not on the log), so the
    #     stage-aware test must read it as un-consumed — hash-equality alone
    #     would over-refuse it.
    def test_fresh_advancing_record_still_whiteoutable(self):
        seed = {"id": "evt.seed", "type": "atom.created",
                "artifact_hash": "sha256:fresh"}
        rc = {"id": "rcp.fresh", "event_id": "evt.seed", "node": "value-gate",
              "artifact_hash": "sha256:fresh", "verdict": "accept",
              "next_suggested_event": "value.accepted"}
        append_line(self.events, seed)
        append_line(self.receipts, rc)

        fold = Fold(self.root)
        # the guard's premise: the verdict has NOT propagated yet
        self.assertIsNone(pen.stage_progressed(fold, rc))
        self.assertEqual(pen.consumers(fold, rc), [])

        code, msg = run("whiteout", "--root", str(self.root),
                        "--target", "rcp.fresh",
                        "--correction", "the verdict should read amend",
                        "--reason", "caught the slip before anything consumed it",
                        "--by", "test-session")
        self.assertEqual(code, 0, msg)
        whiteouts = [a for a in read_jsonl(self.adms) if a.get("type") == "whiteout"]
        self.assertEqual(len(whiteouts), 1)
        self.assertEqual(whiteouts[0]["target"], "rcp.fresh")

    # --- a pointer at nothing is refused (the discharge discipline) ---------
    def test_target_not_on_log_refuses(self):
        code, msg = run("whiteout", "--root", str(self.root),
                        "--target", "evt.ghost",
                        "--correction", "x", "--reason", "y", "--by", "test")
        self.assertEqual(code, 2)
        self.assertIn("no log stream", msg)
        self.assertFalse(self.adms.exists() and read_jsonl(self.adms))

    # --- softening a frozen done-line's bar stays bdo's supersede -----------
    def test_frozen_done_line_bar_refuses_pointing_at_supersede(self):
        done = self.root / "done"
        done.mkdir()
        shutil.copy(DONE_CFG, done / ".pen.json")  # frozen: true
        bar = done / "0033-some-contract.md"
        bar.write_text("# Done-line 0033 — a contract\n\n"
                       "> **Done when:** the bar is met.\n", encoding="utf-8")

        for target in ("0033", str(bar)):  # by id and by path
            code, msg = run("whiteout", "--root", str(self.root),
                            "--target", target,
                            "--correction", "make the bar easier",
                            "--reason", "ran out of time",
                            "--by", "test-session")
            self.assertEqual(code, 2, f"target {target!r} should refuse")
            self.assertIn("supersede", msg)
            self.assertIn("frozen done-line", msg)
        # the contract is untouched and no whiteout landed
        self.assertIn("the bar is met", bar.read_text(encoding="utf-8"))
        self.assertEqual([a for a in read_jsonl(self.adms)
                          if a.get("type") == "whiteout"], [])

    # --- the id-regex must not false-positive on real record ids ------------
    # `rcp.merge.0033` ends in four digits but is NOT a done-line spelling;
    # the frozen-done check must let it through to the ordinary log path, not
    # misroute it to supersede (the regex tightening, done-line 0064).
    def test_record_id_with_trailing_digits_not_seen_as_done_line(self):
        done = self.root / "done"
        done.mkdir()
        shutil.copy(DONE_CFG, done / ".pen.json")  # frozen: true
        (done / "0033-some-contract.md").write_text(
            "# Done-line 0033 — a contract\n\n> **Done when:** met.\n",
            encoding="utf-8")
        # the frozen check refuses the bare done-line id...
        self.assertIsNotNone(pen._frozen_done_line(self.root, "0033"))
        # ...but a record id that merely contains 0033 is NOT a done-line
        self.assertIsNone(pen._frozen_done_line(self.root, "rcp.merge.0033"))

        # and an unconsumed record so named whites out normally (not supersede)
        rec = {"id": "rcp.merge.0033", "node": "merge-node",
               "artifact_hash": "sha256:m", "verdict": "land"}
        append_line(self.receipts, rec)
        code, msg = run("whiteout", "--root", str(self.root),
                        "--target", "rcp.merge.0033",
                        "--correction", "the verdict should read send_back",
                        "--reason", "the merge landing was mis-stamped",
                        "--by", "test-session")
        self.assertEqual(code, 0, msg)
        self.assertNotIn("frozen done-line", msg)
        self.assertEqual(len([a for a in read_jsonl(self.adms)
                              if a.get("type") == "whiteout"]), 1)

    # --- the show path reads the chain without writing ----------------------
    def test_show_renders_chain_and_writes_nothing(self):
        original = {"id": "evt.show1", "type": "note.recorded",
                    "artifact_hash": "sha256:show", "text": "wrong"}
        append_line(self.events, original)
        run("whiteout", "--root", str(self.root), "--target", "evt.show1",
            "--correction", "right", "--reason", "it was wrong", "--by", "t")
        before = self.adms.read_bytes()
        code, msg = run("whiteout", "--root", str(self.root),
                        "--target", "evt.show1", "--show")
        self.assertEqual(code, 0)
        self.assertIn("now", msg)
        self.assertIn("right", msg)       # the correction
        self.assertIn("wrong", msg)       # the original, still visible
        self.assertEqual(self.adms.read_bytes(), before)  # read-only


if __name__ == "__main__":
    unittest.main()
