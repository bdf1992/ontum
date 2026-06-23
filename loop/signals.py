#!/usr/bin/env python3
"""The signal stream (done-line 0092): teeth leave a mark.

bdo, 2026-06-16: a stopping point should be *farmed*, not idled — and "the
refusal is the signal." But a signal that is not recorded cannot be farmed.
Today the loop's newer teeth — loopmaker's `Stop`, cited_sensor's ghost,
reversibility_gate's block — refuse and then vanish: a meteor that burns up,
leaving no meteorite. This records each firing as a foldable signal on an
append-only auxiliary stream (`.ai-native/log/signals.jsonl`, in the grain of
the watcher's `tool-use.jsonl`), so the harvest (atom.harvest.v0) has a field
to work.

A recorded firing lands in state `seed` — raw potential, not yet threshed into a
*grain of insight* nor *banked* as a Commons pattern. Those transitions belong
to the harvest; planting a seed into the Commons stays a deliberate admission
(D-4). The mark is the landing (the meteorite); the harvest is what is done with
what landed.

Pure stdlib, reusing `reconcile.append_line` / `short_hash` (§10 — one append
path, not a new mechanism).
"""

import json
from pathlib import Path

from loop.reconcile import append_line, now_ts, short_hash

STREAM = "signals.jsonl"
SEED = "seed"  # the state a freshly-recorded signal lands in (raw potential)


def _stream_path(root):
    return Path(root) / "log" / STREAM


def mark(root, kind, subject, why, *, state=SEED, extra=None):
    """Land one signal — a teeth-firing made foldable.

    `kind` names the tooth and its verdict ('loop-stop:converged',
    'cited-ghost', 'gate-block:irreversible'); `subject` is what it fired on;
    `why` is the legible reason. The id is content-hashed over
    (kind, subject, why), so re-recording the same firing folds to ONE signal
    (I-2). Returns the record."""
    rec = {
        "id": "sig." + short_hash("signal", kind, subject, why),
        "kind": kind,
        "subject": subject,
        "why": why,
        "state": state,
        "ts": now_ts(),
    }
    if extra:
        rec["extra"] = extra
    append_line(_stream_path(root), rec)
    return rec


def read(root):
    """Fold the signal stream — every recorded firing, latest write of an id
    winning (so a re-recorded firing folds to one). Torn-tail tolerant: a
    partially-written final line is dropped (it never happened, the fold
    re-derives). An absent stream is an empty field (absence is information)."""
    path = _stream_path(root)
    if not path.exists():
        return []
    by_id, order = {}, []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue  # torn tail / partial line — drop it
        rid = rec.get("id")
        if rid not in by_id:
            order.append(rid)
        by_id[rid] = rec
    return [by_id[i] for i in order]
