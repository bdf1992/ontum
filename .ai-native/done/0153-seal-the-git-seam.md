# Done-line 0153 — seal the git seam: the first installed barrier-fence instance

Written before code, per §9.4. When this line is met, stop.

The first INSTALLED instance of the gate/fence primitive ([[0149-gate-fence-primitive]]),
on bdo's pick: turn the modelled seam-seal into a real, enforced barrier.

The finding the primitive surfaced: command_guard's prefix-rule registry reads
the QUOTE-STRIPPED command, so a `git push` reached by shelling out — an argv
list like `subprocess.run(['git','push'])` — survives every prefix rule, because
strip_quoted removes the very quotes the git lives in. The perimeter is torn at
the seam. The catch: a blind raw-command scan for "git push" would false-block
the git pen's own commit traffic (a message that merely mentions it), which is
exactly why strip_quoted exists. The prose-safe key is the argv-LIST shape —
git and push as separate quoted tokens joined by a comma — which prose never
uses.

The seal dogfoods the primitive: command_guard imports `fence/barrier.py`'s
`SEAM_LINK` and runs `decide` over the RAW command, so the live enforcement IS
an instance of the primitive, not a twin of it.

> **Done when:** `command_guard.first_deny` reads the RAW command through `fence.barrier.SEAM_LINK` (the argv-list-shape seam tooth) before the quote-stripped prefix rules, denying a shelled `git push` (exit 2) while leaving the git pen's own commit-message traffic and a shelled `git status` untouched (exit 0); `barrier.command_guard_fence()` (prefix registry + the seam tooth) validates CLOSED while `barrier.prefix_rules_fence()` (registry alone) stays torn at the seam; the seam load is fail-open like the fence load; and `tests/test_fence.py::SeamSeal` proves the seal bites the shelled push AND does not false-block the pen commit — the suite green.
