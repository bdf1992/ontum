import tempfile
import unittest
from pathlib import Path

from loop import agenda

ANIMA = """# Agenda 0001 — Anima

**status:** active

> The soul of an ontum.

## Arcs

_none named yet_
"""


def _write(p, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


class AgendaFold(unittest.TestCase):
    def test_active_no_arcs_exact_line(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root / "agendas" / "0001-anima.md", ANIMA)
            self.assertEqual(
                agenda.agenda_lines(root),
                ["[agenda] current: anima — The soul of an ontum.; "
                 "arcs: no arcs named yet"])

    def test_named_arcs_listed(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            text = ANIMA.replace(
                "_none named yet_",
                "- **the-metabolism** — energy as a computed cost\n"
                "- **the-viewer** — the self-similar zoom")
            _write(root / "agendas" / "0001-anima.md", text)
            lines = agenda.agenda_lines(root)
            self.assertEqual(len(lines), 1)
            self.assertIn("arcs: the-metabolism, the-viewer", lines[0])

    def test_active_is_data_driven_not_constant(self):
        # the reminder follows the declaration, never a literal: flip which
        # agenda is active and the surfaced line flips with it (§10 teeth).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            other = ("# Agenda 0002 — Other\n\n**status:** proposed\n\n"
                     "> Another reality.\n\n## Arcs\n\n_none named yet_\n")
            _write(root / "agendas" / "0001-anima.md", ANIMA)
            _write(root / "agendas" / "0002-other.md", other)
            lines = agenda.agenda_lines(root)
            self.assertEqual(len(lines), 1)
            self.assertIn("current: anima", lines[0])

            _write(root / "agendas" / "0001-anima.md",
                   ANIMA.replace("**status:** active", "**status:** proposed"))
            _write(root / "agendas" / "0002-other.md",
                   other.replace("**status:** proposed", "**status:** active"))
            lines = agenda.agenda_lines(root)
            self.assertEqual(len(lines), 1)
            self.assertIn("current: other", lines[0])

    def test_two_active_both_surface(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root / "agendas" / "0001-anima.md", ANIMA)
            _write(root / "agendas" / "0002-other.md",
                   "# Agenda 0002 — Other\n\n**status:** active\n\n"
                   "> Another.\n\n## Arcs\n\n_none named yet_\n")
            self.assertEqual(len(agenda.agenda_lines(root)), 2)

    def test_arc_association_drawn_from_ties(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root / "done" / "0079-x.md",
                   "# Done-line 0079\n\n> **Arc:** anima\n\n> **Done when:** x\n")
            _write(root / "done" / "0080-y.md",
                   "# Done-line 0080\n\n> **Goal:** goal.z\n")
            self.assertEqual(agenda.arc_association(root, "anima"), ["0079-x"])
            self.assertEqual(agenda.arc_association(root, "nobody"), [])

    def test_missing_dir_is_absence_not_crash(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(agenda.agenda_lines(Path(d)), [])
            self.assertEqual(agenda.load_agendas(Path(d)), [])


if __name__ == "__main__":
    unittest.main()
