#!/usr/bin/env python3
"""The agenda fold (done-line 0079): the current agenda and its arcs, as data.

bdo asked to be reminded at session start which agenda we are on and which arcs
serve it — and his instinct was right that doing it properly forces an
agenda-as-code layer rather than a hardcoded reminder (a constant in code, the
§7 thing this exists to prevent: it breaks the moment there is a second agenda).

Agendas are declared as penned records under `.ai-native/agendas/` (their own
`.pen.json` form). This pure read-only fold resolves the *active* agenda(s) and
their named arcs, drawing each arc's association from the existing greppable
`> **Arc:**` ties in the done-lines rather than re-declaring it — location is not
identity; the fold raises a thing to first-class by reference, never by a second
copy. The ambient one-line rendering rides the existing summon hook; the rich
owner board (priority-ordered roll-up) is this same fold rendered fuller — one
source of truth.

Stdlib only, read-only (I-3). A missing `agendas/` dir is an absence (`[]`),
never a crash — the hook that calls this is exit-0-always.
"""

import re
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT

AGENDAS_DIR = "agendas"

# the tie a piece of work carries to name its arc — the same greppable line the
# done-lines write (`> **Arc:** anima`). Association is drawn from this, never
# re-declared in the agenda file (location is not identity).
ARC_TIE = re.compile(r"^>\s*\*\*Arc:\*\*\s*`?([a-z0-9][a-z0-9._-]*)`?", re.I | re.M)

_HEADING = re.compile(r"^#\s*Agenda\b[^\n]*?—\s*(.+)$", re.M)
_STATUS = re.compile(r"\*\*status:\*\*\s*(\w+)", re.I)
_STATEMENT = re.compile(r"^>\s*(.+)$", re.M)
_ARCS_BLOCK = re.compile(r"^##\s*Arcs\s*$(.*?)(?=^##\s|\Z)", re.M | re.S)
_ARC_ITEM = re.compile(r"^\s*-\s*\*\*(.+?)\*\*\s*(?:—\s*(.*))?$")
_NUMBERED = re.compile(r"^\d{4}-(.+)$")


def _agenda_files(root):
    d = Path(root) / AGENDAS_DIR
    if not d.is_dir():
        return []
    return sorted(p for p in d.iterdir()
                  if p.suffix == ".md" and not p.name.startswith("."))


def _parse(path):
    """One agenda declaration -> {id, title, status, statement, arcs, path}. The
    id is the filename slug (after any NNNN- record number) — the name is the
    identity, the number is just the record's place."""
    text = path.read_text(encoding="utf-8")
    m = _NUMBERED.match(path.stem)
    aid = m.group(1) if m else path.stem
    hm = _HEADING.search(text)
    title = hm.group(1).strip() if hm else aid
    sm = _STATUS.search(text)
    status = sm.group(1).lower() if sm else "proposed"
    qm = _STATEMENT.search(text)
    statement = qm.group(1).strip() if qm else ""
    arcs = []
    bm = _ARCS_BLOCK.search(text)
    if bm:
        for line in bm.group(1).splitlines():
            im = _ARC_ITEM.match(line)
            if im:
                arcs.append({"name": im.group(1).strip(),
                             "line": (im.group(2) or "").strip()})
    return {"id": aid, "title": title, "status": status,
            "statement": statement, "arcs": arcs, "path": str(path)}


def load_agendas(root=DEFAULT_ROOT):
    """Every declared agenda, parsed. Read-only; an absent dir is []."""
    return [_parse(p) for p in _agenda_files(root)]


def active_agendas(root=DEFAULT_ROOT):
    """The agenda(s) declared active — the current one(s). More than one active
    is not an error: working several at once is exactly what forces the
    agenda-as-code layer to be explicit (bdo, 2026-06-14)."""
    return [a for a in load_agendas(root) if a["status"] == "active"]


def arc_association(root, arc_name):
    """The records that tie to this arc by the greppable `> **Arc:** <name>` line
    — the association drawn from ties, never re-declared. Scans the done-lines;
    read-only, an absent dir is []."""
    hits = []
    done = Path(root) / "done"
    if not done.is_dir():
        return hits
    for p in sorted(done.iterdir()):
        if p.suffix != ".md":
            continue
        for m in ARC_TIE.finditer(p.read_text(encoding="utf-8")):
            if m.group(1).lower() == arc_name.lower():
                hits.append(p.stem)
                break
    return hits


def agenda_lines(root=DEFAULT_ROOT):
    """The ambient reminder line(s) for the SessionStart hook — one per active
    agenda, naming the agenda and its arcs (or 'no arcs named yet'). Empty when
    no agenda is active: silence, never a noisy 'all clear'."""
    out = []
    for a in active_agendas(root):
        names = (", ".join(arc["name"] for arc in a["arcs"])
                 if a["arcs"] else "no arcs named yet")
        statement = a["statement"]
        if len(statement) > 140:
            statement = statement[:140].rstrip() + " …"
        out.append(f"[agenda] current: {a['id']} — {statement}; arcs: {names}")
    return out
