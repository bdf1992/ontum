# Done-line 0062 — the records pen claims a fleet-safe id, not a local one

Written before code, per §9.4. When this line is met, stop.

The records pen (`loop/pen.py`) allocates the next record id by folding
the **local** directory only — blind to sibling branches in the
shared-tree fleet. The write guard was already fixed to fold the whole
fleet (it imports `placement.py`, done-line 0023), but the pen — the
paved path sessions actually use — was not, and its subprocess writes
bypass the guard entirely. So a session minting through the pen gets a
local id a sibling branch already claimed, and the git commit fence
refuses it only at commit, forcing a manual renumber (this session: a
done-line born 0057 took three tries to land, a report 0049 → 0051).
The fleet-safe authority already exists in `placement.py`; the pen just
never reached for it.

The architectural constraint holds: git-reach lives under `.claude/`,
never in pure-stdlib `loop/` (placement's own rule). So the pen does not
gain git — it **delegates** to the placement reach-tool by subprocess.

> **Done when:** `loop.pen`'s id allocation claims the **fleet-safe**
> next id — one past the highest record id on ANY git ref — by
> delegating to `placement.py` (the `.claude/` git-reach tool, so
> `loop/` gains no git of its own), with a **fail-open** fallback to the
> local directory fold when placement or git is unreachable; proven by
> test: in a two-branch repo the pen allocates an id strictly above the
> highest id present on either branch's ref (not the local maximum), and
> falls back to the local fold when the reach-tool is absent — a broken
> sensor never blocks a mint.
