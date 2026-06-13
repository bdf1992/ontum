#!/usr/bin/env python3
"""Owner-asks: the needs-you items in session reports, as a fold (done-line 0058).

A session ended (report 0047) with five items "awaiting bdo" written only
into its report — an uncommitted file in a working tree bdo never opens.
The reflect machinery mirrors the owner-stamp *queue* (atoms at his admitted
stamp) onto the surface he reads, but an ad-hoc needs-you item in a session
report enters no queue and reaches no surface: it strands, invisibly parked
on the owner. bdo's correction (2026-06-12): "things shouldn't be parked on
me without a clear plain-English cold-read handoff."

This module is the pure base of the fix: one read-only, stdlib-only fold
over `.ai-native/reports/*.md` that pulls every report's parked asks out of
its scaffolded `## needs-you` section and groups them per report. It writes
nothing and reaches nowhere. Two consumers ride it:

- `loop/reflect.py` adds the **owner-ask-backlog** drift kind, so a report's
  asks are offered to bdo's GitHub inbox through the existing reflector pen
  once he admits the rule (the mirror, never a write path — D-4).
- `.claude/hooks/owner_ask_shame.py` screams every still-unsurfaced ask each
  turn, growing louder, until it reaches him (the floor — like mock-shame).

"Surfaced" is a property of the log (a reflection record acks the group),
computed in reflect.py beside the other reflection folds; here we only read
the durable reports and shape the asks. The anchor is the scaffolded
needs-you HEADING (the report pen's contract), not prose mentions — absence
of a heading is absence of an ask, never a guess.
"""

import re
from pathlib import Path

from loop.reconcile import short_hash

_HEADING = re.compile(r"^#{1,6}\s+(.*?)\s*$")
_NEEDS_YOU = re.compile(r"needs[\s-]?you", re.IGNORECASE)
_LIST_ITEM = re.compile(r"^\s*(?:\d+[.)]|[-*+])\s+(.*\S)\s*$")
# placeholder/empty rows the scaffold or an honest "nothing" leaves behind
_EMPTY = re.compile(r"^(nothing|none|n/?a|—|-)\.?$", re.IGNORECASE)
_MAX_ASK_LEN = 280  # an ask is a headline, not the whole section


def _extract_asks(text):
    """Every list item under a needs-you heading in one report's markdown,
    each item's continuation lines folded in. A heading boundary opens or
    closes the section; the report pen scaffolds `## needs-you`, so the
    heading is the contract we read."""
    asks = []
    in_section = False
    current = None
    for line in text.splitlines():
        heading = _HEADING.match(line)
        if heading:
            if current is not None:
                asks.append(current)
                current = None
            in_section = bool(_NEEDS_YOU.search(heading.group(1)))
            continue
        if not in_section:
            continue
        item = _LIST_ITEM.match(line)
        if item:
            if current is not None:
                asks.append(current)
            current = item.group(1).strip()
        elif current is not None:
            if line.strip():
                current = (current + " " + line.strip())[:_MAX_ASK_LEN]
            else:
                asks.append(current)
                current = None
    if current is not None:
        asks.append(current)
    return [a for a in (a.strip()[:_MAX_ASK_LEN] for a in asks)
            if a and not _EMPTY.match(a) and not a.startswith("<")]


def _title(report_id, asks):
    return (f"[owner-ask] {len(asks)} item(s) parked on you in report "
            f"{report_id}")


def _body(report_id, report_file, asks):
    lines = [
        f"## owner-asks stranded in report `{report_id}`",
        "",
        f"This session's report parks **{len(asks)}** item(s) on you that "
        "reached no surface you read — each was written only into "
        f"`.ai-native/reports/{report_file}`, a working-tree file, not your "
        "inbox. That is the hole report 0047's five invisible taps exposed: "
        "an ad-hoc needs-you item enters no queue and strands.",
        "",
    ]
    for i, ask in enumerate(asks, 1):
        lines.append(f"{i}. {ask}")
    lines += [
        "",
        "*This issue is a one-way **mirror** of the report's needs-you "
        "section (`loop/owner_asks.py`); acting here does nothing — your "
        "answer is a gesture you make where you choose. A free-text ask "
        "carries no log-backed 'answered' signal, so the mirror is "
        "open-only: it never reopens what it surfaced once, and closing it "
        "is yours.*",
    ]
    return "\n".join(lines)


def owner_ask_groups(root):
    """Per report with parked needs-you items, the asks it leaves on bdo.
    Returns a list of {report_id, report_file, asks, id, title, body}, sorted
    by report file. The group id is stable over the report id alone (a
    report's handoff is fixed once written), so an open is idempotent and a
    later edit to settled history does not re-surface. A missing reports/
    directory is an absence, not an error: returns []."""
    reports = Path(root) / "reports"
    if not reports.is_dir():
        return []
    out = []
    for path in sorted(reports.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue  # an unreadable report is a gap to fix, not a crash
        asks = _extract_asks(text)
        if not asks:
            continue
        report_id = path.stem
        out.append({
            "report_id": report_id,
            "report_file": path.name,
            "asks": asks,
            "id": "ask." + short_hash("owner-ask", report_id),
            "title": _title(report_id, asks),
            "body": _body(report_id, path.name, asks),
        })
    return out
