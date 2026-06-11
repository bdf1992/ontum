"""fence/probe_codex.py - record what Codex actually hands a hook.

The local Codex manual documents hook *config* shape but not the hook
stdin/stdout contract, and nothing here gets authored against an
undocumented seam (done-line 0029). This probe is the instrument: wired
into .codex/hooks.json for PreToolUse, PostToolUse and
PermissionRequest, it appends one JSON line per firing - the event name
it was invoked for, raw stdin, argv, cwd, and the CODEX*-shaped
environment - to a gitignored sensor trace:

    .ai-native/log/codex-hook-probe.jsonl

Once that file holds real payloads, the Codex watcher and the
apply_patch write-guard equivalent can be designed against observation
instead of guesswork (bdo's queue, items 2 and 3).

A probe never interferes: it writes nothing to stdout, swallows its own
errors, and exits 0 always. Stdlib only.
"""

import datetime
import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TRACE = ROOT / ".ai-native" / "log" / "codex-hook-probe.jsonl"


def main():
    try:
        entry = {
            "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "event": sys.argv[1] if len(sys.argv) > 1 else "",
            "argv": sys.argv,
            "cwd": os.getcwd(),
            "stdin": sys.stdin.buffer.read().decode("utf-8", "replace"),
            "env": {k: v for k, v in os.environ.items()
                    if "CODEX" in k.upper()},
        }
        TRACE.parent.mkdir(parents=True, exist_ok=True)
        with open(TRACE, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass  # a probe never breaks what it observes
    return 0


if __name__ == "__main__":
    sys.exit(main())
