"""Tests for loop/section.py — named sections of the ledger (the work queues),
bdo 2026-06-21 ("free to work over a named section ... a process which consumes
work").

The §10 teeth here are about the queue being REAL, not vacuous:

  * the value-confirm queue must EXCLUDE an already-confirmed atom — a queue
    that lists settled work never drains and is a clog by construction (the
    discriminator that makes "consume work" terminate);
  * an unknown section raises rather than silently returning [] (a section is a
    named contract, not a free-text query — a typo must not read as "no work");
  * one broken section's fold is reported, never a crash that blinds the rest.

It composes existing folds, so it is tested by stubbing those folds and proving
section.py maps them faithfully — no second truth to re-derive."""

import sys
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import section


class RegistryIntegrity(unittest.TestCase):
    def test_every_section_is_a_full_contract(self):
        # a section names its nature, how its work closes, and a fold to list it
        for name, spec in section.SECTIONS.items():
            self.assertIn("description", spec, name)
            self.assertIn("closes_via", spec, name)
            self.assertTrue(callable(spec["items"]), name)

    def test_unknown_section_raises_not_empty(self):
        # a typo must not read as "no work" — a named section is a contract
        with self.assertRaises(KeyError):
            section.section_items("/nonexistent", "not-a-section")


class ValueConfirmQueueTeeth(unittest.TestCase):
    """The load-bearing discriminator: the value-confirm queue lists only atoms
    still awaiting the independent review — a confirmed one has left the queue."""

    def _run(self):
        accepted = {"id": "atom.waiting.v0", "desired_state": "value_confirmed"}
        confirmed = {"id": "atom.done.v0", "desired_state": "value_confirmed"}
        # an atom that wants confirmation but is not even accepted yet — also out
        early = {"id": "atom.early.v0", "desired_state": "value_confirmed"}
        states = {"h-wait": "value_accepted", "h-done": "value_confirmed",
                  "h-early": "value_gate_pending"}
        with mock.patch.object(section.reconcile, "Fold", return_value=object()), \
             mock.patch.object(section.reconcile, "load_atoms",
                               return_value=[(accepted, "h-wait"), (confirmed, "h-done"),
                                             (early, "h-early")]), \
             mock.patch.object(section.reconcile, "atom_state",
                               side_effect=lambda fold, h: states[h]):
            return section.value_confirm_items("/root")

    def test_only_the_awaiting_atom_is_in_the_queue(self):
        items = self._run()
        ids = {it["id"] for it in items}
        self.assertEqual(ids, {"atom.waiting.v0"})  # not the confirmed, not the early

    def test_confirmed_atom_never_appears(self):
        # the teeth: if this failed the queue would never drain (the clog)
        items = self._run()
        self.assertNotIn("atom.done.v0", {it["id"] for it in items})

    def test_item_carries_its_artifact_hash_for_the_consumer(self):
        items = self._run()
        self.assertEqual(items[0]["artifact_hash"], "h-wait")


class OverviewResilience(unittest.TestCase):
    def test_a_broken_section_is_reported_not_crashed(self):
        boom = {"description": "explodes", "closes_via": "n/a",
                "items": lambda root: (_ for _ in ()).throw(RuntimeError("boom"))}
        with mock.patch.dict(section.SECTIONS, {"broken": boom}):
            rows = section.overview("/root")
        broken = next(r for r in rows if r["name"] == "broken")
        self.assertIsNone(broken["open"])
        self.assertIn("boom", broken["error"])
        # the other sections still computed (one bad fold did not blind the rest)
        self.assertTrue(any(r["name"] != "broken" for r in rows))


if __name__ == "__main__":
    unittest.main()
