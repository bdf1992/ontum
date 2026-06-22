"""Done-line 0178: the loop's guaranteed-tick heartbeat — a §10 refuse-to-fit.

The clog the beat cures: a level-triggered loop with no guaranteed driver. The
beat turns the crank. These tests pin its load-bearing safety with injected
fakes — NO live spawn, NO real headless review:

  - a CONFIRMED-arc atom at value.accepted ADVANCES past the owner-stamp after a
    beat (the loop executes bdo's standing stamp);
  - a locally-identical UNCONFIRMED atom does NOT settle and gets NO owner-stamp
    receipt — it PARKS (the no-fake-stamp teeth: two atoms differing only by arc
    confirmation are treated differently, so the property cannot be vacuous);
  - the drain fires AT MOST drain_limit reviews (injected fake reviewer);
  - a second beat with nothing pending writes nothing and fires nothing
    (idempotent / level-triggered);
  - --hook mode returns exit 0 even when the underlying beat raises (fail-open).

A beat that fake-stamped the unconfirmed atom, or auto-settled it, would fail
the no-fake-stamp case; a beat that did nothing would fail the advance case. The
field is forced to discriminate.
"""

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from loop import heartbeat, orchestrate, reconcile
from loop import node as node_pen

STAMP_MOCK = "owner-stamp.mock-bdo.v0"
STAMP_REAL = "owner-stamp.bdo.v1"
CONFIRM_MOCK = "value-confirm.mock.v0"
CONFIRM_REAL = "value-confirm.claude.v1"
SETPOINT = {"step_budget_per_tick": 8, "max_inflight_atoms": 50,
            "human_queue_cap": 50}

GATE_PY = REPO / ".claude" / "skills" / "gate" / "gate.py"
_spec = importlib.util.spec_from_file_location("gate_pen", GATE_PY)
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)


def _atom(slug, serves):
    return {"atom": {
        "id": f"atom.{slug}.v0",
        "story": {"text": f"As an AI, I need {slug}, because bdo wants the "
                          "heartbeat proven.",
                  "value_confidence": "high", "owner_stamp": "pending"},
        "concern_surface": "systems",
        "incidence": {"serves": [serves], "touches": [".ai-native/log"],
                      "must_not_collide_with": [],
                      "hands_off_to": ["seam.value-to-placement"]},
        "desired_state": "value_confirmed",
        "verdicts": {"value_gate": "pending", "placement_gate": "pending",
                     "eval_gate": "pending"},
        "lineage": {"prompt_versions": [], "source_artifacts": [], "receipts": []},
    }}


def _admit(root, obj):
    reconcile.append_line(root / "log" / "admissions.jsonl", obj)


def _base_root(tmp, atoms_spec, confirmed_epics=()):
    """A records root with the owner-stamp AND value-confirm admitted REAL (the
    production posture this beat is built for), a setpoint, and the named
    atoms. `atoms_spec` is [(slug, serves_epic)]; `confirmed_epics` are the
    arcs whose confirmation is admitted (their atoms auto-stamp)."""
    root = Path(tmp) / ".ai-native"
    (root / "log").mkdir(parents=True)
    (root / "atoms").mkdir(parents=True)
    (root / "epics").mkdir(parents=True)
    for slug, serves in atoms_spec:
        (root / "atoms" / f"atom.{slug}.v0.json").write_text(
            json.dumps(_atom(slug, serves), indent=2), encoding="utf-8")
        # a minimal epic record so epic_of() can file the atom under its arc
        ep = serves
        (root / "epics" / f"{ep}.json").write_text(json.dumps(
            {"epic": {"id": ep, "owner": "bdo", "arc": f"test arc {ep}",
                      "pieces": [{"atom": f"atom.{slug}.v0", "glue": "test"}]}},
            indent=2), encoding="utf-8")
    # owner-stamp REAL: an unconfirmed arc's atom now PARKS here (no mock human).
    _admit(root, {"id": "adm.test-owner-stamp-real", "type": "node_real",
                  "stage_node": STAMP_MOCK, "real_node": STAMP_REAL,
                  "by": "test-bdo", "ts": "2026-06-20T00:00:00Z"})
    # value-confirm REAL: terminal work PARKS here (the review queue).
    _admit(root, {"id": "adm.test-value-confirm-real", "type": "node_real",
                  "stage_node": CONFIRM_MOCK, "real_node": CONFIRM_REAL,
                  "by": "test-bdo", "ts": "2026-06-20T00:00:00Z"})
    for ep in confirmed_epics:
        _admit(root, {"id": f"adm.test-arc-{ep}", "type": "arc_confirmed",
                      "epic": ep, "by": "bdo", "enabled": True,
                      "ts": "2026-06-20T00:00:00Z"})
    orchestrate.admit_setpoint(root, SETPOINT, by="test-bdo")
    return root


def _ahash(root, atom_id):
    return next(h for a, h in reconcile.load_atoms(root) if a["id"] == atom_id)


def _state(root, atom_id):
    return reconcile.atom_state(reconcile.Fold(root), _ahash(root, atom_id))


def _drive_to_owner_stamp(root, atom_id, max_steps=12):
    """Advance one atom step-by-step until it is parked at the owner-stamp
    DECISION: the `value.accepted` event is on the log (the stamp's trigger) and
    no owner-stamp receipt exists yet. Stopping here — not merely at the
    `value_accepted` STATE, which is reached one step earlier, when the
    value-gate receipt lands but before `value.accepted` is derived — is what
    leaves the very next step as the owner-stamp decision, so one beat's tick
    either takes it (confirmed) or refuses to (unconfirmed)."""
    for _ in range(max_steps):
        fold = reconcile.Fold(root)
        ahash = _ahash(root, atom_id)
        if (fold.event("value.accepted", ahash) is not None
                and not _stamp_receipts(root, atom_id)):
            return
        atom = next(a for a, h in reconcile.load_atoms(root) if h == ahash)
        reconcile.pass_once(root, atom=atom, artifact_hash=ahash, quiet=True)


def _stamp_receipts(root, atom_id):
    """Every owner-stamp (real OR mock) receipt on the log for this atom."""
    fold = reconcile.Fold(root)
    ahash = _ahash(root, atom_id)
    return [rc for rc in fold.receipts
            if rc.get("artifact_hash") == ahash
            and rc.get("node") in (STAMP_REAL, STAMP_MOCK)]


def _log_sizes(root):
    out = {}
    for name in ("events", "receipts", "admissions"):
        p = root / "log" / f"{name}.jsonl"
        out[name] = p.stat().st_size if p.exists() else 0
    return out


class HeartbeatTick(unittest.TestCase):
    def test_confirmed_advances_unconfirmed_parks_no_fake_stamp(self):
        """The §10 teeth: two atoms identical but for arc confirmation. One beat
        advances the confirmed atom past the owner-stamp and PARKS the
        unconfirmed one with NO stamp receipt — the loop never invents a stamp."""
        self.tmp = tempfile.mkdtemp()
        root = _base_root(self.tmp,
                          atoms_spec=[("conf", "epic.confirmed"),
                                      ("unconf", "epic.unconfirmed")],
                          confirmed_epics=["epic.confirmed"])
        # place both atoms exactly at the owner-stamp decision (next step = stamp)
        _drive_to_owner_stamp(root, "atom.conf.v0")
        _drive_to_owner_stamp(root, "atom.unconf.v0")
        self.assertEqual(_state(root, "atom.conf.v0"), "value_accepted")
        self.assertEqual(_state(root, "atom.unconf.v0"), "value_accepted")
        self.assertEqual(_stamp_receipts(root, "atom.conf.v0"), [])
        self.assertEqual(_stamp_receipts(root, "atom.unconf.v0"), [])

        summary = heartbeat.beat(root)

        # confirmed: ADVANCED past the owner-stamp (the loop executed bdo's
        # standing confirmation), and a real owner-stamp receipt exists.
        self.assertNotEqual(_state(root, "atom.conf.v0"), "value_accepted")
        conf_stamps = _stamp_receipts(root, "atom.conf.v0")
        self.assertEqual(len(conf_stamps), 1)
        self.assertEqual(conf_stamps[0]["node"], STAMP_REAL)
        self.assertGreater(summary["advanced"], 0)

        # unconfirmed: PARKED — still at value.accepted, and CRUCIALLY no
        # owner-stamp receipt of any kind (no fake-stamp).
        self.assertEqual(_state(root, "atom.unconf.v0"), "value_accepted")
        self.assertEqual(_stamp_receipts(root, "atom.unconf.v0"), [],
                         "an unconfirmed atom must NEVER be stamped by the beat")

    def test_idempotent_quiescent_beat_writes_nothing(self):
        """A beat with nothing pending touches no bytes (idempotent / level-
        triggered). Drive the field to its steady state first, then prove a
        second beat changes no log file's size and advances/drains nothing."""
        self.tmp = tempfile.mkdtemp()
        root = _base_root(self.tmp, atoms_spec=[("solo", "epic.unconfirmed")])
        # run beats until quiescent (the unconfirmed atom parks at owner-stamp)
        for _ in range(8):
            if heartbeat.beat(root)["advanced"] == 0:
                break
        before = _log_sizes(root)
        summary = heartbeat.beat(root)
        after = _log_sizes(root)
        self.assertEqual(before, after, "a quiescent beat must write no bytes")
        self.assertEqual(summary["advanced"], 0)
        self.assertEqual(summary["drained"], 0)


class HeartbeatDrain(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        # three confirmed-arc atoms; the tick drives them to the value-confirm
        # queue, then the drain fires real reviews (injected, no spawn).
        self.root = _base_root(
            self.tmp,
            atoms_spec=[("alpha", "epic.fleet"), ("bravo", "epic.fleet"),
                        ("charlie", "epic.fleet")],
            confirmed_epics=["epic.fleet"])
        # tick the loop to convergence so all three park at value-confirm
        for _ in range(20):
            if heartbeat.beat(self.root)["advanced"] == 0:
                break

    def _queued(self):
        from loop.summon import open_summons
        return {s["atom"]["id"] for s in open_summons(self.root)
                if s["node"] == CONFIRM_REAL}

    def test_queue_formed_at_value_confirm(self):
        self.assertEqual(self._queued(),
                         {"atom.alpha.v0", "atom.bravo.v0", "atom.charlie.v0"})

    def test_drain_fires_at_most_drain_limit(self):
        fired_log = []

        def fake_review(records_root, atom_id, node_id, by):
            fired_log.append(atom_id)
            node_pen.judge(records_root, atom_id, node_id, "confirmed",
                           "fake review: claim delivered")
            return 0

        summary = heartbeat.beat(self.root, drain_limit=2, by="test",
                                 review=fake_review)
        # AT MOST drain_limit reviews fired this beat — not all three.
        self.assertEqual(summary["drained"], 2)
        self.assertEqual(len(fired_log), 2)
        # the third atom is still queued for the next paced beat (level-triggered)
        self.assertEqual(len(self._queued()), 1)

    def test_drain_zero_is_tick_only(self):
        """The default beat (drain_limit=0) never fires a review even with a
        full queue — the cheap path stays cheap."""
        called = []
        summary = heartbeat.beat(self.root, drain_limit=0,
                                 review=lambda *a, **k: called.append(a))
        self.assertEqual(summary["drained"], 0)
        self.assertEqual(called, [])
        self.assertEqual(len(self._queued()), 3)


class HeartbeatHookFailOpen(unittest.TestCase):
    def test_hook_returns_zero_even_when_beat_raises(self):
        """--hook is fail-open: even if the underlying beat blows up, the hook
        catches everything and exits 0 — it can never block a session."""
        self.tmp = tempfile.mkdtemp()
        root = _base_root(self.tmp, atoms_spec=[("solo", "epic.fleet")],
                          confirmed_epics=["epic.fleet"])
        with mock.patch.object(heartbeat, "beat",
                               side_effect=RuntimeError("boom")):
            rc = heartbeat.main(["--hook", "--root", str(root)])
        self.assertEqual(rc, 0)

    def test_hook_no_setpoint_is_silent_exit_zero(self):
        """No setpoint admitted -> the hook simply does not tick, exit 0."""
        tmp = tempfile.mkdtemp()
        root = Path(tmp) / ".ai-native"
        (root / "log").mkdir(parents=True)
        (root / "atoms").mkdir(parents=True)
        rc = heartbeat.main(["--hook", "--root", str(root)])
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
