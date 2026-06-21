# Done-line 0160 — The placement fold: a worker belongs in its own worktree, not the viewport

> **Goal:** the session gateway, platform level

Written before code, per §9.4. When this line is met, stop. The placement organ of the session gateway (`session-gateway.proposal.md` §11 increment #4; bdo's "gateway start, platform level", 2026-06-20). The workstation fence (#341/#346) is the WALL — it FORBIDS a worker writing or flipping the viewport (the shared trunk primary checkout, bdo's reading surface) at the *tool* seam. This is the DOOR beside that wall, at the *session* seam: it computes WHERE a worker belongs (its own worktree) and detects when one is trespassing in the viewport, so the prohibition never has to fire. Platform-level by design — a pure fold in `loop/` (family-neutral), the same define-once / render-per-family split `fence/` uses; the provisioning actuator and the SessionStart render are later waves.

> **Done when:** loop/placement.py is a pure fold (stdlib, no subprocess, no network) reusing loop/workspace.py, exposing placement_path, placement_refusal (the §10 bite: a claimed worker in the viewport is trespassing and is told its placement; a worker in its correct tree passes; no-claim is left alone), and placement_status. tests/test_placement.py proves the teeth are non-vacuous and joins the suite green.
