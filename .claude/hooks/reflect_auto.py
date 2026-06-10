#!/usr/bin/env python3
"""The auto beat (done-line 0020): the repo's first writing hook.

Wired to Stop — after each turn, run the reflector pen's `auto` verb so
the drift that admitted, enabled rules name clears itself. The contract
change (hooks never wrote before this) is stamped on the done-line:
bdo's pub/sub directive and his "Lets do it then" (chat, 2026-06-10).

Discipline of the beat:
- It writes only through the pen, which writes only what enabled rules
  name — no rule, no reach (§10: configured-off drift must not reflect).
- Fail-open, exit 0 always: a broken beat must never break the turn or
  gate the owner. A missed beat costs nothing — drift is level-triggered
  and the next beat re-derives it.
- Quiet when nothing happened; the pen's output surfaces only when an
  act was applied or escalation is needed.
"""

import os
import subprocess
import sys
from pathlib import Path


def main():
    try:
        sys.stdin.read()  # the hook payload; the fold is the truth, not it
        root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or ".").resolve()
        pen = root / ".claude" / "skills" / "reflect" / "reflect.py"
        if not pen.exists():
            return 0
        proc = subprocess.run(
            [sys.executable, str(pen), "auto",
             "--root", str(root / ".ai-native"), "--by", "reflect-auto"],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", cwd=root, timeout=120,
        )
        out = (proc.stdout or "").strip()
        if out and not out.endswith("(no enabled rule has drift)"):
            print(out)
    except Exception:
        pass  # fail-open: the beat never breaks the turn
    return 0


if __name__ == "__main__":
    sys.exit(main())
