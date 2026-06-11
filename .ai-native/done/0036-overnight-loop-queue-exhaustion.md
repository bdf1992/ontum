# Done-line 0036 — Overnight loop stops on exhausted queue

Written before code, per §9.4. When this line is met, stop.

> **Done when:** `overnight.py pickup --arc epic.substrate` reports no safe queued substrate story after all ordered overnight-loop story done-lines are present, instead of repeating the final story.
