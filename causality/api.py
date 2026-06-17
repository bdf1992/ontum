#!/usr/bin/env python3
"""api.py — done-line 0097: the curl-first HTTP layer for Causality.

bdo's steer (2026-06-17): "curl first." The projection-api contract already
said it (`contracts/projection-api.md`: "today the API is the term_economy CLI
... a future HTTP layer drives the same operations against the same records");
this is that layer. The browser canvas is demoted to one client — every surface
read has a non-browser, curl-addressable equivalent:

    python causality/api.py serve            # localhost:8077
    curl localhost:8077/commons              # the derived Pattern Commons
    curl localhost:8077/projection           # the committed term-economy view
    curl localhost:8077/health

Local-first, stdlib only, no network at runtime (loopback only). It is a
PROJECTION, never a source of truth: /projection serves the committed bytes the
fold produced, /commons serves a read-only derivation — neither writes anything,
and minting stays bdo's (D-4). The routing is one pure function `route()` that
the HTTP handler and the §10 test both call, so the curl surface and the test
can never drift (I-4).
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# run either as a plain script (`python causality/api.py`, like term_economy.py)
# or as a module (`python -m causality.api`): put the repo root on the path so
# the package import resolves both ways.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from causality import commons  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
PROJECTION = REPO / "causality" / "examples" / "ontum-terms.projection.json"
DEFAULT_PORT = 8077


def route(path):
    """Pure router: path -> (status, content_type, body_bytes). No I/O beyond
    reading committed bytes and the read-only fold; the single source of truth
    for what every client (curl, the canvas, the test) sees."""
    clean = path.split("?", 1)[0].rstrip("/") or "/"
    if clean == "/health":
        return 200, "application/json", _json({"ok": True, "service": "causality-api"})
    if clean == "/commons":
        return 200, "application/json", _json(commons.derive(REPO))
    if clean == "/projection":
        if not PROJECTION.is_file():
            return 404, "application/json", _json({"error": "no committed projection",
                                                   "hint": "term_economy.py project --write"})
        # serve the committed bytes verbatim — the projection property (a view,
        # byte-reproducible from the seed), never re-folded here.
        return 200, "application/json", PROJECTION.read_bytes()
    if clean == "/":
        return 200, "application/json", _json({
            "service": "causality-api", "curl_first": True,
            "routes": ["/health", "/commons", "/projection"]})
    return 404, "application/json", _json({"error": "no such route", "path": clean,
                                           "routes": ["/health", "/commons", "/projection"]})


def _json(obj):
    return (json.dumps(obj, indent=2, sort_keys=True) + "\n").encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):                      # noqa: N802 (stdlib contract)
        status, ctype, body = route(self.path)
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")  # localhost canvas client
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):             # keep the console quiet
        pass


def serve(port=DEFAULT_PORT):
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"causality-api serving curl-first on http://127.0.0.1:{port} "
          f"(/health /commons /projection) — ctrl-c to stop")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()
        print("\nresult: done — stopped")


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    verb = argv[0] if argv else "serve"
    if verb != "serve":
        print(f"result: needs-you — unknown verb {verb!r}; try `serve [--port N]`")
        return 2
    port = DEFAULT_PORT
    if "--port" in argv:
        port = int(argv[argv.index("--port") + 1])
    serve(port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
