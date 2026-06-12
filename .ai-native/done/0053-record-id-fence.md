# Done-line 0053 — Record ids refuse to collide at the commit seam

﻿Written before code, per §9.4. When this line is met, stop.

> **Done when:** a record id minted against a stale local fold is caught at
> the seam where it becomes durable: the git pen's `commit` refuses to commit
> a NEW `.ai-native/done/` or `.ai-native/reports/` file whose 4-digit id
> already names a *different* file in the same directory on any ref (local
> heads or origin/*), naming the id, both filenames, and the ref — while the
> same file propagated unchanged stays allowed (tonight's 0050 carry), and
> history's existing duplicates (the four 0020s, the twin 0037 reports) are
> never retro-flagged because only newly-staged files are checked. The
> refusal is a pure function the suite hits directly, with the §10 case
> shaped like tonight: `0050-rung-intake.md` staged while a ref holds
> `0050-field-topology-the-first-field.md` refuses; propagating the
> field-topology file itself passes. The check fails open when refs cannot
> be listed — a broken sensor never blocks a commit.

## Out of scope, named

- **Teaching `loop/pen.py` to fold over refs.** loop/ stays pure (no
  subprocess, no git — the placement-gate discipline); the harness-layer pen
  is where git lives, so the fence stands there. If the mint seam itself
  should also know, that is a later line with its own design.
- **Atom-id collisions** — the placement gate already owns those.
- **Retro-repair of history's duplicate ids** — superseding, never erasure;
  the duplicates stand as history.
